from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse

from app.models import JobCreateRequest, JobRecord
from app.services.auth import require_agent_token
from app.services.job_service import create_job, load_job

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobRecord)
def submit_job(request: JobCreateRequest, _: dict = Depends(require_agent_token)) -> JobRecord:
    return create_job(request)


@router.get("/{job_id}", response_model=JobRecord)
def get_job(job_id: str, _: dict = Depends(require_agent_token)) -> JobRecord:
    return load_job(job_id)


@router.get("/{job_id}/artifacts")
def get_job_artifacts(job_id: str, _: dict = Depends(require_agent_token)) -> JSONResponse:
    record = load_job(job_id)
    artifact_dir = Path(record.artifact_dir or "")
    if not artifact_dir.exists():
        raise HTTPException(status_code=404, detail="artifact directory not found")
    return JSONResponse(
        {
            "job_id": job_id,
            "artifact_dir": str(artifact_dir),
            "files": sorted([path.name for path in artifact_dir.iterdir() if path.is_file()]),
        }
    )


@router.get("/{job_id}/artifacts/{filename}")
def get_job_artifact_file(job_id: str, filename: str, _: dict = Depends(require_agent_token)) -> FileResponse:
    record = load_job(job_id)
    path = Path(record.artifact_dir or "") / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="artifact file not found")
    return FileResponse(path)
