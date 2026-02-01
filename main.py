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
from src.parsing.rules_parser import RulesParser
from src.graph.connection import Neo4jConnection
from src.graph.loaders import (
    batch_load_cards,
    create_mechanic_relationships,
    create_role_relationships,
    integrate_related_cards,
    create_zone_nodes,
    create_phase_nodes,
    create_zone_relationships,
    create_phase_relationships,
    create_theme_nodes,
    batch_create_theme_relationships,
    batch_create_subtype_relationships,
    THEME_DEFINITIONS
)
from src.synergy.inference_engine import SynergyInferenceEngine
from src.synergy.queries import DeckbuildingQueries
from src.graph.popularity import PopularityScorer
from src.graph.gds_scoring import GDSScoring
from src.synergy.card_synergies import CardSynergyEngine


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

    # Phase 2: Parse comprehensive rules
    print("\nPHASE 2: Parsing Comprehensive Rules")
    print("-" * 60)

    rules_parser = RulesParser("2025-11-14-rules.md")
    rules_data = rules_parser.parse_all()

    # Phase 3: Parse card data
    print("\nPHASE 3: Data Parsing")
    print("-" * 60)

    print("Parsing AtomicCards...")
    parser = AtomicCardsParser()
    cards = parser.parse(files["atomic_cards"])

    print("\nParsing RelatedCards...")
    related_parser = RelatedCardsParser()
    related_cards = related_parser.parse(files["related_cards"])

    # Phase 4: Enrich data
    print("\nPHASE 4: Property Extraction")
    print("-" * 60)

    enriched_cards = enrich_card_data(cards)

    # Phase 5: Connect to Neo4j
    print("\nPHASE 5: Database Connection")
    print("-" * 60)

    # Get Neo4j password from environment or use default
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "password")

    conn = Neo4jConnection(
        uri="bolt://localhost:7687",
        user="neo4j",
        password=neo4j_password
    )
    conn.create_constraints()

    # Phase 6: Create Zone and Phase nodes
    print("\nPHASE 6: Creating Zone and Phase Nodes")
    print("-" * 60)

    create_zone_nodes(conn, rules_data["zones"])
    create_phase_nodes(conn, rules_data["phases"])

    # Phase 7: Create Theme nodes
    print("\nPHASE 7: Creating Theme Nodes")
    print("-" * 60)

    create_theme_nodes(conn, THEME_DEFINITIONS)

    # Phase 8: Load cards
    print("\nPHASE 8: Loading Cards")
    print("-" * 60)

    batch_load_cards(conn, enriched_cards)

    # Phase 9: Create basic relationships
    print("\nPHASE 9: Creating Relationships")
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

    print("\nCreating zone/phase relationships...")
    for i, card in enumerate(enriched_cards):
        create_zone_relationships(conn, card)
        create_phase_relationships(conn, card)
        if (i + 1) % 1000 == 0:
            print(f"  Processed {i + 1}/{len(enriched_cards)}...")

    print("\nCreating theme relationships...")
    batch_create_theme_relationships(conn, enriched_cards)

    print("\nCreating subtype relationships...")
    batch_create_subtype_relationships(conn, enriched_cards)

    print("\nCreating card-to-card synergy relationships...")
    card_synergy_engine = CardSynergyEngine()
    card_synergy_engine.create_synergy_relationships(conn, min_shared_mechanics=2, min_synergy_score=0.6)

    # Phase 9.5: Enhanced Multi-Dimensional Synergy Scoring
    print("\nPHASE 9.5: Enhanced Synergy Scoring (ML-powered)")
    print("-" * 60)

    synergy_engine = CardSynergyEngine()
    synergy_engine.create_enhanced_synergy_relationships(
        conn,
        min_synergy_score=0.5,
        batch_size=1000
    )

    # Phase 10: Integrate RelatedCards
    print("\nPHASE 10: Integrating RelatedCards")
    print("-" * 60)

    integrate_related_cards(conn, related_cards)

    # Phase 11: Infer commander synergies
    print("\nPHASE 11: Commander Synergy Analysis")
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

    # Phase 12: Calculate Popularity Scores
    print("\nPHASE 12: Calculating Popularity Scores")
    print("-" * 60)

    popularity_scorer = PopularityScorer()
    popularity_scorer.update_all_cards(conn)

    # Phase 13: GDS Similarity Analysis
    print("\nPHASE 13: Graph Data Science - Node Similarity")
    print("-" * 60)

    gds = GDSScoring(conn)
    gds.create_projection()
    gds.compute_similarity(topK=10, similarity_cutoff=0.5)

    # Phase 13.5: GDS Advanced Topological Features
    print("\nPHASE 13.5: GDS Topological Link Prediction & Communities")
    print("-" * 60)

    # Create specialized projections
    print("\nCreating Card-Feature projection...")
    gds.create_card_feature_projection()

    print("\nCreating Card-Synergy projection...")
    gds.create_card_synergy_projection()

    # Compute embeddings and similarity
    print("\nComputing FastRP embeddings...")
    gds.compute_fastrp_embeddings("card-feature-graph", embedding_dim=128)

    print("\nComputing kNN similarity...")
    gds.compute_knn_similarity(topK=100)

    # Link prediction (only if synergy relationships exist)
    print("\nRunning link prediction algorithms...")
    try:
        gds.compute_adamic_adar("card-synergy-graph")
        gds.compute_common_neighbors("card-synergy-graph")
    except Exception as e:
        print(f"  Skipping link prediction (need synergy relationships): {e}")

    # Community detection
    print("\nDetecting communities...")
    try:
        gds.compute_leiden_communities("card-synergy-graph")
        gds.boost_intra_community_synergy(boost_factor=1.2)
    except Exception as e:
        print(f"  Skipping community detection: {e}")

    # Phase 14: Example queries
    print("\nPHASE 14: Example Queries")
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

    print("\n4. Cards similar to Sol Ring:")
    similar = DeckbuildingQueries.find_similar_cards(conn, card_name="Sol Ring", min_similarity=0.6, limit=5)
    for card in similar:
        print(f"  • {card['name']} (similarity: {card['similarity_score']:.2f})")

    print("\n5. Cards that synergize with Eternal Witness:")
    witness_synergies = conn.execute_query("""
        MATCH (c1:Card {name: 'Eternal Witness'})-[s:SYNERGIZES_WITH]-(c2:Card)
        RETURN c2.name AS name, s.synergy_score AS score, s.shared_mechanics AS mechanics
        ORDER BY s.synergy_score DESC
        LIMIT 5
    """)
    for card in witness_synergies:
        print(f"  • {card['name']} (score: {card['score']:.2f}, mechanics: {card['mechanics']})")

    print("\n6. Enhanced multi-dimensional synergy for Necropotence:")
    necro_syn = conn.execute_query("""
        MATCH (c1:Card {name: 'Necropotence'})-[s:SYNERGIZES_WITH]-(c2:Card)
        WHERE s.source = 'ml_enhanced'
        RETURN c2.name AS name,
               s.synergy_score AS score
        ORDER BY s.synergy_score DESC
        LIMIT 5
    """)
    if necro_syn:
        for card in necro_syn:
            print(f"  • {card['name']} (ML score: {card['score']:.3f})")
    else:
        print("  (No enhanced synergies found - run Phase 9.5)")

    print("\n7. Embedding-based similar cards to Sol Ring:")
    embedding_sim = conn.execute_query("""
        MATCH (c1:Card {name: 'Sol Ring'})-[s:EMBEDDING_SIMILAR]->(c2:Card)
        RETURN c2.name AS name, s.score AS score
        ORDER BY s.score DESC
        LIMIT 5
    """)
    if embedding_sim:
        for card in embedding_sim:
            print(f"  • {card['name']} (embedding similarity: {card['score']:.3f})")
    else:
        print("  (No embedding similarities found - run Phase 13.5)")

    print("\n8. Community archetypes (top 3):")
    communities = conn.execute_query("""
        MATCH (c:Card)
        WHERE c.community IS NOT NULL
        RETURN c.community AS community, count(*) AS size, collect(c.name)[0..3] AS samples
        ORDER BY size DESC
        LIMIT 3
    """)
    if communities:
        for comm in communities:
            print(f"  • Community {comm['community']}: {comm['size']} cards")
            print(f"    Samples: {', '.join(comm['samples'])}")
    else:
        print("  (No communities detected - run Phase 13.5)")

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
