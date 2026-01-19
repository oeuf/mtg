"""End-to-end tests for full pipeline with real Neo4j."""

import pytest
from src.data.atomic_cards_parser import AtomicCardsParser
from src.data.related_cards_parser import RelatedCardsParser
from src.parsing.enrichment import enrich_card_data
from src.graph.loaders import (
    batch_load_cards,
    create_mechanic_relationships,
    create_role_relationships,
    integrate_related_cards
)
from src.synergy.inference_engine import SynergyInferenceEngine
from src.synergy.queries import DeckbuildingQueries


@pytest.mark.e2e
def test_full_pipeline_with_neo4j(neo4j_test_connection):
    """Test complete pipeline from parsing to queries with real Neo4j."""
    conn = neo4j_test_connection

    # Step 1: Parse fixtures
    atomic_parser = AtomicCardsParser()
    cards = atomic_parser.parse("tests/fixtures/mtgjson/sample_atomic_cards.json")

    related_parser = RelatedCardsParser()
    related = related_parser.parse("tests/fixtures/mtgjson/sample_related_cards.json")

    # Step 2: Enrich
    enriched = enrich_card_data(cards)

    # Step 3: Create schema
    conn.create_constraints()

    # Step 4: Load cards
    batch_load_cards(conn, enriched)

    # Verify cards loaded
    result = conn.execute_query("MATCH (c:Card) RETURN count(c) AS count")
    assert result[0]["count"] == 4  # 4 non-commander cards

    result = conn.execute_query("MATCH (c:Commander) RETURN count(c) AS count")
    assert result[0]["count"] == 1  # 1 commander (Muldrotha)

    # Step 5: Create relationships
    for card in enriched:
        create_mechanic_relationships(conn, card)
        create_role_relationships(conn, card)

    integrate_related_cards(conn, related)

    # Verify relationships
    result = conn.execute_query("MATCH ()-[r:HAS_MECHANIC]->() RETURN count(r) AS count")
    assert result[0]["count"] > 0

    result = conn.execute_query("MATCH ()-[r:COMBOS_WITH]->() RETURN count(r) AS count")
    assert result[0]["count"] == 1  # Dramatic Reversal -> Isochron Scepter

    # Step 6: Analyze commander
    engine = SynergyInferenceEngine()
    synergies = engine.analyze_commander(conn, "Muldrotha, the Gravetide")

    assert len(synergies) > 0
    assert any(s["mechanic"] == "recursion" for s in synergies)

    # Step 7: Test queries
    # Find known combo
    combos = DeckbuildingQueries.find_known_combos(conn, "Dramatic Reversal")
    assert len(combos) == 1
    assert combos[0]["combo_piece"] == "Isochron Scepter"

    # Find cards by role
    ramp_cards = DeckbuildingQueries.find_cards_by_role(
        conn,
        role="ramp",
        color_identity=[],
        max_cmc=2
    )
    assert len(ramp_cards) > 0
    assert any(c["name"] == "Sol Ring" for c in ramp_cards)


@pytest.mark.e2e
def test_synergistic_cards_query(neo4j_test_connection):
    """Test synergistic cards query with real data."""
    conn = neo4j_test_connection

    # Setup: Load test data
    atomic_parser = AtomicCardsParser()
    cards = atomic_parser.parse("tests/fixtures/mtgjson/sample_atomic_cards.json")
    enriched = enrich_card_data(cards)

    conn.create_constraints()
    batch_load_cards(conn, enriched)

    for card in enriched:
        create_mechanic_relationships(conn, card)
        create_role_relationships(conn, card)

    # Analyze commander
    engine = SynergyInferenceEngine()
    engine.analyze_commander(conn, "Muldrotha, the Gravetide")

    # Query synergistic cards
    synergistic = DeckbuildingQueries.find_synergistic_cards(
        conn,
        commander_name="Muldrotha, the Gravetide",
        max_cmc=4,
        min_strength=0.7,
        limit=10
    )

    # Should find Eternal Witness (has recursion/ETB synergy with Muldrotha)
    card_names = [c["name"] for c in synergistic]
    assert "Eternal Witness" in card_names
