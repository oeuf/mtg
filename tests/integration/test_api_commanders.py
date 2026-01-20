"""Integration tests for commander API endpoints."""

from unittest.mock import Mock
from fastapi.testclient import TestClient

from api.main import app
from api.dependencies import get_db
from src.graph.connection import Neo4jConnection


def test_health_check():
    """Test health check endpoint."""
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint():
    """Test root endpoint."""
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "MTG Commander" in data["message"]


def test_list_commanders():
    """Test listing commanders."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = [
        {
            "name": "Muldrotha, the Gravetide",
            "mana_cost": "{3}{B}{G}{U}",
            "cmc": 6,
            "type_line": "Legendary Creature — Elemental Avatar",
            "oracle_text": "During each of your turns...",
            "color_identity": ["B", "G", "U"],
            "mechanics": ["graveyard"],
            "functional_categories": [],
            "synergies": ["self_mill", "graveyard"]
        }
    ]

    app.dependency_overrides[get_db] = lambda: mock_conn
    try:
        client = TestClient(app)
        response = client.get("/api/commanders?limit=10")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Muldrotha, the Gravetide"
    finally:
        app.dependency_overrides.clear()


def test_get_commander():
    """Test getting a specific commander."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = [
        {
            "name": "Muldrotha, the Gravetide",
            "mana_cost": "{3}{B}{G}{U}",
            "cmc": 6,
            "type_line": "Legendary Creature — Elemental Avatar",
            "oracle_text": "During each of your turns...",
            "color_identity": ["B", "G", "U"],
            "mechanics": ["graveyard"],
            "functional_categories": [],
            "synergies": ["self_mill", "graveyard"]
        }
    ]

    app.dependency_overrides[get_db] = lambda: mock_conn
    try:
        client = TestClient(app)
        response = client.get("/api/commanders/Muldrotha, the Gravetide")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Muldrotha, the Gravetide"
        assert data["cmc"] == 6
    finally:
        app.dependency_overrides.clear()


def test_get_commander_not_found():
    """Test 404 when commander not found."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = []

    app.dependency_overrides[get_db] = lambda: mock_conn
    try:
        client = TestClient(app)
        response = client.get("/api/commanders/Nonexistent Commander")

        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()
