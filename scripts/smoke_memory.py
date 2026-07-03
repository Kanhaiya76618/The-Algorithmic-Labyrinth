"""Go/no-go smoke test for MEMORY_BACKEND=cognee.

Prereqs: docker compose up -d postgres  ·  .env with LLM_API_KEY  ·
MEMORY_BACKEND=cognee. Run:  python3 scripts/smoke_memory.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend import config  # noqa: E402  (loads .env before cognee import)
from backend.memory.service import get_memory_service  # noqa: E402
from contracts.schemas import Episode  # noqa: E402

PLAYER = "smoke_test_hero"


def step(n: int, label: str) -> None:
    print(f"\n=== [{n}] {label} ===", flush=True)


async def main() -> int:
    mem = get_memory_service()
    ok = True

    step(1, "remember 6 episodes (2 fired CONCURRENTLY to prove the topology)")
    episodes = [
        Episode(player_id=PLAYER, event_type="question_attempt", question_id="L21-A",
                topic="trees", difficulty="medium-hard", correct=False,
                failed_probes=["edge:unbalanced"], floor=21, time_taken_s=95),
        Episode(player_id=PLAYER, event_type="question_attempt", question_id="L21-B",
                topic="trees", difficulty="medium-hard", correct=False,
                failed_probes=["edge:single", "edge:unbalanced"], floor=21, time_taken_s=120),
        Episode(player_id=PLAYER, event_type="question_attempt", question_id="L16-A",
                topic="sorting", difficulty="medium", correct=True, floor=16, time_taken_s=40),
        Episode(player_id=PLAYER, event_type="exploration", floor=3,
                detail="inspected sealed wall, floor 3"),
        Episode(player_id=PLAYER, event_type="exploration", floor=2,
                detail="revisited cleared floor 2"),
        Episode(player_id=PLAYER, event_type="question_attempt", question_id="L22-A",
                topic="trees", difficulty="medium-hard", correct=False,
                failed_probes=["edge:duplicates"], floor=22, time_taken_s=150),
    ]
    # concurrency probe: first two together (single-process async writers)
    await asyncio.gather(mem.remember_episode(episodes[0]), mem.remember_episode(episodes[1]))
    for ep in episodes[2:]:
        await mem.remember_episode(ep)
    print("remembered 6 episodes (2 concurrent) ✓")

    step(2, "recall_profile — expect 'trees' among weak_topics")
    profile = await mem.recall_profile(PLAYER)
    print(profile.model_dump_json(indent=2))
    if "trees" not in [t.lower() for t in profile.weak_topics]:
        print("!! weak topic 'trees' not detected", flush=True)
        ok = False
    if not profile.interaction_id:
        print("!! no interaction_id (session QA entry missing?)")

    step(3, "reinforce + improve")
    await mem.reinforce(PLAYER, "boss exploited the tree weakness successfully; profile accurate", 2.0)
    await mem.improve(PLAYER)
    print("reinforce + improve returned ✓")

    step(4, "recall again — profile must not degrade")
    profile2 = await mem.recall_profile(PLAYER)
    print(profile2.model_dump_json(indent=2))
    if "trees" not in [t.lower() for t in profile2.weak_topics]:
        print("!! profile degraded after reinforce/improve")
        ok = False

    step(5, "get_graph — nonempty")
    graph = await mem.get_graph(PLAYER)
    print(f"nodes={len(graph['nodes'])} edges={len(graph['edges'])}")
    if not graph["nodes"]:
        print("!! empty graph")
        ok = False

    step(6, "recall_episodes — newest first, filtered")
    eps = await mem.recall_episodes(PLAYER, event_type="exploration")
    print([e.detail for e in eps])
    if len(eps) != 2:
        ok = False

    step(7, "forget — surgical wipe, default profile after")
    await mem.forget(PLAYER)
    profile3 = await mem.recall_profile(PLAYER)
    print(profile3.model_dump_json(indent=2))
    if profile3.weak_topics or profile3.hidden_discovered or profile3.whispers_heard:
        print("!! forget did not clear the profile")
        ok = False
    if await mem.recall_episodes(PLAYER):
        print("!! journal survived forget")
        ok = False

    print("\n" + ("SMOKE PASSED — flip MEMORY_BACKEND=cognee" if ok else "SMOKE FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
