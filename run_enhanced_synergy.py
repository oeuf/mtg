#!/usr/bin/env python3
"""Run only the enhanced synergy phases (9.5 and 13.5)."""

import os
from src.graph.connection import Neo4jConnection
from src.synergy.card_synergies import CardSynergyEngine
from src.graph.gds_scoring import GDSScoring


def main():
    # Get Neo4j password from environment or use default
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "mtg-commander")

    conn = Neo4jConnection(
        uri="bolt://localhost:7687",
        user="neo4j",
        password=neo4j_password
    )

    # Phase 9.5: Enhanced Multi-Dimensional Synergy Scoring
    print("\nPHASE 9.5: Enhanced Synergy Scoring (ML-powered)")
    print("-" * 60)

    synergy_engine = CardSynergyEngine()
    synergy_engine.create_enhanced_synergy_relationships(
        conn,
        min_synergy_score=0.5,
        batch_size=1000
    )

    # Phase 13.5: GDS Advanced Topological Features
    print("\nPHASE 13.5: GDS Topological Link Prediction & Communities")
    print("-" * 60)

    gds = GDSScoring(conn)

    # Create specialized projections
    print("\nCreating Card-Feature projection...")
    gds.create_card_feature_projection()

    print("\nCreating Card-Synergy projection...")
    gds.create_card_synergy_projection()

    # Compute embeddings and similarity
    print("\nComputing FastRP embeddings...")
    gds.compute_fastrp_embeddings("card-feature-graph", embedding_dim=128)

    print("\nComputing kNN similarity...")
    gds.compute_knn_similarity(topK=20)

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

    # Example queries
    print("\n" + "=" * 60)
    print("EXAMPLE QUERIES")
    print("=" * 60)

    print("\n1. Enhanced synergies for Necropotence:")
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
        print("  (No enhanced synergies found)")

    print("\n2. Embedding-based similar cards to Sol Ring:")
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
        print("  (No embedding similarities found)")

    print("\n3. Community archetypes (top 5):")
    communities = conn.execute_query("""
        MATCH (c:Card)
        WHERE c.community IS NOT NULL
        RETURN c.community AS community, count(*) AS size, collect(c.name)[0..3] AS samples
        ORDER BY size DESC
        LIMIT 5
    """)
    if communities:
        for comm in communities:
            print(f"  • Community {comm['community']}: {comm['size']} cards")
            print(f"    Samples: {', '.join(comm['samples'])}")
    else:
        print("  (No communities detected)")

    print("\n" + "=" * 60)
    print("ENHANCED SYNERGY PHASES COMPLETE")
    print("=" * 60)

    conn.close()


if __name__ == "__main__":
    main()
