"""Cliente Rapiro basado en GPIOzero para control directo desde Raspberry Pi.

Este módulo reemplaza la comunicación serial con control directo por hardware
utilizando la librería gpiozero. Mantiene la misma firma de API y protocolo de comandos
para que el servidor HTTP y el banco de pruebas sigan funcionando sin cambios.
"""

import os
import re
import sys
import time
import threading
from typing import Optional, Dict, List, Tuple

# Intentar importar gpiozero. Si no está disponible, usar mocks para evitar fallos de importación.
try:
    from gpiozero import AngularServo, RGBLED
    GPIO_AVAILABLE = True
except (ImportError, OSError):
    GPIO_AVAILABLE = False
    
    # Clases Mock para simular los pines en entornos sin GPIO (PC/Testing)
    class MockAngularServo:
        def __init__(self, pin: int, min_angle: int = 0, max_angle: int = 180, min_pulse_width: float = 0.0005, max_pulse_width: float = 0.0025):
            self.pin = pin
            self.angle = 90.0
        def close(self):
            pass

    class MockRGBLED:
        def __init__(self, red: int, green: int, blue: int, active_high: bool = True):
            self.red = red
            self.green = green
            self.blue = blue
            self.color = (0.0, 0.0, 0.0)
        def close(self):
            pass

    AngularServo = MockAngularServo
    RGBLED = MockRGBLED


# Mapeo de pines GPIO por defecto (Numeración BCM de la Raspberry Pi)
DEFAULT_PIN_MAPPING = {
    "servo_0": 4,   # S00: Cabeza (yaw)
    "servo_1": 17,  # S01: Cintura (yaw)
    "servo_2": 27,  # S02: Hombro derecho (roll)
    "servo_3": 22,  # S03: Brazo derecho (pitch)
    "servo_4": 10,  # S04: Mano derecha (grip)
    "servo_5": 9,   # S05: Hombro izquierdo (roll)
    "servo_6": 11,  # S06: Brazo izquierdo (pitch)
    "servo_7": 5,   # S07: Mano izquierda (grip)
    "servo_8": 6,   # S08: Pie derecho (yaw)
    "servo_9": 13,  # S09: Pie derecho (pitch)
    "servo_10": 19, # S10: Pie izquierdo (yaw)
    "servo_11": 26, # S11: Pie izquierdo (pitch)
    "led_r": 18,    # LED Ojos: Rojo
    "led_g": 23,    # LED Ojos: Verde
    "led_b": 24,    # LED Ojos: Azul
}

# Calibración/ajuste fino de ángulos de servos en grados
DEFAULT_TRIMS = {
    0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0,
    6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0
}

# Nombres legibles de servomotores
SERVO_NAMES = {
    0: "Head yaw",
    1: "Waist yaw",
    2: "R Shoulder roll",
    3: "R Shoulder pitch",
    4: "R Hand grip",
    5: "L Shoulder roll",
    6: "L Shoulder pitch",
    7: "L Hand grip",
    8: "R Foot yaw",
    9: "R Foot pitch",
    10: "L Foot yaw",
    11: "L Foot pitch",
}

# Nombres legibles de movimientos predefinidos
MOTION_COMMANDS = {
    0: "Stop / home position",
    1: "Walk forward",
    2: "Walk backward",
    3: "Turn right",
    4: "Turn left",
    5: "Wave left hand (green LED)",
    6: "Lower left hand (yellow LED)",
    7: "Move both arms (blue LED)",
    8: "Wave goodbye (red LED)",
    9: "Raise right arm and move waist (blue LED)",
}

