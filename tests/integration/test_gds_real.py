"""Real Neo4j integration tests for GDS scoring.

These tests require:
- A running Neo4j instance with GDS plugin installed
- NEO4J_PASSWORD environment variable set

Tests are skipped if NEO4J_PASSWORD is not set.
"""

import os
import pytest
from src.graph.connection import Neo4jConnection
from src.graph.gds_scoring import GDSScoring

# Skip all tests if no Neo4j password
pytestmark = pytest.mark.skipif(
    not os.environ.get("NEO4J_PASSWORD"),
    reason="NEO4J_PASSWORD not set - skipping real Neo4j tests"
)


@pytest.fixture
def neo4j_conn():
    """Create real Neo4j connection."""
    conn = Neo4jConnection(
        uri="bolt://localhost:7687",
        user="neo4j",
        password=os.environ.get("NEO4J_PASSWORD", "password")
    )
    yield conn
    conn.close()


@pytest.fixture
def gds(neo4j_conn):
    """Create GDS scoring instance."""
    return GDSScoring(neo4j_conn)


@pytest.fixture
def setup_test_data(neo4j_conn):
    """Set up minimal test data for GDS tests."""
    # Create test cards and mechanics
    neo4j_conn.execute_query("""
        // Clean up any existing test data
        MATCH (n) WHERE n.name STARTS WITH 'TestCard_' OR n.name STARTS WITH 'TestMechanic_'
        DETACH DELETE n
    """)

    neo4j_conn.execute_query("""
        // Create test cards
        CREATE (c1:Card {name: 'TestCard_A', cmc: 2})
        CREATE (c2:Card {name: 'TestCard_B', cmc: 3})
        CREATE (c3:Card {name: 'TestCard_C', cmc: 4})

        // Create test mechanics
        CREATE (m1:Mechanic {name: 'TestMechanic_Draw'})
        CREATE (m2:Mechanic {name: 'TestMechanic_Ramp'})

        // Create relationships
        CREATE (c1)-[:HAS_MECHANIC]->(m1)
        CREATE (c2)-[:HAS_MECHANIC]->(m1)
        CREATE (c2)-[:HAS_MECHANIC]->(m2)
        CREATE (c3)-[:HAS_MECHANIC]->(m2)
    """)

    yield

    # Cleanup
    neo4j_conn.execute_query("""
        MATCH (n) WHERE n.name STARTS WITH 'TestCard_' OR n.name STARTS WITH 'TestMechanic_'
        DETACH DELETE n
    """)


class TestGDSRealIntegration:
    """Real integration tests for GDS scoring."""

    def test_create_projection_real(self, gds, setup_test_data):
        """Test creating graph projection with real Neo4j."""
        result = gds.create_projection()

        assert "nodeCount" in result
        assert "relationshipCount" in result
        assert result["nodeCount"] > 0

    def test_compute_pagerank_real(self, gds, setup_test_data):
        """Test PageRank computation with real Neo4j."""
        # Must create projection first
        gds.create_projection()

        result = gds.compute_pagerank()

        assert "nodePropertiesWritten" in result
        assert result["nodePropertiesWritten"] > 0
        assert result["didConverge"] is True

    def test_detect_communities_real(self, gds, setup_test_data):
        """Test Louvain community detection with real Neo4j."""
        # Must create projection first
        gds.create_projection()

        result = gds.detect_communities()

        assert "communityCount" in result
        assert "modularity" in result
        assert result["communityCount"] >= 1

    def test_compute_similarity_real(self, gds, setup_test_data):
        """Test node similarity with real Neo4j."""
        # Must create projection first
        gds.create_projection()

        result = gds.compute_similarity(min_similarity=0.1, top_k=5)

        assert "relationshipsWritten" in result
        assert "nodesCompared" in result

    def test_run_all_real(self, gds, setup_test_data):
        """Test running all GDS algorithms with real Neo4j."""
        results = gds.run_all(min_similarity=0.1, top_k=5)

        assert "projection" in results
        assert "pagerank" in results
        assert "communities" in results
        assert "similarity" in results

        # Verify each algorithm completed
        assert results["pagerank"].get("nodePropertiesWritten", 0) > 0
        assert results["communities"].get("communityCount", 0) >= 1

    def test_pagerank_scores_written_to_nodes(self, neo4j_conn, gds, setup_test_data):
        """Test that PageRank scores are actually written to nodes."""
        gds.create_projection()
        gds.compute_pagerank()

        # Query for pagerank scores on test cards
        result = neo4j_conn.execute_query("""
            MATCH (c:Card)
            WHERE c.name STARTS WITH 'TestCard_'
            RETURN c.name AS name, c.pagerank_score AS score
            ORDER BY c.name
        """)

        assert len(result) == 3
        for row in result:
            assert row["score"] is not None
            assert row["score"] > 0

    def test_community_ids_written_to_nodes(self, neo4j_conn, gds, setup_test_data):
        """Test that community IDs are actually written to nodes."""
        gds.create_projection()
        gds.detect_communities()

        # Query for community IDs on test cards
        result = neo4j_conn.execute_query("""
            MATCH (c:Card)
            WHERE c.name STARTS WITH 'TestCard_'
            RETURN c.name AS name, c.community_id AS community
            ORDER BY c.name
        """)

        assert len(result) == 3
        for row in result:
            assert row["community"] is not None
