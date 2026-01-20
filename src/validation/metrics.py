"""Validation metrics for recommendation quality."""

from typing import Optional


def mean_reciprocal_rank(reference: set[str], ranked: list[str]) -> float:
    """Calculate Mean Reciprocal Rank (MRR).

    For each reference card, find its rank in the recommendations.
    MRR = average of (1/rank) for all reference cards.

    Args:
        reference: Set of card names that should be recommended
        ranked: Ordered list of recommended card names

    Returns:
        MRR score between 0 and 1 (higher is better)
    """
    if not reference:
        return 0.0

    total_reciprocal = 0.0

    for card in reference:
        if card in ranked:
            rank = ranked.index(card) + 1  # 1-indexed
            total_reciprocal += 1.0 / rank
        # Cards not found contribute 0

    return total_reciprocal / len(reference)


def overlap_at_k(reference: set[str], ranked: list[str], k: int) -> float:
    """Calculate what percentage of reference cards appear in top K.

    Args:
        reference: Set of card names that should be recommended
        ranked: Ordered list of recommended card names
        k: Number of top recommendations to consider

    Returns:
        Overlap percentage between 0 and 1
    """
    if not reference:
        return 0.0

    top_k = set(ranked[:k])
    overlap = reference & top_k

    return len(overlap) / len(reference)


def find_missing_cards(
    reference: set[str],
    ranked: list[str],
    k: int,
    include_ranks: bool = False
) -> list:
    """Find reference cards not in top K recommendations.

    Args:
        reference: Set of card names that should be recommended
        ranked: Ordered list of recommended card names
        k: Number of top recommendations to consider
        include_ranks: If True, return (card, rank) tuples for found cards

    Returns:
        List of missing card names, or (name, rank) tuples if include_ranks
    """
    top_k = set(ranked[:k])
    missing_from_top_k = reference - top_k

    if not include_ranks:
        return list(missing_from_top_k)

    # Find actual ranks for missing cards
    result = []
    for card in missing_from_top_k:
        if card in ranked:
            rank = ranked.index(card) + 1
            result.append((card, rank))
        else:
            result.append((card, None))  # Not in list at all

    return sorted(result, key=lambda x: x[1] if x[1] else float('inf'))
