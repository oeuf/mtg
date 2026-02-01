"""Infer card-to-card synergies from mechanics and roles."""

import json
from typing import List, Dict, Tuple
from src.graph.connection import Neo4jConnection
from src.synergy.feature_scorers import FeatureScorers


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

    def __init__(self):
        self.scorers = FeatureScorers()

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

    def compute_synergy_score(self, card1: Dict, card2: Dict) -> Tuple[float, Dict]:
        """Compute comprehensive synergy score between two cards."""

        dimension_scores = {}

        # 1. Mechanic overlap
        dimension_scores["mechanic_overlap"] = self.scorers.score_mechanic_overlap(
            card1.get("mechanics", []),
            card2.get("mechanics", [])
        )

        # 2. Role compatibility
        dimension_scores["role_compatibility"] = self.scorers.score_role_compatibility(
            card1.get("functional_categories", []),
            card2.get("functional_categories", [])
        )

        # 3. Theme alignment
        dimension_scores["theme_alignment"] = self.scorers.score_theme_alignment(
            card1.get("themes", []),
            card2.get("themes", [])
        )

        # 4. Zone chains
        dimension_scores["zone_chain"] = self.scorers.score_zone_chain(
            card1.get("zone_interactions", []),
            card2.get("zone_interactions", [])
        )

        # 5. Phase alignment
        dimension_scores["phase_alignment"] = self.scorers.score_phase_alignment(
            card1.get("phase_triggers", []),
            card2.get("phase_triggers", [])
        )

        # 6. Color compatibility
        dimension_scores["color_compatibility"] = self.scorers.score_color_compatibility(
            card1.get("color_identity", []),
            card2.get("color_identity", [])
        )

        # 7. Type synergy
        dimension_scores["type_synergy"] = self.scorers.score_type_synergy(
            card1.get("subtypes", []),
            card2.get("subtypes", []),
            card1.get("type_line", ""),
            card2.get("type_line", "")
        )

        # Ensemble score
        return self.scorers.calculate_ensemble_score(dimension_scores)

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

    def create_enhanced_synergy_relationships(self, conn: Neo4jConnection,
                                             min_synergy_score: float = 0.5,
                                             batch_size: int = 1000) -> Dict:
        """Create SYNERGIZES_WITH relationships with ML-enhanced scoring."""
        print(f"Computing enhanced synergy scores (min_score={min_synergy_score})...")

        # Fetch all card pairs with properties
        # Note: We filter for cards with at least some overlap to reduce computation
        query_fetch = """
        MATCH (c1:Card), (c2:Card)
        WHERE id(c1) < id(c2)
          AND NOT c1:Commander
          AND NOT c2:Commander
          AND (
              // Only process cards with at least some overlap
              size([m IN c1.mechanics WHERE m IN c2.mechanics]) >= 1
              OR size([t IN c1.themes WHERE t IN c2.themes]) >= 1
          )

        // Fetch zone interactions
        OPTIONAL MATCH (c1)-[z1:INTERACTS_WITH_ZONE]->(zone1:Zone)
        OPTIONAL MATCH (c2)-[z2:INTERACTS_WITH_ZONE]->(zone2:Zone)

        // Fetch phase triggers
        OPTIONAL MATCH (c1)-[p1:TRIGGERS_IN_PHASE]->(phase1:Phase)
        OPTIONAL MATCH (c2)-[p2:TRIGGERS_IN_PHASE]->(phase2:Phase)

        WITH c1, c2,
             collect(DISTINCT {zone: zone1.name, interaction_type: z1.interaction_type}) AS zones1,
             collect(DISTINCT {zone: zone2.name, interaction_type: z2.interaction_type}) AS zones2,
             collect(DISTINCT {phase: phase1.name}) AS phases1,
             collect(DISTINCT {phase: phase2.name}) AS phases2

        RETURN c1.name AS name1,
               c1.mechanics AS mechanics1,
               c1.functional_categories AS roles1,
               c1.themes AS themes1,
               c1.color_identity AS colors1,
               c1.subtypes AS subtypes1,
               c1.type_line AS type_line1,
               [z IN zones1 WHERE z.zone IS NOT NULL] AS zone_interactions1,
               [p IN phases1 WHERE p.phase IS NOT NULL] AS phase_triggers1,
               c2.name AS name2,
               c2.mechanics AS mechanics2,
               c2.functional_categories AS roles2,
               c2.themes AS themes2,
               c2.color_identity AS colors2,
               c2.subtypes AS subtypes2,
               c2.type_line AS type_line2,
               [z IN zones2 WHERE z.zone IS NOT NULL] AS zone_interactions2,
               [p IN phases2 WHERE p.phase IS NOT NULL] AS phase_triggers2
        LIMIT $batch_size
        """

        total_created = 0
        offset = 0
        batch_num = 1

        while True:
            pairs = conn.execute_query(query_fetch, {"batch_size": batch_size})

            if not pairs:
                break

            # Compute synergy scores in Python
            synergies = []
            for pair in pairs:
                card1 = {
                    "mechanics": pair.get("mechanics1") or [],
                    "functional_categories": pair.get("roles1") or [],
                    "themes": pair.get("themes1") or [],
                    "color_identity": pair.get("colors1") or [],
                    "subtypes": pair.get("subtypes1") or [],
                    "type_line": pair.get("type_line1") or "",
                    "zone_interactions": pair.get("zone_interactions1") or [],
                    "phase_triggers": pair.get("phase_triggers1") or []
                }
                card2 = {
                    "mechanics": pair.get("mechanics2") or [],
                    "functional_categories": pair.get("roles2") or [],
                    "themes": pair.get("themes2") or [],
                    "color_identity": pair.get("colors2") or [],
                    "subtypes": pair.get("subtypes2") or [],
                    "type_line": pair.get("type_line2") or "",
                    "zone_interactions": pair.get("zone_interactions2") or [],
                    "phase_triggers": pair.get("phase_triggers2") or []
                }

                score, details = self.compute_synergy_score(card1, card2)

                if score >= min_synergy_score:
                    synergies.append({
                        "name1": pair["name1"],
                        "name2": pair["name2"],
                        "score": score,
                        "details": json.dumps(details)  # Convert to JSON string in Python
                    })

            # Batch write to Neo4j
            if synergies:
                query_write = """
                UNWIND $synergies AS syn
                MATCH (c1:Card {name: syn.name1})
                MATCH (c2:Card {name: syn.name2})
                MERGE (c1)-[s:SYNERGIZES_WITH]-(c2)
                SET s.synergy_score = syn.score,
                    s.dimension_scores = syn.details,
                    s.source = "ml_enhanced"
                """
                conn.execute_query(query_write, {"synergies": synergies})
                total_created += len(synergies)
                print(f"  Batch {batch_num}: Created {len(synergies)} relationships (total: {total_created})...")

            batch_num += 1

            # Since we're using LIMIT without SKIP, we'll only get one batch
            # To process all pairs, we'd need pagination, but for now this is a proof-of-concept
            break

        print(f"✓ Created {total_created} enhanced SYNERGIZES_WITH relationships")
        return {"created": total_created}
