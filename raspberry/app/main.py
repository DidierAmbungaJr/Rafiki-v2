from __future__ import annotations

import sys
from typing import Any

import requests

from agent import RobotAgent
from camera import Camera
from config import CONFIG
from serial_bridge import ArduinoBridge
from speech_input import SpeechInput, default_model_path
from voice import VoiceOutput


class RobotController:
    def __init__(self) -> None:
        self.bridge = ArduinoBridge(CONFIG.serial_port, CONFIG.serial_baudrate)
        self.agent = RobotAgent(name=CONFIG.robot_name)
        self.camera = Camera(device=CONFIG.camera_device)
        self.voice = VoiceOutput(enabled=CONFIG.voice_enabled, model_path=CONFIG.piper_model)

    def connect(self) -> None:
        self.bridge.connect()

    def disconnect(self) -> None:
        self.bridge.idle()
        self.bridge.disconnect()

    def call_local_model(self, user_text: str) -> dict[str, Any]:
        try:
            payload = {"prompt": self.agent.build_prompt(user_text)}
            response = requests.post(
                CONFIG.llm_base_url,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            reply = data.get("reply") or data.get("content") or ""
            tools = data.get("tools", [])
            return {
                "reply": reply,
                "intent": data.get("intent", "llm_response"),
                "tools": tools if isinstance(tools, list) else [],
            }
        except requests.RequestException as exc:
            return {
                "reply": "",
                "intent": "error",
                "tools": [],
                "error": f"Local model request failed: {exc}",
            }

    def process_user_text(self, user_text: str) -> dict[str, Any]:
        intent = self.agent.decide(user_text)
        llm_reply = self.call_local_model(user_text)
        camera_path = ""
        requested_tools = llm_reply.get("tools", [])
        actions = []
        if CONFIG.vision_enabled and any(
            tool in requested_tools for tool in ("capture_camera", "vision")
        ):
            camera_path = self.camera.capture(CONFIG.camera_output)
            actions = [*actions, {"tool": "capture_camera", "path": camera_path}]

        actions = self.agent.run_tool_sequence(intent)
        for action in actions:
            tool = action["tool"]
            if tool == "set_expression":
                self.bridge.set_expression(action["value"])
            elif tool == "set_posture":
                self.bridge.set_posture(action["value"])
            elif tool == "move_servos":
                self.bridge.move_servos(action["left"], action["right"])

        spoken_text = llm_reply.get("reply", "") or intent.message
        spoken = self.voice.speak(spoken_text)

        return {
            "intent": intent.action,
            "message": intent.message,
            "llm_reply": llm_reply.get("reply", ""),
            "tools_executed": actions,
            "spoken": spoken,
            "camera_path": camera_path,
            "requested_tools": requested_tools,
            "error": llm_reply.get("error", ""),
        }


def run_demo() -> None:
    controller = RobotController()
    controller.connect()

    examples = [
        "salut Rafiki",
        "danse un peu",
        "regarde devant toi",
        "dis-moi quelque chose",
    ]

    for text in examples:
        result = controller.process_user_text(text)
        print(f"USER: {text}")
        print(f"INTENT: {result['intent']}")
        print(f"MESSAGE: {result['message']}")
        print(f"LLM: {result['llm_reply']}")
        print(f"TOOLS: {result['tools_executed']}")
        if result.get("error"):
            print(f"ERROR: {result['error']}")

    controller.disconnect()


def capture_camera() -> None:
    path = Camera(device=CONFIG.camera_device).capture(CONFIG.camera_output)
    print(f"Image capturée: {path}")


def run_listen() -> None:
    controller = RobotController()
    speech = SpeechInput(
        default_model_path(),
        device=CONFIG.audio_device,
        threshold=CONFIG.voice_threshold,
    )
    controller.connect()
    print("Écoute active. Ctrl+C pour arrêter.")
    try:
        while True:
            print("Parle maintenant...")
            text = speech.listen(CONFIG.listen_seconds)
            if not text:
                print("Aucune phrase détectée.")
                continue
            print(f"USER: {text}")
            print(controller.process_user_text(text))
    except KeyboardInterrupt:
        print("Arrêt de l'écoute.")
    finally:
        controller.disconnect()


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--capture":
        capture_camera()
        raise SystemExit(0)
    if len(sys.argv) == 2 and sys.argv[1] == "--listen":
        run_listen()
        raise SystemExit(0)
    if len(sys.argv) > 1:
        controller = RobotController()
        controller.connect()
        try:
            result = controller.process_user_text(" ".join(sys.argv[1:]))
            print(result)
        finally:
            controller.disconnect()
    else:
        run_demo()
