# Codex Blender Local Broker v1

Directly callable local Docker-backed Blender sandbox for Codex Cloud addon development.

## Included in this scaffold

- A **broker** API that Codex Cloud can call over HTTPS.
- A **snapshot pipeline** so Blender runs the exact addon state Codex is editing.
- A **local Docker sandbox** bridge that reuses the existing `blender-edgebox-sandbox` runtime.
- A **Windows launcher** that starts the broker, local sandbox, and a temporary `cloudflared` URL.
- A **Codex environment** setup and maintenance flow.
- A **minimal user action plan**.

## Locked decisions

- Provider: **local Docker Blender sandbox**
- Network shape: **Codex Cloud -> temporary HTTPS tunnel -> local broker -> warm local Blender sandbox**
- Sync model: **base SHA + overlay snapshot**
- Auth shape: **Codex setup-script bootstrap secret -> short-lived broker token**
- Viewer: **local browser-accessible UI is enough for v1**

## Repo layout

```text
AGENTS.md               Codex working loop
broker/                 FastAPI broker API
codex/                  Codex Cloud setup + helper client scripts
docs/                   Architecture, setup, auth, pipeline, references
infra/local/            Local broker launcher and runtime bootstrap helper
infra/runpod/           Legacy Pod creation payload and deployment helper
sandbox-image/          Legacy image scaffold
sandbox-runtime/        Blender runtime bridge + scripts
.github/workflows/      Legacy image build/push automation
prompts/local/          Prompt for a local shell-capable agent
```

## Fast start

1. Run `infra/local/start_local_stack.ps1`.
2. Copy the printed `BROKER_PUBLIC_BASE_URL` into the Codex environment.
3. Configure the Codex environment using `docs/codex-environment.md`.
4. Let Codex use `codex/upload_snapshot.py` and `codex/submit_job.py` from the environment.
