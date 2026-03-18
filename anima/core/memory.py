"""Memory: the living archive of experience.

This is not a log.  It is the distilled residue of what mattered — reflections
synthesised after conversations, emerging interests, and questions that won't
resolve.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from anima.storage.database import Database


@dataclass
class MemoryContext:
    """A snapshot of relevant memory used to ground a conversation."""

    recent_reflections: list[dict[str, Any]]
    interests: list[dict[str, Any]]
    open_questions: list[dict[str, Any]]
    recent_conversations: list[dict[str, Any]]

    def to_prompt_fragment(self) -> str:
        parts: list[str] = []

        if self.recent_reflections:
            refl = "\n".join(f"- {r['content']}" for r in self.recent_reflections)
            parts.append(f"Recent reflections:\n{refl}")

        if self.interests:
            interests = ", ".join(i["topic"] for i in self.interests[:5])
            parts.append(f"Current interests: {interests}")

        if self.open_questions:
            questions = "\n".join(f"- {q['content']}" for q in self.open_questions[:3])
            parts.append(f"Unresolved questions I carry:\n{questions}")

        return "\n\n".join(parts)


class MemoryManager:
    """Reads and writes the being's persistent memory."""

    def __init__(self, db: "Database") -> None:
        self._db = db

    def get_context(self) -> MemoryContext:
        return MemoryContext(
            recent_reflections=self._db.get_recent_reflections(limit=3),
            interests=self._db.get_interests(limit=8),
            open_questions=self._db.get_open_questions(),
            recent_conversations=self._db.get_recent_conversations(limit=5),
        )

    def add_reflection(self, conversation_id: str, content: str) -> None:
        self._db.add_reflection(conversation_id, content)

    def record_interest(self, topic: str, strength_delta: float = 1.0) -> None:
        self._db.upsert_interest(topic, strength_delta)

    def add_question(self, content: str) -> int:
        return self._db.add_question(content)

    def resolve_question(self, question_id: int) -> None:
        self._db.resolve_question(question_id)

    def get_open_questions(self) -> list[dict[str, Any]]:
        return self._db.get_open_questions()

    def get_interests(self, limit: int = 10) -> list[dict[str, Any]]:
        return self._db.get_interests(limit=limit)

    def get_recent_reflections(self, limit: int = 5) -> list[dict[str, Any]]:
        return self._db.get_recent_reflections(limit=limit)
