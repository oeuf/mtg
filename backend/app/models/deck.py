"""Deck-related models."""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field, field_validator

from app.models.card import Card
from app.models.commander import Commander


class DeckShell(BaseModel):
    """A deck shell with commander and cards."""

    commander: Commander
    cards: List[Card] = Field(max_length=99, description="Non-commander cards (max 99)")

    @field_validator("cards")
    @classmethod
    def validate_card_count(cls, v: List[Card]) -> List[Card]:
        """Validate deck has at most 99 non-commander cards."""
        if len(v) > 99:
            raise ValueError("Deck can have at most 99 non-commander cards (100 total)")
        return v

    def total_card_count(self) -> int:
        """Get total card count including commander."""
        return len(self.cards) + 1


class DeckAnalysis(BaseModel):
    """Analysis of a deck's composition."""

    total_cards: int
    avg_cmc: float = Field(ge=0.0)
    color_distribution: Dict[str, int] = Field(description="Count of cards by color")
    type_distribution: Dict[str, int] = Field(description="Count of cards by type")
    role_distribution: Dict[str, int] = Field(description="Count of cards by functional role")
    mana_curve: Dict[str, int] = Field(description="Card count by CMC")


class BuildDeckRequest(BaseModel):
    """Request to build an initial deck shell."""

    commander: str = Field(..., description="Commander card name")
    max_cmc: int = Field(default=4, ge=0, description="Maximum CMC for included cards")
    min_strength: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum synergy score")


class DeckValidation(BaseModel):
    """Result of deck validation."""

    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    color_identity: List[str] = Field(description="Validated color identity")
