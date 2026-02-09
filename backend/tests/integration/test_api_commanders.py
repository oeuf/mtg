"""Integration tests for Commander API endpoints - GREEN phase."""

import pytest


class TestCommandersEndpoints:
    """Commander API endpoint tests."""

    def test_get_commanders_returns_list(self, client):
        """GET /api/commanders returns list of commanders."""
        response = client.get("/api/commanders")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "commanders" in data
        assert isinstance(data["commanders"], list)

    def test_get_commander_by_name(self, client, muldrotha_commander_name):
        """GET /api/commanders/{name} returns 404 when commander not found."""
        response = client.get(f"/api/commanders/{muldrotha_commander_name}")
        assert response.status_code == 404

    def test_get_commander_synergies(self, client, muldrotha_commander_name):
        """GET /api/commanders/{name}/synergies returns synergy list."""
        response = client.get(
            f"/api/commanders/{muldrotha_commander_name}/synergies"
        )
        assert response.status_code == 200
        data = response.json()
        assert "commander" in data
        assert "synergies" in data
        assert isinstance(data["synergies"], list)
        assert data["commander"] == muldrotha_commander_name

    def test_get_commander_recommendations(
        self, client, muldrotha_commander_name
    ):
        """GET /api/commanders/{name}/recommendations returns recommendations."""
        response = client.get(
            f"/api/commanders/{muldrotha_commander_name}/recommendations"
        )
        assert response.status_code == 200
        data = response.json()
        assert "commander" in data
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)
        assert data["commander"] == muldrotha_commander_name
