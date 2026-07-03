"""Question bank loader.

Two-tier design (per contract decision):
- INTERNAL: full question records — hidden test cases, probe labels, answers —
  live only in this module as _QuestionRecord. The game layer fetches them by
  question_id via get_hidden_tests()/get_expected_answer() when grading.
- PUBLIC: everything returned as contracts.schemas.Challenge is a public
  projection (visible tests only, no answers, no probes) and is safe to send
  to any client.
"""

from __future__ import annotations

import json
import random
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from contracts.schemas import Challenge, Difficulty, VisibleTest

DATA_DIR = Path(__file__).resolve().parent / "data"

# Boss levels and how many questions each serves (source of truth: level map).
BOSS_QUESTION_COUNTS = {5: 1, 10: 1, 15: 1, 20: 1, 25: 1, 30: 2, 35: 2, 40: 2, 45: 3, 50: 3}
MAX_LEVEL = 50


@dataclass
class _QuestionRecord:
    """Full internal record. NEVER serialize this to a client."""

    question_id: str
    realm: str
    level: int
    topic: str
    difficulty: str
    is_boss: bool
    question_type: str
    title: str
    prompt: str
    starter_code: Optional[dict]
    test_cases: list[dict] = field(default_factory=list)  # includes hidden + probes
    time_limit_s: int = 3
    memory_limit_mb: int = 256
    answer: Optional[str] = None


_records: Optional[list[_QuestionRecord]] = None
_by_id: dict[str, _QuestionRecord] = {}
_by_level: dict[int, list[_QuestionRecord]] = defaultdict(list)
_hidden_by_level: dict[int, list[_QuestionRecord]] = defaultdict(list)
_by_topic: dict[str, list[_QuestionRecord]] = defaultdict(list)
_by_difficulty: dict[str, list[_QuestionRecord]] = defaultdict(list)
_dialogue: Optional[dict] = None


def _load() -> list[_QuestionRecord]:
    global _records
    if _records is not None:
        return _records

    records: list[_QuestionRecord] = []
    for json_path in sorted(DATA_DIR.glob("*.json")):
        with json_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, list):  # boss_dialogue.json etc.
            continue
        for item in payload:
            if not isinstance(item, dict):
                raise ValueError(f"Expected each entry in {json_path.name} to be an object")
            records.append(_QuestionRecord(**item))

    _by_id.clear()
    _by_level.clear()
    _hidden_by_level.clear()
    _by_topic.clear()
    _by_difficulty.clear()
    for rec in records:
        _by_id[rec.question_id] = rec
        (_by_level if rec.realm == "main" else _hidden_by_level)[rec.level].append(rec)
        _by_topic[rec.topic.lower()].append(rec)
        _by_difficulty[rec.difficulty].append(rec)
    for pool in _by_level.values():
        pool.sort(key=lambda r: r.question_id)

    _records = records
    return records


def reload_questions() -> int:
    """Drop caches and reload from disk. Returns the number of questions."""
    global _records, _dialogue
    _records = None
    _dialogue = None
    return len(_load())


def _to_challenge(rec: _QuestionRecord, language: Optional[str] = None) -> Challenge:
    """Public projection: visible tests only, no probes, no answers."""
    starter = rec.starter_code
    if starter and language:
        code = starter.get(language)
        starter = {language: code} if code is not None else None
    return Challenge(
        question_id=rec.question_id,
        realm=rec.realm,
        level=rec.level,
        topic=rec.topic,
        difficulty=Difficulty(rec.difficulty),
        is_boss=rec.is_boss,
        question_type=rec.question_type,
        title=rec.title,
        prompt=rec.prompt,
        starter_code=starter,
        visible_tests=[
            VisibleTest(stdin=t["stdin"], expected_stdout=t["expected_stdout"])
            for t in rec.test_cases
            if t.get("visible")
        ],
        time_limit_s=rec.time_limit_s,
        memory_limit_mb=rec.memory_limit_mb,
    )


# ---------------------------------------------------------------- level serving

