from __future__ import annotations

from fastapi import APIRouter

from app.services.local_sandbox import health_summary

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return health_summary()
