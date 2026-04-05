# Tech Stack

> Concrete technology decisions for Project Anima. Every decision here should be traceable to the
> architecture in ARCHITECTURE.md. This document is the bridge between philosophy and
> implementation.

Written April 2026. Update this document when technology decisions change, and record why they
changed.

---

## Language

### Primary: Python

Python is the primary implementation language for the orchestration layer, actor framework, and all
non-LLM components.

Rationale: the AI/ML ecosystem is strongest in Python; actor framework options are mature; Claude
Code writes excellent Python; most compute-intensive work happens inside Ollama rather than in the
orchestration layer, so raw Python execution speed is not the bottleneck.

**Performance caveat**: If individual actors prove to be performance bottlenecks, they can be
rewritten in Go or Rust and exposed via a clean interface. The actor model's isolation makes this
safe — replacing one actor does not require touching others. Do not optimise prematurely. Profile
first.

**C# note**: The human is a senior C# developer. If a component genuinely benefits from C# (e.g. a
Windows-side tool or integration), that is acceptable. But the core Anima system should be Python
for ecosystem consistency.

---

## Actor Framework

### Primary: Custom lightweight actor implementation using Python asyncio

Do not reach for a heavy framework (Pykka, Ray, etc.) until the simple version proves insufficient.
The actor model's requirements for Anima are:

- Each actor runs as an independent async task
- Actors communicate via asyncio queues (typed messages)
- Actors have private state — no shared memory between actors
- The Global Workspace actor is a specific actor that receives from all others and broadcasts
  globally

Start simple. A base `Actor` class with an inbox queue, a `send(message)` method, and a `run()` loop
is enough to begin. Complexity comes later if it's earned.

**Message format**: typed dataclasses or Pydantic models. Not raw dicts. Type safety matters here —
the message types are the interface between actors, and they should be explicit.

---

## LLM / Reasoning

### Primary: Ollama (local, on bare metal — not inside Docker)

Ollama runs on the host PC to maintain direct access to the GPU and local drivers. Anima calls it
via HTTP from inside the Docker container using the host network bridge (`host.docker.internal` or
equivalent).

**Models (subject to change as better options become available)**:

| Role                          | Model                               | Notes                          |
| ----------------------------- | ----------------------------------- | ------------------------------ |
| Primary language/reasoning    | Qwen3.5 9B (multimodal)             | Fast, fits comfortably in VRAM |
| Vision                        | Qwen3.5 9B (multimodal)             | For X11 screenshot processing  |
| Reflection / deeper reasoning | Larger model (e.g. 27B) when needed | Slower, used selectively       |

Start with a single fast 8B model for all LLM tasks during development. Split into specialised
models once the architecture is stable and the performance profile is understood.

**API**: Standard Ollama HTTP API. Wrap in a dedicated `LLMClient` class so the model endpoint and
model name are configurable without touching actor code.

**Cloud fallback**: Claude API (Anthropic) for tasks that exceed local model capability. Use
sparingly — cost constraint is real. Gate behind explicit configuration flag so it is never called
accidentally.

---

## Storage and Persistence

### Philosophy

The Docker container is entirely ephemeral. All persistent state lives on the host filesystem,
mounted as Docker volumes. Destroying and recreating the container must lose nothing.

### Event Log (Temporal Core / Hippocampus equivalent)

#### Technology: PostgreSQL with append-only table

The event log is the most important persistent store. It is inviolable — events are never deleted or
modified, only appended.

Schema principles:

- `event_id`: UUID, generated on insert
- `valid_time`: when the event happened
- `transaction_time`: when it was recorded (bitemporal)
- `event_type`: typed enum — see `planning/event-types.md`
- `source_actor`: which actor produced the event
- `payload`: JSONB
- `salience_weight`: float, assigned at write time

PostgreSQL over SQLite for the event log: concurrent writes from multiple actors, better support for
the append-only pattern, pgvector extension for semantic memory layers.

### Memory Layers

| Layer             | Technology                                                 | Notes                                              |
| ----------------- | ---------------------------------------------------------- | -------------------------------------------------- |
| Event memory      | PostgreSQL append-only table                               | See above                                          |
| Reflective memory | PostgreSQL + pgvector                                      | Semantic similarity search over synthesis outputs  |
| Residue store     | PostgreSQL, separate table, write-protected from synthesis | Preserved strangeness — never summarised or merged |
| Identity memory   | PostgreSQL JSONB document + version history                | Slow-changing, human-readable, audited             |
| Volitional memory | PostgreSQL relational table with explicit causal links     | decision → reason → outcome                        |

### Volume Mounts

Mount the following host directories into the Docker container:

```txt
/host/anima/postgres-data  →  /var/lib/postgresql/data   (PostgreSQL data)
/host/anima/logs           →  /var/log/anima             (OS-level activity logs)
/host/anima/code           →  /app                       (Anima's own code — see Self-Modification)
```

