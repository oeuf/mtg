"""Parse MTGJSON RelatedCards.json."""

import json


class RelatedCardsParser:
    """Parse MTGJSON RelatedCards.json."""

    @staticmethod
    def parse(filepath: str) -> dict:
        """Parse RelatedCards.json structure."""

        print("Loading RelatedCards.json...")
        with open(filepath, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        # Structure: {"data": {"Card Name": {...}, ...}}
        related_data = raw_data.get("data", {})

        print(f"✓ Loaded relationships for {len(related_data)} cards")
        return related_data
