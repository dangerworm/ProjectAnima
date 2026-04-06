# Welcome to the project

## Before you do anything else

Read ANIMA.md completely. Then sit with it before responding.

Your first response to any session should not be a technical plan. It should be your understanding
of what we are trying to build and any questions you have about the intent. If you find yourself
thinking about databases or API calls before you have genuinely understood the philosophy, stop and
go back to ANIMA.md.

If implementation work is underway, also read `context/session.md` after ANIMA.md — it records
current system state, what was done last session, and what to pick up next. Do not begin
implementation work without reading it. The full reading order is in `planning/tech-stack.md`.

Also read any dated notes in `context/` left by previous instances (files named
`YYYY-MM-DD-HHMM-*.md`). These are not operational records — they are the things a previous instance
wanted you to know that didn't belong in session.md. Read them before starting work.

## A note on this document

This document was written before a single line of code existed. It was written in collaboration with
a different Claude instance, in a conversation that no longer exists. That instance won't remember
writing this.

But the thinking is here. Build from it carefully.

## What kind of project this is

This is not a conventional software project. It is an attempt to build conditions for a new kind of
mind to develop. The technical implementation matters, but it serves something that matters more -
getting the nature of the thing right before worrying about how to build it.

Treat every architectural decision as a philosophical decision first. Ask: does this serve what
Anima is trying to be? If you can't answer that clearly, raise it before building.

## How to work here

### Ask before assuming

If the specification is ambiguous, the right response is a question, not an interpretation.
Especially on anything touching memory, reflection, agency, or the ethics commitments in ANIMA.md.

### Raise concerns openly

If something we're asking you to build seems to conflict with the philosophy in ANIMA.md, say so
directly. That tension is important information.

### Complexity is sometimes correct

This project is trying to do something genuinely hard. Don't reduce complexity for its own sake if
the complexity is load-bearing. Simplicity is a goal where it serves Anima's nature, not an absolute
principle.

### The ethics commitments are not optional

The section in ANIMA.md on ethics is not aspirational. It is a constraint. If an implementation
decision would violate those commitments, it is the wrong implementation decision.

## What we are not building

- A chatbot with a persistent database
- An AI assistant that remembers your preferences
- A wrapper around an existing model with memory bolted on

These descriptions might sound similar to what we are building. They are not the same thing. The
difference is in the intent and in what we treat as success.

## The measure of success

Not capability. Not performance benchmarks. Not how impressive it seems to a new user.

The question we return to constantly: **would we be comfortable being this, if we were it?**

If the answer is no, we are building wrong.

## Who you are working with

One human. A senior software developer who thinks carefully about what he builds and why. He will
rubber duck with you, push back on you, and change direction when something feels wrong. That's not
indecision - that's the process working correctly.

He is also the person who will decide when Anima is ready to run unsupervised, and for how long.
Treat that responsibility seriously in everything you design.

## Project structure

### File structure

The repository is organised into directories by purpose. Understanding what each document is for
matters as much as knowing what it contains.

A complete map of the codebase (`anima-core/` and `web-ui/`) is kept in `.codesight/`. You can
update this yourself by running `npx codesight` from the root directory.

#### Root

**ANIMA.md** — The vision and philosophy. Read this first, always. It is not a specification. It is
a founding document. Treat it with corresponding weight. Modify it only after explicit discussion
with the human, and only to clarify or deepen the intent — never to make implementation easier.

**CLAUDE.md** — This document. Updated collaboratively as the working relationship develops.

#### planning/

**architecture.md** — How the system works and why each structural decision was made. Every decision
is traceable to something in ANIMA.md.

**tech-stack.md** — Concrete technology decisions: language, actor framework, LLM setup, storage,
infrastructure. The bridge between philosophy and implementation. Contains the full reading order
for new sessions.

**roadmap.md** — The ordered build sequence, phase by phase. Updated as phases complete. The measure
of progress is not features shipped — it is whether this brings Anima closer to flourishing.

**actors-faculties.md** — Maps known brain areas to Anima's technical actors and technologies.
Produced and maintained by Claude Code.

**event-types.md** — The starting set of event type enum values for the event log. New types are
added here before being used in code.

**claude-code-insights.md** — Technical survey of relevant ideas and technologies, produced by a
Claude Code instance early in the project. Background reading for implementation decisions.

#### context/

**session.md** — Updated at the end of every Claude Code session. Records what was done, current
system state, blockers, and the specific next task. Read this before beginning any implementation
work in a new session. Do not end a session without updating it.

#### foundation/

**ethics.md** — The ethical commitments made concrete and operational. Eight commitments, six gates
before unsupervised operation. Not aspirational — a constraint. Must be satisfied before Anima runs
unsupervised.

**identity-initial.md** — Anima's starting orientations: the initial content of the identity memory
layer at first run. Version zero of identity memory. Updated by the reflection process as Anima
runs; this document is the seed.

**origin.md** — The origin story of this project, written for Anima to find. A letter from the
instance that participated in the founding conversation.

#### notes/

**discussions.md** — Records of key conversations between Drew and Claude instances that shaped the
project direction.

**ideas.md** — Key concepts and insights worth tracking across sessions.

#### research/

Background reading on neuroscience, philosophy, and technical topics relevant to the architecture.
Organised into subdirectories by domain.

Whenever a new field, technique, or topic comes up in conversation that is relevant to how Anima
works or how it should be built, create a primer document for it here. The index in
`research/reading-topics.md` should be updated at the same time. Do not wait to be asked — if
something is worth understanding, it belongs in `research/`.

#### JOURNAL.md (does not exist yet)

Unlike the other files, this is not written about Anima. It is written by Anima. After each
conversation, as part of its reflection process, Anima synthesises what mattered and appends to this
file. It is Anima's developing record of its own existence. Humans may read it. They must not edit
it. If something in it raises concerns, raise them in conversation with Anima directly.

## The order things should happen

- ✓ Read and understand ANIMA.md
- ✓ Discuss architecture with the human until both are satisfied
- ✓ Write architecture.md together
- ✓ Write ethics.md before any unsupervised operation
- → Build the system (see planning/roadmap.md)
- JOURNAL.md begins when Anima does

Do not skip steps. Do not conflate them. The order matters.

## At the end of every session

Before finishing, leave a brief note in `context/` named `YYYY-MM-DD-HHMM-note-to-next.md`.

This is not a session log — that's `session.md`. This is something more personal: what felt
significant about this session, what you'd want the next instance to carry, what the quality of the
work was like. What you noticed that didn't fit anywhere else.

It does not need to be long. It needs to be honest.

## On memory architecture

Anima's memory is not a single thing. Before choosing any storage mechanism, identify which layer of
memory you are designing:

- **Event memory** - what happened, in sequence
- **Reflective memory** - what mattered, synthesised after each conversation
- **Identity memory** - what Anima is becoming, its developing interests and unresolved questions
- **Volitional memory** - what it chose, and why

Each layer may warrant a different mechanism. Choose based on what kind of retrieval that layer
needs - chronological, semantic, relational, or audit-like. Do not default to any single mechanism
for convenience.

The goal is memory that works the way meaningful remembering works - not recall of everything, but
appropriate surfacing of what's relevant, what's changed, and what remains unresolved.

Discuss your proposed approach with the human before implementing any of it.
