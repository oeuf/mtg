"""Integration tests for Cards API endpoints - TDD GREEN phase."""

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_neo4j_session
from app.main import app


class TestCardsSearchEndpoints:
    """Card search API endpoint tests."""

    def test_search_cards_returns_results(self, client):
        """GET /api/cards returns search results."""
        response = client.get("/api/cards")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert "items" in data
        assert isinstance(data["items"], list)
        assert data["page"] == 1
        assert data["limit"] == 20

    def test_search_cards_with_color_filter(self, client, color_identity_blue_black):
        """GET /api/cards with color filter returns filtered results."""
        params = {"colors": ",".join(color_identity_blue_black)}
        response = client.get("/api/cards", params=params)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_search_cards_with_cmc_filter(self, client):
        """GET /api/cards with CMC filter returns cards in range."""
        params = {"cmc_min": 2, "cmc_max": 5}
        response = client.get("/api/cards", params=params)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_search_cards_with_type_filter(self, client):
        """GET /api/cards with type filter returns matching cards."""
        params = {"types": "Creature"}
        response = client.get("/api/cards", params=params)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_search_cards_with_mechanic_filter(self, client):
        """GET /api/cards with mechanic filter returns matching cards."""
        params = {"mechanics": "etb_trigger"}
        response = client.get("/api/cards", params=params)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_search_cards_with_role_filter(self, client):
        """GET /api/cards with role filter returns matching cards."""
        params = {"roles": "ramp"}
        response = client.get("/api/cards", params=params)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_get_card_by_name(self, client, sample_card):
        """GET /api/cards/{name} returns 404 when card not found."""
        response = client.get(f"/api/cards/{sample_card.name}")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_get_similar_cards_not_found(self, client, sample_card):
        """GET /api/cards/{name}/similar returns 404 when card not found."""
        response = client.get(f"/api/cards/{sample_card.name}/similar")
        assert response.status_code == 404

    def test_get_card_synergies_not_found(self, client, sample_card):
        """GET /api/cards/{name}/synergies returns 404 when card not found."""
        response = client.get(f"/api/cards/{sample_card.name}/synergies")
        assert response.status_code == 404

    def test_get_card_combos_not_found(self, client, sample_card):
        """GET /api/cards/{name}/combos returns 404 when card not found."""
        response = client.get(f"/api/cards/{sample_card.name}/combos")
        assert response.status_code == 404

    def test_similar_route_not_swallowed_by_generic(self, client_with_card):
        """GET /cards/{name}/similar must resolve to the sub-resource route, not generic."""
        response = client_with_card.get("/api/cards/Test Card/similar")
        assert response.status_code == 200
        data = response.json()
        assert "similar_cards" in data
        assert data["card"] == "Test Card"


@pytest.fixture
def client_with_card():
    """Test client where 'Test Card' exists but has no relationships."""
    from app.dependencies import get_neo4j_session

    mock_session = MagicMock()
    exists_result = MagicMock()
    exists_result.single.return_value = MagicMock()  # card exists
    empty_result = MagicMock()
    empty_result.data.return_value = []

    def run_side_effect(query, params=None, **kwargs):
        name = (params or {}).get("name", "")
        if name == "Test Card" and "RETURN c" in query and "EMBEDDING_SIMILAR" not in query and "SYNERGIZES_WITH" not in query:
            return exists_result
        return empty_result

    mock_session.run.side_effect = run_side_effect

    def override():
        yield mock_session

    app.dependency_overrides[get_neo4j_session] = override
    yield TestClient(app)
    app.dependency_overrides.clear()


def _make_autocomplete_client(mock_records):
    """Create a test client with mock Neo4j returning given autocomplete records."""
    mock_session = MagicMock()
    result = MagicMock()
    result.data.return_value = mock_records
    result.single.return_value = None
    mock_session.run.return_value = result

    def override():
        yield mock_session

    app.dependency_overrides[get_neo4j_session] = override
    client = TestClient(app)
    return client, mock_session


