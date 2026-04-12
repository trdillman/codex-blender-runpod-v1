from __future__ import annotations

import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path

from app.config import settings
from app.models import JobCreateRequest, JobRecord
from app.services.sandbox_executor import execute_job

JOB_DIR = settings.broker_data_dir / "jobs"
JOB_DIR.mkdir(parents=True, exist_ok=True)
_LOCK = threading.Lock()


def _job_path(job_id: str) -> Path:
    return JOB_DIR / f"{job_id}.json"


def save_job(record: JobRecord) -> None:
    _job_path(record.job_id).write_text(record.model_dump_json(indent=2), encoding="utf-8")


def load_job(job_id: str) -> JobRecord:
    return JobRecord.model_validate_json(_job_path(job_id).read_text(encoding="utf-8"))


def create_job(request: JobCreateRequest) -> JobRecord:
    now = datetime.now(UTC)
    job_id = f"job_{uuid.uuid4().hex[:12]}"
    record = JobRecord(job_id=job_id, status="queued", created_at=now, updated_at=now, request=request)
    save_job(record)
    threading.Thread(target=_run_job, args=(job_id,), daemon=True).start()
    return record


def _run_job(job_id: str) -> None:
    with _LOCK:
        record = load_job(job_id)
        record.status = "running"
        record.updated_at = datetime.now(UTC)
        save_job(record)

    ok, error, artifact_dir = execute_job(job_id, record.request.model_dump())

    record = load_job(job_id)
    record.status = "succeeded" if ok else "failed"
    record.updated_at = datetime.now(UTC)
    record.artifact_dir = str(artifact_dir)
    record.result_path = str(artifact_dir / "result.json")
    record.error = error
    save_job(record)
