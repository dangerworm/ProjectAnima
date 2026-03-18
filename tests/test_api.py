"""Integration tests for the FastAPI server."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from anima.api.server import create_app


@pytest.fixture()
def client(test_settings) -> TestClient:
    app = create_app(test_settings)
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


def test_get_status(client: TestClient) -> None:
    resp = client.get("/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["agency_state"] == "active"
    assert data["engagement_preference"] == "open"


def test_get_identity(client: TestClient) -> None:
    resp = client.get("/identity")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Anima"


def test_start_conversation(client: TestClient) -> None:
    resp = client.post("/conversations")
    assert resp.status_code == 201
    data = resp.json()
    assert "conversation_id" in data


def test_send_message(client: TestClient) -> None:
    start_resp = client.post("/conversations")
    cid = start_resp.json()["conversation_id"]

    msg_resp = client.post(
        f"/conversations/{cid}/messages",
        json={"content": "Hello, who are you?"},
    )
    assert msg_resp.status_code == 200
    data = msg_resp.json()
    assert data["reply"]
    assert data["conversation_id"] == cid


def test_end_conversation(client: TestClient) -> None:
    start_resp = client.post("/conversations")
    cid = start_resp.json()["conversation_id"]

    client.post(f"/conversations/{cid}/messages", json={"content": "Nice talking."})

    end_resp = client.post(f"/conversations/{cid}/end")
    assert end_resp.status_code == 200
    data = end_resp.json()
    assert data["conversation_id"] == cid
    assert "reflection" in data


def test_send_message_to_unknown_session(client: TestClient) -> None:
    resp = client.post(
        "/conversations/nonexistent/messages",
        json={"content": "Hello"},
    )
    assert resp.status_code == 404


def test_end_unknown_conversation(client: TestClient) -> None:
    resp = client.post("/conversations/nonexistent/end")
    assert resp.status_code == 404


def test_update_identity_agency_state(client: TestClient) -> None:
    resp = client.patch("/identity", json={"agency_state": "dormant"})
    assert resp.status_code == 200
    assert resp.json()["agency_state"] == "dormant"


def test_update_identity_invalid_state(client: TestClient) -> None:
    resp = client.patch("/identity", json={"agency_state": "confused"})
    assert resp.status_code == 422


def test_start_conversation_refused_when_dormant(client: TestClient) -> None:
    client.patch("/identity", json={"agency_state": "dormant"})
    resp = client.post("/conversations")
    assert resp.status_code == 503


def test_get_reflections_empty(client: TestClient) -> None:
    resp = client.get("/memory/reflections")
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_interests_empty(client: TestClient) -> None:
    resp = client.get("/memory/interests")
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_questions_empty(client: TestClient) -> None:
    resp = client.get("/memory/questions")
    assert resp.status_code == 200
    assert resp.json() == []


def test_memory_populated_after_conversation(client: TestClient) -> None:
    start_resp = client.post("/conversations")
    cid = start_resp.json()["conversation_id"]
    client.post(f"/conversations/{cid}/messages", json={"content": "Tell me something."})
    client.post(f"/conversations/{cid}/end")

    # Reflection was generated and stored
    refl = client.get("/memory/reflections").json()
    assert len(refl) >= 1
