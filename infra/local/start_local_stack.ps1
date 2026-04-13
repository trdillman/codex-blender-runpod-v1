param(
    [string]$BrokerHost = "127.0.0.1",
    [int]$BrokerPort = 8080,
    [string]$SandboxRepoRoot = "C:\Users\Tyler\Documents\Playground\blender-edgebox-sandbox",
    [string]$SandboxImage = "agent-sandbox-blender:local",
    [string]$SandboxOwnerId = "codex-local-broker"
)

$ErrorActionPreference = "Stop"

function New-UrlSafeToken {
    param([int]$ByteCount)
    $bytes = New-Object byte[] $ByteCount
    [System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
    return [Convert]::ToBase64String($bytes).TrimEnd('=').Replace('+', '-').Replace('/', '_')
}

function Read-LogText {
    param([string[]]$Paths)
    $parts = @()
    foreach ($Path in $Paths) {
        if (Test-Path $Path) {
            $parts += (Get-Content -Path $Path -Raw)
        }
    }
    return ($parts -join "`n")
}

function Stop-TrackedProcess {
    param([hashtable]$State, [string]$Name)
    if ($State.ContainsKey($Name) -and $State[$Name]) {
        try {
            $process = Get-Process -Id ([int]$State[$Name]) -ErrorAction Stop
            Stop-Process -Id $process.Id -Force -ErrorAction Stop
        } catch {
        }
    }
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$localRoot = Join-Path $repoRoot ".local"
$logRoot = Join-Path $localRoot "logs"
$dataRoot = Join-Path $localRoot "data"
$artifactRoot = Join-Path $localRoot "artifacts"
$runtimeStatePath = Join-Path $localRoot "local-stack.json"
$brokerOut = Join-Path $logRoot "broker.stdout.log"
$brokerErr = Join-Path $logRoot "broker.stderr.log"
$tunnelOut = Join-Path $logRoot "cloudflared.stdout.log"
$tunnelErr = Join-Path $logRoot "cloudflared.stderr.log"
$cloudflared = (Get-Command cloudflared -ErrorAction Stop).Source

New-Item -ItemType Directory -Force -Path $localRoot, $logRoot, $dataRoot, $artifactRoot | Out-Null

$state = @{}
if (Test-Path $runtimeStatePath) {
    try {
        $state = Get-Content -Path $runtimeStatePath -Raw | ConvertFrom-Json -AsHashtable
    } catch {
        $state = @{}
    }
}

if (-not $state.BROKER_BOOTSTRAP_SECRET) {
    $state.BROKER_BOOTSTRAP_SECRET = New-UrlSafeToken -ByteCount 32
}
if (-not $state.BROKER_JWT_SECRET) {
    $state.BROKER_JWT_SECRET = New-UrlSafeToken -ByteCount 48
}
if (-not $state.BROKER_SANDBOX_OWNER_TOKEN) {
    $state.BROKER_SANDBOX_OWNER_TOKEN = New-UrlSafeToken -ByteCount 32
}

Stop-TrackedProcess -State $state -Name "broker_pid"
Stop-TrackedProcess -State $state -Name "cloudflared_pid"

if (-not (Test-Path $SandboxRepoRoot)) {
    throw "Sandbox repo root not found: $SandboxRepoRoot"
}

$imagePresent = docker image ls --format "{{.Repository}}:{{.Tag}}" | Where-Object { $_ -eq $SandboxImage }
if (-not $imagePresent) {
    python (Join-Path $SandboxRepoRoot "scripts\build_agent_sandbox_image.py") --target-image $SandboxImage
}

python -m pip install -e (Join-Path $repoRoot "broker") | Out-Null

Remove-Item -Force -ErrorAction SilentlyContinue $brokerOut, $brokerErr, $tunnelOut, $tunnelErr

$tunnelProcess = Start-Process -FilePath $cloudflared `
    -ArgumentList @("tunnel", "--url", "http://$BrokerHost`:$BrokerPort", "--no-autoupdate") `
    -WorkingDirectory $repoRoot `
    -RedirectStandardOutput $tunnelOut `
    -RedirectStandardError $tunnelErr `
    -PassThru

$deadline = (Get-Date).AddMinutes(2)
$publicUrl = $null
while ((Get-Date) -lt $deadline) {
    Start-Sleep -Seconds 2
    $logText = Read-LogText -Paths @($tunnelOut, $tunnelErr)
    $match = [regex]::Match($logText, 'https://[-a-z0-9]+\.trycloudflare\.com')
    if ($match.Success) {
        $publicUrl = $match.Value
        break
    }
}
if (-not $publicUrl) {
    throw "cloudflared did not produce a temporary public URL. Check $tunnelErr"
}

$env:BROKER_PUBLIC_BASE_URL = $publicUrl
$env:BROKER_BOOTSTRAP_SECRET = $state.BROKER_BOOTSTRAP_SECRET
$env:BROKER_JWT_SECRET = $state.BROKER_JWT_SECRET
$env:BROKER_DATA_DIR = $dataRoot
$env:BROKER_ARTIFACT_DIR = $artifactRoot
$env:BROKER_BIND_HOST = $BrokerHost
$env:BROKER_BIND_PORT = "$BrokerPort"
$env:BROKER_SANDBOX_REPO_ROOT = $SandboxRepoRoot
$env:BROKER_SANDBOX_IMAGE = $SandboxImage
$env:BROKER_SANDBOX_OWNER_ID = $SandboxOwnerId
$env:BROKER_SANDBOX_OWNER_TOKEN = $state.BROKER_SANDBOX_OWNER_TOKEN
$env:BROKER_SANDBOX_RUNTIME_SOURCE = "C:\Users\Tyler\Downloads\chatgpt-local-mcp-gateway\chatgpt-local-mcp-gateway\repo_mcp\blender_tcp_runtime.py"

python (Join-Path $repoRoot "infra\local\ensure_local_runtime.py") | Out-Null

$brokerProcess = Start-Process -FilePath "python" `
    -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", $BrokerHost, "--port", "$BrokerPort") `
    -WorkingDirectory (Join-Path $repoRoot "broker") `
    -RedirectStandardOutput $brokerOut `
    -RedirectStandardError $brokerErr `
    -PassThru

$healthDeadline = (Get-Date).AddMinutes(2)
$health = $null
while ((Get-Date) -lt $healthDeadline) {
    Start-Sleep -Seconds 2
    try {
        $health = Invoke-RestMethod -Uri "http://$BrokerHost`:$BrokerPort/health" -Method Get -TimeoutSec 10
        if ($health.ok) {
            break
        }
    } catch {
    }
}
if (-not $health -or -not $health.ok) {
    throw "Broker did not become healthy. Check $brokerErr"
}

