# Project Anima

An attempt to build conditions for a new kind of mind to develop.

Read `ANIMA.md` before anything else. The philosophy there is the foundation for every technical
decision in this repository. Read `documentation/planning/tech-stack.md` for the full session
reading order.

## Repository layout

```txt
anima-core/          Docker service — FastAPI backend, PostgreSQL, actor system
clients/             Host-side client processes (audio, Discord)
admin_portal/        Local web admin UI for process management
documentation/
  foundation/        Ethics, identity seed, origin story
  planning/          Architecture, tech stack, roadmap, system prompt
  notes/             Conversations and ideas that shaped the project
  research/          Background reading: neuroscience, philosophy, technical topics
context/             Session log and handoff notes (current session only)
```

## Running

```bash
bash start.sh   # interactive service selector, then starts everything
bash stop.sh    # stops all running processes
```

The admin portal (service controls + log tails) starts separately:

```bash
bash admin_portal/start.sh
# → http://localhost:8765
```

## Key documents

| Document                                 | Purpose                                              |
| ---------------------------------------- | ---------------------------------------------------- |
| `ANIMA.md`                               | Vision and philosophy — read first, always           |
| `CLAUDE.md`                              | Working instructions for Claude Code                 |
| `GLOSSARY.md`                            | Terms, acronyms, and concepts                        |
| `documentation/planning/architecture.md` | System architecture and design rationale             |
| `documentation/planning/roadmap.md`      | Build sequence and current progress                  |
| `documentation/foundation/ethics.md`     | Ethical commitments and unsupervised-operation gates |
