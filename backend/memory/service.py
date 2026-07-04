"""CogneeMemoryService — the real memory layer (Role A), self-hosted stores.

Design (see API_NOTES.md for the verified 1.2.2 API):
- SEMANTIC memory: cognee. remember() feeds episode sentences into the
  per-player dataset (dataset_name=f"player_{id}"); recall() answers profile
  questions over the graph; session.add_feedback() is the native feedback
  loop; improve() consolidates; forget(dataset=...) is surgical.
- EXACT memory: a JSONL episode journal per player under COGNEE_DATA_ROOT.
  recall_episodes() needs deterministic, ordered, typed retrieval (discovery
  whisper/reveal logic depends on it); an LLM answer cannot guarantee that.
  The journal lives on the same mounted volume, and forget() deletes it with
  the dataset — so "forget seals the hidden dungeon" still holds exactly.
- recall_profile(): LLM fields (weak/strong topics, probes, frustration,
  explorer_score) come from GRAPH_COMPLETION; the game-critical booleans
  (whispers_heard, hidden_discovered) are overridden from the journal so a
  flaky LLM answer can never un-reveal a found entrance mid-run.

Every cognee call is wrapped: failures log and degrade (default profile /
warn-and-continue). A memory outage must never crash a floor transition.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import time
import uuid
from pathlib import Path
from typing import Optional

from backend import config
from backend.memory.schema import episode_to_text
from contracts.memory_interface import MemoryService
from contracts.schemas import Episode, PlayerProfile

logger = logging.getLogger("dor.memory")

# Outage guard: a hung cognee call (e.g. an LLM retry storm) must degrade like
# any other cognee failure, never stall the game loop.
COGNEE_WRITE_TIMEOUT_S = 35.0   # remember / reinforce / forget — aimlapi cognify runs
                                # 16-21s per call (measured), so 20s clipped it; 35s headroom
COGNEE_RECALL_TIMEOUT_S = 25.0  # recall / graph reads (session-path answers add LLM turns)
COGNEE_IMPROVE_TIMEOUT_S = 120.0  # improve bridges session feedback via cognify (feedback-weights
                                  # + persist + distill pipelines); 60s clipped it on aimlapi

_WHISPER_PREFIX = "whisper:"
_REVEAL_PREFIX = "hidden entrance revealed"

_PROFILE_SYSTEM_PROMPT = (
    "You are the memory of a dungeon boss, answering about one player. "
    "Answer ONLY with a JSON object — no prose, no code fences — with exactly "
    "these keys: weak_topics (list of topic strings the player fails), "
    "strong_topics (list of topic strings the player reliably solves), "
    "weak_probes (list of failure probe labels like 'edge:empty'), "
    "frustration (number 0..1, recent failure pressure), "
    "explorer_score (number 0..1, breadth of exploration behaviour), "
    "whispers_heard (integer), hidden_discovered (boolean). "
    "Topics MUST be the bare canonical topic name exactly as it appears in "
    "the episodes — e.g. 'trees', 'sorting', 'graphs' — never a phrase; "
    "never include difficulty levels or the word 'question'. "
    "'Boss profile correction' statements are ground truth about outcomes: "
    "when one contradicts episode-derived assessments, the correction wins "
    "(e.g. a topic listed as weak must be dropped if a correction says the "
    "player crushed it)."
)

_PROFILE_QUERY = (
    "Summarize player {player}'s behavioural profile from their episodes: "
    "which question topics do they fail or solve, which failure probes recur, "
    "how frustrated are they lately, how much do they explore (inspecting, "
    "lingering, revisiting, taking long routes), how many whispers have they "
    "heard, and did they discover the hidden entrance? [state nonce: {nonce}]"
)


def _clamp(x, lo=0.0, hi=1.0) -> float:
    try:
        return max(lo, min(hi, float(x)))
    except (TypeError, ValueError):
        return 0.0


def _str_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(v) for v in value if isinstance(v, (str, int, float))]
    return []


class CogneeMemoryService(MemoryService):
    def __init__(self) -> None:
        self._journal_dir = config.COGNEE_DATA_ROOT / "journal"
        self._journal_dir.mkdir(parents=True, exist_ok=True)
        self._journal_lock = asyncio.Lock()
        self._last_qa: dict[str, str] = {}  # player_id -> qa_id of last recall
        # player_id -> session of the last SUCCESSFUL recall. Sessions rotate
        # per recall: cognee's session answer path feeds conversation history
        # (our previous JSON answers) back into the prompt, and at temp 0 the
        # model anchors on them — stale profiles the nonce can't defeat. A
        # fresh session per recall keeps answers history-free while qa_id /
        # feedback / improve stay bound to the session that recall used.
        self._sessions: dict[str, str] = {}
        # cognee 1.2.2 races on concurrent creation of a NEW dataset: writer B
        # can see the Dataset row writer A just inserted before A's ACL grant
        # lands (get_dataset_ids reads ownership, the permission check reads
        # ACLs) -> spurious PermissionDeniedError. Serialize writes per player.
        self._write_locks: dict[str, asyncio.Lock] = {}
        self._configure_cognee()

    def _configure_cognee(self) -> None:
        import cognee

        data_root = config.COGNEE_DATA_ROOT
        # Storage trap fix: default roots live inside site-packages.
        cognee.config.data_root_directory(str(data_root / "data"))
        cognee.config.system_root_directory(str(data_root / "system"))

    # ------------------------------------------------------------ helpers

    @staticmethod
    def _dataset(player_id: str) -> str:
        return f"player_{re.sub(r'[^a-zA-Z0-9_]', '_', player_id)}"

    def _session(self, player_id: str) -> str:
        """Session of the last successful recall (feedback/improve target)."""
        sid = self._sessions.get(player_id)
        if sid is None:
            sid = self._new_session_id(player_id)
            self._sessions[player_id] = sid
        return sid

    @staticmethod
    def _new_session_id(player_id: str) -> str:
        safe = re.sub(r"[^a-zA-Z0-9_]", "_", player_id)
        return f"profile_{safe}_{uuid.uuid4().hex[:8]}"

    def _journal_path(self, player_id: str) -> Path:
        return self._journal_dir / f"{self._dataset(player_id)}.jsonl"

    async def _journal_append(self, episode: Episode) -> None:
        line = episode.model_dump_json() + "\n"
        async with self._journal_lock:
            with self._journal_path(episode.player_id).open("a", encoding="utf-8") as fh:
                fh.write(line)

    def _journal_read(self, player_id: str) -> list[Episode]:
        path = self._journal_path(player_id)
        if not path.exists():
            return []
        episodes = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    episodes.append(Episode.model_validate_json(line))
                except Exception:
                    logger.warning("journal: skipping corrupt line for %s", player_id)
        return episodes

    def _journal_facts(self, player_id: str) -> tuple[int, bool]:
        """(whispers_heard, hidden_discovered) — exact, from the journal."""
        whispers = 0
        discovered = False
        for ep in self._journal_read(player_id):
            if ep.event_type == "discovery" and ep.detail:
                if ep.detail.startswith(_WHISPER_PREFIX):
                    whispers += 1
                elif ep.detail.startswith(_REVEAL_PREFIX):
                    discovered = True
        return whispers, discovered

    # ----------------------------------------------------------- interface

    def _write_lock(self, player_id: str) -> asyncio.Lock:
        return self._write_locks.setdefault(player_id, asyncio.Lock())

    async def remember_episode(self, episode: Episode) -> None:
        await self._journal_append(episode)  # exact log first — never lose it
        try:
            import cognee

            async with self._write_lock(episode.player_id):
                await asyncio.wait_for(
                    cognee.remember(
                        episode_to_text(episode),
                        dataset_name=self._dataset(episode.player_id),
                    ),
                    timeout=COGNEE_WRITE_TIMEOUT_S,
                )
        except asyncio.TimeoutError:
            logger.warning(
                "remember() timed out after %.0fs; episode kept in journal only",
                COGNEE_WRITE_TIMEOUT_S,
            )
        except Exception:
            logger.warning("remember() failed; episode kept in journal only", exc_info=True)

    async def recall_profile(self, player_id: str) -> PlayerProfile:
        whispers, discovered = self._journal_facts(player_id)
        profile = PlayerProfile(
            player_id=player_id, whispers_heard=whispers, hidden_discovered=discovered
        )
        try:
            import cognee
            from cognee import SearchType

            # Nonce defeats session-cache staleness (see API_NOTES.md):
            nonce = f"{len(self._journal_read(player_id))}-{int(time.time())}"
            # Fresh session per recall (history-free answers); committed to
            # self._sessions only on success so reinforce/improve always
            # target the last recall that actually produced a QA.
            sid = self._new_session_id(player_id)
            results = await asyncio.wait_for(
                cognee.recall(
                    _PROFILE_QUERY.format(player=player_id, nonce=nonce),
                    query_type=SearchType.GRAPH_COMPLETION,
                    datasets=[self._dataset(player_id)],
                    session_id=sid,
                    top_k=15,
                    feedback_influence=0.5,
                    system_prompt=_PROFILE_SYSTEM_PROMPT,
                ),
                timeout=COGNEE_RECALL_TIMEOUT_S,
            )
            self._sessions[player_id] = sid
            answer, qa_id = self._extract_answer(results)
            if not qa_id:
                # cognee 1.2.2: an explicit query_type forces recall's source
                # list to ["graph"], so the session/QA source is never merged
                # into results and no entry carries qa_id. The QA row for THIS
                # recall was still written (the graph completion runs through
                # the session path and add_qa is awaited before recall
                # returns) — read it back directly.
                qa_id = await self._latest_qa_id(player_id)
            if qa_id:
                self._last_qa[player_id] = qa_id
                profile.interaction_id = qa_id
            parsed = self._parse_profile_json(answer)
            if parsed is not None:
                profile.weak_topics = _str_list(parsed.get("weak_topics"))
                profile.strong_topics = _str_list(parsed.get("strong_topics"))
                profile.weak_probes = _str_list(parsed.get("weak_probes"))
                profile.frustration = _clamp(parsed.get("frustration"))
                profile.explorer_score = _clamp(parsed.get("explorer_score"))
                # whispers_heard / hidden_discovered stay journal-derived:
                # game-critical state must not flap with LLM phrasing.
        except asyncio.TimeoutError:
            logger.warning(
                "recall() timed out after %.0fs; degraded to journal-only",
                COGNEE_RECALL_TIMEOUT_S,
            )
            self._fill_profile_from_journal(profile)
        except Exception:
            logger.warning("recall_profile degraded to journal-only", exc_info=True)
            self._fill_profile_from_journal(profile)
        return profile

    def _fill_profile_from_journal(self, profile: PlayerProfile) -> None:
        """Offline fallback: same derivations the stub proved."""
        eps = self._journal_read(profile.player_id)
        attempts = [e for e in eps if e.event_type == "question_attempt"]
        by_topic: dict[str, list[bool]] = {}
        for e in attempts:
            if e.topic and e.correct is not None:
                by_topic.setdefault(e.topic, []).append(e.correct)
        profile.weak_topics = [t for t, r in by_topic.items() if r.count(False) > r.count(True)]
        profile.strong_topics = [
            t for t, r in by_topic.items() if r.count(True) > r.count(False) and len(r) >= 2
        ]
        probes: dict[str, int] = {}
        for e in attempts:
            for p in e.failed_probes:
                probes[p] = probes.get(p, 0) + 1
        profile.weak_probes = sorted(probes, key=lambda p: -probes[p])[:5]
        recent = attempts[-6:]
        profile.frustration = (
            round(sum(1 for e in recent if e.correct is False) / len(recent), 2) if recent else 0.0
        )
        distinct = {(e.detail or "", e.floor) for e in eps if e.event_type == "exploration"}
        profile.explorer_score = min(1.0, len(distinct) / 8)

    async def _latest_qa_id(self, player_id: str) -> Optional[str]:
        """qa_id of the newest session-cache entry — i.e. the QA that the
        recall which just returned wrote for its own answer."""
        try:
            from cognee.infrastructure.session.get_session_manager import (
                get_session_manager,
            )
            from cognee.modules.users.methods import get_default_user

            sm = get_session_manager()
            if not sm.is_available:
                return None
            user = await get_default_user()
            entries = await sm.get_session(
                user_id=str(user.id),
                session_id=self._session(player_id),
                last_n=1,
                formatted=False,
            )
            if entries:
                return getattr(entries[-1], "qa_id", None)
        except Exception:
            logger.debug("latest_qa_id lookup failed", exc_info=True)
        return None

    @staticmethod
    def _extract_answer(results) -> tuple[str, Optional[str]]:
        answer, qa_id = "", None
        for entry in results or []:
            source = getattr(entry, "source", None)
            if source == "qa" or hasattr(entry, "qa_id"):
                qa_id = getattr(entry, "qa_id", None) or qa_id
                answer = getattr(entry, "answer", "") or answer
            elif not answer:
                answer = getattr(entry, "text", "") or getattr(entry, "content", "") or ""
        return answer, qa_id

    @staticmethod
    def _parse_profile_json(answer: str) -> Optional[dict]:
        if not answer:
            return None
        text = answer.strip()
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            logger.warning("profile parse: no JSON object in answer: %.120s", answer)
            return None
        try:
            parsed = json.loads(match.group(0))
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError as exc:
            logger.warning("profile parse: %s in %.120s", exc, answer)
            return None

    async def recall_episodes(
        self, player_id: str, event_type: Optional[str] = None, limit: int = 20
    ) -> list[Episode]:
        eps = self._journal_read(player_id)
        if event_type:
            eps = [e for e in eps if e.event_type == event_type]
        return list(reversed(eps[-limit:]))  # newest first

    async def reinforce(self, player_id: str, outcome_text: str, score: float) -> None:
        text = f"outcome score {score:+g}: {outcome_text}"
        # Channel 1 — feedback EPISODE into the player's graph. This is the
        # load-bearing path: graph content changes, so the next recall's
        # context (and answer) changes even on tiny graphs. Never depends on
        # a qa_id being present.
        await self.remember_episode(
            Episode(player_id=player_id, event_type="feedback", detail=text)
        )
        # Channel 2 — session-scoped QA feedback (opportunistic). Re-weights
        # the graph elements the last profile answer used, once improve()
        # bridges it. Only possible if the last recall yielded a qa_id.
        qa_id = self._last_qa.get(player_id)
        if not qa_id:
            logger.info(
                "reinforce: no qa_id for %s — episode channel only", player_id
            )
            return
        try:
            import cognee
            # cognee 1.2.2 validates feedback_score as a 1..5 rating (not a
            # signed delta): map our [-5..+5] onto it. -5 -> 1 (worst),
            # 0 -> 3, +5 -> 5. The signed semantics stay in feedback_text.
            rating = int(round((_clamp(score, -5, 5) + 5) / 10 * 4 + 1))
            await asyncio.wait_for(
                cognee.session.add_feedback(
                    session_id=self._session(player_id),
                    qa_id=qa_id,
                    feedback_text=text,
                    feedback_score=rating,
                ),
                timeout=COGNEE_WRITE_TIMEOUT_S,
            )
        except asyncio.TimeoutError:
            logger.warning(
                "reinforce timed out after %.0fs (non-fatal)", COGNEE_WRITE_TIMEOUT_S
            )
        except Exception:
            logger.warning("reinforce failed (non-fatal)", exc_info=True)

    async def improve(self, player_id: str) -> None:
        try:
            import cognee

            # session_ids is what makes feedback bite: without it improve()
            # only enriches the graph and NEVER runs the feedback-weights
            # pipeline (reinforce()'s scores would sit unused in the session
            # cache). With it, QA feedback re-weights the graph elements the
            # answer actually used, so future recalls rank them differently.
            await asyncio.wait_for(
                cognee.improve(
                    self._dataset(player_id),
                    session_ids=[self._session(player_id)],
                ),
                timeout=COGNEE_IMPROVE_TIMEOUT_S,
            )
        except asyncio.TimeoutError:
            logger.warning(
                "improve timed out after %.0fs (non-fatal)", COGNEE_IMPROVE_TIMEOUT_S
            )
        except Exception:
            logger.warning("improve failed (non-fatal)", exc_info=True)

    async def forget(self, player_id: str) -> None:
        """Surgical per-player wipe: cognee dataset + journal. Discovery state
        derives from these, so the hidden entrance re-seals by derivation."""
        try:
            import cognee

            await asyncio.wait_for(
                cognee.forget(dataset=self._dataset(player_id)),
                timeout=COGNEE_WRITE_TIMEOUT_S,
            )
        except asyncio.TimeoutError:
            logger.warning(
                "cognee.forget timed out after %.0fs; journal still wiped",
                COGNEE_WRITE_TIMEOUT_S,
            )
        except Exception:
            logger.warning("cognee.forget failed; journal still wiped", exc_info=True)
        try:
            # Session cache lives outside the dataset — wipe it too, or a
            # "forgotten" player's stale QA entries (and qa_ids) would leak
            # back in via _latest_qa_id on their next recall.
            from cognee.infrastructure.session.get_session_manager import (
                get_session_manager,
            )
            from cognee.modules.users.methods import get_default_user

            sm = get_session_manager()
            if sm.is_available:
                user = await get_default_user()
                await sm.delete_session(
                    user_id=str(user.id), session_id=self._session(player_id)
                )
        except Exception:
            logger.warning("session wipe failed during forget (non-fatal)", exc_info=True)
        self._journal_path(player_id).unlink(missing_ok=True)
        self._last_qa.pop(player_id, None)

    async def get_graph(self, player_id: str) -> dict:
        try:
            from cognee.infrastructure.databases.graph import get_graph_engine

            async def _fetch():
                engine = await get_graph_engine()
                return await engine.get_graph_data()

            nodes_raw, edges_raw = await asyncio.wait_for(
                _fetch(), timeout=COGNEE_RECALL_TIMEOUT_S
            )
            nodes, edges = [], []
            degree: dict[str, int] = {}
            for src, dst, *rest in edges_raw:
                degree[str(src)] = degree.get(str(src), 0) + 1
                degree[str(dst)] = degree.get(str(dst), 0) + 1
                props = rest[-1] if rest and isinstance(rest[-1], dict) else {}
                weight = props.get("weight") or props.get("feedback_weight")
                edges.append({"from": str(src), "to": str(dst), "weight": float(weight) if weight else 0.0})
            max_degree = max(degree.values(), default=1)
            for node_id, props in nodes_raw:
                label = (props or {}).get("name") or (props or {}).get("text", "")[:40] or str(node_id)
                nodes.append({"id": str(node_id), "label": str(label)})
            for edge in edges:  # degree-based fallback when no feedback weights
                if not edge["weight"]:
                    edge["weight"] = round(
                        max(degree.get(edge["from"], 1), degree.get(edge["to"], 1)) / max_degree, 3
                    )
            if nodes:
                return {"nodes": nodes, "edges": edges}
        except asyncio.TimeoutError:
            logger.warning(
                "get_graph timed out after %.0fs; degraded to journal fallback",
                COGNEE_RECALL_TIMEOUT_S,
            )
        except Exception:
            logger.warning("get_graph degraded to journal fallback", exc_info=True)
        return self._graph_from_journal(player_id)

    def _graph_from_journal(self, player_id: str) -> dict:
        topics: dict[str, int] = {}
        for e in self._journal_read(player_id):
            if e.event_type == "question_attempt" and e.topic:
                topics[e.topic] = topics.get(e.topic, 0) + 1
        nodes = [{"id": player_id, "label": player_id}] + [
            {"id": t, "label": t} for t in topics
        ]
        edges = [
            {"from": player_id, "to": t, "weight": min(1.0, n / 5)} for t, n in topics.items()
        ]
        return {"nodes": nodes, "edges": edges}


_service: Optional[CogneeMemoryService] = None


def get_memory_service() -> CogneeMemoryService:
    """Entry point backend/game/deps.py expects."""
    global _service
    if _service is None:
        _service = CogneeMemoryService()
    return _service
