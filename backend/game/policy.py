"""
Role B — the thin action-selection policy.

This is the ONLY 'RL-ish' code outside Cognee. It reads the weighted
profile (from recall) and picks the next topic/difficulty. Most of the
intelligence lives in the memory graph; this is just the selector.
"""
from __future__ import annotations
from contracts.schemas import PlayerProfile, Difficulty


def choose_topic(profile: PlayerProfile, default: str) -> str:
    # bias toward the player's weakest topic on boss floors
    return profile.weak_topics[0] if profile.weak_topics else default


def damp_for_frustration(base: Difficulty, profile: PlayerProfile) -> Difficulty:
    if profile.frustration >= 0.6 and base == Difficulty.HARD:
        return Difficulty.MEDIUM
    return base
