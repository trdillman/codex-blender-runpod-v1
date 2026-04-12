from __future__ import annotations

"""
Playback smoke scaffold.

This is intentionally conservative in v1.
It does not yet guarantee a fully reliable real-time viewport metric across all desktop stacks.
Instead it captures a minimal signal path that can be hardened on the real Pod.
"""

import json
import time
from pathlib import Path

import bpy  # type: ignore

_RESULT = {}
_START = time.monotonic()
_START_FRAME = int(bpy.context.scene.frame_current)
_DURATION = 2.5
_OUTPUT_PATH = None


def _finish() -> None:
    global _RESULT
    if bpy.context.screen.is_animation_playing:
        bpy.ops.screen.animation_cancel(restore_frame=False)
    _RESULT = {
        "start_frame": _START_FRAME,
        "end_frame": int(bpy.context.scene.frame_current),
        "duration_seconds": round(time.monotonic() - _START, 3),
        "has_view3d": any(area.type == "VIEW_3D" for area in bpy.context.screen.areas),
        "note": "v1 placeholder metric; harden after live Pod validation",
    }
    Path(_OUTPUT_PATH).write_text(json.dumps(_RESULT, indent=2), encoding="utf-8")


def _tick():
    if time.monotonic() - _START >= _DURATION:
        _finish()
        return None
    return 0.1


def run(output_path: str) -> None:
    global _OUTPUT_PATH
    _OUTPUT_PATH = output_path
    bpy.ops.screen.animation_play()
    bpy.app.timers.register(_tick)
