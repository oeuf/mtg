"""Neo4j Graph Data Science scoring operations."""

from src.graph.connection import Neo4jConnection


class GDSScoring:
    """Compute graph-based scores using Neo4j GDS."""

    GRAPH_NAME = "synergy-graph"

    def __init__(self, conn: Neo4jConnection):
        """Initialize with Neo4j connection."""
        self.conn = conn

    def drop_projection(self):
        """Drop existing graph projection if it exists."""
        query = f"""
        CALL gds.graph.drop('{self.GRAPH_NAME}', false)
        YIELD graphName
        RETURN graphName
        """
        try:
            self.conn.execute_query(query)
            print(f"✓ Dropped existing projection '{self.GRAPH_NAME}'")
        except Exception:
            # Graph doesn't exist, that's fine
            pass

    def create_projection(self) -> dict:
        """Create in-memory graph projection for GDS algorithms.

        Returns:
            Projection metadata
        """
        # Drop existing projection first
        self.drop_projection()

        query = """
        CALL gds.graph.project(
            'synergy-graph',
            ['Card', 'Commander', 'Mechanic', 'Functional_Role'],
            {
                HAS_MECHANIC: {orientation: 'UNDIRECTED'},
                FILLS_ROLE: {orientation: 'UNDIRECTED'},
                COMBOS_WITH: {orientation: 'UNDIRECTED'},
                SYNERGIZES_WITH_MECHANIC: {orientation: 'UNDIRECTED'}
            }
        )
        YIELD graphName, nodeCount, relationshipCount
        RETURN graphName, nodeCount, relationshipCount
        """

        result = self.conn.execute_query(query)
        if result:
            print(f"✓ Created projection '{self.GRAPH_NAME}'")
            print(f"  Nodes: {result[0]['nodeCount']}")
            print(f"  Relationships: {result[0]['relationshipCount']}")
        return result[0] if result else {}

    def projection_exists(self) -> bool:
        """Check if projection exists."""
        query = """
        CALL gds.graph.exists($name) YIELD exists
        RETURN exists
        """
        result = self.conn.execute_query(query, {"name": self.GRAPH_NAME})
        return result[0]["exists"] if result else False
