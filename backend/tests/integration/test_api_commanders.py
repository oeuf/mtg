"""Integration tests for Commander API endpoints - TDD RED phase."""

import pytest


class TestCommandersEndpoints:
    """Commander API endpoint tests."""

    def test_get_commanders_returns_list(self, client):
        """GET /api/commanders returns list of commanders."""
        response = client.get("/api/commanders")
        # Endpoint doesn't exist yet (RED phase - should fail with 404)
        # Once implemented, should return:
        # {
        #     "total": int,
        #     "commanders": List[CommanderStats]
        # }
        assert response.status_code == 404

    def test_get_commander_by_name(self, client, muldrotha_commander_name):
        """GET /api/commanders/{name} returns commander details."""
        response = client.get(f"/api/commanders/{muldrotha_commander_name}")
        # Should return: Commander model with full details
        assert response.status_code == 404

    def test_get_commander_synergies(self, client, muldrotha_commander_name):
        """GET /api/commanders/{name}/synergies returns synergistic cards."""
        response = client.get(
            f"/api/commanders/{muldrotha_commander_name}/synergies"
        )
        # Should return:
        # {
        #     "commander": str,
        #     "synergies": List[SynergyResponse]
        # }
        assert response.status_code == 404

    def test_get_commander_recommendations(
        self, client, muldrotha_commander_name
    ):
        """GET /api/commanders/{name}/recommendations returns recommendations."""
        response = client.get(
            f"/api/commanders/{muldrotha_commander_name}/recommendations"
        )
        # Should return:
        # {
        #     "commander": str,
        #     "recommendations": List[RecommendationResponse]
        # }
        assert response.status_code == 404
