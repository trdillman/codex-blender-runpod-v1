from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from app.services.artifact_store import artifact_dir_for_job
from app.services.snapshot_store import snapshot_blob_path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RUN_JOB_SCRIPT = PROJECT_ROOT / "sandbox-runtime" / "run_job.py"


def execute_job(job_id: str, payload: dict) -> tuple[bool, str | None, Path]:
    artifact_dir = artifact_dir_for_job(job_id)
    snapshot_path = snapshot_blob_path(payload["snapshot_id"])
    cmd = [
        sys.executable,
        str(RUN_JOB_SCRIPT),
        "--job-id", job_id,
        "--snapshot", str(snapshot_path),
        "--addon-root", payload["addon_root"],
        "--module-name", payload["module_name"],
        "--artifact-dir", str(artifact_dir),
        "--checks-json", json.dumps(payload.get("checks", [])),
    ]
    if payload.get("blend_file"):
        cmd.extend(["--blend-file", payload["blend_file"]])

    proc = subprocess.run(cmd, capture_output=True, text=True)
    (artifact_dir / "broker.stdout.log").write_text(proc.stdout, encoding="utf-8")
    (artifact_dir / "broker.stderr.log").write_text(proc.stderr, encoding="utf-8")
    ok = proc.returncode == 0
    return ok, None if ok else proc.stderr.strip() or "job execution failed", artifact_dir
