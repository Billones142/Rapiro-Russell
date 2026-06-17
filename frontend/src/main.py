"""
Cliente Rapiro para la Raspberry Pi.
Conecta de forma saliente al Backend usando WebSockets para transmitir
el video de la cámara y recibir comandos de control y cambios de estado (LEDs).
"""

import json
import os
import time
import math
import threading

# Importar websocket-client
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

BACKEND_WS_URL = os.environ.get("SEADD_BACKEND_WS", "ws://seadd.ddns.net:8000/ws/rapiro")

client = RapiroSerialClient()

# --- SIMULACIÓN DE IMÁGENES (Pillow) ---
def make_mock_frame():
    """Genera una imagen de simulación de lesión en formato JPEG."""
    if Image is None:
        return b""
    # Crear un lienzo simulando piel
    img = Image.new("RGB", (320, 240), color=(30, 41, 59))
    draw = ImageDraw.Draw(img)
    # Dibujar lesión simulada (patrón eritematoso difuso)
    draw.ellipse([110, 70, 210, 170], fill=(153, 27, 27))
    draw.ellipse([130, 90, 190, 150], fill=(252, 165, 165))
    
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


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
        print("[WS Client] ERROR: 'websocket-client' no está instalado. El túnel reverso no arrancará.")
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
        print(f"[WS Client] Error en la conexión: {error}")

    def on_close(ws, close_status_code, close_msg):
        print("[WS Client] Conexión cerrada con el servidor backend.")

    def on_open(ws):
        print("[WS Client] Conectado al backend con éxito. Transmitiendo video...")
        
        # Hilo secundario para transmitir video continuamente al backend en binario (JPEG)
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


def main() -> None:
    # Auto-conectar puerto serie con Rapiro Arduino
    client.connect()
    if client.is_connected:
        print(f"Puerto Serie conectado en {client.port} @ {client.baud} baud")
    else:
        print("Puerto Serie falló (se ejecutará en modo simulación de robot).")

    # Iniciar animador LED de ojos
    led_manager.start()

    # Iniciar el cliente WebSocket saliente hacia el servidor en la nube
    start_websocket_client()

    print("[SEADD Client] Rapiro iniciado y en funcionamiento. Presiona Ctrl+C para salir.")
    
    # Mantener el hilo principal activo
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nDeteniendo cliente Rapiro...")
        client.disconnect()


if __name__ == "__main__":
    main()
