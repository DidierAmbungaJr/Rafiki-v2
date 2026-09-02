from __future__ import annotations

import subprocess
from pathlib import Path


class Camera:
    def __init__(self, device: str = "/dev/video0", width: int = 1280, height: int = 720):
        self.device = device
        self.width = width
        self.height = height

    def capture(self, output_path: str) -> str:
        destination = Path(output_path).expanduser().resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-f",
                "video4linux2",
                "-input_format",
                "mjpeg",
                "-video_size",
                f"{self.width}x{self.height}",
                "-i",
                self.device,
                "-frames:v",
                "1",
                "-y",
                str(destination),
            ],
            check=True,
        )
        return str(destination)
