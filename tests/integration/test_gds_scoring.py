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


def test_compute_pagerank():
    """Test PageRank computation."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = [{
        "nodePropertiesWritten": 100,
        "ranIterations": 20,
        "didConverge": True
    }]

    gds = GDSScoring(mock_conn)
    result = gds.compute_pagerank()

    assert mock_conn.execute_query.called
    call_args = mock_conn.execute_query.call_args[0][0]

    assert "gds.pageRank" in call_args
    assert "pagerank_score" in call_args
    assert result["nodePropertiesWritten"] == 100


def test_detect_communities():
    """Test Louvain community detection."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = [{
        "communityCount": 15,
        "modularity": 0.65,
        "nodePropertiesWritten": 100
    }]

    gds = GDSScoring(mock_conn)
    result = gds.detect_communities()

    assert mock_conn.execute_query.called
    call_args = mock_conn.execute_query.call_args[0][0]

    assert "gds.louvain" in call_args
    assert "community_id" in call_args
    assert result["communityCount"] == 15


def test_compute_similarity():
    """Test node similarity computation."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = [{
        "relationshipsWritten": 500,
        "nodesCompared": 100
    }]

    gds = GDSScoring(mock_conn)
    result = gds.compute_similarity(min_similarity=0.5, top_k=10)

    assert mock_conn.execute_query.called
    call_args = mock_conn.execute_query.call_args[0][0]

    assert "gds.nodeSimilarity" in call_args
    assert "SIMILAR_TO" in call_args
    assert result["relationshipsWritten"] == 500
