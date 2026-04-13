from __future__ import annotations

import json
import traceback
from pathlib import Path

from app.services.artifact_store import artifact_dir_for_job
from app.services.local_sandbox import (
    capture_viewport,
    ensure_runtime_ready,
    install_snapshot_addon,
    list_installed_addons,
    materialize_snapshot,
    open_blend_file,
    placeholder_playback_smoke,
    scene_info,
    ui_smoke,
    viewer_url,
)
from app.services.snapshot_store import load_snapshot_metadata, snapshot_blob_path


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _resolve_blend_path(materialized: dict, requested: str | None) -> str | None:
    if not requested:
        return None
    candidate = Path(requested)
    if candidate.is_absolute() and candidate.exists():
        return str(candidate)
    source_root = Path(materialized["host_source_root"])
    source_candidate = (source_root / requested).resolve()
    if source_candidate.exists():
        return str(source_candidate)
    return requested


def execute_job(job_id: str, payload: dict) -> tuple[bool, str | None, Path]:
    artifact_dir = artifact_dir_for_job(job_id)
    stdout_lines: list[str] = []
    stderr_lines: list[str] = []
    result_path = artifact_dir / "result.json"

    try:
        snapshot_path = snapshot_blob_path(payload["snapshot_id"])
        snapshot_meta = load_snapshot_metadata(payload["snapshot_id"])
        stdout_lines.append(f"using snapshot {payload['snapshot_id']} from {snapshot_path}")
        runtime_snapshot = ensure_runtime_ready()
        stdout_lines.append("local sandbox runtime is healthy")

        materialized = materialize_snapshot(
            payload["snapshot_id"],
            snapshot_path,
            addon_root=payload["addon_root"],
            module_name=payload["module_name"],
        )
        stdout_lines.append(f"materialized snapshot at {materialized['host_materialized_root']}")

        blend_path = _resolve_blend_path(materialized, payload.get("blend_file"))
        opened_blend = open_blend_file(blend_path) if blend_path else None
        if opened_blend:
            stdout_lines.append(f"opened blend file {blend_path}")

        addon_install = install_snapshot_addon(materialized)
        stdout_lines.append("installed snapshot addon into local Blender sandbox")

        requested_checks = list(payload.get("checks") or [])
        checks: dict[str, object] = {}
        if "registration" in requested_checks:
            checks["registration"] = scene_info()
        if "ui_smoke" in requested_checks:
            checks["ui_smoke"] = ui_smoke()
        if "playback_smoke" in requested_checks:
            checks["playback_smoke"] = placeholder_playback_smoke()

        screenshot_path = artifact_dir / "viewport.png"
        viewport = capture_viewport(screenshot_path)
        checks["viewport_screenshot"] = viewport
        checks["installed_addons"] = list_installed_addons()

        result = {
            "job_id": job_id,
            "status": "succeeded",
            "requested_checks": requested_checks,
            "snapshot": snapshot_meta,
            "materialized_snapshot": materialized,
            "runtime": runtime_snapshot.get("runtime"),
            "viewer_url": viewer_url(),
            "blend_file": blend_path,
            "opened_blend": opened_blend,
            "addon_install": addon_install,
            "checks": checks,
        }
        _write_json(result_path, result)
        return True, None, artifact_dir
    except Exception as exc:  # noqa: BLE001
        stderr_lines.append(traceback.format_exc())
        failure = {
            "job_id": job_id,
            "status": "failed",
            "error": str(exc),
            "requested_checks": list(payload.get("checks") or []),
        }
        _write_json(result_path, failure)
        return False, str(exc), artifact_dir
    finally:
        (artifact_dir / "broker.stdout.log").write_text("\n".join(stdout_lines).strip() + ("\n" if stdout_lines else ""), encoding="utf-8")
        (artifact_dir / "broker.stderr.log").write_text("\n".join(stderr_lines).strip() + ("\n" if stderr_lines else ""), encoding="utf-8")
