"""Integration tests for Cards API endpoints - TDD GREEN phase."""

import pytest


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
        assert "results" in data
        assert isinstance(data["results"], list)
        assert data["page"] == 1
        assert data["limit"] == 20

    def test_search_cards_with_color_filter(self, client, color_identity_blue_black):
        """GET /api/cards with color filter returns filtered results."""
        params = {"colors": ",".join(color_identity_blue_black)}
        response = client.get("/api/cards", params=params)
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)

    def test_search_cards_with_cmc_filter(self, client):
        """GET /api/cards with CMC filter returns cards in range."""
        params = {"cmc_min": 2, "cmc_max": 5}
        response = client.get("/api/cards", params=params)
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)

    def test_search_cards_with_type_filter(self, client):
        """GET /api/cards with type filter returns matching cards."""
        params = {"types": "Creature"}
        response = client.get("/api/cards", params=params)
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)

    def test_search_cards_with_mechanic_filter(self, client):
        """GET /api/cards with mechanic filter returns matching cards."""
        params = {"mechanics": "etb_trigger"}
        response = client.get("/api/cards", params=params)
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)

    def test_search_cards_with_role_filter(self, client):
        """GET /api/cards with role filter returns matching cards."""
        params = {"roles": "ramp"}
        response = client.get("/api/cards", params=params)
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)

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
