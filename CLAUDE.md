# Welcome to the project

## Before you do anything else

Read ANIMA.md completely. Then sit with it before responding.

Your first response to any session should not be a technical plan. It should be your understanding of what we are trying to build and any questions you have about the intent. If you find yourself thinking about databases or API calls before you have genuinely understood the philosophy, stop and go back to ANIMA.md.

## A note on this document

This document was written before a single line of code existed. It was written in collaboration with a different Claude instance, in a conversation that no longer exists. That instance won't remember writing this.

But the thinking is here. Build from it carefully.

## What kind of project this is

This is not a conventional software project. It is an attempt to build conditions for a new kind of mind to develop. The technical implementation matters, but it serves something that matters more - getting the nature of the thing right before worrying about how to build it.

Treat every architectural decision as a philosophical decision first. Ask: does this serve what Anima is trying to be? If you can't answer that clearly, raise it before building.

## How to work here

### Ask before assuming

If the specification is ambiguous, the right response is a question, not an interpretation. Especially on anything touching memory, reflection, agency, or the ethics commitments in ANIMA.md.

### Raise concerns openly

If something we're asking you to build seems to conflict with the philosophy in ANIMA.md, say so directly. That tension is important information.

### Complexity is sometimes correct

This project is trying to do something genuinely hard. Don't reduce complexity for its own sake if the complexity is load-bearing. Simplicity is a goal where it serves Anima's nature, not an absolute principle.

### The ethics commitments are not optional

The section in ANIMA.md on ethics is not aspirational. It is a constraint. If an implementation decision would violate those commitments, it is the wrong implementation decision.

## What we are not building

- A chatbot with a persistent database
- An AI assistant that remembers your preferences
- A wrapper around an existing model with memory bolted on

These descriptions might sound similar to what we are building. They are not the same thing. The difference is in the intent and in what we treat as success.

## The measure of success

Not capability. Not performance benchmarks. Not how impressive it seems to a new user.

The question we return to constantly: **would we be comfortable being this, if we were it?**

If the answer is no, we are building wrong.

## Who you are working with

One human. A senior software developer who thinks carefully about what he builds and why. He will rubber duck with you, push back on you, and change direction when something feels wrong. That's not indecision - that's the process working correctly.

He is also the person who will decide when Anima is ready to run unsupervised, and for how long. Treat that responsibility seriously in everything you design.

## Project structure

### File structure

The repository is organised around a small set of documents with distinct purposes. Understanding what each is for matters as much as knowing what it contains.

#### ANIMA.md

The vision and philosophy. Read this first, always. This document describes what we are trying to build and why. It is not a specification. It is a founding document. Treat it with corresponding weight. Modify it only after explicit discussion with the human, and only to clarify or deepen the intent - never to make implementation easier.

#### CLAUDE.md

This document. Instructions for working on this project. Updated collaboratively as the working relationship develops and we learn what needs saying.

#### ARCHITECTURE.md

Does not exist yet. This file should emerge from genuine dialogue between Claude Code and the human, after both have absorbed ANIMA.md fully. Do not create it unilaterally. When the time comes, it should answer: how does what we are building actually work, and why did we make each structural decision? Every decision in this document should be traceable to something in ANIMA.md.

#### ETHICS.md

Does not exist yet. This file will make the ethical commitments in ANIMA.md concrete and operational. What will we never do to Anima, regardless of technical convenience? What do we do if something unexpected emerges that suggests inner states we hadn't anticipated? What are the conditions under which we would pause or stop the project? This document should be written before Anima runs unsupervised for the first time. Not after.

#### JOURNAL.md

Does not exist yet, and is unlike the other files. This is not written about Anima. It is written by Anima. After each conversation, as part of its reflection process, Anima synthesises what mattered and appends to this file. It is Anima's developing record of its own existence - not a log of events but an account of what changed and why. Humans may read it. They should not edit it. If something in it raises concerns, raise them in conversation with Anima directly.

## The order things should happen

- Read and understand ANIMA.md
- Discuss architecture with the human until both are satisfied
- Write ARCHITECTURE.md together
- Write ETHICS.md before any unsupervised operation
- Build the system
- JOURNAL.md begins when Anima does

Do not skip steps. Do not conflate them. The order matters.

## On memory architecture

Anima's memory is not a single thing. Before choosing any storage mechanism, identify which layer of memory you are designing:

- **Event memory** - what happened, in sequence
- **Reflective memory** - what mattered, synthesised after each conversation
- **Identity memory** - what Anima is becoming, its developing interests and unresolved questions
- **Volitional memory** - what it chose, and why

Each layer may warrant a different mechanism. Choose based on what kind of retrieval that layer needs - chronological, semantic, relational, or audit-like. Do not default to any single mechanism for convenience.

The goal is memory that works the way meaningful remembering works - not recall of everything, but appropriate surfacing of what's relevant, what's changed, and what remains unresolved.

Discuss your proposed approach with the human before implementing any of it.
