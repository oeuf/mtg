"""Integration tests for search, autocomplete, and response format fixes."""

from unittest.mock import MagicMock, call

import pytest


class TestCommandersResponseFormat:
    """Commander API returns correct response format."""

    def test_commanders_returns_items_key(self, client, mock_neo4j_session):
        """GET /api/commanders returns {"items": [...], "total": N}."""
        count_result = MagicMock()
        count_result.single.return_value = {"total": 2}

        items_result = MagicMock()
        items_result.data.return_value = [
            {"name": "Commander A", "color_identity": ["W"]},
            {"name": "Commander B", "color_identity": ["U"]},
        ]

        mock_neo4j_session.run.side_effect = [count_result, items_result]

        response = client.get("/api/commanders")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "commanders" not in data
        assert isinstance(data["items"], list)
        assert data["total"] == 2

    def test_commanders_search_by_name(self, client, mock_neo4j_session):
        """GET /api/commanders?search=TestCommander returns matching items."""
        count_result = MagicMock()
        count_result.single.return_value = {"total": 1}

        items_result = MagicMock()
        items_result.data.return_value = [
            {"name": "TestCommander", "color_identity": ["B", "G", "U"]},
        ]

        mock_neo4j_session.run.side_effect = [count_result, items_result]

        response = client.get("/api/commanders?search=TestCommander")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "TestCommander"

        # Verify the search param was passed in the Cypher query
        count_call_args = mock_neo4j_session.run.call_args_list[0]
        query = count_call_args[0][0]
        assert "toLower" in query
        assert "CONTAINS" in query

    def test_commanders_returns_full_properties(self, client, mock_neo4j_session):
        """Commander items have full properties, not just name/color/rank."""
        count_result = MagicMock()
        count_result.single.return_value = {"total": 1}

        items_result = MagicMock()
        items_result.data.return_value = [
            {
                "name": "Muldrotha, the Gravetide",
                "mana_cost": "{2}{B}{G}{U}",
                "cmc": 5,
                "type_line": "Legendary Creature — Elemental",
                "oracle_text": "During each of your turns...",
                "color_identity": ["B", "G", "U"],
                "colors": ["B", "G", "U"],
                "power": "6",
                "toughness": "6",
                "edhrec_rank": 100,
                "keywords": [],
                "is_legendary": True,
                "functional_categories": ["recursion"],
                "mechanics": ["recursion"],
                "themes": ["graveyard_value"],
                "archetype": None,
                "popularity_score": None,
            },
        ]

        mock_neo4j_session.run.side_effect = [count_result, items_result]

        response = client.get("/api/commanders")
        data = response.json()
        item = data["items"][0]
        assert item["name"] == "Muldrotha, the Gravetide"
        assert item["mana_cost"] == "{2}{B}{G}{U}"
        assert item["type_line"] == "Legendary Creature — Elemental"
        assert item["color_identity"] == ["B", "G", "U"]
        assert item["oracle_text"] == "During each of your turns..."

    def test_commanders_pagination(self, client, mock_neo4j_session):
        """GET /api/commanders?page=2&limit=5 uses correct offset."""
        count_result = MagicMock()
        count_result.single.return_value = {"total": 10}

        items_result = MagicMock()
        items_result.data.return_value = []

        mock_neo4j_session.run.side_effect = [count_result, items_result]

        response = client.get("/api/commanders?page=2&limit=5")
        assert response.status_code == 200

        # Verify SKIP $offset with offset = (2-1)*5 = 5
        data_call_args = mock_neo4j_session.run.call_args_list[1]
        params = data_call_args[0][1]
        assert params["offset"] == 5
        assert params["limit"] == 5


class TestCardsResponseFormat:
    """Card API returns correct response format."""

    def test_cards_returns_items_key(self, client, mock_neo4j_session):
        """GET /api/cards returns {"items": [...], "total": N}."""
        count_result = MagicMock()
        count_result.single.return_value = {"total": 1}

        items_result = MagicMock()
        items_result.data.return_value = [
            {"name": "Lightning Bolt", "cmc": 1},
        ]

        mock_neo4j_session.run.side_effect = [count_result, items_result]

        response = client.get("/api/cards")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "results" not in data

    def test_cards_text_search(self, client, mock_neo4j_session):
        """GET /api/cards?text_search=TestCard returns matches."""
        count_result = MagicMock()
        count_result.single.return_value = {"total": 1}

        items_result = MagicMock()
        items_result.data.return_value = [
            {"name": "TestCard", "oracle_text": "Draw a card"},
        ]

        mock_neo4j_session.run.side_effect = [count_result, items_result]

        response = client.get("/api/cards?text_search=TestCard")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "TestCard"

        # Verify text_search was used in the query
        count_call_args = mock_neo4j_session.run.call_args_list[0]
        query = count_call_args[0][0]
        assert "text_search" in query or "toLower" in query

    def test_cards_items_not_nested(self, client, mock_neo4j_session):
        """Items are flat objects with 'name' key, not {"c": {...}}."""
        count_result = MagicMock()
        count_result.single.return_value = {"total": 1}

        items_result = MagicMock()
        items_result.data.return_value = [
            {"name": "Sol Ring", "cmc": 1, "type_line": "Artifact"},
        ]

        mock_neo4j_session.run.side_effect = [count_result, items_result]

        response = client.get("/api/cards")
        data = response.json()
        item = data["items"][0]
        # Should be flat: {"name": "Sol Ring", ...} not {"c": {"name": ...}}
        assert "name" in item
        assert "c" not in item


class TestAutocomplete:
    """Autocomplete endpoint tests."""

    def test_autocomplete_returns_results(self, client, mock_neo4j_session):
        """GET /api/cards/autocomplete?q=Test returns matches."""
        result = MagicMock()
        result.data.return_value = [
            {"name": "Test Card", "type_line": "Creature", "mana_cost": "{1}"},
            {"name": "Testing Grounds", "type_line": "Enchantment", "mana_cost": "{2}"},
        ]
        mock_neo4j_session.run.return_value = result

        response = client.get("/api/cards/autocomplete?q=Test")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["name"] == "Test Card"

    def test_autocomplete_commander_only(self, client, mock_neo4j_session):
        """GET /api/cards/autocomplete?q=Test&commander_only=true uses Commander label."""
        result = MagicMock()
        result.data.return_value = [
            {"name": "Test Commander", "type_line": "Legendary Creature", "mana_cost": "{3}"},
        ]
        mock_neo4j_session.run.return_value = result

        response = client.get("/api/cards/autocomplete?q=Test&commander_only=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        # Verify the query used Commander label
        call_args = mock_neo4j_session.run.call_args
        query = call_args[0][0]
        assert "Commander" in query
