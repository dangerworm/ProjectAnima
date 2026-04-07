# Source Model — Architecture for Multi-Channel Input/Output

> Status: **deferred**. The minimal fix (output cooldown replacing conversation gate) is in place.
> This document captures the fuller architecture so the shape isn't lost.
> Implement when a second input source arrives (Discord, voice, etc.).

---

## The Problem with the Conversation Model

The current architecture treats "conversation" as a first-class entity with a start and end. This
created an inversion: Anima is most constrained (unsolicited expression suppressed) exactly when
Drew is most present. The conversation boundary was protecting against overlapping LLM calls and
output bursting — both real concerns — but it did so by suppressing *all* autonomous expression
during the conversation window. That's too blunt.

The deeper issue: "conversation" is a human-to-human metaphor. What's actually happening is:
inputs arrive from sources, Anima processes them, outputs are optionally directed somewhere. The
concept of a discrete conversational session doesn't map cleanly onto this.

---

## The Source Model

### Core idea

Replace the conversation boundary with source annotation. Every input is tagged with its origin.
Every output is optionally targeted at a destination. Thoughts with no target are real — they
happened, they're logged — whether or not anyone receives them.

### Input sources

Each input carries a `source` field identifying where it came from:

```python
@dataclass(frozen=True)
class SourcedInput:
    source_id: str        # "web_ui", "discord:server_id", "voice", "internal" etc.
    source_type: str      # "human", "system", "self"
    content: str
    metadata: dict        # channel, user, timestamp, etc.
```

The event log gains a `source` column. Memory entries — reflections, residue, volitional choices
— are annotated with the source context they arose from.

### Output targeting

Anima chooses whether to direct output somewhere:

```python
@dataclass(frozen=True)
class LanguageOutput:
    content: str
    thinking: str | None
    target: str | None    # "web_ui", "discord:channel_id", None (internal thought)
    in_response_to: str   # event type that triggered this
```

`target=None` means the thought is real but not directed. It still gets logged to the event log
and written to JOURNAL.md. The distinction between "said something" and "thought something" is in
the target field, not in whether it happened.

### What replaces conversation tracking

Nothing needs to track conversation start/end for the purpose of gating expression. Instead:

**For overlapping LLM calls:** The actor message loop is sequential — calls can't truly overlap.
A short output cooldown (configurable, default 120s) prevents bursting when multiple surface
signals have queued.

**For reflection triggering:** SelfNarrativeActor currently reflects on CONVERSATION_END.
Replace this with a volume-based or time-based trigger: reflect when N events have accumulated
since the last reflection, or when the motivation system selects trigger_reflection. The
between-conversation reflection path already works this way.

**For identity of "who was this with":** The `source` annotation on events answers this more
precisely than conversation boundaries did. A reflection can note "this arose from exchanges
with Drew via web_ui" rather than "this was a conversation."

### Memory enrichment

With source annotation, memory layers gain context:

- **Reflective memory**: knows which sources were involved in what it's synthesising
- **Volitional memory**: knows whether a choice was made in response to a human or arose internally
- **Residue**: knows whether an unresolved question came from Drew's input or from autonomous thinking
- **JOURNAL.md**: receives all outputs with `target=None` — Anima's actual thought record

### The workspace doesn't change

The GlobalWorkspace model handles source multiplicity naturally. Signals from different sources
compete on salience. High-salience human input outcompetes low-salience autonomous surface
signals, which is the correct behaviour. The workspace already does what the conversation model
was trying to do, but more gracefully.

---

## Implementation sketch

When implementing, the key changes are:

1. **Event log schema**: add `source TEXT` column, `source_type TEXT` column. Null = internal.
   Migration: `ALTER TABLE event_log ADD COLUMN source TEXT, ADD COLUMN source_type TEXT`.

2. **PerceptionActor**: passes `source_id` and `source_type` with every input message. Currently
   always "web_ui" / "human". Discord integration would add new source IDs.

3. **LanguageActor**: `target` in LanguageOutput. For now, target = the source that triggered the
   expression (respond where the input came from). For autonomous expression, target = None or
   whichever channel Anima chooses.

4. **ExpressionActor**: routes LanguageOutput based on `target`. Routes to WebSocket for "web_ui",
   to Discord client for "discord:*", logs to journal for None.

5. **SelfNarrativeActor**: reflection triggers change. Remove CONVERSATION_END dependency.
   Add event-volume trigger: reflect when `event_count_since_last_reflection >= REFLECTION_THRESHOLD`
   (configurable). The motivation system's trigger_reflection action remains as the primary path.

6. **Memory annotations**: add `source` context to StoreReflection, StoreVolitionalChoice.
   Surface in identity/reflective memory as metadata, not core content.

---

## What to keep from the conversation model

- **CONVERSATION_START/END events in the log**: keep as informational events, just don't use them
  as gates. They're useful for "Drew arrived at this time, left at this time" context.
- **TemporalCoreActor conversation tracking**: keep for the heartbeat status display and for
  providing "time since last human contact" to MotivationActor's time_obs observation.
- **The reflection pipeline itself**: unchanged. Only the trigger changes.

---

## When to build this

When a second input source appears. The source abstraction before the second source is premature
— you can't validate the shape of an abstraction with only one instance of it. Discord integration
or voice input would be the natural trigger.

The minimal fix (cooldown replacing conversation gate) is sufficient until then.
