"""Remove duplicate Card/Commander nodes created by double-faced card names.

MTGJSON stores double-faced cards like "Sol Ring // Sol Ring" as separate dict
keys, producing duplicate Neo4j nodes.  This script:
  1. DETACH DELETEs nodes whose front-face name already exists as a separate node.
  2. Renames any remaining // nodes to their front-face name.
"""

import os

from src.graph.connection import Neo4jConnection


def remove_duplicate_slash_nodes(conn: Neo4jConnection) -> tuple[int, int]:
    """Delete true duplicates and rename remaining // nodes.

    Returns:
        (deleted_count, renamed_count)
    """
    # Step 1: Delete nodes where the front-face name already exists as a
    # separate node (true duplicates like "Sol Ring // Sol Ring" when
    # "Sol Ring" also exists).
    delete_result = conn.execute_query(
        """
        MATCH (dupe) WHERE dupe.name CONTAINS ' // '
        WITH dupe, split(dupe.name, ' // ')[0] AS front
        MATCH (canonical) WHERE canonical.name = front AND id(canonical) <> id(dupe)
        WITH collect(dupe) AS dupes, count(dupe) AS cnt
        FOREACH (d IN dupes | DETACH DELETE d)
        RETURN cnt AS deleted
        """
    )
    deleted = delete_result[0]["deleted"] if delete_result else 0
    print(f"  Deleted {deleted} duplicate // nodes")

    # Step 2: Rename any remaining // nodes to their front-face name.
    rename_result = conn.execute_query(
        """
        MATCH (c) WHERE c.name CONTAINS ' // '
        SET c.name = split(c.name, ' // ')[0]
        RETURN count(c) AS renamed
        """
    )
    renamed = rename_result[0]["renamed"] if rename_result else 0
    print(f"  Renamed {renamed} remaining // nodes to front-face name")

    return deleted, renamed


if __name__ == "__main__":
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "password")

    print("Connecting to Neo4j...")
    conn = Neo4jConnection(uri, user, password)
    try:
        print("Removing duplicate // card nodes...")
        deleted, renamed = remove_duplicate_slash_nodes(conn)
        print(f"Done — {deleted} deleted, {renamed} renamed.")
    finally:
        conn.close()
