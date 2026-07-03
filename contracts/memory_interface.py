"""Abstract memory service. FROZEN — changes require team approval.

Role A implements this against Cognee (remember/recall/improve/forget +
native feedback). backend/stubs/fake_memory.py is the in-memory fallback.
The discovery engine calls only the first three methods; the rest fix the
implementation target for Role A.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from contracts.schemas import Episode, PlayerProfile


class MemoryService(ABC):
    @abstractmethod
    async def remember_episode(self, episode: Episode) -> None:
        """Write one episode to the player's graph."""

    @abstractmethod
    async def recall_profile(self, player_id: str) -> PlayerProfile:
        """Aggregate profile recalled from the graph. Sets interaction_id so
        reinforce() can target this recall's graph elements."""

    @abstractmethod
    async def recall_episodes(
        self, player_id: str, event_type: Optional[str] = None, limit: int = 20
    ) -> list[Episode]:
        """Most-recent-first episodes, optionally filtered by event_type."""

    @abstractmethod
    async def reinforce(self, player_id: str, outcome_text: str, score: float) -> None:
        """Feedback on the last recall (Cognee native feedback loop)."""

    @abstractmethod
    async def improve(self, player_id: str) -> None:
        """Consolidate/re-derive the player's graph."""

    @abstractmethod
    async def forget(self, player_id: str) -> None:
        """Wipe the player's dataset. Discovery state derives from the graph,
        so forgetting also re-seals the hidden dungeon — by derivation, not
        by special-casing."""

    @abstractmethod
    async def get_graph(self, player_id: str) -> dict:
        """Nodes/edges view for the frontend memory graph."""
