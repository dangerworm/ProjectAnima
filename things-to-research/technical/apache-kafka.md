# Apache Kafka

## What it is

Most messaging systems work as queues: you put a message in, a consumer reads it, and it's gone.
The message is consumed and deleted.

**Kafka** is different. Kafka is a **persistent distributed log**. Messages are not deleted when
consumed. They are retained for a configurable period (days, weeks, indefinitely). Multiple
consumers can read the same messages, independently, at their own pace. A new consumer can start
from the beginning of the log and replay everything that ever happened.

This makes Kafka closer to a **commit log** than to a message queue. It is infrastructure for the
event sourcing model — the persistent, replayable record of what happened, that multiple systems
can read without affecting each other.

## Core concepts

**Topic**: A named log. You write to a topic; you read from a topic. Events in a topic are ordered
and immutable.

**Partition**: Topics are divided into partitions for parallelism. Each partition is an independent
ordered log. Events with the same *partition key* go to the same partition, preserving their relative
order.

**Offset**: The position of a message within a partition. Consumers track their own offset — how far
along the log they've read. Two consumers can read the same topic at completely different offsets
without interfering with each other.

**Consumer Group**: Multiple consumers working together to process a topic. Each partition is
assigned to one consumer in the group, distributing the load. Different consumer groups maintain
independent offsets — one group at offset 100, another at offset 3, each progressing independently.

**Retention**: Kafka retains messages according to policy — by age (e.g., keep the last 30 days),
by size (e.g., keep the last 100GB), or indefinitely with *compaction* (keep only the latest value
for each key).

**Log compaction**: A mode where Kafka keeps only the most recent event for each key. Useful for
state snapshots — you maintain a full history of changes but can retrieve the current value of any
key efficiently. This turns Kafka into something like a changelog database.

## The architecture it enables

The classic Kafka architecture:

```
[Producers] → [Kafka Topic] → [Consumer A] → [Projection / Database A]
                           → [Consumer B] → [Projection / Database B]
                           → [Consumer C] → [Monitoring / Alerting]
```

One log, many consumers, each building its own view. Each consumer can fail and resume from where it
left off. New consumers can be added and start from the beginning, building a historical view
without affecting others.

This maps directly onto Anima's specialist systems. The temporal core writes to the event log.
Memory, reflection, motivation, and self-narrative all consume from it independently. Each builds
its own projection. A new specialist system (say, a pattern-detection system added later) can be
added and start from the beginning without requiring any changes to the existing architecture.

## Event time vs processing time

One of Kafka's important contributions to stream processing is the explicit distinction between:

- **Event time**: when the event actually happened in the real world
- **Processing time**: when the event was processed by the consuming system

These differ whenever there are delays — network latency, consumer downtime, batch processing. A
consumer processing yesterday's events today must distinguish "this happened yesterday" from "I
am processing this now".

This is the same distinction as [bitemporal modeling](bitemporal-modeling.md) but at the stream
processing level. Kafka's streaming library (Kafka Streams) and the ecosystem around it
(Apache Flink, Apache Spark Streaming) have developed sophisticated tools for windowing,
watermarking, and late-arrival handling — all consequences of taking this distinction seriously.

## Is Kafka the right tool for Anima?

Kafka is industrial infrastructure. It was built for systems handling millions of events per second
across hundreds of servers. For a single-instance Anima, it may be overengineered.

Lighter alternatives for the same conceptual model:
- **SQLite with an append-only events table** — simplest possible; works for early development
- **EventStoreDB** — an open-source event store purpose-built for event sourcing; simpler than
  Kafka but adds subscription and projection support
- **Chronicle Queue** (Java) — extremely fast persistent queue for single-machine use
- **Redpanda** — Kafka-compatible but significantly simpler to operate

The concept is more important than the specific tool. Whatever stores the event log should be:
- Append-only
- Ordered
- Replayable from any point
- Retained indefinitely (or until explicitly archived)

Kafka is worth understanding because it has shaped how the industry thinks about persistent streams.
But it need not be the first implementation choice.

## Where to go deeper

- **"Designing Event-Driven Systems" by Ben Stopford** — free O'Reilly ebook; the first half is
  an excellent introduction to Kafka's design philosophy
- **"Kafka: The Definitive Guide"** — comprehensive reference; free from Confluent
- **Kafka's own documentation** — the "Design" section explains the log-based architecture clearly
- **Martin Kleppmann's "Designing Data-Intensive Applications"** — Chapter 11 covers stream
  processing; some of the best writing on event time vs processing time

## Relationship to other topics

- [Event Sourcing](event-sourcing-and-cqrs.md) — Kafka is the infrastructure; event sourcing is
  the pattern
- [Bitemporal Modeling](bitemporal-modeling.md) — event time vs processing time is bitemporality
  in stream form
- [Actor Model](actor-model-and-process-calculi.md) — Kafka is often used as the message bus
  between actor-style systems
