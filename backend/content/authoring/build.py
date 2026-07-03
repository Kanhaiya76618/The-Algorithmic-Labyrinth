"""Build data/*.json from the spec modules.

Every expected_stdout is produced by EXECUTING the reference solution against
the test stdin, so the bank can never ship a wrong answer key. Run from the
repo root:

    python3 backend/content/authoring/build.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from model import (  # noqa: E402
    BOSS_QUESTION_COUNTS,
    PROBE_LABELS,
    TOPIC_TAXONOMY,
    Puzzle,
    Q,
    difficulty_for_level,
    test_count_range,
)
from templates import STARTER_CODE  # noqa: E402
from specs import ALL_QUESTIONS, HIDDEN_PUZZLES  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

BAND_FILES = {
    "questions_l01_l10.json": range(1, 11),
    "questions_l11_l25.json": range(11, 26),
    "questions_l26_l40.json": range(26, 41),
    "questions_l41_l50.json": range(41, 51),
}


def run_solution(source: str, stdin: str, timeout: int = 60) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as handle:
        handle.write(source)
        path = handle.name
    try:
        proc = subprocess.run(
            [sys.executable, path],
            input=stdin,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    finally:
        Path(path).unlink(missing_ok=True)
    if proc.returncode != 0:
        raise RuntimeError(f"reference solution failed (rc={proc.returncode}):\n{proc.stderr[:2000]}")
    return proc.stdout.strip()


def validate(questions: list[Q]) -> list[str]:
    errors: list[str] = []
    ids = Counter(q.qid for q in questions)
    for qid, count in ids.items():
        if count > 1:
            errors.append(f"duplicate qid {qid}")

    by_level: dict[int, list[Q]] = {}
    for q in questions:
        by_level.setdefault(q.level, []).append(q)
        if q.topic not in TOPIC_TAXONOMY:
            errors.append(f"{q.qid}: topic {q.topic!r} not in taxonomy")
        if q.is_boss != (q.level in BOSS_QUESTION_COUNTS):
            errors.append(f"{q.qid}: is_boss={q.is_boss} inconsistent with level {q.level}")

        lo, hi, vlo, vhi = test_count_range(q.level)
        total = len(q.tests)
        visible = sum(1 for t in q.tests if t.visible)
        if not lo <= total <= hi:
            errors.append(f"{q.qid}: {total} tests, expected {lo}-{hi}")
        if not vlo <= visible <= vhi:
            errors.append(f"{q.qid}: {visible} visible tests, expected {vlo}-{vhi}")
        for i, t in enumerate(q.tests):
            if t.probe is not None and t.probe not in PROBE_LABELS:
                errors.append(f"{q.qid} test {i}: unknown probe {t.probe!r}")
            if t.probe is not None and t.visible:
                errors.append(f"{q.qid} test {i}: probes belong on hidden tests only")

    for level in range(1, 51):
        pool = by_level.get(level, [])
        if level in BOSS_QUESTION_COUNTS:
            want = BOSS_QUESTION_COUNTS[level]
            if len(pool) != want:
                errors.append(f"level {level}: boss needs exactly {want} questions, has {len(pool)}")
        else:
            if not 2 <= len(pool) <= 3:
                errors.append(f"level {level}: needs 2-3 variants, has {len(pool)}")
    return errors


def question_payload(q: Q) -> dict:
    test_cases = []
    for i, t in enumerate(q.tests):
        stdin = t.realize(seed=f"{q.qid}#{i}")
        expected = run_solution(q.solution, stdin)
        if expected == "":
            raise RuntimeError(f"{q.qid} test {i}: reference produced empty output")
        test_cases.append(
            {
                "stdin": stdin,
                "expected_stdout": expected,
                "visible": t.visible,
                "probe": t.probe,
            }
        )
    return {
        "question_id": q.qid,
        "realm": "main",
        "level": q.level,
        "topic": q.topic,
        "difficulty": difficulty_for_level(q.level),
        "is_boss": q.is_boss,
        "question_type": "code",
        "title": q.title,
        "prompt": q.prompt.strip(),
        "starter_code": STARTER_CODE,
        "test_cases": test_cases,
        "time_limit_s": q.time_limit_s,
        "memory_limit_mb": q.memory_limit_mb,
        "answer": None,
    }


def puzzle_payload(p: Puzzle) -> dict:
    return {
        "question_id": p.qid,
        "realm": "hidden",
        "level": p.level,
        "topic": p.topic,
        "difficulty": "boss-tier",
        "is_boss": True,
        "question_type": "short_answer",
        "title": p.title,
        "prompt": p.prompt.strip(),
        "starter_code": None,
        "test_cases": [],
        "time_limit_s": 0,
        "memory_limit_mb": 0,
        "answer": p.answer,
    }


def main() -> int:
    errors = validate(ALL_QUESTIONS)
    hidden_levels = sorted(p.level for p in HIDDEN_PUZZLES)
    if hidden_levels != list(range(1, 11)):
        errors.append(f"hidden dungeon must be levels 1-10, got {hidden_levels}")
    if errors:
        print("SPEC ERRORS:")
        for e in errors:
            print(f"  - {e}")
        return 1

    DATA_DIR.mkdir(exist_ok=True)
    for filename, levels in BAND_FILES.items():
        band = [question_payload(q) for q in ALL_QUESTIONS if q.level in levels]
        band.sort(key=lambda item: (item["level"], item["question_id"]))
        out = DATA_DIR / filename
        out.write_text(json.dumps(band, indent=2) + "\n", encoding="utf-8")
        tests = sum(len(item["test_cases"]) for item in band)
        print(f"{filename}: {len(band)} questions, {tests} tests")

    hidden = [puzzle_payload(p) for p in sorted(HIDDEN_PUZZLES, key=lambda p: p.level)]
    (DATA_DIR / "hidden_dungeon.json").write_text(json.dumps(hidden, indent=2) + "\n", encoding="utf-8")
    print(f"hidden_dungeon.json: {len(hidden)} puzzles")
    print(f"TOTAL: {len(ALL_QUESTIONS)} coding questions + {len(hidden)} puzzles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
