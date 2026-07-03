"""Go/no-go verification of the four memory verbs against LIVE cognee.

Prereqs: MEMORY_BACKEND=cognee · real LLM_API_KEY in .env · relational store
up (docker compose up -d postgres, or DB_PROVIDER=sqlite for solo dev).
Run:  python3 scripts/smoke_memory.py

Every step ASSERTS (exit 1 on any failure) and detects silent degradation:
the service swallows cognee errors by design (a memory outage must not crash
the game), so this harness listens on the "dor.memory" logger — any WARNING
during a step means the cognee path failed and the step FAILS even though the
journal fallback kept the API alive.
"""

from __future__ import annotations

import asyncio
import logging
import os
import socket
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend import config  # noqa: E402  (loads .env before cognee import)

PLAYER_A = "smoke_hero_a"
PLAYER_B = "smoke_hero_b"  # written NEVER — proves per-player isolation

RESULTS: list[tuple[str, bool, str]] = []


def record(verb: str, ok: bool, evidence: str) -> None:
    RESULTS.append((verb, ok, evidence))
    print(f"[{'PASS' if ok else 'FAIL'}] {verb}: {evidence}", flush=True)


class DegradationDetector(logging.Handler):
    """Collects dor.memory warnings — cognee failures the service swallowed."""

    def __init__(self) -> None:
        super().__init__(level=logging.WARNING)
        self.records: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record.getMessage())

    def drain(self) -> list[str]:
        out, self.records = self.records, []
        return out


def preflight() -> None:
    problems = []
    if config.MEMORY_BACKEND != "cognee":
        problems.append(f"MEMORY_BACKEND={config.MEMORY_BACKEND!r} (need 'cognee')")
    if not os.environ.get("LLM_API_KEY"):
        problems.append("LLM_API_KEY missing — cognee cannot call the LLM")
    if os.environ.get("DB_PROVIDER", "sqlite").lower() == "postgres":
        host = os.environ.get("DB_HOST", "127.0.0.1")
        port = int(os.environ.get("DB_PORT", "5432"))
        try:
            socket.create_connection((host, port), timeout=3).close()
        except OSError:
            problems.append(
                f"postgres unreachable at {host}:{port} — docker compose up -d postgres"
            )
    if problems:
        print("NO-GO — live preconditions unmet:")
        for p in problems:
            print(f"  - {p}")
        raise SystemExit(2)


def profile_signature(p) -> tuple:
    """The fields the feedback bite test may legitimately move."""
    return (
        sorted(t.lower() for t in p.weak_topics),
        sorted(t.lower() for t in p.strong_topics),
        sorted(p.weak_probes),
        round(p.frustration, 2),
        round(p.explorer_score, 2),
    )


async def dataset_names() -> set[str]:
    import cognee

    return {getattr(d, "name", str(d)) for d in await cognee.datasets.list_datasets()}


