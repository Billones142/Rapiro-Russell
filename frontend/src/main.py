"""
Servidor y Cliente Rapiro para la Raspberry Pi.
Controla servomotores y LEDs por puerto serie, y se conecta al Backend
mediante un túnel reverso usando WebSockets.
"""

import json
import os
import time
import math
import threading
from urllib.parse import parse_qs, urlparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Intentar importar websocket-client para túnel de control
try:
    import websocket
except ImportError:
    websocket = None

# Soporte de cámara con fallback
try:
    import cv2
except ImportError:
    cv2 = None

try:
    from PIL import Image, ImageDraw
    import io
except ImportError:
    Image = None

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
BACKEND_WS_URL = os.environ.get("SEADD_BACKEND_WS", "ws://seadd.ddns.net/ws/rapiro")

client = RapiroSerialClient()

# --- SIMULACIÓN DE IMÁGENES ---
def make_mock_frame():
    if Image is None:
        return b""
    img = Image.new("RGB", (320, 240), color=(30, 41, 59))
    draw = ImageDraw.Draw(img)
    # Dibujar lesión simulada (patrón eritematoso difuso)
    draw.ellipse([110, 70, 210, 170], fill=(153, 27, 27))
    draw.ellipse([130, 90, 190, 150], fill=(252, 165, 165))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def gen_frames():
    """Genera tramas de video para el feed HTTP local."""
    if cv2 is not None:
        camera = cv2.VideoCapture(0)
        if camera.isOpened():
            try:
                while True:
                    success, frame = camera.read()
                    if not success:
                        break
                    ret, buffer = cv2.imencode('.jpg', frame)
                    if ret:
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                    time.sleep(0.05)
            finally:
                camera.release()
            return

    # Fallback si no hay cámara
    while True:
        frame_bytes = make_mock_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.2)


# --- GESTOR DE EFECTOS LED AUTOMATIZADOS ---
class LedEffectManager:
    """Administra las secuencias de animación LED de los ojos en un hilo en segundo plano."""
    def __init__(self, serial_client: RapiroSerialClient):
        self.client = serial_client
        self.state = "waiting"
        self._stop_event = threading.Event()
        self._thread = None

    def start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def set_state(self, state: str):
        print(f"[LED Manager] Cambiando a estado: {state}")
        self.state = state

    def _run_loop(self):
        last_state = None
        tick = 0
        
        while not self._stop_event.is_set():
            # Esperar a que la conexión serial esté lista
            if not self.client.is_connected:
                time.sleep(1.0)
                continue

            state = self.state

            # 1. Esperando al dermatólogo (Breathing Cyan)
            if state == "waiting":
                intensity = int(70 + 60 * math.sin(tick * 0.3))
                cmd = self.client.build_led_command(0, intensity, intensity, duration_ms=200)
                self.client.send_command(cmd, wait=0.2)

            # 2. Capturando lesión (Solid Yellow)
            elif state == "capturing":
                if last_state != "capturing":
                    cmd = self.client.build_led_command(255, 200, 0, duration_ms=300)
                    self.client.send_command(cmd, wait=0.3)
                time.sleep(0.3)

            # 3. Analizando la imagen con la red de visión (Pulsing Violet)
            elif state == "analyzing":
                intensity = int(128 + 120 * math.sin(tick * 1.0))
                cmd = self.client.build_led_command(intensity, 0, intensity, duration_ms=100)
                self.client.send_command(cmd, wait=0.1)

            # 4. Inferencia del sistema experto en curso (Blinking Orange)
            elif state == "inferring":
                if tick % 2 == 0:
                    cmd = self.client.build_led_command(255, 100, 0, duration_ms=100)
                else:
                    cmd = self.client.build_led_command(0, 0, 0, duration_ms=100)
                self.client.send_command(cmd, wait=0.1)

            # 5. Inferencia completa / resultado listo (Solid Green + Gestura de Saludo)
            elif state == "result_ready":
                if last_state != "result_ready":
                    # Poner ojos verdes
                    cmd = self.client.build_led_command(0, 255, 0, duration_ms=500)
                    self.client.send_command(cmd, wait=0.5)
                    # Ejecutar saludo/wave con el brazo (#M5) para notificar físicamente
                    self.client.send_command("#M5", wait=2.5)
                time.sleep(0.5)

            last_state = state
            tick += 1

led_manager = LedEffectManager(client)


