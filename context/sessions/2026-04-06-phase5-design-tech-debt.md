## Session: 6th April 2026 — Phase 5 design finalised; tech debt fixes

### What happened this session

Two threads: (1) Phase 5 architecture was fully designed and documented. (2) Six code/doc fixes from
a Claude.ai review were applied.

**Phase 5 design**

All architectural decisions resolved before build begins. Key outcomes:

- SelfModificationActor confirmed as a separate actor (not folded into LanguageActor)
- `trigger_proposal` follows the `trigger_reflection` → SelfNarrativeActor pattern; B matrix grows
  by 1 policy, no model redesign
- ProposalMonitorActor polls GitHub on a schedule; `PROPOSAL_APPROVED`/`REJECTED` close the loop
- Open proposals tracked via event log query on `proposal_id` — no new persistence mechanism
- Identity resonance resolved: Option 2 (MotivationActor carries coherence, workspace stays free)
- web-ui moves into anima-core (clean cut); mount changes from `./app:/app` → `.:/repo`
- Two runtime secrets: SSH deploy key (git push) + fine-grained PAT (gh pr create)
- Approval workflow: GitHub PR. No Web UI approval surface.
- Proposal initiation: autonomous only (MotivationActor). No conversation-driven path.
- Build order: 5.0 (infra restructure) → 5.4 (identity resonance) → 5.1 → 5.2 → 5.3 → 5.5

All decisions captured in roadmap.md, architecture.md, actors-faculties.md, event-types.md,
ideas.md, and actors-faculties.md.

**Bug fixes from Claude.ai review (all applied, tests passing)**

- `SelfNarrativeActor._format_events()`: between-conversation types (HEARTBEAT, TIME_PASSING,
  CHOSEN_SILENCE, MOTIVATION_SIGNAL, INTERNAL_STATE_REPORT, RESIDUE_FLAGGED) were not handled —
  prompts had "(no events in this period)" despite relevant events existing. Fixed: high-frequency
  types aggregated as summary lines; RESIDUE_FLAGGED shown per-event.
- `PerceptionActor._in_conversation`: accessed as a private attribute in `main.py`. Added
  `in_conversation` public property.
- `TemporalCoreActor.set_chosen_silence()`: dead production code (message-driven integration done in
  Phase 4.4). Removed; two tests that used it for setup now access `actor._chosen_silence` directly.
- `MotivationActor._tick`: redundant second `qs = self._agent.qs` read removed.
- `main.py` shutdown sleep: comment added explaining the 0.5s is optimistic for LLM reflection.
- `MEMORY_SURFACE` event type: documented as not yet emitted, with note on intended future path.

Test count: 98 unit tests passing (29 LLM/integration deselected).

**Next action**: Phase 5.0 — repository and infrastructure restructure (move web-ui into anima-core,
update Dockerfile and docker-compose.yml, provision SSH deploy key and PAT).
