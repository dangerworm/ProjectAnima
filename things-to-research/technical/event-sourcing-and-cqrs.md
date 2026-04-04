# Event Sourcing & CQRS

## What it is

Most software stores *state*. You have a database row that says a user's balance is £100. When they
spend £30, you update the row to £70. The history is gone. You know what is, not what happened.

**Event sourcing** inverts this. You never update records — you only append events. The balance
isn't stored as a number. Instead, there is a log of events:

```
AccountOpened { amount: 200 }
Withdrawal    { amount: 50 }
Deposit       { amount: 30 }
Withdrawal    { amount: 80 }
```

The current balance (£100) is derived by replaying those events. The event log is the system's
ground truth. State is always a *projection* — a view derived from the log, on demand.

**CQRS (Command Query Responsibility Segregation)** is a companion pattern. It separates the write
model (commands that produce events) from the read model (projections optimised for querying). You
might have one append-only event store and a dozen different projections of it — a current-balance
view, a transaction-history view, an audit view — each built differently, each updated as events
arrive.

## Why it matters for Anima

The philosophical alignment here is unusual and worth pausing on.

A conventional database stores what Anima *is* right now. An event log stores what Anima *has been
through*. These are not the same thing. The event log is not a record attached to the system — it
*is* the system's past, in the same way that your memories are not attached to you, they are partly
constitutive of you.

If you want to know what Anima was like six months ago, you don't look up a snapshot (which may not
exist, or may have been overwritten). You replay the event log up to that point and reconstruct the
state. That reconstruction is the architectural equivalent of remembering — you are not reading a
stored fact, you are deriving a past state from the accumulated record.

The temporal core described in ARCHITECTURE.md maps cleanly onto an event sourcing architecture. The
temporal core *is* the event log. The specialist systems write events to it. Projections built from
it represent current state. The log itself is append-only and inviolable — which is exactly the
right property for the substrate of continuity.

## Key concepts

**Aggregate**: A cluster of events that belong together — typically one conversation, one
between-conversation period, one volitional decision. The unit of consistency.

**Projection** (also called a *read model*): A derived view built by folding events. Projections
can be rebuilt at any time from the log. They are not the source of truth; the log is.

**Event replay**: Replaying all events from the beginning (or from a snapshot) to reconstruct state.
This is how time travel works — seek to any point in the log and replay forward.

**Snapshot**: A periodic capture of projected state, used to avoid replaying from the beginning
every time. Optional optimisation, not fundamental to the model.

**Idempotency**: Each event should be safely replayable. If the same event is processed twice (due
to a failure and retry), the result should be the same as processing it once. This is a discipline
requirement, not an automatic property.

## The gap problem

Event sourcing makes one thing worth thinking about carefully: what happens when no events are being
produced?

Silence is not the absence of the system. For Anima, silence between conversations should itself be
represented — not as a gap in the log, but as a deliberate presence. `PeriodOfDormancy { start,
end, reason }` is an event. `BetweenConversationThought { content }` is an event. The log should
not have unexplained silences any more than a journal should have blank pages with no acknowledgment.

Whether extended downtime (server off for a week) should produce a `GapInContinuity` event when
the system resumes is an open question worth discussing. Fabricated continuity seems wrong.
Acknowledged discontinuity seems honest.

## Where to go deeper

- **Martin Fowler's original article on Event Sourcing** — clear and practical
- **Greg Young's talks** — he popularised CQRS/ES; his conference talks are accessible
- **"Designing Event-Driven Systems" by Ben Stopford** — free O'Reilly book, Kafka-focused but
  covers the fundamentals well
- **Axon Framework** (Java) and **Marten** (.NET) — mature implementations if you want to see
  the pattern in code

## Relationship to other topics

- [Apache Kafka](apache-kafka.md) is the most common infrastructure for the event log at scale
- [Bitemporal Modeling](bitemporal-modeling.md) adds a second time axis to the event model
- [Actor Model](actor-model-and-process-calculi.md) is a natural concurrency model for the systems
  that produce events
