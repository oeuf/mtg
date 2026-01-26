"""Tests for similarity queries."""

import pytest
from unittest.mock import Mock
from src.synergy.queries import DeckbuildingQueries


def test_find_similar_cards():
    """Test finding similar cards query."""
    mock_conn = Mock()
    mock_conn.execute_query.return_value = [{
        "name": "Eternal Witness",
        "similarity_score": 0.85,
        "cmc": 3,
        "shared_mechanics": ["etb_trigger", "recursion"]
    }]

    result = DeckbuildingQueries.find_similar_cards(
        mock_conn, card_name="Regrowth", min_similarity=0.7, limit=10
    )

    assert len(result) == 1
    assert result[0]["similarity_score"] > 0.7
