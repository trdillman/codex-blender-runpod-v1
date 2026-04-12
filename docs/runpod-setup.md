# Runpod setup

## Target Pod profile

- Provider: Runpod Pods
- Pod type: Secure Cloud preferred, Community Cloud acceptable for lower-cost testing
- GPU priority list:
  1. `NVIDIA GeForce RTX 4070 Ti`
  2. `NVIDIA GeForce RTX 3090`
- Ports:
  - `8080/http` broker
  - `3001/http` viewer
  - `22/tcp` optional operator SSH
- Persistent volume mount: `/workspace`

## Why this profile

The workload needs moderate GPU capability for viewport simulation and UI checks, not max-tier rendering. RTX 4070 Ti is usually enough; RTX 3090 is the fallback when availability or VRAM is better.

## Image strategy

Build one custom image from `sandbox-image/Dockerfile` and publish it to GHCR. The Pod runs that image directly.

## Create the Pod

### Option A: REST API helper

```bash
python infra/runpod/deploy_pod.py
```

### Option B: Runpod CLI

```bash
runpodctl config --apiKey "$RUNPOD_API_KEY"
runpodctl create pod \
  --name "$RUNPOD_NAME" \
  --gpuType "NVIDIA GeForce RTX 4070 Ti" \
  --gpuCount 1 \
  --imageName "$RUNPOD_IMAGE" \
  --secureCloud \
  --containerDiskSize 40 \
  --volumeSize 80
```
