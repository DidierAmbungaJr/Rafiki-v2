from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class RaspberryConfig:
    serial_port: str = os.getenv("RAFIKI_SERIAL_PORT", "/dev/ttyUSB0")
    serial_baudrate: int = int(os.getenv("RAFIKI_SERIAL_BAUDRATE", "115200"))
    llm_base_url: str = os.getenv("RAFIKI_LLM_BASE_URL", "http://127.0.0.1:8000/chat")
    model_name: str = os.getenv("RAFIKI_MODEL_NAME", "")
    voice_enabled: bool = os.getenv("RAFIKI_VOICE_ENABLED", "true").lower() == "true"
    vision_enabled: bool = os.getenv("RAFIKI_VISION_ENABLED", "false").lower() == "true"
    robot_name: str = os.getenv("RAFIKI_NAME", "Rafiki")


CONFIG = RaspberryConfig()