# --- HILO DE CONEXIÓN WEBSOCKET DE CLIENTE (TÚNEL REVERSO) ---
def start_websocket_client():
    if websocket is None:
        print("[WS Client] AVISO: 'websocket-client' no está instalado. El túnel reverso no arrancará.")
        return

    def on_message(ws, message):
        try:
            data = json.loads(message)
            if data.get("type") == "command":
                cmd = data.get("cmd")
                print(f"[WS Client] Comando serial recibido desde dashboard: {cmd}")
                client.send_command(cmd)
            elif data.get("type") == "state":
                state_val = data.get("value")
                led_manager.set_state(state_val)
        except Exception as e:
            print(f"[WS Client] Error al procesar mensaje WebSocket: {e}")

    def on_error(ws, error):
        print(f"[WS Client] Error: {error}")

    def on_close(ws, close_status_code, close_msg):
        print("[WS Client] Conexión cerrada con el servidor backend.")

    def on_open(ws):
        print("[WS Client] Conexión establecida con el servidor backend. Transmitiendo stream...")
        
        # Hilo para transmitir video continuamente al backend en binario (JPEG)
        def video_stream_loop():
            camera = None
            if cv2 is not None:
                camera = cv2.VideoCapture(0)
                if not camera.isOpened():
                    camera = None

            try:
                while ws.keep_running:
                    frame_bytes = None
                    if camera is not None:
                        success, frame = camera.read()
                        if success:
                            ret, buffer = cv2.imencode('.jpg', frame)
                            if ret:
                                frame_bytes = buffer.tobytes()
                    
                    if frame_bytes is None:
                        frame_bytes = make_mock_frame()

                    if frame_bytes:
                        # Enviar el frame como mensaje binario opcode
                        ws.send(frame_bytes, opcode=websocket.ABNF.OPCODE_BINARY)
                    
                    # 5 fotogramas por segundo (suficiente para fluidez clínica y ahorro de red)
                    time.sleep(0.2)
            except Exception as stream_err:
                print(f"[WS Client] Error en loop de transmisión: {stream_err}")
            finally:
                if camera is not None:
                    camera.release()

        threading.Thread(target=video_stream_loop, daemon=True).start()

    def client_reconnect_loop():
        while True:
            try:
                print(f"[WS Client] Conectando al backend en: {BACKEND_WS_URL}")
                ws = websocket.WebSocketApp(
                    BACKEND_WS_URL,
                    on_open=on_open,
                    on_message=on_message,
                    on_error=on_error,
                    on_close=on_close
                )
                ws.run_forever()
            except Exception as conn_err:
                print(f"[WS Client] Error de conexión: {conn_err}")
            print("[WS Client] Reintentando conexión en 5 segundos...")
            time.sleep(5)

    threading.Thread(target=client_reconnect_loop, daemon=True).start()


# --- SERVIDORES LOCALES Y ROUTING (PARA PRUEBAS LOCALES) ---
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
            "service": "Rapiro Local Server",
            "version": "1.1.0",
            "endpoints": {
                "GET /camera/stream": "MJPEG local video feed",
                "GET /status": "Serial and client state",
            }
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
            wait=float(b.get("wait", 1.8)),
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
    def log_message(self, format: str, *args) -> None:
        # Silenciar logs del stream de video local
        if "stream" not in format:
            print(f"[HTTP] {self.address_string()} - {format % args}")

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        
        # Local video stream
        if path == "/camera/stream":
            self.send_response(200)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            try:
                for frame in gen_frames():
                    self.wfile.write(frame)
            except Exception as e:
                pass
            return

        if path == "/":
            try:
                ui_path = os.path.join(os.path.dirname(__file__), "index.html")
                with open(ui_path, "r", encoding="utf-8") as f:
                    html_content = f.read()
                body = html_content.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(f"Error loading UI: {e}".encode("utf-8"))
            return

        self._dispatch("GET")

    def do_POST(self) -> None:
        self._dispatch("POST")

    def _dispatch(self, method: str) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query = {k: v[0] for k, v in parse_qs(parsed.query).items()}
        body = _read_json_body(self) if method == "POST" else {}

        routes = API_ROUTES.get(method, {})

        if path.startswith("/test/servos/") and method == "POST":
            try:
                servo_id = int(path.split("/")[-1])
                result = test_servo(
                    client,
                    servo_id,
                    duration_ms=int(body.get("duration_ms", query.get("duration_ms", 400))),
                )
                _json_response(self, 200 if result.get("ok") else 500, result)
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
                _json_response(self, 200 if result.get("ok") else 500, result)
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
            _json_response(self, 200 if result.get("ok", True) else 500, result)
        except Exception as exc:
            _json_response(self, 500, {"ok": False, "message": str(exc)})


def run_server() -> None:
    # Auto-conectar serial al iniciar
    client.connect()
    if client.is_connected:
        print(f"Serial conectado en {client.port} @ {client.baud} baud")
    else:
        print("Serial auto-connect falló. Se podrá reintentar vía API local.")

    # Arrancar manager LED
    led_manager.start()

    # Arrancar cliente WebSocket hacia la nube
    start_websocket_client()

    server = ThreadingHTTPServer((HOST, PORT), RapiroRequestHandler)
    print(f"Servidor HTTP Rapiro iniciado en http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nCerrando...")
        client.disconnect()
        server.server_close()


if __name__ == "__main__":
    run_server()
