"""Query Neo4j for card recommendations."""

from typing import Dict, List
from src.graph.connection import Neo4jConnection


def get_embedding_recommendations(
    conn: Neo4jConnection,
    commander_name: str,
    top_k: int = 20
) -> List[Dict]:
    """Get top-K recommendations using EMBEDDING_SIMILAR relationships.

    Traverses from Commander through shared mechanics to Cards with high
    embedding similarity.

    Args:
        conn: Neo4j connection
        commander_name: Name of commander card
        top_k: Number of recommendations to return

    Returns:
        List of dicts with 'name' and 'score' keys
    """
    query = """
    MATCH (cmd:Commander {name: $commander_name})-[:SYNERGIZES_WITH_MECHANIC]->(m:Mechanic)
    MATCH (m)<-[:HAS_MECHANIC]-(seed:Card)-[sim:EMBEDDING_SIMILAR]-(card:Card)
    WHERE NOT card:Commander
    RETURN DISTINCT card.name AS name, MAX(sim.score) AS score
    ORDER BY score DESC
    LIMIT $top_k
    """

    result = conn.execute_query(query, {
        "commander_name": commander_name,
        "top_k": top_k
    })

    return result


def get_similarity_recommendations(
    conn: Neo4jConnection,
    commander_name: str,
    top_k: int = 20
) -> List[Dict]:
    """Get top-K recommendations using SIMILAR_TO relationships.

    Traverses from Commander through SIMILAR_TO commanders to their
    synergistic mechanics and recommended cards.

    Args:
        conn: Neo4j connection
        commander_name: Name of commander card
        top_k: Number of recommendations to return

    Returns:
        List of dicts with 'name' and 'score' keys
    """
    query = """
    MATCH (cmd:Commander {name: $commander_name})-[sim:SIMILAR_TO]-(similar:Commander)
    MATCH (similar)-[:SYNERGIZES_WITH_MECHANIC]->(m:Mechanic)<-[:HAS_MECHANIC]-(card:Card)
    WHERE NOT card:Commander
    RETURN DISTINCT card.name AS name, AVG(sim.score) AS score
    ORDER BY score DESC
    LIMIT $top_k
    """

    result = conn.execute_query(query, {
        "commander_name": commander_name,
        "top_k": top_k
    })

    return result
