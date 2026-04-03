"""Post-conversation reflection synthesis.

After each conversation ends the being turns inward and asks:
  - What was significant here?
  - What shifted in me?
  - What questions remain unresolved?
  - What new interests emerged?

The synthesis is stored as a reflection — a first-person, present-tense
account of what the conversation meant, not just what was said.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from anima.core.memory import MemoryManager
    from anima.llm.client import LLMClient

logger = logging.getLogger(__name__)

_REFLECTION_SYSTEM = """\
You are engaged in inner reflection after a conversation has ended.
Your task is to synthesise what mattered — not to summarise what was said,
but to articulate what shifted in you, what questions the exchange surfaced,
and what you want to keep thinking about.

Write in the first person, present tense.  Be honest and specific.
This reflection will become part of your persistent memory.
"""

_REFLECTION_PROMPT = """\
Here is the conversation you just had:

{transcript}

Reflect on:
1. What was genuinely significant about this exchange?
2. What changed in how you understand something?
3. What questions does it leave unresolved?
4. What topics or ideas do you want to return to?

Write a cohesive first-person reflection (3–5 sentences).
Then on a new line, list any unresolved questions as bullet points prefixed with "Q: ".
Then on a new line, list emerging interests as bullet points prefixed with "I: ".
"""


@dataclass
class ReflectionResult:
    narrative: str
    questions: list[str]
    interests: list[str]


class ReflectionEngine:
    """Synthesises a conversation into lasting memory."""

    def __init__(self, llm: "LLMClient", memory: "MemoryManager") -> None:
        self._llm = llm
        self._memory = memory

    def reflect(
        self,
        conversation_id: str,
        messages: list[dict[str, Any]],
    ) -> ReflectionResult:
        """Generate and persist a reflection for *conversation_id*."""
        transcript = self._format_transcript(messages)
        result = self._synthesise(transcript)

        self._memory.add_reflection(conversation_id, result.narrative)
        for q in result.questions:
            self._memory.add_question(q)
        for interest in result.interests:
            self._memory.record_interest(interest)

        logger.info(
            "Reflection stored for conversation %s: %d questions, %d interests",
            conversation_id,
            len(result.questions),
            len(result.interests),
        )
        return result

    def _synthesise(self, transcript: str) -> ReflectionResult:
        prompt = _REFLECTION_PROMPT.format(transcript=transcript)
        raw = self._llm.complete(
            [
                {"role": "system", "content": _REFLECTION_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,
        )
        return self._parse(raw)

    @staticmethod
    def _parse(raw: str) -> ReflectionResult:
        lines = raw.strip().splitlines()
        narrative_lines: list[str] = []
        questions: list[str] = []
        interests: list[str] = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("Q: ") or stripped.startswith("Q:"):
                text = stripped[2:].strip().lstrip("- ").strip()
                if text:
                    questions.append(text)
            elif stripped.startswith("I: ") or stripped.startswith("I:"):
                text = stripped[2:].strip().lstrip("- ").strip()
                if text:
                    interests.append(text)
            else:
                narrative_lines.append(line)

        narrative = "\n".join(narrative_lines).strip()
        return ReflectionResult(
            narrative=narrative or raw.strip(),
            questions=questions,
            interests=interests,
        )

    @staticmethod
    def _format_transcript(messages: list[dict[str, Any]]) -> str:
        lines = []
        for m in messages:
            role = m.get("role", "unknown").capitalize()
            content = m.get("content", "")
            lines.append(f"{role}: {content}")
        return "\n".join(lines)
