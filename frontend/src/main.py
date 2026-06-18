"""
Cliente Rapiro para la Raspberry Pi.
Conecta de forma saliente al Backend usando WebSockets para transmitir
el video de la cámara y recibir comandos de control y cambios de estado (LEDs).
"""

import json
import os
import time
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
        
        while not self._stop_event.is_set():
            if not self.client.is_connected:
                time.sleep(1.0)
                continue

            state = self.state

            if state != last_state:
                print(f"[LED Manager] Cambiando a estado: {state}")
                
                # 1. Esperando al dermatólogo (Cyan estático y posición inicial)
                if state == "waiting":
                    self.client.send_command("#PR000G128B128T005", wait=0.1)
                    self.client.send_command("#M0", wait=1.0)

                # 2. Capturando lesión (Amarillo + Brazo derecho arriba + Garra cerrada/pulgar arriba)
                elif state == "capturing":
                    # Ojos amarillos, S02 (hombro derecho roll) a 120, S03 (brazo derecho pitch) a 90, S04 (garra derecha) a 50
                    self.client.send_command("#PS02A120S03A090S04A050R255G200B000T005", wait=1.0)

                # 3. Analizando la imagen con la red de visión (Violeta estático)
                elif state == "analyzing":
                    self.client.send_command("#PR128G000B128T005", wait=0.5)

                # 4. Inferencia del sistema experto en curso (Naranja estático)
                elif state == "inferring":
                    self.client.send_command("#PR255G100B000T005", wait=0.5)

                # 5. Inferencia completa (Verde + Saludo + Espera de 3 segundos y vuelta a waiting)
                elif state == "result_ready":
                    self.client.send_command("#PR000G255B000T005", wait=0.1)
                    self.client.send_command("#M5", wait=2.5)
                    time.sleep(3.0)
                    self.set_state("waiting")

                last_state = state

            time.sleep(0.1)

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
            print("[Camera Debug] Iniciando verificación de cámara...")
            
            if cv2 is None:
                print("[Camera Debug] AVISO: 'opencv-python' (cv2) no está instalado. No se puede usar la webcam física.")
            else:
                print("[Camera Debug] OpenCV está instalado con éxito. Intentando abrir webcam física en index 0 (/dev/video0)...")
                try:
                    camera = cv2.VideoCapture(0)
                    if not camera.isOpened():
                        print("[Camera Debug] ERROR: No se pudo abrir la webcam física en index 0. ¿Está ocupada o desconectada?")
                        camera = None
                    else:
                        width = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
                        height = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
                        print(f"[Camera Debug] EXITO: Cámara física abierta correctamente. Resolución: {width}x{height}")
                except Exception as cam_err:
                    print(f"[Camera Debug] EXPORT EXCEPTION al abrir la cámara: {cam_err}")
                    camera = None

            if Image is None:
                print("[Camera Debug] AVISO: 'Pillow' (PIL) no está instalado. La simulación de imagen no estará disponible.")

            try:
                first_frame_logged = False
                while ws.keep_running:
                    frame_bytes = None
                    
                    if camera is not None:
                        success, frame = camera.read()
                        if success:
                            if not first_frame_logged:
                                print("[Camera Debug] Frame capturado con éxito de la cámara física. Codificando a JPEG...")
                            ret, buffer = cv2.imencode('.jpg', frame)
                            if ret:
                                frame_bytes = buffer.tobytes()
                                if not first_frame_logged:
                                    print(f"[Camera Debug] JPEG codificado correctamente ({len(frame_bytes)} bytes). Enviando...")
                                    first_frame_logged = True
                            else:
                                if not first_frame_logged:
                                    print("[Camera Debug] ERROR: Falló la codificación JPEG de OpenCV.")
                        else:
                            print("[Camera Debug] ERROR: Falló la lectura del frame de la cámara física (camera.read() devolvió False).")
                            camera.release()
                            camera = None # Forzar fallback
                    
                    if frame_bytes is None:
                        if not first_frame_logged:
                            print("[Camera Debug] Usando generador de imágenes de simulación (Pillow)...")
                            first_frame_logged = True
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
                    print("[Camera Debug] Liberando cámara física...")
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
