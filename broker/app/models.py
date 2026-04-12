from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class BootstrapResponse(BaseModel):
    token: str
    expires_in_seconds: int


class SnapshotResponse(BaseModel):
    snapshot_id: str
    base_sha: str
    addon_root: str
    module_name: str
    stored_at: datetime
    size_bytes: int


class JobCreateRequest(BaseModel):
    snapshot_id: str
    base_sha: str
    addon_root: str
    module_name: str
    blend_file: str | None = None
    checks: list[str] = Field(default_factory=lambda: ["registration", "ui_smoke", "playback_smoke"])


class JobRecord(BaseModel):
    job_id: str
    status: Literal["queued", "running", "succeeded", "failed"]
    created_at: datetime
    updated_at: datetime
    request: JobCreateRequest
    result_path: str | None = None
    artifact_dir: str | None = None
    error: str | None = None


class ViewerTokenResponse(BaseModel):
    viewer_url: str | None
    token: str | None = None
    expires_in_seconds: int | None = None
