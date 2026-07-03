from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Optional

from contracts.schemas import Challenge, Difficulty

DATA_DIR = Path(__file__).resolve().parent / "data"
_questions_cache: Optional[list[Challenge]] = None
_questions_by_id: dict[str, Challenge] = {}
_questions_by_topic: dict[str, list[Challenge]] = defaultdict(list)
_questions_by_difficulty: dict[str, list[Challenge]] = defaultdict(list)


def _parse_challenge(payload: dict) -> Challenge:
    if hasattr(Challenge, "model_validate"):
        return Challenge.model_validate(payload)
    return Challenge.parse_obj(payload)


def _normalize_difficulty(difficulty: str | Difficulty) -> Difficulty:
    if isinstance(difficulty, Difficulty):
        return difficulty

    try:
        return Difficulty(difficulty.lower())
    except ValueError as exc:
        raise ValueError(f"Unsupported difficulty: {difficulty}") from exc


def _build_indexes(questions: list[Challenge]) -> None:
    global _questions_by_id, _questions_by_topic, _questions_by_difficulty

    _questions_by_id = {question.question_id: question for question in questions}
    _questions_by_topic = defaultdict(list)
    _questions_by_difficulty = defaultdict(list)

    for question in questions:
        _questions_by_topic[question.topic.lower()].append(question)
        _questions_by_difficulty[question.difficulty.value].append(question)


def load_questions() -> list[Challenge]:
    """Load all challenge JSON files from the data folder and cache them in memory."""
    global _questions_cache

    if _questions_cache is not None:
        return list(_questions_cache)

    questions: list[Challenge] = []

    for json_path in sorted(DATA_DIR.glob("*.json")):
        with json_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        if not isinstance(payload, list):
            continue

        for item in payload:
            if not isinstance(item, dict):
                raise ValueError(f"Expected each entry in {json_path.name} to be an object")
            questions.append(_parse_challenge(item))

    _questions_cache = questions
    _build_indexes(questions)
    return list(_questions_cache)


def reload_questions() -> list[Challenge]:
    """Reload questions from disk and refresh the in-memory indexes."""
    global _questions_cache
    _questions_cache = None
    return load_questions()


def get_all_questions() -> list[Challenge]:
    """Return all loaded questions as a fresh list."""
    return load_questions()


def get_question_by_id(question_id: str) -> Optional[Challenge]:
    """Return the question matching the supplied question_id."""
    load_questions()
    return _questions_by_id.get(question_id)


def get_random_question() -> Optional[Challenge]:
    """Return a single random question from the loaded set."""
    questions = load_questions()
    if not questions:
        return None
    return random.choice(questions)


def get_questions_by_topic(topic: str) -> list[Challenge]:
    """Return all questions belonging to the requested topic."""
    load_questions()
    normalized_topic = topic.strip().lower()
    return list(_questions_by_topic.get(normalized_topic, []))


def get_questions_by_difficulty(difficulty: str | Difficulty) -> list[Challenge]:
    """Return all questions with the requested difficulty."""
    load_questions()
    normalized_difficulty = _normalize_difficulty(difficulty)
    return list(_questions_by_difficulty.get(normalized_difficulty.value, []))


__all__ = [
    "load_questions",
    "reload_questions",
    "get_all_questions",
    "get_question_by_id",
    "get_random_question",
    "get_questions_by_topic",
    "get_questions_by_difficulty",
]
