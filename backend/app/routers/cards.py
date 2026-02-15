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
    text_search: Optional[str] = Query(None, description="Search by name or oracle text"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    session: Session = Depends(get_neo4j_session),
):
    """Search cards with optional filters."""
    conditions = []
    params: dict = {}

    if text_search:
        conditions.append(
            "(toLower(c.name) CONTAINS toLower($text_search) "
            "OR toLower(c.oracle_text) CONTAINS toLower($text_search))"
        )
        params["text_search"] = text_search

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

    count_query = f"MATCH (c:Card) {where_clause} RETURN count(c) AS total"
    count_params = {k: v for k, v in params.items() if k not in ("skip", "limit")}
    count_result = session.run(count_query, count_params)
    count_record = count_result.single()
    total = count_record["total"] if count_record else 0

    query = f"""
        MATCH (c:Card)
        {where_clause}
        RETURN c.name AS name, c.mana_cost AS mana_cost, c.cmc AS cmc,
               c.type_line AS type_line, c.oracle_text AS oracle_text,
               c.color_identity AS color_identity, c.colors AS colors,
               c.keywords AS keywords, c.is_legendary AS is_legendary,
               c.edhrec_rank AS edhrec_rank,
               c.functional_categories AS functional_categories,
               c.mechanics AS mechanics, c.themes AS themes,
               c.archetype AS archetype, c.popularity_score AS popularity_score
        ORDER BY c.edhrec_rank ASC
        SKIP $skip LIMIT $limit
    """

    result = session.run(query, params)
    items = result.data()

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.get("/cards/autocomplete")
def autocomplete_cards(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(8, ge=1, le=20),
    commander_only: bool = Query(False),
    session: Session = Depends(get_neo4j_session),
):
    """Fast autocomplete for card names."""
    label = "Commander" if commander_only else "Card"
    result = session.run(
        f"MATCH (c:{label}) "
        "WHERE toLower(c.name) CONTAINS toLower($q) "
        "RETURN c.name AS name, c.type_line AS type_line, c.mana_cost AS mana_cost "
        "ORDER BY CASE WHEN toLower(c.name) STARTS WITH toLower($q) THEN 0 ELSE 1 END, "
        "c.edhrec_rank ASC "
        "LIMIT $limit",
        {"q": q, "limit": limit},
    )
    return result.data()


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
    exists = session.run("MATCH (c:Card {name: $name}) RETURN c", {"name": name})
    if exists.single() is None:
        raise HTTPException(status_code=404, detail=f"Card '{name}' not found")

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
    exists = session.run("MATCH (c:Card {name: $name}) RETURN c", {"name": name})
    if exists.single() is None:
        raise HTTPException(status_code=404, detail=f"Card '{name}' not found")

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


@router.get("/cards/{name}/combos")
def get_card_combos(
    name: str,
    limit: int = Query(10, ge=1, le=50, description="Number of combos"),
    session: Session = Depends(get_neo4j_session),
):
    """Get known combos involving the given card."""
    exists = session.run("MATCH (c:Card {name: $name}) RETURN c", {"name": name})
    if exists.single() is None:
        raise HTTPException(status_code=404, detail=f"Card '{name}' not found")

    result = session.run(
        """
        MATCH (c:Card {name: $name})-[cb:COMBOS_WITH]-(other:Card)
        RETURN other.name AS name, cb.combo_name AS combo_name,
               cb.description AS description
        ORDER BY cb.combo_name
        LIMIT $limit
        """,
        {"name": name, "limit": limit},
    )
    records = result.data()

    return {
        "card": name,
        "combos": records,
    }
