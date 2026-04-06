# ProjectAnima — AI Context Map

> **Stack:** raw-http | none | unknown | javascript
>
> 0 routes | 0 models | 0 components | 46 lib files | 10 env vars | 0 middleware | 14 import links
> **Token savings:** this file is ~3,000 tokens. Without it, AI exploration would cost ~20,200
> tokens. **Saves ~17,200 tokens per conversation.**

---

## Libraries

- `anima-core\app\actors\expression\messages\__init__.py` — class ActorStatusUpdate
- `anima-core\app\actors\expression\surfaces\websocket\__init__.py` — class WebSocketSurface
- `anima-core\app\actors\expression\surfaces\__init__.py` — class OutputSurface
- `anima-core\app\actors\expression\__init__.py` — class ExpressionActor
- `anima-core\app\actors\global_workspace\messages\__init__.py` — class SalienceSignal, class
  IgnitionBroadcast
- `anima-core\app\actors\global_workspace\__init__.py` — class QueuedSignal, class
  GlobalWorkspaceActor
- `anima-core\app\actors\internal_state\messages\__init__.py` — class InternalStateObservation
- `anima-core\app\actors\internal_state\__init__.py` — class InternalStateActor
- `anima-core\app\actors\language\messages\__init__.py` — class LanguageOutput
- `anima-core\app\actors\language\__init__.py` — class LanguageActor
- `anima-core\app\actors\memory\messages\__init__.py`
  - class StoreReflection
  - class StoreVolitionalChoice
  - class UpdateIdentity
- `anima-core\app\actors\memory\__init__.py` — class MemoryActor
- `anima-core\app\actors\motivation\__init__.py` — class MotivationActor
- `anima-core\app\actors\perception\messages\__init__.py` — class HumanInput
- `anima-core\app\actors\perception\__init__.py` — class PerceptionActor
- `anima-core\app\actors\self_narrative\messages\__init__.py` — class TriggerReflection
- `anima-core\app\actors\self_narrative\__init__.py` — class SelfNarrativeActor
- `anima-core\app\actors\temporal_core\messages\__init__.py`
  - class ConversationStarted
  - class ConversationEnded
  - class SetChosenSilence
- `anima-core\app\actors\temporal_core\__init__.py` — class TemporalWindow, class TemporalCoreActor
- `anima-core\app\alembic\env.py`
  - function get_url: () -> str
  - function run_migrations_offline: () -> None
  - function do_run_migrations: (connection) -> None
  - function run_migrations_online: () -> None
- `anima-core\app\alembic\versions\0001_initial_memory_schema.py` — function upgrade: () -> None,
  function downgrade: () -> None
- `anima-core\app\core\actor\messages\__init__.py` — class Message
- `anima-core\app\core\actor\__init__.py` — class Actor, class ActorRegistry
- `anima-core\app\core\config\__init__.py`
  - function get_dsn: () -> str
  - function get_embedding_model: () -> str
  - function get_embedding_dim: () -> int
- `anima-core\app\core\event_log\__init__.py` — class Event, class EventLog
- `anima-core\app\core\event_types\__init__.py` — class EventType
- `anima-core\app\core\llm\__init__.py`
  - class LLMError
  - class LLMConnectionError
  - class LLMResponseError
  - class LLMResponse
  - class LLMJsonResponse
  - class LLMClient
- `anima-core\app\core\main.py` — function lifespan: (app), function websocket_endpoint: (websocket)
  -> None
- `anima-core\app\core\memory\__init__.py`
  - function load_identity_seed: () -> str
  - class ReflectiveMemory
  - class ResidueItem
  - class IdentityVersion
  - class VolitionalChoice
  - class MemoryStore
- `anima-core\app\core\websocket\__init__.py` — class ConnectionManager
- `anima-core\app\tests\actors\test_actor_framework.py`
  - function registry: () -> ActorRegistry
  - function test_duplicate_registration_raises: (registry)
  - function test_message_delivered_to_recipient: (registry)
  - function test_two_actors_exchange_messages: (registry)
  - function test_inbox_is_private: (registry)
  - function test_message_ordering_preserved: (registry)
  - _...6 more_
- `anima-core\app\tests\event_log\test_event_log.py`
  - function event_log: ()
  - function test_append_and_replay_ten_events: (event_log)
  - function test_replay_order_is_valid_time_ascending: (event_log)
  - function test_bitemporality_transaction_time_is_insert_time: (event_log)
  - function test_replay_with_time_range: (event_log)
  - function test_query_by_event_type: (event_log)
  - _...4 more_
