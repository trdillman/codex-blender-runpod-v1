from __future__ import annotations

from pathlib import Path

from app.config import settings


def artifact_dir_for_job(job_id: str) -> Path:
    path = settings.broker_artifact_dir / job_id
    path.mkdir(parents=True, exist_ok=True)
    return path
