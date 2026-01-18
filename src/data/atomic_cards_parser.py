"""Parse MTGJSON AtomicCards.json structure."""

import json


class AtomicCardsParser:
    """Parse MTGJSON AtomicCards.json structure."""

    @staticmethod
    def parse(filepath: str) -> list[dict]:
        """Parse and filter for Commander-legal cards."""

        print("Loading AtomicCards.json...")
        with open(filepath, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        # MTGJSON structure: {"data": {"Card Name": [{card_object}, ...], ...}}
        cards_by_name = raw_data.get("data", {})

        commander_cards = []

        print("Filtering for Commander-legal cards...")
        for card_name, printings in cards_by_name.items():
            # Take first printing as canonical
            canonical = printings[0]

            # Check Commander legality
            legalities = canonical.get("legalities", {})
            if legalities.get("commander") != "Legal":
                continue

            # Extract card data
            card = {
                "name": card_name,
                "mana_cost": canonical.get("manaCost", ""),
                "cmc": canonical.get("manaValue", 0),
                "type_line": canonical.get("type", ""),
                "oracle_text": canonical.get("text", ""),
                "color_identity": canonical.get("colorIdentity", []),
                "colors": canonical.get("colors", []),
                "keywords": canonical.get("keywords", []),
                "is_legendary": "Legendary" in canonical.get("type", ""),
                "is_reserved_list": canonical.get("isReserved", False),
                "can_be_commander": canonical.get("leadershipSkills", {}).get("commander", False),
                "edhrec_rank": canonical.get("edhrecRank"),
            }

            commander_cards.append(card)

        print(f"✓ Parsed {len(commander_cards)} Commander-legal cards")
        return commander_cards
