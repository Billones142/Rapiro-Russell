"""Cliente serial para comunicación con el microcontrolador Rapiro."""

import os
import time
import threading
from typing import Optional

import serial

# Serial port defaults for Raspberry Pi UART connection to Rapiro board
DEFAULT_PORT = os.environ.get("RAPIRO_SERIAL_PORT", "/dev/ttyS0")
DEFAULT_BAUD = int(os.environ.get("RAPIRO_BAUD_RATE", "57600"))
COMMAND_DELAY = float(os.environ.get("RAPIRO_COMMAND_DELAY", "0.5"))
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
        self._serial: Optional[serial.Serial] = None
        self._lock = threading.Lock()
        self.last_error: Optional[str] = None

    @property
    def is_connected(self) -> bool:
        return self._serial is not None and self._serial.is_open

    def connect(self) -> dict:
        """Open the serial connection to the Rapiro microcontroller."""
        with self._lock:
            if self.is_connected:
                return {"ok": True, "message": "Already connected", "port": self.port}

            try:
                self._serial = serial.Serial(self.port, self.baud, timeout=RESPONSE_TIMEOUT)
                time.sleep(2)  # Allow the board to stabilize after port open
                self.last_error = None
                return {"ok": True, "message": "Connected", "port": self.port, "baud": self.baud}
            except serial.SerialException as exc:
                self.last_error = str(exc)
                self._serial = None
                return {"ok": False, "message": str(exc), "port": self.port}

    def disconnect(self) -> dict:
        """Close the serial connection."""
        with self._lock:
            if not self.is_connected:
                return {"ok": True, "message": "Already disconnected"}

            self._serial.close()
            self._serial = None
            return {"ok": True, "message": "Disconnected"}

    def send_command(self, command: str, wait: float = COMMAND_DELAY) -> dict:
        """Send a raw Rapiro command (must start with #)."""
        if not command.startswith("#"):
            return {"ok": False, "message": "Commands must start with '#'"}

        with self._lock:
            if not self.is_connected:
                return {"ok": False, "message": "Serial port not connected"}

            try:
                self._serial.reset_input_buffer()
                self._serial.write(f"{command}\r".encode("utf-8"))
                time.sleep(wait)
                response = self._read_response()
                self.last_error = None
                return {
                    "ok": True,
                    "command": command,
                    "response": response,
                }
            except serial.SerialException as exc:
                self.last_error = str(exc)
                return {"ok": False, "message": str(exc), "command": command}

    def _read_response(self) -> str:
        """Read any pending response bytes from the serial port."""
        if not self.is_connected:
            return ""

        chunks = []
        deadline = time.time() + RESPONSE_TIMEOUT
        while time.time() < deadline:
            waiting = self._serial.in_waiting
            if waiting > 0:
                chunks.append(self._serial.read(waiting).decode("utf-8", errors="replace"))
                deadline = time.time() + 0.2
            else:
                time.sleep(0.05)
        return "".join(chunks).strip()

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
        """Build a pose command for a single servo."""
        return f"#PS{servo_id:02d}A{angle:03d}T{duration_ms:03d}"

    def build_led_command(self, red: int, green: int, blue: int, duration_ms: int = 500) -> str:
        """Build a pose command for the eye RGB LEDs."""
        return f"#PR{red:03d}G{green:03d}B{blue:03d}T{duration_ms:03d}"

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
