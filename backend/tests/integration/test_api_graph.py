"""Integration tests for Graph API endpoints - TDD GREEN phase."""

import pytest


class TestGraphEndpoints:
    """Graph metadata API endpoint tests."""

    def test_get_graph_stats(self, client):
        """GET /api/graph/stats returns graph statistics."""
        response = client.get("/api/graph/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_cards" in data
        assert "total_commanders" in data
        assert "total_mechanics" in data
        assert "total_relationships" in data
        assert "last_updated" in data

    def test_get_all_mechanics(self, client):
        """GET /api/mechanics returns all mechanics."""
        response = client.get("/api/mechanics")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "mechanics" in data

    def test_get_all_themes(self, client):
        """GET /api/themes returns all themes."""
        response = client.get("/api/themes")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "themes" in data

    def test_get_all_functional_roles(self, client):
        """GET /api/roles returns all functional roles."""
        response = client.get("/api/roles")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "roles" in data

    def test_get_graph_health(self, client):
        """GET /api/graph/health returns Neo4j connection status."""
        response = client.get("/api/graph/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "message" in data
