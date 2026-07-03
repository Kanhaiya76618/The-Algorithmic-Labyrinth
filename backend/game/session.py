"""Run/session state. PROGRESSION lives here (levels, seen questions, hidden
progress). DISCOVERY does not — it is derived from the memory graph by
backend/game/discovery.py; session only CACHES the last DiscoveryState for
response building, never decides from it.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Optional

from contracts.schemas import DiscoveryState

MAX_LEVEL = 50
MAX_HIDDEN_LEVEL = 10


@dataclass
class RunState:
    run_id: str
    player_id: str
    level: int = 1
    boss_question_index: int = 0  # progress within a multi-question boss floor
    seen_question_ids: set[str] = field(default_factory=set)
    current_question_id: Optional[str] = None
    run_complete: bool = False
    # hidden dungeon PROGRESSION (entry is gated by derived discovery, not this)
    in_hidden: bool = False
    hidden_level: int = 1
    hidden_complete: bool = False
    # debounce: one exploration episode per (action, floor) per floor visit
    exploration_seen: set[tuple[str, int]] = field(default_factory=set)
    # cache only — re-derived at every floor transition / boss attempt
    last_discovery: Optional[DiscoveryState] = None


_runs: dict[str, RunState] = {}


def create_run(player_id: str) -> RunState:
    run = RunState(run_id=uuid.uuid4().hex[:12], player_id=player_id)
    _runs[run.run_id] = run
    return run


def get_run(run_id: str) -> Optional[RunState]:
    return _runs.get(run_id)


def on_floor_transition(run: RunState) -> None:
    """New floor visit: reset the exploration debounce window."""
    run.exploration_seen.clear()
