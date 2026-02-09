#!/usr/bin/env python3
"""Test queries for MTG Knowledge Graph."""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.graph.connection import Neo4jConnection


QUERIES = {
    "commander_synergy": """
        MATCH (cmd:Commander {name: $commander})-[:SYNERGIZES_WITH_MECHANIC]->(m:Mechanic)
        MATCH (card:Card)-[:HAS_MECHANIC]->(m)
        WHERE card.cmc <= $max_cmc
        RETURN card.name, collect(m.name) as shared_mechanics
        ORDER BY size(shared_mechanics) DESC
        LIMIT 20
    """,

    "graveyard_cards": """
        MATCH (card:Card)-[:INTERACTS_WITH_ZONE]->(z:Zone {name: "graveyard"})
        WHERE ALL(c IN card.color_identity WHERE c IN $colors)
        RETURN card.name, card.oracle_text
        LIMIT 20
    """,

    "upkeep_triggers": """
        MATCH (card:Card)-[:TRIGGERS_IN_PHASE]->(p:Phase {name: "upkeep"})
        WHERE ALL(c IN card.color_identity WHERE c IN $colors)
        RETURN card.name, card.oracle_text
        LIMIT 20
    """,

    "keyword_search": """
        MATCH (card:Card)
        WHERE $keyword IN card.keywords
        AND ALL(c IN card.color_identity WHERE c IN $colors)
        RETURN card.name, card.mana_cost
        LIMIT 20
    """,

    "zone_interactions": """
        MATCH (z:Zone)<-[r:INTERACTS_WITH_ZONE]-(c:Card)
        RETURN z.name as zone,
               count(c) as card_count,
               r.interaction_type as interaction_type
        ORDER BY card_count DESC
    """,

    "phase_triggers": """
        MATCH (p:Phase)<-[r:TRIGGERS_IN_PHASE]-(c:Card)
        RETURN p.name as phase,
               p.order as phase_order,
               count(c) as card_count,
               r.trigger_type as trigger_type
        ORDER BY phase_order
    """
}


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Test MTG Knowledge Graph queries')
    parser.add_argument('--query', required=True, choices=QUERIES.keys(),
                       help='Query to run')
    parser.add_argument('--commander', help='Commander name (for commander_synergy)')
    parser.add_argument('--max-cmc', type=int, default=7,
                       help='Maximum CMC (for commander_synergy)')
    parser.add_argument('--colors', nargs='+', default=[],
                       help='Color identity (e.g., B G U)')
    parser.add_argument('--keyword', help='Keyword to search for')
    return parser.parse_args()


def run_query(conn: Neo4jConnection, query_name: str, params: dict):
    """Run a query and display results."""
    query = QUERIES[query_name]

    print(f"\n=== Running query: {query_name} ===\n")
    print(f"Parameters: {params}\n")

    try:
        results = conn.execute_query(query, params)

        if not results:
            print("No results found.")
            return

        print(f"Found {len(results)} results:\n")

        for i, record in enumerate(results[:20], 1):
            print(f"{i}. {dict(record)}")

        if len(results) > 20:
            print(f"\n... and {len(results) - 20} more results")

    except Exception as e:
        print(f"Error running query: {e}")
        raise


def main():
    """Main entry point."""
    args = parse_args()

    # Build parameters based on query type
    params = {}

    if args.query == "commander_synergy":
        if not args.commander:
            print("Error: --commander required for commander_synergy query")
            sys.exit(1)
        params = {
            "commander": args.commander,
            "max_cmc": args.max_cmc
        }

    elif args.query in ["graveyard_cards", "upkeep_triggers", "keyword_search"]:
        params["colors"] = args.colors

    if args.query == "keyword_search":
        if not args.keyword:
            print("Error: --keyword required for keyword_search query")
            sys.exit(1)
        params["keyword"] = args.keyword

    # Connect and run query
    conn = Neo4jConnection()

    try:
        run_query(conn, args.query, params)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
