"""Episode -> natural-language sentence for the graph extractor.

These sentences are the ONLY thing Cognee sees; every discriminative token
(topic names, probe labels, "explored", "lingered", "whisper") must appear
explicitly and consistently, or the graph can't form the entities the Boss
reasons over. Keep wording stable — the extractor rewards consistency.
"""

from __future__ import annotations

from contracts.schemas import Episode


def episode_to_text(ep: Episode) -> str:
    if ep.event_type == "exploration":
        floor = f" on floor {ep.floor}" if ep.floor is not None else ""
        return f"Player {ep.player_id} explored{floor}: {ep.detail or 'wandered without purpose'}."

    if ep.event_type == "discovery":
        return f"Player {ep.player_id} discovery event: {ep.detail or 'found something hidden'}."

    # question_attempt
    outcome = "solved" if ep.correct else "failed"
    parts = [
        f"Player {ep.player_id} {outcome} a {ep.difficulty or 'unknown-difficulty'}",
        f"{ep.topic or 'unknown-topic'} question",
    ]
    if ep.question_id:
        parts.append(f"({ep.question_id})")
    if ep.floor is not None:
        parts.append(f"on floor {ep.floor}")
    sentence = " ".join(parts)
    extras = []
    if ep.time_taken_s is not None:
        extras.append(f"taking {ep.time_taken_s:.0f} seconds")
    if ep.hints_used:
        extras.append(f"using {ep.hints_used} hints")
    if ep.retries:
        extras.append(f"after {ep.retries} retries")
    if extras:
        sentence += ", " + ", ".join(extras)
    if ep.failed_probes:
        sentence += ". Failure probes: " + ", ".join(ep.failed_probes)
    return sentence + "."
