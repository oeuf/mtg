"""Test theme node and relationship loading."""

import pytest
from src.graph.connection import Neo4jConnection
from src.graph.loaders import create_theme_nodes, create_theme_relationships


@pytest.fixture
def test_connection():
    """Create test Neo4j connection."""
    conn = Neo4jConnection(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="mtg-commander"
    )

    # Clean up test data
    conn.execute_query("MATCH (t:Theme) DETACH DELETE t")
    conn.execute_query("MATCH (c:Card {name: 'Test Card'}) DETACH DELETE c")

    yield conn

    # Cleanup after test
    conn.execute_query("MATCH (t:Theme) DETACH DELETE t")
    conn.execute_query("MATCH (c:Card {name: 'Test Card'}) DETACH DELETE c")
    conn.close()


def test_create_theme_nodes(test_connection):
    """Should create Theme nodes with metadata."""
    themes = {
        "reanimation": {"description": "Return creatures from graveyard to battlefield"},
        "tokens": {"description": "Create and benefit from tokens"}
    }

    create_theme_nodes(test_connection, themes)

    # Verify themes created
    result = test_connection.execute_query("""
        MATCH (t:Theme)
        WHERE t.name IN ['reanimation', 'tokens']
        RETURN t.name as name, t.description as description
        ORDER BY t.name
    """)

    assert len(result) == 2
    assert result[0]["name"] == "reanimation"
    assert "graveyard" in result[0]["description"]


def test_create_theme_relationships(test_connection):
    """Should create SUPPORTS_THEME relationships."""
    # Create test card
    test_connection.execute_query("""
        CREATE (c:Card {
            name: 'Test Card',
            themes: ['reanimation', 'graveyard_value']
        })
    """)

    # Create themes
    themes = {
        "reanimation": {"description": "Reanimate creatures"},
        "graveyard_value": {"description": "Graveyard synergies"}
    }
    create_theme_nodes(test_connection, themes)

    # Create card data
    card_data = {
        "name": "Test Card",
        "themes": ["reanimation", "graveyard_value"]
    }

    create_theme_relationships(test_connection, card_data)

    # Verify relationships
    result = test_connection.execute_query("""
        MATCH (c:Card {name: 'Test Card'})-[:SUPPORTS_THEME]->(t:Theme)
        RETURN t.name as theme
        ORDER BY theme
    """)

    assert len(result) == 2
    assert result[0]["theme"] == "graveyard_value"
    assert result[1]["theme"] == "reanimation"
