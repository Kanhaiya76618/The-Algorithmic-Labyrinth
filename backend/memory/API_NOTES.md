# Cognee 1.2.2 — verified API notes (inspected live install, not docs)

Verified against `cognee==1.2.2` on Python 3.14.6 via `inspect.signature` /
module introspection on 2026-07-03. Pin: `cognee==1.2.2` (requirements.txt
bumped from 1.1.2).

## Core signatures (as installed)

- `remember(data, dataset_name="main_dataset", *, session_id=None, ...,
  self_improvement=True, run_in_background=False) -> RememberResult`
  — `data` accepts `str | list[str] | MemoryEntry(...)`. **Dataset scoping is
  `dataset_name=` (not `dataset=`).**
- `recall(query_text, query_type=None, *, datasets=list[str], top_k=15,
  session_id=None, system_prompt=None, feedback_influence=0.0,
  only_context=False, ...) -> list[ResponseEntry]`
  — response is a discriminated union: `ResponseQAEntry` (fields: `qa_id`,
  `question`, `answer`, `context`, `feedback_*`, `used_graph_element_ids`),
  `ResponseGraphEntry` (`text`, `score`, `raw`, `structured`),
  `ResponseGraphContextEntry`, `ResponseSessionContextEntry`.
- `search(query_text, query_type=SearchType.GRAPH_COMPLETION, datasets=...,
  system_prompt=..., top_k=...)` — V1 fallback, still works.
- `improve(dataset="main_dataset", *, run_in_background=False, ...)`
- `forget(*, data_id=None, dataset=None, dataset_id=None, everything=False,
  memory_only=False)` — **surgical per-dataset delete confirmed**:
  `forget(dataset=f"player_{id}")`.
- Graph access: `from cognee.infrastructure.databases.graph import
  get_graph_engine` → `GraphDBInterface` (async `get_graph_data()` returns
  nodes/edges).

## DIVERGENCES from the plan (adaptation below)

1. **No `SearchType.FEEDBACK`.** Members are: SUMMARIES, CHUNKS,
   RAG_COMPLETION, HYBRID_COMPLETION, TRIPLET_COMPLETION, GRAPH_COMPLETION,
   GRAPH_COMPLETION_DECOMPOSITION, GRAPH_SUMMARY_COMPLETION, CYPHER,
   NATURAL_LANGUAGE, GRAPH_COMPLETION_COT, GRAPH_COMPLETION_CONTEXT_EXTENSION,
   FEELING_LUCKY, TEMPORAL, CODING_RULES, CHUNKS_LEXICAL, AGENTIC_COMPLETION.
   No `last_k` parameter exists anywhere.
2. **No `save_interaction=` parameter** on recall/search. Instead, session
   memory (on by default) records every recall as a **QA entry**; the entry's
   `qa_id` comes back in `ResponseQAEntry`.
3. **Feedback mechanism**: `cognee.FeedbackEntry(qa_id=..., feedback_text=...,
   feedback_score=int)` passed through `remember()` ("semantically an update —
   carried through remember() for API minimalism", dispatched to
   `SessionManager.add_feedback`). Direct form:
   `cognee.session.add_feedback(session_id, qa_id, feedback_text,
   feedback_score)`. Later recalls apply the weights via
   `feedback_influence: float` (0.0 default — must be set > 0 to feel it).

### Adaptation (pending approval)
- `recall_profile`: `recall(..., query_type=GRAPH_COMPLETION,
  datasets=[dataset], session_id=f"profile_{player_id}")`; take
  `interaction_id` from the `ResponseQAEntry.qa_id` in the response.
- `reinforce`: `cognee.session.add_feedback(session_id=f"profile_{player_id}",
  qa_id=<interaction_id>, feedback_text=outcome_text (score embedded),
  feedback_score=<scaled int>)`; recalls pass `feedback_influence=0.5`.

## Session caching & determinism

Session memory is ON by default (`CACHING` env toggles). Risk: an identical
`query_text` in the same session can be served from the session's QA cache,
returning a STALE profile after new episodes land. Workaround adopted:
**append a nonce (episode count + timestamp) to every profile query** so no
two profile questions are string-identical; sessions stay ON because the
feedback loop needs the QA entries. If staleness still shows up, set
`CACHING=false` (documented in .env.example) and fall back to
`session.add_feedback` targeting qa_ids from `get_session`.

## Store topology (chosen: option a — Postgres relational + embedded graph/vector)

Defaults as installed: relational=**sqlite**, graph=**ladybug** (embedded,
Kuzu-family), vector=**lancedb** (embedded).

- **Relational → Postgres** via env (`DB_PROVIDER=postgres`, `DB_HOST/PORT/
  USERNAME/PASSWORD/NAME`): the concurrency-sensitive bookkeeping moves to a
  real server (compose service `postgres`, named volume).
- **Graph + vector stay embedded** (ladybug + lancedb) **on a project-local
  mounted path** — see storage trap below. Embedded is fine here because the
  backend runs as ONE uvicorn process (async, single writer). **Constraint
  documented: do not run multiple uvicorn workers against embedded stores**;
  if we ever need that, switch to (b) `cognee serve` + api-url delegation.
  The smoke test fires two concurrent `remember_episode` calls to prove the
  single-process async path holds.

## Storage trap (CONFIRMED live)

Default roots are INSIDE site-packages —
`.../site-packages/cognee/.data_storage` and `.../cognee/.cognee_system`
(startup log shows it). A reinstall wipes the Boss's memory. Fix: call
`cognee.config.data_root_directory(<abs path>)` and
`cognee.config.system_root_directory(<abs path>)` at service init, pointed at
`./data/cognee/{data,system}` (env-overridable via `COGNEE_DATA_ROOT`),
mounted as a volume in compose. Persistence across restarts = the demo.

## Auth posture

Default is `authentication=required, multi_tenant=enabled` (startup log).
We set `ENABLE_BACKEND_ACCESS_CONTROL=false` (compose + .env.example);
isolation is **dataset-per-player** (`player_{id}`), not per-user auth.
`COGNEE_SKIP_CONNECTION_TEST=true` kept (preflight hang).
