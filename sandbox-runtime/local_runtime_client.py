from __future__ import annotations

import json
import socket
from typing import Any


class RuntimeClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 9876, timeout: float = 20.0) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout

    def request(self, payload: dict[str, Any]) -> dict[str, Any]:
        raw = json.dumps(payload).encode("utf-8")
        with socket.create_connection((self.host, self.port), timeout=self.timeout) as sock:
            sock.sendall(raw)
            chunks = []
            while True:
                data = sock.recv(65536)
                if not data:
                    break
                chunks.append(data)
        if not chunks:
            raise RuntimeError("runtime returned no data")
        return json.loads(b"".join(chunks).decode("utf-8"))
