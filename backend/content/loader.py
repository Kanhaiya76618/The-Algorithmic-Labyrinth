"""
Role C — loads/filters the question bank and boss dialogue.

The bank is plain DATA (JSON) on purpose: questions never go through the
Cognee graph extractor (keeps token cost down and recall sharp). Role C
edits the JSON files in data/; this loader is the only code here that
other slices call.
"""
from __future__ import annotations
import json
import random
from pathlib import Path
from contracts.schemas import Difficulty, Track, PlayerProfile

_DATA = Path(__file__).parent / "data"


def _load(name: str) -> list[dict]:
    return json.loads((_DATA / name).read_text())


_DSA = {q["id"]: q for q in _load("dsa_questions.json")}
_LOGIC = {q["id"]: q for q in _load("logic_math_questions.json")}
_ALL = {**_DSA, **_LOGIC}
_DIALOGUE = _load("boss_dialogue.json")


def get_question(qid: str) -> dict:
    return _ALL[qid]


def pick_question(difficulty: Difficulty, track: Track,
                  topic: str | None = None, exclude: set[str] | None = None) -> dict:
    pool_src = _DSA if track == Track.DSA else _LOGIC
    exclude = exclude or set()
    pool = [q for q in pool_src.values()
            if q["difficulty"] == difficulty.value and q["id"] not in exclude
            and (topic is None or q["topic"] == topic)]
    if not pool:  # graceful fallback so the game never dead-ends
        pool = [q for q in pool_src.values() if q["difficulty"] == difficulty.value]
    return random.choice(pool)


def check_answer(qid: str, answer: str) -> bool:
    return str(answer).strip().lower() == str(_ALL[qid]["answer"]).strip().lower()


def boss_line(profile: PlayerProfile) -> str:
    weak = profile.weak_topics[0] if profile.weak_topics else None
    for line in _DIALOGUE:
        if line.get("topic") == weak:
            return line["text"]
    return _DIALOGUE[0]["text"]
