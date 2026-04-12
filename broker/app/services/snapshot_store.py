from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import BinaryIO

from app.config import settings
from app.models import SnapshotResponse

SNAPSHOT_DIR = settings.broker_data_dir / "snapshots"
SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)


def store_snapshot(*, upload: BinaryIO, base_sha: str, addon_root: str, module_name: str) -> SnapshotResponse:
    raw = upload.read()
    digest = hashlib.sha256(raw).hexdigest()
    snapshot_id = f"snap_{digest[:16]}"
    blob_path = SNAPSHOT_DIR / f"{snapshot_id}.tar.gz"
    meta_path = SNAPSHOT_DIR / f"{snapshot_id}.json"
    stored_at = datetime.now(UTC)

    if not blob_path.exists():
        blob_path.write_bytes(raw)
        meta_path.write_text(
            json.dumps(
                {
                    "snapshot_id": snapshot_id,
                    "base_sha": base_sha,
                    "addon_root": addon_root,
                    "module_name": module_name,
                    "stored_at": stored_at.isoformat(),
                    "size_bytes": len(raw),
                    "blob_path": str(blob_path),
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    return SnapshotResponse(
        snapshot_id=snapshot_id,
        base_sha=base_sha,
        addon_root=addon_root,
        module_name=module_name,
        stored_at=stored_at,
        size_bytes=len(raw),
    )


def snapshot_blob_path(snapshot_id: str) -> Path:
    return SNAPSHOT_DIR / f"{snapshot_id}.tar.gz"
