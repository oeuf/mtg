#!/usr/bin/env python3
"""Re-run embedding pipeline: backfill features → clear old → embed → kNN.

Run from project root with the data-pipeline venv:
    source venv/bin/activate
    python -u run_reembed.py
"""

import os
from src.graph.connection import Neo4jConnection
from src.graph.backfill_card_features import backfill_card_features
from src.graph.gds_scoring import GDSScoring


def main():
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "password")
    conn = Neo4jConnection(
        uri="bolt://localhost:7687",
        user="neo4j",
        password=neo4j_password
    )

    gds = GDSScoring(conn)

    # Step 1: Backfill numeric features on existing Card nodes
    print("\nSTEP 1: Backfill numeric feature properties")
    print("-" * 60)
    backfill_card_features(conn)

    # Step 2: Delete stale EMBEDDING_SIMILAR relationships
    print("\nSTEP 2: Clear stale EMBEDDING_SIMILAR relationships")
    print("-" * 60)
    gds.clear_embedding_similar()

    # Step 3: Create card-feature projection (includes all node types + relationships)
    print("\nSTEP 3: Create card-feature graph projection")
    print("-" * 60)
    gds.create_card_feature_projection()

    # Step 4: Compute FastRP embeddings with featureProperties
    print("\nSTEP 4: Compute FastRP embeddings (with numeric features)")
    print("-" * 60)
    gds.compute_fastrp_embeddings("card-feature-graph", embedding_dim=128)

    # Step 5: kNN similarity at topK=10 (quality over quantity)
    print("\nSTEP 5: Compute kNN similarity (topK=10)")
    print("-" * 60)
    gds.compute_knn_similarity(topK=10)

    # Spot-check results
    print("\n" + "=" * 60)
    print("SPOT CHECK")
    print("=" * 60)

    for card_name in ["Mox Diamond", "Sol Ring"]:
        print(f"\nTop similar cards to '{card_name}':")
        results = conn.execute_query("""
            MATCH (c:Card {name: $name})-[r:EMBEDDING_SIMILAR]->(o:Card)
            RETURN o.name AS name, r.score AS score, o.cmc AS cmc,
                   o.is_fast_mana AS fast_mana, o.is_artifact AS artifact
            ORDER BY r.score DESC LIMIT 10
        """, {"name": card_name})
        if results:
            for row in results:
                print(f"  {row['score']:.4f}  {row['name']}  (cmc={row['cmc']}, "
                      f"fast_mana={row['fast_mana']}, artifact={row['artifact']})")
        else:
            print(f"  (No EMBEDDING_SIMILAR found for '{card_name}')")

    print("\n" + "=" * 60)
    print("REEMBED COMPLETE")
    print("=" * 60)

    conn.close()


if __name__ == "__main__":
    main()
