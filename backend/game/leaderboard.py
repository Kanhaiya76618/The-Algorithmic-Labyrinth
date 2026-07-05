from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from pydantic import BaseModel

from backend.config import REPO_ROOT

logger = logging.getLogger("dor.game")
LEADERBOARD_FILE = REPO_ROOT / "data" / "leaderboard.json"


class LeaderboardEntry(BaseModel):
    player_id: str
    max_level: int
    explorer_score: float
    threat_level: float
    correct_attempts: int
    total_attempts: int
    last_updated: float


def get_leaderboard() -> list[LeaderboardEntry]:
    if not LEADERBOARD_FILE.exists():
        return []
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                return []
            entries = []
            for item in data:
                try:
                    entries.append(LeaderboardEntry(**item))
                except Exception:
                    pass
            # Sort by max_level desc, explorer_score desc, correct_attempts desc, total_attempts asc
            entries.sort(
                key=lambda e: (
                    -e.max_level,
                    -e.explorer_score,
                    -e.correct_attempts,
                    e.total_attempts,
                )
            )
            return entries
    except Exception as e:
        logger.warning(f"Failed to read leaderboard: {e}")
        return []


def save_leaderboard(entries: list[LeaderboardEntry]) -> None:
    LEADERBOARD_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump([e.dict() for e in entries], f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save leaderboard: {e}")


async def refresh_player_leaderboard(player_id: str, current_level: int, mem) -> None:
    try:
        # Retrieve player profile and history to build stats
        profile = await mem.recall_profile(player_id)
        attempts = await mem.recall_episodes(
            player_id, event_type="question_attempt", limit=1000
        )
        total_attempts = len(attempts)
        correct_attempts = sum(1 for e in attempts if e.correct)
        threat = profile.frustration * 100.0

        entries = get_leaderboard()
        updated = False
        for entry in entries:
            if entry.player_id.lower() == player_id.lower():
                entry.max_level = max(entry.max_level, current_level)
                entry.explorer_score = profile.explorer_score
                entry.threat_level = threat
                entry.correct_attempts = correct_attempts
                entry.total_attempts = total_attempts
                entry.last_updated = time.time()
                updated = True
                break

        if not updated:
            entries.append(
                LeaderboardEntry(
                    player_id=player_id,
                    max_level=current_level,
                    explorer_score=profile.explorer_score,
                    threat_level=threat,
                    correct_attempts=correct_attempts,
                    total_attempts=total_attempts,
                    last_updated=time.time(),
                )
            )

        save_leaderboard(entries)
    except Exception as e:
        logger.warning(f"Failed to update leaderboard for {player_id}: {e}")
