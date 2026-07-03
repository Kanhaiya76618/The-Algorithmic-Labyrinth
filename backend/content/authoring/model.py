"""Spec dataclasses + level-map rules shared by the spec modules and build.py."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional
import random


@dataclass
class T:
    """One test case. Either a literal stdin string, or gen(rng) -> stdin."""

    stdin: Optional[str] = None
    gen: Optional[Callable[[random.Random], str]] = None
    visible: bool = False
    probe: Optional[str] = None

    def realize(self, seed: str) -> str:
        if self.stdin is not None:
            return self.stdin
        rng = random.Random(seed)
        return self.gen(rng)


@dataclass
class Q:
    qid: str
    level: int
    topic: str
    title: str
    prompt: str
    solution: str  # standalone python3 source reading stdin, writing stdout
    tests: list[T] = field(default_factory=list)
    is_boss: bool = False
    time_limit_s: int = 3
    memory_limit_mb: int = 256


@dataclass
class Puzzle:
    """Hidden-dungeon short-answer puzzle. No code execution."""

    qid: str
    level: int  # 1..10 within the hidden realm
    topic: str
    title: str
    prompt: str
    answer: str


# ---- Level map (source of truth: hackathon task brief) ----

BOSS_QUESTION_COUNTS = {5: 1, 10: 1, 15: 1, 20: 1, 25: 1, 30: 2, 35: 2, 40: 2, 45: 3, 50: 3}


def difficulty_for_level(level: int) -> str:
    if level <= 4:
        return "easy"
    if level <= 9:
        return "easy-medium"
    if level == 10:
        return "medium"
    if level <= 19:
        return "medium"
    if level == 20:
        return "medium-hard"
    if level <= 24:
        return "medium-hard"
    if level == 25:
        return "hard"
    if level <= 29:
        return "medium-hard"
    if level <= 44:
        return "hard"
    if level == 45:
        return "very-hard"
    if level <= 49:
        return "hard"
    return "hardest"


def test_count_range(level: int) -> tuple[int, int, int, int]:
    """(min_total, max_total, min_visible, max_visible) for a level."""
    if level <= 10:
        return (3, 4, 1, 2)
    if level <= 25:
        return (5, 7, 2, 2)
    if level <= 40:
        return (8, 10, 2, 3)
    return (10, 12, 3, 3)


TOPIC_TAXONOMY = [
    "arrays",
    "strings",
    "hashing",
    "two-pointers",
    "sliding-window",
    "stacks-queues",
    "linked-lists",
    "recursion",
    "sorting",
    "binary-search",
    "trees",
    "heaps",
    "graphs",
    "dynamic-programming",
    "greedy",
    "bit-manipulation",
    "math",
    "logic-puzzle",
]

PROBE_LABELS = [
    "edge:empty",
    "edge:single",
    "edge:duplicates",
    "edge:all-equal",
    "edge:sorted",
    "edge:reverse-sorted",
    "edge:negative",
    "edge:zero",
    "edge:max-bounds",
    "edge:overflow",
    "edge:no-solution",
    "edge:cycle",
    "edge:disconnected",
    "edge:unbalanced",
    "perf:large_n",
    "adversarial:worst-case",
]
