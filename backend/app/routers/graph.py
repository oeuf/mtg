"""Graph metadata API router."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from neo4j import Session

from app.dependencies import get_neo4j_session

router = APIRouter()


@router.get("/graph/stats")
def get_graph_stats(session: Session = Depends(get_neo4j_session)):
    """Get graph statistics."""
    result = session.run(
        """
        OPTIONAL MATCH (card:Card)
        WITH count(card) AS cards
        OPTIONAL MATCH (cmd:Commander)
        WITH cards, count(cmd) AS commanders
        OPTIONAL MATCH (m:Mechanic)
        WITH cards, commanders, count(m) AS mechanics
        OPTIONAL MATCH ()-[r]->()
        RETURN cards, commanders, mechanics, count(r) AS relationships
        """
    )
    record = result.single()
    if record:
        return {
            "total_cards": record["cards"],
            "total_commanders": record["commanders"],
            "total_mechanics": record["mechanics"],
            "total_relationships": record["relationships"],
            "last_updated": None,
        }
    return {
        "total_cards": 0,
        "total_commanders": 0,
        "total_mechanics": 0,
        "total_relationships": 0,
        "last_updated": None,
    }


@router.get("/mechanics")
def get_mechanics(session: Session = Depends(get_neo4j_session)):
    """Get all mechanics."""
    result = session.run(
        """
        MATCH (m:Mechanic)
        OPTIONAL MATCH (c:Card)-[:HAS_MECHANIC]->(m)
        RETURN m.name AS name, m.description AS description, count(c) AS card_count
        ORDER BY card_count DESC
        """
    )
    records = result.data()
    return {
        "total": len(records),
        "mechanics": records,
    }


@router.get("/themes")
def get_themes(session: Session = Depends(get_neo4j_session)):
    """Get all themes."""
    result = session.run(
        """
        MATCH (t:Theme)
        OPTIONAL MATCH (c:Card)-[:SUPPORTS_THEME]->(t)
        RETURN t.name AS name, t.description AS description, count(c) AS card_count
        ORDER BY card_count DESC
        """
    )
    records = result.data()
    return {
        "total": len(records),
        "themes": records,
    }


@router.get("/roles")
def get_roles(session: Session = Depends(get_neo4j_session)):
    """Get all functional roles."""
    result = session.run(
        """
        MATCH (r:Functional_Role)
        OPTIONAL MATCH (c:Card)-[:FILLS_ROLE]->(r)
        RETURN r.name AS name, r.description AS description, count(c) AS card_count
        ORDER BY card_count DESC
        """
    )
    records = result.data()
    return {
        "total": len(records),
        "roles": records,
    }


@router.get("/graph/health")
def get_graph_health(session: Session = Depends(get_neo4j_session)):
    """Check Neo4j connection health."""
    try:
        session.run("RETURN 1")
        return {"status": "healthy", "message": "Connected to Neo4j"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "message": str(e)},
        )
