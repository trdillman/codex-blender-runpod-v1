from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests


class BrokerClient:
    def __init__(self) -> None:
        self.base_url = os.environ["BROKER_PUBLIC_BASE_URL"].rstrip("/")
        self.token = os.environ["BROKER_AGENT_TOKEN"]
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def upload_snapshot(self, *, tarball_path: Path, base_sha: str, addon_root: str, module_name: str) -> dict[str, Any]:
        with tarball_path.open("rb") as handle:
            response = self.session.post(
                f"{self.base_url}/snapshots",
                data={"base_sha": base_sha, "addon_root": addon_root, "module_name": module_name},
                files={"bundle": (tarball_path.name, handle, "application/gzip")},
                timeout=120,
            )
        response.raise_for_status()
        return response.json()

    def submit_job(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = self.session.post(f"{self.base_url}/jobs", json=payload, timeout=30)
        response.raise_for_status()
        return response.json()

    def get_job(self, job_id: str) -> dict[str, Any]:
        response = self.session.get(f"{self.base_url}/jobs/{job_id}", timeout=30)
        response.raise_for_status()
        return response.json()

    def list_artifacts(self, job_id: str) -> dict[str, Any]:
        response = self.session.get(f"{self.base_url}/jobs/{job_id}/artifacts", timeout=30)
        response.raise_for_status()
        return response.json()
