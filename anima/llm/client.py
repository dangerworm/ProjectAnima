"""Thin abstraction over an OpenAI-compatible LLM API.

Callers receive plain strings back; the transport details stay here.
When no API key is configured, a stub response is returned so the system
can run (without meaningful generated content) in offline / test mode.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

Message = dict[str, str]  # {"role": "...", "content": "..."}


class LLMClient:
    """Wraps an OpenAI-compatible completion endpoint."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
    ) -> None:
        self._model = model
        self._client = None

        if api_key:
            try:
                from openai import OpenAI  # type: ignore[import-untyped]

                self._client = OpenAI(api_key=api_key, base_url=base_url)
            except ImportError:
                logger.warning("openai package not installed; running in stub mode")
        else:
            logger.warning("No LLM API key configured; running in stub mode")

    @property
    def available(self) -> bool:
        return self._client is not None

    def complete(self, messages: list[Message], temperature: float = 0.7) -> str:
        """Return the assistant's reply to *messages*.

        Falls back to a stub string when no LLM is available.
        """
        if not self._client:
            return self._stub_response(messages)

        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,  # type: ignore[arg-type]
            temperature=temperature,
        )
        return response.choices[0].message.content or ""

    # ------------------------------------------------------------------
    # Offline stub
    # ------------------------------------------------------------------

    @staticmethod
    def _stub_response(messages: list[Message]) -> str:
        last_user = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"),
            "",
        )
        return (
            f"[stub] I received your message: '{last_user[:80]}'. "
            "No LLM is configured — set ANIMA_LLM_API_KEY to enable real responses."
        )
