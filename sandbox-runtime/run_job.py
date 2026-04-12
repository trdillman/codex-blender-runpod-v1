from __future__ import annotations

import argparse
import json
import shutil
import tarfile
from pathlib import Path

from local_runtime_client import RuntimeClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--addon-root", required=True)
    parser.add_argument("--module-name", required=True)
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--blend-file")
    parser.add_argument("--checks-json", default='["registration","ui_smoke","playback_smoke"]')
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    artifact_dir = Path(args.artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    checks = json.loads(args.checks_json)
    runtime = RuntimeClient()

    snapshot_extract_root = artifact_dir / "snapshot"
    snapshot_extract_root.mkdir(parents=True, exist_ok=True)
    with tarfile.open(args.snapshot, "r:gz") as handle:
        handle.extractall(snapshot_extract_root)

    addon_root_path = snapshot_extract_root / args.addon_root
    if not addon_root_path.exists():
        raise SystemExit(f"addon root not found inside snapshot: {addon_root_path}")

    addon_zip_base = artifact_dir / args.module_name
    shutil.make_archive(addon_zip_base.as_posix(), "zip", addon_root_path)
    addon_zip_path = addon_zip_base.with_suffix(".zip")

    result = {
        "job_id": args.job_id,
        "checks": {},
        "status": "running",
        "requested_checks": checks,
    }

    result["runtime"] = runtime.request({"command": "ping"})
    result["addon_install"] = runtime.request({"command": "install_addon_zip", "zip_path": str(addon_zip_path)})
    result["addon_enable"] = runtime.request({"command": "enable_addon", "module_name": args.module_name})
    result["checks"]["registration"] = runtime.request({"command": "scene_info"})

    screenshot_path = artifact_dir / "viewport.png"
    try:
        result["checks"]["viewport_screenshot"] = runtime.request({"command": "viewport_screenshot", "filepath": str(screenshot_path)})
    except Exception as exc:  # noqa: BLE001
        result["checks"]["viewport_screenshot"] = {"status": "error", "message": str(exc)}

    result["checks"]["ui_smoke"] = {"status": "todo", "note": "connect script-file invocation after live Pod validation"}
    result["checks"]["playback_smoke"] = {"status": "todo", "note": "replace placeholder with timed playback + viewer capture in the real Pod"}

    result["status"] = "succeeded"
    (artifact_dir / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
