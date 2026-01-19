"""Pytest configuration for E2E tests."""

import pytest
import os


def pytest_configure(config):
    """Add e2e marker."""
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end (requires Neo4j)"
    )


@pytest.fixture(scope="session")
def neo4j_available():
    """Check if Neo4j is available for testing."""
    neo4j_uri = os.environ.get("NEO4J_TEST_URI", "bolt://localhost:7687")
    neo4j_password = os.environ.get("NEO4J_TEST_PASSWORD")

    if not neo4j_password:
        pytest.skip("NEO4J_TEST_PASSWORD not set, skipping E2E tests")

    from src.graph.connection import Neo4jConnection

    try:
        conn = Neo4jConnection(neo4j_uri, "neo4j", neo4j_password)
        conn.close()
        return True
    except Exception as e:
        pytest.skip(f"Neo4j not available: {e}")


@pytest.fixture(scope="function")
def neo4j_test_connection(neo4j_available):
    """Provide clean Neo4j connection for each test."""
    from src.graph.connection import Neo4jConnection

    neo4j_uri = os.environ.get("NEO4J_TEST_URI", "bolt://localhost:7687")
    neo4j_password = os.environ.get("NEO4J_TEST_PASSWORD")

    conn = Neo4jConnection(neo4j_uri, "neo4j", neo4j_password)

    # Clean database before test
    conn.execute_query("MATCH (n) DETACH DELETE n")

    yield conn

    # Clean database after test
    conn.execute_query("MATCH (n) DETACH DELETE n")
    conn.close()