# Matriz de movimientos predefinidos (copiada directamente del firmware de Rapiro)
# 10 movimientos (M0-M9), 8 fotogramas (frames) por movimiento.
# Cada frame tiene 16 valores: 12 ángulos de servo, 3 valores RGB de LED, 1 duración en décimas de segundo.
MOTIONS = [
    # M0: Detener / Posición inicial (Home)
    [
        [90, 90, 0, 130, 90, 180, 50, 90, 90, 90, 90, 90, 0, 0, 255, 10],
        [90, 90, 0, 130, 90, 180, 50, 90, 90, 90, 90, 90, 0, 0, 0, 0],
        [90, 90, 0, 130, 90, 180, 50, 90, 90, 90, 90, 90, 0, 0, 0, 0],
        [90, 90, 0, 130, 90, 180, 50, 90, 90, 90, 90, 90, 0, 0, 0, 0],
        [90, 90, 0, 130, 90, 180, 50, 90, 90, 90, 90, 90, 0, 0, 0, 0],
        [90, 90, 0, 130, 90, 180, 50, 90, 90, 90, 90, 90, 0, 0, 0, 0],
        [90, 90, 0, 130, 90, 180, 50, 90, 90, 90, 90, 90, 0, 0, 0, 0],
        [90, 90, 0, 130, 90, 180, 50, 90, 90, 90, 90, 90, 0, 0, 0, 0],
    ],
    # M1: Caminar adelante
    [
        [90, 90, 0, 90, 90, 180, 90, 90, 80, 110, 80, 120, 0, 0, 0, 5],
        [90, 90, 0, 90, 90, 180, 90, 90, 70, 90, 70, 90, 0, 0, 255, 5],
        [90, 90, 0, 90, 90, 180, 90, 90, 70, 70, 70, 80, 0, 0, 255, 5],
        [90, 90, 0, 90, 90, 180, 90, 90, 100, 60, 100, 70, 0, 0, 0, 5],
        [90, 90, 0, 90, 90, 180, 90, 90, 110, 90, 110, 90, 0, 0, 255, 5],
        [90, 90, 0, 90, 90, 180, 90, 90, 110, 100, 110, 110, 0, 0, 255, 5],
        [90, 90, 0, 90, 90, 180, 90, 90, 90, 90, 90, 90, 0, 0, 0, 0],
        [90, 90, 0, 90, 90, 180, 90, 90, 90, 90, 90, 90, 0, 0, 0, 0],
    ],
    # M2: Caminar atrás
    [
        [90, 90, 0, 90, 90, 180, 90, 90, 100, 110, 100, 120, 0, 0, 0, 5],
        [90, 90, 0, 90, 90, 180, 90, 90, 110, 90, 110, 90, 0, 0, 255, 5],
        [90, 90, 0, 90, 90, 180, 90, 90, 110, 70, 110, 80, 0, 0, 255, 5],
        [90, 90, 0, 90, 90, 180, 90, 90, 80, 30, 80, 70, 0, 0, 0, 5],
        [90, 90, 0, 90, 90, 180, 90, 90, 70, 90, 70, 90, 0, 0, 255, 5],
        [90, 90, 0, 90, 90, 180, 90, 90, 70, 100, 70, 110, 0, 0, 255, 5],
        [90, 90, 0, 90, 90, 180, 90, 90, 90, 90, 90, 90, 0, 0, 0, 0],
        [90, 90, 0, 90, 90, 180, 90, 90, 90, 90, 90, 90, 0, 0, 0, 0],
    ],
    # M3: Girar derecha
    [
        [90, 90, 0, 90, 90, 180, 90, 90, 95, 110, 85, 120, 0, 0, 0, 5],
        [90, 90, 0, 90, 90, 180, 90, 90, 100, 90, 80, 90, 0, 0, 255, 5],
        [90, 90, 0, 90, 90, 180, 90, 90, 100, 70, 80, 80, 0, 0, 0, 5],
        [90, 90, 0, 90, 90, 180, 90, 90, 85, 60, 95, 70, 0, 0, 255, 5],
        [90, 90, 0, 90, 90, 180, 90, 90, 80, 90, 100, 90, 0, 0, 0, 5],
        [90, 90, 0, 90, 90, 180, 90, 90, 80, 100, 100, 110, 0, 0, 255, 5],
        [90, 90, 0, 90, 90, 180, 90, 90, 90, 90, 90, 90, 0, 0, 0, 0],
        [90, 90, 0, 90, 90, 180, 90, 90, 90, 90, 90, 90, 0, 0, 0, 0],
    ],
    # M4: Girar izquierda
    [
        [90, 90, 0, 90, 90, 180, 90, 90, 95, 60, 85, 70, 0, 0, 0, 5],
        [90, 90, 0, 90, 90, 180, 90, 90, 100, 90, 80, 90, 0, 0, 255, 5],
        [90, 90, 0, 90, 90, 180, 90, 90, 100, 100, 80, 110, 0, 0, 0, 5],
        [90, 90, 0, 90, 90, 180, 90, 90, 85, 110, 95, 120, 0, 0, 255, 5],
        [90, 90, 0, 90, 90, 180, 90, 90, 80, 90, 100, 90, 0, 0, 0, 5],
        [90, 90, 0, 90, 90, 180, 90, 90, 80, 70, 100, 80, 0, 0, 255, 5],
        [90, 90, 0, 90, 90, 180, 90, 90, 90, 90, 90, 90, 0, 0, 0, 0],
        [90, 90, 0, 90, 90, 180, 90, 90, 90, 90, 90, 90, 0, 0, 0, 0],
    ],
    # M5: Saludar (mano izquierda, LED verde)
    [
        [90, 90, 120, 90, 90, 60, 90, 90, 90, 90, 90, 90, 0, 0, 0, 10],
        [100, 90, 120, 130, 110, 60, 50, 70, 90, 90, 90, 90, 0, 255, 0, 5],
        [90, 90, 120, 90, 90, 60, 90, 90, 90, 90, 90, 90, 0, 255, 0, 5],
        [80, 90, 120, 130, 110, 60, 50, 70, 90, 90, 90, 90, 0, 0, 0, 5],
        [90, 90, 120, 90, 90, 60, 90, 90, 90, 90, 90, 90, 0, 255, 0, 10],
        [90, 90, 120, 130, 110, 60, 50, 70, 90, 90, 90, 90, 0, 255, 0, 5],
        [90, 90, 0, 90, 90, 180, 90, 90, 90, 90, 90, 90, 0, 0, 0, 0],
        [90, 90, 0, 90, 90, 180, 90, 90, 90, 90, 90, 90, 0, 0, 0, 0],
    ],
    # M6: Bajar mano izquierda (LED amarillo)
    [
        [90, 120, 120, 130, 90, 180, 90, 90, 90, 90, 90, 90, 255, 255, 0, 7],
        [90, 120, 120, 90, 90, 180, 90, 90, 90, 90, 90, 90, 255, 255, 0, 7],
        [90, 90, 0, 90, 90, 180, 90, 90, 90, 90, 90, 90, 0, 0, 0, 0],
        [90, 90, 0, 90, 90, 180, 90, 90, 90, 90, 90, 90, 0, 0, 0, 0],
        [90, 90, 0, 90, 90, 180, 90, 90, 90, 90, 90, 90, 0, 0, 0, 0],
        [90, 90, 0, 90, 90, 180, 90, 90, 90, 90, 90, 90, 0, 0, 0, 0],
        [90, 90, 0, 90, 90, 180, 90, 90, 90, 90, 90, 90, 0, 0, 0, 0],
        [90, 90, 0, 90, 90, 180, 90, 90, 90, 90, 90, 90, 0, 0, 0, 0],
    ],
    # M7: Mover ambos brazos (LED azul)
    [
        [90, 90, 120, 130, 70, 60, 50, 110, 90, 90, 90, 90, 0, 0, 255, 10],
        [90, 90, 120, 130, 110, 60, 50, 70, 90, 90, 90, 90, 0, 0, 255, 5],
        [90, 90, 120, 130, 70, 60, 50, 110, 90, 90, 90, 90, 0, 0, 255, 5],
        [90, 90, 120, 130, 110, 60, 50, 70, 90, 90, 90, 90, 0, 0, 255, 5],
        [90, 90, 120, 130, 110, 60, 50, 70, 90, 90, 90, 90, 0, 0, 255, 15],
        [90, 90, 90, 130, 110, 90, 50, 70, 90, 90, 90, 90, 0, 0, 255, 3],
        [90, 90, 120, 130, 110, 60, 50, 70, 90, 90, 90, 90, 0, 0, 255, 3],
        [90, 90, 90, 130, 110, 90, 50, 70, 90, 90, 90, 90, 0, 0, 255, 3],
    ],
    # M8: Despedirse (LED rojo)
    [
        [90, 60, 0, 90, 90, 60, 50, 90, 90, 90, 90, 90, 255, 0, 0, 7],
        [90, 60, 0, 90, 90, 60, 90, 90, 90, 90, 90, 90, 255, 0, 0, 7],
        [90, 90, 0, 90, 90, 180, 90, 90, 90, 90, 90, 90, 0, 0, 0, 0],
        [90, 90, 0, 90, 90, 180, 90, 90, 90, 90, 90, 90, 0, 0, 0, 0],
        [90, 90, 0, 90, 90, 180, 90, 90, 90, 90, 90, 90, 0, 0, 0, 0],
        [90, 90, 0, 90, 90, 180, 90, 90, 90, 90, 90, 90, 0, 0, 0, 0],
        [90, 90, 0, 90, 90, 180, 90, 90, 90, 90, 90, 90, 0, 0, 0, 0],
        [90, 90, 0, 90, 90, 180, 90, 90, 90, 90, 90, 90, 0, 0, 0, 0],
    ],
    # M9: Brazo derecho + cintura (LED azul)
    [
        [90, 90, 90, 130, 110, 180, 50, 90, 90, 90, 90, 90, 0, 0, 0, 10],
        [90, 90, 90, 130, 110, 180, 50, 90, 90, 90, 90, 90, 0, 0, 255, 5],
        [90, 90, 90, 130, 110, 180, 50, 90, 90, 90, 90, 90, 0, 0, 255, 25],
        [90, 90, 90, 130, 90, 180, 50, 90, 90, 90, 90, 90, 0, 0, 0, 5],
        [40, 140, 90, 70, 90, 180, 90, 90, 90, 90, 90, 90, 0, 0, 255, 10],
        [40, 140, 90, 70, 90, 180, 90, 90, 90, 90, 90, 90, 0, 0, 255, 25],
        [90, 90, 0, 90, 90, 180, 90, 90, 90, 90, 90, 90, 0, 0, 0, 0],
        [90, 90, 0, 90, 90, 180, 90, 90, 90, 90, 90, 90, 0, 0, 0, 0],
    ],
]


