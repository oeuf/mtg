"""Unit tests for graph connection constraints."""

import pytest
from unittest.mock import MagicMock, patch
from src.graph.connection import Neo4jConnection


@pytest.fixture
def mock_connection():
    """Create a mock Neo4j connection."""
    mock_driver = MagicMock()
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session

    conn = Neo4jConnection.__new__(Neo4jConnection)
    conn.driver = mock_driver
    return conn


def test_create_zone_constraint(mock_connection):
    """Test that Zone constraint is created."""
    queries_called = []

    original_execute = mock_connection.execute_query
    def track_execute(query, params=None):
        queries_called.append(query)
        return original_execute(query, params)

    mock_connection.execute_query = track_execute

    mock_connection.create_constraints()

    # Check if Zone constraint query was called
    assert any('Zone' in call and 'UNIQUE' in call for call in queries_called)


def test_create_phase_constraint(mock_connection):
    """Test that Phase constraint is created."""
    queries_called = []

    original_execute = mock_connection.execute_query
    def track_execute(query, params=None):
        queries_called.append(query)
        return original_execute(query, params)

    mock_connection.execute_query = track_execute

    mock_connection.create_constraints()

    # Check if Phase constraint query was called
    assert any('Phase' in call and 'UNIQUE' in call for call in queries_called)


def test_zone_name_is_unique(mock_connection):
    """Test that zone names must be unique."""
    queries_called = []

    original_execute = mock_connection.execute_query
    def track_execute(query, params=None):
        queries_called.append(query)
        return original_execute(query, params)

    mock_connection.execute_query = track_execute

    mock_connection.create_constraints()

    # Find the Zone constraint
    zone_constraint = next((c for c in queries_called if 'Zone' in c and 'name' in c), None)

    assert zone_constraint is not None
    assert 'UNIQUE' in zone_constraint


def test_phase_name_is_unique(mock_connection):
    """Test that phase names must be unique."""
    queries_called = []

    original_execute = mock_connection.execute_query
    def track_execute(query, params=None):
        queries_called.append(query)
        return original_execute(query, params)

    mock_connection.execute_query = track_execute

    mock_connection.create_constraints()

    # Find the Phase constraint
    phase_constraint = next((c for c in queries_called if 'Phase' in c and 'name' in c), None)

    assert phase_constraint is not None
    assert 'UNIQUE' in phase_constraint
