from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from fastapi import Header, HTTPException, status

from app.config import settings


def issue_agent_token(subject: str = "codex-agent") -> tuple[str, int]:
    ttl = settings.broker_token_ttl_seconds
    expires = datetime.now(UTC) + timedelta(seconds=ttl)
    payload: dict[str, Any] = {
        "sub": subject,
        "scope": "agent",
        "exp": expires,
        "iat": datetime.now(UTC),
    }
    token = jwt.encode(payload, settings.broker_jwt_secret, algorithm="HS256")
    return token, ttl


def require_bootstrap_secret(x_bootstrap_secret: str | None = Header(default=None)) -> None:
    if x_bootstrap_secret != settings.broker_bootstrap_secret:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid bootstrap secret")


def require_agent_token(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = jwt.decode(token, settings.broker_jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"invalid bearer token: {exc}") from exc
    if payload.get("scope") != "agent":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="wrong token scope")
    return payload
