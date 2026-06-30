"""
SHARED CONTRACT — frozen on Day 1. Edit only in a team huddle.

These Pydantic models are the API contract between all four slices.
Everyone imports from here; nobody redefines these shapes locally.
If a field must change, announce it, change it ONCE here, and let the
type checker show each role exactly what to update in their own files.
"""
from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Track(str, Enum):
    DSA = "dsa"
    LOGIC_MATH = "logic_math"   # the hidden dungeon


# ---- what the memory layer stores (Role A) ----
class Episode(BaseModel):
    """One compact behavioral record written after every attempt."""
    player_id: str
    question_id: str
    topic: str                       # e.g. "dynamic_programming"
    track: Track = Track.DSA
    difficulty: Difficulty
    correct: bool
    time_taken_s: float
    hints_used: int = 0
    retries: int = 0
    pattern: Optional[str] = None     # e.g. "two_pointer_instinct", "panicked_timer"


# ---- what recall() gives back (Role A -> Role B) ----
class PlayerProfile(BaseModel):
    player_id: str
    weak_topics: list[str] = Field(default_factory=list)
    strong_topics: list[str] = Field(default_factory=list)
    pace: str = "unknown"             # "fast" | "steady" | "slow"
    frustration: float = 0.0          # 0..1, drives difficulty damping
    interaction_id: Optional[str] = None   # handle so a reward can target this read


# ---- game flow (Role B <-> Role D) ----
class StartGameRequest(BaseModel):
    player_id: str


class StartGameResponse(BaseModel):
    player_id: str
    floor: int = 1


class Challenge(BaseModel):
    question_id: str
    prompt: str
    topic: str
    track: Track
    difficulty: Difficulty
    floor: int
    is_boss: bool = False
    boss_dialogue: Optional[str] = None


class SubmitAnswerRequest(BaseModel):
    player_id: str
    question_id: str
    answer: str
    time_taken_s: float
    hints_used: int = 0
    retries: int = 0


class AnswerResult(BaseModel):
    correct: bool
    advanced: bool                    # did the player clear the floor/gate?
    next_floor: int
    message: str = ""


# ---- the reward signal (Role B -> Role A) ----
class FeedbackSignal(BaseModel):
    player_id: str
    outcome_text: str                 # natural-language reward, e.g. "cleared DP boss, no hints"
    score: int = 0                    # -5..+5
    interaction_id: Optional[str] = None
