from __future__ import annotations

from fastapi import APIRouter, Depends

from app.services.auth import require_agent_token
from app.services.local_sandbox import viewer_url

router = APIRouter(prefix="/provision", tags=["provision"])


@router.get("/capabilities")
def capabilities(_: dict = Depends(require_agent_token)) -> dict:
    return {
        "backend": "local-agent-sandbox",
        "warp": True,
        "viewer_url": viewer_url(),
        "temporary_public_url": True,
        "privileged_provisioning": False,
        "note": "v1 uses the local Docker Blender sandbox and a temporary Cloudflare broker URL.",
    }
