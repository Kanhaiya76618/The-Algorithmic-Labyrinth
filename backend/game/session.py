"""Role B — per-player session/run state. In-memory for the hackathon."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class RunState:
    player_id: str
    floor: int = 1
    hidden_unlocked: bool = False
    cleared_questions: set[str] = field(default_factory=set)


_runs: dict[str, RunState] = {}


def get_run(player_id: str) -> RunState:
    return _runs.setdefault(player_id, RunState(player_id=player_id))


def reset_run(player_id: str) -> None:
    _runs.pop(player_id, None)
