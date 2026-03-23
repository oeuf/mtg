"""Commander-specific models."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator

from app.models.card import Card


class Commander(Card):
    """Represents a legendary creature that can be a Commander."""

    is_legendary: bool = Field(default=True, description="Commanders must be legendary")
    power: Optional[str] = Field(default=None, description="Creature power")
    toughness: Optional[str] = Field(default=None, description="Creature toughness")

    @field_validator("is_legendary")
    @classmethod
    def validate_legendary(cls, v: bool) -> bool:
        """Commanders must be legendary."""
        if not v:
            raise ValueError("Commanders must be legendary creatures")
        return v


class CommanderStats(BaseModel):
    """Statistics about a commander."""

    name: str
    color_identity: list[str]
    card_count_in_database: int
    edhrec_rank: Optional[int] = None
    popularity_percentile: float = Field(ge=0.0, le=100.0)


class CommanderRecommendation(BaseModel):
    """Recommendation for cards in a commander deck."""

    card_name: str
    reason: str
    synergy_score: float = Field(ge=0.0, le=1.0)
    mechanic_match: bool
    role_match: bool
