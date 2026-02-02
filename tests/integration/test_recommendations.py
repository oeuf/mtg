"""Integration tests for recommendation queries."""

import pytest
from src.graph.connection import Neo4jConnection
from src.validation.recommendations import get_embedding_recommendations, get_similarity_recommendations


@pytest.fixture
def conn():
    """Create Neo4j connection."""
    import os
    password = os.getenv('NEO4J_PASSWORD', 'mtg-commander')
    conn = Neo4jConnection('bolt://localhost:7687', 'neo4j', password)
    yield conn
    conn.close()


def test_get_embedding_recommendations(conn):
    """Test getting recommendations using EMBEDDING_SIMILAR."""
    recs = get_embedding_recommendations(
        conn,
        commander_name="Muldrotha, the Gravetide",
        top_k=10
    )

    assert len(recs) > 0
    assert len(recs) <= 10

    # Check structure
    first = recs[0]
    assert "name" in first
    assert "score" in first
    assert 0.0 <= first["score"] <= 1.0


def test_get_similarity_recommendations(conn):
    """Test getting recommendations using SIMILAR_TO."""
    recs = get_similarity_recommendations(
        conn,
        commander_name="Muldrotha, the Gravetide",
        top_k=10
    )

    assert len(recs) > 0
    assert len(recs) <= 10

    first = recs[0]
    assert "name" in first
    assert "score" in first
