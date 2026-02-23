"""Backfill numeric feature properties on existing Card nodes for FastRP."""

import os
from src.graph.connection import Neo4jConnection


def backfill_card_features(conn: Neo4jConnection) -> int:
    """Compute and SET numeric feature properties on all Card (and Commander) nodes."""
    print("Backfilling numeric feature properties on Card nodes...")

    query = """
    MATCH (c:Card)
    SET c.cmc_normalized        = CASE WHEN c.cmc IS NULL THEN 0.0
                                       ELSE toFloat(CASE WHEN c.cmc > 16 THEN 16 ELSE c.cmc END) / 16.0
                                  END,
        c.is_colorless          = CASE WHEN c.color_identity IS NULL OR size(c.color_identity) = 0
                                       THEN 1 ELSE 0 END,
        c.color_count           = CASE WHEN c.color_identity IS NULL THEN 0
                                       ELSE size(c.color_identity) END,
        c.is_creature           = CASE WHEN c.type_line IS NOT NULL AND c.type_line CONTAINS 'Creature'
                                       THEN 1 ELSE 0 END,
        c.is_instant_sorcery    = CASE WHEN c.type_line IS NOT NULL AND
                                            (c.type_line CONTAINS 'Instant' OR c.type_line CONTAINS 'Sorcery')
                                       THEN 1 ELSE 0 END,
        c.is_artifact           = CASE WHEN c.type_line IS NOT NULL AND c.type_line CONTAINS 'Artifact'
                                       THEN 1 ELSE 0 END,
        c.is_land               = CASE WHEN c.type_line IS NOT NULL AND c.type_line CONTAINS 'Land'
                                       THEN 1 ELSE 0 END,
        c.is_fast_mana_int      = CASE WHEN c.is_fast_mana = true THEN 1 ELSE 0 END
    RETURN count(c) AS updated
    """

    result = conn.execute_query(query)
    updated = result[0]["updated"] if result else 0
    print(f"✓ Backfilled {updated} Card nodes with numeric features")
    return updated


def main():
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "password")
    conn = Neo4jConnection(
        uri="bolt://localhost:7687",
        user="neo4j",
        password=neo4j_password
    )

    try:
        updated = backfill_card_features(conn)
        print(f"\nDone. {updated} cards updated.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
