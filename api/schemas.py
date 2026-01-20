"""Pydantic schemas for API request/response models."""

from pydantic import BaseModel, Field
from typing import Optional


class CardBase(BaseModel):
    """Base card model."""
    name: str
    mana_cost: Optional[str] = None
    cmc: Optional[int] = None
    type_line: Optional[str] = None
    oracle_text: Optional[str] = None
    color_identity: list[str] = Field(default_factory=list)


class CardResponse(CardBase):
    """Card response with computed fields."""
    mechanics: list[str] = Field(default_factory=list)
    functional_categories: list[str] = Field(default_factory=list)
    synergy_score: Optional[float] = None
    popularity_score: Optional[float] = None


class CommanderResponse(CardResponse):
    """Commander response."""
    can_be_commander: bool = True
    synergies: list[str] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    """Card recommendation with score."""
    name: str
    mana_cost: Optional[str] = None
    type_line: Optional[str] = None
    cmc: Optional[int] = None
    score: float
    shared_mechanics: list[str] = Field(default_factory=list)
    roles: list[str] = Field(default_factory=list)


class DeckAnalysis(BaseModel):
    """Deck analysis response."""
    commander: str
    card_count: int
    role_coverage: dict[str, int]
    missing_roles: list[str]
    suggested_additions: list[RecommendationResponse]
    suggested_cuts: list[str]


class ComboResponse(BaseModel):
    """Known combo response."""
    piece1: str
    piece2: str
    description: Optional[str] = None


class GraphNodeResponse(BaseModel):
    """Graph node for visualization."""
    id: str
    label: str
    type: str  # Card, Mechanic, Role, etc.
    properties: dict = Field(default_factory=dict)


class GraphEdgeResponse(BaseModel):
    """Graph edge for visualization."""
    source: str
    target: str
    type: str
    properties: dict = Field(default_factory=dict)


class GraphResponse(BaseModel):
    """Graph data for visualization."""
    nodes: list[GraphNodeResponse]
    edges: list[GraphEdgeResponse]
