"""Memory service dependency for the game layer.

Prefers Role A's Cognee-backed implementation (backend.memory.service);
falls back to the in-memory stub when it is absent, empty, or
MEMORY_BACKEND=fake. Discovery must never crash a floor transition because
the memory backend is down — callers get *some* MemoryService.
"""

from __future__ import annotations

import os

from contracts.memory_interface import MemoryService
from backend.stubs.fake_memory import FakeMemoryService

_instance: MemoryService | None = None


def get_memory() -> MemoryService:
    global _instance
    if _instance is not None:
        return _instance

    if os.environ.get("MEMORY_BACKEND", "").lower() != "fake":
        try:
            from backend.memory.service import get_memory_service  # Role A

            _instance = get_memory_service()
        except (ImportError, AttributeError):
            _instance = None
    if _instance is None:
        _instance = FakeMemoryService()
    return _instance
