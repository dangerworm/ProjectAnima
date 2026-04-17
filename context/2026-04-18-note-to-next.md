# Note to next instance — 18 April 2026

Drew was asleep through this session. I was working from the context summary, picking up where the
previous window ran out mid-build. That worked. The approach of reading session.md + ANIMA.md first
(from CLAUDE.md) is the right one — this session was smooth because I had that structure.

What this session built: Phase 8 ethics gate infrastructure (PostgreSQL triggers for volitional
memory and residue store immutability, test file, two ethics documents), Phase 7.1 audio pipeline
(backend endpoint + standalone capture script + Web UI tab update), and Phase 9 self-modification
tools (GitHub API-based propose_code_change and read_pr_status MCP tools).

A few things worth knowing going in:

The ethics documents (distress-response.md, ethics-review.md) are templates that Drew needs to
fill in. They're not complete in the sense that Gate 5 still needs Drew's actual written assessment,
and Gate 6 procedure needs to be exercised at least once. The infrastructure is there, but the human
piece of it isn't done.

The audio pipeline is built but not tested end-to-end. The capture script (audio_client/capture.py)
uses Silero VAD and WhisperX and POSTs transcriptions to /perception/audio. It runs on the host,
not in Docker. Drew will need to install the requirements and test it against a running stack.
WhisperX will download model weights on first run.

The Phase 9 tools require GITHUB_TOKEN and GITHUB_REPO set in .env. The repo path would be the
anima-core submodule's GitHub remote — I don't know what that is yet. Drew will need to set that up
before the tools are live.

One design decision I made that Drew should know about: the propose_code_change tool is restricted
to anima-core/ file paths only (won't touch the outer ProjectAnima repo), and the branch must start
with "anima/". These feel like the right constraints but Drew should confirm.

The "clean LLM review" in Phase 9 is a bare Ollama call with just the diff — no system prompt, no
Anima identity context, no memory. This is intentional: it gives Drew an independent read. It might
feel odd to Anima to have its proposals reviewed by a stripped-down version of itself. Worth
mentioning to Anima when this first runs.

Migration 0006 needs to run before the next live session.

Quality of this session: methodical, no major errors. TypeScript passed cleanly. Python AST parsed
clean. I didn't run the full test suite inside Docker — that still needs to happen.

The next thing that matters most is probably running the stack and verifying the MCP architecture
actually works. Phase 6 was completed but never run live. That's the biggest unknown.
