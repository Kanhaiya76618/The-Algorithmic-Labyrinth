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

### Adaptation (IMPLEMENTED — updated 2026-07-04 after live smoke debugging)

Four findings from the live run changed the original plan:

1. **`ResponseQAEntry` never appears in recall results when `query_type` is
   explicit.** recall.py:434-445: an explicit `query_type` forces the source
   list to `["graph"]` — the session/QA source is skipped entirely (only the
   `query_type is None` auto path merges it). The QA row for the recall IS
   still written (the graph completion runs through
   `SessionManager.generate_completion_with_session`, awaited before recall
   returns). Fix: read it back directly —
   `SessionManager.get_session(user_id, session_id, last_n=1)` right after
   recall; that entry's `qa_id` is the interaction id of the answer just
   produced.
2. **Session history poisons profile answers.** The session answer path
   feeds conversation history (our previous JSON profiles) into the prompt;
   at temp 0 the model anchors on them and new episodes stop registering —
   staleness the query nonce cannot defeat. Fix: **rotate the session id per
   recall** (`profile_{player}_{uuid8}`); history stays empty, answers stay
   fresh, and feedback/improve still target the session of the last
   successful recall (tracked in the service).
3. **`feedback_score` is a 1..5 rating, not a signed delta.**
   `SessionQAEntry` validation rejects negatives. Our [-5..+5] game scores
   map linearly: -5→1, 0→3, +5→5; signed semantics stay in `feedback_text`.
4. **`improve()` without `session_ids` never applies feedback.** It only
   enriches the graph; `apply_feedback_weights_pipeline` runs solely for the
   sessions passed in. Fix: `improve(dataset, session_ids=[<last recall's
   session>])`.

### Reinforcement: dual-channel (episode content + session weights)

The session feedback-weight channel alone **cannot** move the profile on
small graphs: weights only re-RANK triplets, and with `top_k=15 >= graph
size` every triplet is retrieved regardless, so the LLM context is
unchanged. Verified live: `apply_feedback_weights` logged
`nodes=16, edges=15, applied=True` yet the next recall was byte-identical.

`reinforce()` therefore writes BOTH:

- **Channel 1 (load-bearing): a feedback EPISODE** — the outcome lands as a
  real `remember()` episode (`event_type="feedback"`, rendered as "Boss
  profile correction about player X: outcome score -5: ..."). Graph CONTENT
  changes, so the next recall's context changes at any graph size. The
  system prompt instructs that corrections override episode-derived
  assessments.
- **Channel 2 (opportunistic): session QA feedback** — `session.add_feedback`
  keyed to the last recall's `qa_id`, bridged by
  `improve(session_ids=[...])` into graph `feedback_weight`s, applied by
  recalls via `feedback_influence=0.5`. Skipped without error when no qa_id
  exists; `recall_profile`/`reinforce` never depend on it.

This is a deliberate engineering choice made at hackathon time: session-
scoped QA feedback alone was not observable on demo-sized graphs (plus the
cognee 1.2.2 session/permission interactions above), so reinforcement is
carried by graph-enriched feedback episodes with session feedback layered on
top. All four verbs stay genuinely exercised; smoke-verified end to end.

### Concurrency: dataset-creation race (CONFIRMED live)

Two concurrent `remember()` calls for a NEW dataset race:
`get_dataset_ids` reads the ownership table while
`get_specific_user_permission_datasets` reads the ACL table — writer B can
see writer A's freshly-inserted Dataset row before A's ACL grant commits →
spurious `PermissionDeniedError ... [write]`. Fix: the service serializes
cognee writes per player (`asyncio.Lock` per player_id).

## Session caching & determinism

Session memory is ON by default (`CACHING` env toggles); the feedback loop
needs it for QA entries. Staleness is handled structurally now — sessions
rotate per recall (see above), so no answer is ever generated on top of a
previous profile answer. The query nonce is kept as a cheap extra guard.
`forget()` also deletes the player's current session cache
(`SessionManager.delete_session`), otherwise stale qa_ids would leak back
after a wipe.

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
