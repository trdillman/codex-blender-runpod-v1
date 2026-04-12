from __future__ import annotations

from fastapi import APIRouter, Depends

from app.services.auth import require_agent_token

router = APIRouter(prefix="/provision", tags=["provision"])


@router.get("/capabilities")
def capabilities(_: dict = Depends(require_agent_token)) -> dict:
    return {
        "warp": True,
        "privileged_provisioning": False,
        "note": "v1 assumes Warp is preinstalled in the image or available via vendored wheels.",
    }
