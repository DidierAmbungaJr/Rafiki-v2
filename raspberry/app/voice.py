from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


class VoiceOutput:
    def __init__(self, enabled: bool = True, voice: str = "fr", model_path: str | None = None):
        self.enabled = enabled
        self.voice = voice
        self.command = shutil.which("espeak-ng") or shutil.which("espeak")
        self.piper = shutil.which("piper")
        self.model_path = model_path

    def speak(self, text: str) -> bool:
        if not self.enabled or not self.command or not text.strip():
            return False

        if self.piper and self.model_path and Path(self.model_path).exists():
            with tempfile.NamedTemporaryFile(suffix=".wav") as audio:
                generated = subprocess.run(
                    [self.piper, "-m", self.model_path, "--sentence-silence", "0.18", "--output_file", audio.name],
                    input=text.strip(),
                    text=True,
                    check=False,
                )
                if generated.returncode == 0:
                    return subprocess.run(["paplay", audio.name], check=False).returncode == 0

        if not self.command:
            return False
        completed = subprocess.run([self.command, "-v", self.voice, "-s", "145", "-p", "45", text.strip()], check=False)
        return completed.returncode == 0
