# CRDTs (Conflict-free Replicated Data Types)

## The problem: distributed state that must stay consistent

If Anima ever runs as multiple instances — or if any part of its memory lives on multiple servers —
you face the fundamental tension of distributed systems: *consistency* vs *availability*.

The standard answer is locking: before writing, acquire a lock. This guarantees consistency but
means that if the lock-holder goes down, everything waits. It also requires coordination, which adds
latency.

**CRDTs** are a class of data structures that sidestep this tradeoff. They guarantee that any two
replicas of the same data structure, having received the same set of updates (in *any* order),
will converge to the same state. No coordination required. No locks. Eventual consistency guaranteed
by mathematical construction.

## How they work

A CRDT is designed so that every possible merge of two states produces a deterministic result, and
that result is the same regardless of the order in which updates were applied. This property is
called **commutativity** and **idempotency**.

The simplest example: a **G-Counter** (grow-only counter).

Each replica maintains its own count. When you query the total, you sum all replicas' counts. When
two replicas merge, the merged counter for each replica is the maximum of the two values.

```
Replica A: {A: 3, B: 1, C: 0}
Replica B: {A: 2, B: 2, C: 1}
Merged:    {A: 3, B: 2, C: 1}  (take max for each)
Total:     6
```

No matter what order A and B merge their states, they converge to the same result.

More useful types:

**OR-Set (Observed-Remove Set)**: A set you can add to and remove from. Additions are tagged with
unique identifiers. A remove removes specific tagged additions rather than the value itself. Two
replicas can safely add and remove without coordination.

**LWW-Register (Last-Write-Wins Register)**: A single value, where concurrent writes are resolved
by taking the one with the latest timestamp. Simple but requires synchronized clocks.

**Sequence CRDTs** (e.g., LSEQ, RGA): Ordered sequences where concurrent insertions at the same
position are resolved deterministically. This is how collaborative text editing works (Google Docs,
Figma) — multiple people editing the same document simultaneously, with CRDTs resolving conflicts
automatically.

## Why it matters for Anima

The immediate practical reason: if Anima's memory layers are stored in a distributed database, or
if you ever want to run multiple Anima instances (even for testing vs production), CRDTs ensure
that state stays consistent without requiring coordination.

But there's a more interesting reason. The identity memory layer — what Anima is becoming — needs
a specific property: it should be stable and consistent, never producing contradictory states due to
concurrent updates from different specialist systems. A CRDT-based identity store would allow the
temporal core, the reflection pipeline, and the motivation system to all update identity memory
simultaneously, with the guarantee that their updates will merge consistently.

The volitional record is another candidate. Multiple processes might be writing to it concurrently
(the perception system noting an engagement choice while the motivation system notes an inclination).
A CRDT log guarantees these concurrent writes produce a consistent, ordered record.

## State-based vs operation-based

There are two main approaches to CRDTs:

**State-based (CvRDT)**: Replicas periodically exchange their full state. The merge function
determines how to combine two states. Simple to reason about but potentially expensive if state is
large.

**Operation-based (CmRDT)**: Replicas exchange operations (the changes, not the whole state).
Operations must be commutative — applying op A then op B gives the same result as op B then op A.
More efficient but requires reliable delivery of operations.

## Limitations

CRDTs are not a universal solution. They work well for specific data structures with well-defined
merge semantics. Complex application logic — "apply this change only if that condition holds" — is
hard to express as a CRDT. CRDTs are also eventually consistent: replicas will converge, but they
may temporarily diverge. For some data (e.g., access control decisions) this is unacceptable.

## Where to go deeper

- **"A comprehensive study of Convergent and Commutative Replicated Data Types" by Shapiro et al.
  (2011)** — the foundational paper; free on arXiv; the first half is accessible
- **Martin Kleppmann's "Designing Data-Intensive Applications"** — Chapter 5 covers replication and
  consistency excellently; CRDTs appear in the context of collaborative editing
- **Automerge** — an open-source CRDT library for JSON documents; excellent for understanding the
  practical shape of CRDT-based state management

## Relationship to other topics

- [Actor Model](actor-model-and-process-calculi.md) — actors in distributed systems often use
  CRDTs to manage shared state without coordination
- [Event Sourcing](event-sourcing-and-cqrs.md) — event logs are naturally CRDT-compatible; two
  replicas of an append-only log can merge by taking the union of their events
