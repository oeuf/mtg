"""Cards API router."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from neo4j import Session
from rapidfuzz import fuzz, process

from app.dependencies import get_neo4j_session

logger = logging.getLogger(__name__)
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

    # Always include label filter; append other conditions if present
    label_condition = "(c:Card OR c:Commander)"
    all_conditions = [label_condition] + conditions
    where_clause = "WHERE " + " AND ".join(all_conditions)

    skip = (page - 1) * limit
    params["skip"] = skip
    params["limit"] = limit

    count_query = f"MATCH (c) {where_clause} RETURN count(c) AS total"
    count_params = {k: v for k, v in params.items() if k not in ("skip", "limit")}
    count_result = session.run(count_query, count_params)
    count_record = count_result.single()
    total = count_record["total"] if count_record else 0

    query = f"""
        MATCH (c)
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
    """Fast autocomplete for card names with fuzzy re-ranking."""
    base_match = "MATCH (c) WHERE (c:Card OR c:Commander)"
    if commander_only:
        base_match += " AND c:Commander"
    result = session.run(
        base_match + " AND toLower(c.name) CONTAINS toLower($q) "
        "RETURN c.name AS name, c.type_line AS type_line, c.mana_cost AS mana_cost "
        "ORDER BY CASE WHEN toLower(c.name) STARTS WITH toLower($q) THEN 0 ELSE 1 END, "
        "c.edhrec_rank ASC "
        "LIMIT $fetch_limit",
        {"q": q, "fetch_limit": 50},
    )
    records = result.data()

    if not records:
        return []

    name_map = {r["name"]: r for r in records}
    ranked = process.extract(q, list(name_map.keys()), scorer=fuzz.WRatio, limit=limit)
    return [name_map[name] for name, score, _ in ranked]


@router.get("/cards/by-role/{role}")
def get_cards_by_role(
    role: str,
    color_identity: Optional[str] = Query(None, description="Comma-separated colors (e.g. U,B)"),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_neo4j_session),
):
    """Get cards that fill a functional role, optionally filtered by color identity."""
    params: dict = {"role": role, "limit": limit}
    color_clause = ""
    if color_identity:
        color_list = [c.strip() for c in color_identity.split(",")]
        color_clause = "AND ALL(color IN card.color_identity WHERE color IN $colors) "
        params["colors"] = color_list

    result = session.run(
        "MATCH (card:Card)-[r:FILLS_ROLE]->(role_node:Functional_Role {name: $role}) "
        "WHERE NOT card:Commander "
        f"{color_clause}"
        "RETURN card.name AS name, card.mana_cost AS mana_cost, card.cmc AS cmc, "
        "card.type_line AS type_line, card.oracle_text AS oracle_text, "
        "card.color_identity AS color_identity "
        "ORDER BY card.edhrec_rank ASC "
        "LIMIT $limit",
        params,
    )
    return result.data()


@router.get("/cards/{name:path}/similar")
def get_similar_cards(
    name: str,
    limit: int = Query(10, ge=1, le=50, description="Number of similar cards"),
    session: Session = Depends(get_neo4j_session),
):
    """Get cards similar to the given card via embedding similarity."""
    logger.info("[cards] get_similar_cards: name=%r", name)
    exists = session.run(
        "MATCH (c {name: $name}) WHERE (c:Card OR c:Commander) RETURN c", {"name": name}
    )
    if exists.single() is None:
        raise HTTPException(status_code=404, detail=f"Card '{name}' not found")

    result = session.run(
        """
        MATCH (c {name: $name})-[s:EMBEDDING_SIMILAR]-(other)
        WHERE (c:Card OR c:Commander) AND (other:Card OR other:Commander)
        RETURN other.name AS name, max(s.score) AS score
        ORDER BY score DESC
        LIMIT $limit
        """,
        {"name": name, "limit": limit},
    )
    records = result.data()
    logger.info("[cards] get_similar_cards: name=%r count=%d", name, len(records))

    return {
        "card": name,
        "similar_cards": records,
    }


@router.get("/cards/{name:path}/synergies")
def get_card_synergies(
    name: str,
    limit: int = Query(10, ge=1, le=50, description="Number of synergies"),
    session: Session = Depends(get_neo4j_session),
):
    """Get cards with synergy to the given card."""
    logger.info("[cards] get_card_synergies: name=%r", name)
    exists = session.run(
        "MATCH (c {name: $name}) WHERE (c:Card OR c:Commander) RETURN c", {"name": name}
    )
    if exists.single() is None:
        raise HTTPException(status_code=404, detail=f"Card '{name}' not found")

    result = session.run(
        """
        MATCH (c {name: $name})-[s:SYNERGIZES_WITH]-(other)
        WHERE (c:Card OR c:Commander) AND (other:Card OR other:Commander)
        RETURN other.name AS name, max(s.synergy_score) AS score
        ORDER BY score DESC
        LIMIT $limit
        """,
        {"name": name, "limit": limit},
    )
    records = result.data()
    logger.info("[cards] get_card_synergies: name=%r count=%d", name, len(records))

    return {
        "card": name,
        "synergies": records,
    }


@router.get("/cards/{name:path}/combos")
def get_card_combos(
    name: str,
    limit: int = Query(10, ge=1, le=50, description="Number of combos"),
    session: Session = Depends(get_neo4j_session),
):
    """Get known combos involving the given card."""
    logger.info("[cards] get_card_combos: name=%r", name)
    exists = session.run(
        "MATCH (c {name: $name}) WHERE (c:Card OR c:Commander) RETURN c", {"name": name}
    )
    if exists.single() is None:
        raise HTTPException(status_code=404, detail=f"Card '{name}' not found")

    result = session.run(
        """
        MATCH (c {name: $name})-[cb:COMBOS_WITH]-(other)
        WHERE (c:Card OR c:Commander) AND (other:Card OR other:Commander)
        RETURN other.name AS name, cb.combo_name AS combo_name,
               cb.description AS description
        ORDER BY cb.combo_name
        LIMIT $limit
        """,
        {"name": name, "limit": limit},
    )
    records = result.data()
    logger.info("[cards] get_card_combos: name=%r count=%d", name, len(records))

    return {
        "card": name,
        "combos": records,
    }


@router.get("/cards/{name:path}")
def get_card_by_name(
    name: str,
    session: Session = Depends(get_neo4j_session),
):
    """Get a card by name."""
    logger.info("[cards] get_card_by_name: name=%r", name)
    result = session.run(
        "MATCH (c {name: $name}) WHERE (c:Card OR c:Commander) "
        "RETURN c.name AS name, c.mana_cost AS mana_cost, c.cmc AS cmc, "
        "c.type_line AS type_line, c.oracle_text AS oracle_text, "
        "c.color_identity AS color_identity, c.colors AS colors, "
        "c.keywords AS keywords, c.is_legendary AS is_legendary, "
        "c.edhrec_rank AS edhrec_rank, c.power AS power, c.toughness AS toughness, "
        "c.functional_categories AS functional_categories, "
        "c.mechanics AS mechanics, c.themes AS themes, "
        "c.archetype AS archetype, c.popularity_score AS popularity_score",
        {"name": name},
    )
    record = result.single()
    logger.info("[cards] get_card_by_name: found=%s", record is not None)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Card '{name}' not found")
    return record.data()
