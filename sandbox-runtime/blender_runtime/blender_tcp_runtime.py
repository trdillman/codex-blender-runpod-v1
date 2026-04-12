from __future__ import annotations

import contextlib
import io
import json
import os
import socket
import threading
import traceback
from pathlib import Path

import addon_utils  # type: ignore
import bpy  # type: ignore

HOST = os.environ.get("BROKER_RUNTIME_HOST", "127.0.0.1")
PORT = int(os.environ.get("BROKER_RUNTIME_PORT", "9876"))


class BlenderRuntime:
    def __init__(self, host: str = HOST, port: int = PORT) -> None:
        self.host = host
        self.port = port
        self.running = False
        self.sock: socket.socket | None = None

    def start(self) -> None:
        if self.running:
            return
        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        self.sock.settimeout(1.0)
        threading.Thread(target=self._loop, daemon=True).start()
        print(f"[runtime] listening on {self.host}:{self.port}")

    def _loop(self) -> None:
        assert self.sock is not None
        while self.running:
            try:
                client, _ = self.sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            threading.Thread(target=self._handle_client, args=(client,), daemon=True).start()

    def _handle_client(self, client: socket.socket) -> None:
        buffer = b""
        try:
            while True:
                chunk = client.recv(65536)
                if not chunk:
                    break
                buffer += chunk
                try:
                    request = json.loads(buffer.decode("utf-8"))
                except json.JSONDecodeError:
                    continue
                response_holder = {}
                event = threading.Event()

                def _execute() -> None:
                    try:
                        response_holder["response"] = self.execute(request)
                    except Exception as exc:  # noqa: BLE001
                        response_holder["response"] = {"status": "error", "message": str(exc), "traceback": traceback.format_exc()}
                    finally:
                        event.set()

                bpy.app.timers.register(_execute, first_interval=0.0)
                event.wait()
                client.sendall(json.dumps(response_holder["response"]).encode("utf-8"))
                break
        finally:
            with contextlib.suppress(Exception):
                client.close()

    def execute(self, request: dict) -> dict:
        command = str(request.get("command") or "")
        if command == "ping":
            return {"status": "ok", "result": {"version": bpy.app.version_string, "file": bpy.data.filepath}}
        if command == "scene_info":
            return {
                "status": "ok",
                "result": {
                    "scene": bpy.context.scene.name,
                    "frame": int(bpy.context.scene.frame_current),
                    "objects": len(bpy.context.scene.objects),
                },
            }
        if command == "execute_code":
            code = str(request["code"])
            scope = {"bpy": bpy, "__name__": "__main__"}
            capture = io.StringIO()
            with contextlib.redirect_stdout(capture):
                exec(code, scope)  # noqa: S102
            return {"status": "ok", "result": {"stdout": capture.getvalue()}}
        if command == "install_addon_zip":
            zip_path = str(request["zip_path"])
            bpy.ops.preferences.addon_install(filepath=zip_path, overwrite=True)
            return {"status": "ok", "result": {"installed": zip_path}}
        if command == "enable_addon":
            module_name = str(request["module_name"])
            addon_utils.enable(module_name, default_set=False, persistent=False)
            return {"status": "ok", "result": {"enabled": module_name}}
        if command == "disable_addon":
            module_name = str(request["module_name"])
            addon_utils.disable(module_name, default_set=False)
            return {"status": "ok", "result": {"disabled": module_name}}
        if command == "viewport_screenshot":
            filepath = str(request["filepath"])
            area = next((a for a in bpy.context.screen.areas if a.type == "VIEW_3D"), None)
            if area is None:
                raise RuntimeError("no VIEW_3D area available")
            with bpy.context.temp_override(area=area):
                bpy.ops.screen.screenshot_area(filepath=filepath)
            return {"status": "ok", "result": {"filepath": filepath}}
        raise ValueError(f"unknown command: {command}")


def main() -> None:
    BlenderRuntime().start()


if __name__ == "__main__":
    main()
