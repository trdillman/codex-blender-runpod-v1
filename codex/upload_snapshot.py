from __future__ import annotations

import argparse
import json
import subprocess
import tarfile
import tempfile
from pathlib import Path

from sandbox_client import BrokerClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--addon-root", required=True)
    parser.add_argument("--module-name", required=True)
    return parser.parse_args()


def git_base_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def main() -> int:
    args = parse_args()
    addon_root = Path(args.addon_root)
    if not addon_root.exists():
        raise SystemExit(f"addon root not found: {addon_root}")

    with tempfile.TemporaryDirectory() as tmpdir:
        tarball = Path(tmpdir) / "snapshot.tar.gz"
        with tarfile.open(tarball, "w:gz") as handle:
            handle.add(addon_root, arcname=args.addon_root)
        payload = BrokerClient().upload_snapshot(
            tarball_path=tarball,
            base_sha=git_base_sha(),
            addon_root=args.addon_root,
            module_name=args.module_name,
        )
        print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
