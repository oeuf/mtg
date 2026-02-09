"""Synergy and similarity models."""

from typing import Dict, Optional
from pydantic import BaseModel, Field


class SynergyDimensions(BaseModel):
    """7-dimensional synergy breakdown."""

    mechanic_overlap: float = Field(ge=0.0, le=1.0, description="Shared mechanics score")
    role_compatibility: float = Field(ge=0.0, le=1.0, description="Functional role match score")
    theme_alignment: float = Field(ge=0.0, le=1.0, description="Thematic alignment score")
    zone_chain: float = Field(ge=0.0, le=1.0, description="Zone interaction score")
    phase_alignment: float = Field(ge=0.0, le=1.0, description="Phase trigger score")
    color_compatibility: float = Field(ge=0.0, le=1.0, description="Color compatibility score")
    type_synergy: float = Field(ge=0.0, le=1.0, description="Card type synergy score")

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return self.model_dump()

    def weighted_average(self) -> float:
        """Compute weighted average with predefined weights."""
        weights = {
            "mechanic_overlap": 0.20,
            "role_compatibility": 0.25,
            "theme_alignment": 0.20,
            "zone_chain": 0.15,
            "phase_alignment": 0.10,
            "color_compatibility": 0.05,
            "type_synergy": 0.05,
        }

        total = sum(
            getattr(self, dim) * weight
            for dim, weight in weights.items()
        )
        return min(1.0, max(0.0, total))


class SynergyResponse(BaseModel):
    """Synergy analysis for a card with another card."""

    card_name: str = Field(..., description="Card being synergized with")
    synergy_score: float = Field(ge=0.0, le=1.0, description="Overall synergy score (0-1)")
    dimensions: SynergyDimensions = Field(..., description="7-dimensional breakdown")
    explanation: Optional[str] = Field(
        default=None, description="Human-readable explanation of synergy"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "card_name": "Eternal Witness",
                "synergy_score": 0.78,
                "dimensions": {
                    "mechanic_overlap": 0.8,
                    "role_compatibility": 0.7,
                    "theme_alignment": 0.6,
                    "zone_chain": 0.5,
                    "phase_alignment": 0.4,
                    "color_compatibility": 0.3,
                    "type_synergy": 0.2,
                },
                "explanation": "Strong ETB trigger synergy with Muldrotha's recursion theme",
            }
        }


class SimilarCardResponse(BaseModel):
    """Response for similar cards endpoint."""

    card_name: str = Field(..., description="Similar card name")
    similarity_score: float = Field(ge=0.0, le=1.0, description="Embedding similarity (0-1)")
    reason: Optional[str] = Field(default=None, description="Why this card is similar")


class RecommendationResponse(BaseModel):
    """Recommendation response for deck building."""

    card_name: str
    synergy_score: float = Field(ge=0.0, le=1.0)
    category: str = Field(description="Category (synergy, similarity, role-based)")
    mechanic_overlap_count: int = 0
    has_color_match: bool = False
    edhrec_rank: Optional[int] = None
