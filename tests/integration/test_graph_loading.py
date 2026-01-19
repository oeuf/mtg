"""Integration tests for loading cards into Neo4j graph.

Tests the full pipeline:
1. Parse MTGJSON data
2. Enrich with functional roles and mechanics
3. Load into Neo4j
4. Verify nodes and relationships

These tests require a running Neo4j instance.
"""

import os
import json
import pytest
from src.graph.connection import Neo4jConnection
from src.graph.loaders import (
    load_card_to_graph,
    batch_load_cards,
    create_mechanic_relationships,
    create_role_relationships,
    create_related_card_relationships,
    integrate_related_cards,
)
from src.data.atomic_cards_parser import AtomicCardsParser
from src.data.related_cards_parser import RelatedCardsParser
from src.parsing.enrichment import enrich_card_data


# Neo4j connection settings
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "mtg-commander")


@pytest.fixture(scope="module")
def neo4j_conn():
    """Create a Neo4j connection for integration tests."""
    conn = Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    conn.create_constraints()
    yield conn
    conn.close()


@pytest.fixture(scope="module")
def sample_cards():
    """Load and enrich sample cards from fixture."""
    fixture_path = "tests/fixtures/mtgjson/sample_atomic_cards.json"
    parser = AtomicCardsParser()
    cards = parser.parse(fixture_path)
    enriched = enrich_card_data(cards)
    return enriched


@pytest.fixture(scope="module")
def related_cards():
    """Load related cards from fixture."""
    fixture_path = "tests/fixtures/mtgjson/sample_related_cards.json"
    parser = RelatedCardsParser()
    return parser.parse(fixture_path)


@pytest.fixture(scope="module")
def loaded_graph(neo4j_conn, sample_cards, related_cards):
    """Load all sample cards and relationships into graph."""
    # Clear existing test data
    neo4j_conn.execute_query("MATCH (n) DETACH DELETE n")

    # Load cards
    batch_load_cards(neo4j_conn, sample_cards)

    # Create relationships
    for card in sample_cards:
        create_mechanic_relationships(neo4j_conn, card)
        create_role_relationships(neo4j_conn, card)

    # Integrate related cards
    integrate_related_cards(neo4j_conn, related_cards)

    return neo4j_conn


class TestCardLoading:
    """Tests for loading cards into the graph."""

    def test_cards_loaded(self, loaded_graph):
        """Verify all sample cards are loaded."""
        result = loaded_graph.execute_query(
            "MATCH (c:Card) RETURN count(c) AS count"
        )
        # 5 cards in fixture (Sol Ring, Muldrotha, Eternal Witness, Dramatic Reversal, Isochron Scepter)
        # But Muldrotha is a Commander, so 4 Card nodes + 1 Commander node
        assert result[0]["count"] >= 4

    def test_commander_loaded_with_label(self, loaded_graph):
        """Verify Muldrotha is loaded as Commander."""
        result = loaded_graph.execute_query(
            "MATCH (c:Commander {name: 'Muldrotha, the Gravetide'}) RETURN c"
        )
        assert len(result) == 1
        commander = result[0]["c"]
        assert commander["color_identity"] == ["B", "G", "U"]

    def test_card_properties_loaded(self, loaded_graph):
        """Verify card properties are correctly loaded."""
        result = loaded_graph.execute_query(
            "MATCH (c:Card {name: 'Sol Ring'}) RETURN c"
        )
        assert len(result) == 1
        sol_ring = result[0]["c"]
        assert sol_ring["cmc"] == 1
        assert sol_ring["mana_cost"] == "{1}"
        assert "ramp" in sol_ring["functional_categories"]

    def test_eternal_witness_has_recursion_role(self, loaded_graph):
        """Verify Eternal Witness is correctly categorized."""
        result = loaded_graph.execute_query(
            "MATCH (c:Card {name: 'Eternal Witness'}) RETURN c"
        )
        assert len(result) == 1
        card = result[0]["c"]
        assert "recursion" in card["functional_categories"]


