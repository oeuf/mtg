"""Infer card-to-card synergies from mechanics and roles."""

from src.graph.connection import Neo4jConnection


class CardSynergyEngine:
    """Infer synergies between cards based on shared mechanics and roles."""

    def find_mechanic_synergies(self, conn: Neo4jConnection, min_shared_mechanics: int = 2) -> list[dict]:
        """Find pairs of cards with shared mechanics."""
        query = """
        MATCH (c1:Card)-[:HAS_MECHANIC]->(m:Mechanic)<-[:HAS_MECHANIC]-(c2:Card)
        WHERE id(c1) < id(c2) AND NOT c1:Commander AND NOT c2:Commander

        WITH c1, c2, collect(DISTINCT m.name) AS shared_mechanics
        WHERE size(shared_mechanics) >= $min_shared

        RETURN c1.name AS card1, c2.name AS card2, shared_mechanics,
               size(shared_mechanics) AS mechanic_overlap
        ORDER BY mechanic_overlap DESC
        """

        return conn.execute_query(query, {"min_shared": min_shared_mechanics})
