"""Infer card-to-card synergies from mechanics and roles."""

from src.graph.connection import Neo4jConnection


class CardSynergyEngine:
    """Infer synergies between cards based on shared mechanics and roles."""

    ROLE_SYNERGIES = {
        ("etb_trigger", "sacrifice_outlet"): 0.9,
        ("etb_trigger", "recursion"): 0.85,
        ("dies_trigger", "sacrifice_outlet"): 0.95,
        ("recursion", "self_mill"): 0.8,
        ("token_generation", "sacrifice_outlet"): 0.85,
        ("ramp", "card_draw"): 0.6,
        ("removal", "protection"): 0.5,
    }

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

    def calculate_role_compatibility(self, roles1: list[str], roles2: list[str]) -> float:
        """Calculate compatibility score between two sets of roles."""
        if not roles1 or not roles2:
            return 0.0

        max_score = 0.0

        for r1 in roles1:
            for r2 in roles2:
                key1 = (r1, r2)
                key2 = (r2, r1)
                score = max(
                    self.ROLE_SYNERGIES.get(key1, 0.0),
                    self.ROLE_SYNERGIES.get(key2, 0.0)
                )
                max_score = max(max_score, score)

        if set(roles1) & set(roles2):
            max_score *= 0.3

        return max_score
