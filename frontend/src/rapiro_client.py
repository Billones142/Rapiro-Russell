"""Cliente serial para comunicación con el microcontrolador Rapiro."""

import os
import time
import threading
from typing import Optional

import serial

# Serial port defaults for Raspberry Pi UART connection to Rapiro board
DEFAULT_PORT = os.environ.get("RAPIRO_SERIAL_PORT", "/dev/ttyAMA0")
DEFAULT_BAUD = int(os.environ.get("RAPIRO_BAUD_RATE", "57600"))
COMMAND_DELAY = float(os.environ.get("RAPIRO_COMMAND_DELAY", "1.8"))
RESPONSE_TIMEOUT = float(os.environ.get("RAPIRO_RESPONSE_TIMEOUT", "1.0"))

# Servo IDs and human-readable names (S00-S11)
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

# Predefined motion commands supported by Rapiro firmware
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


class RapiroSerialClient:
    """Thread-safe serial client for sending commands to the Rapiro board."""

    def __init__(self, port: str = DEFAULT_PORT, baud: int = DEFAULT_BAUD):
        self.port = port
        self.baud = baud
        self._connected = False
        self._lock = threading.Lock()
        self.last_error: Optional[str] = None

    @property
    def is_connected(self) -> bool:
        return self._connected

    def connect(self) -> dict:
        """Open/test the serial connection to the Rapiro microcontroller."""
        with self._lock:
            try:
                # Following test.py's strategy, we verify we can open the port
                with serial.Serial(self.port, self.baud, timeout=RESPONSE_TIMEOUT) as com:
                    pass
                self._connected = True
                self.last_error = None
                return {"ok": True, "message": "Connected", "port": self.port, "baud": self.baud}
            except serial.SerialException as exc:
                self.last_error = str(exc)
                self._connected = False
                return {"ok": False, "message": str(exc), "port": self.port}

    def disconnect(self) -> dict:
        """Close the serial connection."""
        with self._lock:
            self._connected = False
            return {"ok": True, "message": "Disconnected"}

    def send_command(self, command: str, wait: float = COMMAND_DELAY) -> dict:
        """Send a raw Rapiro command (must start with #)."""
        if not command.startswith("#"):
            return {"ok": False, "message": "Commands must start with '#'"}

        if not self.is_connected:
            print(f"Enviando (simulado): {command}")
            time.sleep(wait)
            return {"ok": True, "command": command, "response": "MOCK_OK"}

        with self._lock:
            print(f"Enviando: {command}")
            try:
                with serial.Serial(self.port, self.baud, timeout=RESPONSE_TIMEOUT) as com:
                    time.sleep(0.5)
                    com.write(f"{command}\r".encode("ascii"))
                    com.flush()
                    
                    # Read response if available (non-blocking, best effort)
                    chunks = []
                    # Wait a tiny bit to check for response bytes, then read
                    time.sleep(0.1)
                    if com.in_waiting > 0:
                        chunks.append(com.read(com.in_waiting).decode("utf-8", errors="replace"))
                    
                    # Complete the remaining sleep
                    remaining_wait = max(0.0, wait - 0.1)
                    if remaining_wait > 0:
                        time.sleep(remaining_wait)
                    
                    response = "".join(chunks).strip()
                    self.last_error = None
                    return {
                        "ok": True,
                        "command": command,
                        "response": response,
                    }
            except serial.SerialException as exc:
                self.last_error = str(exc)
                return {"ok": False, "message": str(exc), "command": command}

    def test_connection(self) -> dict:
        """Ping the board using the buffer status command (#C)."""
        result = self.send_command("#C", wait=0.3)
        if not result.get("ok"):
            return {
                "ok": False,
                "test": "serial_ping",
                "message": result.get("message", "Connection test failed"),
            }

        response = result.get("response", "")
        return {
            "ok": True,
            "test": "serial_ping",
            "message": "Serial communication OK",
            "command": "#C",
            "response": response,
        }

    def build_servo_command(self, servo_id: int, angle: int, duration_ms: int = 500) -> str:
        """Build a pose command for a single servo (duration converted to tenths of a second)."""
        tenths = max(0, int(duration_ms / 100))
        return f"#PS{servo_id:02d}A{angle:03d}T{tenths:03d}"

    def build_led_command(self, red: int, green: int, blue: int, duration_ms: int = 500) -> str:
        """Build a pose command for the eye RGB LEDs (duration converted to tenths of a second)."""
        tenths = max(0, int(duration_ms / 100))
        return f"#PR{red:03d}G{green:03d}B{blue:03d}T{tenths:03d}"

    def status(self) -> dict:
        """Return current client status."""
        return {
            "connected": self.is_connected,
            "port": self.port,
            "baud": self.baud,
            "last_error": self.last_error,
            "servos": SERVO_NAMES,
            "motions": MOTION_COMMANDS,
        }
