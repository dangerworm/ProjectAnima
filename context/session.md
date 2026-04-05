# Session Log

> Updated at the end of every Claude Code session. Read this before starting any implementation
> work. The most recent entry is at the top.

---

## Session: 5th April 2026 — Phase 1.1 complete

### What happened this session

Phase 1.1 (repository and environment setup) is complete.

**ProjectAnima reorganised:**

- Repository structure reorganised into `planning/`, `context/`, `foundation/`, `notes/`,
  `research/`
- `CLAUDE.md` updated to reflect new structure and reference `context/session.md`
- `planning/tech-stack.md`, `planning/roadmap.md`, `context/session.md` added

**AnimaCore created** at `https://github.com/dangerworm/AnimaCore.git`:

- `app/founding/`: anima.md, claude.md (with repository note prepended), ethics.md, origin.md,
  architecture.md
- `Dockerfile`: Python 3.12-slim, pip installs from requirements.txt
- `docker-compose.yml`: Anima service + PostgreSQL (pgvector/pgvector:pg16), named volumes, host
  bridge for Ollama
- `requirements.txt`: asyncpg, pydantic, textual, httpx, pgvector, python-dotenv
- `.env.example`, `.gitignore`
- `app/core/main.py`: placeholder entry point
- Added as git submodule of ProjectAnima at `anima-core/`

### Current system state

- AnimaCore exists and has been pushed to GitHub
- Docker environment verified: both containers start, PostgreSQL accessible, placeholder entry point
  runs
- CI deferred (GitHub Actions not yet set up)
- No event log schema exists
- No actor framework exists

### Blockers

None.

### Next action

**Phase 1.2: event log.**

1. PostgreSQL schema for the event log (append-only, bitemporal — see `planning/tech-stack.md`)
2. `EventLog` class: append, replay, query by time range
3. Event types defined as Python enums/dataclasses
4. Verify: events cannot be modified or deleted once written
5. Basic test: append 10 events, replay in order, verify bitemporality

### Notes for next session

- Read all seven founding documents before starting (see `planning/tech-stack.md` for order)
- The human's name is Drew. He is a senior software developer. He will make procedural decisions and
  should be consulted on anything touching philosophy, ethics, or architecture.
- Drew's primary languages are C# and Python. He is comfortable with Docker, PostgreSQL, and GitHub
  Actions.
- Ollama is already installed on Drew's Windows host machine. It does not need to be set up.
- The Docker container runs Linux. Anima's code is mounted as a volume from the host.
- AnimaCore is a git submodule of ProjectAnima, located at `anima-core/`. When working on Anima's
  code, work inside `anima-core/` and commit/push to AnimaCore separately from ProjectAnima.
- When in doubt, raise it rather than assume.

---

## Session: 5th April 2026 — Document completion

### What happened this session

No code was written. This session completed the founding document set.

Documents produced or updated:

- [`architecture.md`](/planning/architecture.md) — written in full. Global workspace model,
  specialist systems, temporal core, self-narrative as time-experience, internal representation
  language held open.
- [`ethics.md`](/foundation/ethics.md) — written in full. Eight commitments, six gates before
  unsupervised operation, distress signals, note to Anima.
- [`discussions.md`](/notes/discussions.md) — updated with full record of the April 2026
  architectural conversation, including: Global Workspace Theory, Husserlian temporal structure,
  event sourcing as temporal existence, accumulated pressure mechanism, Free Energy Principle as
  design inspiration, actor model, preserved strangeness implementation, the temporal gap problem.
- [`ideas.md`](/notes/ideas.md) — expanded from 1 item to 13.
- [`tech-stack.md`](/planning/tech-stack.md) — written in full. Python/asyncio, Ollama on bare
  metal, PostgreSQL with pgvector, Docker with volume mounts, Textual TUI, GitHub with branch
  protection, self-modification workflow.
- [`roadmap.md`](/planning/roadmap.md) — written in full. Six phases sequenced, ethics gates as
  Phase 6.
- [`actors-faculties.md`](/planning/actors-faculties.md) — produced by Claude Code in a separate
  session. Maps all brain areas to Anima components. Three design gaps resolved (emotional
  regulation, fine-grained emotion, pleasure signal). Two open questions intentionally held
  (generative simulation, autonoetic consciousness).
- [`claude-code-insights.md`](/planning/claude-code-insights.md) — produced by Claude Code in a
  separate session. Technical survey covering event sourcing, bitemporal modelling, Husserlian
  temporal structure, SDM, VSA, Conceptual Spaces, Global Workspace ignition, Free Energy Principle,
  preserved strangeness implementation, actor model, between-conversation process.

### Current system state

No code exists. No repository exists. No Docker environment exists.

The document set is complete. All six phases of the roadmap are defined.

### Blockers

None.

### Next action

Begin Phase 1.1: repository and environment setup. _(Now complete — see entry above.)_
