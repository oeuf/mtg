"""Load reference decklists for validation."""

import re
from pathlib import Path
from typing import Optional


def parse_decklist_line(line: str) -> Optional[str]:
    """Parse a single line from a decklist.

    Formats supported:
    - "1\tCard Name" (tab-separated)
    - "1 Card Name" (space-separated)
    - "4\tForest" (multiple copies)

    Returns:
        Card name or None if line should be skipped
    """
    line = line.strip()

    # Skip empty lines
    if not line:
        return None

    # Skip comments and headers
    if line.startswith("#") or line.startswith("*") or line.startswith("-"):
        return None

    # Skip section headers
    if line.startswith("##"):
        return None

    # Match quantity + card name (tab or space separated)
    match = re.match(r'^(\d+)\s+(.+)$', line)
    if match:
        return match.group(2).strip()

    return None


def load_reference_deck(
    filepath: str,
    exclude_commander: bool = False,
    commander_name: str = "Muldrotha, the Gravetide"
) -> set[str]:
    """Load card names from a Moxfield-format decklist.

    Args:
        filepath: Path to decklist file
        exclude_commander: Whether to exclude the commander from results
        commander_name: Commander name to exclude if exclude_commander=True

    Returns:
        Set of card names in the deck
    """
    cards = set()
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"Deck file not found: {filepath}")

    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            card_name = parse_decklist_line(line)
            if card_name:
                if exclude_commander and card_name == commander_name:
                    continue
                cards.add(card_name)

    return cards
