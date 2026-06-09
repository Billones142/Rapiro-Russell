"""
Rapiro test server for Raspberry Pi.

Exposes an HTTP API to run serial communication tests, servomotor checks,
eye LED (RGB) tests and predefined motion commands against the Rapiro robot.
"""

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from rapiro_client import RapiroSerialClient
from test_suite import (
    test_all_motions,
    test_all_servos,
    test_full_diagnostic,
    test_motion,
    test_neopixel,
    test_serial,
    test_servo,
)

HOST = os.environ.get("RAPIRO_HTTP_HOST", "0.0.0.0")
PORT = int(os.environ.get("RAPIRO_HTTP_PORT", "8080"))

client = RapiroSerialClient()


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.end_headers()
    handler.wfile.write(body)


def _read_json_body(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length", 0))
    if length == 0:
        return {}
    raw = handler.rfile.read(length)
    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError:
        return {}


API_ROUTES = {
    "GET": {
        "/": lambda _h, _q, _b: {
            "service": "Rapiro Test Server",
            "version": "1.0.0",
            "endpoints": {
                "GET /": "API documentation",
                "GET /health": "Server health check",
                "GET /status": "Serial connection and robot info",
                "POST /serial/connect": "Open serial port",
                "POST /serial/disconnect": "Close serial port",
                "POST /serial/test": "Test serial communication (#C)",
                "POST /command": '{"command": "#M0"} — send raw command',
                "POST /test/servos": "Test all 12 servomotors",
                "POST /test/servos/{id}": "Test a single servo (0-11)",
                "POST /test/neopixel": "Cycle eye RGB LED colors",
                "POST /test/motions": "Run safe predefined motions (M0,M5-M9)",
                "POST /test/motions/{id}": "Run a single motion (0-9)",
                "POST /test/full": "Full diagnostic (serial + LED + servos + motions)",
            },
        },
        "/health": lambda _h, _q, _b: {"ok": True, "status": "running"},
        "/status": lambda _h, _q, _b: client.status(),
    },
    "POST": {
        "/serial/connect": lambda _h, _q, _b: client.connect(),
        "/serial/disconnect": lambda _h, _q, _b: client.disconnect(),
        "/serial/test": lambda _h, _q, _b: test_serial(client),
        "/command": lambda _h, _q, b: client.send_command(
            b.get("command", ""),
            wait=float(b.get("wait", 0.5)),
        ),
        "/test/servos": lambda _h, _q, b: test_all_servos(
            client, duration_ms=int(b.get("duration_ms", 400))
        ),
        "/test/neopixel": lambda _h, _q, b: test_neopixel(
            client, pause=float(b.get("pause", 0.8))
        ),
        "/test/motions": lambda _h, _q, b: test_all_motions(
            client, motion_pause=float(b.get("pause", 2.5))
        ),
        "/test/full": lambda _h, _q, _b: test_full_diagnostic(client),
    },
}


class RapiroRequestHandler(BaseHTTPRequestHandler):
    """HTTP handler that maps REST endpoints to Rapiro test routines."""

    def log_message(self, format: str, *args) -> None:
        print(f"[HTTP] {self.address_string()} - {format % args}")

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        self._dispatch("GET")

    def do_POST(self) -> None:
        self._dispatch("POST")

    def _dispatch(self, method: str) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query = {k: v[0] for k, v in parse_qs(parsed.query).items()}
        body = _read_json_body(self) if method == "POST" else {}

        routes = API_ROUTES.get(method, {})

        # Dynamic routes: /test/servos/{id} and /test/motions/{id}
        if path.startswith("/test/servos/") and method == "POST":
            try:
                servo_id = int(path.split("/")[-1])
                result = test_servo(
                    client,
                    servo_id,
                    duration_ms=int(body.get("duration_ms", query.get("duration_ms", 400))),
                )
                status = 200 if result.get("ok") else 500
                _json_response(self, status, result)
                return
            except ValueError:
                _json_response(self, 400, {"ok": False, "message": "Invalid servo id"})
                return

        if path.startswith("/test/motions/") and method == "POST":
            try:
                motion_id = int(path.split("/")[-1])
                result = test_motion(
                    client,
                    motion_id,
                    duration=float(body.get("duration", query.get("duration", 3.0))),
                )
                status = 200 if result.get("ok") else 500
                _json_response(self, status, result)
                return
            except ValueError:
                _json_response(self, 400, {"ok": False, "message": "Invalid motion id"})
                return

        handler = routes.get(path)
        if handler is None:
            _json_response(self, 404, {"ok": False, "message": f"Route not found: {path}"})
            return

        try:
            result = handler(self, query, body)
            status = 200 if result.get("ok", True) else 500
            _json_response(self, status, result)
        except Exception as exc:
            _json_response(self, 500, {"ok": False, "message": str(exc)})


def run_server() -> None:
    """Start the HTTP test server and optionally auto-connect serial."""
    auto_connect = os.environ.get("RAPIRO_AUTO_CONNECT", "true").lower() == "true"
    if auto_connect:
        result = client.connect()
        if result.get("ok"):
            print(f"Serial connected on {client.port} @ {client.baud} baud")
        else:
            print(f"Serial auto-connect failed: {result.get('message')}")
            print("Server will start anyway; use POST /serial/connect when ready.")

    server = HTTPServer((HOST, PORT), RapiroRequestHandler)
    print(f"Rapiro test server listening on http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        client.disconnect()
        server.server_close()


if __name__ == "__main__":
    run_server()
