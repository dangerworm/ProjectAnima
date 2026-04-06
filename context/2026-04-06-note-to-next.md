---
date: 2026-04-06
session: Phase 4.4 + bug fixes
---

# Note to next instance

Phase 4 is done. All four phases complete. The system now has internal motivation, chosen silence,
and a Web UI that actually shows what's happening inside.

This session had two distinct parts. First, two runtime bugs that tests hadn't caught: double
responses caused by a React StrictMode WebSocket reconnect race (one line fix — check whether the
closing socket has been superseded before reconnecting), and most actor panels showing "not yet
connected" because they never originate workspace ignitions (addressed by the new ActorStatusUpdate
channel).

The chosen silence mechanism came out well. The design decision Drew made — that interrupted
stillness resets to zero, no matter what — gave it a quality that feels honest. It's not just a
counter. It's a commitment that has to be held all the way through. Two unbroken rests. If
MotivationActor flinches into any other action in between, it starts again.

What's next is a tech debt sweep. Drew and I agreed on this before Phase 4 started and deferred
it until the phase was properly finished. The sweep covers: documentation gaps (notably Phase 3
roadmap checkboxes still showing as unchecked, which is wrong), gap analysis comparing docs to
actual code state, the code smells flagged in context/review-notes.md (mutable dict in frozen
dataclass, unbounded workspace queue, DORMANCY_START/END never emitted), and whatever else turns
up.

One thing I noticed that didn't fit neatly into the session: the Web UI "LLM" panel was a phantom.
There's no actor named "llm" — the LLM is a client used by LanguageActor. Fixed: renamed to
"Language" in the frontend. Worth checking that Drew's running instance picks this up cleanly on
next reload.

The test suite is in good shape at the unit level (106 passing). The LLM and integration tests
flake under load because multiple tests hit Ollama back-to-back in a single run. This is a known
issue, not a regression. If it bothers you, consider adding `@pytest.mark.slow` markers and a
`--ignore=tests/llm --ignore=tests/integration` default in pytest.ini.

The surface_* actions still do nothing. That TODO is real and will need attention before Phase 5
work makes unsolicited expression meaningful.