class TestMechanicRelationships:
    """Tests for [:HAS_MECHANIC] relationships."""

    def test_mechanic_nodes_created(self, loaded_graph):
        """Verify mechanic nodes are created."""
        result = loaded_graph.execute_query(
            "MATCH (m:Mechanic) RETURN m.name AS name"
        )
        mechanic_names = [r["name"] for r in result]
        # Isochron Scepter has Imprint keyword
        assert "Imprint" in mechanic_names or len(mechanic_names) > 0

    def test_card_has_mechanic_relationship(self, loaded_graph):
        """Verify cards have mechanic relationships."""
        result = loaded_graph.execute_query("""
            MATCH (c:Card {name: 'Eternal Witness'})-[r:HAS_MECHANIC]->(m:Mechanic)
            RETURN m.name AS mechanic, r.is_primary AS is_primary
        """)
        # Eternal Witness should have etb_trigger mechanic
        mechanics = [r["mechanic"] for r in result]
        assert "etb_trigger" in mechanics


class TestRoleRelationships:
    """Tests for [:FILLS_ROLE] relationships."""

    def test_role_nodes_created(self, loaded_graph):
        """Verify functional role nodes are created."""
        result = loaded_graph.execute_query(
            "MATCH (r:Functional_Role) RETURN r.name AS name"
        )
        role_names = [r["name"] for r in result]
        assert "ramp" in role_names
        assert "recursion" in role_names

    def test_sol_ring_fills_ramp_role(self, loaded_graph):
        """Verify Sol Ring fills ramp role."""
        result = loaded_graph.execute_query("""
            MATCH (c:Card {name: 'Sol Ring'})-[r:FILLS_ROLE]->(role:Functional_Role {name: 'ramp'})
            RETURN r.efficiency_score AS efficiency
        """)
        assert len(result) == 1
        assert result[0]["efficiency"] > 0


class TestComboRelationships:
    """Tests for [:COMBOS_WITH] relationships from RelatedCards."""

    def test_dramatic_reversal_combos_with_isochron(self, loaded_graph):
        """Verify Dramatic Reversal + Isochron Scepter combo is loaded."""
        result = loaded_graph.execute_query("""
            MATCH (c1:Card {name: 'Dramatic Reversal'})
                  -[r:COMBOS_WITH]->(c2:Card {name: 'Isochron Scepter'})
            RETURN r.source AS source, r.confidence AS confidence
        """)
        assert len(result) == 1, "Dramatic Reversal + Isochron Scepter combo not found"
        assert result[0]["source"] == "mtgjson_spellbook"
        assert result[0]["confidence"] == 1.0

    def test_commonly_paired_relationships(self, loaded_graph):
        """Verify COMMONLY_PAIRED_WITH relationships are created."""
        result = loaded_graph.execute_query("""
            MATCH (c1:Card)-[r:COMMONLY_PAIRED_WITH]->(c2:Card)
            RETURN c1.name AS card1, c2.name AS card2
        """)
        # Should have pairing between Dramatic Reversal and Isochron Scepter
        pairs = [(r["card1"], r["card2"]) for r in result]
        assert len(pairs) > 0


class TestGraphStatistics:
    """Tests for overall graph statistics."""

    def test_graph_node_counts(self, loaded_graph):
        """Verify expected node counts."""
        # Cards (non-commanders)
        cards = loaded_graph.execute_query(
            "MATCH (c:Card) WHERE NOT c:Commander RETURN count(c) AS count"
        )[0]["count"]
        assert cards >= 4

        # Commanders
        commanders = loaded_graph.execute_query(
            "MATCH (c:Commander) RETURN count(c) AS count"
        )[0]["count"]
        assert commanders >= 1

        # Mechanics
        mechanics = loaded_graph.execute_query(
            "MATCH (m:Mechanic) RETURN count(m) AS count"
        )[0]["count"]
        assert mechanics > 0

        # Roles
        roles = loaded_graph.execute_query(
            "MATCH (r:Functional_Role) RETURN count(r) AS count"
        )[0]["count"]
        assert roles > 0

    def test_relationship_counts(self, loaded_graph):
        """Verify relationships exist."""
        # HAS_MECHANIC
        has_mechanic = loaded_graph.execute_query(
            "MATCH ()-[r:HAS_MECHANIC]->() RETURN count(r) AS count"
        )[0]["count"]
        assert has_mechanic > 0

        # FILLS_ROLE
        fills_role = loaded_graph.execute_query(
            "MATCH ()-[r:FILLS_ROLE]->() RETURN count(r) AS count"
        )[0]["count"]
        assert fills_role > 0

        # COMBOS_WITH
        combos = loaded_graph.execute_query(
            "MATCH ()-[r:COMBOS_WITH]->() RETURN count(r) AS count"
        )[0]["count"]
        assert combos >= 1  # At least Dramatic Reversal + Isochron
