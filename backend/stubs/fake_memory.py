"""
Shared stub — implements MemoryService with canned data so Roles B/C/D
can run the whole app on Day 1 without any Cognee key or setup.

DO NOT add game logic here. When Role A's CogneeMemoryService is ready,
set MEMORY_BACKEND=cognee and this file is simply no longer loaded.
"""
from __future__ import annotations
from collections import defaultdict
from contracts.memory_interface import MemoryService
from contracts.schemas import Episode, PlayerProfile, FeedbackSignal


class FakeMemoryService(MemoryService):
    def __init__(self) -> None:
        self._episodes: dict[str, list[Episode]] = defaultdict(list)

    async def remember_episode(self, episode: Episode) -> None:
        self._episodes[episode.player_id].append(episode)

    async def recall_profile(self, player_id: str) -> PlayerProfile:
        eps = self._episodes[player_id]
        wrong = [e.topic for e in eps if not e.correct]
        right = [e.topic for e in eps if e.correct]
        return PlayerProfile(
            player_id=player_id,
            weak_topics=sorted(set(wrong)),
            strong_topics=sorted(set(right) - set(wrong)),
            pace="steady",
            frustration=min(1.0, len(wrong) * 0.2),
            interaction_id="fake",
        )

    async def reinforce(self, signal: FeedbackSignal) -> None:
        pass

    async def improve(self, player_id: str) -> None:
        pass

    async def forget(self, player_id: str) -> None:
        self._episodes.pop(player_id, None)

    async def get_graph(self, player_id: str) -> dict:
        eps = self._episodes[player_id]
        nodes = [{"id": player_id, "label": "player"}]
        edges = []
        for t in sorted({e.topic for e in eps}):
            fails = sum(1 for e in eps if e.topic == t and not e.correct)
            nodes.append({"id": t, "label": t})
            edges.append({"from": player_id, "to": t, "weight": 1 + fails})
        return {"nodes": nodes, "edges": edges}
