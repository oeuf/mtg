"""Deck-related models."""

from pydantic import BaseModel, Field


class DeckShell(BaseModel):
    """A deck shell with commander and cards grouped by role."""

    commander: str
    cards_by_role: dict[str, list[str]]
    total_cards: int


class DeckAnalysis(BaseModel):
    """Analysis of a deck's composition."""

    total_cards: int
    avg_cmc: float = Field(ge=0.0)
    color_distribution: dict[str, int] = Field(description="Count of cards by color")
    type_distribution: dict[str, int] = Field(description="Count of cards by type")
    role_distribution: dict[str, int] = Field(description="Count of cards by functional role")
    mana_curve: dict[str, int] = Field(description="Card count by CMC")


class BuildDeckRequest(BaseModel):
    """Request to build an initial deck shell."""

    commander: str = Field(..., description="Commander card name")
    max_cmc: int = Field(default=4, ge=0, description="Maximum CMC for included cards")
    min_strength: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum synergy score")


class DeckValidation(BaseModel):
    """Result of deck validation."""

    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    color_identity: list[str] = Field(description="Validated color identity")
