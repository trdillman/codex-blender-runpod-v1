# Prompt for a local shell-capable agent

```text
You are bootstrapping a single Runpod Pod for the Codex Blender Runpod Bridge v1 project.

Use the repo files under:
- infra/runpod/
- sandbox-image/
- .github/workflows/
- docs/

Tasks:
1. Verify the required environment variables are set.
2. Build and publish the sandbox image to the configured registry.
3. Create the Pod using infra/runpod/deploy_pod.py.
4. Print the resulting broker URL and viewer URL.
5. Smoke test GET /health on the broker.
6. Do not make broader infrastructure changes.
```
