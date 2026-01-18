"""Pre-built queries for deckbuilding recommendations."""

from src.graph.connection import Neo4jConnection


class DeckbuildingQueries:
    """Pre-built queries for deckbuilding recommendations."""

    @staticmethod
    def find_synergistic_cards(conn: Neo4jConnection,
                              commander_name: str,
                              max_cmc: int = 4,
                              min_strength: float = 0.7,
                              limit: int = 50) -> list[dict]:
        """Find cards that synergize with commander via shared mechanics."""

        query = """
        MATCH (cmd:Commander {name: $commander_name})
              -[s:SYNERGIZES_WITH_MECHANIC]->(m:Mechanic)
              <-[:HAS_MECHANIC]-(card:Card)
        WHERE card.cmc <= $max_cmc
          AND s.strength >= $min_strength
          AND NOT card:Commander
        RETURN DISTINCT card.name AS name,
               card.mana_cost AS mana_cost,
               card.type_line AS type,
               card.cmc AS cmc,
               card.oracle_text AS text,
               m.name AS shared_mechanic,
               s.strength AS synergy_strength,
               card.functional_categories AS roles
        ORDER BY s.strength DESC, card.cmc ASC
        LIMIT $limit
        """

        return conn.execute_query(query, {
            "commander_name": commander_name,
            "max_cmc": max_cmc,
            "min_strength": min_strength,
            "limit": limit
        })

    @staticmethod
    def find_known_combos(conn: Neo4jConnection,
                         card_name: str) -> list[dict]:
        """Find explicitly documented combos from MTGJSON."""

        query = """
        MATCH (c1:Card {name: $card_name})
              -[r:COMBOS_WITH {source: "mtgjson_spellbook"}]->(c2:Card)
        RETURN c2.name AS combo_piece,
               c2.oracle_text AS text,
               c2.mana_cost AS cost,
               c2.cmc AS cmc
        ORDER BY c2.cmc ASC
        """

        return conn.execute_query(query, {"card_name": card_name})

    @staticmethod
    def find_token_generators(conn: Neo4jConnection,
                             token_type: str,
                             color_identity: list[str] = None,
                             max_cmc: int = None) -> list[dict]:
        """Find all cards that create a specific token."""

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

        return conn.execute_query(query, {
            "token_type": token_type,
            "color_identity": color_identity,
            "max_cmc": max_cmc
        })

    @staticmethod
    def find_cards_by_role(conn: Neo4jConnection,
                          role: str,
                          color_identity: list[str],
                          max_cmc: int = 3,
                          min_efficiency: float = 0.6) -> list[dict]:
        """Find efficient cards for a functional role in colors."""

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

        return conn.execute_query(query, {
            "role": role,
            "color_identity": color_identity,
            "max_cmc": max_cmc,
            "min_efficiency": min_efficiency
        })

    @staticmethod
    def build_deck_shell(conn: Neo4jConnection,
                        commander_name: str) -> dict:
        """Build a deck shell with role distribution (8x8 method)."""

        # Define role distribution
        roles_needed = {
            "ramp": 9,
            "card_draw": 9,
            "removal": 9,
            "protection": 5,
            "win_condition": 5
        }

        # Get commander color identity
        query_colors = """
        MATCH (cmd:Commander {name: $commander_name})
        RETURN cmd.color_identity AS colors
        """
        result = conn.execute_query(query_colors, {"commander_name": commander_name})

        if not result:
            return {"error": f"Commander '{commander_name}' not found"}

        colors = result[0]["colors"]

        deck_shell = {
            "commander": commander_name,
            "color_identity": colors,
            "cards_by_role": {}
        }

        # Find synergistic cards for each role
        for role, count in roles_needed.items():
            query_cards = """
            MATCH (cmd:Commander {name: $commander_name})
                  -[s:SYNERGIZES_WITH_MECHANIC]->(m:Mechanic)
                  <-[:HAS_MECHANIC]-(card:Card)
                  -[:FILLS_ROLE]->(r:Functional_Role {name: $role})
            WHERE NOT card:Commander
            RETURN DISTINCT card.name AS name,
                   card.mana_cost AS cost,
                   card.cmc AS cmc,
                   s.strength AS synergy
            ORDER BY s.strength DESC, card.cmc ASC
            LIMIT $count
            """

            cards = conn.execute_query(query_cards, {
                "commander_name": commander_name,
                "role": role,
                "count": count
            })

            deck_shell["cards_by_role"][role] = cards

        return deck_shell

    @staticmethod
    def find_combo_packages(conn: Neo4jConnection,
                           commander_name: str) -> list[dict]:
        """Find known combo packages relevant to commander."""

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

        return conn.execute_query(query, {"commander_name": commander_name})
