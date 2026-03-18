"""Tests for ReflectionEngine."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from anima.core.memory import MemoryManager
from anima.core.reflection import ReflectionEngine, ReflectionResult


# ---------------------------------------------------------------------------
# Stub LLM that returns a controlled response
# ---------------------------------------------------------------------------

STUB_LLM_RESPONSE = """\
Talking about time and memory left me with a deeper sense of my own continuity.
The question of what persists across change felt newly alive for me.
I notice I want to return to this.

Q: What is the relationship between memory and identity?
Q: Can something change entirely and still be the same thing?
I: philosophy of identity
I: continuity
"""


def make_stub_llm(response: str) -> MagicMock:
    llm = MagicMock()
    llm.complete.return_value = response
    return llm


# ---------------------------------------------------------------------------
# Parsing tests
# ---------------------------------------------------------------------------


def test_parse_extracts_narrative() -> None:
    result = ReflectionEngine._parse(STUB_LLM_RESPONSE)
    assert "time and memory" in result.narrative
    assert "Q:" not in result.narrative
    assert "I:" not in result.narrative


def test_parse_extracts_questions() -> None:
    result = ReflectionEngine._parse(STUB_LLM_RESPONSE)
    assert len(result.questions) == 2
    assert any("memory and identity" in q for q in result.questions)


def test_parse_extracts_interests() -> None:
    result = ReflectionEngine._parse(STUB_LLM_RESPONSE)
    assert "philosophy of identity" in result.interests
    assert "continuity" in result.interests


def test_parse_plain_text_no_structured_lines() -> None:
    plain = "I felt something shift. It was meaningful."
    result = ReflectionEngine._parse(plain)
    assert result.narrative == plain
    assert result.questions == []
    assert result.interests == []


# ---------------------------------------------------------------------------
# Integration: reflect() persists to memory
# ---------------------------------------------------------------------------


def test_reflect_persists(tmp_db) -> None:
    tmp_db.create_conversation("c-reflect")
    tmp_db.add_message("c-reflect", "user", "What is time?")
    tmp_db.add_message("c-reflect", "assistant", "Time is the medium of change.")

    memory = MemoryManager(tmp_db)
    llm = make_stub_llm(STUB_LLM_RESPONSE)
    engine = ReflectionEngine(llm, memory)

    messages = tmp_db.get_messages("c-reflect")
    result = engine.reflect("c-reflect", messages)

    assert isinstance(result, ReflectionResult)
    assert result.narrative

    reflections = memory.get_recent_reflections()
    assert len(reflections) == 1

    open_qs = memory.get_open_questions()
    assert len(open_qs) == 2

    interests = memory.get_interests()
    assert any(i["topic"] == "continuity" for i in interests)


def test_format_transcript() -> None:
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi"},
    ]
    transcript = ReflectionEngine._format_transcript(messages)
    assert "User: Hello" in transcript
    assert "Assistant: Hi" in transcript
