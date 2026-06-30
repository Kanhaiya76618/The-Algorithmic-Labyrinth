"""Role B — game endpoints."""
from fastapi import APIRouter, Depends
from backend.deps import get_memory
from contracts.memory_interface import MemoryService
from contracts.schemas import (
    StartGameRequest, StartGameResponse, Challenge,
    SubmitAnswerRequest, AnswerResult,
)
from backend.game import engine, session

router = APIRouter()


@router.post("/start", response_model=StartGameResponse)
async def start(req: StartGameRequest):
    session.reset_run(req.player_id)
    return StartGameResponse(player_id=req.player_id, floor=1)


@router.get("/{player_id}/next", response_model=Challenge)
async def next_challenge(player_id: str, mem: MemoryService = Depends(get_memory)):
    return await engine.next_challenge(player_id, mem)


@router.post("/answer", response_model=AnswerResult)
async def answer(req: SubmitAnswerRequest, mem: MemoryService = Depends(get_memory)):
    return await engine.submit_answer(req, mem)
