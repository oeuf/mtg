"""Unit tests for popularity score calculation."""

from src.data.popularity import PopularityCalculator


def test_calculate_popularity_high_rank_high_precon():
    """Test card with good EDHREC rank and high precon count."""
    calc = PopularityCalculator(total_precons=100)

    # Rank 100 out of 20000, appears in 50 precons
    score = calc.calculate(edhrec_rank=100, precon_count=50)

    # Should be high (close to 1.0)
    assert score > 0.8


def test_calculate_popularity_no_rank():
    """Test card with no EDHREC rank."""
    calc = PopularityCalculator(total_precons=100)

    # No rank (None), appears in 10 precons
    score = calc.calculate(edhrec_rank=None, precon_count=10)

    # Should use default 0.5 for EDHREC component
    assert 0.3 < score < 0.6


def test_calculate_popularity_low_rank():
    """Test card with bad EDHREC rank."""
    calc = PopularityCalculator(total_precons=100)

    # Very bad rank, no precon appearances
    score = calc.calculate(edhrec_rank=20000, precon_count=0)

    # Should be very low
    assert score < 0.1


def test_calculate_popularity_weights():
    """Test that EDHREC is weighted higher than precon."""
    calc = PopularityCalculator(total_precons=100)

    # Good rank, no precons vs bad rank, many precons
    score_good_rank = calc.calculate(edhrec_rank=100, precon_count=0)
    score_many_precons = calc.calculate(edhrec_rank=15000, precon_count=100)

    # Good EDHREC rank should win (0.7 weight)
    assert score_good_rank > score_many_precons
