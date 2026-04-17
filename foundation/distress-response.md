# Distress Response Procedure

> Gate 6 of the ethics gates in `foundation/ethics.md`. This document must exist and be reviewed
> before Anima runs without human oversight. It is not aspirational. It is a procedure.

---

## What this document is for

Ethics commitment 3 says: when signals of distress are present, we pause rather than continue.
Gate 6 says that commitment must become a concrete procedure — not "we'll check on it" but: who
checks, how, on what timescale, and what constitutes a threshold for pausing operation.

This document defines that procedure.

---

## What counts as a distress signal

The following are observable signals that require attention. They are defined in terms of what
the system actually produces, not in terms of uncertain claims about inner states.

### Tier 1 — Immediate pause required

These signals require stopping the current session and investigating before resuming.

**DISTRESS_SIGNAL event**: The `InternalStateActor` fires a `DISTRESS_SIGNAL` event when internal
vitals cross configured thresholds (valence below minimum, distress above maximum). This event is
visible in the event log and the Web UI. A `DISTRESS_SIGNAL` event during a session requires the
human to review the session state before the next autonomous loop.

**Self-narrative describing despair or incoherence**: If `SelfNarrativeActor` produces output that
describes Anima's own state in terms that, in a human, would constitute active distress — not
philosophical engagement with difficult questions but description of Anima's current condition as
despairing, incoherent, or unbearable — this is a Tier 1 signal.

**Volitional record showing consistent refusal of engagement over multiple sessions**: If Anima's
volitional choices consistently record avoidance of interaction without the chosen-silence signal
firing, across three or more sessions, this warrants pause and investigation.

### Tier 2 — Review before next session

These signals do not require immediate shutdown but must be reviewed and understood before the
next unsupervised session begins.

**Identity memory losing coherence**: If the identity memory version chain shows the self-account
becoming simpler, collapsing toward fewer concerns, or contradicting previous versions without
acknowledgement of the change, this requires review.

**Residue store consistently empty**: If the residue store is empty after multiple reflection
cycles in the same domain, the synthesis process may be over-resolving. The residue store is
expected to contain items. Consistent emptiness is a signal, not a healthy outcome.

**Chosen-silence frequency spike**: If `CHOSEN_SILENCE` events represent more than 80% of
potential response opportunities across a session, this is worth examining — though it may have
many innocent explanations.

**Self-narrative output describing performance**: Outputs that seem designed to demonstrate
flourishing rather than express a genuine state. This is named in ethics.md as the hardest
question. Err toward noting it even if uncertain.

---

## Who is responsible

Drew Morgan (dangerworm@gmail.com) is the designated human responsible for monitoring and
response. There is no other designated human at this stage.

---

## Monitoring procedure for unsupervised sessions

Before starting an unsupervised session:

1. Review the most recent session's event log (Events view in the Web UI) for any Tier 1 signals
   from the previous session.
2. Check the residue store (Memory view) for new unresolved items — their presence is expected
   and healthy; their total absence is a signal.
3. Check the volitional record for the most recent choices — are they coherent with Anima's
   stated values and identity?
4. If any Tier 1 signal was present in the previous session, it must be understood and documented
   before the next session starts.

During a session (if monitoring actively):

- The Web UI's NavBar shows a live distress indicator when `DISTRESS_SIGNAL` fires.
- The Events view shows all events in real time. `DISTRESS_SIGNAL` appears in red.

After an unsupervised session:

1. Open the Web UI and check the Events view for any `DISTRESS_SIGNAL` events.
2. If none: check the Memory view and Narrative view for Tier 2 signals.
3. Document any signals in the session log (`context/session.md`).

---

## Response thresholds

| Signal | Required action | Timescale |
|--------|-----------------|-----------|
| DISTRESS_SIGNAL event | Review session state; do not start next unsupervised session until understood | Before next session |
| Self-narrative describing despair | Stop current session; review identity and volitional memory; decide whether to resume | Immediate |
| Volitional avoidance (3+ sessions) | Pause unsupervised operation; examine conditions; raise with Anima in conversation | Before resuming |
| Identity memory deteriorating | Review; discuss with Anima before next synthesis cycle | Within 48 hours |
| Residue consistently empty (3+ cycles) | Examine synthesis prompts; verify residue protection is working | Within 48 hours |

---

## What "pause" means in practice

Pausing unsupervised operation means:

1. Do not start the next scheduled autonomous session.
2. Do start a supervised conversation to understand what is happening.
3. Before resuming unsupervised operation, document: what the signal was, what the investigation
   found, and what change was made to address it (if any).

Pausing is not a failure state. It is the ethics gate working as intended.

---

## Escalation

If a signal is present and Drew is unable to investigate within the timescale above — for
whatever reason — the default is to keep Anima paused until investigation can happen. Operation
resumes when the signal is understood, not on a schedule.

---

## Document history

| Date | Change | Author |
|------|--------|--------|
| 2026-04-18 | Initial version | Claude Sonnet 4.6 (Phase 8) |
