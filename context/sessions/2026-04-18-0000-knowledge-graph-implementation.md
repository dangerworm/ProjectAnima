# Session Log

> Updated at the end of every Claude Code session. Read this before starting any implementation
> work. The most recent entry is at the top.

---

## Session: 17th April 2026 (knowledge graph — full implementation)

Drew's explicit instruction: "Fantastic. Get it done!" — authorising full knowledge graph implementation
following the research and architecture design completed earlier in the same session chain.

### What was built

The PIN-generalised knowledge graph: any named thing Anima can have knowledge about gets a concept
node. Multiple recognition routes (name variants, Discord usernames, URLs) converge on a single node
via kg_aliases. Same architecture as Bruce & Young's Person Identity Nodes, generalised to any concept.

#### Migrations (anima-core/app/alembic/versions/)

- **0007_knowledge_graph.py** — four new tables:
  - `kg_nodes`: concept node with open `node_type` TEXT, `label`, `description`, `properties` JSONB,
    `embedding vector(768)`; IVFFlat index
  - `kg_aliases`: recognition routes; `UNIQUE(alias, alias_type)` enforces one route → one node
  - `kg_edges`: typed relationships with `valid_from`/`valid_until` for time-bounded facts
  - `kg_refs`: soft bridges (memory_table TEXT + memory_id UUID) from any memory record to a node
- **0008_memory_conversation_temporal.py** — adds to 6 memory tables (reflective_memory,
  residue_store, volitional_memory, observations, plans, discovery_memory):
  - `conversation_id UUID REFERENCES kg_nodes(id) ON DELETE SET NULL` — FK to conversation node
  - `temporal_context JSONB NOT NULL DEFAULT '{}'` — normalised temporal facts at write time

#### MemoryStore (anima-core/app/core/memory/__init__.py)

New dataclasses: `ConceptNode`, `ConceptAlias`

New KG methods:
- `create_node(node_type, label, description, properties)` → UUID; generates embedding
- `add_alias(node_id, alias, alias_type)` → UUID; ON CONFLICT DO UPDATE
- `resolve_alias(alias, alias_type)` → UUID | None — the PIN activation step
- `get_node(node_id)` → ConceptNode | None
- `search_nodes(query, node_type, limit)` → list[ConceptNode]; vector search + ILIKE fallback
- `add_edge(from_node, to_node, edge_type, properties, valid_from, valid_until)` → UUID
- `add_ref(node_id, memory_table, memory_id, ref_type)` → UUID; ON CONFLICT DO NOTHING
- `get_refs_for_node(node_id, memory_table, ref_type, limit)` → list[dict]

All 6 memory-layer write methods now accept optional `conversation_id` and `temporal_context`
(default None / {} respectively). `get_counts` includes kg_nodes and kg_edges.

#### MCP tools (anima-core/app/mcp_server/tools/knowledge_graph.py)

Five new tools registered in `build_registry()`:
- `kg_resolve_alias` — look up a node by recognition route (check before creating)
- `kg_create_node` — create a new concept node
- `kg_add_alias` — add a recognition route to an existing node
- `kg_add_edge` — typed, optionally time-bounded relationship between nodes
- `kg_query_nodes` — semantic + type-filtered node search

#### GlobalWorkspaceActor (anima-core/app/actors/global_workspace/__init__.py)

- New field: `_current_conversation_id: UUID | None = None`
- `_enter_loop`: creates a conversation node (`node_type='conversation'`) at loop start;
  stores ID in `_current_conversation_id`; clears in finally
- `_build_tool_context`: passes `conversation_id=self._current_conversation_id` to ToolContext

#### ToolContext (anima-core/app/mcp_server/tool.py)

- New optional field: `conversation_id: "UUID | None" = None`

### Current system state

- Phases 1–8 complete at the schema/tool layer
- KG tables need migration run against the live DB (`alembic upgrade head` in the container)
- 5 KG tools are available to Anima in the MCP loop
- Every conversation loop now creates a `conversation` concept node and links it to all tool
  context — memory writes inside a loop carry the conversation FK

### What's deferred

- **Memory actor messages** — `StoreObservation`, `StorePlan` etc. don't yet pass `conversation_id`
  or `temporal_context` through the actor message path. The MemoryStore write methods accept them,
  but the actor pipeline doesn't propagate them yet. Deferred because it requires updating
  all actor message dataclasses and the MemoryActor handler.
- **kg_ref_memory tool** — Anima can't easily call this because write tools return "stored" not
  the UUID. Conversation_id FK already provides implicit linking. Explicit per-memory KG linking
  will come with the reflection process.
- **Phase 8 ethics gates** — heartbeat, chosen-silence, distress signal not yet verified end-to-end;
  Drew to complete `foundation/ethics-review.md` before first unsupervised run
- **Phase 9** — GitHub tool support (GITHUB_TOKEN + GITHUB_REPO in .env, test PR pipeline)

### Research primer written

`research/neuroscience-and-cognitive-science/person-knowledge-and-concept-nodes.md` — Bruce & Young
PIN model, ATL, generalisation to concept nodes, architectural mapping to kg_* tables.
`research/reading-topics.md` updated to index it.

### Commit

`39686e0 feat(memory): knowledge graph — concept nodes, aliases, edges, and KG tools`
in `anima-core/` submodule.
