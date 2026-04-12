# Codex Blender Runpod Bridge v1

Directly callable Runpod-backed Blender GPU sandbox for Codex Cloud addon development.

## Included in this scaffold

- A **broker** API that Codex Cloud can call over HTTPS.
- A **snapshot pipeline** so Blender runs the exact addon state Codex is editing.
- A **Runpod Pod deployment** skeleton using a single Pod topology.
- A **sandbox image** scaffold with Blender UI, viewer exposure, and NVIDIA Warp installation.
- A **Codex environment** setup and maintenance flow.
- A **minimal user action plan**.

## Locked decisions

- Provider: **Runpod Pods**
- GPU target: **RTX 4070 Ti preferred**, **RTX 3090 fallback**
- Network shape: **Codex Cloud -> HTTPS broker -> warm Runpod Blender sandbox**
- Sync model: **base SHA + overlay snapshot**
- Auth shape: **Codex setup-script bootstrap secret -> short-lived broker token**
- Tooling: **Warp via pip or vendored wheel**, not broad host-shell package installation in v1
- Viewer: **basic browser-accessible UI is enough for v1**

## Repo layout

```text
AGENTS.md               Codex working loop
broker/                 FastAPI broker API
codex/                  Codex Cloud setup + helper client scripts
docs/                   Architecture, setup, auth, pipeline, references
infra/runpod/           Pod creation payload and deployment helper
sandbox-image/          Runpod image scaffold
sandbox-runtime/        Blender runtime bridge + job runner + scripts
.github/workflows/      Image build/push automation
prompts/local/          Prompt for a local shell-capable agent
```

## Fast start

1. Read `docs/minimal-user-steps.md`.
2. Build and publish the sandbox image with `.github/workflows/build-sandbox-image.yml` or locally.
3. Create the Pod with `infra/runpod/deploy_pod.py`.
4. Configure the Codex environment using `docs/codex-environment.md`.
5. Let Codex use `codex/upload_snapshot.py` and `codex/submit_job.py` from the environment.
