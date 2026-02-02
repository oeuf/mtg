#!/usr/bin/env python3
"""Validate recommendation quality against reference deck."""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.graph.connection import Neo4jConnection
from src.validation.reference_deck import load_reference_deck
from src.validation.recommendations import get_embedding_recommendations, get_similarity_recommendations
from src.validation.metrics import precision_at_k, recall_at_k, mean_reciprocal_rank


def main():
    """Run validation."""
    # Load reference deck
    deck_path = "reference_decks/muldrotha.txt"

    if not os.path.exists(deck_path):
        print(f"Error: Reference deck not found at {deck_path}")
        return 1

    print(f"Loading reference deck: {deck_path}")
    reference_cards = load_reference_deck(deck_path)

    # Exclude commander from reference
    commander = "Muldrotha, the Gravetide"
    reference_cards = [c for c in reference_cards if c != commander]

    print(f"Reference deck: {len(reference_cards)} cards (excluding commander)\n")

    # Connect to Neo4j
    password = os.getenv('NEO4J_PASSWORD', 'mtg-commander')
    conn = Neo4jConnection('bolt://localhost:7687', 'neo4j', password)

    try:
        # Test both recommendation methods
        methods = [
            ("EMBEDDING_SIMILAR (topK=100)", lambda: get_embedding_recommendations(conn, commander, top_k=50)),
            ("SIMILAR_TO (node similarity)", lambda: get_similarity_recommendations(conn, commander, top_k=50))
        ]

        for method_name, get_recs in methods:
            print(f"=== {method_name} ===")

            recommendations = get_recs()
            rec_names = [r["name"] for r in recommendations]

            print(f"Got {len(recommendations)} recommendations\n")

            # Calculate metrics at different K values
            for k in [10, 20, 50]:
                p = precision_at_k(rec_names, reference_cards, k)
                r = recall_at_k(rec_names, reference_cards, k)

                print(f"K={k}:")
                print(f"  Precision@{k}: {p:.3f}")
                print(f"  Recall@{k}: {r:.3f}")

            mrr = mean_reciprocal_rank(rec_names, reference_cards)
            print(f"\nMean Reciprocal Rank: {mrr:.3f}")

            # Show top matches
            print("\nTop 5 recommendations:")
            for i, rec in enumerate(recommendations[:5], 1):
                in_deck = "✓" if rec["name"] in reference_cards else " "
                print(f"  {i}. [{in_deck}] {rec['name']} (score: {rec['score']:.3f})")

            print("\n" + "="*60 + "\n")

    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
