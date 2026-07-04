"""Async client for the self-hosted Piston execution engine.

The single entry point is run_submission(). It never raises on infrastructure
failure: if Piston is unreachable the verdict is "judge_offline" so the game
loop keeps running.

The most important output field is `failed_probes`: the probe labels of the
hidden test cases the submission failed. The game layer writes these into the
player's Cognee memory episodes — they are how the Boss learns which KIND of
input breaks a player, not merely that something failed.
"""

from __future__ import annotations

import time
from typing import Any, Optional

import httpx

PISTON_URL = "http://127.0.0.1:2000"
EXECUTE_ENDPOINT = f"{PISTON_URL}/api/v2/execute"

# Game language id -> Piston (language, file name). Version "*" = whatever
# runtime is installed (see README for the one-time package install).
SUPPORTED_LANGUAGES: dict[str, dict[str, str]] = {
    "python3": {"language": "python", "file": "main.py"},
    "java": {"language": "java", "file": "Main.java"},
    "c++": {"language": "c++", "file": "main.cpp"},
    "c": {"language": "c", "file": "main.c"},
}

COMPILED = {"java", "c++", "c"}
# Compiled languages pay a JVM/compiler startup tax on top of the question's
# per-test budget.
RUN_GRACE_MS = {"python3": 500, "java": 2000, "c++": 300, "c": 300}
COMPILE_TIMEOUT_MS = 10000  # Piston's compile_timeout ceiling; 15000 was 400-rejected
# Piston rejects any request whose run_timeout exceeds its configured ceiling
# (default 3000ms) with HTTP 400 -> we'd read that as judge_offline for EVERY
# submission. With time_limit_s=3 + grace we were sending 3300-5000ms, so the
# judge was silently offline for all languages. Clamp to the ceiling. If Piston
# is reconfigured with a higher PISTON_RUN_TIMEOUT, raise this to match.
PISTON_MAX_RUN_TIMEOUT_MS = 3000


def _offline(language: str, total: int) -> dict[str, Any]:
    return {
        "passed": False,
        "tests_passed": 0,
        "tests_total": total,
        "verdict": "judge_offline",
        "failed_probes": [],
        "runtime_ms": 0,
        "language": language,
    }


async def run_submission(
    code: str,
    language: str,
    test_cases: list[dict],
    time_limit_s: int,
) -> dict[str, Any]:
    """Judge `code` against `test_cases` (dicts with stdin / expected_stdout /
    probe keys, as stored in the question bank).

    Returns the structured verdict described in the module docstring. Verdicts:
    accepted | wrong_answer | timeout | compile_error | runtime_error |
    judge_offline. All tests are always run (no fail-fast) so every failed
    probe is captured — richer memory signal beats a faster wrong answer.
    """
    total = len(test_cases)
    if language not in SUPPORTED_LANGUAGES:
        return {
            "passed": False,
            "tests_passed": 0,
            "tests_total": total,
            "verdict": "runtime_error",
            "failed_probes": [],
            "runtime_ms": 0,
            "language": language,
        }

    lang = SUPPORTED_LANGUAGES[language]
    run_timeout_ms = min(
        time_limit_s * 1000 + RUN_GRACE_MS[language], PISTON_MAX_RUN_TIMEOUT_MS
    )

    tests_passed = 0
    failed_probes: list[str] = []
    worst = "accepted"  # escalates: wrong_answer < timeout < runtime_error
    runtime_ms = 0

    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        for case in test_cases:
            payload = {
                "language": lang["language"],
                "version": "*",
                "files": [{"name": lang["file"], "content": code}],
                "stdin": case.get("stdin", ""),
                "compile_timeout": COMPILE_TIMEOUT_MS,
                "run_timeout": run_timeout_ms,
            }
            started = time.monotonic()
            try:
                response = await client.post(EXECUTE_ENDPOINT, json=payload)
                response.raise_for_status()
                result = response.json()
            except (httpx.HTTPError, ValueError):
                return _offline(language, total)
            runtime_ms += int((time.monotonic() - started) * 1000)

            compile_stage: Optional[dict] = result.get("compile")
            if compile_stage and compile_stage.get("code") != 0:
                # Nothing ran; failed_probes stays empty — a compile error says
                # nothing about which inputs break the player.
                return {
                    "passed": False,
                    "tests_passed": 0,
                    "tests_total": total,
                    "verdict": "compile_error",
                    "failed_probes": [],
                    "runtime_ms": runtime_ms,
                    "language": language,
                }

            run_stage = result.get("run", {})
            case_verdict = _classify(run_stage, case.get("expected_stdout", ""))
            if case_verdict == "accepted":
                tests_passed += 1
            else:
                if case.get("probe"):
                    failed_probes.append(case["probe"])
                worst = _worse(worst, case_verdict)

    return {
        "passed": tests_passed == total,
        "tests_passed": tests_passed,
        "tests_total": total,
        "verdict": "accepted" if tests_passed == total else worst,
        "failed_probes": failed_probes,
        "runtime_ms": runtime_ms,
        "language": language,
    }


def _classify(run_stage: dict, expected: str) -> str:
    status = run_stage.get("status")
    signal = run_stage.get("signal")
    if status == "TO" or signal == "SIGKILL":
        return "timeout"
    if run_stage.get("code") != 0:
        return "runtime_error"
    actual = (run_stage.get("stdout") or "").strip()
    return "accepted" if actual == expected.strip() else "wrong_answer"


_SEVERITY = {"accepted": 0, "wrong_answer": 1, "timeout": 2, "runtime_error": 3}


def _worse(a: str, b: str) -> str:
    return a if _SEVERITY[a] >= _SEVERITY[b] else b
