"""Deck API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from api.dependencies import get_db
from api.schemas import DeckAnalysis, RecommendationResponse
from src.graph.connection import Neo4jConnection
from src.synergy.queries import DeckbuildingQueries

router = APIRouter(prefix="/api/decks", tags=["decks"])

# In-memory deck storage (for demo; use database in production)
_decks: dict[str, dict] = {}
_deck_counter = 0


class CreateDeckRequest(BaseModel):
    """Request to create a new deck."""
    commander: str
    name: Optional[str] = None


class AddCardRequest(BaseModel):
    """Request to add a card to deck."""
    card_name: str


class AnalyzeDeckRequest(BaseModel):
    """Request to analyze a decklist."""
    commander: str
    cards: list[str] = Field(..., min_length=1)


@router.post("/")
async def create_deck(
    request: CreateDeckRequest,
    db: Neo4jConnection = Depends(get_db)
):
    """Create a new deck."""
    global _deck_counter

    # Verify commander exists
    query = "MATCH (c:Commander {name: $name}) RETURN c.name"
    result = db.execute_query(query, {"name": request.commander})

    if not result:
        raise HTTPException(status_code=404, detail=f"Commander '{request.commander}' not found")

    _deck_counter += 1
    deck_id = f"deck_{_deck_counter}"

    _decks[deck_id] = {
        "id": deck_id,
        "name": request.name or f"{request.commander} Deck",
        "commander": request.commander,
        "cards": []
    }

    return _decks[deck_id]


@router.get("/{deck_id}")
async def get_deck(deck_id: str):
    """Get a deck by ID."""
    if deck_id not in _decks:
        raise HTTPException(status_code=404, detail="Deck not found")

    return _decks[deck_id]


@router.post("/{deck_id}/cards")
async def add_card_to_deck(
    deck_id: str,
    request: AddCardRequest,
    db: Neo4jConnection = Depends(get_db)
):
    """Add a card to the deck."""
    if deck_id not in _decks:
        raise HTTPException(status_code=404, detail="Deck not found")

    # Verify card exists
    query = "MATCH (c:Card {name: $name}) RETURN c.name"
    result = db.execute_query(query, {"name": request.card_name})

    if not result:
        raise HTTPException(status_code=404, detail=f"Card '{request.card_name}' not found")

    deck = _decks[deck_id]
    if request.card_name not in deck["cards"]:
        deck["cards"].append(request.card_name)

    return deck


@router.delete("/{deck_id}/cards/{card_name}")
async def remove_card_from_deck(deck_id: str, card_name: str):
    """Remove a card from the deck."""
    if deck_id not in _decks:
        raise HTTPException(status_code=404, detail="Deck not found")

    deck = _decks[deck_id]
    if card_name in deck["cards"]:
        deck["cards"].remove(card_name)

    return deck


@router.post("/analyze", response_model=DeckAnalysis)
async def analyze_deck(
    request: AnalyzeDeckRequest,
    db: Neo4jConnection = Depends(get_db)
):
    """Analyze a decklist for role coverage and suggestions."""
    commander = request.commander
    cards = request.cards

    # Get role coverage
    role_query = """
    UNWIND $cards AS card_name
    MATCH (c:Card {name: card_name})-[:FILLS_ROLE]->(r:Functional_Role)
    RETURN r.name AS role, count(*) AS count
    """

    role_results = db.execute_query(role_query, {"cards": cards})
    role_coverage = {r["role"]: r["count"] for r in role_results}

    # Expected roles
    expected_roles = ["ramp", "card_draw", "removal", "protection", "recursion"]
    missing_roles = [r for r in expected_roles if role_coverage.get(r, 0) < 5]

    # Get suggestions
    try:
        suggestions = DeckbuildingQueries.find_synergistic_cards_v2(
            db, commander, max_cmc=6, limit=20
        )
    except Exception:
        suggestions = DeckbuildingQueries.find_synergistic_cards(
            db, commander, max_cmc=6, min_strength=0.5, limit=20
        )

    # Filter out cards already in deck
    card_set = set(cards)
    new_suggestions = [s for s in suggestions if s["name"] not in card_set]

    return DeckAnalysis(
        commander=commander,
        card_count=len(cards),
        role_coverage=role_coverage,
        missing_roles=missing_roles,
        suggested_additions=[
            RecommendationResponse(
                name=s["name"],
                mana_cost=s.get("mana_cost"),
                type_line=s.get("type"),
                cmc=s.get("cmc"),
                score=s.get("combined_score", 0),
                shared_mechanics=s.get("shared_mechanics", []),
                roles=s.get("roles", [])
            )
            for s in new_suggestions[:10]
        ],
        suggested_cuts=[]  # TODO: Implement cut suggestions
    )
