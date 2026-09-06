"""NVIDIA AI sentiment analysis with graceful fallback."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

import requests
from django.conf import settings

logger = logging.getLogger("chatbot")

ALLOWED_SENTIMENTS = {"POSITIVE", "NEUTRAL", "NEGATIVE", "ANGRY"}

SENTIMENT_SYSTEM_PROMPT = """You are a sentiment classifier for a food delivery customer support chatbot.
Analyze the user's message and return ONLY valid JSON with this exact shape:
{"sentiment": "POSITIVE|NEUTRAL|NEGATIVE|ANGRY", "confidence": 0.0}
Rules:
- Prefer ANGRY when the user is furious, insulting, uses caps/exclamation rage, or says the situation is unacceptable.
- Use NEGATIVE for unhappy, disappointed, or complaining tone without rage.
- Use POSITIVE for gratitude, praise, or satisfaction.
- Use NEUTRAL for factual questions or calm statements.
Do not include markdown fences or any extra text."""


class SentimentService:
    """Call NVIDIA chat completions to classify sentiment."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        timeout: float = 12.0,
    ) -> None:
        self.api_key = api_key if api_key is not None else settings.NVIDIA_API_KEY
        self.model = model if model is not None else settings.NVIDIA_MODEL
        self.base_url = (base_url or settings.NVIDIA_API_BASE_URL).rstrip("/")
        self.timeout = timeout

    def analyze(self, message: str) -> dict[str, Any]:
        """Return sentiment and confidence. Falls back to NEUTRAL on failure."""
        if not message or not message.strip():
            return {"sentiment": "NEUTRAL", "confidence": 1.0, "source": "fallback"}

        if not self.api_key:
            logger.warning("NVIDIA_API_KEY missing; using NEUTRAL sentiment fallback.")
            return {"sentiment": "NEUTRAL", "confidence": 0.0, "source": "fallback"}

        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": SENTIMENT_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Classify sentiment for this message:\n{message}",
                    },
                ],
                "temperature": 0.1,
                "max_tokens": 80,
            }
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            parsed = self._parse_response(content)
            if parsed:
                return parsed
            logger.warning("Invalid NVIDIA sentiment response: %s", content)
        except Exception as exc:  # noqa: BLE001 — must never crash chat flow
            logger.error("Sentiment analysis unavailable: %s", exc)

        return {"sentiment": "NEUTRAL", "confidence": 0.0, "source": "fallback"}

    def _parse_response(self, content: str) -> dict[str, Any] | None:
        text = content.strip()
        fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if fence_match:
            text = fence_match.group(1)
        else:
            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if json_match:
                text = json_match.group(0)

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return None

        sentiment = str(data.get("sentiment", "")).upper().strip()
        if sentiment not in ALLOWED_SENTIMENTS:
            return None

        try:
            confidence = float(data.get("confidence", 0.0))
        except (TypeError, ValueError):
            confidence = 0.0

        return {
            "sentiment": sentiment,
            "confidence": max(0.0, min(1.0, confidence)),
            "source": "nvidia",
        }
