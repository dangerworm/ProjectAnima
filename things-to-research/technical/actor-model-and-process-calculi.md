# Actor Model & Process Calculi

## The problem: concurrent systems that share state

Most concurrency bugs come from the same source: multiple processes accessing and modifying shared
memory simultaneously. One process reads a value, another modifies it before the first finishes, and
the result is inconsistent. The traditional solution is _locking_ — making processes queue up for
exclusive access. Locking is correct in theory and painful in practice: deadlocks, starvation, and
the sheer difficulty of reasoning about what needs to be locked when.

The Actor Model and Process Calculi are both attempts to build concurrency on a different
foundation, where shared mutable state is not the primitive.

---

## The Actor Model

**Carl Hewitt** proposed the Actor Model in 1973. The central idea: the fundamental unit of
computation is an _actor_ — an independent process that has:

- Private state (no other actor can read or write it directly)
- A mailbox (a queue of incoming messages)
- A behaviour (what it does when it processes a message)

Actors communicate _only_ by sending messages to each other's mailboxes. There is no shared memory,
no shared state, no locking. When an actor processes a message, it can:

- Send messages to other actors (including itself)
- Create new actors
- Update its own private state
- Decide how to handle the _next_ message (change behaviour)

That's it. Everything a concurrent system can do is built from those four operations.

### Why this is elegant

Because the isolation is total, there are no race conditions within a single actor — it processes
one message at a time. And because there is no shared state, two actors can't corrupt each other's
state, only communicate with each other.

Failure is also isolated. An actor that crashes doesn't corrupt other actors. You can build
_supervision trees_: one actor watches another, and when the watched actor crashes, the supervisor
restarts it. This is the basis of Erlang's legendary fault tolerance.

### Erlang and Elixir

Erlang was designed at Ericsson in the 1980s for telephone switching systems — systems that needed
to be running 24/7/365 with nine nines of availability, processing millions of concurrent
connections, and patching themselves without downtime.

The language is built around the Actor Model (called "processes" in Erlang). Key properties:

- Processes are extremely lightweight (thousands of bytes, not megabytes)
- You can run millions of concurrent processes on a single machine
- The VM supports hot code reloading — you can swap out a module while it's running
- The standard supervision pattern makes self-healing systems straightforward to build

**Elixir** is a more modern language that runs on the Erlang VM (the BEAM). It has a nicer syntax,
better tooling, and the Phoenix framework for web development. For a new project in 2026, Elixir is
probably the more practical choice.

### Why this matters for Anima

Anima's architecture consists of several specialist systems running in parallel: the temporal core,
perception, memory layers, motivation, self-narrative, and the global workspace. These systems must
run concurrently and communicate.

The Actor Model maps almost perfectly onto this architecture:

- Each specialist system is an actor
- The global workspace is an actor (or a small cluster of actors) that receives from all others
- Messages between systems are typed events
- Failures in one system don't cascade to others

In Python, `pykka` is a simple actor library. In the JVM ecosystem, Akka is the dominant
implementation. But the native actor model — Erlang/Elixir — has been living with these problems for
forty years and has solved many edge cases that newer implementations still struggle with.

---

## Process Calculi

Process calculi are the _formal_ foundations for reasoning about concurrent communicating systems.
Where the Actor Model is a programming model, process calculi are mathematical languages for
describing and proving properties of concurrent systems.

### CSP (Communicating Sequential Processes)

**Tony Hoare** (of Quicksort fame) published CSP in 1978. It describes concurrent processes as
_sequential processes that communicate over named channels_. The key operations:

- `c!v` — send value `v` on channel `c`
- `c?x` — receive a value from channel `c` and bind it to `x`
- `P || Q` — run processes P and Q in parallel
- `P ; Q` — run P, then Q
- `P [] Q` — non-deterministic choice between P and Q

CSP has a rich theory, including tools for proving that a system is deadlock-free, that two
descriptions of a system are equivalent, and that a system satisfies a specification.

**Go** was directly inspired by CSP. Go's channels and goroutines are a practical implementation of
Hoare's ideas.

### Pi-calculus

**Robin Milner** proposed the Pi-calculus in 1992 as an extension of CSP with one crucial addition:
_channels can be passed as values_. This means the _topology_ of a concurrent system — which
processes can talk to which — can change at runtime.

This matters for systems that need to be dynamic. In a fixed-topology system, you define once which
actors communicate with which. In Pi-calculus, an actor can receive a new channel and start
communicating with someone it had no prior connection to.

For Anima, this might matter: could the connections between specialist systems strengthen and weaken
dynamically, based on what co-activates? Pi-calculus provides the formal tools to reason about
systems where the communication structure itself evolves.

### Practical value

Most developers don't write Pi-calculus directly. Its value is:

1. **Formal verification**: You can prove properties of concurrent systems that would be impossible
   to verify by testing alone.
2. **Conceptual clarity**: Understanding process calculi makes you think more carefully about what
   _communication_ means — synchronous vs asynchronous, buffered vs unbuffered, directed vs
   broadcast.
3. **Influence on tools**: CSP influenced Go. The Actor Model influenced Erlang, Akka, and many
   others. Understanding the theory helps you use the tools well.

## Where to go deeper

- **"Programming Erlang" by Joe Armstrong** — practical introduction; Armstrong was one of Erlang's
  creators
- **"Elixir in Action" by Saša Jurić** — excellent practical book; the concurrency chapters are the
  best introduction to BEAM concurrency I've encountered
- **"Communicating Sequential Processes" by C.A.R. Hoare** — the original book; available free
  online; more approachable than expected
- **"A Calculus of Communicating Systems" by Robin Milner** — the formal foundation; dense

## Relationship to other topics

- [CRDTs](crdts.md) — CRDTs solve consistency in distributed actor systems; the two concerns often
  arise together
- [Apache Kafka](apache-kafka.md) — Kafka is often used as the message bus in actor-style systems at
  scale