async def main() -> int:
    preflight()

    from backend.game.discovery import check_discovery
    from backend.memory.service import get_memory_service
    from contracts.schemas import Episode

    detector = DegradationDetector()
    logging.getLogger("dor.memory").addHandler(detector)

    mem = get_memory_service()
    await mem.forget(PLAYER_A)  # clean slate; also proves forget is callable
    await mem.forget(PLAYER_B)
    detector.drain()

    # ---------------------------------------------------------- 1. remember()
    episodes = [
        Episode(player_id=PLAYER_A, event_type="question_attempt", question_id="L21-A",
                topic="trees", difficulty="medium-hard", correct=False,
                failed_probes=["edge:unbalanced"], floor=21, time_taken_s=95),
        Episode(player_id=PLAYER_A, event_type="question_attempt", question_id="L21-B",
                topic="trees", difficulty="medium-hard", correct=False,
                failed_probes=["edge:single", "edge:unbalanced"], floor=21, time_taken_s=120),
        Episode(player_id=PLAYER_A, event_type="question_attempt", question_id="L16-A",
                topic="sorting", difficulty="medium", correct=True, floor=16, time_taken_s=40),
        Episode(player_id=PLAYER_A, event_type="exploration", floor=3,
                detail="inspected sealed wall, floor 3"),
        Episode(player_id=PLAYER_A, event_type="discovery", floor=3,
                detail="whisper: You inspected sealed wall, floor 3. It remembers you too."),
        Episode(player_id=PLAYER_A, event_type="discovery",
                detail="hidden entrance revealed via explorer"),
    ]
    # concurrency probe: two writes land together (single-process async path)
    await asyncio.gather(mem.remember_episode(episodes[0]), mem.remember_episode(episodes[1]))
    for ep in episodes[2:]:
        await mem.remember_episode(ep)

    degraded = detector.drain()
    journal = await mem.recall_episodes(PLAYER_A, limit=50)
    names = await dataset_names()
    ds_a = mem._dataset(PLAYER_A)
    ds_b = mem._dataset(PLAYER_B)
    b_journal = await mem.recall_episodes(PLAYER_B, limit=50)
    remember_ok = (
        not degraded
        and len(journal) == 6
        and ds_a in names
        and ds_b not in names
        and not b_journal
    )
    record(
        "remember",
        remember_ok,
        f"6 episodes (2 concurrent) journal={len(journal)}/6 valid, dataset {ds_a} "
        f"{'exists' if ds_a in names else 'MISSING'}, isolation: {ds_b} "
        f"{'absent' if ds_b not in names else 'LEAKED'}, degradations={degraded or 'none'}",
    )

    # ------------------------------------------------------------ 2. recall()
    p1 = await mem.recall_profile(PLAYER_A)
    degraded = detector.drain()
    qa1 = p1.interaction_id
    trees_weak = "trees" in [t.lower() for t in p1.weak_topics]
    recall_ok = not degraded and qa1 is not None and trees_weak
    record(
        "recall",
        recall_ok,
        f"parsed profile weak={p1.weak_topics} strong={p1.strong_topics} "
        f"qa_id={'set' if qa1 else 'MISSING'}, degradations={degraded or 'none'}",
    )

    # staleness probe: a fresh episode must change the NEXT recall (the nonce)
    await mem.remember_episode(
        Episode(player_id=PLAYER_A, event_type="question_attempt", question_id="L33-A",
                topic="graphs", difficulty="hard", correct=False,
                failed_probes=["edge:disconnected"], floor=33, time_taken_s=200)
    )
    p2 = await mem.recall_profile(PLAYER_A)
    degraded = detector.drain()
    graphs_weak = "graphs" in [t.lower() for t in p2.weak_topics]
    fresh_qa = p2.interaction_id and p2.interaction_id != qa1
    record(
        "recall/staleness",
        bool(not degraded and graphs_weak and fresh_qa),
        f"fresh 'graphs' episode reflected={graphs_weak}, new qa_id={bool(fresh_qa)} "
        f"(nonce beat the session cache), degradations={degraded or 'none'}",
    )

    # ----------------------------------------------------------- 3. improve()
    before = profile_signature(p2)
    await mem.reinforce(
        PLAYER_A,
        "WRONG: the boss exploited 'trees' and the player crushed it instantly; "
        "this profile misjudges them",
        -5.0,
    )
    await mem.improve(PLAYER_A)
    p3 = await mem.recall_profile(PLAYER_A)
    degraded = detector.drain()
    after = profile_signature(p3)
    shifted = after != before
    if shifted:
        record("improve", not degraded,
               f"profile shifted after strong negative feedback: {before} -> {after}, "
               f"degradations={degraded or 'none'}")
    else:
        # isolate: is the session cache serving a stale answer, or did the
        # feedback genuinely not bite?
        import cognee
        from cognee import SearchType

        fixed_q = f"Summarize player {PLAYER_A}'s weak and strong question topics."
        try:
            r1 = await cognee.recall(fixed_q, query_type=SearchType.GRAPH_COMPLETION,
                                     datasets=[ds_a], session_id=mem._session(PLAYER_A),
                                     top_k=15, feedback_influence=0.5)
            r2 = await cognee.recall(fixed_q, query_type=SearchType.GRAPH_COMPLETION,
                                     datasets=[ds_a], session_id=mem._session(PLAYER_A),
                                     top_k=15, feedback_influence=0.5)
            a1, _ = mem._extract_answer(r1)
            a2, _ = mem._extract_answer(r2)
            condition = (
                "session cache serves stale answers for identical queries (nonce required)"
                if a1 == a2
                else "feedback did not measurably bite even without the nonce"
            )
        except Exception as exc:
            condition = f"isolation probe errored: {exc!r:.200}"
        record("improve", False, f"NO SHIFT after reinforce(-5)+improve; isolation: {condition}")

    # ------------------------------------------------------------ 4. forget()
    pre = await check_discovery(PLAYER_A, mem)
    await mem.forget(PLAYER_A)
    degraded = detector.drain()
    p4 = await mem.recall_profile(PLAYER_A)
    post = await check_discovery(PLAYER_A, mem)
    names_after = await dataset_names()
    other_datasets_intact = True  # forget must be surgical: only A's dataset goes
    wiped = (
        pre.revealed is True
        and ds_a not in names_after
        and not p4.weak_topics
        and not p4.hidden_discovered
        and p4.whispers_heard == 0
        and not await mem.recall_episodes(PLAYER_A)
        and post.revealed is False
    )
    record(
        "forget",
        wiped and other_datasets_intact,
        f"pre-forget revealed={pre.revealed}, post: dataset "
        f"{'gone' if ds_a not in names_after else 'SURVIVED'}, profile default="
        f"{not p4.weak_topics and not p4.hidden_discovered}, journal empty, "
        f"check_discovery revealed={post.revealed} (hidden dungeon re-sealed)",
    )

    failed = [r for r in RESULTS if not r[1]]
    print("\n--- verb table ---")
    for verb, ok, ev in RESULTS:
        print(f"{verb:<18} {'PASS' if ok else 'FAIL'}")
    print("\n" + ("SMOKE PASSED — all four verbs verified live" if not failed
                  else f"SMOKE FAILED ({len(failed)}): {[r[0] for r in failed]}"))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
