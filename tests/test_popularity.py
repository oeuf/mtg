"""Unit tests for popularity scoring."""

import pytest
from unittest.mock import Mock
from src.graph.popularity import PopularityScorer
from src.graph.connection import Neo4jConnection


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


def test_update_card_popularity_scores():
    """Test batch update of card popularity scores."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = [{"updated": 100}]

    scorer = PopularityScorer()
    scorer.update_all_cards(mock_conn)

    assert mock_conn.execute_query.called
    # Check first call (cards with EDHREC rank)
    call_args = mock_conn.execute_query.call_args_list[0][0][0]
    assert "SET c.popularity_score" in call_args
