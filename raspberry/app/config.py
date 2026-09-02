from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class RaspberryConfig:
    serial_port: str = os.getenv(
        "RAFIKI_SERIAL_PORT",
        "/dev/serial/by-id/usb-Arduino__www.arduino.cc__Arduino_Mega_2560_7593231303935171F1F1-if00",
    )
    serial_baudrate: int = int(os.getenv("RAFIKI_SERIAL_BAUDRATE", "115200"))
    llm_base_url: str = os.getenv("RAFIKI_LLM_BASE_URL", "http://127.0.0.1:8000/chat")
    model_name: str = os.getenv("RAFIKI_MODEL_NAME", "")
    voice_enabled: bool = os.getenv("RAFIKI_VOICE_ENABLED", "true").lower() == "true"
    vision_enabled: bool = os.getenv("RAFIKI_VISION_ENABLED", "true").lower() == "true"
    camera_device: str = os.getenv("RAFIKI_CAMERA_DEVICE", "/dev/video0")
    camera_output: str = os.getenv("RAFIKI_CAMERA_OUTPUT", "/tmp/rafiki/latest.jpg")
    audio_device: str = os.getenv("RAFIKI_AUDIO_DEVICE", "hw:2,0")
    listen_seconds: int = int(os.getenv("RAFIKI_LISTEN_SECONDS", "8"))
    voice_threshold: int | None = (
        int(os.getenv("RAFIKI_VOICE_THRESHOLD"))
        if os.getenv("RAFIKI_VOICE_THRESHOLD")
        else None
    )
    piper_model: str = os.getenv(
        "RAFIKI_PIPER_MODEL",
        "models/piper-fr/fr_FR-siwis-medium.onnx",
    )
    robot_name: str = os.getenv("RAFIKI_NAME", "Rafiki")


CONFIG = RaspberryConfig()
