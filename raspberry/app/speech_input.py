from __future__ import annotations

import json
import os
import struct
import subprocess
import time
from pathlib import Path

from vosk import KaldiRecognizer, Model


class SpeechInput:
    def __init__(self, model_path: str, device: str = "default", threshold: int | None = None):
        self.device = device
        self.threshold = threshold
        self.model = Model(model_path)

    def listen(self, max_seconds: int = 8, silence_seconds: float = 0.9) -> str:
        process = subprocess.Popen(
            ["arecord", "-D", self.device, "-q", "-t", "raw", "-f", "S16_LE", "-r", "16000", "-c", "1", "-"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        recognizer = KaldiRecognizer(self.model, 16000)
        started = False
        last_voice = 0.0
        deadline = time.monotonic() + max_seconds
        calibration_deadline = time.monotonic() + 0.5
        noise_levels: list[float] = []
        active_threshold = self.threshold

        try:
            while time.monotonic() < deadline:
                chunk = process.stdout.read(3200) if process.stdout else b""
                if not chunk:
                    break
                recognizer.AcceptWaveform(chunk)
                samples = struct.unpack(f"<{len(chunk) // 2}h", chunk[: len(chunk) // 2 * 2])
                level = sum(abs(sample) for sample in samples) / max(len(samples), 1)
                now = time.monotonic()
                if active_threshold is None and now < calibration_deadline:
                    noise_levels.append(level)
                    continue
                if active_threshold is None:
                    noise_floor = sorted(noise_levels)[len(noise_levels) // 2] if noise_levels else 0
                    active_threshold = max(120, int(noise_floor * 3.5))
                if level >= active_threshold:
                    started = True
                    last_voice = now
                elif started and now - last_voice >= silence_seconds:
                    break

            result = json.loads(recognizer.FinalResult())
            return result.get("text", "").strip()
        finally:
            process.terminate()
            process.wait(timeout=2)

    @classmethod
    def from_environment(cls, model_path: str) -> "SpeechInput":
        device = os.getenv("RAFIKI_AUDIO_DEVICE", "hw:2,0")
        threshold_value = os.getenv("RAFIKI_VOICE_THRESHOLD")
        threshold = int(threshold_value) if threshold_value else None
        return cls(model_path, device=device, threshold=threshold)


def default_model_path() -> str:
    return str(Path(__file__).resolve().parents[1] / "models" / "vosk-model-small-fr-0.22")
