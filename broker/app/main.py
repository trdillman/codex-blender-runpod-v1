from __future__ import annotations

from fastapi import FastAPI

from app.routes.auth import router as auth_router
from app.routes.health import router as health_router
from app.routes.jobs import router as jobs_router
from app.routes.provision import router as provision_router
from app.routes.snapshots import router as snapshots_router
from app.routes.viewer import router as viewer_router

app = FastAPI(title="Codex Blender Broker", version="0.1.0")
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(snapshots_router)
app.include_router(jobs_router)
app.include_router(viewer_router)
app.include_router(provision_router)
