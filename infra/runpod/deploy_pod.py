from __future__ import annotations

import os
import sys
from typing import Any

import requests

RUNPOD_API = "https://rest.runpod.io/v1/pods"


def build_payload() -> dict[str, Any]:
    gpu_candidates = [item.strip() for item in os.environ.get("RUNPOD_GPU_CANDIDATES", "NVIDIA GeForce RTX 4070 Ti,NVIDIA GeForce RTX 3090").split(",") if item.strip()]
    secure = os.environ.get("RUNPOD_SECURE_CLOUD", "true").lower() == "true"
    return {
        "name": os.environ.get("RUNPOD_NAME", "codex-blender-sandbox"),
        "cloudType": "SECURE" if secure else "COMMUNITY",
        "computeType": "GPU",
        "gpuCount": 1,
        "gpuTypeIds": gpu_candidates,
        "gpuTypePriority": "availability",
        "containerDiskInGb": int(os.environ.get("RUNPOD_CONTAINER_DISK_GB", "40")),
        "volumeInGb": int(os.environ.get("RUNPOD_VOLUME_GB", "80")),
        "volumeMountPath": "/workspace",
        "imageName": os.environ["RUNPOD_IMAGE"],
        "ports": ["8080/http", "3001/http", "22/tcp"],
        "env": {
            "BROKER_PUBLIC_BASE_URL": os.environ.get("BROKER_PUBLIC_BASE_URL", ""),
            "BROKER_BOOTSTRAP_SECRET": os.environ["BROKER_BOOTSTRAP_SECRET"],
            "BROKER_JWT_SECRET": os.environ["BROKER_JWT_SECRET"],
        },
        "supportPublicIp": True,
    }


def main() -> int:
    api_key = os.environ.get("RUNPOD_API_KEY")
    if not api_key:
        print("RUNPOD_API_KEY is required", file=sys.stderr)
        return 2
    response = requests.post(
        RUNPOD_API,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=build_payload(),
        timeout=60,
    )
    print(response.text)
    response.raise_for_status()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
