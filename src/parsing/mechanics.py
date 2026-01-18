"""Extract mechanics from keywords and oracle text."""

import re


class MechanicExtractor:
    """Extract mechanics from keywords and oracle text."""

    TRIGGERED_ABILITY_PATTERNS = {
        "etb_trigger": r"[Ww]hen .* enters the battlefield",
        "dies_trigger": r"[Ww]hen .* (?:dies|is put into .* graveyard from the battlefield)",
        "attack_trigger": r"[Ww]henever .* attacks?",
        "cast_trigger": r"[Ww]henever (?:you cast|a player casts)",
        "draw_trigger": r"[Ww]henever (?:you draw|a player draws)",
        "sacrifice_trigger": r"[Ww]henever you sacrifice",
    }

    STATIC_ABILITY_PATTERNS = {
        "cost_reduction": r"(?:spells?|cards?) (?:you cast )?(?:cost|costs) \{?\d+\}? less",
        "anthem": r"(?:creatures?|permanents?) you control (?:get|have) \+\d+/\+\d+",
        "tax_effect": r"(?:spells?|abilities) .* (?:cost|costs) \{?\d+\}? more",
    }

    @classmethod
    def extract_mechanics(cls, card_data: dict) -> list[str]:
        """Extract all mechanics from card."""
        mechanics = []

        # 1. Keywords (pre-extracted by MTGJSON)
        keywords = card_data.get("keywords", [])
        mechanics.extend(keywords)

        # 2. Triggered abilities
        oracle_text = card_data.get("oracle_text", "")

        for mechanic, pattern in cls.TRIGGERED_ABILITY_PATTERNS.items():
            if re.search(pattern, oracle_text):
                mechanics.append(mechanic)

        # 3. Static abilities
        for mechanic, pattern in cls.STATIC_ABILITY_PATTERNS.items():
            if re.search(pattern, oracle_text):
                mechanics.append(mechanic)

        return list(set(mechanics))  # Remove duplicates
