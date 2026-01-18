#!/usr/bin/env python3
"""
Commander Knowledge Graph - Complete Pipeline
MTGJSON version with RelatedCards integration
"""

import os
from src.data.mtgjson_downloader import MTGJSONDownloader
from src.data.atomic_cards_parser import AtomicCardsParser
from src.data.related_cards_parser import RelatedCardsParser
from src.parsing.enrichment import enrich_card_data
from src.graph.connection import Neo4jConnection
from src.graph.loaders import (
    batch_load_cards,
    create_mechanic_relationships,
    create_role_relationships,
    integrate_related_cards
)
from src.synergy.inference_engine import SynergyInferenceEngine
from src.synergy.queries import DeckbuildingQueries


def main():
    """Execute complete pipeline."""

    print("=" * 60)
    print("Commander Deckbuilding Knowledge Graph")
    print("MTGJSON v5 | RelatedCards Integration")
    print("=" * 60)
    print()

    # Phase 1: Download MTGJSON data
    print("PHASE 1: Data Acquisition")
    print("-" * 60)

    downloader = MTGJSONDownloader()
    files = downloader.download_all()

    # Phase 2: Parse card data
    print("\nPHASE 2: Data Parsing")
    print("-" * 60)

    print("Parsing AtomicCards...")
    parser = AtomicCardsParser()
    cards = parser.parse(files["atomic_cards"])

    print("\nParsing RelatedCards...")
    related_parser = RelatedCardsParser()
    related_cards = related_parser.parse(files["related_cards"])

    # Phase 3: Enrich data
    print("\nPHASE 3: Property Extraction")
    print("-" * 60)

    enriched_cards = enrich_card_data(cards)

    # Phase 4: Connect to Neo4j
    print("\nPHASE 4: Database Connection")
    print("-" * 60)

    # Get Neo4j password from environment or use default
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "password")

    conn = Neo4jConnection(
        uri="bolt://localhost:7687",
        user="neo4j",
        password=neo4j_password
    )
    conn.create_constraints()

    # Phase 5: Load cards
    print("\nPHASE 5: Loading Cards")
    print("-" * 60)

    batch_load_cards(conn, enriched_cards)

    # Phase 6: Create basic relationships
    print("\nPHASE 6: Creating Relationships")
    print("-" * 60)

    print("Creating mechanic relationships...")
    for i, card in enumerate(enriched_cards):
        create_mechanic_relationships(conn, card)
        if (i + 1) % 1000 == 0:
            print(f"  Processed {i + 1}/{len(enriched_cards)}...")

    print("\nCreating role relationships...")
    for i, card in enumerate(enriched_cards):
        create_role_relationships(conn, card)
        if (i + 1) % 1000 == 0:
            print(f"  Processed {i + 1}/{len(enriched_cards)}...")

    # Phase 7: Integrate RelatedCards
    print("\nPHASE 7: Integrating RelatedCards")
    print("-" * 60)

    integrate_related_cards(conn, related_cards)

    # Phase 8: Infer commander synergies
    print("\nPHASE 8: Commander Synergy Analysis")
    print("-" * 60)

    popular_commanders = [
        "Muldrotha, the Gravetide",
        "Korvold, Fae-Cursed King",
        "Chulane, Teller of Tales",
        "The Gitrog Monster",
        "Kinnan, Bonder Prodigy",
        "Yuriko, the Tiger's Shadow",
        "Tymna the Weaver",
        "Thrasios, Triton Hero"
    ]

    engine = SynergyInferenceEngine()
    for commander in popular_commanders:
        engine.analyze_commander(conn, commander)

    # Phase 9: Example queries
    print("\nPHASE 9: Example Queries")
    print("-" * 60)

    print("\n1. Cards that synergize with Muldrotha:")
    muldrotha_cards = DeckbuildingQueries.find_synergistic_cards(
        conn,
        commander_name="Muldrotha, the Gravetide",
        max_cmc=4,
        min_strength=0.7,
        limit=10
    )

    for i, card in enumerate(muldrotha_cards, 1):
        print(f"  {i}. {card['name']} ({card['mana_cost']}) - {card['shared_mechanic']}")

    print("\n2. Known combos with Dramatic Reversal:")
    combos = DeckbuildingQueries.find_known_combos(
        conn,
        card_name="Dramatic Reversal"
    )

    for combo in combos:
        print(f"  → {combo['combo_piece']} ({combo['cost']})")

    print("\n3. Goblin token generators in Jund:")
    goblin_gens = DeckbuildingQueries.find_token_generators(
        conn,
        token_type="Goblin",
        color_identity=["B", "R", "G"],
        max_cmc=4
    )

    for card in goblin_gens[:5]:
        print(f"  • {card['name']} ({card['cost']})")

    # Summary
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"✓ Loaded {len(enriched_cards)} cards")
    print(f"✓ Integrated {len(related_cards)} card relationships")
    print(f"✓ Analyzed {len(popular_commanders)} commanders")
    print()
    print("Database ready for queries!")
    print("Connection: bolt://localhost:7687")
    print()

    conn.close()


if __name__ == "__main__":
    main()
