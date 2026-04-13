from __future__ import annotations

import hashlib
import importlib
import json
import shutil
import sys
import tarfile
from pathlib import Path, PurePosixPath
from typing import Any

from app.config import settings

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _sandbox_owner_token() -> str:
    _, state = _runtime_modules()
    existing = state.sandbox_record(settings.broker_sandbox_owner_id)
    existing_token = str((existing or {}).get("owner_token") or "").strip()
    if existing_token:
        return existing_token
    if settings.broker_sandbox_owner_token:
        return settings.broker_sandbox_owner_token
    digest = hashlib.sha256(settings.broker_jwt_secret.encode("utf-8")).hexdigest()
    return f"codex-local-{digest[:32]}"


def _configure_runtime_environment() -> None:
    sys.path.insert(0, str((settings.broker_sandbox_repo_root / "src").resolve()))
    sys.path = list(dict.fromkeys(sys.path))
    runtime_source = settings.broker_sandbox_runtime_source.resolve()
    if not runtime_source.exists():
        raise RuntimeError(f"broker sandbox runtime source not found: {runtime_source}")
    sandbox_root = settings.broker_sandbox_repo_root.resolve()
    if not sandbox_root.exists():
        raise RuntimeError(f"broker sandbox repo not found: {sandbox_root}")
    # Reuse the existing local Docker sandbox runtime, but point it at this repo's runtime script.
    import os

    os.environ.setdefault("AGENT_SANDBOX_IMAGE", settings.broker_sandbox_image)
    os.environ.setdefault("AGENT_SANDBOX_RUNTIME_SOURCE", str(runtime_source))


def _runtime_modules() -> tuple[Any, Any]:
    _configure_runtime_environment()
    runtime = importlib.import_module("agent_sandbox_mcp.runtime")
    state = importlib.import_module("agent_sandbox_mcp.state")
    if not getattr(runtime, "_CODEX_BROKER_SUPPRESS_BROWSER_OPEN", False):
        runtime._open_url_once = lambda url: {"opened_url": url, "open_reason": "suppressed_by_broker"}  # type: ignore[attr-defined]
        runtime._CODEX_BROKER_SUPPRESS_BROWSER_OPEN = True  # type: ignore[attr-defined]
    return runtime, state


def _owner_credentials() -> tuple[str, str]:
    return settings.broker_sandbox_owner_id, _sandbox_owner_token()


def _owner_layout() -> dict[str, Path]:
    _, state = _runtime_modules()
    layout = state.ensure_owner_layout(settings.broker_sandbox_owner_id)
    return {key: Path(value).resolve() for key, value in layout.items()}


def _host_path_to_remote(host_path: str | Path) -> str:
    layout = _owner_layout()
    root = layout["root"]
    relative = Path(host_path).resolve().relative_to(root)
    return PurePosixPath("/workspace", *relative.parts).as_posix()


def ensure_sandbox() -> dict[str, Any]:
    runtime, _ = _runtime_modules()
    owner_id, owner_token = _owner_credentials()
    return runtime.connect_sandbox(owner_id, owner_token, gpu=settings.broker_sandbox_gpu)


def sandbox_snapshot(*, tail_lines: int = 40) -> dict[str, Any]:
    runtime, _ = _runtime_modules()
    owner_id, owner_token = _owner_credentials()
    ensure_sandbox()
    return runtime.sandbox_snapshot(owner_id, owner_token, tail_lines=tail_lines)


def ensure_runtime_ready() -> dict[str, Any]:
    runtime, _ = _runtime_modules()
    owner_id, owner_token = _owner_credentials()
    ensure_sandbox()
    try:
        snapshot = runtime.sandbox_snapshot(owner_id, owner_token, tail_lines=25)
        if bool(((snapshot.get("runtime") or {}).get("healthy"))):
            return snapshot
    except Exception:
        pass
    runtime.launch_blender(owner_id, owner_token, gpu=settings.broker_sandbox_gpu)
    return runtime.sandbox_snapshot(owner_id, owner_token, tail_lines=25)


def viewer_url() -> str | None:
    try:
        snapshot = sandbox_snapshot(tail_lines=10)
    except Exception:
        return settings.broker_viewer_base_url
    viewer = snapshot.get("viewer") or {}
    return str(viewer.get("viewer_url") or settings.broker_viewer_base_url or "").strip() or None


def health_summary() -> dict[str, Any]:
    try:
        snapshot = sandbox_snapshot(tail_lines=15)
        runtime_data = snapshot.get("runtime") or {}
        viewer = snapshot.get("viewer") or {}
        container = snapshot.get("container") or {}
        return {
            "ok": True,
            "backend": "local-agent-sandbox",
            "broker_public_base_url": settings.broker_public_base_url,
            "viewer_url": str(viewer.get("viewer_url") or settings.broker_viewer_base_url or "").strip() or None,
            "runtime": {
                "host": settings.broker_runtime_host,
                "port": runtime_data.get("host_port") or settings.broker_runtime_port,
                "healthy": bool(runtime_data.get("healthy")),
                "url": (runtime_data.get("url") or None),
            },
            "sandbox": {
                "owner_id": settings.broker_sandbox_owner_id,
                "image": ((container.get("inspect") or {}).get("config") or {}).get("image"),
                "running": ((container.get("inspect") or {}).get("state") or {}).get("running"),
                "viewer_health": viewer.get("viewer_health"),
            },
        }
    except Exception as exc:
        return {
            "ok": False,
            "backend": "local-agent-sandbox",
            "broker_public_base_url": settings.broker_public_base_url,
            "viewer_url": settings.broker_viewer_base_url,
            "runtime": {
                "host": settings.broker_runtime_host,
                "port": settings.broker_runtime_port,
                "healthy": False,
                "url": None,
            },
            "sandbox": {
                "owner_id": settings.broker_sandbox_owner_id,
                "running": False,
                "error": str(exc),
            },
        }


