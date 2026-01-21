"""FastAPI dependencies for dependency injection."""

import os
from typing import Optional
from src.graph.connection import Neo4jConnection


_connection: Optional[Neo4jConnection] = None


def get_neo4j_connection() -> Neo4jConnection:
    """Get Neo4j connection. Raises error if not configured."""
    global _connection

    if _connection is not None:
        return _connection

    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD")

    if not password:
        raise RuntimeError(
            "NEO4J_PASSWORD environment variable not set. "
            "Please configure Neo4j and run 'python main.py' to load card data."
        )

    _connection = Neo4jConnection(uri, user, password)
    return _connection


def get_db() -> Neo4jConnection:
    """Dependency for Neo4j connection."""
    return get_neo4j_connection()
