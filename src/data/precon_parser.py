"""Parse MTGJSON deck files and count card appearances."""

import json
from pathlib import Path
from collections import defaultdict


class PreconParser:
    """Parse preconstructed deck files."""

    def parse_all_decks(self, deck_dir: str) -> dict[str, int]:
        """Parse all Commander decks and return card appearance counts.

        Args:
            deck_dir: Directory containing deck JSON files

        Returns:
            Dictionary mapping card names to appearance counts
        """
        counts, _ = self.parse_all_decks_with_total(deck_dir)
        return counts

    def parse_all_decks_with_total(self, deck_dir: str) -> tuple[dict[str, int], int]:
        """Parse all Commander decks and return counts with total deck count.

        Returns:
            Tuple of (card_counts, total_commander_decks)
        """
        deck_path = Path(deck_dir)
        counts = defaultdict(int)
        total_decks = 0

        if not deck_path.exists():
            return dict(counts), 0

        for deck_file in deck_path.glob("*.json"):
            try:
                with open(deck_file, 'r', encoding='utf-8') as f:
                    deck = json.load(f)

                # Only count Commander decks
                if deck.get("type") != "Commander":
                    continue

                total_decks += 1

                # Count mainboard cards
                for card in deck.get("mainBoard", []):
                    name = card.get("name")
                    if name:
                        counts[name] += 1

                # Count commander(s)
                for card in deck.get("commander", []):
                    name = card.get("name")
                    if name:
                        counts[name] += 1

            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not parse {deck_file}: {e}")
                continue

        return dict(counts), total_decks
