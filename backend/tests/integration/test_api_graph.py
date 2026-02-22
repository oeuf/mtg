"""Integration tests for Graph API endpoints - TDD GREEN phase."""

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.dependencies import get_neo4j_session


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

    def test_get_graph_health_returns_503_when_db_fails(self):
        """GET /api/graph/health returns 503 unhealthy when Neo4j query raises."""
        failing_session = MagicMock()
        failing_session.run.side_effect = Exception("Connection refused")

        def override_get_session():
            yield failing_session

        app.dependency_overrides[get_neo4j_session] = override_get_session
        try:
            test_client = TestClient(app)
            response = test_client.get("/api/graph/health")
            assert response.status_code == 503
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["message"] == "Unable to connect to database"
        finally:
            app.dependency_overrides.clear()
