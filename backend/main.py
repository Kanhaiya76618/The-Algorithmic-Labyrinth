"""Dungeon of Recall — FastAPI app. Run: uvicorn backend.main:app --reload"""

from __future__ import annotations

import os

from backend import config  # noqa: F401  — loads .env before anything reads env
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.content.router import router as content_router
from backend.game.router import router as game_router
from backend.memory.router import router as memory_router

app = FastAPI(title="Dungeon of Recall", version="0.1.0")

# CRA dev server (3000) is the current frontend; 5173 kept for older Vite setups.
_origins = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173"] + [
    origin.strip()
    for origin in os.environ.get("ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(game_router)
app.include_router(content_router)
app.include_router(memory_router)


@app.get("/health")
def health() -> dict:
    return {"ok": True, "memory_backend": config.MEMORY_BACKEND}
