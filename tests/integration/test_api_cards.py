"""Integration tests for cards API endpoints."""

from unittest.mock import Mock
from fastapi.testclient import TestClient

from api.main import app
from api.dependencies import get_db
from src.graph.connection import Neo4jConnection


def test_search_cards():
    """Test searching for cards."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = [
        {
            "name": "Eternal Witness",
            "mana_cost": "{1}{G}{G}",
            "cmc": 3,
            "type_line": "Creature — Human Shaman",
            "oracle_text": "When Eternal Witness enters the battlefield...",
            "color_identity": ["G"],
            "mechanics": ["etb_trigger"],
            "functional_categories": ["recursion"],
            "popularity_score": 0.9
        }
    ]

    app.dependency_overrides[get_db] = lambda: mock_conn
    try:
        client = TestClient(app)
        response = client.get("/api/cards/search?q=witness")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Eternal Witness"
    finally:
        app.dependency_overrides.clear()


def test_get_card():
    """Test getting a specific card."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = [
        {
            "name": "Sol Ring",
            "mana_cost": "{1}",
            "cmc": 1,
            "type_line": "Artifact",
            "oracle_text": "{T}: Add {C}{C}.",
            "color_identity": [],
            "mechanics": [],
            "functional_categories": ["ramp"],
            "popularity_score": 0.99
        }
    ]

    app.dependency_overrides[get_db] = lambda: mock_conn
    try:
        client = TestClient(app)
        response = client.get("/api/cards/Sol Ring")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Sol Ring"
        assert data["cmc"] == 1
    finally:
        app.dependency_overrides.clear()


def test_get_card_not_found():
    """Test 404 when card not found."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = []

    app.dependency_overrides[get_db] = lambda: mock_conn
    try:
        client = TestClient(app)
        response = client.get("/api/cards/Nonexistent Card")

        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_get_card_combos():
    """Test getting combos for a card."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = [
        {
            "combo_piece": "Isochron Scepter",
            "text": "Infinite mana with 2+ mana rocks",
            "cost": "{2}",
            "cmc": 2
        }
    ]

    app.dependency_overrides[get_db] = lambda: mock_conn
    try:
        client = TestClient(app)
        response = client.get("/api/cards/Dramatic Reversal/combos")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["piece2"] == "Isochron Scepter"
    finally:
        app.dependency_overrides.clear()
