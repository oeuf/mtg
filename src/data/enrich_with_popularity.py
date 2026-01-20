"""Enrich cards with popularity scores from precon data."""

from typing import Dict, List
from src.data.popularity import PopularityCalculator


def enrich_cards_with_popularity(
    cards: List[dict],
    precon_counts: Dict[str, int],
    total_precons: int
) -> List[dict]:
    """Add popularity_score and precon_count to cards.

    Args:
        cards: List of card dictionaries
        precon_counts: Dictionary of card name -> precon appearance count
        total_precons: Total number of Commander precons

    Returns:
        Cards with added popularity_score and precon_count fields
    """
    calculator = PopularityCalculator(total_precons)

    for card in cards:
        name = card.get("name", "")
        edhrec_rank = card.get("edhrec_rank")
        precon_count = precon_counts.get(name, 0)

        card["precon_count"] = precon_count
        card["popularity_score"] = calculator.calculate(edhrec_rank, precon_count)

    return cards
