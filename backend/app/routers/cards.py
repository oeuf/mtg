"""Cards API router."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from neo4j import Session

from app.dependencies import get_neo4j_session

router = APIRouter()


@router.get("/cards")
def search_cards(
    colors: Optional[str] = Query(None, description="Comma-separated color identity (e.g. U,B)"),
    cmc_min: Optional[int] = Query(None, ge=0, description="Minimum CMC"),
    cmc_max: Optional[int] = Query(None, ge=0, description="Maximum CMC"),
    types: Optional[str] = Query(None, description="Card type filter"),
    mechanics: Optional[str] = Query(None, description="Mechanic filter"),
    roles: Optional[str] = Query(None, description="Functional role filter"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    session: Session = Depends(get_neo4j_session),
):
    """Search cards with optional filters."""
    conditions = []
    params: dict = {}

    if colors:
        color_list = [c.strip() for c in colors.split(",")]
        conditions.append("ALL(color IN $colors WHERE color IN c.color_identity)")
        params["colors"] = color_list

    if cmc_min is not None:
        conditions.append("c.cmc >= $cmc_min")
        params["cmc_min"] = cmc_min

    if cmc_max is not None:
        conditions.append("c.cmc <= $cmc_max")
        params["cmc_max"] = cmc_max

    if types:
        conditions.append("c.type_line CONTAINS $types")
        params["types"] = types

    if mechanics:
        conditions.append(
            "EXISTS { MATCH (c)-[:HAS_MECHANIC]->(m:Mechanic {name: $mechanics}) }"
        )
        params["mechanics"] = mechanics

    if roles:
        conditions.append(
            "EXISTS { MATCH (c)-[:FILLS_ROLE]->(r:Functional_Role {name: $roles}) }"
        )
        params["roles"] = roles

    where_clause = " AND ".join(conditions)
    if where_clause:
        where_clause = "WHERE " + where_clause

    skip = (page - 1) * limit
    params["skip"] = skip
    params["limit"] = limit

    query = f"""
        MATCH (c:Card)
        {where_clause}
        RETURN c
        ORDER BY c.edhrec_rank ASC
        SKIP $skip LIMIT $limit
    """

    result = session.run(query, params)
    records = result.data()

    return {
        "total": len(records),
        "page": page,
        "limit": limit,
        "results": records,
    }


@router.get("/cards/{name}")
def get_card_by_name(
    name: str,
    session: Session = Depends(get_neo4j_session),
):
    """Get a card by name."""
    result = session.run(
        "MATCH (c:Card {name: $name}) RETURN c",
        {"name": name},
    )
    record = result.single()
    if record is None:
        raise HTTPException(status_code=404, detail=f"Card '{name}' not found")
    return record.data()


@router.get("/cards/{name}/similar")
def get_similar_cards(
    name: str,
    limit: int = Query(10, ge=1, le=50, description="Number of similar cards"),
    session: Session = Depends(get_neo4j_session),
):
    """Get cards similar to the given card via embedding similarity."""
    result = session.run(
        """
        MATCH (c:Card {name: $name})-[s:EMBEDDING_SIMILAR]-(other:Card)
        RETURN other.name AS name, s.score AS score
        ORDER BY s.score DESC
        LIMIT $limit
        """,
        {"name": name, "limit": limit},
    )
    records = result.data()

    return {
        "card": name,
        "similar_cards": records,
    }


@router.get("/cards/{name}/synergies")
def get_card_synergies(
    name: str,
    limit: int = Query(10, ge=1, le=50, description="Number of synergies"),
    session: Session = Depends(get_neo4j_session),
):
    """Get cards with synergy to the given card."""
    result = session.run(
        """
        MATCH (c:Card {name: $name})-[s:SYNERGIZES_WITH]-(other:Card)
        RETURN other.name AS name, s.synergy_score AS score
        ORDER BY s.synergy_score DESC
        LIMIT $limit
        """,
        {"name": name, "limit": limit},
    )
    records = result.data()

    return {
        "card": name,
        "synergies": records,
    }
