"""Game engine: floor progression, grading, exploration events, and the
discovery hooks. Memory layer (Role A) is reached only through the
MemoryService interface.
"""

from __future__ import annotations

import time
from typing import Optional

from backend.content import loader
from backend.game import session
from backend.game.discovery import check_discovery
from backend.game.session import RunState
from contracts.memory_interface import MemoryService
from contracts.schemas import AnswerResult, Challenge, DiscoveryState, Episode

EXPLORATION_ACTIONS = {"revisit_floor", "inspect", "idle_linger", "off_path_move"}


def _exploration_detail(action: str, target: Optional[str], level: int) -> str:
    if action == "inspect":
        return f"inspected {target or 'the surroundings'}, floor {level}"
    if action == "revisit_floor":
        return f"revisited cleared floor {level}"
    if action == "idle_linger":
        return f"lingered on floor {level}"
    return f"took the long way on floor {level}"


async def start_run(player_id: str, mem: MemoryService) -> tuple[RunState, DiscoveryState]:
    run = session.create_run(player_id)
    discovery = await check_discovery(player_id, mem)
    run.last_discovery = discovery
    return run, discovery


def current_challenge(run: RunState, language: Optional[str] = None) -> Optional[Challenge]:
    if run.in_hidden:
        challenge = loader.get_hidden_dungeon_challenge(run.hidden_level)
    elif run.level in loader.BOSS_QUESTION_COUNTS:
        bosses = loader.get_boss_challenges_for_level(run.level, language)
        challenge = bosses[run.boss_question_index] if run.boss_question_index < len(bosses) else None
    else:
        challenge = loader.get_challenge_for_level(run.level, language, exclude_ids=run.seen_question_ids)
    if challenge:
        run.current_question_id = challenge.question_id
        run.seen_question_ids.add(challenge.question_id)
    return challenge


async def _grade(
    question_id: str, answer: Optional[str], code: Optional[str], language: str
) -> AnswerResult:
    if code:
        from backend.judge.client import run_submission

        tests = loader.get_hidden_tests(question_id)
        verdict = await run_submission(code, language, tests, loader.get_time_limit(question_id))
        message = "The judge sleeps; your spell goes unjudged." if verdict["verdict"] == "judge_offline" else None
        return AnswerResult(
            correct=verdict["passed"],
            tests_passed=verdict["tests_passed"],
            tests_total=verdict["tests_total"],
            verdict=verdict["verdict"],
            failed_probes=verdict["failed_probes"],
            message=message,
        )
    expected = loader.get_expected_answer(question_id)
    correct = expected is not None and answer is not None and answer.strip() == expected.strip()
    return AnswerResult(
        correct=correct,
        tests_passed=1 if correct else 0,
        tests_total=1,
        verdict="accepted" if correct else "wrong_answer",
    )


async def submit_answer(
    run: RunState,
    question_id: str,
    answer: Optional[str],
    code: Optional[str],
    language: str,
    mem: MemoryService,
) -> tuple[AnswerResult, DiscoveryState]:
    started = time.monotonic()
    public = loader.get_question_by_id(question_id)
    result = await _grade(question_id, answer, code, language)

    is_boss_floor = not run.in_hidden and run.level in loader.BOSS_QUESTION_COUNTS

    # question_attempt episode — the memory loop's staple diet
    await _remember_safely(
        mem,
        Episode(
            player_id=run.player_id,
            event_type="question_attempt",
            question_id=question_id,
            topic=public.topic if public else None,
            difficulty=public.difficulty.value if public else None,
            correct=result.correct,
            time_taken_s=round(time.monotonic() - started, 3),
            failed_probes=result.failed_probes,
            floor=run.hidden_level if run.in_hidden else run.level,
        ),
    )

    result = _advance(run, result)

    # Discovery checks: floor transitions and post-boss-attempt.
    discovery = run.last_discovery or DiscoveryState()
    if run.in_hidden:
        pass  # already inside — no discovery checks needed
    elif is_boss_floor and not result.correct:
        taunt = loader.get_boss_taunt(
            topic=public.topic if public else None,
            probe=result.failed_probes[0] if result.failed_probes else None,
        )
        result.message = f"{result.message + ' ' if result.message else ''}{taunt}"
        discovery = await check_discovery(run.player_id, mem, boss_level=run.level, boss_failed=True)
    elif result.floor_cleared or result.run_complete:
        discovery = await check_discovery(run.player_id, mem)
    run.last_discovery = discovery
    return result, discovery


def _advance(run: RunState, result: AnswerResult) -> AnswerResult:
    if not result.correct:
        return result
    if run.in_hidden:
        result.floor_cleared = True
        if run.hidden_level >= session.MAX_HIDDEN_LEVEL:
            run.hidden_complete = True
            result.run_complete = True
        else:
            run.hidden_level += 1
        return result

    if run.level in loader.BOSS_QUESTION_COUNTS:
        run.boss_question_index += 1
        if run.boss_question_index < loader.BOSS_QUESTION_COUNTS[run.level]:
            return result  # more boss questions on this floor
    result.floor_cleared = True
    if run.level >= session.MAX_LEVEL:
        run.run_complete = True
    else:
        run.level += 1
        run.boss_question_index = 0
        session.on_floor_transition(run)
        result.boss_triggered = run.level in loader.BOSS_QUESTION_COUNTS
    return result


async def record_exploration(
    run: RunState, action: str, target: Optional[str], mem: MemoryService
) -> bool:
    """Write ONE exploration episode, debounced per (action, floor) per floor
    visit. Returns False when debounced or unknown action."""
    if action not in EXPLORATION_ACTIONS:
        return False
    key = (action, run.level)
    if key in run.exploration_seen:
        return False
    run.exploration_seen.add(key)
    await _remember_safely(
        mem,
        Episode(
            player_id=run.player_id,
            event_type="exploration",
            floor=run.level,
            detail=_exploration_detail(action, target, run.level),
        ),
    )
    return True


async def enter_hidden(run: RunState, mem: MemoryService) -> Optional[DiscoveryState]:
    """Enter the hidden dungeon — gated by DERIVED discovery, never session
    state. Returns the state on success, None when still sealed."""
    discovery = await check_discovery(run.player_id, mem)
    run.last_discovery = discovery
    if not discovery.revealed:
        return None
    run.in_hidden = True
    return discovery


async def _remember_safely(mem: MemoryService, episode: Episode) -> None:
    try:
        await mem.remember_episode(episode)
    except Exception:
        pass  # memory being down must never crash the game loop
