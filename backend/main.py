"""
SHARED — set up ONCE on Day 1, then frozen.

This file includes all four routers up front. The router modules already
exist as stubs, so the app boots immediately. After today, NOBODY edits
main.py — each role only fills in their own router.py. That is how the
one file everyone would normally fight over stops causing conflicts.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.memory.router import router as memory_router
from backend.game.router import router as game_router
from backend.content.router import router as content_router

app = FastAPI(title="Dungeon of Recall API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # tighten before submission
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(game_router, prefix="/game", tags=["game"])         # Role B
app.include_router(content_router, prefix="/content", tags=["content"])  # Role C
app.include_router(memory_router, prefix="/memory", tags=["memory"])   # Role A


@app.get("/health")
async def health():
    return {"ok": True}