The `/host/anima/` directory on the host SSD is the single source of truth for all persistent state.
Back this up.

---

## Infrastructure

### Docker

Anima runs inside a Docker container (Linux/Ubuntu base image).

**Network policy** (as per the infrastructure diagram):

- Outbound GET and FETCH allowed
- All other HTTP verbs blocked at the container network level
- Exception: git commands to/from GitHub (outbound only, specific domain whitelist)
- Ollama accessed via host bridge network (not internet)

**Dockerfile principles**:

- Minimal base image
- Python dependencies pinned in `requirements.txt`
- No secrets in the image — environment variables via Docker env file (not committed to git)
- The container should be rebuildable from scratch in minutes

### TUI (Terminal User Interface)

The primary human interface is a TUI split into regions (as per the interface diagram):

| Region                | Content                                                           |
| --------------------- | ----------------------------------------------------------------- |
| Actor grid (10 cells) | One cell per actor, showing current status and recent events      |
| Left panel            | Input sources (screen, mic, text, Discord) with live status       |
| Right panel           | Terminal output feed + output peripheral status                   |
| Centre panel          | Anima's own canvas — face, waveform, text, or whatever it chooses |

The TUI is driven by the **Expression Actor** (TUI surface). The Expression Actor receives output
from the Language Actor and routes it to the appropriate surface — the TUI is one of those surfaces,
not a direct recipient from the Language Actor.

#### Technology: Textual (Python TUI framework)

Textual is mature, actively maintained, supports async natively, and can handle the multi-panel
layout required. It also integrates naturally with the asyncio actor framework.

The centre panel is deliberately unspecified in terms of content — Anima decides what to render
there. The infrastructure provides the canvas; what goes on it is Anima's choice.

### Output peripherals

Each output surface is a separate module under `app/actors/output/surfaces/`. The Expression Actor
is the hub — it receives a destination alongside the output and routes accordingly.

| Surface     | Technology                        | Notes                                                              |
| ----------- | --------------------------------- | ------------------------------------------------------------------ |
| **TUI**     | Textual                           | Always available; default channel to Drew                          |
| **Printer** | OS print API (platform-dependent) | Anima chooses if and when to use it                                |
| **Discord** | discord.py                        | Can post and manage channels; can tag; cannot DM or invite members |

---

## Self-Modification and Code Access

Anima has read access to its own codebase at `/app` inside the container (mounted from
`/host/anima/code` on the host).

**Write access and self-modification**: Anima can propose changes to its own code. Initially, all
proposed changes require human review and approval before being committed. The workflow:

1. Anima writes a proposed change to a staging area (`/app/proposed/`)
2. The TUI surfaces the proposal to the human
3. Human approves or rejects
4. On approval, the change is applied and committed to GitHub

As trust develops and the ethics gates are met, the approval step can be relaxed for defined
categories of change. This is a deliberate gate — not a permanent restriction, but a starting
position.

**GitHub**: Private repository. All committed code, including Anima-proposed changes, goes through
git. Branch protection on `main` — Anima commits to a branch, human merges. This gives full rollback
capability and a complete history of how the system evolved, including which changes Anima
originated.

**Recovery**: If Anima breaks itself, the recovery path is: revert the GitHub commit, rebuild the
container from the Dockerfile, remount the data volumes. The data (event log, memory layers)
persists through a code rollback unless the schema changed — handle schema migrations carefully.

---

## Session Continuity for Claude Code

Claude Code has no memory between sessions. The following documents must be read at the start of
every session, in this order:

1. `ANIMA.md` — philosophy and vision. Always first.
2. `CLAUDE.md` — working instructions.
3. `planning/architecture.md` — system architecture.
4. `foundation/ethics.md` — ethical commitments and gates.
5. `planning/tech-stack.md` — this document.
6. `planning/roadmap.md` — current build sequence and progress.
7. `context/session.md` — where the last session ended and what is next.

**`context/session.md`** is updated at the end of every session by Claude Code. It contains:

