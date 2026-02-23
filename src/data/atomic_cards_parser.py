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

            # Normalize double-faced card names: "X // Y" → "X", "X // X" → "X"
            if " // " in card_name:
                card_name = card_name.split(" // ")[0].strip()

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

        # Deduplicate: after // normalization, front-face name may appear multiple times
        seen: dict[str, dict] = {}
        for card in commander_cards:
            if card["name"] not in seen:
                seen[card["name"]] = card
        commander_cards = list(seen.values())

        print(f"✓ Parsed {len(commander_cards)} Commander-legal cards")
        return commander_cards
