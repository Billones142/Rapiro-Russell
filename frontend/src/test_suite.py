"""Test routines for Rapiro servomotors, LEDs and predefined motions."""

import time
from typing import Optional

from rapiro_client import MOTION_COMMANDS, SERVO_NAMES, RapiroSerialClient

# RGB test colors for the eye LEDs (Rapiro uses PWM RGB, not addressable NeoPixels)
LED_TEST_COLORS = [
    {"name": "off", "r": 0, "g": 0, "b": 0},
    {"name": "red", "r": 255, "g": 0, "b": 0},
    {"name": "green", "r": 0, "g": 255, "b": 0},
    {"name": "blue", "r": 0, "g": 0, "b": 255},
    {"name": "yellow", "r": 255, "g": 255, "b": 0},
    {"name": "cyan", "r": 0, "g": 255, "b": 255},
    {"name": "magenta", "r": 255, "g": 0, "b": 255},
    {"name": "white", "r": 255, "g": 255, "b": 255},
]


def _ensure_connected(client: RapiroSerialClient) -> Optional[dict]:
    if client.is_connected:
        return None
    connect_result = client.connect()
    if not connect_result.get("ok"):
        return {"ok": False, "message": connect_result.get("message")}
    return None


def test_serial(client: RapiroSerialClient) -> dict:
    """Verify basic serial communication with the Rapiro board."""
    error = _ensure_connected(client)
    if error:
        return error
    return client.test_connection()


def test_servo(
    client: RapiroSerialClient,
    servo_id: int,
    min_angle: int = 45,
    max_angle: int = 135,
    center_angle: int = 90,
    duration_ms: int = 400,
) -> dict:
    """Exercise a single servo through center, min and max angles."""
    error = _ensure_connected(client)
    if error:
        return error

    if servo_id not in SERVO_NAMES:
        return {"ok": False, "message": f"Invalid servo id {servo_id}. Valid range: 0-11"}

    steps = []
    for angle in (center_angle, min_angle, max_angle, center_angle):
        command = client.build_servo_command(servo_id, angle, duration_ms)
        result = client.send_command(command, wait=duration_ms / 1000 + 0.3)
        steps.append(
            {
                "servo_id": servo_id,
                "servo_name": SERVO_NAMES[servo_id],
                "angle": angle,
                "command": command,
                "ok": result.get("ok", False),
                "response": result.get("response", ""),
            }
        )
        if not result.get("ok"):
            return {
                "ok": False,
                "test": "servo",
                "servo_id": servo_id,
                "servo_name": SERVO_NAMES[servo_id],
                "steps": steps,
                "message": result.get("message", "Servo test failed"),
            }

    return {
        "ok": True,
        "test": "servo",
        "servo_id": servo_id,
        "servo_name": SERVO_NAMES[servo_id],
        "steps": steps,
        "message": f"Servo S{servo_id:02d} ({SERVO_NAMES[servo_id]}) OK",
    }


def test_all_servos(client: RapiroSerialClient, duration_ms: int = 400) -> dict:
    """Run the single-servo test on all 12 servomotors sequentially."""
    error = _ensure_connected(client)
    if error:
        return error

    # Return to home before starting the servo sweep
    home = client.send_command("#M0", wait=2.0)
    if not home.get("ok"):
        return {"ok": False, "test": "servos_all", "message": home.get("message")}

    results = []
    for servo_id in range(12):
        result = test_servo(client, servo_id, duration_ms=duration_ms)
        results.append(result)
        if not result.get("ok"):
            return {
                "ok": False,
                "test": "servos_all",
                "completed": len(results),
                "total": 12,
                "results": results,
                "message": f"Failed on servo S{servo_id:02d}",
            }

    client.send_command("#M0", wait=1.5)
    return {
        "ok": True,
        "test": "servos_all",
        "completed": 12,
        "total": 12,
        "results": results,
        "message": "All 12 servos tested successfully",
    }


