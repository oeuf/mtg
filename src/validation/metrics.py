"""Validation metrics for ranking quality."""

from typing import List


def precision_at_k(recommendations: List[str], reference: List[str], k: int) -> float:
    """Calculate Precision@K.

    Precision@K = (# relevant items in top-K) / K

    Args:
        recommendations: Ranked list of recommended cards
        reference: Set of cards in reference deck
        k: Number of top recommendations to consider

    Returns:
        Precision score between 0.0 and 1.0
    """
    if k == 0 or len(recommendations) == 0:
        return 0.0

    top_k = recommendations[:k]
    reference_set = set(reference)

    relevant_count = sum(1 for card in top_k if card in reference_set)

    return relevant_count / k


def recall_at_k(recommendations: List[str], reference: List[str], k: int) -> float:
    """Calculate Recall@K.

    Recall@K = (# relevant items in top-K) / (total # relevant items)

    Args:
        recommendations: Ranked list of recommended cards
        reference: Set of cards in reference deck
        k: Number of top recommendations to consider

    Returns:
        Recall score between 0.0 and 1.0
    """
    if len(reference) == 0:
        return 0.0

    top_k = recommendations[:k]
    reference_set = set(reference)

    relevant_count = sum(1 for card in top_k if card in reference_set)

    return relevant_count / len(reference)


def mean_reciprocal_rank(recommendations: List[str], reference: List[str]) -> float:
    """Calculate Mean Reciprocal Rank (MRR).

    MRR = 1 / (rank of first relevant item)

    Args:
        recommendations: Ranked list of recommended cards
        reference: Set of cards in reference deck

    Returns:
        MRR score between 0.0 and 1.0
    """
    reference_set = set(reference)

    for rank, card in enumerate(recommendations, start=1):
        if card in reference_set:
            return 1.0 / rank

    return 0.0  # No relevant items found