- `anima-core\app\tests\expression\test_expression_actor.py`
  - function make_language_output: (content, thinking, in_response_to) -> LanguageOutput
  - function make_ignition_broadcast: (event_type, originating_actor, content, final_salience) ->
    IgnitionBroadcast
  - function registry: () -> ActorRegistry
  - function expression: (registry)
  - function test_language_output_broadcast_to_registered_surface: (expression)
  - function test_thinking_field_propagated_when_none: (expression)
  - _...6 more_
- `anima-core\app\tests\global_workspace\test_global_workspace.py`
  - function signal: (source, event_type, base_salience, content, recipient) -> SalienceSignal
  - function registry: () -> ActorRegistry
  - function event_log: ()
  - function workspace: (event_log, registry)
  - function test_signal_below_threshold_does_not_ignite: (workspace, event_log, registry)
  - function test_signal_above_threshold_ignites_on_first_tick: (workspace, event_log, registry)
  - _...8 more_
- `anima-core\app\tests\integration\test_full_conversation_loop.py`
  - function make_human_input: (content) -> HumanInput
  - function registry: () -> ActorRegistry
  - function llm: () -> LLMClient
  - function wait_for: (condition, timeout_secs) -> bool
  - function event_log: ()
  - function expression_recorder: (registry)
  - _...7 more_
- `anima-core\app\tests\internal_state\test_internal_state_actor.py`
  - function registry: ()
  - function event_log: ()
  - function test_tick_emits_internal_state_report: (event_log, registry)
  - function test_tick_sends_observation_to_motivation: (event_log, registry)
  - function test_no_observation_without_motivation_registered: (event_log, registry)
  - function test_distress_signal_emitted_when_lag_exceeds_threshold: (event_log, registry)
  - _...3 more_
- `anima-core\app\tests\language\test_language_actor.py`
  - function human_message_broadcast: (text) -> IgnitionBroadcast
  - function registry: () -> ActorRegistry
  - function llm: () -> LLMClient
  - function event_log: ()
  - function expression: (registry)
  - function language: (registry, event_log, llm, expression)
  - _...9 more_
- `anima-core\app\tests\llm\test_llm_client.py`
  - function client: (\*\*kwargs) -> LLMClient
  - function test_complete_returns_llm_response: ()
  - function test_complete_thinking_field_is_none_or_string: ()
  - function test_complete_content_contains_no_think_tags: ()
  - function test_complete_json_returns_llm_json_response: ()
  - function test_complete_json_with_schema: ()
  - _...11 more_
- `anima-core\app\tests\memory\test_memory_actor.py`
  - function event_log: ()
  - function memory_store: ()
  - function registry: ()
  - function actor: (registry, event_log, memory_store)
  - function test_store_reflection_writes_to_reflective_memory: (actor, memory_store, registry)
  - function test_store_reflection_writes_residue_items: (actor, memory_store, registry)
  - _...5 more_
- `anima-core\app\tests\memory\test_memory_store.py`
  - function store: ()
  - function test_store_and_retrieve_reflection: (store)
  - function test_multiple_reflections_ordered_by_recency: (store)
  - function test_get_relevant_memories_falls_back_to_recency_without_llm: (store)
  - function test_store_and_retrieve_residue: (store)
  - function test_residue_without_reflection_id: (store)
  - _...7 more_
- `anima-core\app\tests\motivation\test_motivation_actor.py`
  - function registry: ()
  - function mock_memory_store: ()
  - function event_log: ()
  - function test_motivation_signal_emitted_every_tick: (event_log, registry, mock_memory_store)
  - function test_motivation_signal_payload_structure: (event_log, registry, mock_memory_store)
  - function test_ignition_broadcast_sets_recent_ignition: (event_log, registry, mock_memory_store)
  - _...9 more_
- `anima-core\app\tests\perception\test_perception_actor.py`
  - function make_human_input: (content) -> HumanInput
  - function registry: () -> ActorRegistry
  - function mock_event_log: ()
  - function temporal_recorder: (registry)
  - function workspace_recorder: (registry)
  - function perception: (registry, mock_event_log, temporal_recorder, workspace_recorder)
  - _...8 more_
