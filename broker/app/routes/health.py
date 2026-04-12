from __future__ import annotations

from fastapi import APIRouter

from app.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "broker_public_base_url": settings.broker_public_base_url,
        "viewer_url": settings.broker_viewer_base_url,
        "runtime": {
            "host": settings.broker_runtime_host,
            "port": settings.broker_runtime_port,
        },
    }
