#!/usr/bin/env bash
set -euo pipefail
HOST="${BROKER_RUNTIME_HOST:-127.0.0.1}"
PORT="${BROKER_RUNTIME_PORT:-9876}"

if python3 - <<PY
import socket
s=socket.socket()
s.settimeout(1)
try:
    s.connect(("$HOST", int("$PORT")))
    print("ok")
except Exception:
    raise SystemExit(1)
PY
then
  exit 0
fi

/opt/codex/sandbox-runtime/launch_blender.sh
sleep 8
