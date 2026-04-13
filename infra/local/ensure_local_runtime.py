from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BROKER_ROOT = PROJECT_ROOT / "broker"
if str(BROKER_ROOT) not in sys.path:
    sys.path.insert(0, str(BROKER_ROOT))

from app.services.local_sandbox import ensure_runtime_ready  # noqa: E402


def main() -> int:
    payload = ensure_runtime_ready()
    print(json.dumps(payload, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
