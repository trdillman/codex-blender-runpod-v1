#!/usr/bin/env bash
set -euo pipefail

python3 -m pip install --upgrade pip
python3 -m pip install -r codex/requirements.txt

python3 - <<'PY'
import json
import os
from pathlib import Path
import requests

base_url = os.environ['BROKER_PUBLIC_BASE_URL'].rstrip('/')
secret = os.environ['BROKER_BOOTSTRAP_SECRET']
response = requests.post(
    f"{base_url}/auth/bootstrap",
    headers={"x-bootstrap-secret": secret},
    timeout=30,
)
response.raise_for_status()
payload = response.json()
with Path.home().joinpath('.bashrc').open('a', encoding='utf-8') as handle:
    handle.write(f"\nexport BROKER_AGENT_TOKEN='{payload['token']}'\n")
print(json.dumps({"bootstrapped": True, "token_ttl": payload['expires_in_seconds']}))
PY
