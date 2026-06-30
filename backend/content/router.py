"""Role C — content endpoints (mostly for tooling/preview)."""
from fastapi import APIRouter
from backend.content import loader

router = APIRouter()


@router.get("/question/{qid}")
async def question(qid: str):
    q = loader.get_question(qid).copy()
    q.pop("answer", None)   # never leak the answer to the client
    return q
