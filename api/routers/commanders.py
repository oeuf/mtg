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
    db = Depends(get_db)
):
    """Get card recommendations for a commander."""
    from api.dependencies import MockNeo4jConnection

    # Check if using mock mode
    if isinstance(db, MockNeo4jConnection):
        # Return mock recommendations
        mock_recs = [
            {"name": "Sol Ring", "mana_cost": "{1}", "cmc": 1, "type": "Artifact", "combined_score": 0.95, "shared_mechanics": ["mana_production"], "roles": ["ramp"]},
            {"name": "Eternal Witness", "mana_cost": "{1}{G}{G}", "cmc": 3, "type": "Creature", "combined_score": 0.92, "shared_mechanics": ["etb_trigger", "recursion"], "roles": ["recursion"]},
            {"name": "Spore Frog", "mana_cost": "{G}", "cmc": 1, "type": "Creature", "combined_score": 0.88, "shared_mechanics": ["sacrifice"], "roles": ["protection"]},
            {"name": "Sakura-Tribe Elder", "mana_cost": "{1}{G}", "cmc": 2, "type": "Creature", "combined_score": 0.87, "shared_mechanics": ["sacrifice", "ramp"], "roles": ["ramp"]},
            {"name": "Rhystic Study", "mana_cost": "{2}{U}", "cmc": 3, "type": "Enchantment", "combined_score": 0.85, "shared_mechanics": ["card_draw"], "roles": ["card_draw"]},
            {"name": "Mystic Remora", "mana_cost": "{U}", "cmc": 1, "type": "Enchantment", "combined_score": 0.84, "shared_mechanics": ["card_draw"], "roles": ["card_draw"]},
            {"name": "Animate Dead", "mana_cost": "{1}{B}", "cmc": 2, "type": "Enchantment", "combined_score": 0.83, "shared_mechanics": ["recursion"], "roles": ["recursion"]},
            {"name": "Reanimate", "mana_cost": "{B}", "cmc": 1, "type": "Sorcery", "combined_score": 0.82, "shared_mechanics": ["recursion"], "roles": ["recursion"]},
            {"name": "Coiling Oracle", "mana_cost": "{G}{U}", "cmc": 2, "type": "Creature", "combined_score": 0.80, "shared_mechanics": ["etb_trigger"], "roles": ["ramp", "card_draw"]},
            {"name": "Mulldrifter", "mana_cost": "{4}{U}", "cmc": 5, "type": "Creature", "combined_score": 0.78, "shared_mechanics": ["etb_trigger", "evoke"], "roles": ["card_draw"]},
        ]
        results = [r for r in mock_recs if r["cmc"] <= max_cmc][:limit]
    else:
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
