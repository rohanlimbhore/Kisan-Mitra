import base64
import json
from typing import Any

import requests
from flask import current_app


class AIServiceError(Exception):
    """Raised when the AI provider cannot process a request."""


def _headers() -> dict[str, str]:
    api_key = current_app.config.get("AI_API_KEY", "")
    if not api_key:
        # Place your AI provider API key in .env as AI_API_KEY for production.
        raise AIServiceError("AI service is not configured yet.")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def _chat_completion(messages: list[dict[str, Any]]) -> str:
    payload = {
        "model": current_app.config["AI_MODEL"],
        "messages": messages,
        "temperature": 0.2,
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=_headers(),
        data=json.dumps(payload),
        timeout=45,
    )
    if response.status_code >= 400:
        raise AIServiceError("Unable to fetch response from AI service.")
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()


def ask_assistant(user_message: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "You are Krishi Mitra, an agriculture advisor for Indian farmers. "
                "Respond with practical, region-aware guidance in simple language. "
                "Detect language from user message and reply in same language."
            ),
        },
        {"role": "user", "content": user_message},
    ]
    return _chat_completion(messages)


def explain_government_scheme(query: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "Explain Indian agriculture government schemes with eligibility, "
                "required documents, and how to apply. Keep response structured "
                "with bullet points."
            ),
        },
        {"role": "user", "content": query},
    ]
    return _chat_completion(messages)


def diagnose_crop_issue(image_bytes: bytes, filename: str) -> str:
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    messages = [
        {
            "role": "system",
            "content": (
                "You are an agronomy assistant. Diagnose visible crop disease/stress, "
                "possible causes, urgency level, and action plan for small farmers in India."
            ),
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Analyze this crop image and provide a structured diagnosis."},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/{filename.rsplit('.', 1)[-1]};base64,{encoded}"},
                },
            ],
        },
    ]
    return _chat_completion(messages)