class RapiroSerialClient:
    """Cliente Rapiro que emula la API serial pero controla los pines GPIO de la Raspberry Pi directamente.

    Implementa la interpolación suave y las secuencias de movimiento emulando
    el bucle de refresco a 50Hz (cada 20ms) del microcontrolador Arduino.
    """

    def __init__(self, port: Optional[str] = None, baud: Optional[int] = None):
        # Para compatibilidad con la firma anterior de la API
        self.port = port or "GPIO"
        self.baud = baud or 57600
        self.last_error: Optional[str] = None

        # Configuración de pines y offsets
        self.pins = DEFAULT_PIN_MAPPING.copy()
        self.trims = DEFAULT_TRIMS.copy()

        # Objetos de control físico
        self.servos: List[Optional[AngularServo]] = [None] * 12
        self.led: Optional[RGBLED] = None

        # Posición inicial / home (coincide con M0 Frame 0)
        self.current_angles = [90.0, 90.0, 0.0, 130.0, 90.0, 180.0, 50.0, 90.0, 90.0, 90.0, 90.0, 90.0]
        self.current_rgb = [0.0, 0.0, 255.0]

        # Estado de interpolación y transición
        self.target_angles = list(self.current_angles)
        self.target_rgb = list(self.current_rgb)
        
        self.step_count = 0
        self.step_delta_angles = [0.0] * 12
        self.step_delta_rgb = [0.0] * 3

        # Estado del parser/máquina de estados de movimiento
        self.mode = 'P'  # 'M' para movimiento continuo, 'P' para pose fija
        self.active_motion = 0
        self.active_frame = 0

        # Control del hilo de fondo
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    @property
    def is_connected(self) -> bool:
        """Determina si la interfaz de control GPIO y el bucle de actualización están activos."""
        return self._running

    def connect(self) -> dict:
        """Inicializa los pines GPIO e inicia el hilo de interpolación a 50Hz."""
        with self._lock:
            if self.is_connected:
                return {"ok": True, "message": "Ya conectado al bus GPIO", "port": self.port}

            try:
                print("[RAPIRO-GPIO] Inicializando pines GPIO con gpiozero...")
                
                # Inicializar 12 servos
                for idx in range(12):
                    pin_key = f"servo_{idx}"
                    pin = self.pins[pin_key]
                    try:
                        # Usamos AngularServo para poder controlar en grados (0 a 180).
                        # Ajustamos anchos de pulso típicos (500us a 2500us) para rango completo.
                        self.servos[idx] = AngularServo(
                            pin, 
                            min_angle=0, 
                            max_angle=180, 
                            min_pulse_width=0.0005, 
                            max_pulse_width=0.0025
                        )
                        # Ir a la posición inicial inmediatamente
                        angle_with_trim = max(0.0, min(180.0, self.current_angles[idx] + self.trims[idx]))
                        self.servos[idx].angle = angle_with_trim
                    except Exception as e:
                        print(f"[RAPIRO-GPIO] Advertencia: No se pudo inicializar servo S{idx:02d} en pin GPIO {pin}: {e}", file=sys.stderr)
                        self.servos[idx] = None

                # Inicializar el LED RGB
                try:
                    self.led = RGBLED(
                        red=self.pins["led_r"],
                        green=self.pins["led_g"],
                        blue=self.pins["led_b"],
                        active_high=True
                    )
                    self.led.color = (self.current_rgb[0]/255.0, self.current_rgb[1]/255.0, self.current_rgb[2]/255.0)
                except Exception as e:
                    print(f"[RAPIRO-GPIO] Advertencia: No se pudo inicializar LED RGB en pines ({self.pins['led_r']}, {self.pins['led_g']}, {self.pins['led_b']}): {e}", file=sys.stderr)
                    self.led = None

                # Iniciar el hilo de actualización de fondo
                self._running = True
                self._thread = threading.Thread(target=self._update_loop, daemon=True)
                self._thread.start()
                
                self.last_error = None
                return {"ok": True, "message": "Interfaz GPIO inicializada y activa", "port": self.port, "baud": self.baud}
            except Exception as exc:
                self.last_error = str(exc)
                self.disconnect()
                return {"ok": False, "message": f"Fallo al conectar GPIO: {exc}", "port": self.port}

    def disconnect(self) -> dict:
        """Detiene el hilo de actualización y libera los pines GPIO."""
        with self._lock:
            self._running = False
            
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
            
        with self._lock:
            # Liberar todos los servos
            for idx in range(12):
                if self.servos[idx] is not None:
                    try:
                        self.servos[idx].close()
                    except Exception:
                        pass
                    self.servos[idx] = None
            
            # Liberar el LED RGB
            if self.led is not None:
                try:
                    self.led.close()
                except Exception:
                    pass
                self.led = None

            return {"ok": True, "message": "Pines GPIO liberados correctamente"}

    def send_command(self, command: str, wait: float = 0.5) -> dict:
        """Parsea y ejecuta un comando en formato serie de Rapiro (e.g. #M1 o #PS00A090T010)."""
        if not command.startswith("#"):
            return {"ok": False, "message": "Los comandos deben empezar con '#'", "command": command}

        with self._lock:
            if not self.is_connected:
                return {"ok": False, "message": "Pines GPIO no inicializados. Llama a connect() primero", "command": command}

            cmd_type = command[1] if len(command) > 1 else ""
            response_payload = ""

            if cmd_type == 'M':
                # Comando de Movimiento (e.g. #M1)
                try:
                    motion_id = int(command[2])
                    if 0 <= motion_id < len(MOTIONS):
                        self.mode = 'M'
                        self.active_motion = motion_id
                        self.active_frame = 0
                        self._load_frame(motion_id, 0)
                        response_payload = f"#M{motion_id}"
                    else:
                        response_payload = "#EM"  # Error en movimiento
                except (ValueError, IndexError):
                    response_payload = "#EM"

            elif cmd_type == 'P':
                # Comando de Pose personalizada (e.g. #PS00A090T010)
                parsed = self._parse_pose_command(command)
                if parsed is not None:
                    servos, leds, duration_tenths = parsed
                    self.mode = 'P'
                    
                    # Actualizar targets
                    for s_id, s_angle in servos.items():
                        if 0 <= s_id < 12:
                            self.target_angles[s_id] = float(s_angle)

                    if 'r' in leds:
                        self.target_rgb[0] = float(leds['r'])
                    if 'g' in leds:
                        self.target_rgb[1] = float(leds['g'])
                    if 'b' in leds:
                        self.target_rgb[2] = float(leds['b'])

                    # Configurar la duración de la transición
                    if duration_tenths > 0:
                        # 20ms por tick = 5 ticks por cada 100ms (décima de segundo)
                        self.step_count = int(duration_tenths * 5)
                        for idx in range(12):
                            self.step_delta_angles[idx] = (self.target_angles[idx] - self.current_angles[idx]) / self.step_count
                        for idx in range(3):
                            self.step_delta_rgb[idx] = (self.target_rgb[idx] - self.current_rgb[idx]) / self.step_count
                    else:
                        # Movimiento instantáneo
                        self.step_count = 0
                        self.current_angles = list(self.target_angles)
                        self.current_rgb = list(self.target_rgb)
                        self._write_hardware()

                    response_payload = f"#PT{duration_tenths:03d}"
                else:
                    response_payload = "#EP"  # Error en pose

            elif cmd_type == 'Q':
                # Consulta de tiempo restante
                tenths = int(self.step_count / 5)
                response_payload = f"#Q{tenths:03d}"

            elif cmd_type == 'C':
                # Consulta de estado del buffer
                response_payload = "#C0"  # Buffer libre

            else:
                response_payload = "#E"  # Comando desconocido/error

        # Simular el retraso especificado por la llamada (reemplazando el bloqueo del puerto serie)
        if wait > 0:
            time.sleep(wait)

        return {
            "ok": True,
            "command": command,
            "response": response_payload
        }

    def test_connection(self) -> dict:
        """Emula el comando de ping serie #C."""
        result = self.send_command("#C", wait=0.1)
        if not result.get("ok"):
            return {"ok": False, "test": "gpio_ping", "message": result.get("message", "Fallo al consultar interfaz")}
        return {
            "ok": True,
            "test": "gpio_ping",
            "message": "Interfaz de control directo GPIO lista",
            "command": "#C",
            "response": result.get("response")
        }

    def build_servo_command(self, servo_id: int, angle: int, duration_ms: int = 500) -> str:
        """Crea el string del comando para posicionar un servo."""
        tenths = max(0, int(duration_ms / 100))
        return f"#PS{servo_id:02d}A{angle:03d}T{tenths:03d}"

    def build_led_command(self, red: int, green: int, blue: int, duration_ms: int = 500) -> str:
        """Crea el string del comando para cambiar el color del LED de los ojos."""
        tenths = max(0, int(duration_ms / 100))
        return f"#PR{red:03d}G{green:03d}B{blue:03d}T{tenths:03d}"

    def status(self) -> dict:
        """Devuelve el estado de la interfaz de control y mapeo de pines."""
        return {
            "connected": self.is_connected,
            "port": self.port,
            "baud": self.baud,
            "last_error": self.last_error,
            "servos": SERVO_NAMES,
            "motions": MOTION_COMMANDS,
            "gpio_pins": self.pins,
            "trims": self.trims
        }

    # --- Funciones internas de control de bucle y hardware ---

    def _update_loop(self):
        """Bucle en segundo plano que corre a 50Hz (cada 20ms) e interpola movimientos."""
        next_tick = time.time()
        while self._running:
            with self._lock:
                if self.step_count > 0:
                    # Avanzar interpolación
                    for idx in range(12):
                        self.current_angles[idx] += self.step_delta_angles[idx]
                        self.current_angles[idx] = max(0.0, min(180.0, self.current_angles[idx]))
                    
                    for idx in range(3):
                        self.current_rgb[idx] += self.step_delta_rgb[idx]
                        self.current_rgb[idx] = max(0.0, min(255.0, self.current_rgb[idx]))

                    self._write_hardware()
                    self.step_count -= 1

                elif self.mode == 'M':
                    # Si no quedan pasos pero estamos en modo de movimiento, cargar siguiente fotograma
                    self._next_frame()

            # Sincronizar el reloj del hilo a intervalos exactos de 20ms para una interpolación suave
            next_tick += 0.02
            sleep_time = next_tick - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                next_tick = time.time()

    def _write_hardware(self):
        """Envía el estado de ángulos y colores RGB actual a los pines del hardware RPi."""
        # Enviar comandos de posición a los servos (sumándole la calibración individual)
        for idx in range(12):
            if self.servos[idx] is not None:
                try:
                    angle_with_trim = self.current_angles[idx] + self.trims[idx]
                    angle_with_trim = max(0.0, min(180.0, angle_with_trim))
                    self.servos[idx].angle = angle_with_trim
                except Exception:
                    pass

        # Enviar comandos de modulación PWM al LED de los ojos
        if self.led is not None:
            try:
                # gpiozero RGBLED usa valores normalizados de 0.0 a 1.0
                self.led.color = (
                    self.current_rgb[0] / 255.0,
                    self.current_rgb[1] / 255.0,
                    self.current_rgb[2] / 255.0
                )
            except Exception:
                pass

    def _load_frame(self, motion_id: int, frame_id: int):
        """Carga un fotograma (frame) de la matriz de movimientos y calcula la trayectoria."""
        frame = MOTIONS[motion_id][frame_id]
        target_angles = frame[:12]
        target_rgb = frame[12:15]
        duration_tenths = frame[15]

        self.target_angles = [float(a) for a in target_angles]
        self.target_rgb = [float(c) for c in target_rgb]

        if duration_tenths > 0:
            self.step_count = int(duration_tenths * 5)
            for idx in range(12):
                self.step_delta_angles[idx] = (self.target_angles[idx] - self.current_angles[idx]) / self.step_count
            for idx in range(3):
                self.step_delta_rgb[idx] = (self.target_rgb[idx] - self.current_rgb[idx]) / self.step_count
        else:
            self.step_count = 0
            self.current_angles = list(self.target_angles)
            self.current_rgb = list(self.target_rgb)
            self._write_hardware()

    def _next_frame(self):
        """Avanza al siguiente frame del movimiento activo. Soporta bucle continuo."""
        self.active_frame += 1
        if self.active_frame >= 8:
            self.active_frame = 0

        # Buscar el siguiente frame que tenga duración > 0 para evitar bloquear el hilo
        found = False
        start_frame = self.active_frame
        for offset in range(8):
            test_frame_id = (start_frame + offset) % 8
            test_frame = MOTIONS[self.active_motion][test_frame_id]
            if test_frame[15] > 0:
                self.active_frame = test_frame_id
                self._load_frame(self.active_motion, self.active_frame)
                found = True
                break

        if not found:
            # Si no hay ningún frame activo con duración, cambiamos a modo estático (Pose)
            self.mode = 'P'
            self.step_count = 0

    def _parse_pose_command(self, command: str) -> Optional[Tuple[Dict[int, int], Dict[str, int], int]]:
        """Analiza un comando de pose para extraer servos, LEDs y duración."""
        if not command.startswith("#P"):
            return None

        servos: Dict[int, int] = {}
        leds: Dict[str, int] = {}
        duration_tenths = 0

        payload = command[2:]

        # Extraer servos (#PSxxAyyy)
        servo_pattern = re.compile(r"S(\d{2})A(\d{3})")
        for match in servo_pattern.finditer(payload):
            s_id = int(match.group(1))
            s_angle = int(match.group(2))
            servos[s_id] = s_angle

        # Extraer LEDs (#PRxxx, #PGyyy, #PBzzz)
        r_match = re.search(r"R(\d{3})", payload)
        if r_match:
            leds['r'] = int(r_match.group(1))
        g_match = re.search(r"G(\d{3})", payload)
        if g_match:
            leds['g'] = int(g_match.group(1))
        b_match = re.search(r"B(\d{3})", payload)
        if b_match:
            leds['b'] = int(b_match.group(1))

        # Extraer duración (Taaa)
        t_match = re.search(r"T(\d{3})", payload)
        if t_match:
            duration_tenths = int(t_match.group(1))

        return servos, leds, duration_tenths
