"""Commander API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from api.dependencies import get_db
from api.schemas import CommanderResponse, RecommendationResponse
from src.graph.connection import Neo4jConnection
from src.synergy.queries import DeckbuildingQueries

router = APIRouter(prefix="/api/commanders", tags=["commanders"])


@router.get("/", response_model=list[CommanderResponse])
async def list_commanders(
    limit: int = Query(50, ge=1, le=500),
    search: Optional[str] = None,
    colors: Optional[str] = None,
    db: Neo4jConnection = Depends(get_db)
):
    """List all commanders with optional filtering."""
    query = """
    MATCH (c:Commander)
    WHERE ($search IS NULL OR toLower(c.name) CONTAINS toLower($search))
      AND ($colors IS NULL OR ALL(color IN $color_list WHERE color IN c.color_identity))
    RETURN c.name AS name,
           c.mana_cost AS mana_cost,
           c.cmc AS cmc,
           c.type_line AS type_line,
           c.oracle_text AS oracle_text,
           c.color_identity AS color_identity,
           c.mechanics AS mechanics,
           c.functional_categories AS functional_categories
    ORDER BY c.edhrec_rank ASC NULLS LAST
    LIMIT $limit
    """

    color_list = colors.split(",") if colors else None

    results = db.execute_query(query, {
        "search": search,
        "colors": colors,
        "color_list": color_list,
        "limit": limit
    })

    return [CommanderResponse(**r) for r in results]


@router.get("/{commander_name}", response_model=CommanderResponse)
async def get_commander(
    commander_name: str,
    db: Neo4jConnection = Depends(get_db)
):
    """Get details for a specific commander."""
    query = """
    MATCH (c:Commander {name: $name})
    OPTIONAL MATCH (c)-[s:SYNERGIZES_WITH_MECHANIC]->(m:Mechanic)
    RETURN c.name AS name,
           c.mana_cost AS mana_cost,
           c.cmc AS cmc,
           c.type_line AS type_line,
           c.oracle_text AS oracle_text,
           c.color_identity AS color_identity,
           c.mechanics AS mechanics,
           c.functional_categories AS functional_categories,
           collect(DISTINCT m.name) AS synergies
    """

    results = db.execute_query(query, {"name": commander_name})

    if not results:
        raise HTTPException(status_code=404, detail=f"Commander '{commander_name}' not found")

    return CommanderResponse(**results[0])


@router.get("/{commander_name}/recommendations", response_model=list[RecommendationResponse])
async def get_recommendations(
    commander_name: str,
    max_cmc: int = Query(10, ge=0, le=20),
    limit: int = Query(50, ge=1, le=200),
    db: Neo4jConnection = Depends(get_db)
):
    """Get card recommendations for a commander."""
    # Try v2 (GDS-enhanced) first, fall back to v1
    try:
        results = DeckbuildingQueries.find_synergistic_cards_v2(
            db,
            commander_name=commander_name,
            max_cmc=max_cmc,
            limit=limit
        )
    except Exception:
        results = DeckbuildingQueries.find_synergistic_cards(
            db,
            commander_name=commander_name,
            max_cmc=max_cmc,
            min_strength=0.0,
            limit=limit
        )

    return [
        RecommendationResponse(
            name=r["name"],
            mana_cost=r.get("mana_cost"),
            type_line=r.get("type"),
            cmc=r.get("cmc"),
            score=r.get("combined_score", r.get("synergy_strength", 0)),
            shared_mechanics=r.get("shared_mechanics", []),
            roles=r.get("roles", [])
        )
        for r in results
    ]
