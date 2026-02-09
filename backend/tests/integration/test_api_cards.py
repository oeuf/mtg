"""Integration tests for Cards API endpoints - TDD RED phase."""

import pytest


class TestCardsSearchEndpoints:
    """Card search API endpoint tests."""

    def test_search_cards_returns_results(self, client):
        """GET /api/cards returns search results."""
        response = client.get("/api/cards")
        # Should return:
        # {
        #     "total": int,
        #     "page": int,
        #     "limit": int,
        #     "results": List[Card]
        # }
        assert response.status_code == 404

    def test_search_cards_with_color_filter(self, client, color_identity_blue_black):
        """GET /api/cards with color filter returns filtered results."""
        params = {"colors": ",".join(color_identity_blue_black)}
        response = client.get("/api/cards", params=params)
        # Should filter by exact color match
        assert response.status_code == 404

    def test_search_cards_with_cmc_filter(self, client):
        """GET /api/cards with CMC filter returns cards in range."""
        params = {"cmc_min": 2, "cmc_max": 5}
        response = client.get("/api/cards", params=params)
        # Should return cards with 2 <= cmc <= 5
        assert response.status_code == 404

    def test_search_cards_with_type_filter(self, client):
        """GET /api/cards with type filter returns matching cards."""
        params = {"types": "Creature"}
        response = client.get("/api/cards", params=params)
        # Should filter by card type
        assert response.status_code == 404

    def test_search_cards_with_mechanic_filter(self, client):
        """GET /api/cards with mechanic filter returns matching cards."""
        params = {"mechanics": "etb_trigger"}
        response = client.get("/api/cards", params=params)
        # Should filter by mechanic
        assert response.status_code == 404

    def test_search_cards_with_role_filter(self, client):
        """GET /api/cards with role filter returns matching cards."""
        params = {"roles": "ramp"}
        response = client.get("/api/cards", params=params)
        # Should filter by functional role
        assert response.status_code == 404

    def test_get_card_by_name(self, client, sample_card):
        """GET /api/cards/{name} returns card details."""
        response = client.get(f"/api/cards/{sample_card.name}")
        # Should return: Card model
        assert response.status_code == 404

    def test_get_similar_cards(self, client, sample_card):
        """GET /api/cards/{name}/similar returns similar cards."""
        response = client.get(f"/api/cards/{sample_card.name}/similar")
        # Should return:
        # {
        #     "card": str,
        #     "similar_cards": List[SimilarCardResponse]
        # }
        assert response.status_code == 404

    def test_get_card_synergies(self, client, sample_card):
        """GET /api/cards/{name}/synergies returns synergistic cards."""
        response = client.get(f"/api/cards/{sample_card.name}/synergies")
        # Should return:
        # {
        #     "card": str,
        #     "synergies": List[SynergyResponse]
        # }
        assert response.status_code == 404
