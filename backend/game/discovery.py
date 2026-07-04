"""The Whisper of Recall — hidden-dungeon discovery engine.

Discovery runs THROUGH the memory layer: the unlock decision is derived from
recall() over the player's graph on every check. Nothing here persists
discovery in session state.

Path C (forget seals it) falls out of that derivation for free: the revealed
state IS the "discovery" episode in the graph plus the recalled profile.
When forget() wipes the player's dataset, the next check_discovery finds no
whispers, no reveal episode, explorer_score back at 0 — and returns
revealed=False. The entrance seals itself. No special case exists, and none
may be added: that re-sealing is a demo beat.
"""

from __future__ import annotations

from typing import Optional

from contracts.memory_interface import MemoryService
from contracts.schemas import DiscoveryState, Episode

EXPLORER_THRESHOLD = 0.6
WHISPERS_TO_REVEAL = 3
MERCY_FAILURES = 3
MERCY_FRUSTRATION = 0.6

_WHISPER_PREFIX = "whisper:"
_REVEAL_PREFIX = "hidden entrance revealed"

# Templates interpolate a RECALLED exploration detail — whispers quote the
# player's own remembered behaviour, they are not a static clue list.
_WHISPER_TEMPLATES = [
    "You {detail}. It remembers you too.",
    "The dungeon felt it when you {detail}. Something behind the stone leaned closer.",
    "You {detail} — and far below, a door dreamed of being found.",
]

_MERCY_WHISPER = "The wall splits. The dungeon has seen enough."


async def check_discovery(
    player_id: str,
    mem: MemoryService,
    boss_level: Optional[int] = None,
    boss_failed: bool = False,
) -> DiscoveryState:
    """Called at floor transitions and after boss attempts. Never raises —
    a dead memory backend must not break a floor transition."""
    try:
        return await _check(player_id, mem, boss_level, boss_failed)
    except Exception:
        return DiscoveryState()


async def _check(
    player_id: str,
    mem: MemoryService,
    boss_level: Optional[int],
    boss_failed: bool,
) -> DiscoveryState:
    profile = await mem.recall_profile(player_id)
    whispers = await _recall_whispers(mem, player_id)

    # Already found (the reveal episode lives in the graph).
    if profile.hidden_discovered:
        via = await _recall_reveal_via(mem, player_id)
        return DiscoveryState(revealed=True, via=via, whispers=whispers)

    # Path B — MERCY CRACK: the dungeon relents on a beaten-down challenger.
    if boss_failed and boss_level is not None and profile.frustration >= MERCY_FRUSTRATION:
        failures = await _recent_boss_failures(mem, player_id, boss_level)
        if failures >= MERCY_FAILURES:
            await mem.remember_episode(
                Episode(
                    player_id=player_id,
                    event_type="discovery",
                    floor=boss_level,
                    detail=f"{_REVEAL_PREFIX} via mercy",
                )
            )
            return DiscoveryState(revealed=True, via="mercy", whispers=whispers + [_MERCY_WHISPER])

    # Path A — EXPLORER: curiosity, recalled, becomes a voice.
    if profile.explorer_score >= EXPLORER_THRESHOLD:
        new_whisper = await _emit_whisper(mem, player_id, whispers)
        if new_whisper:
            whispers = whispers + [new_whisper]
        if len(whispers) >= WHISPERS_TO_REVEAL:
            await mem.remember_episode(
                Episode(
                    player_id=player_id,
                    event_type="discovery",
                    detail=f"{_REVEAL_PREFIX} via explorer",
                )
            )
            return DiscoveryState(revealed=True, via="explorer", whispers=whispers)

    return DiscoveryState(revealed=False, via=None, whispers=whispers)


async def _emit_whisper(mem: MemoryService, player_id: str, heard: list[str]) -> Optional[str]:
    """Build one new whisper quoting a recalled exploration episode the player
    hasn't been whispered about yet. Remember it as a discovery episode so
    whisper count itself lives in the graph (and dies with forget())."""
    explorations = await mem.recall_episodes(player_id, event_type="exploration", limit=20)
    # prefer episodes not yet quoted in any earlier whisper, so each whisper
    # surfaces a different remembered moment
    fresh = [ep for ep in explorations if ep.detail and not any(ep.detail in w for w in heard)]
    for ep in fresh or explorations:
        if not ep.detail:
            continue
        template = _WHISPER_TEMPLATES[len(heard) % len(_WHISPER_TEMPLATES)]
        text = template.format(detail=ep.detail)
        if text in set(heard):
            continue
        await mem.remember_episode(
            Episode(
                player_id=player_id,
                event_type="discovery",
                floor=ep.floor,
                detail=f"{_WHISPER_PREFIX} {text}",
            )
        )
        return text
    return None


async def _recall_whispers(mem: MemoryService, player_id: str) -> list[str]:
    episodes = await mem.recall_episodes(player_id, event_type="discovery", limit=20)
    texts = [
        e.detail[len(_WHISPER_PREFIX):].strip()
        for e in episodes
        if e.detail and e.detail.startswith(_WHISPER_PREFIX)
    ]
    return list(reversed(texts))  # chronological


async def _recall_reveal_via(mem: MemoryService, player_id: str) -> Optional[str]:
    episodes = await mem.recall_episodes(player_id, event_type="discovery", limit=20)
    for e in episodes:
        if e.detail and e.detail.startswith(_REVEAL_PREFIX):
            return "mercy" if e.detail.endswith("mercy") else "explorer"
    return None


async def _recent_boss_failures(mem: MemoryService, player_id: str, boss_level: int) -> int:
    attempts = await mem.recall_episodes(player_id, event_type="question_attempt", limit=20)
    return sum(1 for e in attempts if e.floor == boss_level and e.correct is False)
