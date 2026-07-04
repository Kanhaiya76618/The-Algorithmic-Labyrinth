"""In-memory MemoryService fallback (MEMORY_BACKEND=fake or Role A's Cognee
service unavailable). Everything is DERIVED from stored episodes — same
contract the real implementation must honour, so discovery behaves
identically, just without persistence across process restarts.
"""

from __future__ import annotations

import uuid
from collections import defaultdict
from typing import Optional

from contracts.memory_interface import MemoryService
from contracts.schemas import Episode, PlayerProfile

_WHISPER_PREFIX = "whisper:"
_REVEAL_PREFIX = "hidden entrance revealed"


class FakeMemoryService(MemoryService):
    def __init__(self) -> None:
        self._episodes: dict[str, list[Episode]] = defaultdict(list)
        self._feedback: dict[str, list[tuple[str, float]]] = defaultdict(list)

    async def remember_episode(self, episode: Episode) -> None:
        self._episodes[episode.player_id].append(episode)

    async def recall_profile(self, player_id: str) -> PlayerProfile:
        eps = self._episodes.get(player_id, [])
        attempts = [e for e in eps if e.event_type == "question_attempt"]
        explorations = [e for e in eps if e.event_type == "exploration"]
        discoveries = [e for e in eps if e.event_type == "discovery"]

        by_topic: dict[str, list[bool]] = defaultdict(list)
        for e in attempts:
            if e.topic and e.correct is not None:
                by_topic[e.topic].append(e.correct)
        weak = [t for t, r in by_topic.items() if r.count(False) > r.count(True)]
        strong = [t for t, r in by_topic.items() if r.count(True) > r.count(False) and len(r) >= 2]

        probe_counts: dict[str, int] = defaultdict(int)
        for e in attempts:
            for p in e.failed_probes:
                probe_counts[p] += 1
        weak_probes = sorted(probe_counts, key=lambda p: -probe_counts[p])[:5]

        recent = attempts[-6:]
        frustration = (sum(1 for e in recent if e.correct is False) / len(recent)) if recent else 0.0

        # explorer_score: breadth of distinct exploration signals, saturating at 8
        distinct = {(e.detail or "", e.floor) for e in explorations}
        explorer_score = min(1.0, len(distinct) / 8)

        whispers = sum(1 for e in discoveries if (e.detail or "").startswith(_WHISPER_PREFIX))
        discovered = any((e.detail or "").startswith(_REVEAL_PREFIX) for e in discoveries)

        return PlayerProfile(
            player_id=player_id,
            weak_topics=weak,
            strong_topics=strong,
            weak_probes=weak_probes,
            frustration=round(frustration, 2),
            explorer_score=round(explorer_score, 2),
            whispers_heard=whispers,
            hidden_discovered=discovered,
            interaction_id=uuid.uuid4().hex,
        )

    async def recall_episodes(
        self, player_id: str, event_type: Optional[str] = None, limit: int = 20
    ) -> list[Episode]:
        eps = self._episodes.get(player_id, [])
        if event_type:
            eps = [e for e in eps if e.event_type == event_type]
        return list(reversed(eps[-limit:]))

    async def reinforce(self, player_id: str, outcome_text: str, score: float) -> None:
        self._feedback[player_id].append((outcome_text, score))

    async def improve(self, player_id: str) -> None:
        return None  # nothing to consolidate in the stub

    async def forget(self, player_id: str) -> None:
        # Wipes everything — including discovery episodes, so the hidden
        # entrance re-seals on the next check_discovery, purely by derivation.
        self._episodes.pop(player_id, None)
        self._feedback.pop(player_id, None)

    async def get_graph(self, player_id: str) -> dict:
        eps = self._episodes.get(player_id, [])
        topics: dict[str, dict] = {}
        for e in eps:
            if e.event_type == "question_attempt" and e.topic:
                node = topics.setdefault(e.topic, {"id": e.topic, "attempts": 0, "fails": 0})
                node["attempts"] += 1
                node["fails"] += 0 if e.correct else 1
        nodes = [{"id": player_id, "kind": "player"}] + [
            {**t, "kind": "topic"} for t in topics.values()
        ]
        edges = [
            {"from": player_id, "to": t["id"], "weight": min(1.0, t["attempts"] / 5)}
            for t in topics.values()
        ]
        return {"nodes": nodes, "edges": edges}
