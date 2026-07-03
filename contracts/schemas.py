"""Shared API contracts. FROZEN — changes require team approval.

Challenge is PUBLIC-ONLY by design: it never carries hidden test cases,
answers, or probe labels. The full question record lives inside
backend/content/loader.py; the game layer fetches hidden tests from the
loader by question_id when grading — never from a Challenge object.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class Difficulty(str, Enum):
    EASY = "easy"
    EASY_MEDIUM = "easy-medium"
    MEDIUM = "medium"
    MEDIUM_HARD = "medium-hard"
    HARD = "hard"
    VERY_HARD = "very-hard"
    HARDEST = "hardest"
    BOSS_TIER = "boss-tier"  # hidden-dungeon puzzles


class VisibleTest(BaseModel):
    """A sample test safe to show the player. Hidden tests and their probe
    labels never leave the loader."""

    stdin: str
    expected_stdout: str


class Challenge(BaseModel):
    """Public view of a question — everything here may reach the client."""

    question_id: str
    realm: str = "main"  # "main" | "hidden"
    level: int
    topic: str
    difficulty: Difficulty
    is_boss: bool = False
    question_type: str = "code"  # "code" | "short_answer"
    title: str
    prompt: str
    starter_code: dict[str, str] | None = None  # keyed by language
    visible_tests: list[VisibleTest] = Field(default_factory=list)
    time_limit_s: int = 3
    memory_limit_mb: int = 256


class SubmitAnswerRequest(BaseModel):
    run_id: str
    question_id: str
    answer: str | None = None  # short_answer path
    code: str | None = None
    language: str = "python3"


class Episode(BaseModel):
    """One memory episode written to the player's graph via remember()."""

    player_id: str
    event_type: str = "question_attempt"  # "question_attempt" | "exploration" | "discovery"
    question_id: str | None = None
    topic: str | None = None
    difficulty: str | None = None
    correct: bool | None = None
    time_taken_s: float | None = None
    failed_probes: list[str] = Field(default_factory=list)
    hints_used: int = 0
    retries: int = 0
    detail: str | None = None  # e.g. "inspected sealed wall, floor 3"
    floor: int | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PlayerProfile(BaseModel):
    """Aggregate view recalled from the player's graph (memory layer = Role A)."""

    player_id: str
    weak_topics: list[str] = Field(default_factory=list)
    strong_topics: list[str] = Field(default_factory=list)
    weak_probes: list[str] = Field(default_factory=list)
    frustration: float = 0.0  # recall-derived
    explorer_score: float = 0.0  # 0..1
    whispers_heard: int = 0
    hidden_discovered: bool = False
    interaction_id: str | None = None  # handle for feedback targeting the last recall


class DiscoveryState(BaseModel):
    revealed: bool = False
    via: str | None = None  # "explorer" | "mercy"
    whispers: list[str] = Field(default_factory=list)


class AnswerResult(BaseModel):
    correct: bool
    tests_passed: int = 0
    tests_total: int = 0
    verdict: str = "accepted"  # accepted|wrong_answer|timeout|compile_error|runtime_error|judge_offline
    failed_probes: list[str] = Field(default_factory=list)  # memory fuel
    floor_cleared: bool = False
    run_complete: bool = False
    boss_triggered: bool = False
    message: str | None = None
