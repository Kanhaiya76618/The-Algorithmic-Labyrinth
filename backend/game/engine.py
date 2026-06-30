"""Role B — orchestrates a turn: pick challenge, grade answer, write memory."""
from __future__ import annotations
from contracts.schemas import (
    Challenge, SubmitAnswerRequest, AnswerResult, Episode, FeedbackSignal, Track,
)
from contracts.memory_interface import MemoryService
from backend.game import progression, session, policy
from backend.content import loader


async def next_challenge(player_id: str, mem: MemoryService) -> Challenge:
    run = session.get_run(player_id)
    profile = await mem.recall_profile(player_id)
    difficulty = policy.damp_for_frustration(
        progression.difficulty_for_floor(run.floor), profile
    )
    boss = progression.is_boss_floor(run.floor)
    topic = policy.choose_topic(profile, default="arrays") if boss else None
    q = loader.pick_question(difficulty, Track.DSA, topic=topic,
                             exclude=run.cleared_questions)
    return Challenge(
        question_id=q["id"], prompt=q["prompt"], topic=q["topic"],
        track=Track.DSA, difficulty=difficulty, floor=run.floor,
        is_boss=boss,
        boss_dialogue=loader.boss_line(profile) if boss else None,
    )


async def submit_answer(req: SubmitAnswerRequest, mem: MemoryService) -> AnswerResult:
    run = session.get_run(req.player_id)
    correct = loader.check_answer(req.question_id, req.answer)
    q = loader.get_question(req.question_id)

    # 1) write the episode
    await mem.remember_episode(Episode(
        player_id=req.player_id, question_id=req.question_id,
        topic=q["topic"], difficulty=q["difficulty"], correct=correct,
        time_taken_s=req.time_taken_s, hints_used=req.hints_used,
        retries=req.retries,
    ))
    # 2) reward signal (the feedback step) + improve happens inside reinforce/improve
    outcome = ("cleared" if correct else "failed") + f" {q['topic']}"
    await mem.reinforce(FeedbackSignal(
        player_id=req.player_id, outcome_text=outcome,
        score=2 if correct else -2,
    ))
    if correct:
        run.cleared_questions.add(req.question_id)
        run.floor += 1
    return AnswerResult(correct=correct, advanced=correct,
                        next_floor=run.floor,
                        message="Onward." if correct else "The boss grins.")
