from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.models import SnapshotResponse
from app.services.auth import require_agent_token
from app.services.snapshot_store import store_snapshot

router = APIRouter(prefix="/snapshots", tags=["snapshots"])


@router.post("", response_model=SnapshotResponse)
def create_snapshot(
    base_sha: str = Form(...),
    addon_root: str = Form(...),
    module_name: str = Form(...),
    bundle: UploadFile = File(...),
    _: dict = Depends(require_agent_token),
) -> SnapshotResponse:
    return store_snapshot(upload=bundle.file, base_sha=base_sha, addon_root=addon_root, module_name=module_name)
