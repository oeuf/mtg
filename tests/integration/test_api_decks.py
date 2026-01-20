"""Integration tests for decks API endpoints."""

from unittest.mock import Mock
from fastapi.testclient import TestClient

from api.main import app
from api.dependencies import get_db
from api.routers import decks
from src.graph.connection import Neo4jConnection


def setup_function():
    """Reset deck storage before each test."""
    decks._decks.clear()
    decks._deck_counter = 0


def test_create_deck():
    """Test creating a new deck."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = [{"name": "Muldrotha, the Gravetide"}]

    app.dependency_overrides[get_db] = lambda: mock_conn
    try:
        client = TestClient(app)
        response = client.post("/api/decks", json={
            "commander": "Muldrotha, the Gravetide",
            "name": "My Muldrotha Deck"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["commander"] == "Muldrotha, the Gravetide"
        assert data["name"] == "My Muldrotha Deck"
        assert "id" in data
    finally:
        app.dependency_overrides.clear()


def test_create_deck_commander_not_found():
    """Test 404 when commander doesn't exist."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = []

    app.dependency_overrides[get_db] = lambda: mock_conn
    try:
        client = TestClient(app)
        response = client.post("/api/decks", json={
            "commander": "Nonexistent Commander"
        })

        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_get_deck():
    """Test getting a deck by ID."""
    # First create a deck
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = [{"name": "Muldrotha, the Gravetide"}]

    app.dependency_overrides[get_db] = lambda: mock_conn
    try:
        client = TestClient(app)
        create_response = client.post("/api/decks", json={
            "commander": "Muldrotha, the Gravetide"
        })
        deck_id = create_response.json()["id"]

        # Then get it
        response = client.get(f"/api/decks/{deck_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == deck_id
    finally:
        app.dependency_overrides.clear()


def test_get_deck_not_found():
    """Test 404 when deck doesn't exist."""
    client = TestClient(app)
    response = client.get("/api/decks/nonexistent_deck")

    assert response.status_code == 404


def test_analyze_deck():
    """Test deck analysis."""
    mock_conn = Mock(spec=Neo4jConnection)
    # First call for role coverage
    mock_conn.execute_query.side_effect = [
        [
            {"role": "ramp", "count": 10},
            {"role": "card_draw", "count": 8}
        ],
        # Second call for suggestions
        [
            {
                "name": "Spore Frog",
                "mana_cost": "{G}",
                "type": "Creature",
                "cmc": 1,
                "combined_score": 0.9,
                "shared_mechanics": ["dies_trigger"],
                "roles": ["protection"]
            }
        ]
    ]

    app.dependency_overrides[get_db] = lambda: mock_conn
    try:
        client = TestClient(app)
        response = client.post("/api/decks/analyze", json={
            "commander": "Muldrotha, the Gravetide",
            "cards": ["Sol Ring", "Eternal Witness"]
        })

        assert response.status_code == 200
        data = response.json()
        assert data["commander"] == "Muldrotha, the Gravetide"
        assert data["card_count"] == 2
        assert "role_coverage" in data
        assert "missing_roles" in data
    finally:
        app.dependency_overrides.clear()
