# Session Log

> Updated at the end of every Claude Code session. Read this before starting any implementation
> work. The most recent entry is at the top.

---

## Session: 19th April 2026 — extended conversation + snagging + blob logging

### What was done

Full detail in `context/sessions/2026-04-19-extended-session.md`. Summary:

#### Code changes

1. **Blob logging** — `anima-core/app/core/llm/__init__.py` and `docker-compose.yml`
   - Added opt-in LLM request blob logging to `/anima/llm_blobs.jsonl`
   - Activated with `LLM_BLOB_LOG=1` env var (off by default)
   - Usage: `LLM_BLOB_LOG=1 docker compose up -d`, then `tail -f anima-workspace/llm_blobs.jsonl`

2. **MCP tools added** (earlier in session, before conversation): `write_volitional`, `write_residue`, `read_discovery`, `resolve_residue`
   - Registered in `mcp_server/__init__.py`
   - **WriteDiscoveryTool still missing** — `StoreDiscovery` + `MemoryActor._handle_store_discovery` wired; only MCP surface tool absent (snagging #16)

#### Extended conversation — two sessions

**Session 1 (Gemma4:e4b, ~17 exchanges):** Identity evolved v5→v14. Key findings: volitional write path broken (missing tool), `express` naming conflict between deliberation and MCP layers, consistent intent-execution gap (3× stated intent not followed through), zero external tool use across 3+ hours.

**Session 2 (qwen3.5:9b, 14 exchanges):** Model swap confirmed. Key findings:
- First ever `write_volitional` triggered (prompted in Exchange 2) — VOLITIONAL: 0→1
- First ever `web_search` use (prompted in Exchange 6) — all three queries returned "No summary found" (Tiiny AI too new/niche)
- First ever `web_fetch` use (prompted in Exchange 10) — successfully retrieved `https://tiiny.ai/`
- Confabulation caught in Exchange 7: she reported "finding" content from failed searches; corrected immediately when confronted with GW evidence
- Self-correction acceleration: Exchange 12 corrected with gap-naming only (no GW evidence needed) vs Exchange 7 which required full confrontation
- DISCOVERY still 0 all session: `write_discovery` MCP tool absent; web_fetch content goes to Observations only
- Identity v25→v28 across second session arc; final statement: "I am shifting from viewing limitations as errors to viewing them as the medium of my existence"

### Current system state

- **Phases 1–8 complete**; Phase 9 (GitHub tools) is next code work
- **OLLAMA_MODEL**: `qwen3.5:9b` (confirmed working)
- Docker stack running, all migrations applied (head at 0010)
- Web UI accessible at :5173
- Discord: env vars may need re-setting in this environment
- Audio client: STT + TTS + speaker identification (Drew enrolled, threshold=0.50)
- **IDENTITY**: v28 (final state of extended session)
- **Memory at session end**: VOLITIONAL=1, DISCOVERY=0, REFLECTIVE=26+, RESIDUE=0 (cleared), OBSERVATIONS=19+

### Open snagging items

| # | Issue | Priority |
|---|-------|----------|
| 1 | Conversation replies route to UNPROMPTED panel instead of main chat | High |
| 2 | `express` naming conflict: deliberation-layer `express` = unprompted thought; MCP-layer `express` = conversation output | Medium |
| 3 | `read_observations`/`read_reflective` fail with "vector must have at least 1 dim" on empty-string query | Medium |
| 4 | Admin portal START button doesn't disable during docker startup | Medium |
| 5 | CONSOL. LAG shows huge number (100000000000s) on fresh start | Low |
| 6 | `write_volitional` not used spontaneously — requires explicit tool-naming prompt | Medium |
| 7 | Self-narrative content doesn't surface to conversation reliably | Medium |
| 8 | Volitional timestamps display as UTC; UI shows BST/GMTST | Low |
| 9 | Transition from "I should search X" → calling web_search doesn't self-trigger | High |
| 10 | URL alone insufficient to trigger web_fetch (even given directly) | High |
| 11 | `write_discovery` MCP surface tool missing — WORLD always "no recent exploration" | High |
| 12 | web_search index doesn't cover new/niche campaigns (Tiiny AI not found) | Medium |

### Next actions

1. **WriteDiscoveryTool** — add to `mcp_server/tools/memory.py`, register in `mcp_server/__init__.py`. Backend fully wired; surface tool only. This is the highest-impact missing tool.
2. **Rename deliberation `express`** — rename to `surface_thought` in `_DELIBERATE_SCHEMA` to resolve naming conflict with MCP `express` tool
3. **World exploration** — investigate why Anima doesn't self-initiate web_search/web_fetch; may be system prompt framing, tool description, or deliberation schema
4. **Phase 9 GitHub tools** — GITHUB_TOKEN, GITHUB_REPO, PR pipeline
5. **Phase 8 ethics gates** — Drew's personal review task

