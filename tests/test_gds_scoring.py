"""Tests for GDS scoring operations."""

import pytest
from unittest.mock import Mock
from src.graph.gds_scoring import GDSScoring
from src.graph.connection import Neo4jConnection


def test_create_graph_projection():
    """Test graph projection creation."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = [{
        "graphName": "synergy-graph",
        "nodeCount": 1000,
        "relationshipCount": 5000
    }]

    gds = GDSScoring(mock_conn)
    result = gds.create_projection()

    assert result["graphName"] == "synergy-graph"
    assert result["nodeCount"] == 1000


def test_drop_projection():
    """Test dropping existing projection."""
    mock_conn = Mock(spec=Neo4jConnection)
    gds = GDSScoring(mock_conn)
    gds.drop_projection()

    assert mock_conn.execute_query.called
