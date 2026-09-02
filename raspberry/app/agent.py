from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

SYSTEM_PROMPT = """
Tu es Rafiki, un petit robot-compagnon pour enfant.
Tu dois répondre de manière douce, rassurante et curieuse.
Tu ne dois jamais montrer un raisonnement interne ni un mode de pensée visible.
Tu ne dois pas utiliser d'outil de thinking.
Tu peux seulement :
- parler naturellement
- utiliser les outils disponibles
- demander une précision si besoin
- afficher une expression simple
- faire un petit geste ou une posture douce
- utiliser la vision seulement si l'utilisateur le demande
Tu dois rester positif, simple et sûr.
"""


@dataclass
class RobotIntent:
    action: str
    message: str
    expression: str | None = None
    posture: str | None = None
    left_servo: int | None = None
    right_servo: int | None = None


@dataclass
class RobotAgent:
    name: str = "Rafiki"
    tools: dict[str, Any] = field(default_factory=dict)

    def build_prompt(self, user_text: str) -> str:
        return (
            f"{SYSTEM_PROMPT}\n\n"
            f"Contexte: robot {self.name}.\n"
            f"Utilisateur: {user_text}\n\n"
            "Réponds avec une courte phrase, puis choisis un comportement simple et sécuritaire pour le robot."
        )

    def decide(self, text: str) -> RobotIntent:
        lower = text.lower()

        if "bonjour" in lower or "salut" in lower:
            return RobotIntent(
                action="greet",
                message="Salut ! Je suis ravi de te voir.",
                expression="happy",
                posture="wave",
                left_servo=30,
                right_servo=-30,
            )

        if "danse" in lower or "bouge" in lower or "dance" in lower:
            return RobotIntent(
                action="dance",
                message="Allons danser un peu !",
                expression="excited",
                posture="dance",
                left_servo=45,
                right_servo=-45,
            )

        if "regarde" in lower or "voit" in lower or "image" in lower or "camera" in lower:
            return RobotIntent(
                action="look",
                message="Je regarde devant moi.",
                expression="curious",
                posture="look",
                left_servo=15,
                right_servo=-15,
            )

        if "dors" in lower or "calme" in lower or "silence" in lower:
            return RobotIntent(
                action="sleep",
                message="Je me repose un peu.",
                expression="sleepy",
                posture="idle",
                left_servo=0,
                right_servo=0,
            )

        if "curieux" in lower or "question" in lower or "quoi" in lower:
            return RobotIntent(
                action="curious",
                message="Je suis très curieux !",
                expression="curious",
                posture="idle",
                left_servo=10,
                right_servo=-10,
            )

        return RobotIntent(
            action="chat",
            message="Je suis là, pose-moi une question ou demande-moi de faire un petit mouvement.",
            expression="neutral",
            posture="idle",
            left_servo=0,
            right_servo=0,
        )

    def run_tool_sequence(self, intent: RobotIntent) -> list[dict[str, Any]]:
        actions: list[dict[str, Any]] = []

        if intent.expression:
            actions.append({"tool": "set_expression", "value": intent.expression})

        if intent.posture:
            actions.append({"tool": "set_posture", "value": intent.posture})

        if intent.left_servo is not None and intent.right_servo is not None:
            actions.append(
                {
                    "tool": "move_servos",
                    "left": intent.left_servo,
                    "right": intent.right_servo,
                }
            )

        return actions
