"""Integration tests for Neo4j connection and Graph Data Science plugin.

These tests require a running Neo4j instance with GDS plugin:
    docker run -d --name neo4j-mtg -p 7474:7474 -p 7687:7687 \
        -e NEO4J_AUTH=neo4j/mtg-commander \
        -e NEO4J_PLUGINS='["graph-data-science"]' \
        neo4j:5.26.0
"""

import os
import pytest
from src.graph.connection import Neo4jConnection


# Neo4j connection settings - can be overridden by environment variables
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "mtg-commander")


@pytest.fixture(scope="module")
def neo4j_conn():
    """Create a Neo4j connection for integration tests."""
    conn = Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    yield conn
    conn.close()


class TestNeo4jConnection:
    """Tests for basic Neo4j connectivity."""

    def test_connection_works(self, neo4j_conn):
        """Verify we can connect and execute a simple query."""
        result = neo4j_conn.execute_query("RETURN 1 AS test")
        assert len(result) == 1
        assert result[0]["test"] == 1

    def test_create_and_query_node(self, neo4j_conn):
        """Verify we can create and query nodes."""
        # Clean up first
        neo4j_conn.execute_query("MATCH (n:TestNode) DELETE n")

        # Create a test node
        neo4j_conn.execute_query(
            "CREATE (n:TestNode {name: $name})",
            {"name": "test_card"}
        )

        # Query it back
        result = neo4j_conn.execute_query(
            "MATCH (n:TestNode {name: $name}) RETURN n.name AS name",
            {"name": "test_card"}
        )
        assert len(result) == 1
        assert result[0]["name"] == "test_card"

        # Clean up
        neo4j_conn.execute_query("MATCH (n:TestNode) DELETE n")

    def test_constraints_created(self, neo4j_conn):
        """Verify constraints can be created."""
        neo4j_conn.create_constraints()

        # Check that card constraint exists
        result = neo4j_conn.execute_query("SHOW CONSTRAINTS")
        constraint_names = [r.get("name", "") for r in result]

        # Should have card_name constraint
        assert any("card_name" in name for name in constraint_names)


class TestGraphDataSciencePlugin:
    """Tests to verify GDS plugin is installed and working."""

    def test_gds_plugin_installed(self, neo4j_conn):
        """Verify GDS plugin is available."""
        result = neo4j_conn.execute_query("RETURN gds.version() AS version")
        assert len(result) == 1
        version = result[0]["version"]
        assert version is not None
        assert len(version) > 0
        print(f"GDS version: {version}")

    def test_gds_list_procedures(self, neo4j_conn):
        """Verify GDS procedures are available."""
        result = neo4j_conn.execute_query(
            "CALL gds.list() YIELD name RETURN name LIMIT 10"
        )
        assert len(result) > 0
        # Should have common algorithms
        procedure_names = [r["name"] for r in result]
        print(f"Available GDS procedures: {procedure_names[:5]}...")

    def test_gds_node_similarity_available(self, neo4j_conn):
        """Verify node similarity algorithm is available (needed for recommendations)."""
        result = neo4j_conn.execute_query(
            "CALL gds.list() YIELD name WHERE name CONTAINS 'nodeSimilarity' RETURN name"
        )
        assert len(result) > 0, "nodeSimilarity algorithm not found in GDS"

    def test_gds_louvain_available(self, neo4j_conn):
        """Verify Louvain community detection is available (needed for synergy clusters)."""
        result = neo4j_conn.execute_query(
            "CALL gds.list() YIELD name WHERE name CONTAINS 'louvain' RETURN name"
        )
        assert len(result) > 0, "louvain algorithm not found in GDS"

    def test_gds_pagerank_available(self, neo4j_conn):
        """Verify PageRank is available (useful for card importance ranking)."""
        result = neo4j_conn.execute_query(
            "CALL gds.list() YIELD name WHERE name CONTAINS 'pageRank' RETURN name"
        )
        assert len(result) > 0, "pageRank algorithm not found in GDS"
