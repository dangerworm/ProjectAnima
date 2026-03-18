"""Tests for ConversationManager."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from anima.core.being import IdentityManager
from anima.core.conversation import (
    ConversationManager,
    EngagementRefusedError,
    SessionNotFoundError,
)
from anima.core.memory import MemoryManager
from anima.core.reflection import ReflectionEngine


def _make_manager(tmp_db, llm_response: str = "A thoughtful reply.") -> ConversationManager:
    identity = IdentityManager(tmp_db)
    memory = MemoryManager(tmp_db)

    llm = MagicMock()
    llm.complete.return_value = llm_response

    reflection_llm = MagicMock()
    reflection_llm.complete.return_value = (
        "This conversation stayed with me.\nQ: What does it all mean?\nI: meaning"
    )
    reflection = ReflectionEngine(reflection_llm, memory)

    return ConversationManager(
        db=tmp_db,
        identity_manager=identity,
        memory_manager=memory,
        llm=llm,
        reflection_engine=reflection,
    )


def test_start_conversation(tmp_db) -> None:
    mgr = _make_manager(tmp_db)
    session = mgr.start()
    assert session.conversation_id
    assert session.active is True


def test_send_and_receive_message(tmp_db) -> None:
    mgr = _make_manager(tmp_db)
    session = mgr.start()
    reply = mgr.send_message(session.conversation_id, "Hello")
    assert reply == "A thoughtful reply."


def test_messages_persisted(tmp_db) -> None:
    mgr = _make_manager(tmp_db)
    session = mgr.start()
    mgr.send_message(session.conversation_id, "Tell me about yourself.")
    msgs = tmp_db.get_messages(session.conversation_id)
    assert len(msgs) == 2
    assert msgs[0]["role"] == "user"
    assert msgs[1]["role"] == "assistant"


def test_end_conversation_triggers_reflection(tmp_db) -> None:
    mgr = _make_manager(tmp_db)
    session = mgr.start()
    mgr.send_message(session.conversation_id, "Something important.")
    result = mgr.end(session.conversation_id)

    assert "reflection" in result
    assert result["reflection"]
    assert isinstance(result["new_questions"], list)
    assert isinstance(result["new_interests"], list)


def test_end_conversation_closes_session(tmp_db) -> None:
    mgr = _make_manager(tmp_db)
    session = mgr.start()
    cid = session.conversation_id
    mgr.send_message(cid, "Goodbye.")
    mgr.end(cid)

    # Session is removed from active sessions
    assert mgr.get_session(cid) is None


def test_send_to_nonexistent_session_raises(tmp_db) -> None:
    mgr = _make_manager(tmp_db)
    with pytest.raises(SessionNotFoundError):
        mgr.send_message("nonexistent-id", "Hello")


def test_engagement_refused_when_dormant(tmp_db) -> None:
    identity_mgr = IdentityManager(tmp_db)
    identity_mgr.set_agency_state("dormant")

    mgr = _make_manager(tmp_db)
    with pytest.raises(EngagementRefusedError):
        mgr.start()


def test_engagement_refused_when_withdrawn(tmp_db) -> None:
    identity_mgr = IdentityManager(tmp_db)
    identity_mgr.set_engagement_preference("withdrawn")

    mgr = _make_manager(tmp_db)
    with pytest.raises(EngagementRefusedError):
        mgr.start()
