#!/usr/bin/env python3
"""CLI for validating deck recommendations against reference."""

import argparse
import os
import sys

from src.graph.connection import Neo4jConnection
from src.validation.reference_deck import load_reference_deck
from src.validation.validator import DeckValidator


def main():
    parser = argparse.ArgumentParser(
        description="Validate recommendations against a reference deck"
    )
    parser.add_argument(
        "--commander",
        type=str,
        default="Muldrotha, the Gravetide",
        help="Commander name"
    )
    parser.add_argument(
        "--reference",
        type=str,
        default="Muldrotha/DECKLIST.md",
        help="Path to reference decklist"
    )
    parser.add_argument(
        "--neo4j-uri",
        type=str,
        default="bolt://localhost:7687",
        help="Neo4j connection URI"
    )
    parser.add_argument(
        "--neo4j-user",
        type=str,
        default="neo4j",
        help="Neo4j username"
    )

    args = parser.parse_args()

    # Get password from environment
    password = os.environ.get("NEO4J_PASSWORD")
    if not password:
        print("Error: NEO4J_PASSWORD environment variable not set")
        sys.exit(1)

    # Load reference deck
    print(f"Loading reference deck: {args.reference}")
    try:
        reference_cards = load_reference_deck(
            args.reference,
            exclude_commander=True,
            commander_name=args.commander
        )
        print(f"Loaded {len(reference_cards)} cards (excluding commander)")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Connect to Neo4j
    print(f"\nConnecting to Neo4j: {args.neo4j_uri}")
    conn = Neo4jConnection(args.neo4j_uri, args.neo4j_user, password)

    try:
        # Run validation
        validator = DeckValidator(conn)
        result = validator.validate(
            reference_cards=reference_cards,
            commander_name=args.commander
        )

        # Print report
        validator.print_report(result)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
