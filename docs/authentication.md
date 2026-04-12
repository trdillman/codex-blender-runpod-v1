# Authentication and secrets

## v1 model

### Setup phase

Codex setup has access to `BROKER_BOOTSTRAP_SECRET`.

The setup script calls:

- `POST /auth/bootstrap`

The broker validates the secret and returns a short-lived bearer token.

### Agent phase

The setup script writes the short-lived token into `~/.bashrc` as `BROKER_AGENT_TOKEN`.

All runtime API calls use:

```http
Authorization: Bearer <BROKER_AGENT_TOKEN>
```

## Viewer auth

Viewer access is intentionally separate from broker job auth.

The broker exposes:

- `POST /viewer/token`
