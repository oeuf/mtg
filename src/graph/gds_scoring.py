"""Neo4j Graph Data Science scoring operations."""

from typing import Dict
from src.graph.connection import Neo4jConnection


class GDSScoring:
    """Compute graph-based scores using Neo4j GDS."""

    GRAPH_NAME = "synergy-graph"

    def __init__(self, conn: Neo4jConnection):
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
            pass

    def create_projection(self) -> Dict:
        """Create in-memory graph projection for GDS algorithms."""
        self.drop_projection()

        query = """
        CALL gds.graph.project(
            'synergy-graph',
            ['Card', 'Commander', 'Mechanic', 'Functional_Role', 'Theme', 'Subtype'],
            {
                HAS_MECHANIC: {orientation: 'UNDIRECTED'},
                FILLS_ROLE: {orientation: 'UNDIRECTED'},
                COMBOS_WITH: {orientation: 'UNDIRECTED'},
                SYNERGIZES_WITH_MECHANIC: {orientation: 'UNDIRECTED'},
                SUPPORTS_THEME: {orientation: 'UNDIRECTED'},
                HAS_SUBTYPE: {orientation: 'UNDIRECTED'}
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

    def compute_similarity(self, topK: int = 10, similarity_cutoff: float = 0.5) -> Dict:
        """Compute node similarity and write SIMILAR_TO relationships."""
        print(f"Computing node similarity (topK={topK}, cutoff={similarity_cutoff})...")

        query = """
        CALL gds.nodeSimilarity.write('synergy-graph', {
            writeRelationshipType: 'SIMILAR_TO',
            writeProperty: 'score',
            topK: $topK,
            similarityCutoff: $cutoff
        })
        YIELD nodesCompared, relationshipsWritten
        RETURN nodesCompared, relationshipsWritten
        """

        result = self.conn.execute_query(query, {
            "topK": topK,
            "cutoff": similarity_cutoff
        })

        if result:
            print(f"✓ Computed similarity for {result[0]['nodesCompared']} nodes")
            print(f"✓ Created {result[0]['relationshipsWritten']} SIMILAR_TO relationships")

        return result[0] if result else {}
