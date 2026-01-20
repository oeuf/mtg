"""Card API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from api.dependencies import get_db
from api.schemas import CardResponse, ComboResponse
from src.graph.connection import Neo4jConnection
from src.synergy.queries import DeckbuildingQueries

router = APIRouter(prefix="/api/cards", tags=["cards"])


@router.get("/search", response_model=list[CardResponse])
async def search_cards(
    q: str = Query(..., min_length=2),
    max_cmc: Optional[int] = None,
    colors: Optional[str] = None,
    role: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Neo4jConnection = Depends(get_db)
):
    """Search for cards by name or text."""
    query = """
    MATCH (c:Card)
    WHERE (toLower(c.name) CONTAINS toLower($search)
           OR toLower(c.oracle_text) CONTAINS toLower($search))
      AND ($max_cmc IS NULL OR c.cmc <= $max_cmc)
      AND ($colors IS NULL OR ALL(color IN c.color_identity WHERE color IN $color_list))
      AND ($role IS NULL OR $role IN c.functional_categories)
    RETURN c.name AS name,
           c.mana_cost AS mana_cost,
           c.cmc AS cmc,
           c.type_line AS type_line,
           c.oracle_text AS oracle_text,
           c.color_identity AS color_identity,
           c.mechanics AS mechanics,
           c.functional_categories AS functional_categories,
           c.popularity_score AS popularity_score
    ORDER BY c.popularity_score DESC NULLS LAST
    LIMIT $limit
    """

    color_list = colors.split(",") if colors else None

    results = db.execute_query(query, {
        "search": q,
        "max_cmc": max_cmc,
        "colors": colors,
        "color_list": color_list,
        "role": role,
        "limit": limit
    })

    return [CardResponse(**r) for r in results]


@router.get("/{card_name}", response_model=CardResponse)
async def get_card(
    card_name: str,
    db: Neo4jConnection = Depends(get_db)
):
    """Get details for a specific card."""
    query = """
    MATCH (c:Card {name: $name})
    RETURN c.name AS name,
           c.mana_cost AS mana_cost,
           c.cmc AS cmc,
           c.type_line AS type_line,
           c.oracle_text AS oracle_text,
           c.color_identity AS color_identity,
           c.mechanics AS mechanics,
           c.functional_categories AS functional_categories,
           c.popularity_score AS popularity_score
    """

    results = db.execute_query(query, {"name": card_name})

    if not results:
        raise HTTPException(status_code=404, detail=f"Card '{card_name}' not found")

    return CardResponse(**results[0])


@router.get("/{card_name}/combos", response_model=list[ComboResponse])
async def get_combos(
    card_name: str,
    db: Neo4jConnection = Depends(get_db)
):
    """Get known combos for a card."""
    results = DeckbuildingQueries.find_known_combos(db, card_name)

    return [
        ComboResponse(
            piece1=card_name,
            piece2=r["combo_piece"],
            description=r.get("text", "")[:200] if r.get("text") else None
        )
        for r in results
    ]


@router.get("/role/{role_name}", response_model=list[CardResponse])
async def get_cards_by_role(
    role_name: str,
    colors: Optional[str] = None,
    max_cmc: int = Query(5, ge=0, le=20),
    limit: int = Query(20, ge=1, le=100),
    db: Neo4jConnection = Depends(get_db)
):
    """Get cards that fill a specific role."""
    color_list = colors.split(",") if colors else []

    results = DeckbuildingQueries.find_cards_by_role(
        db,
        role=role_name,
        color_identity=color_list,
        max_cmc=max_cmc,
        min_efficiency=0.0
    )

    return [
        CardResponse(
            name=r["name"],
            mana_cost=r.get("mana_cost"),
            cmc=r.get("cmc"),
            oracle_text=r.get("text")
        )
        for r in results[:limit]
    ]
