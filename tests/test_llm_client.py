"""Tests for the LLM client (stub mode)."""

from __future__ import annotations

from anima.llm.client import LLMClient


def test_stub_mode_when_no_key() -> None:
    client = LLMClient(api_key="", base_url="", model="gpt-4o")
    assert client.available is False


def test_stub_response_contains_user_message() -> None:
    client = LLMClient(api_key="", base_url="", model="gpt-4o")
    messages = [{"role": "user", "content": "What is consciousness?"}]
    response = client.complete(messages)
    assert "What is consciousness?" in response
    assert "[stub]" in response


def test_stub_response_with_no_user_message() -> None:
    client = LLMClient(api_key="", base_url="", model="gpt-4o")
    response = client.complete([{"role": "system", "content": "System prompt"}])
    assert "[stub]" in response
