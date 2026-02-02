"""Unit tests for validation metrics."""

from src.validation.metrics import precision_at_k, recall_at_k, mean_reciprocal_rank


def test_precision_at_k_perfect():
    """Test precision when all recommendations are in reference."""
    recommendations = ["Sol Ring", "Sakura-Tribe Elder", "Eternal Witness"]
    reference = ["Sol Ring", "Sakura-Tribe Elder", "Eternal Witness", "Forest"]

    p = precision_at_k(recommendations, reference, k=3)
    assert p == 1.0


def test_precision_at_k_partial():
    """Test precision with partial overlap."""
    recommendations = ["Sol Ring", "Mana Crypt", "Eternal Witness"]
    reference = ["Sol Ring", "Eternal Witness"]

    p = precision_at_k(recommendations, reference, k=3)
    assert p == 2/3


def test_precision_at_k_none():
    """Test precision with no overlap."""
    recommendations = ["Sol Ring", "Mana Crypt"]
    reference = ["Forest", "Island"]

    p = precision_at_k(recommendations, reference, k=2)
    assert p == 0.0


def test_recall_at_k_perfect():
    """Test recall when all reference cards found."""
    recommendations = ["Sol Ring", "Eternal Witness", "Sakura-Tribe Elder"]
    reference = ["Sol Ring", "Eternal Witness"]

    r = recall_at_k(recommendations, reference, k=3)
    assert r == 1.0


def test_recall_at_k_partial():
    """Test recall with partial coverage."""
    recommendations = ["Sol Ring", "Mana Crypt", "Eternal Witness"]
    reference = ["Sol Ring", "Eternal Witness", "Sakura-Tribe Elder", "Forest"]

    r = recall_at_k(recommendations, reference, k=3)
    assert r == 2/4


def test_mean_reciprocal_rank_first():
    """Test MRR when first recommendation matches."""
    recommendations = ["Sol Ring", "Mana Crypt", "Eternal Witness"]
    reference = ["Sol Ring"]

    mrr = mean_reciprocal_rank(recommendations, reference)
    assert mrr == 1.0


def test_mean_reciprocal_rank_third():
    """Test MRR when third recommendation matches."""
    recommendations = ["Mana Crypt", "Mana Vault", "Sol Ring"]
    reference = ["Sol Ring"]

    mrr = mean_reciprocal_rank(recommendations, reference)
    assert abs(mrr - 1/3) < 0.001


def test_mean_reciprocal_rank_multiple():
    """Test MRR with multiple reference cards."""
    recommendations = ["A", "B", "C", "D", "E"]
    reference = ["C", "D"]  # First match at position 3

    mrr = mean_reciprocal_rank(recommendations, reference)
    assert abs(mrr - 1/3) < 0.001  # 1/3 for first match at position 3
