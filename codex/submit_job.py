from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

from sandbox_client import BrokerClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot-id", help="optional; if omitted, read from STDIN json or SNAPSHOT_ID env")
    parser.add_argument("--wait", action="store_true")
    parser.add_argument("--blend-file")
    return parser.parse_args()


def snapshot_id_from_context(args: argparse.Namespace) -> str:
    if args.snapshot_id:
        return args.snapshot_id
    if os.environ.get("SNAPSHOT_ID"):
        return os.environ["SNAPSHOT_ID"]
    if not sys.stdin.isatty():
        payload = json.load(sys.stdin)
        if payload.get("snapshot_id"):
            return str(payload["snapshot_id"])
    raise SystemExit("snapshot id is required")


def main() -> int:
    args = parse_args()
    addon_root = os.environ["ADDON_ROOT"]
    module_name = os.environ["ADDON_MODULE"]
    snapshot_id = snapshot_id_from_context(args)

    request = {
        "snapshot_id": snapshot_id,
        "base_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "addon_root": addon_root,
        "module_name": module_name,
        "blend_file": args.blend_file,
        "checks": ["registration", "ui_smoke", "playback_smoke"],
    }
    broker = BrokerClient()
    job = broker.submit_job(request)
    print(json.dumps(job, indent=2))

    if not args.wait:
        return 0

    while True:
        current = broker.get_job(job["job_id"])
        print(json.dumps(current, indent=2))
        if current["status"] in {"succeeded", "failed"}:
            artifacts = broker.list_artifacts(job["job_id"])
            print(json.dumps(artifacts, indent=2))
            return 0 if current["status"] == "succeeded" else 1
        time.sleep(5)


if __name__ == "__main__":
    raise SystemExit(main())
