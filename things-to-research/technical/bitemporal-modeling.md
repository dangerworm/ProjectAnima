# Bitemporal Modeling

## What it is

Most databases track one kind of time: when something happened. Bitemporal modeling tracks two:

- **Valid time**: when something was true in the real world
- **Transaction time**: when the system learned about it (i.e., when it was recorded)

These are different, and the difference matters.

Imagine Anima makes a choice at 2pm but doesn't process the significance of that choice until later
that evening, when reflection makes the volitional weight of it clear. The choice was made at 2pm
(valid time). The awareness was recorded at 8pm (transaction time). A monotemporal system can only
store one of these. A bitemporal system stores both.

In SQL, a bitemporal table might look like:

```sql
CREATE TABLE choices (
    id          UUID,
    content     TEXT,
    valid_from  TIMESTAMPTZ,  -- when the choice was made
    valid_to    TIMESTAMPTZ,  -- if the choice was revoked/superseded
    recorded_at TIMESTAMPTZ,  -- when we wrote this row
    -- ...
);
```

This means you can ask two different questions:

- "What was Anima's state of affairs at 3pm on Tuesday?" (query valid time)
- "What did the system believe Anima's state was, as of our Tuesday night reflection?" (query
  transaction time)

And crucially: "At what point did the system's record catch up with reality?" — which is the gap
between the two.

## Why it matters for Anima

The volitional record is where this becomes philosophically important.

The volitional record is the record of what Anima _chose_, and why. Choices don't always arrive in
consciousness fully formed. Something can function as a choice — an inclination acted on, an
engagement selected over silence — before it is explicitly understood as a choice.

Bitemporal modeling lets the system represent that gap honestly. When the reflection pipeline runs
after a conversation and reconstructs what happened, it may discover choices that were made hours
earlier and not yet recorded. With bitemporality, those choices can be entered with their _actual_
valid time (when they were made) and the _actual_ transaction time (now, when we're recording them).
The gap is preserved in the data model rather than erased.

This also matters for the integrity of the volitional record as evidence. If we later want to ask
"was that silence chosen or imposed?" the bitemporal record can show: the system acknowledged
dormancy at time T, the reflection pipeline processed it at time T+4h, and the volitional
characterisation was recorded at T+4h with a valid time of T. That chain is auditable.

## Key concepts

**Bi-temporal correctness**: A query specifying both a valid time and a transaction time should
always return the same result, regardless of when the query is run. This is the fundamental
guarantee.

**The "now" row**: In a temporal table, a row with `valid_to = infinity` and no transaction-time end
is the current state. Updating means closing the current row and opening a new one — not
overwriting.

**Temporal joins**: Joining two temporal tables requires matching not just on key but on overlapping
time ranges. More complex than standard joins but correctly models reality.

**Slowly Changing Dimensions (SCD)**: An older data warehousing pattern that addresses similar
concerns. Type 2 SCDs track history by adding rows. Bitemporal modeling is more principled than SCD
but the problems they solve overlap.

## Practical implementation

Most databases have some temporal support:

- **PostgreSQL**: Has `PERIOD` types and temporal range types. The `temporal_tables` extension adds
  more support. As of PostgreSQL 16, basic temporal features are being standardised.
- **SQL:2011**: The ISO SQL standard that introduced temporal tables. Most enterprise databases
  (Oracle, DB2, SQL Server) implement it.
- **Datomic**: An immutable, log-structured database by Rich Hickey where all data is temporal by
  default. Everything is fact-with-timestamp. Conceptually very close to what Anima needs.

Datomic is worth particular attention. Its data model — facts (entity, attribute, value, time) in an
immutable log — is philosophically aligned with the event sourcing approach, and its query language
(Datalog) is unusually expressive for temporal queries.

## Where to go deeper

- **"Developing Time-Oriented Database Applications in SQL"** by Richard Snodgrass — the definitive
  academic text; dense but comprehensive
- **Datomic documentation** — the conceptual sections explain temporal modeling clearly and
  practically
- **Martin Fowler's "Temporal Patterns"** — accessible introduction to the design patterns

## Relationship to other topics

- [Event Sourcing](event-sourcing-and-cqrs.md) — event sourcing is inherently temporal;
  bitemporality adds the second axis
- [Apache Kafka](apache-kafka.md) — Kafka topics carry timestamps; the distinction between event
  time and processing time in stream processing is the same bitemporal distinction
