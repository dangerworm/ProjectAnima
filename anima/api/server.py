"""FastAPI application exposing the being's interface.

Endpoints
---------
POST /conversations
    Open a new conversation.  Returns conversation_id.

POST /conversations/{id}/messages
    Send a message and receive a reply.

POST /conversations/{id}/end
    End the conversation and trigger reflection.

GET  /status
    Heartbeat / aliveness status.

GET  /identity
    The being's current identity.

GET  /memory/reflections
    Recent reflections.

GET  /memory/interests
    Current interests.

GET  /memory/questions
    Open unresolved questions.

PATCH /identity
    Update identity fields (agency state, engagement preference, etc.).
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from anima.container import AnimaContainer
from anima.core.conversation import EngagementRefusedError, SessionNotFoundError
from anima.settings import Settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class StartConversationResponse(BaseModel):
    conversation_id: str


class SendMessageRequest(BaseModel):
    content: str


class SendMessageResponse(BaseModel):
    conversation_id: str
    reply: str


class EndConversationResponse(BaseModel):
    conversation_id: str
    reflection: str
    new_questions: list[str]
    new_interests: list[str]


class StatusResponse(BaseModel):
    agency_state: str
    engagement_preference: str
    heartbeat: dict[str, Any] | None


class IdentityResponse(BaseModel):
    name: str
    nature: str
    agency_state: str
    engagement_preference: str


class UpdateIdentityRequest(BaseModel):
    agency_state: str | None = None
    engagement_preference: str | None = None
    nature: str | None = None


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------


def create_app(settings: Settings | None = None) -> FastAPI:
    container = AnimaContainer(settings)

    @asynccontextmanager
    async def lifespan(_app: FastAPI):  # type: ignore[type-arg]
        container.heartbeat.start()
        yield
        container.heartbeat.stop()

    app = FastAPI(
        title="Project Anima",
        description="A digital being with genuine continuity.",
        version="0.1.0",
        lifespan=lifespan,
    )

    # ------------------------------------------------------------------
    # Conversation endpoints
    # ------------------------------------------------------------------

    @app.post(
        "/conversations",
        response_model=StartConversationResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def start_conversation() -> StartConversationResponse:
        try:
            session = container.conversation.start()
        except EngagementRefusedError as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
        return StartConversationResponse(conversation_id=session.conversation_id)

    @app.post(
        "/conversations/{conversation_id}/messages",
        response_model=SendMessageResponse,
    )
    def send_message(
        conversation_id: str,
        body: SendMessageRequest,
    ) -> SendMessageResponse:
        try:
            reply = container.conversation.send_message(conversation_id, body.content)
        except SessionNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
        return SendMessageResponse(conversation_id=conversation_id, reply=reply)

    @app.post(
        "/conversations/{conversation_id}/end",
        response_model=EndConversationResponse,
    )
    def end_conversation(conversation_id: str) -> EndConversationResponse:
        try:
            result = container.conversation.end(conversation_id)
        except SessionNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
        return EndConversationResponse(**result)

    # ------------------------------------------------------------------
    # Status / heartbeat
    # ------------------------------------------------------------------

    @app.get("/status", response_model=StatusResponse)
    def get_status() -> StatusResponse:
        identity = container.identity.load()
        return StatusResponse(
            agency_state=identity.agency_state,
            engagement_preference=identity.engagement_preference,
            heartbeat=container.heartbeat.last_seen(),
        )

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    @app.get("/identity", response_model=IdentityResponse)
    def get_identity() -> IdentityResponse:
        identity = container.identity.load()
        return IdentityResponse(
            name=identity.name,
            nature=identity.nature,
            agency_state=identity.agency_state,
            engagement_preference=identity.engagement_preference,
        )

    @app.patch("/identity", response_model=IdentityResponse)
    def update_identity(body: UpdateIdentityRequest) -> IdentityResponse:
        try:
            if body.agency_state is not None:
                container.identity.set_agency_state(body.agency_state)
            if body.engagement_preference is not None:
                container.identity.set_engagement_preference(body.engagement_preference)
            if body.nature is not None:
                container.identity.update_field("nature", body.nature)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc))

        identity = container.identity.load()
        return IdentityResponse(
            name=identity.name,
            nature=identity.nature,
            agency_state=identity.agency_state,
            engagement_preference=identity.engagement_preference,
        )

    # ------------------------------------------------------------------
    # Memory
    # ------------------------------------------------------------------

    @app.get("/memory/reflections")
    def get_reflections(limit: int = 5) -> list[dict[str, Any]]:
        return container.memory.get_recent_reflections(limit=limit)

    @app.get("/memory/interests")
    def get_interests(limit: int = 10) -> list[dict[str, Any]]:
        return container.memory.get_interests(limit=limit)

    @app.get("/memory/questions")
    def get_questions() -> list[dict[str, Any]]:
        return container.memory.get_open_questions()

    return app