def materialize_snapshot(snapshot_id: str, snapshot_path: str | Path, *, addon_root: str, module_name: str) -> dict[str, Any]:
    owner_layout = _owner_layout()
    materialized_root = owner_layout["uploads"] / "snapshot-materialized" / snapshot_id
    source_root = materialized_root / "source"
    archive_root = materialized_root / "archives"
    bundle_root = materialized_root / "bundle"
    addon_source = source_root / addon_root

    if not addon_source.exists():
        if source_root.exists():
            shutil.rmtree(source_root, ignore_errors=True)
        source_root.mkdir(parents=True, exist_ok=True)
        with tarfile.open(Path(snapshot_path), "r:gz") as handle:
            handle.extractall(source_root)

    if not addon_source.exists():
        raise RuntimeError(f"addon root not found inside snapshot: {addon_source}")

    archive_root.mkdir(parents=True, exist_ok=True)
    archive_base = archive_root / module_name
    zip_path = archive_base.with_suffix(".zip")
    if not zip_path.exists():
        bundle_addon_root = bundle_root / module_name
        if bundle_root.exists():
            shutil.rmtree(bundle_root, ignore_errors=True)
        bundle_addon_root.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(addon_source, bundle_addon_root)
        shutil.make_archive(
            archive_base.as_posix(),
            "zip",
            root_dir=bundle_root,
            base_dir=module_name,
        )

    metadata = {
        "snapshot_id": snapshot_id,
        "host_materialized_root": str(materialized_root),
        "host_source_root": str(source_root),
        "host_addon_root": str(addon_source),
        "host_addon_zip": str(zip_path),
        "host_bundle_root": str(bundle_root),
        "remote_source_root": _host_path_to_remote(source_root),
        "remote_addon_root": _host_path_to_remote(addon_source),
        "remote_addon_zip": _host_path_to_remote(zip_path),
        "addon_root": addon_root,
        "module_name": module_name,
    }
    (materialized_root / "snapshot.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def _execute_json_code(python_body: str) -> dict[str, Any]:
    runtime, _ = _runtime_modules()
    owner_id, owner_token = _owner_credentials()
    ensure_runtime_ready()
    return runtime._execute_json_code(owner_id, owner_token, python_body)


def install_snapshot_addon(snapshot: dict[str, Any]) -> dict[str, Any]:
    addon_zip = snapshot["remote_addon_zip"]
    module_name = snapshot["module_name"]
    return _execute_json_code(
        f"""
import addon_utils
addon_path = {addon_zip!r}
module_name = {module_name!r}
before_modules = {{module.__name__ for module in addon_utils.modules()}}
before_enabled = sorted(bpy.context.preferences.addons.keys())
if module_name in bpy.context.preferences.addons:
    try:
        bpy.ops.preferences.addon_disable(module=module_name)
    except Exception:
        pass
bpy.ops.preferences.addon_install(filepath=addon_path, overwrite=True)
after_modules = {{module.__name__ for module in addon_utils.modules()}}
enable_error = None
enabled = False
try:
    bpy.ops.preferences.addon_enable(module=module_name)
    enabled = module_name in bpy.context.preferences.addons
except Exception as exc:
    enable_error = str(exc)
try:
    bpy.ops.wm.save_userpref()
except Exception:
    pass
result = {{
    "addon_path": addon_path,
    "module_name": module_name,
    "enabled": enabled,
    "enable_error": enable_error,
    "available_modules": sorted(after_modules),
    "new_modules": sorted(after_modules - before_modules),
    "enabled_modules": sorted(bpy.context.preferences.addons.keys()),
    "enabled_modules_before": before_enabled,
}}
"""
    )


def open_blend_file(path: str) -> dict[str, Any]:
    runtime, _ = _runtime_modules()
    owner_id, owner_token = _owner_credentials()
    ensure_runtime_ready()
    return runtime.open_blend_file(owner_id, owner_token, path)


def scene_info() -> dict[str, Any]:
    runtime, _ = _runtime_modules()
    owner_id, owner_token = _owner_credentials()
    ensure_runtime_ready()
    return runtime.get_scene_info(owner_id, owner_token)


def list_installed_addons() -> dict[str, Any]:
    runtime, _ = _runtime_modules()
    owner_id, owner_token = _owner_credentials()
    ensure_runtime_ready()
    return runtime.list_installed_addons(owner_id, owner_token)


def ui_smoke() -> dict[str, Any]:
    return _execute_json_code(
        """
area_types = [area.type for area in bpy.context.screen.areas]
result = {
    "screen": bpy.context.screen.name if bpy.context.screen else None,
    "area_types": area_types,
    "has_view3d": "VIEW_3D" in area_types,
}
"""
    )


def placeholder_playback_smoke() -> dict[str, Any]:
    return {
        "runtime_response": None,
        "parsed_result": {
            "status": "skipped",
            "note": "playback smoke remains a placeholder in the local broker v1 path",
        },
    }


def capture_viewport(target_path: str | Path) -> dict[str, Any]:
    runtime, _ = _runtime_modules()
    owner_id, owner_token = _owner_credentials()
    ensure_runtime_ready()
    payload = runtime.viewport_screenshot(owner_id, owner_token, filename=Path(target_path).name)
    exported = ((payload.get("exported_file") or {}).get("host_path")) or ""
    source_path = Path(exported)
    destination = Path(target_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source_path.exists():
        shutil.copy2(source_path, destination)
    return {
        **payload,
        "copied_to": str(destination),
        "copied": destination.exists(),
    }
