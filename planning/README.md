# planning

The technical blueprint for Project Anima. Read these documents (in the order below) before
beginning any significant implementation work in a new session.

## Reading order

1. `tech-stack.md` — Concrete technology decisions and the full recommended reading order for new
   sessions. Start here.
2. `architecture.md` — How the system works and why each structural decision was made. Every
   decision is traceable to something in `ANIMA.md`.
3. `roadmap.md` — The ordered build sequence, phase by phase. Current progress is marked.

## Reference documents

| File                      | Purpose                                                                                                                             |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `actors-faculties.md`     | Maps known brain areas to Anima's technical actors and technologies.                                                                |
| `event-types.md`          | The canonical set of event type enum values for the event log. New types are defined here before being used in code.                |
| `system-prompt.md`        | The system prompt template used when calling the LLM.                                                                               |
| `source-model.md`         | Notes on the source LLM and model selection rationale.                                                                              |
| `claude-code-insights.md` | Technical survey of relevant ideas and technologies produced early in the project. Background reading for implementation decisions. |
