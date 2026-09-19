#!/usr/bin/env python3
"""Single-port deployment server for the integrated Industrial AI demo.

Serves:
  /             unified portal
  /layer1/      Layer 1 static UI
  /layer2/      Layer 2A static UI
  /layer3/      Layer 3 Digital Twin UI
  /layer4/      Layer 4 static UI
  /developer-workspace.html
  /api/*        Layer 3 Digital Twin APIs
  /health.json  portal health summary

Designed for Render and other hosts that expose one HTTP port.
"""
from __future__ import annotations

import json
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from digital_twin_layer3.dev_ui import INDEX_HTML as LAYER3_HTML, get_service

ROOT = Path(__file__).resolve().parent
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "10000"))

STATIC_MOUNTS = {
    "/layer1/": ROOT / "layer1_data_acquisition" / "frontend",
    "/layer2/": ROOT / "layer2a_fault_detection" / "frontend",
    "/layer4/": ROOT / "layer4_recovery_with_simple_ui" / "frontend",
}


def _safe_file(base: Path, rel: str) -> Path | None:
    rel = unquote(rel).lstrip("/")
    target = (base / rel).resolve()
    try:
        target.relative_to(base.resolve())
    except ValueError:
        return None
    if target.is_dir():
        target = target / "index.html"
    return target


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Keep deployment logs readable but preserve errors from the host.
        if not self.path.startswith("/health.json"):
            super().log_message(fmt, *args)

    def _bytes(self, body: bytes, content_type: str, status: int = 200, cache: str | None = None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        if cache is not None:
            self.send_header("Cache-Control", cache)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, payload, status: int = 200):
        self._bytes(json.dumps(payload, indent=2).encode("utf-8"), "application/json; charset=utf-8", status, "no-store")

    def _html(self, html: str, status: int = 200):
        self._bytes(html.encode("utf-8"), "text/html; charset=utf-8", status, "no-store")

    def _serve_file(self, path: Path | None):
        if path is None or not path.exists() or not path.is_file():
            self._json({"error": "not found"}, 404)
            return
        ctype, _ = mimetypes.guess_type(str(path))
        self._bytes(path.read_bytes(), ctype or "application/octet-stream", 200, "public, max-age=300")

    def _layer3_get(self, parsed):
        qs = parse_qs(parsed.query)
        line = qs.get("line", ["ELECTRONICS"])[0]
        try:
            if parsed.path == "/api/topology":
                svc = get_service(line)
                self._json({"line": line, "topology": svc.get_topology()})
            elif parsed.path == "/api/snapshot":
                self._json(get_service(line).get_line_snapshot())
            elif parsed.path == "/api/combined":
                machine_id = qs.get("machine_id", [None])[0]
                if not machine_id:
                    self._json({"error": "machine_id is required"}, 400)
                    return
                self._json(get_service(line).get_combined_condition(machine_id))
            elif parsed.path == "/api/bottleneck":
                svc = get_service(line)
                self._json({"ranking": svc.get_bottleneck_ranking(), "primary_bottleneck": svc.get_primary_bottleneck()})
            else:
                self._json({"error": "not found"}, 404)
        except Exception as exc:
            self._json({"error": str(exc)}, 500)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            self._serve_file(ROOT / "portal" / "index.html")
            return
        if path == "/health.json":
            self._json({
                "l1": (STATIC_MOUNTS["/layer1/"] / "index.html").exists(),
                "l2": (STATIC_MOUNTS["/layer2/"] / "index.html").exists(),
                "l3": True,
                "l4": (STATIC_MOUNTS["/layer4/"] / "index.html").exists(),
            })
            return
        if path == "/developer-workspace.html":
            self._serve_file(ROOT / "developer-workspace.html")
            return
        if path in ("/layer3", "/layer3/"):
            self._html(LAYER3_HTML)
            return
        if path.startswith("/api/"):
            self._layer3_get(parsed)
            return

        for prefix, base in STATIC_MOUNTS.items():
            if path == prefix[:-1]:
                self.send_response(302)
                self.send_header("Location", prefix)
                self.end_headers()
                return
            if path.startswith(prefix):
                rel = path[len(prefix):] or "index.html"
                self._serve_file(_safe_file(base, rel))
                return

        self._json({"error": "not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/whatif":
            self._json({"error": "not found"}, 404)
            return
        qs = parse_qs(parsed.query)
        line = qs.get("line", ["ELECTRONICS"])[0]
        try:
            length = int(self.headers.get("Content-Length", 0) or 0)
            payload = json.loads(self.rfile.read(length) if length else b"{}")
            result = get_service(line).run_what_if(
                scenario_name=payload.get("scenario_name", "adhoc"),
                kind=payload["kind"],
                affected_machine_id=payload["affected_machine_id"],
                factor=payload.get("factor"),
                shift_to_machine_id=payload.get("shift_to_machine_id"),
                duration_hr=float(payload.get("duration_hr", 8.0)),
                arrival_rate_uph=payload.get("arrival_rate_uph"),
                seed=int(payload.get("seed", 42)),
            )
            self._json(result)
        except (KeyError, ValueError, json.JSONDecodeError) as exc:
            self._json({"error": str(exc)}, 400)
        except Exception as exc:
            self._json({"error": str(exc)}, 500)


def main():
    # Warm Layer 3 state so first page load is responsive.
    get_service("ELECTRONICS")
    get_service("AUTOMOBILE")
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Industrial AI unified deployment server listening on {HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
