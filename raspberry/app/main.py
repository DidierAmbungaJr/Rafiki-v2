from __future__ import annotations

import sys
from typing import Any

import requests

from agent import RobotAgent
from config import CONFIG
from serial_bridge import ArduinoBridge


class RobotController:
    def __init__(self) -> None:
        self.bridge = ArduinoBridge(CONFIG.serial_port, CONFIG.serial_baudrate)
        self.agent = RobotAgent(name=CONFIG.robot_name)

    def connect(self) -> None:
        self.bridge.connect()

    def disconnect(self) -> None:
        self.bridge.idle()
        self.bridge.disconnect()

    def call_local_model(self, user_text: str) -> dict[str, Any]:
        try:
            payload = {"prompt": user_text}
            response = requests.post(
                CONFIG.llm_base_url,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            reply = data.get("reply") or data.get("content") or ""
            return {"reply": reply, "intent": data.get("intent", "llm_response")}
        except requests.RequestException as exc:
            return {
                "reply": "",
                "intent": "error",
                "error": f"Local model request failed: {exc}",
            }

    def process_user_text(self, user_text: str) -> dict[str, Any]:
        intent = self.agent.decide(user_text)
        llm_reply = self.call_local_model(user_text)

        actions = self.agent.run_tool_sequence(intent)
        for action in actions:
            tool = action["tool"]
            if tool == "set_expression":
                self.bridge.set_expression(action["value"])
            elif tool == "set_posture":
                self.bridge.set_posture(action["value"])
            elif tool == "move_servos":
                self.bridge.move_servos(action["left"], action["right"])

        return {
            "intent": intent.action,
            "message": intent.message,
            "llm_reply": llm_reply.get("reply", ""),
            "tools_executed": actions,
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


if __name__ == "__main__":
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
