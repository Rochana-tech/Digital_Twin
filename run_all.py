#!/usr/bin/env python3
"""Run every layer UI plus one common portal.

Open only: http://127.0.0.1:8090

This launcher intentionally keeps the original layer projects isolated and
starts them on their existing ports, reducing the chance of integration
breakage during demos.
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from functools import partial

ROOT = Path(__file__).resolve().parent
PORTAL_PORT = 8090
SERVICES = {
    "l1": ("127.0.0.1", 5173),
    "l2": ("127.0.0.1", 5174),
    "l3": ("127.0.0.1", 8765),
    "l4": ("127.0.0.1", 5176),
}
PROCS: list[subprocess.Popen] = []


def port_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.25):
            return True
    except OSError:
        return False


def start(cmd: list[str], cwd: Path, label: str) -> None:
    if not cwd.exists():
        print(f"[SKIP] {label}: missing {cwd}")
        return
    try:
        p = subprocess.Popen(cmd, cwd=str(cwd))
        PROCS.append(p)
        print(f"[STARTED] {label} (pid={p.pid})")
    except Exception as exc:
        print(f"[ERROR] {label}: {exc}")


class PortalHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/health.json"):
            body = json.dumps({k: port_open(*v) for k, v in SERVICES.items()}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/developer-workspace.html":
            target = ROOT / "developer-workspace.html"
            if target.exists():
                body = target.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
        super().do_GET()

    def log_message(self, fmt, *args):
        # Keep the terminal readable during a demo.
        if "/health.json" not in str(args):
            super().log_message(fmt, *args)


def main() -> None:
    py = sys.executable

    # Existing layer UIs, unchanged.
    start([py, "-m", "http.server", "5173", "--bind", "127.0.0.1"], ROOT / "layer1_data_acquisition" / "frontend", "Layer 1 UI")
    start([py, "-m", "http.server", "5174", "--bind", "127.0.0.1"], ROOT / "layer2a_fault_detection" / "frontend", "Layer 2A UI")
    start([py, "-m", "digital_twin_layer3.dev_ui"], ROOT, "Layer 3 Digital Twin UI")
    start([py, "-m", "http.server", "5176", "--bind", "127.0.0.1"], ROOT / "layer4_recovery_with_simple_ui" / "frontend", "Layer 4 UI")

    handler = partial(PortalHandler, directory=str(ROOT / "portal"))
    server = ThreadingHTTPServer(("127.0.0.1", PORTAL_PORT), handler)
    print("\n=======================================================")
    print(" Industrial AI Unified Portal: http://127.0.0.1:8090")
    print("=======================================================")
    print("Press Ctrl+C here to stop all layer UIs.\n")

    threading.Timer(1.2, lambda: webbrowser.open("http://127.0.0.1:8090")).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping services...")
    finally:
        server.server_close()
        for p in PROCS:
            if p.poll() is None:
                p.terminate()
        for p in PROCS:
            try:
                p.wait(timeout=3)
            except Exception:
                p.kill()


if __name__ == "__main__":
    main()
