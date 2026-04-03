"""Tests for the Database persistence layer."""

from __future__ import annotations

from anima.storage.database import Database


def test_identity_seed_and_read(tmp_db: Database) -> None:
    tmp_db.set_identity_field("name", "TestBeing")
    data = tmp_db.get_identity()
    assert data["name"] == "TestBeing"


def test_identity_upsert(tmp_db: Database) -> None:
    tmp_db.set_identity_field("name", "First")
    tmp_db.set_identity_field("name", "Second")
    assert tmp_db.get_identity()["name"] == "Second"


def test_conversation_lifecycle(tmp_db: Database) -> None:
    cid = "conv-001"
    tmp_db.create_conversation(cid)
    tmp_db.add_message(cid, "user", "Hello")
    tmp_db.add_message(cid, "assistant", "Hi there")
    msgs = tmp_db.get_messages(cid)
    assert len(msgs) == 2
    assert msgs[0]["role"] == "user"
    assert msgs[1]["role"] == "assistant"


def test_end_conversation(tmp_db: Database) -> None:
    cid = "conv-002"
    tmp_db.create_conversation(cid)
    tmp_db.end_conversation(cid, summary="It was good.")
    convs = tmp_db.get_recent_conversations()
    assert any(c["id"] == cid and c["summary"] == "It was good." for c in convs)


def test_reflections(tmp_db: Database) -> None:
    cid = "conv-003"
    tmp_db.create_conversation(cid)
    tmp_db.add_reflection(cid, "Something shifted in my understanding of time.")
    reflections = tmp_db.get_recent_reflections()
    assert len(reflections) == 1
    assert "time" in reflections[0]["content"]


def test_interests_accumulate(tmp_db: Database) -> None:
    tmp_db.upsert_interest("consciousness", 2.0)
    tmp_db.upsert_interest("consciousness", 3.0)
    interests = tmp_db.get_interests()
    assert interests[0]["topic"] == "consciousness"
    assert interests[0]["strength"] == 5.0


def test_interests_cap_at_ten(tmp_db: Database) -> None:
    for _ in range(20):
        tmp_db.upsert_interest("continuity", 1.0)
    interests = tmp_db.get_interests()
    assert interests[0]["strength"] == 10.0


def test_questions_lifecycle(tmp_db: Database) -> None:
    qid = tmp_db.add_question("What does it mean to exist across time?")
    open_qs = tmp_db.get_open_questions()
    assert any(q["id"] == qid for q in open_qs)

    tmp_db.resolve_question(qid)
    open_qs_after = tmp_db.get_open_questions()
    assert not any(q["id"] == qid for q in open_qs_after)


def test_heartbeat(tmp_db: Database) -> None:
    assert tmp_db.get_last_heartbeat() is None
    tmp_db.record_heartbeat("active")
    tmp_db.record_heartbeat("dormant")
    last = tmp_db.get_last_heartbeat()
    assert last is not None
    assert last["status"] == "dormant"