def test_neopixel(client: RapiroSerialClient, pause: float = 0.8) -> dict:
    """Cycle through RGB colors on the eye LEDs."""
    error = _ensure_connected(client)
    if error:
        return error

    steps = []
    for color in LED_TEST_COLORS:
        command = client.build_led_command(color["r"], color["g"], color["b"], 300)
        result = client.send_command(command, wait=pause)
        steps.append(
            {
                "color": color["name"],
                "rgb": [color["r"], color["g"], color["b"]],
                "command": command,
                "ok": result.get("ok", False),
                "response": result.get("response", ""),
            }
        )
        if not result.get("ok"):
            return {
                "ok": False,
                "test": "neopixel",
                "steps": steps,
                "message": result.get("message", "LED test failed"),
            }

    # Turn LEDs off at the end
    client.send_command(client.build_led_command(0, 0, 0, 200), wait=0.5)
    return {
        "ok": True,
        "test": "neopixel",
        "steps": steps,
        "message": "Eye LED color cycle completed",
    }


def test_motion(client: RapiroSerialClient, motion_id: int, duration: float = 3.0) -> dict:
    """Execute a predefined motion command (#M0-#M9)."""
    error = _ensure_connected(client)
    if error:
        return error

    if motion_id not in MOTION_COMMANDS:
        return {"ok": False, "message": f"Invalid motion id {motion_id}. Valid range: 0-9"}

    command = f"#M{motion_id}"
    result = client.send_command(command, wait=duration)
    return {
        "ok": result.get("ok", False),
        "test": "motion",
        "motion_id": motion_id,
        "motion_name": MOTION_COMMANDS[motion_id],
        "command": command,
        "response": result.get("response", ""),
        "message": MOTION_COMMANDS[motion_id],
    }


def test_all_motions(client: RapiroSerialClient, motion_pause: float = 2.5) -> dict:
    """Run all predefined motion commands except walking (M1-M4) to avoid movement."""
    error = _ensure_connected(client)
    if error:
        return error

    # Safe motions for bench testing: home + gesture motions
    safe_motions = [0, 5, 6, 7, 8, 9]
    results = []
    for motion_id in safe_motions:
        result = test_motion(client, motion_id, duration=motion_pause)
        results.append(result)
        if not result.get("ok"):
            return {
                "ok": False,
                "test": "motions_safe",
                "results": results,
                "message": f"Motion M{motion_id} failed",
            }

    client.send_command("#M0", wait=1.5)
    return {
        "ok": True,
        "test": "motions_safe",
        "results": results,
        "message": "Safe motion tests completed",
    }


def test_full_diagnostic(client: RapiroSerialClient) -> dict:
    """Run a complete diagnostic: serial, LEDs, servos and safe motions."""
    error = _ensure_connected(client)
    if error:
        return error

    report = {"ok": True, "test": "full_diagnostic", "sections": []}

    serial_result = test_serial(client)
    report["sections"].append({"name": "serial", **serial_result})
    if not serial_result.get("ok"):
        report["ok"] = False
        report["message"] = "Full diagnostic failed at serial test"
        return report

    led_result = test_neopixel(client)
    report["sections"].append({"name": "neopixel", **led_result})
    if not led_result.get("ok"):
        report["ok"] = False
        report["message"] = "Full diagnostic failed at LED test"
        return report

    servo_result = test_all_servos(client)
    report["sections"].append({"name": "servos", **servo_result})
    if not servo_result.get("ok"):
        report["ok"] = False
        report["message"] = "Full diagnostic failed at servo test"
        return report

    motion_result = test_all_motions(client)
    report["sections"].append({"name": "motions", **motion_result})
    if not motion_result.get("ok"):
        report["ok"] = False
        report["message"] = "Full diagnostic failed at motion test"
        return report

    client.send_command("#M0", wait=1.0)
    report["message"] = "Full diagnostic completed successfully"
    return report
