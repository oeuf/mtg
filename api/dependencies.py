"""FastAPI dependencies for dependency injection."""

import os
from functools import lru_cache
from typing import Any


class MockNeo4jConnection:
    """Mock Neo4j connection for demo mode when database isn't available."""

    # Sample data for demos
    SAMPLE_COMMANDERS = [
        {
            "name": "Muldrotha, the Gravetide",
            "mana_cost": "{3}{B}{G}{U}",
            "cmc": 6,
            "type_line": "Legendary Creature — Elemental Avatar",
            "oracle_text": "During each of your turns, you may play a land and cast a permanent spell of each permanent type from your graveyard.",
            "color_identity": ["B", "G", "U"],
            "mechanics": ["graveyard_recursion", "permanent_cast"],
            "functional_categories": ["recursion", "value"],
            "synergies": ["self_mill", "sacrifice", "etb_triggers"]
        },
        {
            "name": "Atraxa, Praetors' Voice",
            "mana_cost": "{G}{W}{U}{B}",
            "cmc": 4,
            "type_line": "Legendary Creature — Phyrexian Angel Horror",
            "oracle_text": "Flying, vigilance, deathtouch, lifelink\nAt the beginning of your end step, proliferate.",
            "color_identity": ["B", "G", "U", "W"],
            "mechanics": ["proliferate", "flying", "vigilance", "deathtouch", "lifelink"],
            "functional_categories": ["counters", "value"],
            "synergies": ["counters", "planeswalkers", "infect"]
        },
        {
            "name": "The Wise Mothman",
            "mana_cost": "{3}{B}{G}",
            "cmc": 5,
            "type_line": "Legendary Creature — Insect Mutant",
            "oracle_text": "Flying\nWhenever The Wise Mothman attacks or an opponent loses the game, each opponent gets two rad counters.",
            "color_identity": ["B", "G"],
            "mechanics": ["flying", "rad_counters"],
            "functional_categories": ["aggro", "control"],
            "synergies": ["rad_counters", "mill", "combat"]
        },
    ]

    SAMPLE_CARDS = [
        {
            "name": "Sol Ring",
            "mana_cost": "{1}",
            "cmc": 1,
            "type_line": "Artifact",
            "oracle_text": "{T}: Add {C}{C}.",
            "color_identity": [],
            "mechanics": ["mana_production"],
            "functional_categories": ["ramp"],
        },
        {
            "name": "Eternal Witness",
            "mana_cost": "{1}{G}{G}",
            "cmc": 3,
            "type_line": "Creature — Human Shaman",
            "oracle_text": "When Eternal Witness enters the battlefield, you may return target card from your graveyard to your hand.",
            "color_identity": ["G"],
            "mechanics": ["etb_trigger", "graveyard_recursion"],
            "functional_categories": ["recursion"],
        },
        {
            "name": "Spore Frog",
            "mana_cost": "{G}",
            "cmc": 1,
            "type_line": "Creature — Frog",
            "oracle_text": "Sacrifice Spore Frog: Prevent all combat damage that would be dealt this turn.",
            "color_identity": ["G"],
            "mechanics": ["sacrifice", "fog"],
            "functional_categories": ["protection"],
        },
        {
            "name": "Rhystic Study",
            "mana_cost": "{2}{U}",
            "cmc": 3,
            "type_line": "Enchantment",
            "oracle_text": "Whenever an opponent casts a spell, you may draw a card unless that player pays {1}.",
            "color_identity": ["U"],
            "mechanics": ["card_draw", "tax"],
            "functional_categories": ["card_draw"],
        },
        {
            "name": "Sakura-Tribe Elder",
            "mana_cost": "{1}{G}",
            "cmc": 2,
            "type_line": "Creature — Snake Shaman",
            "oracle_text": "Sacrifice Sakura-Tribe Elder: Search your library for a basic land card, put that card onto the battlefield tapped, then shuffle.",
            "color_identity": ["G"],
            "mechanics": ["sacrifice", "land_ramp"],
            "functional_categories": ["ramp"],
        },
    ]

    def execute_query(self, query: str, params: dict[str, Any] = None) -> list[dict]:
        """Execute a mock query returning sample data."""
        params = params or {}

        # Commander queries
        if "Commander" in query:
            results = self.SAMPLE_COMMANDERS.copy()
            if params.get("search"):
                search = params["search"].lower()
                results = [c for c in results if search in c["name"].lower()]
            if params.get("name"):
                results = [c for c in results if c["name"] == params["name"]]
            if params.get("limit"):
                results = results[:params["limit"]]
            return results

        # Card queries
        if "Card" in query:
            results = self.SAMPLE_CARDS.copy()
            if params.get("search"):
                search = params["search"].lower()
                results = [c for c in results if search in c["name"].lower()]
            if params.get("name"):
                results = [c for c in results if c["name"] == params["name"]]
            if params.get("role"):
                role = params["role"]
                results = [c for c in results if role in c.get("functional_categories", [])]
            if params.get("limit"):
                results = results[:params["limit"]]
            return results

        # Default empty
        return []

    def close(self):
        """No-op for mock."""
        pass


# Cache for connections
_connection = None


def get_neo4j_connection():
    """Get Neo4j connection, falling back to mock if not configured."""
    global _connection

    if _connection is not None:
        return _connection

    password = os.environ.get("NEO4J_PASSWORD")

    if password:
        # Real Neo4j connection
        from src.graph.connection import Neo4jConnection
        uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        user = os.environ.get("NEO4J_USER", "neo4j")
        _connection = Neo4jConnection(uri, user, password)
    else:
        # Mock mode for demos
        print("WARNING: NEO4J_PASSWORD not set, running in demo mode with sample data")
        _connection = MockNeo4jConnection()

    return _connection


def get_db():
    """Dependency for Neo4j connection."""
    return get_neo4j_connection()
