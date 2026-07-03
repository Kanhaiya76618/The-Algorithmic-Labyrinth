"""Memory endpoints — exactly the surface the frontend needs, nothing more.
No debug endpoints: nothing here may expose hidden tests, answers, episodes.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from backend.game.deps import get_memory
from contracts.memory_interface import MemoryService
from contracts.schemas import PlayerProfile

router = APIRouter(prefix="/memory", tags=["memory"])


class DifficultySpike(BaseModel):
    topic: str
    delta: int


class TopicEdge(BaseModel):
    id: str
    name: str
    weight: float
    reinforced_recently: bool = False


class MemoryReport(BaseModel):
    """Shape MemoryView/MemoryGraph already consume, plus the raw profile."""

    player_id: str
    threat_level: int  # 0..100
    executive_summary: str
    difficulty_spike: Optional[DifficultySpike] = None
    topics: list[TopicEdge] = Field(default_factory=list)
    profile: PlayerProfile
    graph: dict


def _summary(p: PlayerProfile) -> str:
    if not p.weak_topics and not p.strong_topics:
        return "The Boss has no measure of this challenger yet. It watches, and it waits."
    parts = []
    if p.weak_topics:
        parts.append(f"The Boss has noted repeated failure on {', '.join(p.weak_topics[:3])}")
    if p.weak_probes:
        parts.append(f"and knows which inputs break them: {', '.join(p.weak_probes[:3])}")
    if p.strong_topics:
        parts.append(f"It avoids their strengths: {', '.join(p.strong_topics[:2])}")
    if p.frustration >= 0.6:
        parts.append("It senses frustration, and it presses")
    return ". ".join(parts) + "."


def _threat(p: PlayerProfile) -> int:
    score = 0.55 * p.frustration + 0.07 * len(p.weak_topics) + 0.04 * len(p.weak_probes)
    if p.hidden_discovered:
        score += 0.1
    return round(100 * min(1.0, score))


def _topics(profile: PlayerProfile, graph: dict) -> list[TopicEdge]:
    labels = {n["id"]: n.get("label") or n.get("id", "") for n in graph.get("nodes", [])}
    weak = {t.lower() for t in profile.weak_topics}
    out = []
    for edge in graph.get("edges", []):
        name = str(labels.get(edge.get("to"), edge.get("to", "")))
        out.append(
            TopicEdge(
                id=str(edge.get("to")),
                name=name,
                weight=max(0.0, min(1.0, float(edge.get("weight", 0)))),
                reinforced_recently=name.lower() in weak,
            )
        )
    return out[:12]


@router.get("/report/{player_id}", response_model=MemoryReport)
async def report(player_id: str, mem: MemoryService = Depends(get_memory)) -> MemoryReport:
    profile = await mem.recall_profile(player_id)
    graph = await mem.get_graph(player_id)
    spike = None
    if profile.weak_topics:
        spike = DifficultySpike(
            topic=profile.weak_topics[0],
            delta=min(25, 8 + 4 * len(profile.weak_probes)),
        )
    return MemoryReport(
        player_id=player_id,
        threat_level=_threat(profile),
        executive_summary=_summary(profile),
        difficulty_spike=spike,
        topics=_topics(profile, graph),
        profile=profile,
        graph=graph,
    )


@router.post("/forget/{player_id}")
async def forget(player_id: str, mem: MemoryService = Depends(get_memory)) -> dict:
    await mem.forget(player_id)
    return {"forgotten": player_id}
