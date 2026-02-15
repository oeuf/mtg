"""Commander API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from neo4j import Session

from app.dependencies import get_neo4j_session

router = APIRouter()


@router.get("/commanders")
def get_commanders(
    search: Optional[str] = Query(None, description="Search by name"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_neo4j_session),
):
    """List commanders with optional search."""
    conditions = []
    params: dict = {}

    if search:
        conditions.append("toLower(c.name) CONTAINS toLower($search)")
        params["search"] = search

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    offset = (page - 1) * limit
    params["offset"] = offset
    params["limit"] = limit

    count_query = f"MATCH (c:Commander) {where_clause} RETURN count(c) AS total"
    count_params = {k: v for k, v in params.items() if k not in ("offset", "limit")}
    count_result = session.run(count_query, count_params)
    count_record = count_result.single()
    total = count_record["total"] if count_record else 0

    query = f"""
        MATCH (c:Commander) {where_clause}
        RETURN c.name AS name, c.mana_cost AS mana_cost, c.cmc AS cmc,
               c.type_line AS type_line, c.oracle_text AS oracle_text,
               c.color_identity AS color_identity, c.colors AS colors,
               c.power AS power, c.toughness AS toughness,
               c.edhrec_rank AS edhrec_rank, c.keywords AS keywords,
               c.is_legendary AS is_legendary,
               c.functional_categories AS functional_categories,
               c.mechanics AS mechanics, c.themes AS themes,
               c.archetype AS archetype, c.popularity_score AS popularity_score
        ORDER BY c.edhrec_rank ASC
        SKIP $offset LIMIT $limit
    """
    result = session.run(query, params)
    items = result.data()

    return {"items": items, "total": total}


@router.get("/commanders/{name}")
def get_commander_by_name(
    name: str,
    session: Session = Depends(get_neo4j_session),
):
    """Get a single commander by name."""
    result = session.run(
        "MATCH (c:Commander {name: $name}) "
        "RETURN c.name AS name, c.mana_cost AS mana_cost, c.cmc AS cmc, "
        "c.type_line AS type_line, c.oracle_text AS oracle_text, "
        "c.color_identity AS color_identity, c.colors AS colors, "
        "c.power AS power, c.toughness AS toughness, "
        "c.edhrec_rank AS edhrec_rank",
        name=name,
    )
    record = result.single()
    if record is None:
        raise HTTPException(status_code=404, detail=f"Commander '{name}' not found")
    return record.data()


@router.get("/commanders/{name}/synergies")
def get_commander_synergies(
    name: str,
    limit: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_neo4j_session),
):
    """Get synergistic cards for a commander."""
    exists = session.run(
        "MATCH (c:Commander {name: $name}) RETURN c", name=name
    )
    if exists.single() is None:
        raise HTTPException(status_code=404, detail=f"Commander '{name}' not found")

    result = session.run(
        "MATCH (cmd:Commander {name: $name})-[s:SYNERGIZES_WITH]-(card:Card) "
        "WHERE NOT card:Commander "
        "RETURN card.name AS card_name, s.synergy_score AS synergy_score "
        "ORDER BY s.synergy_score DESC "
        "LIMIT $limit",
        name=name,
        limit=limit,
    )
    synergies = result.data()
    return {"commander": name, "synergies": synergies}


@router.get("/commanders/{name}/recommendations")
def get_commander_recommendations(
    name: str,
    limit: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_neo4j_session),
):
    """Get card recommendations for a commander deck."""
    exists = session.run(
        "MATCH (c:Commander {name: $name}) RETURN c", name=name
    )
    if exists.single() is None:
        raise HTTPException(status_code=404, detail=f"Commander '{name}' not found")

    result = session.run(
        "MATCH (cmd:Commander {name: $name})-[s:EMBEDDING_SIMILAR]->(card:Card) "
        "WHERE NOT card:Commander "
        "RETURN card.name AS card_name, s.score AS score "
        "ORDER BY s.score DESC "
        "LIMIT $limit",
        name=name,
        limit=limit,
    )
    recommendations = result.data()
    return {"commander": name, "recommendations": recommendations}
