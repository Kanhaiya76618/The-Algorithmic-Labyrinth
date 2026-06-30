"""Role A — the native Cognee feedback loop, isolated here.

NOTE: API signatures below target cognee 1.1.2 and are moving fast.
Re-confirm against the pinned version before the rest of the team relies
on the return shapes. Keep ALL Cognee-version-sensitive code in this file
and service.py so churn never touches other slices.
"""
from __future__ import annotations


async def recall_with_interaction(query: str):
    """Run a graph-completion recall and keep the interaction so a reward
    can later be attached to the exact graph elements that answered."""
    import cognee
    from cognee import SearchType
    result = await cognee.search(
        query_text=query,
        query_type=SearchType.GRAPH_COMPLETION,
        save_interaction=True,
    )
    return result


async def apply_reward(outcome_text: str, score: int = 0, last_k: int = 1):
    """Attach the game outcome as feedback on the last recall, then let
    improve() propagate it into feedback_weight edges."""
    import cognee
    from cognee import SearchType
    await cognee.search(
        query_text=outcome_text,
        query_type=SearchType.FEEDBACK,
        last_k=last_k,
    )
    await cognee.improve()
