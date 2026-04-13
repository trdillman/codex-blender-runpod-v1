#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/data /workspace/artifacts /workspace/jobs
mkdir -p /opt/codex/viewer
cat >/opt/codex/viewer/index.html <<'EOF'
<!doctype html>
<html lang="en">
  <head><meta charset="utf-8"><title>Codex Blender Viewer</title></head>
  <body>
    <h1>Codex Blender Viewer</h1>
    <p>The broker is running. Live viewer wiring is pending runtime integration.</p>
  </body>
</html>
EOF

cd /opt/codex/broker
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080 &
BROKER_PID=$!

python3 -m http.server 3001 --directory /opt/codex/viewer &
VIEWER_PID=$!

cleanup() {
  kill "$BROKER_PID" >/dev/null 2>&1 || true
  kill "$VIEWER_PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

wait -n "$BROKER_PID" "$VIEWER_PID"
