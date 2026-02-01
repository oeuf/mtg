"""Extract mechanics from keywords and oracle text."""

import re


class MechanicExtractor:
    """Extract mechanics from keywords and oracle text."""

    # MTGJSON uses abbreviated text like "When this creature enters," not "enters the battlefield"
    TRIGGERED_ABILITY_PATTERNS = {
        "etb_trigger": r"[Ww]hen (?:this|~|it|[A-Z][a-z]+).* enters",
        "dies_trigger": r"(?:[Ww]hen(?:ever)?).* (?:dies|is put into .* graveyard from the battlefield)",
        "attack_trigger": r"[Ww]henever .* attacks?",
        "cast_trigger": r"[Ww]henever (?:you cast|a player casts)",
        "draw_trigger": r"[Ww]henever (?:you draw|a player draws)",
        "discard_trigger": r"[Ww]henever (?:you |a player )?discards?",
        "sacrifice_trigger": r"[Ww]henever you sacrifice",
        "self_mill": r"(?:[Mm]ill|put .* cards? from .* library into .* graveyard)",
    }

    # Patterns for functional mechanics (for Muldrotha synergies)
    FUNCTIONAL_PATTERNS = {
        "recursion": r"[Rr]eturn .* from .* graveyard",
        "sacrifice_outlet": r"[Ss]acrifice (?:a|an|one|another) (?:creature|permanent|artifact|enchantment).*:",
        "exile_mechanic": r"[Ee]xile",
        "life_payment": r"[Pp]ay \d+ life",
    }

    STATIC_ABILITY_PATTERNS = {
        "cost_reduction": r"(?:spells?|cards?) (?:you cast )?(?:cost|costs) .* less",
        "anthem": r"(?:creatures?|permanents?) you control (?:get|have) \+\d+/\+\d+",
        "tax_effect": r"(?:spells?|abilities) .* (?:cost|costs) \{?\d+\}? more",
        "skip_draw": r"[Ss]kip your draw step",
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
            if re.search(pattern, oracle_text, re.IGNORECASE):
                mechanics.append(mechanic)

        # 3. Static abilities
        for mechanic, pattern in cls.STATIC_ABILITY_PATTERNS.items():
            if re.search(pattern, oracle_text, re.IGNORECASE):
                mechanics.append(mechanic)

        # 4. Functional mechanics (recursion, sacrifice outlets, etc.)
        for mechanic, pattern in cls.FUNCTIONAL_PATTERNS.items():
            if re.search(pattern, oracle_text, re.IGNORECASE):
                mechanics.append(mechanic)

        return list(set(mechanics))  # Remove duplicates
