"""
Role A — the real Cognee 1.x MemoryService.

This is the technical core both winning criteria hinge on. Everything
Cognee-specific lives in this module + feedback.py, so version churn is
contained. Roles B/C/D never import this directly — they get it via
backend.deps.get_memory().
"""
from __future__ import annotations
from contracts.memory_interface import MemoryService
from contracts.schemas import Episode, PlayerProfile, FeedbackSignal
from backend.memory.schema import episode_to_text
from backend.memory import feedback


class CogneeMemoryService(MemoryService):
    def _dataset(self, player_id: str) -> str:
        return f"player_{player_id}"

    async def remember_episode(self, episode: Episode) -> None:
        import cognee
        await cognee.remember(
            episode_to_text(episode),
            dataset=self._dataset(episode.player_id),
        )

    async def recall_profile(self, player_id: str) -> PlayerProfile:
        q = (f"For player {player_id}: list weakest topics, strongest topics, "
             f"overall pace, and whether they seem frustrated.")
        _result = await feedback.recall_with_interaction(q)
        # TODO(Role A): parse _result into the structured profile below.
        # Until parsing is done this returns an empty-but-valid profile so
        # Role B can integrate against the real endpoint immediately.
        return PlayerProfile(player_id=player_id, interaction_id="last")

    async def reinforce(self, signal: FeedbackSignal) -> None:
        await feedback.apply_reward(signal.outcome_text, score=signal.score)

    async def improve(self, player_id: str) -> None:
        import cognee
        await cognee.improve()

    async def forget(self, player_id: str) -> None:
        import cognee
        await cognee.forget(dataset=self._dataset(player_id))

    async def get_graph(self, player_id: str) -> dict:
        # TODO(Role A): return real nodes/edges for the memory view.
        return {"nodes": [], "edges": []}
