"""Integration tests for graph API endpoints."""

from unittest.mock import Mock
from fastapi.testclient import TestClient

from api.main import app
from api.dependencies import get_db
from src.graph.connection import Neo4jConnection


def test_get_card_graph():
    """Test getting graph centered on a card."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = [
        {
            "center": {"name": "Sol Ring", "cmc": 1},
            "mechanics": [{"node": {"name": "tap_ability"}, "rel": {}, "type": "HAS_MECHANIC"}],
            "roles": [{"node": {"name": "ramp"}, "rel": {}, "type": "FILLS_ROLE"}],
            "combos": [],
            "similars": []
        }
    ]

    app.dependency_overrides[get_db] = lambda: mock_conn
    try:
        client = TestClient(app)
        response = client.get("/api/graph/card/Sol Ring")

        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) == 3  # Card + mechanic + role
        assert len(data["edges"]) == 2  # HAS_MECHANIC + FILLS_ROLE
    finally:
        app.dependency_overrides.clear()


def test_get_card_graph_not_found():
    """Test graph response when card not found."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = []

    app.dependency_overrides[get_db] = lambda: mock_conn
    try:
        client = TestClient(app)
        response = client.get("/api/graph/card/Nonexistent Card")

        assert response.status_code == 200
        data = response.json()
        assert data["nodes"] == []
        assert data["edges"] == []
    finally:
        app.dependency_overrides.clear()


def test_get_community_graph():
    """Test getting cards in a community."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = [
        {"name": "Sol Ring", "mana_cost": "{1}", "type_line": "Artifact", "pagerank": 0.05},
        {"name": "Arcane Signet", "mana_cost": "{2}", "type_line": "Artifact", "pagerank": 0.04}
    ]

    app.dependency_overrides[get_db] = lambda: mock_conn
    try:
        client = TestClient(app)
        response = client.get("/api/graph/community/1")

        assert response.status_code == 200
        data = response.json()
        assert len(data["nodes"]) == 2
        assert data["nodes"][0]["label"] == "Sol Ring"
    finally:
        app.dependency_overrides.clear()


def test_get_similar_cards():
    """Test getting similar cards."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = [
        {"name": "Mana Crypt", "mana_cost": "{0}", "type_line": "Artifact", "similarity_score": 0.95},
        {"name": "Arcane Signet", "mana_cost": "{2}", "type_line": "Artifact", "similarity_score": 0.85}
    ]

    app.dependency_overrides[get_db] = lambda: mock_conn
    try:
        client = TestClient(app)
        response = client.get("/api/graph/similar/Sol Ring")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Mana Crypt"
        assert data[0]["similarity_score"] == 0.95
    finally:
        app.dependency_overrides.clear()
