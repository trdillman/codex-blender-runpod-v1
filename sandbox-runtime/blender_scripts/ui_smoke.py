from __future__ import annotations

import json
from pathlib import Path

import bpy  # type: ignore


def run(output_path: str) -> None:
    area_types = [area.type for area in bpy.context.screen.areas]
    payload = {
        "screen": bpy.context.screen.name if bpy.context.screen else None,
        "area_types": area_types,
        "has_view3d": "VIEW_3D" in area_types,
    }
    Path(output_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
