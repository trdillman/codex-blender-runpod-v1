#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/data /workspace/artifacts /workspace/jobs

cd /opt/codex/broker
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080 &
BROKER_PID=$!

/init &
INIT_PID=$!

cleanup() {
  kill "$BROKER_PID" >/dev/null 2>&1 || true
  kill "$INIT_PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

wait -n "$BROKER_PID" "$INIT_PID"
