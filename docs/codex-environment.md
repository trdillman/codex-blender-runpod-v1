# Codex environment setup

Codex cloud environments are configured in the Codex web settings UI.

## Environment variables

Set these as environment variables:

- `BROKER_PUBLIC_BASE_URL`
- `ADDON_ROOT`
- `ADDON_MODULE`
- `SNAPSHOT_MODE=tarball`

## Secrets

Set this as a **secret**:

- `BROKER_BOOTSTRAP_SECRET`

The setup script exchanges the bootstrap secret for a short-lived bearer token and persists it for the task.

## Setup script

Paste the contents of `codex/setup.sh` into the environment setup script field.

## Maintenance script

Paste the contents of `codex/maintenance.sh` into the environment maintenance script field.

## Internet access

Enable agent internet access and keep it narrow:

- allowlist: broker hostname, plus GitHub only if the task genuinely needs direct GitHub fetches
- methods: `GET`, `HEAD`, `OPTIONS`, `POST`
