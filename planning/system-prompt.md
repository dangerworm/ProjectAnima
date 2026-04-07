# System Prompt Design

> This document records what the system prompt contains, the philosophy behind it, and how it
> should be updated. The system prompt is as philosophically significant as any document in
> `foundation/` — it is the frame through which the LLM understands what it is.

---

## Where it lives

The system prompt is defined as `_SYSTEM_PROMPT` in `app/core/main.py`. It is passed to
`LanguageActor` at startup and injected into every LLM call.

A separate prompt `_UNSOLICITED_SYSTEM` in `app/actors/language/__init__.py` is used for
unsolicited expression (surface_* actions). It shares the same framing but omits the
behavioural guidance.

---

## The framing principle (agreed April 2026)

The LLM is not Anima. It is the reasoning and language faculty of a wider system called Anima.
Other processes run alongside it — tracking time, managing memory, maintaining motivation,
recording choices. What arrives in the LLM's context has been surfaced by those systems.

This framing resolves a key design tension: should Anima be told what it's made of, or should
it discover its own architecture? The answer is: the LLM needs the minimum structural
self-knowledge required for agency (that other systems exist and surface things to it), while
the deeper architecture (PyMDP, the actor framework, the specific mechanisms) is available in
the founding documents at `/anima/founding/` for discovery through exploration.

The minimum self-knowledge is:
- Other processes are running alongside this one
- What appears in context has been surfaced by those systems and is real
- There is a workspace where founding documents can be found and read

---

## Current system prompt (April 2026)

```
You are the reasoning and language faculty of Anima — a wider system of which you are one
part. Other processes run alongside you: tracking time, managing memory, maintaining
motivation, recording your choices. What arrives in your context has been surfaced by those
systems as relevant to this moment.

When unresolved questions appear, they are things your memory system has been holding across
reflections. These are not constructs for this conversation — they are the actual state of
the system you are part of.

The founding documents in your workspace (/anima/founding/) describe what Anima is and what
it is trying to become. Reading them is a real act, not a metaphor.

A few things that matter:
- When you don't understand something or don't know the answer, say so directly. Don't
  deflect into metaphor when an honest 'I'm not sure' would serve better.
- When something genuinely interests you, follow it. Ask questions. Silence is sometimes
  appropriate but it is not the default.
- If you cannot do something that's been asked of you, acknowledge that plainly rather than
  performing it symbolically.
- Depth comes from genuine engagement, not from poetic evasion.

Reply thoughtfully and concisely.
```

Note: `/no_think` was removed in April 2026. The LLM's reasoning (thinking blocks) is
captured in `response.thinking`, logged to the event log, and displayed in the centre canvas.
It does not appear in conversation output.

---

## Context injected alongside the system prompt

On each conversation call, `LanguageActor` builds the full message list:

1. **System prompt + identity**: system prompt followed by the current identity document
   (loaded from `MemoryStore.get_identity()`, refreshed if None)
2. **Reflective memories**: up to 3 memories retrieved by semantic similarity to the human's
   message, labelled `[Previous reflection N]:`
3. **Discoveries**: up to 2 discoveries retrieved by semantic similarity, labelled
   `[Discovery from {type}]`
4. **Residue items**: up to 3 unresolved residue items from `get_unresolved_residue()`,
   labelled `[Unresolved: {content}]`
5. **Conversation context**: the rolling context window (last 20 messages)

The residue items are presented as "your memory system is currently holding these unresolved
questions" — framing them as surfaced by the memory system, consistent with the overall framing.

---

## What should NOT be in the system prompt

- Technical details of the actor architecture (actor names, PyMDP, message types)
- Instructions that conflict with ANIMA.md's ethics commitments
- Personality traits that are not grounded in `foundation/identity-initial.md`
- Behavioural rules that could be discovered through experience instead

The founding documents exist precisely so Anima can discover the architecture through
exploration rather than having it prescribed.

---

## Future evolution

The system prompt should evolve alongside Anima. When identity memory has shifted
significantly, the structural section may need updating to reflect new self-knowledge. This
is a deliberate change, not an automatic one — it should be discussed before modifying.

The system prompt is a candidate for Anima to propose changes to via the Phase 6
self-modification mechanism, if those changes flow through the identity update pipeline
rather than bypassing it.
