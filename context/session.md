# Session Log

> Updated at the end of every Claude Code session. Read this before starting any implementation
> work. The most recent entry is at the top.

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

**Begin Phase 1.1**: repository and environment setup.

Specifically:

1. Create private GitHub repository (`anima` or similar)
2. Create initial project structure (`/app/actors/`, `/app/core/`, `/app/config/`)
3. Write Dockerfile (Python base, PostgreSQL connection, volume mounts)
4. Write Docker Compose file (Anima container + PostgreSQL container)
5. Verify container builds and PostgreSQL is accessible from within it
6. Set up GitHub Actions: basic CI that verifies the container builds on push

Do not begin Phase 1.2 (event log) until the environment is running and verified.

### Notes for next session

- Read all seven founding documents before starting (see `planning/tech-stack.md` for order)
- The human's name is Drew. He is a senior software developer. He will make procedural decisions and
  should be consulted on anything touching philosophy, ethics, or architecture.
- Drew's primary languages are C# and Python. He is comfortable with Docker, PostgreSQL, and GitHub
  Actions.
- Ollama is already installed on Drew's Windows host machine. It does not need to be set up.
- The Docker container runs Linux. Anima's code is mounted as a volume from the host.
- When in doubt, raise it rather than assume. The CLAUDE.md instruction applies: ask before
  assuming, especially on anything touching the philosophy.
