"""Integration tests for GDS scoring module."""

import pytest
from unittest.mock import Mock, MagicMock
from src.graph.gds_scoring import GDSScoring
from src.graph.connection import Neo4jConnection


def test_create_graph_projection():
    """Test that graph projection is created with correct parameters."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = [
        {"graphName": "synergy-graph", "nodeCount": 100, "relationshipCount": 500}
    ]

    gds = GDSScoring(mock_conn)
    result = gds.create_projection()

    # Verify projection query was called (second call, after drop)
    assert mock_conn.execute_query.call_count >= 1
    # Get the last call (create_projection)
    calls = [c[0][0] for c in mock_conn.execute_query.call_args_list]
    projection_call = [c for c in calls if "gds.graph.project" in c][0]

    assert "synergy-graph" in projection_call
    assert "Card" in projection_call
    assert "HAS_MECHANIC" in projection_call


def test_drop_projection():
    """Test dropping existing projection."""
    mock_conn = Mock(spec=Neo4jConnection)

    gds = GDSScoring(mock_conn)
    gds.drop_projection()

    assert mock_conn.execute_query.called
    call_args = mock_conn.execute_query.call_args[0][0]
    assert "gds.graph.drop" in call_args
