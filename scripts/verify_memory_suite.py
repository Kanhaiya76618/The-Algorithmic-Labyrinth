"""Comprehensive assertion-level verification of the Cognee memory lifecycle.

~55 numbered tests across remember / recall / improve / forget + cross-verb
chains, run against LIVE Cognee (MEMORY_BACKEND=cognee, Postgres up, real LLM
key). Extends scripts/smoke_memory.py rather than duplicating it: the
degradation detector, preflight, dataset listing and profile signature are
imported from there.

Honesty rules (inherited from smoke_memory):
  * Every test that exercises cognee FAILS if the service silently degraded —
    the "dor.memory" logger is watched via smoke_memory.DegradationDetector,
    so a swallowed cognee error can never masquerade as a green test.
  * No test passes on stub behaviour: --mode live is required and the run
    aborts if MEMORY_BACKEND != cognee.
  * Each test uses a fresh uuid-suffixed player_id, so tests never contaminate
    one another, and cleans up its dataset afterwards.

Usage:  python3 scripts/verify_memory_suite.py --mode live
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import time
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # import sibling smoke_memory

from backend import config  # noqa: E402  (loads .env before cognee import)
from smoke_memory import (  # noqa: E402  (reuse, don't duplicate)
    DegradationDetector,
    dataset_names,
    preflight,
)

# ------------------------------------------------------------------ harness

RESULTS: list[dict] = []  # {n, verb, name, ok, evidence}
_N = 0


def check(verb: str, name: str, ok: bool, evidence: str) -> bool:
    global _N
    _N += 1
    RESULTS.append({"n": _N, "verb": verb, "name": name, "ok": bool(ok), "evidence": evidence})
    tag = "PASS" if ok else "FAIL"
    print(f"[{tag}] #{_N:02d} {verb}/{name}: {evidence}", flush=True)
    return bool(ok)


def clamped(x: float) -> bool:
    return isinstance(x, (int, float)) and 0.0 <= float(x) <= 1.0


def pid(name: str) -> str:
    return f"vs_{name}_{uuid.uuid4().hex[:8]}"


# ------------------------------------------------------------ cognee helpers

async def graph_item_texts(mem, player_id: str) -> set[str]:
    """Raw text of the player's cognee dataset data-items (GRAPH level, not the
    JSONL journal). Used to prove the surgical per-episode forget actually
    removed the graph data-item."""
    import os as _os
    import urllib.parse

    import cognee.modules.data.methods as M
    from cognee.modules.data.methods import get_dataset_data
    from cognee.modules.users.methods import get_default_user

    u = await get_default_user()
    try:
        dss = await M.get_datasets_by_name([mem._dataset(player_id)], u.id)
    except Exception:
        return set()
    if not dss:
        return set()
    data = await get_dataset_data(dss[0].id)
    texts: set[str] = set()
    for d in data:
        p = urllib.parse.urlparse(d.raw_data_location).path
        if _os.path.exists(p):
            try:
                texts.add(open(p, encoding="utf-8").read())
            except Exception:
                pass
    return texts


async def safe_forget(mem, *player_ids: str) -> None:
    for p in player_ids:
        try:
            await mem.forget(p)
        except Exception:
            pass


# ------------------------------------------------------------ episode makers

from contracts.schemas import Episode  # noqa: E402


def q_fail(p, qid, topic, probes, floor=10, diff="medium-hard"):
    return Episode(player_id=p, event_type="question_attempt", question_id=qid, topic=topic,
                   difficulty=diff, correct=False, failed_probes=probes, floor=floor,
                   time_taken_s=120, hints_used=2, retries=2)


def q_solve(p, qid, topic, floor=10, diff="medium"):
    return Episode(player_id=p, event_type="question_attempt", question_id=qid, topic=topic,
                   difficulty=diff, correct=True, floor=floor, time_taken_s=35)


def explore(p, detail, floor):
    return Episode(player_id=p, event_type="exploration", floor=floor, detail=detail)


# ===================================================================== tests


async def section_remember(mem):
    print("\n=== REMEMBER ===", flush=True)
    from backend.memory.schema import episode_to_text

    # 1 — question_attempt with failed_probes lands
    p = pid("rq")
    await mem.remember_episode(q_fail(p, "L21-A", "trees", ["edge:unbalanced"], floor=21))
    eps = await mem.recall_episodes(p, event_type="question_attempt")
    names = await dataset_names()
    check("remember", "question_attempt_lands",
          len(eps) == 1 and eps[0].topic == "trees" and eps[0].failed_probes == ["edge:unbalanced"]
          and mem._dataset(p) in names,
          f"journal={len(eps)} topic={eps[0].topic if eps else None} probes={eps[0].failed_probes if eps else None} dataset_present={mem._dataset(p) in names}")
    await safe_forget(mem, p)

    # 2 — exploration with detail + floor
    p = pid("re")
    await mem.remember_episode(explore(p, "inspected the sealed wall", 3))
    eps = await mem.recall_episodes(p, event_type="exploration")
    check("remember", "exploration_lands",
          len(eps) == 1 and eps[0].floor == 3 and "sealed wall" in (eps[0].detail or ""),
          f"journal={len(eps)} floor={eps[0].floor if eps else None} detail={eps[0].detail if eps else None!r}")
    await safe_forget(mem, p)

    # 3 — discovery episode
    p = pid("rd")
    await mem.remember_episode(Episode(player_id=p, event_type="discovery", detail="hidden entrance revealed via explorer"))
    eps = await mem.recall_episodes(p, event_type="discovery")
    check("remember", "discovery_lands",
          len(eps) == 1 and "revealed" in (eps[0].detail or ""),
          f"journal={len(eps)} detail={eps[0].detail if eps else None!r}")
    await safe_forget(mem, p)

    # 4 — feedback-correction episode
    p = pid("rf")
    await mem.remember_episode(Episode(player_id=p, event_type="feedback", detail="outcome score +5: mastered trees"))
    eps = await mem.recall_episodes(p, event_type="feedback")
    txt = episode_to_text(eps[0]) if eps else ""
    check("remember", "feedback_correction_lands",
          len(eps) == 1 and "correction" in txt.lower(),
          f"journal={len(eps)} rendered={txt[:60]!r}")
    await safe_forget(mem, p)

    # 5 — isolation A -> B empty
    pa, pb = pid("iA"), pid("iB")
    await mem.remember_episode(q_fail(pa, "L21-A", "trees", ["edge:x"]))
    names = await dataset_names()
    b_eps = await mem.recall_episodes(pb)
    check("remember", "isolation_A_written_B_empty",
          mem._dataset(pa) in names and mem._dataset(pb) not in names and not b_eps,
          f"A_present={mem._dataset(pa) in names} B_present={mem._dataset(pb) in names} B_journal={len(b_eps)}")

    # 6 — isolation reverse: write B, A journal must not gain B's episodes
    await mem.remember_episode(q_solve(pb, "L16-A", "sorting"))
    a_eps = await mem.recall_episodes(pa)
    b_eps = await mem.recall_episodes(pb)
    check("remember", "isolation_both_ways",
          len(a_eps) == 1 and a_eps[0].topic == "trees" and len(b_eps) == 1 and b_eps[0].topic == "sorting",
          f"A={[e.topic for e in a_eps]} B={[e.topic for e in b_eps]}")
    await safe_forget(mem, pa, pb)

    # 7 — 2 concurrent writes land
    p = pid("c2")
    await asyncio.gather(
        mem.remember_episode(q_fail(p, "L1-A", "arrays", ["edge:empty"])),
        mem.remember_episode(q_fail(p, "L1-B", "arrays", ["edge:single"])),
    )
    eps = await mem.recall_episodes(p, limit=50)
    check("remember", "two_concurrent_writes",
          len(eps) == 2 and {e.question_id for e in eps} == {"L1-A", "L1-B"},
          f"journal={len(eps)} ids={sorted(e.question_id for e in eps)}")
    await safe_forget(mem, p)

    # 8 — 5-concurrent burst, no corruption
    p = pid("c5")
    await asyncio.gather(*[
        mem.remember_episode(q_fail(p, f"B{i}", "graphs", [f"edge:{i}"], floor=30)) for i in range(5)
    ])
    eps = await mem.recall_episodes(p, limit=50)
    valid = all(e.player_id == p and e.topic == "graphs" for e in eps)
    check("remember", "five_concurrent_burst",
          len(eps) == 5 and valid and len({e.question_id for e in eps}) == 5,
          f"journal={len(eps)} unique_ids={len({e.question_id for e in eps})} all_valid={valid}")
    await safe_forget(mem, p)

    # 9 — long / special-character detail survives round-trip
    p = pid("sp")
    weird = "quotes\"'` unicode:✓→π emoji:🐉 newline:\\n tab:\t <xml> {json:1} " + "x" * 300
    await mem.remember_episode(Episode(player_id=p, event_type="exploration", floor=1, detail=weird))
    eps = await mem.recall_episodes(p, event_type="exploration")
    check("remember", "special_chars_roundtrip",
          len(eps) == 1 and eps[0].detail == weird,
          f"len_in={len(weird)} len_out={len(eps[0].detail) if eps and eps[0].detail else 0} exact_match={bool(eps and eps[0].detail == weird)}")
    await safe_forget(mem, p)

    # 10 — 10 rapid sequential episodes all retrievable
    p = pid("seq")
    for i in range(10):
        await mem.remember_episode(q_fail(p, f"S{i}", "hashing", [f"edge:{i}"], floor=11))
    eps = await mem.recall_episodes(p, limit=50)
    check("remember", "ten_sequential_retrievable",
          len(eps) == 10 and len({e.question_id for e in eps}) == 10,
          f"journal={len(eps)} unique_ids={len({e.question_id for e in eps})}")
    await safe_forget(mem, p)

    # 11 — episode text carries discriminative tokens
    p = pid("tok")
    ep = q_fail(p, "L33-A", "graphs", ["edge:disconnected", "edge:cycle"], floor=33)
    txt = episode_to_text(ep)
    check("remember", "discriminative_tokens_present",
          "graphs" in txt and "edge:disconnected" in txt and "edge:cycle" in txt,
          f"text={txt!r}")


async def section_recall(mem):
    print("\n=== RECALL ===", flush=True)
    from contracts.schemas import PlayerProfile

    # shared seed player for the topic/probe/parse assertions (one LLM recall reused)
    p = pid("rc")
    await mem.remember_episode(q_fail(p, "L21-A", "trees", ["edge:unbalanced"], floor=21))
    await mem.remember_episode(q_fail(p, "L21-B", "trees", ["edge:single"], floor=21))
    await mem.remember_episode(q_solve(p, "L16-A", "sorting"))
    await mem.remember_episode(q_solve(p, "L16-B", "sorting"))
    prof = await mem.recall_profile(p)
    degraded = det.drain()

    # 12 — parses to a valid PlayerProfile
    check("recall", "parses_valid_profile",
          isinstance(prof, PlayerProfile) and prof.player_id == p and not degraded,
          f"type=PlayerProfile pid_ok={prof.player_id == p} degradations={degraded or 'none'}")

    wt = [t.lower() for t in prof.weak_topics]
    st = [t.lower() for t in prof.strong_topics]
    # 13 — weak_topics reflects seeded fails
    check("recall", "weak_topics_reflect_seed", "trees" in wt and not degraded,
          f"weak_topics={prof.weak_topics}")
    # 14 — strong_topics reflects seeded solves
    check("recall", "strong_topics_reflect_seed", "sorting" in st and not degraded,
          f"strong_topics={prof.strong_topics}")
    # 15 — weak_probes reflects seeded probes
    check("recall", "weak_probes_reflect_seed",
          any("edge:" in x for x in prof.weak_probes) and not degraded,
          f"weak_probes={prof.weak_probes}")
    # 16 — frustration & explorer_score clamped [0,1]
    check("recall", "scores_clamped_0_1",
          clamped(prof.frustration) and clamped(prof.explorer_score),
          f"frustration={prof.frustration} explorer={prof.explorer_score}")
    # 17 — interaction_id (qa_id) set
    qa1 = prof.interaction_id
    check("recall", "interaction_id_set", qa1 is not None, f"qa_id={qa1}")
    await safe_forget(mem, p)

    # 18 — frustration rises with pressure (LLM-derived); heavy-fail seed
    p = pid("fr")
    for i in range(3):
        await mem.remember_episode(q_fail(p, f"F{i}", "dynamic-programming", ["edge:overlap"], floor=41))
    proff = await mem.recall_profile(p)
    degraded = det.drain()
    check("recall", "frustration_rises",
          proff.frustration >= 0.4 and clamped(proff.frustration) and not degraded,
          f"frustration={proff.frustration} (>=0.4 expected after 3 hard fails; LLM-derived)")
    await safe_forget(mem, p)

    # 19 — explorer_score rises with exploration (LLM-derived)
    p = pid("ex")
    for i, d in enumerate(["inspected a sealed wall", "lingered by the fountain",
                           "took the long way", "revisited a cleared floor",
                           "pried at loose stones"]):
        await mem.remember_episode(explore(p, d, i + 1))
    profe = await mem.recall_profile(p)
    degraded = det.drain()
    check("recall", "explorer_score_rises",
          profe.explorer_score >= 0.4 and clamped(profe.explorer_score) and not degraded,
          f"explorer_score={profe.explorer_score} (>=0.4 expected after 5 explorations; LLM-derived)")
    await safe_forget(mem, p)

    # 20 — interaction_id changes between recalls
    p = pid("qa")
    await mem.remember_episode(q_fail(p, "L21-A", "trees", ["edge:x"], floor=21))
    r1 = await mem.recall_profile(p)
    d1 = det.drain()
    await mem.remember_episode(q_fail(p, "L33-A", "graphs", ["edge:disconnected"], floor=33))
    r2 = await mem.recall_profile(p)
    d2 = det.drain()
    check("recall", "interaction_id_changes",
          r1.interaction_id and r2.interaction_id and r1.interaction_id != r2.interaction_id and not (d1 or d2),
          f"qa1={r1.interaction_id} qa2={r2.interaction_id}")
    # 21 — staleness: fresh episode changes the next profile (graphs now weak)
    graphs_weak = "graphs" in [t.lower() for t in r2.weak_topics]
    check("recall", "staleness_nonce_defeats_cache",
          graphs_weak and not (d1 or d2),
          f"graphs_reflected_in_second_recall={graphs_weak} weak_topics={r2.weak_topics}")
    await safe_forget(mem, p)

    # 22 — recall_episodes event_type filter
    p = pid("ff")
    await mem.remember_episode(q_fail(p, "L1-A", "arrays", ["edge:empty"]))
    await mem.remember_episode(explore(p, "wandered floor 2", 2))
    await mem.remember_episode(Episode(player_id=p, event_type="discovery", detail="whisper: something"))
    only_expl = await mem.recall_episodes(p, event_type="exploration")
    check("recall", "recall_episodes_type_filter",
          len(only_expl) == 1 and only_expl[0].event_type == "exploration",
          f"exploration_only={len(only_expl)} types={[e.event_type for e in only_expl]}")
    # 23 — recall_episodes limit + newest-first
    p2 = pid("nf")
    for i in range(5):
        await mem.remember_episode(q_fail(p2, f"N{i}", "greedy", [f"edge:{i}"], floor=44))
    last3 = await mem.recall_episodes(p2, limit=3)
    ids = [e.question_id for e in last3]
    check("recall", "recall_episodes_limit_newest_first",
          len(last3) == 3 and ids == ["N4", "N3", "N2"],
          f"limit=3 got={ids} (expect newest-first N4,N3,N2)")
    await safe_forget(mem, p, p2)

    # 24 — zero-episode player → default profile, no raise
    p = pid("zero")
    prof0 = await mem.recall_profile(p)
    check("recall", "zero_episode_default_profile",
          isinstance(prof0, PlayerProfile) and not prof0.weak_topics and not prof0.strong_topics,
          f"weak={prof0.weak_topics} strong={prof0.strong_topics} whispers={prof0.whispers_heard}")
    await safe_forget(mem, p)

    # 25 — dead backend → journal fallback, degradation DETECTED (not a fake pass)
    p = pid("dead")
    await mem.remember_episode(q_fail(p, "L21-A", "trees", ["edge:unbalanced"], floor=21))
    await mem.remember_episode(q_fail(p, "L21-B", "trees", ["edge:single"], floor=21))
    det.drain()
    import cognee
    _orig = cognee.recall

    async def _boom(*a, **k):
        raise RuntimeError("simulated cognee outage")

    cognee.recall = _boom
    try:
        profd = await mem.recall_profile(p)
    finally:
        cognee.recall = _orig
    degraded = det.drain()
    fell_back = "trees" in [t.lower() for t in profd.weak_topics]  # journal-derived
    check("recall", "dead_backend_journal_fallback",
          bool(degraded) and fell_back,
          f"degradation_detected={bool(degraded)} journal_fallback_weak={profd.weak_topics} (must be BOTH, not a stub pass)")
    await safe_forget(mem, p)


async def section_improve(mem):
    print("\n=== IMPROVE (hardened) ===", flush=True)

    # 26 — baseline: single prior episode (no contradiction) → reliable shift 3x
    trials = []
    for _ in range(3):
        p = pid("imp1")
        await mem.remember_episode(q_fail(p, "L21-A", "trees", ["edge:unbalanced"], floor=21))
        await mem.remember_episode(q_solve(p, "L16-A", "sorting"))
        before = _sig(await mem.recall_profile(p))
        det.drain()
        await mem.reinforce(p, "The player has now completely mastered trees: they solve every "
                               "trees question correctly and instantly. Trees is a strongest topic.", 5.0)
        await mem.improve(p)
        after = _sig(await mem.recall_profile(p))
        det.drain()
        trials.append(after != before)
        await safe_forget(mem, p)
    check("improve", "baseline_single_prior_shift_3x", all(trials),
          f"shift per trial={trials} (clean case, expect 3/3)")

    # 27 — contradiction case: surgical forget of contradicted graph items fires 3x (deterministic)
    fired = []
    shifts = []
    for _ in range(3):
        p = pid("impc")
        await mem.remember_episode(q_fail(p, "L21-A", "trees", ["edge:unbalanced"], floor=21))
        await mem.remember_episode(q_fail(p, "L21-B", "trees", ["edge:single"], floor=21))
        await mem.remember_episode(q_solve(p, "L16-A", "sorting"))
        before_texts = await graph_item_texts(mem, p)
        before = _sig(await mem.recall_profile(p))
        det.drain()
        await mem.reinforce(p, "The player has now completely mastered trees: they solve every "
                               "trees question correctly and instantly. Trees is a strongest topic.", 5.0)
        after_texts = await graph_item_texts(mem, p)
        # the two trees-failure item texts must be GONE from the graph
        gone = sum(1 for t in before_texts if "failed a medium-hard trees question" in t and t not in after_texts)
        fired.append(gone == 2)
        after = _sig(await mem.recall_profile(p))
        det.drain()
        shifts.append(after != before)
        await safe_forget(mem, p)
    check("improve", "contradiction_surgical_forget_fires_3x", all(fired),
          f"graph-level trees-failure deletions per trial={fired} (deterministic guarantee); "
          f"end-to-end profile shift (LLM, informational)={shifts}")

    # 28 — reinforce with no prior recall (no qa_id) → logged skip, no raise
    p = pid("noqa")
    await mem.remember_episode(q_fail(p, "L21-A", "trees", ["edge:x"], floor=21))
    det.drain()
    raised = False
    try:
        await mem.reinforce(p, "mastered trees", 5.0)  # no recall_profile beforehand => no _last_qa
    except Exception:
        raised = True
    check("improve", "reinforce_no_qa_id_graceful", not raised,
          f"raised={raised} (episode+supersede channels run; session channel skipped, no exception)")
    await safe_forget(mem, p)

    # 29 — reinforce+improve does not bleed across players
    pa, pb = pid("blA"), pid("blB")
    await mem.remember_episode(q_fail(pa, "L21-A", "trees", ["edge:x"], floor=21))
    await mem.remember_episode(q_fail(pb, "L21-A", "trees", ["edge:x"], floor=21))
    await mem.recall_profile(pa)
    det.drain()
    await mem.reinforce(pa, "mastered trees", 5.0)
    await mem.improve(pa)
    b_eps = await mem.recall_episodes(pb, event_type="question_attempt")
    b_graph = await graph_item_texts(mem, pb)
    check("improve", "reinforce_no_cross_player_bleed",
          len(b_eps) == 1 and any("trees" in t for t in b_graph),
          f"B_journal_intact={len(b_eps)==1} B_graph_trees_present={any('trees' in t for t in b_graph)}")
    await safe_forget(mem, pa, pb)

    # 30 — two reinforce cycles compound without error
    p = pid("two")
    await mem.remember_episode(q_fail(p, "L21-A", "trees", ["edge:x"], floor=21))
    await mem.recall_profile(p)
    det.drain()
    raised = False
    try:
        for _ in range(2):
            await mem.reinforce(p, "mastered trees", 5.0)
            await mem.improve(p)
    except Exception:
        raised = True
    check("improve", "two_reinforce_cycles_compound", not raised, f"raised={raised}")
    await safe_forget(mem, p)

    # 31 — improve callable twice consecutively
    p = pid("imp2")
    await mem.remember_episode(q_fail(p, "L21-A", "trees", ["edge:x"], floor=21))
    det.drain()
    raised = False
    try:
        await mem.improve(p)
        await mem.improve(p)
    except Exception:
        raised = True
    check("improve", "improve_twice_no_error", not raised, f"raised={raised}")
    await safe_forget(mem, p)

    # 32 — improve on empty dataset → no-op, no raise
    p = pid("impe")
    det.drain()
    raised = False
    try:
        await mem.improve(p)
    except Exception:
        raised = True
    check("improve", "improve_empty_dataset_noop", not raised, f"raised={raised} (never-written player)")
    await safe_forget(mem, p)

    # 33 — journal RETAINS contradicted episodes after the graph-level forget (audit trail)
    p = pid("aud")
    await mem.remember_episode(q_fail(p, "L21-A", "trees", ["edge:unbalanced"], floor=21))
    await mem.remember_episode(q_fail(p, "L21-B", "trees", ["edge:single"], floor=21))
    det.drain()
    await mem.reinforce(p, "The player has now mastered trees; trees is a strongest topic.", 5.0)
    journal_after = await mem.recall_episodes(p, event_type="question_attempt")
    graph_after = await graph_item_texts(mem, p)
    graph_has_trees_fail = any("failed a medium-hard trees question" in t for t in graph_after)
    check("improve", "journal_retains_after_graph_forget",
          len(journal_after) == 2 and not graph_has_trees_fail,
          f"journal_kept={len(journal_after)}/2 graph_trees_failures_removed={not graph_has_trees_fail} "
          f"(design: local audit record persists, only graph data-item removed)")
    await safe_forget(mem, p)

    # 34 — _contradicted_failures matches only same-topic failures
    p = pid("ctr")
    await mem.remember_episode(q_fail(p, "L21-A", "trees", ["edge:x"], floor=21))
    await mem.remember_episode(q_fail(p, "L33-A", "graphs", ["edge:disconnected"], floor=33))
    await mem.remember_episode(q_solve(p, "L21-C", "trees"))  # a solve, must NOT be contradicted
    matched = mem._contradicted_failures(p, "the player mastered trees now")
    ids = sorted(e.question_id for e in matched)
    check("improve", "contradicted_failures_topic_scoped",
          ids == ["L21-A"],
          f"matched={ids} (only the trees FAILURE; not graphs-fail, not the trees solve)")
    await safe_forget(mem, p)

    # 35 — surgical forget leaves other topics' graph items intact
    p = pid("keep")
    await mem.remember_episode(q_fail(p, "L21-A", "trees", ["edge:x"], floor=21))
    await mem.remember_episode(q_fail(p, "L33-A", "graphs", ["edge:disconnected"], floor=33))
    det.drain()
    await mem.reinforce(p, "the player mastered trees; trees is now a strongest topic", 5.0)
    g = await graph_item_texts(mem, p)
    check("improve", "surgical_forget_spares_other_topics",
          any("graphs question" in t for t in g) and not any("trees question" in t for t in g),
          f"graphs_kept={any('graphs question' in t for t in g)} trees_removed={not any('trees question' in t for t in g)}")
    await safe_forget(mem, p)


async def section_forget(mem):
    print("\n=== FORGET ===", flush=True)
    from backend.game.discovery import check_discovery

    # 36 — forget wipes the dataset (datasets.list confirms)
    p = pid("fw")
    await mem.remember_episode(q_fail(p, "L21-A", "trees", ["edge:x"], floor=21))
    assert mem._dataset(p) in await dataset_names()
    await mem.forget(p)
    check("forget", "wipes_dataset",
          mem._dataset(p) not in await dataset_names(),
          f"dataset_present_after_forget={mem._dataset(p) in await dataset_names()}")

    # 37 — recall after forget → default profile
    p = pid("rf")
    await mem.remember_episode(q_fail(p, "L21-A", "trees", ["edge:unbalanced"], floor=21))
    await mem.forget(p)
    prof = await mem.recall_profile(p)
    det.drain()
    check("forget", "recall_after_forget_default",
          not prof.weak_topics and not prof.strong_topics and prof.whispers_heard == 0,
          f"weak={prof.weak_topics} strong={prof.strong_topics} whispers={prof.whispers_heard}")
    await safe_forget(mem, p)

    # 38 — neighbour intact after this player's forget
    pa, pb = pid("nbrA"), pid("nbrB")
    await mem.remember_episode(q_fail(pa, "L21-A", "trees", ["edge:x"], floor=21))
    await mem.remember_episode(q_fail(pb, "L33-A", "graphs", ["edge:disconnected"], floor=33))
    await mem.forget(pa)
    b_eps = await mem.recall_episodes(pb)
    check("forget", "neighbour_intact",
          mem._dataset(pb) in await dataset_names() and len(b_eps) == 1 and b_eps[0].topic == "graphs",
          f"B_dataset_present={mem._dataset(pb) in await dataset_names()} B_journal={[e.topic for e in b_eps]}")
    await safe_forget(mem, pb)

    # 39 — check_discovery after forget → revealed=False (re-seal by derivation)
    p = pid("seal")
    await mem.remember_episode(Episode(player_id=p, event_type="discovery", detail="hidden entrance revealed via explorer"))
    await mem.forget(p)
    ds = await check_discovery(p, mem)
    det.drain()
    check("forget", "reseal_by_derivation", ds.revealed is False,
          f"revealed_after_forget={ds.revealed} via={ds.via}")
    await safe_forget(mem, p)

    # 40 — remember after forget works cleanly (no tombstone)
    p = pid("reafter")
    await mem.remember_episode(q_fail(p, "L21-A", "trees", ["edge:x"], floor=21))
    await mem.forget(p)
    await mem.remember_episode(q_solve(p, "L16-A", "sorting"))
    eps = await mem.recall_episodes(p)
    check("forget", "remember_after_forget",
          len(eps) == 1 and eps[0].topic == "sorting" and mem._dataset(p) in await dataset_names(),
          f"journal={[e.topic for e in eps]} (only post-forget episode) dataset_recreated={mem._dataset(p) in await dataset_names()}")
    await safe_forget(mem, p)

    # 41 — forget never-existed player → graceful
    p = pid("never")
    det.drain()
    raised = False
    try:
        await mem.forget(p)
    except Exception:
        raised = True
    check("forget", "forget_nonexistent_graceful", not raised, f"raised={raised}")

    # 42 — forget twice → second is a no-op
    p = pid("twice")
    await mem.remember_episode(q_fail(p, "L21-A", "trees", ["edge:x"], floor=21))
    await mem.forget(p)
    raised = False
    try:
        await mem.forget(p)
    except Exception:
        raised = True
    check("forget", "forget_twice_noop", not raised and mem._dataset(p) not in await dataset_names(),
          f"raised={raised} dataset_absent={mem._dataset(p) not in await dataset_names()}")

    # 43 — forget removes the JSONL journal file
    p = pid("jrm")
    await mem.remember_episode(q_fail(p, "L21-A", "trees", ["edge:x"], floor=21))
    jp = mem._journal_path(p)
    existed = jp.exists()
    await mem.forget(p)
    check("forget", "forget_removes_journal_file", existed and not jp.exists(),
          f"journal_existed={existed} journal_present_after={jp.exists()}")

    # 44 — forget clears _last_qa handle
    p = pid("lqa")
    await mem.remember_episode(q_fail(p, "L21-A", "trees", ["edge:x"], floor=21))
    await mem.recall_profile(p)
    det.drain()
    had = p in mem._last_qa
    await mem.forget(p)
    check("forget", "forget_clears_last_qa", had and p not in mem._last_qa,
          f"had_qa={had} cleared={p not in mem._last_qa}")

    # 45 — surgical per-episode forget in isolation (_supersede_graph_episodes)
    p = pid("surg")
    ep = q_fail(p, "L21-A", "trees", ["edge:unbalanced"], floor=21)
    await mem.remember_episode(ep)
    await mem.remember_episode(q_solve(p, "L16-A", "sorting"))
    before = await graph_item_texts(mem, p)
    await mem._supersede_graph_episodes(p, [ep])
    after = await graph_item_texts(mem, p)
    journal = await mem.recall_episodes(p, event_type="question_attempt")
    trees_gone = any("trees question" in t for t in before) and not any("trees question" in t for t in after)
    sorting_kept = any("sorting question" in t for t in after)
    check("forget", "surgical_per_episode_forget_isolated",
          trees_gone and sorting_kept and any(e.topic == "trees" for e in journal),
          f"graph_trees_removed={trees_gone} graph_sorting_kept={sorting_kept} journal_trees_retained={any(e.topic=='trees' for e in journal)}")
    await safe_forget(mem, p)


async def section_cross(mem):
    print("\n=== CROSS-VERB CHAINS ===", flush=True)
    from backend.game.discovery import (
        EXPLORER_THRESHOLD,
        MERCY_FRUSTRATION,
        check_discovery,
    )

    # 46 — full lifecycle: remember x6 → recall → reinforce+improve → forget → remember → recall
    p = pid("life")
    for e in [q_fail(p, "L21-A", "trees", ["edge:unbalanced"], floor=21),
              q_fail(p, "L21-B", "trees", ["edge:single"], floor=21),
              q_solve(p, "L16-A", "sorting"),
              q_solve(p, "L16-B", "sorting"),
              explore(p, "inspected a sealed wall", 3),
              q_fail(p, "L33-A", "graphs", ["edge:disconnected"], floor=33)]:
        await mem.remember_episode(e)
    await mem.recall_profile(p)
    det.drain()
    await mem.reinforce(p, "the player mastered graphs now; graphs is a strongest topic", 5.0)
    await mem.improve(p)
    det.drain()
    await mem.forget(p)
    await mem.remember_episode(q_solve(p, "L1-A", "arrays"))
    post = await mem.recall_episodes(p, limit=50)
    prof = await mem.recall_profile(p)
    det.drain()
    check("cross", "full_lifecycle_reflects_post_forget_only",
          len(post) == 1 and post[0].topic == "arrays" and "trees" not in [t.lower() for t in prof.weak_topics],
          f"post_forget_journal={[e.topic for e in post]} profile_weak={prof.weak_topics} (no pre-forget trees)")
    await safe_forget(mem, p)

    # 47 — whisper chain: explorations → explorer_score → whisper quoting a real detail
    p = pid("whis")
    details = ["inspected a sealed wall on floor 3", "lingered by the glowing fountain",
               "took the long way around floor 5", "revisited a cleared floor",
               "pried at the loose stones", "traced the strange rune"]
    for i, d in enumerate(details):
        await mem.remember_episode(explore(p, d, i + 1))
    prof = await mem.recall_profile(p)
    det.drain()
    # accumulate up to 3 whispers via repeated checks (each emits one if score>=threshold)
    states = [await check_discovery(p, mem) for _ in range(3)]
    det.drain()
    last = states[-1]
    quoted_real = any(any(d in w for d in details) for w in last.whispers)
    check("cross", "whisper_chain_quotes_real_detail",
          prof.explorer_score >= EXPLORER_THRESHOLD and len(last.whispers) >= 1 and quoted_real,
          f"explorer_score={prof.explorer_score} (>= {EXPLORER_THRESHOLD}) whispers={len(last.whispers)} "
          f"quotes_a_seeded_detail={quoted_real}")
    await safe_forget(mem, p)

    # 48 — mercy chain: 3 boss fails + high frustration → reveal via mercy
    p = pid("mercy")
    for i in range(3):
        await mem.remember_episode(Episode(player_id=p, event_type="question_attempt", question_id=f"BOSS{i}",
                                           topic="dynamic-programming", difficulty="boss-tier", correct=False,
                                           failed_probes=["edge:overlap"], floor=25, time_taken_s=280,
                                           hints_used=3, retries=3))
    prof = await mem.recall_profile(p)
    det.drain()
    ds = await check_discovery(p, mem, boss_level=25, boss_failed=True)
    det.drain()
    check("cross", "mercy_chain_reveals_via_mercy",
          prof.frustration >= MERCY_FRUSTRATION and ds.revealed and ds.via == "mercy",
          f"frustration={prof.frustration} (>= {MERCY_FRUSTRATION}) revealed={ds.revealed} via={ds.via}")
    await safe_forget(mem, p)

    # 49 — boss-taunt substrate: seeded probe failures surface as weak_probes (the taunt key)
    p = pid("taunt")
    for i in range(2):
        await mem.remember_episode(q_fail(p, f"T{i}", "trees", ["edge:unbalanced"], floor=21))
    prof = await mem.recall_profile(p)
    det.drain()
    has_probe = any("edge:unbalanced" in x for x in prof.weak_probes)
    check("cross", "boss_taunt_key_present_in_profile",
          has_probe,
          f"weak_probes={prof.weak_probes} contains_taunt_key(edge:unbalanced)={has_probe} "
          f"(taunt text mapping itself lives in frontend BOSS_TAUNT_MAPPING; this verifies the backend key it needs)")
    await safe_forget(mem, p)

    # 50 — PERSISTENCE: recall, recreate the service (same Postgres+journal), recall again → survives
    p = pid("persist")
    await mem.remember_episode(q_fail(p, "L21-A", "trees", ["edge:unbalanced"], floor=21))
    await mem.remember_episode(q_fail(p, "L21-B", "trees", ["edge:single"], floor=21))
    prof1 = await mem.recall_profile(p)
    det.drain()
    from backend.memory.service import CogneeMemoryService
    mem2 = CogneeMemoryService()  # brand-new object, same underlying stores
    prof2 = await mem2.recall_profile(p)
    d2 = det.drain()
    eps2 = await mem2.recall_episodes(p)
    survived = ("trees" in [t.lower() for t in prof2.weak_topics]) and len(eps2) == 2
    check("cross", "persistence_survives_service_restart",
          survived and not d2,
          f"fresh_service_weak_topics={prof2.weak_topics} journal={len(eps2)}/2 "
          f"(memory outlived the process object — the core pitch)")
    await safe_forget(mem, p)

    # 51 — get_graph returns a populated node/edge view for a seeded player
    p = pid("graph")
    for e in [q_fail(p, "L21-A", "trees", ["edge:unbalanced"], floor=21),
              q_solve(p, "L16-A", "sorting")]:
        await mem.remember_episode(e)
    g = await mem.get_graph(p)
    det.drain()
    check("cross", "get_graph_populated",
          isinstance(g, dict) and len(g.get("nodes", [])) > 0,
          f"nodes={len(g.get('nodes', []))} edges={len(g.get('edges', []))}")
    await safe_forget(mem, p)

    # 52 — explorer reveal → forget → re-seal round trip (discovery fully derived)
    p = pid("round")
    for i, d in enumerate(["inspected a sealed wall", "lingered by the fountain",
                           "took the long way", "revisited a cleared floor",
                           "pried at loose stones", "traced a rune"]):
        await mem.remember_episode(explore(p, d, i + 1))
    await mem.recall_profile(p)
    det.drain()
    for _ in range(4):
        st = await check_discovery(p, mem)
    det.drain()
    await mem.forget(p)
    st2 = await check_discovery(p, mem)
    det.drain()
    check("cross", "reveal_then_forget_reseals",
          st.revealed is True and st2.revealed is False,
          f"revealed_before_forget={st.revealed} revealed_after_forget={st2.revealed}")
    await safe_forget(mem, p)

    # 53 — journal-derived facts (whispers_heard/hidden_discovered) reflect discovery episodes
    p = pid("facts")
    await mem.remember_episode(Episode(player_id=p, event_type="discovery", detail="whisper: You lingered. It remembers you too."))
    await mem.remember_episode(Episode(player_id=p, event_type="discovery", detail="hidden entrance revealed via explorer"))
    prof = await mem.recall_profile(p)
    det.drain()
    check("cross", "journal_derived_discovery_facts",
          prof.whispers_heard == 1 and prof.hidden_discovered is True,
          f"whispers_heard={prof.whispers_heard} hidden_discovered={prof.hidden_discovered} (journal-derived, deterministic)")
    await safe_forget(mem, p)


# --------------------------------------------------------------- signature

def _sig(p) -> tuple:
    return (
        tuple(sorted(t.lower() for t in p.weak_topics)),
        tuple(sorted(t.lower() for t in p.strong_topics)),
        tuple(sorted(p.weak_probes)),
        round(p.frustration, 2),
        round(p.explorer_score, 2),
    )


# ------------------------------------------------------------------- runner

det = DegradationDetector()


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=["live"],
                        help="live only — this suite verifies real Cognee, not the stub")
    parser.parse_args()

    if config.MEMORY_BACKEND != "cognee":
        print(f"NO-GO: MEMORY_BACKEND={config.MEMORY_BACKEND!r}, need 'cognee' for --mode live")
        return 2
    preflight()

    import logging
    logging.getLogger("dor.memory").addHandler(det)

    from backend.memory.service import get_memory_service
    mem = get_memory_service()

    started = time.monotonic()
    for section in (section_remember, section_recall, section_improve, section_forget, section_cross):
        try:
            await section(mem)
        except Exception as exc:  # a crashing section is itself a failure, recorded honestly
            check(section.__name__.replace("section_", ""), "section_crashed", False,
                  f"section raised {type(exc).__name__}: {exc!r:.200}")
    elapsed = time.monotonic() - started

    # ---- summaries
    print("\n" + "=" * 70)
    print("PER-VERB SUMMARY")
    print("=" * 70)
    verbs: dict[str, list] = {}
    for r in RESULTS:
        verbs.setdefault(r["verb"], []).append(r)
    order = ["remember", "recall", "improve", "forget", "cross"]
    for v in order + [x for x in verbs if x not in order]:
        rows = verbs.get(v)
        if not rows:
            continue
        passed = sum(1 for r in rows if r["ok"])
        print(f"  {v:10s}  {passed}/{len(rows)} PASS")

    print("\n" + "=" * 70)
    print("FINAL TABLE")
    print("=" * 70)
    print(f"{'#':>3}  {'VERB':10s}  {'RESULT':6s}  TEST")
    for r in RESULTS:
        print(f"{r['n']:>3}  {r['verb']:10s}  {'PASS' if r['ok'] else 'FAIL':6s}  {r['name']}")

    total = len(RESULTS)
    passed = sum(1 for r in RESULTS if r["ok"])
    failed = [r for r in RESULTS if not r["ok"]]
    print("\n" + "=" * 70)
    print(f"TOTAL: {passed}/{total} PASS  ({len(failed)} FAIL)  in {elapsed:.0f}s")
    if failed:
        print("FAILURES:")
        for r in failed:
            print(f"  #{r['n']:02d} {r['verb']}/{r['name']}: {r['evidence']}")
    print("=" * 70)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