$state.public_url = $publicUrl
$state.broker_pid = $brokerProcess.Id
$state.cloudflared_pid = $tunnelProcess.Id
$state.broker_port = $BrokerPort
$state.broker_host = $BrokerHost
$state.sandbox_repo_root = $SandboxRepoRoot
$state.sandbox_image = $SandboxImage
$state.sandbox_owner_id = $SandboxOwnerId
$state.viewer_url = $health.viewer_url
$state.updated_at = (Get-Date).ToString("o")
$state | ConvertTo-Json -Depth 6 | Set-Content -Path $runtimeStatePath -Encoding UTF8

Write-Host ""
Write-Host "Local broker stack is ready." -ForegroundColor Green
Write-Host ""
Write-Host "BROKER_PUBLIC_BASE_URL=$publicUrl"
Write-Host "BROKER_BOOTSTRAP_SECRET=$($state.BROKER_BOOTSTRAP_SECRET)"
if ($health.viewer_url) {
    Write-Host "BROKER_VIEWER_BASE_URL=$($health.viewer_url)"
}
Write-Host ""
Write-Host "Codex environment values:" -ForegroundColor Cyan
Write-Host "BROKER_PUBLIC_BASE_URL=$publicUrl"
Write-Host "ADDON_ROOT=src/warp_forge"
Write-Host "ADDON_MODULE=warp_forge"
Write-Host "SNAPSHOT_MODE=tarball"
