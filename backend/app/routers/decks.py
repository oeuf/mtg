"""Deck building and analysis endpoints."""

from collections import Counter
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from neo4j import Session
from pydantic import BaseModel

from app.dependencies import get_neo4j_session
from app.limiter import limiter
from app.models.deck import DeckShell

router = APIRouter()


class BuildShellRequest(BaseModel):
    commander: str


class CardEntry(BaseModel):
    name: str | None = None
    cmc: float = 0
    colors: list[str] = []
    type_line: str = "Unknown"
    functional_categories: list[str] = []

    model_config = {"extra": "allow"}


class AnalyzeDeckRequest(BaseModel):
    commander: dict[str, Any] = {}
    cards: list[CardEntry] = []


@router.post("/decks/build-shell", response_model=DeckShell)
@limiter.limit("10/minute")
def build_deck_shell(request: Request, body: BuildShellRequest, session: Session = Depends(get_neo4j_session)):
    """Build an initial deck shell for a given commander."""
    commander_name = body.commander
    if not commander_name:
        raise HTTPException(status_code=400, detail="Commander name is required")

    # Look up commander in Neo4j
    result = session.run(
        "MATCH (c:Card {name: $name}) WHERE c.is_legendary = true RETURN c",
        name=commander_name,
    )
    record = result.single()
    if record is None:
        raise HTTPException(
            status_code=404, detail=f"Commander '{commander_name}' not found"
        )

    commander_data = record["c"]

    # Find synergistic cards for the commander
    cards_result = session.run(
        """
        MATCH (cmd:Card {name: $name})-[s:SYNERGIZES_WITH]-(c:Card)
        WHERE c.is_legendary = false
        RETURN c, s.synergy_score AS score
        ORDER BY score DESC
        LIMIT 37
        """,
        name=commander_name,
    )
    cards_by_role: dict[str, list] = {}
    for rec in cards_result:
        card = rec["c"]
        card_name = card.get("name", "Unknown")
        role = card.get("functional_categories", ["utility"])[0] if card.get("functional_categories") else "utility"
        cards_by_role.setdefault(role, []).append(card_name)

    total_cards = sum(len(v) for v in cards_by_role.values()) + 1  # +1 for commander

    return {
        "commander": commander_name,
        "cards_by_role": cards_by_role,
        "total_cards": total_cards,
    }


@router.post("/decks/analyze")
@limiter.limit("20/minute")
def analyze_deck(request: Request, body: AnalyzeDeckRequest, session: Session = Depends(get_neo4j_session)):
    """Analyze deck composition."""
    cards = body.cards

    total_cards = len(cards) + 1  # +1 for commander

    # Average CMC
    cmc_values = [card.cmc for card in cards]
    avg_cmc = sum(cmc_values) / len(cmc_values) if cmc_values else 0.0

    # Color distribution
    color_counter: Counter = Counter()
    for card in cards:
        for color in card.colors:
            color_counter[color] += 1
    color_distribution = dict(color_counter)

    # Type distribution
    type_counter: Counter = Counter()
    for card in cards:
        type_counter[card.type_line] += 1
    type_distribution = dict(type_counter)

    # Role distribution — look up functional_roles from Neo4j per card name
    role_counter: Counter = Counter()
    card_names = [card.name for card in cards if card.name]
    if card_names:
        roles_result = session.run(
            """
            UNWIND $names AS name
            MATCH (c:Card {name: name})
            UNWIND coalesce(c.functional_categories, []) AS role
            RETURN role, count(*) AS cnt
            """,
            names=card_names,
        )
        for rec in roles_result:
            role_counter[rec["role"]] += rec["cnt"]
    role_distribution = dict(role_counter)

    # Mana curve: count cards per CMC value
    mana_counter: Counter = Counter()
    for card in cards:
        mana_counter[str(int(card.cmc))] += 1
    mana_curve = dict(mana_counter)

    return {
        "total_cards": total_cards,
        "avg_cmc": avg_cmc,
        "color_distribution": color_distribution,
        "type_distribution": type_distribution,
        "role_distribution": role_distribution,
        "mana_curve": mana_curve,
    }
