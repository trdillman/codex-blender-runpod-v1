# Local Docker Broker Setup

This repo now supports a local Docker-backed broker path for Codex Cloud.

## One-time prerequisites

- Docker Desktop running
- `cloudflared` installed and on `PATH`
- The local sandbox repo available at `C:\Users\Tyler\Documents\Playground\blender-edgebox-sandbox`

## Start the stack

From the repo root:

```powershell
pwsh -File .\infra\local\start_local_stack.ps1
```

The launcher will:

1. build `agent-sandbox-blender:local` if needed
2. generate or reuse the broker secrets in `.local/local-stack.json`
3. start a temporary `cloudflared` URL
4. start the local Blender sandbox runtime
5. start the FastAPI broker on `127.0.0.1`
6. print the current `BROKER_PUBLIC_BASE_URL`

## Codex environment values

Use the printed temporary URL for:

```text
BROKER_PUBLIC_BASE_URL=<printed trycloudflare URL>
```

The bootstrap secret is also printed by the launcher and should be set as:

```text
BROKER_BOOTSTRAP_SECRET=<printed secret>
```

The viewer stays local-first. The broker reports the current local viewer URL from the sandbox when available.
