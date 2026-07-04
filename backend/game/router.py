"""Game routes. Response wrappers are game-layer models (not contracts) so the
frozen contract files stay untouched; they embed the approved contract models.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.game import engine, session
from backend.game.deps import get_memory
from contracts.memory_interface import MemoryService
from contracts.schemas import AnswerResult, Challenge, DiscoveryState, SubmitAnswerRequest

router = APIRouter(prefix="/game", tags=["game"])


class StartRequest(BaseModel):
    player_name: str


class StartResponse(BaseModel):
    run_id: str
    player_id: str
    level: int
    discovery: DiscoveryState


class NextResponse(BaseModel):
    challenge: Challenge
    level: int
    in_hidden: bool
    hidden_level: int


class AnswerResponse(BaseModel):
    result: AnswerResult
    level: int
    in_hidden: bool
    hidden_level: int
    discovery: DiscoveryState
    new_whisper: Optional[str] = None


class ExploreRequest(BaseModel):
    run_id: str
    action: str  # revisit_floor | inspect | idle_linger | off_path_move
    target: Optional[str] = None


class ExploreResponse(BaseModel):
    recorded: bool  # False = debounced or unknown action


class HiddenEnterRequest(BaseModel):
    run_id: str


def _run_or_404(run_id: str) -> session.RunState:
    run = session.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Unknown run")
    return run


@router.post("/start", response_model=StartResponse)
async def start(req: StartRequest, mem: MemoryService = Depends(get_memory)) -> StartResponse:
    run, discovery = await engine.start_run(req.player_name.strip(), mem)
    return StartResponse(run_id=run.run_id, player_id=run.player_id, level=run.level, discovery=discovery)


@router.post("/next", response_model=NextResponse)
async def next_challenge(req: HiddenEnterRequest) -> NextResponse:
    run = _run_or_404(req.run_id)
    challenge = engine.current_challenge(run)
    if challenge is None:
        raise HTTPException(status_code=404, detail="No challenge available")
    return NextResponse(
        challenge=challenge, level=run.level, in_hidden=run.in_hidden, hidden_level=run.hidden_level
    )


@router.post("/answer", response_model=AnswerResponse)
async def answer(req: SubmitAnswerRequest, mem: MemoryService = Depends(get_memory)) -> AnswerResponse:
    run = _run_or_404(req.run_id)
    # Server-side anti-replay: only the challenge actually being served may be
    # answered — otherwise one memorized easy question climbs all 50 floors.
    if run.current_question_id is None or req.question_id != run.current_question_id:
        raise HTTPException(status_code=409, detail="That is not the challenge before you")
    known_whispers = len((run.last_discovery or DiscoveryState()).whispers)
    result, discovery = await engine.submit_answer(
        run, req.question_id, req.answer, req.code, req.language, mem
    )
    new_whisper = discovery.whispers[-1] if len(discovery.whispers) > known_whispers else None
    return AnswerResponse(
        result=result,
        level=run.level,
        in_hidden=run.in_hidden,
        hidden_level=run.hidden_level,
        discovery=discovery,
        new_whisper=new_whisper,
    )


@router.post("/explore", response_model=ExploreResponse)
async def explore(req: ExploreRequest, mem: MemoryService = Depends(get_memory)) -> ExploreResponse:
    run = _run_or_404(req.run_id)
    recorded = await engine.record_exploration(run, req.action, req.target, mem)
    return ExploreResponse(recorded=recorded)


@router.post("/hidden/enter", response_model=StartResponse)
async def hidden_enter(req: HiddenEnterRequest, mem: MemoryService = Depends(get_memory)) -> StartResponse:
    run = _run_or_404(req.run_id)
    discovery = await engine.enter_hidden(run, mem)
    if discovery is None:
        raise HTTPException(status_code=403, detail="The entrance is sealed. The dungeon does not remember you finding it.")
    return StartResponse(run_id=run.run_id, player_id=run.player_id, level=run.hidden_level, discovery=discovery)
