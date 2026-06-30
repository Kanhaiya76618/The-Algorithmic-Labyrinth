"""Role A — how an Episode is serialized into memory text.

Kept separate so Role A can tune the wording the LLM extracts from
without touching service.py logic.
"""
from contracts.schemas import Episode


def episode_to_text(ep: Episode) -> str:
    outcome = "solved" if ep.correct else "failed"
    pat = f" Pattern: {ep.pattern}." if ep.pattern else ""
    return (
        f"Player {ep.player_id} {outcome} a {ep.difficulty.value} "
        f"{ep.topic} problem ({ep.track.value}) in {ep.time_taken_s:.0f}s "
        f"using {ep.hints_used} hints and {ep.retries} retries.{pat}"
    )
