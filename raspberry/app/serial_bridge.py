from __future__ import annotations

import json
import time
from typing import Any

import serial


class ArduinoBridge:
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn: serial.Serial | None = None

    def connect(self) -> None:
        self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        time.sleep(2)

    def disconnect(self) -> None:
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()

    def send_command(self, command: dict[str, Any]) -> dict[str, Any]:
        if self.serial_conn is None or not self.serial_conn.is_open:
            raise RuntimeError("Arduino serial connection is not open")

        payload = json.dumps(command)
        self.serial_conn.write((payload + "\n").encode("utf-8"))
        self.serial_conn.flush()

        response = self.serial_conn.readline().decode("utf-8", errors="replace").strip()
        if not response:
            return {"status": "ok"}

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"status": "ok", "raw": response}

    def set_expression(self, name: str) -> dict[str, Any]:
        return self.send_command({"type": "expression", "value": name})

    def set_posture(self, name: str) -> dict[str, Any]:
        return self.send_command({"type": "posture", "value": name})

    def move_servos(self, left_angle: int, right_angle: int) -> dict[str, Any]:
        return self.send_command({
            "type": "servo",
            "left": left_angle,
            "right": right_angle,
        })

    def idle(self) -> dict[str, Any]:
        return self.send_command({"type": "idle"})

    def dance(self) -> dict[str, Any]:
        return self.send_command({"type": "dance"})