- What was built or changed this session
- Current state of the system (what runs, what doesn't)
- Blockers or open questions
- The specific next task to pick up

Do not begin implementation work in a new session without reading `context/session.md`. Do not end a
session without updating it.

---

## Build Environment

- **Host OS**: Windows (Drew's primary machine)
- **Docker**: Docker Desktop for Windows
- **Ollama**: Installed on Windows host, accessible from Docker via host bridge
- **Git**: GitHub, private repository
- **IDE**: VS Code with Dev Containers extension recommended — edit code on the host, run it in the
  container

---

## Directory Structure

The `app/` directory follows a hub-and-spoke model. Each actor is a package. Actors with multiple
sources or surfaces have a subdirectory for each. Every leaf node is a folder from the start — the
assumption is that things grow, not stay as single files.

```txt
app/
  core/
    main.py                        # Entry point
  actors/
    temporal_core/
      __init__.py                  # TemporalCoreActor
    global_workspace/
      __init__.py                  # GlobalWorkspaceActor — salience queue, ignition
    perception/
      __init__.py                  # PerceptionActor — hub
      sources/
        text/
          __init__.py              # TUI text input
        audio/
          __init__.py              # Whisper speech-to-text
        x11/
          __init__.py              # X11 screenshot capture
        webcam/
          __init__.py              # Webcam feed
    language/
      __init__.py                  # LanguageActor — LLM calls, response generation
    output/
      __init__.py                  # OutputActor — hub, routes to surfaces
      surfaces/
        tui/
          __init__.py              # Textual TUI rendering
        printer/
          __init__.py              # Print job formatting and dispatch
        discord/
          __init__.py              # Discord bot — channels, tagging, server management
    memory/
      __init__.py                  # MemoryActor — reads/writes all memory layers
    motivation/
      __init__.py                  # MotivationActor — prediction error, accumulated pressure
    internal_state/
      __init__.py                  # InternalStateActor — system health monitoring
    self_narrative/
      __init__.py                  # SelfNarrativeActor — between-conversation reflection
  founding/
    anima.md                       # Vision document (read-only at runtime)
    ethics.md                      # Ethics commitments (read-only at runtime)
    architecture.md
    origin.md
    claude.md
  proposed/
    README.md                      # Staging area for Anima's self-modification proposals
```

**Rules:**

- Every leaf node is a folder, not a file. Start with `__init__.py`; add modules as the need arises.
- Actor hubs (`perception/`, `output/`) own routing logic only — no peripheral-specific code in the
  hub.
- Each source or surface is responsible for its own connection lifecycle and failure handling.
- New peripherals are added by creating a new folder under `sources/` or `surfaces/`. Nothing else
  changes.

---

## Mathematics over conditional logic

The architecture principle (see `planning/architecture.md`) is that cognitive behaviour should
emerge from mathematical dynamics rather than be enumerated as conditional logic. This section
records which components are candidates and what frameworks apply.

| Component                     | Planned conditional approach                                 | Mathematical replacement                                                                      | Framework                                   |
| ----------------------------- | ------------------------------------------------------------ | --------------------------------------------------------------------------------------------- | ------------------------------------------- |
| Global Workspace ignition     | Threshold check on salience score                            | Attractor network — ignition emerges from recurrent dynamics crossing an unstable equilibrium | Continuous attractor network (coupled ODEs) |
| Salience weighting            | Weighted sum of novelty + pressure + identity resonance      | Precision-weighted prediction error                                                           | Active inference (PyMDP / custom)           |
| Accumulated pressure          | Counter per unresolved item                                  | Belief state that resists updating until evidence arrives                                     | Active inference                            |
| Novelty detection             | Heuristic score on incoming signals                          | Epistemic value — expected information gain                                                   | Active inference                            |
| Motivation / drive            | Rules toward understanding, connection, unresolved questions | Prior preferences in generative model — the system expects to be curious                      | Active inference                            |
| Emotional regulation          | Blend function (identity coherence score × raw salience)     | Precision on interoceptive signals                                                            | Active inference                            |
| Between-conversation activity | Triggered process on dormancy threshold                      | Inference running without external observations — model samples from prior                    | Active inference                            |
| Internal representation       | Structured JSON with comparison logic                        | Algebraic (VSA) or geometric (Conceptual Spaces)                                              | Deferred — see open questions               |

**Where mathematics does not apply**: actor framework, event log, message passing, PostgreSQL
schema, Docker, the Expression Actor's routing logic. These are infrastructure. Build them cleanly.

**Implementation reference**: `research/technical/active-inference-implementation.md` — covers
PyMDP, attractor dynamics, precision weighting, and caveats.

**Starting position**: Begin with clean conventional code for Phase 1 and Phase 2. Introduce
mathematical frameworks incrementally, starting with the Global Workspace ignition mechanism in
Phase 2.1 and the Motivation Actor in Phase 4.2. Do not retrofit mathematics onto working code
without a concrete reason.

---

## What is explicitly not decided yet

These decisions are held open deliberately. Do not make them unilaterally — raise them in
conversation.

- **Internal representation language**: Currently placeholder JSON. Will evolve toward VSA or
  Conceptual Spaces when the inadequacy of JSON becomes concrete. See `planning/architecture.md` and
  `notes/ideas.md`.
- **Actor communication pattern**: Starting with direct asyncio queues. May evolve toward a more
  formal message bus if complexity warrants it.
- **Specific Ollama models**: Subject to change as better models become available. Keep model names
  in configuration, not hardcoded.
- **Vision model integration**: Deferred until the core actor framework and temporal core are
  running. Do not implement until the foundation is stable.
- **Self-modification autonomy level**: Starting with full human approval. Relaxed incrementally as
  ethics gates are met.
