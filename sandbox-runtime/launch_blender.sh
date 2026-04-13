#!/usr/bin/env bash
set -euo pipefail
BLENDER_BIN="${BLENDER_BIN:-blender}"
RUNTIME_SCRIPT="/opt/codex/sandbox-runtime/blender_runtime/blender_tcp_runtime.py"
"$BLENDER_BIN" --background --factory-startup --python "$RUNTIME_SCRIPT" "$@" &