def get_challenge_for_level(
    level: int,
    language: Optional[str] = None,
    exclude_ids: Optional[set[str]] = None,
) -> Optional[Challenge]:
    """One question for a non-boss floor. exclude_ids skips variants the player
    already saw this run; if that exhausts the pool we fall back to the full
    pool rather than failing the floor."""
    _load()
    pool = _by_level.get(level, [])
    if not pool:
        return None
    fresh = [r for r in pool if not exclude_ids or r.question_id not in exclude_ids]
    return _to_challenge(random.choice(fresh or pool), language)


def get_boss_challenges_for_level(level: int, language: Optional[str] = None) -> list[Challenge]:
    """All questions of a boss floor, in stable order. Enforces the level map's
    boss question count (truncates extras, logs nothing — data is validated at
    build time)."""
    _load()
    if level not in BOSS_QUESTION_COUNTS:
        return []
    pool = _by_level.get(level, [])
    return [_to_challenge(r, language) for r in pool[: BOSS_QUESTION_COUNTS[level]]]


def get_hidden_dungeon_challenge(hidden_level: int) -> Optional[Challenge]:
    _load()
    pool = _hidden_by_level.get(hidden_level, [])
    return _to_challenge(random.choice(pool)) if pool else None


# ------------------------------------------------- grading access (game layer)

def get_hidden_tests(question_id: str) -> list[dict]:
    """FULL test list (visible + hidden, with probe labels) for the judge.
    Game layer only — never expose through a router."""
    _load()
    rec = _by_id.get(question_id)
    return list(rec.test_cases) if rec else []


def get_expected_answer(question_id: str) -> Optional[str]:
    """Expected string for short_answer questions. Game layer only."""
    _load()
    rec = _by_id.get(question_id)
    return rec.answer if rec else None


def get_time_limit(question_id: str) -> int:
    _load()
    rec = _by_id.get(question_id)
    return rec.time_limit_s if rec else 3


# ------------------------------------------------------ browsing API (public)

def load_questions() -> list[Challenge]:
    return [_to_challenge(r) for r in _load()]


def get_all_questions() -> list[Challenge]:
    return load_questions()


def get_question_by_id(question_id: str) -> Optional[Challenge]:
    _load()
    rec = _by_id.get(question_id)
    return _to_challenge(rec) if rec else None


def get_random_question() -> Optional[Challenge]:
    records = _load()
    return _to_challenge(random.choice(records)) if records else None


def get_questions_by_topic(topic: str) -> list[Challenge]:
    _load()
    return [_to_challenge(r) for r in _by_topic.get(topic.strip().lower(), [])]


def get_questions_by_difficulty(difficulty: str | Difficulty) -> list[Challenge]:
    _load()
    value = difficulty.value if isinstance(difficulty, Difficulty) else Difficulty(difficulty.lower()).value
    return [_to_challenge(r) for r in _by_difficulty.get(value, [])]


# ------------------------------------------------------------- boss dialogue

def _load_dialogue() -> dict:
    global _dialogue
    if _dialogue is None:
        path = DATA_DIR / "boss_dialogue.json"
        _dialogue = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    return _dialogue


def get_boss_taunt(
    topic: Optional[str] = None,
    probe: Optional[str] = None,
    rng: Optional[random.Random] = None,
) -> str:
    """Pick the taunt that matches the player's recalled weakness: a probe-keyed
    line beats a topic line beats a generic one. This is where the memory layer
    becomes visible to the player."""
    dialogue = _load_dialogue()
    pick = (rng or random).choice
    for pool in (
        dialogue.get("by_probe", {}).get(probe or ""),
        dialogue.get("by_topic", {}).get((topic or "").lower()),
        dialogue.get("generic"),
    ):
        if isinstance(pool, str):
            return pool
        if pool:
            return pick(pool)
    return "The Boss watches. It remembers."


__all__ = [
    "BOSS_QUESTION_COUNTS",
    "MAX_LEVEL",
    "reload_questions",
    "get_challenge_for_level",
    "get_boss_challenges_for_level",
    "get_hidden_dungeon_challenge",
    "get_hidden_tests",
    "get_expected_answer",
    "get_time_limit",
    "load_questions",
    "get_all_questions",
    "get_question_by_id",
    "get_random_question",
    "get_questions_by_topic",
    "get_questions_by_difficulty",
    "get_boss_taunt",
]
