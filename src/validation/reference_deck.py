"""Load reference decklists for validation."""

from pathlib import Path


def load_reference_deck(filepath: str, exclude_commander: bool = False) -> list[str]:
    """Load card names from reference deck file.

    Args:
        filepath: Path to deck file (one card name per line)
        exclude_commander: If True, excludes cards with "Commander" in database

    Returns:
        List of card names from the deck
    """
    cards = []

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            cards.append(line)

    # Commander exclusion will be handled in query, not here
    # This keeps the loader simple
    return cards
