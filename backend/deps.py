"""
Role A — dependency wiring. THE SWAP POINT.

This is the only place that decides whether the app uses the real Cognee
service or the stub. Roles B/C/D call `get_memory()` and never care which
one they got. Changing fake -> real is a one-line env flip (MEMORY_BACKEND).
"""
from __future__ import annotations
from functools import lru_cache
from backend.config import settings
from contracts.memory_interface import MemoryService


@lru_cache
def get_memory() -> MemoryService:
    if settings.MEMORY_BACKEND == "cognee":
        from backend.memory.service import CogneeMemoryService
        return CogneeMemoryService()
    from backend.stubs.fake_memory import FakeMemoryService
    return FakeMemoryService()
