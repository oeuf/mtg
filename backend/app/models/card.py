"""Card data models."""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class Card(BaseModel):
    """Represents a Magic: The Gathering card."""

    name: str = Field(..., description="Card name")
    mana_cost: str = Field(default="", description="Mana cost string (e.g., {2}{B}{G}{U})")
    cmc: float = Field(ge=0.0, description="Converted mana cost")
    type_line: str = Field(..., description="Card type line (e.g., 'Creature — Elemental')")
    oracle_text: str = Field(default="", description="Official card rules text")
    color_identity: List[str] = Field(default_factory=list, description="Color identity letters")
    colors: List[str] = Field(default_factory=list, description="Colors in mana cost")
    keywords: List[str] = Field(default_factory=list, description="Ability keywords")
    is_legendary: bool = Field(default=False, description="Is legendary creature/planeswalker")
    edhrec_rank: Optional[int] = Field(default=None, description="EDHREC popularity rank")
    functional_categories: List[str] = Field(
        default_factory=list, description="Functional roles (ramp, draw, removal)"
    )
    mechanics: List[str] = Field(default_factory=list, description="Mechanics extracted from text")
    themes: List[str] = Field(default_factory=list, description="Thematic categories")
    archetype: Optional[str] = Field(default=None, description="Card community/archetype")
    popularity_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Normalized popularity")

    @field_validator("color_identity", "colors")
    @classmethod
    def validate_colors(cls, v: List[str]) -> List[str]:
        """Validate colors are valid MTG colors."""
        valid_colors = {"W", "U", "B", "R", "G", "C"}
        if not all(c in valid_colors for c in v):
            raise ValueError("Invalid color identity")
        return v



class CardSearchFilters(BaseModel):
    """Filters for card search."""

    colors: Optional[List[str]] = Field(default=None, description="Exact color match")
    color_identity: Optional[List[str]] = Field(default=None, description="Color identity filters")
    types: Optional[List[str]] = Field(default=None, description="Card types (Creature, Instant, etc.)")
    cmc_min: Optional[int] = Field(default=None, ge=0, description="Minimum CMC")
    cmc_max: Optional[int] = Field(default=None, ge=0, description="Maximum CMC")
    rarity: Optional[List[str]] = Field(default=None, description="Rarity filters")
    mechanics: Optional[List[str]] = Field(default=None, description="Mechanic filters")
    roles: Optional[List[str]] = Field(default=None, description="Functional role filters")
    text_search: Optional[str] = Field(default=None, description="Full-text search in oracle text")
    page: int = Field(default=1, ge=1, description="Page number for pagination")
    limit: int = Field(default=20, ge=1, le=100, description="Results per page")
