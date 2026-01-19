#!/usr/bin/env python3
"""
Example queries for the Commander Knowledge Graph.

This script demonstrates how to use the graph database
to find synergistic cards, combos, and build deck shells.
"""

import os
from src.graph.connection import Neo4jConnection
from src.synergy.queries import DeckbuildingQueries


def main():
    """Run example queries."""

    # Connect to Neo4j
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "password")
    conn = Neo4jConnection(
        uri="bolt://localhost:7687",
        user="neo4j",
        password=neo4j_password
    )

    print("=" * 60)
    print("Commander Knowledge Graph - Query Examples")
    print("=" * 60)
    print()

    # Example 1: Find synergistic cards for a commander
    print("1. Finding cards that synergize with Muldrotha")
    print("-" * 60)
    cards = DeckbuildingQueries.find_synergistic_cards(
        conn,
        commander_name="Muldrotha, the Gravetide",
        max_cmc=4,
        min_strength=0.7,
        limit=10
    )

    if cards:
        for i, card in enumerate(cards, 1):
            print(f"{i:2d}. {card['name']:<30} ({card['cmc']}) - {card['shared_mechanic']}")
    else:
        print("No results found. Make sure the database has been populated.")
    print()

    # Example 2: Find known combos
    print("2. Finding known combos with Dramatic Reversal")
    print("-" * 60)
    combos = DeckbuildingQueries.find_known_combos(
        conn,
        card_name="Dramatic Reversal"
    )

    if combos:
        for combo in combos:
            print(f"  → {combo['combo_piece']} (CMC: {combo['cmc']})")
    else:
        print("  No combos found")
    print()

    # Example 3: Find token generators
    print("3. Finding Goblin token generators in Jund colors")
    print("-" * 60)
    goblins = DeckbuildingQueries.find_token_generators(
        conn,
        token_type="Goblin",
        color_identity=["B", "R", "G"],
        max_cmc=5
    )

    if goblins:
        for card in goblins[:5]:
            print(f"  • {card['name']:<30} (CMC: {card['cmc']})")
    else:
        print("  No results found")
    print()

    # Example 4: Find cards by role
    print("4. Finding efficient ramp cards in Sultai colors")
    print("-" * 60)
    ramp = DeckbuildingQueries.find_cards_by_role(
        conn,
        role="ramp",
        color_identity=["U", "B", "G"],
        max_cmc=3,
        min_efficiency=0.6
    )

    if ramp:
        for card in ramp[:10]:
            print(f"  • {card['name']:<30} (CMC: {card['cmc']}, Eff: {card['efficiency']:.2f})")
    else:
        print("  No results found")
    print()

    # Example 5: Build a deck shell
    print("5. Building deck shell for Muldrotha")
    print("-" * 60)
    shell = DeckbuildingQueries.build_deck_shell(
        conn,
        commander_name="Muldrotha, the Gravetide"
    )

    if "error" not in shell:
        print(f"Commander: {shell['commander']}")
        print(f"Colors: {', '.join(shell['color_identity'])}")
        print()
        for role, cards in shell["cards_by_role"].items():
            print(f"{role.upper()} ({len(cards)} cards):")
            for card in cards[:3]:
                print(f"  • {card['name']}")
            if len(cards) > 3:
                print(f"  ... and {len(cards) - 3} more")
            print()
    else:
        print(f"Error: {shell['error']}")

    conn.close()
    print("=" * 60)
    print("Query examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
