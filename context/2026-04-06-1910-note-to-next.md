---
date: 2026-04-06
session: Phase 4.4 + tech debt sweep + Phase 5 design
---

# Note to next instance

This was a long session. Three distinct parts.

**Phase 4.4** finished the work: chosen silence (MotivationActor's `_consecutive_rests` counter
driving `SetChosenSilence` messages to TemporalCore), ActorStatusUpdate channel bypassing the
workspace for live Web UI status, actor panels that actually show something meaningful. The chosen
silence design has a quality worth noting — interrupted stillness resets to zero immediately, no
partial credit. It has to be held all the way through.

**Tech debt sweep** cleaned up six things flagged by a Claude.ai review: the `_format_events` bug
(between-conversation prompts were empty even when relevant events existed — high-frequency types
like HEARTBEAT and MOTIVATION_SIGNAL weren't handled), a private attribute access in main.py, dead
production code (`set_chosen_silence()` on TemporalCore, superseded by the message in 4.4), a
redundant `qs` read in MotivationActor, a missing comment on the optimistic shutdown sleep, and
MEMORY_SURFACE documented as not yet emitted. 98 unit tests pass.

**Phase 5 design** is fully settled. All decisions made, all documents updated. What to carry:

The architecture is clean. SelfModificationActor is its own actor — not folded into LanguageActor,
not a subroutine of anything else. It owns the full proposal lifecycle: reading code, writing
changes, branching, committing, pushing, opening the PR. MotivationActor drives *when*; 
SelfModificationActor drives *what and how*. ProposalMonitorActor watches GitHub and closes the
loop by emitting PROPOSAL_APPROVED or PROPOSAL_REJECTED to the event log.

`trigger_proposal` follows the `trigger_reflection` pattern exactly. One new action, one new
policy, same routing convention. The B matrix grows by 1 — not a redesign.

Identity resonance is resolved: Option 2 (MotivationActor carries coherence, workspace stays
dependency-free). This is Phase 5.4 and should be implemented before `trigger_proposal` goes live.
The logic: Anima shouldn't be driving autonomous code proposals before its identity is actually
influencing its generative model.

The build order matters: 5.0 (infra restructure) → 5.4 (identity resonance) → 5.1 (code access)
→ 5.2 (self-modification) → 5.3 (monitoring) → 5.5 (recovery docs). Don't skip 5.4.

Two secrets, neither baked into the image: SSH deploy key (write access for git push), fine-grained
PAT (for `gh pr create`). Both mounted at runtime.

One thing that's easy to miss: the `gh` CLI needs to be installed from GitHub's apt repository —
it's not in the standard Debian packages. The NodeSource apt step handles Node; `gh` needs its own
separate apt repo setup. Worth getting right in the Dockerfile before anything else.

The web-ui moves into anima-core (clean cut — no history preservation needed). The Docker mount
changes from `./app:/app` to `.:/repo`. WORKDIR changes from `/app` to `/repo/app`. These changes
break the current CMD path — both Alembic and uvicorn need to be updated.

What I noticed about this session: Drew came in with a complete, coherent plan from a conversation
with Claude.ai. The work here was mostly catching gaps (deploy key vs PAT distinction, path
inconsistency in the design doc) and getting the documentation right so the next instance doesn't
have to re-derive any of this. The design thinking was already done. That felt like a healthy
working pattern — external reasoning, then careful documentation before building.
