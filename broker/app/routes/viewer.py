from __future__ import annotations

from fastapi import APIRouter, Depends

from app.models import ViewerTokenResponse
from app.services.auth import require_agent_token
from app.services.local_sandbox import viewer_url

router = APIRouter(prefix="/viewer", tags=["viewer"])


@router.post("/token", response_model=ViewerTokenResponse)
def viewer_token(_: dict = Depends(require_agent_token)) -> ViewerTokenResponse:
    return ViewerTokenResponse(viewer_url=viewer_url())