CARD_CANDIDATES = [
    {"name": "Sol Ring", "type_line": "Artifact", "mana_cost": "{1}"},
    {"name": "Sol Talisman", "type_line": "Artifact", "mana_cost": "{0}"},
    {"name": "Solar Blaze", "type_line": "Sorcery", "mana_cost": "{2}{R}{W}"},
    {"name": "Soldevi Adnate", "type_line": "Creature", "mana_cost": "{1}{B}"},
    {"name": "Lightning Bolt", "type_line": "Instant", "mana_cost": "{R}"},
    {"name": "Lightning Greaves", "type_line": "Artifact — Equipment", "mana_cost": "{2}"},
    {"name": "Lightsaber", "type_line": "Artifact — Equipment", "mana_cost": "{1}"},
]


class TestAutocompleteEndpoint:
    """Autocomplete endpoint tests including fuzzy search."""

    def test_route_not_404(self):
        """GET /api/cards/autocomplete must not 404 (route isolation)."""
        client, _ = _make_autocomplete_client([])
        try:
            response = client.get("/api/cards/autocomplete", params={"q": "test"})
            assert response.status_code != 404, "autocomplete route matched as /cards/{name}"
            assert response.status_code == 200
        finally:
            app.dependency_overrides.clear()

    def test_exact_match(self):
        """Exact query 'Sol Ring' returns Sol Ring as first result."""
        client, _ = _make_autocomplete_client(CARD_CANDIDATES)
        try:
            response = client.get("/api/cards/autocomplete", params={"q": "Sol Ring"})
            assert response.status_code == 200
            data = response.json()
            assert len(data) > 0
            assert data[0]["name"] == "Sol Ring"
        finally:
            app.dependency_overrides.clear()

    def test_single_typo(self):
        """Query 'Sol Rng' still returns Sol Ring via fuzzy matching."""
        client, _ = _make_autocomplete_client(CARD_CANDIDATES)
        try:
            response = client.get("/api/cards/autocomplete", params={"q": "Sol Rng"})
            assert response.status_code == 200
            data = response.json()
            names = [r["name"] for r in data]
            assert "Sol Ring" in names
        finally:
            app.dependency_overrides.clear()

    def test_transposition(self):
        """Query 'Lcihtnig Bolt' returns Lightning Bolt via fuzzy matching."""
        client, _ = _make_autocomplete_client(CARD_CANDIDATES)
        try:
            response = client.get("/api/cards/autocomplete", params={"q": "Lcihtnig Bolt"})
            assert response.status_code == 200
            data = response.json()
            names = [r["name"] for r in data]
            assert "Lightning Bolt" in names
        finally:
            app.dependency_overrides.clear()

    def test_case_insensitive(self):
        """Query 'SOL RING' returns Sol Ring."""
        client, _ = _make_autocomplete_client(CARD_CANDIDATES)
        try:
            response = client.get("/api/cards/autocomplete", params={"q": "SOL RING"})
            assert response.status_code == 200
            data = response.json()
            assert len(data) > 0
            assert data[0]["name"] == "Sol Ring"
        finally:
            app.dependency_overrides.clear()

    def test_commander_only_filter(self):
        """Query with commander_only=true uses Commander label."""
        commander_records = [
            {"name": "Atraxa, Praetors' Voice", "type_line": "Legendary Creature", "mana_cost": "{G}{W}{U}{B}"},
        ]
        client, mock_session = _make_autocomplete_client(commander_records)
        try:
            response = client.get(
                "/api/cards/autocomplete",
                params={"q": "atraxa", "commander_only": "true"},
            )
            assert response.status_code == 200
            # Verify the Cypher query filters by Commander label
            call_args = mock_session.run.call_args
            cypher_query = call_args[0][0]
            assert "Commander" in cypher_query
            # When commander_only=true, query must include AND c:Commander filter
            assert "AND c:Commander" in cypher_query
        finally:
            app.dependency_overrides.clear()

    def test_min_length_guard(self):
        """Single character query returns 422 validation error."""
        client, _ = _make_autocomplete_client([])
        try:
            response = client.get("/api/cards/autocomplete", params={"q": "s"})
            assert response.status_code == 422
        finally:
            app.dependency_overrides.clear()

    def test_empty_results(self):
        """Empty Neo4j results return empty list."""
        client, _ = _make_autocomplete_client([])
        try:
            response = client.get("/api/cards/autocomplete", params={"q": "xyznonexistent"})
            assert response.status_code == 200
            assert response.json() == []
        finally:
            app.dependency_overrides.clear()
