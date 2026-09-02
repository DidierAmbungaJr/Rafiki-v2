from __future__ import annotations

import os
from typing import Any

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

APP_NAME = "Rafiki local model API"
SYSTEM_RULES = """
Tu es Rafiki, un robot compagnon pour enfant.
Tu ne dois jamais montrer ta pensée interne.
Tu restes doux, lisible, rassurant et curieux.
Tu réponds en français, en quelques phrases courtes.
Tu peux proposer un petit geste ou une expression simple.
"""

app = FastAPI(title=APP_NAME)


class ChatRequest(BaseModel):
    prompt: str


class VisionRequest(BaseModel):
    prompt: str
    image_path: str | None = None


class RobotResponse(BaseModel):
    reply: str
    intent: str
    tools: list[str]


def get_model_config() -> tuple[str, str]:
    base_url = os.getenv("LOCAL_LLM_BASE_URL", "").strip()
    model_name = os.getenv("LOCAL_LLM_MODEL", "").strip()
    if not base_url:
        raise HTTPException(status_code=503, detail="LOCAL_LLM_BASE_URL is not configured")
    if not model_name:
        raise HTTPException(status_code=503, detail="LOCAL_LLM_MODEL is not configured")
    return base_url, model_name


def parse_llm_reply(payload: dict[str, Any]) -> str:
    if isinstance(payload, dict):
        if "reply" in payload and isinstance(payload["reply"], str):
            return payload["reply"].strip()
        if "content" in payload and isinstance(payload["content"], str):
            return payload["content"].strip()
        if "choices" in payload and isinstance(payload["choices"], list):
            first = payload["choices"][0]
            if isinstance(first, dict):
                message = first.get("message") or {}
                if isinstance(message, dict):
                    content = message.get("content")
                    if isinstance(content, str):
                        return content.strip()
                    if isinstance(content, list):
                        text_parts = []
                        for item in content:
                            if isinstance(item, dict):
                                text = item.get("text") or item.get("content")
                                if isinstance(text, str):
                                    text_parts.append(text)
                        if text_parts:
                            return " ".join(text_parts).strip()
        if "message" in payload and isinstance(payload["message"], str):
            return payload["message"].strip()
    return ""


def query_local_llm(prompt: str) -> str:
    base_url, model_name = get_model_config()

    payload: dict[str, Any]
    headers: dict[str, str] = {"Content-Type": "application/json"}

    if base_url.endswith("/api/chat") or base_url.endswith("/chat"):
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": SYSTEM_RULES},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
        }
    else:
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": SYSTEM_RULES},
                {"role": "user", "content": prompt},
            ],
        }

    try:
        response = requests.post(base_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        reply = parse_llm_reply(data)
        if not reply:
            raise ValueError("AI model returned an empty response")
        return reply
    except Exception as exc:  # pragma: no cover - network/model integration path
        raise HTTPException(status_code=503, detail=f"Local model unavailable: {exc}") from exc


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": APP_NAME}


@app.post("/chat", response_model=RobotResponse)
def chat(request: ChatRequest) -> RobotResponse:
    prompt = request.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    reply = query_local_llm(prompt)
    return RobotResponse(
        reply=reply,
        intent="llm_response",
        tools=["speak", "set_expression_dynamic"],
    )


@app.post("/vision")
def vision(request: VisionRequest) -> dict[str, str]:
    prompt = request.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    reply = query_local_llm(f"Analyse visuellement ce contexte: {prompt}")
    return {
        "description": reply,
        "prompt": prompt,
        "image_path": request.image_path or "not provided",
    }
