"""Infer card-to-card synergies from mechanics and roles."""

from typing import List, Dict
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

    def find_mechanic_synergies(self, conn: Neo4jConnection, min_shared_mechanics: int = 2) -> List[Dict]:
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

    def calculate_role_compatibility(self, roles1: List[str], roles2: List[str]) -> float:
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

    def create_synergy_relationships(self, conn: Neo4jConnection,
                                    min_shared_mechanics: int = 2,
                                    min_synergy_score: float = 0.6) -> Dict:
        """Create SYNERGIZES_WITH relationships between synergistic cards."""
        print(f"Creating card synergy relationships (min_mechanics={min_shared_mechanics}, min_score={min_synergy_score})...")

        query = """
        MATCH (c1:Card)-[:HAS_MECHANIC]->(m:Mechanic)<-[:HAS_MECHANIC]-(c2:Card)
        WHERE id(c1) < id(c2) AND NOT c1:Commander AND NOT c2:Commander

        WITH c1, c2, collect(DISTINCT m.name) AS shared_mechanics
        WHERE size(shared_mechanics) >= $min_shared

        WITH c1, c2, shared_mechanics,
             (toFloat(size(shared_mechanics)) / 5.0) AS mechanic_score

        WHERE mechanic_score >= ($min_score * 0.5)

        MERGE (c1)-[s:SYNERGIZES_WITH]->(c2)
        SET s.synergy_score = mechanic_score,
            s.shared_mechanics = shared_mechanics,
            s.source = "mechanic_inference"

        RETURN count(s) AS created
        """

        result = conn.execute_query(query, {
            "min_shared": min_shared_mechanics,
            "min_score": min_synergy_score
        })

        created = result[0]["created"] if result else 0
        print(f"✓ Created {created} SYNERGIZES_WITH relationships")

        return {"created": created}
