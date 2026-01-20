"""Integration tests for GDS-enhanced queries."""

from unittest.mock import Mock
from src.synergy.queries import DeckbuildingQueries
from src.graph.connection import Neo4jConnection


def test_find_synergistic_cards_uses_gds_scores():
    """Test that synergistic cards query uses GDS scores."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = [
        {
            "name": "Eternal Witness",
            "mana_cost": "{1}{G}{G}",
            "type": "Creature",
            "cmc": 3,
            "text": "When...",
            "shared_mechanics": ["etb_trigger"],
            "synergy_strength": 0.9,
            "roles": ["recursion"],
            "combined_score": 0.85,
            "pagerank_score": 0.02,
            "community_match": True
        }
    ]

    results = DeckbuildingQueries.find_synergistic_cards_v2(
        mock_conn,
        commander_name="Muldrotha, the Gravetide",
        max_cmc=4,
        limit=10
    )

    # Verify the query includes GDS fields
    call_args = mock_conn.execute_query.call_args[0][0]

    assert "pagerank_score" in call_args
    assert "community_id" in call_args
    assert "popularity_score" in call_args

    assert len(results) == 1
    assert results[0]["name"] == "Eternal Witness"