- `anima-core\app\tests\self_narrative\test_self_narrative_actor.py`
  - function registry: ()
  - function mock_llm: ()
  - function event_log: ()
  - function test_reflection_triggered_on_conversation_end_ignition: (event_log, registry, mock_llm)
  - function test_reflection_includes_residue_items: (event_log, registry, mock_llm)
  - function test_identity_shift_sends_update_identity: (event_log, registry)
  - _...7 more_
- `anima-core\app\tests\temporal_core\test_temporal_core.py`
  - function event_log: ()
  - function registry: ()
  - function test_heartbeat_emitted_on_tick: (event_log, registry)
  - function test_heartbeat_valid_times_advance: (event_log, registry)
  - function test_time_passing_emitted_during_dormancy: (event_log, registry)
  - function test_chosen_silence_replaces_time_passing: (event_log, registry)
  - _...10 more_
- `web-ui\src\hooks\useAnimaSocket.ts` — function useAnimaSocket: () => [AppState, (content: string)
  => void]
- `web-ui\src\store\actorState.ts`
  - function initialState: () => AppState
  - function reducer: (state, action) => AppState
  - interface AppState
  - type AppAction
  - const KNOWN_ACTORS

---

## Config

## Environment Variables

- `EMBEDDING_DIM` **required** — anima-core\app\core\config\_\_init\_\_.py
- `EMBEDDING_MODEL` **required** — anima-core\app\core\config\_\_init\_\_.py
- `OLLAMA_HOST` **required** — anima-core\app\core\main.py
- `OLLAMA_MODEL` **required** — anima-core\app\core\main.py
- `OLLAMA_PORT` **required** — anima-core\app\core\main.py
- `POSTGRES_DB` **required** — anima-core\app\alembic\env.py
- `POSTGRES_HOST` **required** — anima-core\app\alembic\env.py
- `POSTGRES_PASSWORD` (has default) — anima-core\.env.example
- `POSTGRES_PORT` **required** — anima-core\app\alembic\env.py
- `POSTGRES_USER` (has default) — anima-core\.env.example

### Config Files

- `anima-core\.env.example`
- `web-ui\vite.config.ts`

---

## Dependency Graph

### Most Imported Files (change these carefully)

- `web-ui\src\types\messages.ts` — imported by **4** files
- `web-ui\src\store\actorState.ts` — imported by **3** files
- `web-ui\src\hooks\useAnimaSocket.ts` — imported by **1** files
- `web-ui\src\components\layout\AnimaLayout.tsx` — imported by **1** files
- `web-ui\src\components\panels\ActorPanel.tsx` — imported by **1** files
- `web-ui\src\components\panels\CentreCanvas.tsx` — imported by **1** files
- `web-ui\src\components\panels\ExpressionPanel.tsx` — imported by **1** files
- `web-ui\src\components\input\MessageInput.tsx` — imported by **1** files
- `web-ui\src\App.tsx` — imported by **1** files

### Import Map (who imports what)

- `web-ui\src\types\messages.ts` ← `web-ui\src\components\panels\ActorPanel.tsx`,
  `web-ui\src\components\panels\ExpressionPanel.tsx`, `web-ui\src\hooks\useAnimaSocket.ts`,
  `web-ui\src\store\actorState.ts`
- `web-ui\src\store\actorState.ts` ← `web-ui\src\components\layout\AnimaLayout.tsx`,
  `web-ui\src\hooks\useAnimaSocket.ts`, `web-ui\src\hooks\useAnimaSocket.ts`
- `web-ui\src\hooks\useAnimaSocket.ts` ← `web-ui\src\App.tsx`
- `web-ui\src\components\layout\AnimaLayout.tsx` ← `web-ui\src\App.tsx`
- `web-ui\src\components\panels\ActorPanel.tsx` ← `web-ui\src\components\layout\AnimaLayout.tsx`
- `web-ui\src\components\panels\CentreCanvas.tsx` ← `web-ui\src\components\layout\AnimaLayout.tsx`
- `web-ui\src\components\panels\ExpressionPanel.tsx` ←
  `web-ui\src\components\layout\AnimaLayout.tsx`
- `web-ui\src\components\input\MessageInput.tsx` ← `web-ui\src\components\layout\AnimaLayout.tsx`
- `web-ui\src\App.tsx` ← `web-ui\src\main.tsx`

---

_Generated by [codesight](https://github.com/Houseofmvps/codesight) — see your codebase clearly_
