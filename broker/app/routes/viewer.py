from __future__ import annotations

from fastapi import APIRouter, Depends

from app.config import settings
from app.models import ViewerTokenResponse
from app.services.auth import require_agent_token

router = APIRouter(prefix="/viewer", tags=["viewer"])


@router.post("/token", response_model=ViewerTokenResponse)
def viewer_token(_: dict = Depends(require_agent_token)) -> ViewerTokenResponse:
    return ViewerTokenResponse(viewer_url=settings.broker_viewer_base_url)
