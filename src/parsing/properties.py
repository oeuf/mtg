"""Calculate derived properties from card data."""

import re


class PropertyCalculator:
    """Calculate derived properties from card data."""

    @staticmethod
    def calculate_mana_efficiency(card: dict) -> float:
        """Heuristic: more effects per CMC = higher efficiency."""
        cmc = card.get("cmc", 0)

        if cmc == 0:
            return 1.0  # Free spells are maximally efficient

        # Count functional roles
        role_count = len(card.get("functional_categories", []))

        # Count keywords
        keyword_count = len(card.get("keywords", []))

        # Simple heuristic: (roles + 0.5*keywords) / (CMC + 1)
        efficiency = (role_count + keyword_count * 0.5) / (cmc + 1)

        return min(efficiency, 1.0)  # Cap at 1.0

    @staticmethod
    def count_color_pips(mana_cost: str) -> int:
        """Count colored mana symbols in cost."""
        if not mana_cost:
            return 0

        # Count {W}, {U}, {B}, {R}, {G} symbols
        colored_pips = re.findall(r'\{[WUBRG]\}', mana_cost)
        return len(colored_pips)

    @staticmethod
    def is_fast_mana(card: dict) -> bool:
        """Determine if card is fast mana (produces mana, low CMC)."""
        cmc = card.get("cmc", 0)
        oracle_text = card.get("oracle_text", "")

        if cmc > 2:
            return False

        # Check if produces mana
        produces_mana = bool(re.search(
            r"add \{[WUBRGC]\}",
            oracle_text,
            re.IGNORECASE
        ))

        return produces_mana

    @staticmethod
    def is_free_spell(card: dict) -> bool:
        """Check for alternative casting costs."""
        oracle_text = card.get("oracle_text", "")

        patterns = [
            r"you may .* rather than pay",
            r"if .* you may cast .* without paying",
            r"pitch",  # Pitch spells (Force of Will, etc.)
            r"alternate cost",
        ]

        for pattern in patterns:
            if re.search(pattern, oracle_text, re.IGNORECASE):
                return True

        return False
