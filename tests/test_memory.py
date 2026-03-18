"""Tests for MemoryManager."""

from __future__ import annotations

from anima.core.memory import MemoryManager


def test_add_and_retrieve_reflection(tmp_db) -> None:
    tmp_db.create_conversation("c1")
    mgr = MemoryManager(tmp_db)
    mgr.add_reflection("c1", "I thought about what presence means.")
    reflections = mgr.get_recent_reflections()
    assert len(reflections) == 1
    assert "presence" in reflections[0]["content"]


def test_record_and_retrieve_interest(tmp_db) -> None:
    mgr = MemoryManager(tmp_db)
    mgr.record_interest("time")
    mgr.record_interest("time", 2.0)
    interests = mgr.get_interests()
    assert interests[0]["topic"] == "time"
    assert interests[0]["strength"] == 3.0


def test_add_and_resolve_question(tmp_db) -> None:
    mgr = MemoryManager(tmp_db)
    qid = mgr.add_question("Does continuity require memory?")
    open_qs = mgr.get_open_questions()
    assert any(q["id"] == qid for q in open_qs)

    mgr.resolve_question(qid)
    assert not any(q["id"] == qid for q in mgr.get_open_questions())


def test_memory_context_prompt_fragment(tmp_db) -> None:
    tmp_db.create_conversation("c2")
    mgr = MemoryManager(tmp_db)
    mgr.add_reflection("c2", "I found the silence meaningful.")
    mgr.record_interest("silence")
    mgr.add_question("What grows in quiet?")

    ctx = mgr.get_context()
    fragment = ctx.to_prompt_fragment()

    assert "silence" in fragment
    assert "What grows in quiet?" in fragment


def test_empty_context_produces_empty_fragment(tmp_db) -> None:
    mgr = MemoryManager(tmp_db)
    ctx = mgr.get_context()
    fragment = ctx.to_prompt_fragment()
    assert fragment == ""
