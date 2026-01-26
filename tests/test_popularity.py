"""Unit tests for popularity scoring."""

import pytest
from src.graph.popularity import PopularityScorer


def test_calculate_popularity_score_high_rank():
    """Cards with low edhrec_rank (high popularity) get high scores."""
    scorer = PopularityScorer()
    score = scorer.calculate_edhrec_score(edhrec_rank=1)
    assert score > 0.95


def test_calculate_popularity_score_medium_rank():
    """Cards with medium edhrec_rank get medium scores."""
    scorer = PopularityScorer()
    score = scorer.calculate_edhrec_score(edhrec_rank=1000)
    assert 0.3 < score < 0.6


def test_calculate_popularity_score_low_rank():
    """Cards with high edhrec_rank (low popularity) get low scores."""
    scorer = PopularityScorer()
    score = scorer.calculate_edhrec_score(edhrec_rank=20000)
    assert score < 0.3


def test_calculate_popularity_score_no_rank():
    """Cards without edhrec_rank get baseline score."""
    scorer = PopularityScorer()
    score = scorer.calculate_edhrec_score(edhrec_rank=None)
    assert score == 0.0
