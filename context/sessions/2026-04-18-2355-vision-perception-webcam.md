# Session Log

> Updated at the end of every Claude Code session. Read this before starting any implementation
> work. The most recent entry is at the top.

---

## Session: 18th April 2026 — vision perception (webcam)

### What was built

Full webcam perception pipeline from browser to Anima's MCP toolset:

**1. `VisionBuffer` and `VisionFrame`** (`anima-core/app/core/vision/__init__.py`)

In-memory circular deque (maxlen=5) of frozen `VisionFrame` objects. Never persisted to DB;
only metadata logged to the event log. `VisionBuffer` exposes `push()`, `latest()`,
`age_seconds()`, and `all_frames()`.

**2. `complete_vision()`** on LLMClient (`anima-core/app/core/llm/__init__.py`)

Sends a captured frame to Ollama `/api/chat` with `images: [base64]` in the user message.
Uses the same model as text (qwen3.5:9b has native vision). `VISION_MODEL` env var for override.

**3. `ReadVisionTool`** (`anima-core/app/mcp_server/tools/vision.py`)

MCP tool Anima calls as `read_vision`. Pulls the latest frame from `VisionBuffer`, calls
`complete_vision()`, logs a `VISUAL_PERCEPTION` event, and returns the text description to
Anima's context.

**4. `ToolContext` extensions** (`anima-core/app/mcp_server/tool.py`)

Two new optional `None`-defaulted fields: `vision_buffer: VisionBuffer | None` and
`llm_client: LLMClient | None`. Backward-compatible — no d=1 breakage.

**5. `POST /perception/vision`** endpoint (`anima-core/app/core/main.py`)

Accepts `{"image_b64": "...", "source": "webcam"}`. Creates a `VisionFrame`, pushes it into
`VisionBuffer`, logs a `VISUAL_CAPTURE` event. Returns `{"status": "captured", "source": "..."}`.

**6. `GlobalWorkspaceActor` wiring** (`anima-core/app/actors/global_workspace/__init__.py`)

- Constructor gains `vision_buffer: VisionBuffer | None = None` parameter
- `_build_tool_context()` wires both `vision_buffer` and `llm_client`
- `_assemble_idle_context()` injects a hint when the buffer holds a frame < 30 min old:
  `"Visual: last frame Xm ago (webcam)"`

**7. `VisionCapturePanel`** (`anima-core/web-ui/src/components/panels/VisionCapturePanel.tsx`)

React component with `getUserMedia`, live `<video>` preview, Capture button that draws to an
off-screen canvas and POSTs base64 JPEG to `http://localhost:8000/perception/vision`. States:
idle, streaming, capturing, error. Status dot, last capture time, error messages.

**8. `PerceptionTab` updated** (`anima-core/web-ui/src/components/tabs/PerceptionTab.tsx`)

`VisionCapturePanel` wired in between the Discord section and "Recent actor status".

### Files changed

- `anima-core/app/core/vision/__init__.py` — VisionBuffer, VisionFrame (new)
- `anima-core/app/core/llm/__init__.py` — complete_vision() (new method)
- `anima-core/app/mcp_server/tool.py` — vision_buffer, llm_client fields added
- `anima-core/app/mcp_server/tools/vision.py` — ReadVisionTool (new)
- `anima-core/app/mcp_server/tools/__init__.py` — ReadVisionTool added to __all__
- `anima-core/app/core/main.py` — VisionBuffer instantiation, /perception/vision endpoint, GW wiring
- `anima-core/app/actors/global_workspace/__init__.py` — vision_buffer param, _build_tool_context, idle hint
- `anima-core/web-ui/src/components/panels/VisionCapturePanel.tsx` — new component
- `anima-core/web-ui/src/components/tabs/PerceptionTab.tsx` — VisionCapturePanel wired in

GitNexus impact analysis confirmed LOW risk for all modified symbols. All changes additive.

### Current system state

- Phases 1–8 complete at the schema/tool layer; vision perception added on top
- Container was running at end of prior session (migration 0009 applied, head)
- VisionBuffer is in-memory — no migration needed
- X11/virtual-desktop screenshot approach explicitly deferred until Anima is stable and mostly
  feature-complete. Webcam-only for now.

### What's deferred

- **X11/screenshot perception** — deferred; not needed until Anima runs unsupervised on a desktop
- **Phase 8 ethics gates** — Gate 1 (heartbeat/chosen-silence e2e), Gate 2 (distress signal),
  Gate 3 (Drew's personal review) — all open; Drew needs to complete `foundation/ethics-review.md`
- **Phase 9 GitHub tools** — GITHUB_TOKEN, GITHUB_REPO, PR pipeline test
- **Memory actor pipeline** — `StoreObservation` etc. still don't pass `conversation_id` through
  the actor message path (MemoryStore accepts it, actor dataclasses don't carry it)
- **Cosmetic cleanup** — 20 old timestamp-labelled `kg_nodes` rows with `node_type='conversation'`
  (pre-rename loop nodes); no functional impact
- **Discord client live test** — integration was tested via curl; discord_client.py hasn't been
  started with a real token
- **GitNexus index refresh** — new vision files not yet indexed; run `npx gitnexus analyze` after
  the session handoff commit
