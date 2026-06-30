"""Role B — floor -> difficulty/boss gating, hidden-dungeon unlock."""
from __future__ import annotations
from contracts.schemas import Difficulty


def difficulty_for_floor(floor: int) -> Difficulty:
    if floor <= 3:
        return Difficulty.EASY
    if floor <= 7:
        return Difficulty.MEDIUM
    return Difficulty.HARD


def is_boss_floor(floor: int) -> bool:
    # mini-boss at end of each mid stage; final boss deep
    return floor in (7,) or floor >= 10
