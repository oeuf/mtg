"""Tests for QueryService - TDD GREEN phase.

Tests wrap DeckbuildingQueries methods. These tests use a mocked
Neo4j connection to verify QueryService behavior.
"""

import pytest
from unittest.mock import MagicMock
from app.models.card import Card


@pytest.fixture
def mock_connection():
    """Mock Neo4j connection that returns predefined query results."""
    conn = MagicMock()
    return conn


class TestQueryService:
    """QueryService method tests."""

    def test_find_synergistic_cards_returns_list(self, mock_connection):
        """QueryService.find_synergistic_cards returns synergistic cards."""
        mock_connection.execute_query.return_value = [
            {"name": "Sakura-Tribe Elder", "synergy_strength": 0.85, "cmc": 2},
            {"name": "Eternal Witness", "synergy_strength": 0.78, "cmc": 3},
        ]
        from app.services.query_service import QueryService
        service = QueryService(mock_connection)
        result = service.find_synergistic_cards(
            commander_name="Muldrotha, the Gravetide",
            max_cmc=4,
            min_strength=0.7,
            limit=50
        )
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(c, dict) for c in result)
        assert all("name" in c and "synergy_strength" in c for c in result)

    def test_find_known_combos_returns_combos(self, mock_connection):
        """QueryService.find_known_combos returns documented combos."""
        mock_connection.execute_query.return_value = [
            {"combo_piece": "Deadeye Navigator", "text": "...", "cost": "{4}{U}{U}", "cmc": 6},
        ]
        from app.services.query_service import QueryService
        service = QueryService(mock_connection)
        result = service.find_known_combos(card_name="Eternal Witness")
        assert isinstance(result, list)
        # May be empty for cards without documented combos
        if result:
            assert all("combo_piece" in c for c in result)

    def test_find_token_generators_returns_cards(self, mock_connection):
        """QueryService.find_token_generators returns token-generating cards."""
        mock_connection.execute_query.return_value = [
            {"name": "Krenko, Mob Boss", "cmc": 4, "cost": "{2}{R}{R}"},
        ]
        from app.services.query_service import QueryService
        service = QueryService(mock_connection)
        result = service.find_token_generators(
            token_type="Goblin",
            color_identity=["R"],
            max_cmc=5
        )
        assert isinstance(result, list)
        if result:
            assert all("name" in c and "cmc" in c for c in result)

    def test_find_cards_by_role_returns_efficient_cards(self, mock_connection):
        """QueryService.find_cards_by_role returns role-filtered cards."""
        mock_connection.execute_query.return_value = [
            {"name": "Llanowar Elves", "efficiency": 0.9, "cmc": 1},
            {"name": "Sol Ring", "efficiency": 0.95, "cmc": 1},
        ]
        from app.services.query_service import QueryService
        service = QueryService(mock_connection)
        result = service.find_cards_by_role(
            role="ramp",
            color_identity=["G"],
            max_cmc=3,
            min_efficiency=0.6
        )
        assert isinstance(result, list)
        assert all("name" in c and "efficiency" in c for c in result)
        assert len(result) <= 20  # Hard limit

    def test_build_deck_shell_returns_37_cards(self, mock_connection):
        """QueryService.build_deck_shell returns initial shell with 37 cards."""
        # First call returns commander colors, subsequent calls return cards per role
        def mock_execute(query, params):
            if "cmd.color_identity AS colors" in query:
                return [{"colors": ["B", "G", "U"]}]
            count = params.get("count", 5)
            return [{"name": f"Card_{i}", "cost": "{2}", "cmc": 2, "synergy": 0.5} for i in range(count)]

        mock_connection.execute_query.side_effect = mock_execute
        from app.services.query_service import QueryService
        service = QueryService(mock_connection)
        result = service.build_deck_shell(
            commander_name="Muldrotha, the Gravetide"
        )
        assert isinstance(result, dict)
        assert "commander" in result
        assert "cards_by_role" in result
        # Verify 8x8 distribution
        assert len(result["cards_by_role"]["ramp"]) == 9
        assert len(result["cards_by_role"]["card_draw"]) == 9
        assert len(result["cards_by_role"]["removal"]) == 9
        total_cards = sum(len(cards) for cards in result["cards_by_role"].values())
        assert total_cards == 37

    def test_find_combo_packages_returns_combos(self, mock_connection):
        """QueryService.find_combo_packages returns combo packages."""
        mock_connection.execute_query.return_value = [
            {"piece1": "Eternal Witness", "piece2": "Deadeye Navigator", "cmc1": 3, "cmc2": 6, "shared_mechanic": "etb_trigger"},
        ]
        from app.services.query_service import QueryService
        service = QueryService(mock_connection)
        result = service.find_combo_packages(
            commander_name="Muldrotha, the Gravetide"
        )
        assert isinstance(result, list)
        if result:
            assert all("piece1" in c and "piece2" in c for c in result)

    def test_find_similar_cards_returns_embeddings(self, mock_connection):
        """QueryService.find_similar_cards returns similar cards."""
        mock_connection.execute_query.return_value = [
            {"name": "Regrowth", "similarity_score": 0.82, "mana_cost": "{1}{G}", "cmc": 2},
            {"name": "Noxious Revival", "similarity_score": 0.75, "mana_cost": "{G/P}", "cmc": 1},
        ]
        from app.services.query_service import QueryService
        service = QueryService(mock_connection)
        result = service.find_similar_cards(
            card_name="Eternal Witness",
            min_similarity=0.5,
            limit=20
        )
        assert isinstance(result, list)
        assert all("name" in c and "similarity_score" in c for c in result)
        assert all(0 <= c["similarity_score"] <= 1 for c in result)
        assert len(result) <= 20
