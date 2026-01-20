"""FastAPI dependencies for dependency injection."""

import os
from functools import lru_cache
from src.graph.connection import Neo4jConnection


@lru_cache()
def get_neo4j_connection() -> Neo4jConnection:
    """Get cached Neo4j connection."""
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD")

    if not password:
        raise ValueError("NEO4J_PASSWORD environment variable not set")

    return Neo4jConnection(uri, user, password)


def get_db():
    """Dependency for Neo4j connection."""
    return get_neo4j_connection()
