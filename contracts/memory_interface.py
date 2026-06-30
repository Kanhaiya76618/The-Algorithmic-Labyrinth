"""
SHARED CONTRACT — the MemoryService interface. Frozen on Day 1.

Role B, C, D build against THIS, never against Role A's concrete code.
Role A implements it for real in backend/memory/service.py.
Until that's ready, backend/stubs/fake_memory.py implements the same
interface with canned data, so nobody is ever blocked.

Swapping fake -> real is one line in backend/deps.py.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from contracts.schemas import Episode, PlayerProfile, FeedbackSignal


class MemoryService(ABC):
    @abstractmethod
    async def remember_episode(self, episode: Episode) -> None:
        """Write one behavioral episode into the player's memory."""

    @abstractmethod
    async def recall_profile(self, player_id: str) -> PlayerProfile:
        """Read the weighted player profile. Records the interaction
        so a later reward can target the exact graph elements used."""

    @abstractmethod
    async def reinforce(self, signal: FeedbackSignal) -> None:
        """Write the game outcome back as feedback on the last read."""

    @abstractmethod
    async def improve(self, player_id: str) -> None:
        """Propagate accumulated feedback into graph edge weights."""

    @abstractmethod
    async def forget(self, player_id: str) -> None:
        """Surgically wipe this player's memory (the 'potion of forgetting')."""

    @abstractmethod
    async def get_graph(self, player_id: str) -> dict:
        """Return nodes+edges for the player-facing memory visualization."""
