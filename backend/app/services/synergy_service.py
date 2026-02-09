"""Service layer wrapping CardSynergyEngine for synergy analysis."""

from typing import Dict, List, Optional, Tuple

from src.synergy.card_synergies import CardSynergyEngine


class SynergyService:
    """Wraps CardSynergyEngine for the API layer."""

    def __init__(self, conn=None):
        self._engine = CardSynergyEngine()
        self._conn = conn

    def compute_synergy_score(self, card1: Dict, card2: Dict) -> Tuple[float, Dict]:
        """Compute synergy score between two cards."""
        return self._engine.compute_synergy_score(card1, card2)

    def calculate_role_compatibility(self, roles1: List[str], roles2: List[str]) -> float:
        """Calculate role compatibility score."""
        return self._engine.calculate_role_compatibility(roles1, roles2)

    def find_mechanic_synergies(self, min_shared_mechanics: int = 2) -> List[Dict]:
        """Find card pairs with shared mechanics."""
        return self._engine.find_mechanic_synergies(self._conn, min_shared_mechanics=min_shared_mechanics)
