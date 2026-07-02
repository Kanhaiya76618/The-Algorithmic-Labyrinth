from fastapi import APIRouter, HTTPException

from backend.content.loader import (
    get_all_questions,
    get_question_by_id,
    get_questions_by_difficulty,
    get_questions_by_topic,
    get_random_question,
)
from contracts.schemas import Challenge, Difficulty

router = APIRouter(prefix="/content", tags=["content"])


@router.get("/questions", response_model=list[Challenge])
def get_questions() -> list[Challenge]:
    """Return every loaded challenge."""
    return get_all_questions()


@router.get("/questions/random", response_model=Challenge)
def get_random_questions() -> Challenge:
    """Return one random challenge."""
    question = get_random_question()
    if question is None:
        raise HTTPException(status_code=404, detail="No questions available")
    return question


@router.get("/questions/{question_id}", response_model=Challenge)
def get_question(question_id: str) -> Challenge:
    """Return a single challenge by its question_id."""
    question = get_question_by_id(question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.get("/questions/topic/{topic}", response_model=list[Challenge])
def get_questions_for_topic(topic: str) -> list[Challenge]:
    """Return all challenges for the requested topic."""
    questions = get_questions_by_topic(topic)
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for topic")
    return questions


@router.get("/questions/difficulty/{difficulty}", response_model=list[Challenge])
def get_questions_for_difficulty(difficulty: str) -> list[Challenge]:
    """Return all challenges for the requested difficulty."""
    try:
        Difficulty(difficulty.lower())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid difficulty") from exc

    questions = get_questions_by_difficulty(difficulty)
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for difficulty")
    return questions
