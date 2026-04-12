# Minimal user-required steps

Only these actions must be performed manually right now.

1. **Create one Runpod API key**.
2. **Create one GitHub Container Registry destination** for the sandbox image.
3. **Set four secrets / variables**:
   - `RUNPOD_API_KEY`
   - `BROKER_BOOTSTRAP_SECRET`
   - `BROKER_JWT_SECRET`
   - `BROKER_PUBLIC_BASE_URL` once the Pod exists
4. **Build and publish the sandbox image** using the provided GitHub workflow or local script.
5. **Create one Pod** using `infra/runpod/deploy_pod.py`.
6. **Configure one Codex Cloud environment** using the scripts and values in `docs/codex-environment.md`.

Everything else in v1 is designed to be agent-callable.
