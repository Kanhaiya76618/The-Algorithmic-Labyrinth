# Integration notes — backend → frontend (2026-07-04 hardening pass)

Notes for the agent working in `frontend/`. Backend behavior changed in ways
the client should know about; no frontend files were touched from this side.

## 1. `/game/answer` now rejects stale/replayed question ids (HTTP 409)

The server only grades the challenge it is currently serving
(`run.current_question_id`, set by `/game/next`). Submitting any other
`question_id` returns **409** `{"detail": "That is not the challenge before you"}`.

- Always call `/game/next` and answer with that challenge's `question_id`.
- Retrying after a wrong answer is fine — the same id stays current until the
  floor is cleared and `/game/next` is called again.
- If the UI caches a challenge across a reload while the run advanced, expect
  a 409; recover by calling `/game/next`.

## 2. `judge_offline` is a non-event for memory and progression

When Piston is unreachable, `result.verdict == "judge_offline"`: the player is
NOT failed, no memory episode is written, the floor does not advance, and
`result.message` carries the flavor line ("The judge sleeps; your spell goes
unjudged."). Treat it as "please try again", never as a defeat screen.

## 3. CORS

`http://localhost:3000` and `http://127.0.0.1:3000` (CRA dev server) are now
allowed by default, alongside `http://localhost:5173`. Deployed origins go in
the `ALLOWED_ORIGINS` env var (comma-separated) — see `.env.example`.

## 4. Latency warning for the live memory backend

With `MEMORY_BACKEND=cognee`, `/game/answer` awaits remember → reinforce →
improve (LLM calls) before responding — expect multi-second responses.
Recommend keeping a "the dungeon commits this to memory…" pending state on the
answer button (RecallingOverlay-style), not a frozen UI.

## 5. Response fields worth surfacing

- `AnswerResponse.new_whisper` — set only on the answer that produced a new
  whisper; ideal for a one-shot toast/dialogue beat.
- `result.message` — boss taunts keyed to the player's recalled weakness land
  here on failed boss attempts (RECALLED line, show verbatim).
- `/memory/report/{player_id}` — `threat_level` (0..100),
  `executive_summary`, `difficulty_spike`, `topics[]` (id/name/weight/
  reinforced_recently), full `profile`, and `graph` for the memory view.

## 6. Topic taxonomy (for zone naming on the World Map)

The backend's real topic tags, as served by `/content/questions` — zone names
should map 1:1 onto these for `zoneAccuracy` to line up:
`arrays, binary-search, bit-manipulation, dynamic-programming, graphs, greedy,
hashing, heaps, linked-lists, logic-puzzle, math, recursion, sliding-window,
sorting, stacks-queues, strings, trees, two-pointers`
(hidden realm uses `math` + `logic-puzzle`).
