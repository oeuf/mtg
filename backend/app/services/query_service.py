"""QueryService provides deckbuilding query methods over a Neo4j connection."""

from typing import List, Dict, Optional


class QueryService:
    """Service layer for deckbuilding queries against the graph."""

    def __init__(self, connection):
        self._conn = connection

    def find_synergistic_cards(
        self,
        commander_name: str,
        max_cmc: int = 4,
        min_strength: float = 0.7,
        limit: int = 50,
    ) -> List[Dict]:
        query = """
        MATCH (cmd:Commander {name: $commander_name})
        MATCH (card:Card)
        WHERE card.cmc <= $max_cmc
          AND NOT card:Commander
          AND ALL(c IN card.color_identity WHERE c IN cmd.color_identity)
        OPTIONAL MATCH (cmd)-[s:SYNERGIZES_WITH_MECHANIC]->(m:Mechanic)<-[:HAS_MECHANIC]-(card)
        OPTIONAL MATCH (card)-[:FILLS_ROLE]->(r:Functional_Role)
        WITH card,
             max(coalesce(s.strength, 0)) AS synergy_score,
             collect(DISTINCT m.name) AS shared_mechanics,
             collect(DISTINCT r.name) AS roles
        WHERE synergy_score >= $min_strength OR size(roles) > 0
        WITH card, synergy_score, shared_mechanics, roles,
             (synergy_score + 0.3 * size(roles)) AS combined_score
        RETURN DISTINCT card.name AS name,
               card.mana_cost AS mana_cost,
               card.type_line AS type,
               card.cmc AS cmc,
               card.oracle_text AS text,
               shared_mechanics,
               synergy_score AS synergy_strength,
               roles,
               combined_score
        ORDER BY combined_score DESC, card.cmc ASC
        LIMIT $limit
        """
        return self._conn.execute_query(query, {
            "commander_name": commander_name,
            "max_cmc": max_cmc,
            "min_strength": min_strength,
            "limit": limit,
        })

    def find_known_combos(self, card_name: str) -> List[Dict]:
        query = """
        MATCH (c1:Card {name: $card_name})
              -[r:COMBOS_WITH {source: "mtgjson_spellbook"}]->(c2:Card)
        RETURN c2.name AS combo_piece,
               c2.oracle_text AS text,
               c2.mana_cost AS cost,
               c2.cmc AS cmc
        ORDER BY c2.cmc ASC
        """
        return self._conn.execute_query(query, {"card_name": card_name})

    def find_token_generators(
        self,
        token_type: str,
        color_identity: Optional[List[str]] = None,
        max_cmc: Optional[int] = None,
    ) -> List[Dict]:
        query = """
        MATCH (card:Card)-[:CREATES_TOKEN]->(t:Token {name: $token_type})
        WHERE ($color_identity IS NULL OR
               ALL(color IN card.color_identity WHERE color IN $color_identity))
          AND ($max_cmc IS NULL OR card.cmc <= $max_cmc)
        RETURN card.name AS name,
               card.mana_cost AS cost,
               card.cmc AS cmc,
               card.type_line AS type,
               card.oracle_text AS text
        ORDER BY card.cmc ASC
        """
        return self._conn.execute_query(query, {
            "token_type": token_type,
            "color_identity": color_identity,
            "max_cmc": max_cmc,
        })

    def find_cards_by_role(
        self,
        role: str,
        color_identity: List[str],
        max_cmc: int = 3,
        min_efficiency: float = 0.6,
    ) -> List[Dict]:
        query = """
        MATCH (card:Card)-[r:FILLS_ROLE]->(role:Functional_Role {name: $role})
        WHERE ALL(color IN card.color_identity WHERE color IN $color_identity)
          AND card.cmc <= $max_cmc
          AND r.efficiency_score >= $min_efficiency
        RETURN card.name AS name,
               card.mana_cost AS mana_cost,
               card.cmc AS cmc,
               r.efficiency_score AS efficiency,
               r.conditionality AS conditionality,
               card.oracle_text AS text
        ORDER BY r.efficiency_score DESC, card.cmc ASC
        LIMIT 20
        """
        return self._conn.execute_query(query, {
            "role": role,
            "color_identity": color_identity,
            "max_cmc": max_cmc,
            "min_efficiency": min_efficiency,
        })

    def build_deck_shell(self, commander_name: str) -> Dict:
        roles_needed = {
            "ramp": 9,
            "card_draw": 9,
            "removal": 9,
            "protection": 5,
            "win_condition": 5,
        }

        query_colors = """
        MATCH (cmd:Commander {name: $commander_name})
        RETURN cmd.color_identity AS colors
        """
        result = self._conn.execute_query(query_colors, {"commander_name": commander_name})

        if not result:
            raise ValueError(f"Commander '{commander_name}' not found")

        colors = result[0]["colors"]

        deck_shell = {
            "commander": commander_name,
            "color_identity": colors,
            "cards_by_role": {},
        }

        for role, count in roles_needed.items():
            query_cards = """
            MATCH (cmd:Commander {name: $commander_name})
            MATCH (card:Card)-[:FILLS_ROLE]->(r:Functional_Role {name: $role})
            WHERE NOT card:Commander
              AND ALL(c IN card.color_identity WHERE c IN cmd.color_identity)
            OPTIONAL MATCH (cmd)-[s:SYNERGIZES_WITH_MECHANIC]->(m:Mechanic)<-[:HAS_MECHANIC]-(card)
            WITH card, max(coalesce(s.strength, 0)) AS synergy_bonus
            RETURN DISTINCT card.name AS name,
                   card.mana_cost AS cost,
                   card.cmc AS cmc,
                   synergy_bonus AS synergy
            ORDER BY synergy_bonus DESC, card.cmc ASC
            LIMIT $count
            """
            cards = self._conn.execute_query(query_cards, {
                "commander_name": commander_name,
                "role": role,
                "count": count,
            })
            deck_shell["cards_by_role"][role] = cards

        return deck_shell

    def find_combo_packages(self, commander_name: str) -> List[Dict]:
        query = """
        MATCH (cmd:Commander {name: $commander_name})
              -[:SYNERGIZES_WITH_MECHANIC]->(m:Mechanic)
              <-[:HAS_MECHANIC]-(c1:Card)
              -[combo:COMBOS_WITH {source: "mtgjson_spellbook"}]->(c2:Card)
        RETURN DISTINCT c1.name AS piece1,
               c2.name AS piece2,
               c1.cmc AS cmc1,
               c2.cmc AS cmc2,
               m.name AS shared_mechanic
        ORDER BY (c1.cmc + c2.cmc) ASC
        """
        return self._conn.execute_query(query, {"commander_name": commander_name})

    def find_similar_cards(
        self,
        card_name: str,
        min_similarity: float = 0.5,
        limit: int = 20,
    ) -> List[Dict]:
        query = """
        MATCH (c1:Card {name: $card_name})-[sim:SIMILAR_TO]->(c2:Card)
        WHERE sim.score >= $min_similarity
        OPTIONAL MATCH (c1)-[:HAS_MECHANIC]->(m:Mechanic)<-[:HAS_MECHANIC]-(c2)
        WITH c2, sim.score AS similarity_score, collect(DISTINCT m.name) AS shared_mechanics
        RETURN c2.name AS name,
               c2.mana_cost AS mana_cost,
               c2.cmc AS cmc,
               c2.type_line AS type_line,
               similarity_score,
               shared_mechanics
        ORDER BY similarity_score DESC
        LIMIT $limit
        """
        return self._conn.execute_query(query, {
            "card_name": card_name,
            "min_similarity": min_similarity,
            "limit": limit,
        })
