"""Unit tests for validation metrics."""

from src.validation.metrics import (
    mean_reciprocal_rank,
    overlap_at_k,
    find_missing_cards
)


def test_mrr_perfect_ranking():
    """Test MRR when all reference cards are ranked first."""
    reference = {"A", "B", "C"}
    ranked = ["A", "B", "C", "D", "E"]

    mrr = mean_reciprocal_rank(reference, ranked)

    # Perfect ranking: 1/1 + 1/2 + 1/3 = 1.833, avg = 0.611
    assert abs(mrr - 0.611) < 0.01


def test_mrr_worst_ranking():
    """Test MRR when reference cards are at the end."""
    reference = {"A", "B"}
    ranked = ["X", "Y", "Z", "A", "B"]

    mrr = mean_reciprocal_rank(reference, ranked)

    # A at rank 4, B at rank 5: (1/4 + 1/5) / 2 = 0.225
    assert abs(mrr - 0.225) < 0.01


def test_mrr_missing_cards():
    """Test MRR when some reference cards not in ranking."""
    reference = {"A", "B", "C"}
    ranked = ["A", "X", "Y"]

    mrr = mean_reciprocal_rank(reference, ranked)

    # Only A found at rank 1: 1/3 * (1/1 + 0 + 0) = 0.333
    assert abs(mrr - 0.333) < 0.01


def test_overlap_at_k():
    """Test overlap percentage calculation."""
    reference = {"A", "B", "C", "D", "E"}  # 5 cards
    ranked = ["A", "B", "X", "Y", "Z"]

    # Top 5 contains A, B from reference = 40%
    overlap = overlap_at_k(reference, ranked, k=5)
    assert abs(overlap - 0.40) < 0.01

    # Top 2 contains A, B from reference = 40%
    overlap = overlap_at_k(reference, ranked, k=2)
    assert abs(overlap - 0.40) < 0.01


def test_find_missing_cards():
    """Test finding reference cards not in top K."""
    reference = {"A", "B", "C", "D"}
    ranked = ["A", "X", "B", "Y", "Z"]

    missing = find_missing_cards(reference, ranked, k=5)

    assert "C" in missing
    assert "D" in missing
    assert "A" not in missing
    assert "B" not in missing


def test_find_missing_cards_with_ranks():
    """Test finding missing cards with their actual ranks."""
    reference = {"A", "B", "C"}
    ranked = ["X", "Y", "A", "Z", "B", "W", "C"]

    missing = find_missing_cards(reference, ranked, k=2, include_ranks=True)

    # A is at rank 3, B at 5, C at 7 - all outside top 2
    assert ("A", 3) in missing
    assert ("B", 5) in missing
    assert ("C", 7) in missing
