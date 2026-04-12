from __future__ import annotations

from fastapi import APIRouter, Depends

from app.models import BootstrapResponse
from app.services.auth import issue_agent_token, require_bootstrap_secret

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/bootstrap", response_model=BootstrapResponse)
def bootstrap(_: None = Depends(require_bootstrap_secret)) -> BootstrapResponse:
    token, ttl = issue_agent_token()
    return BootstrapResponse(token=token, expires_in_seconds=ttl)
