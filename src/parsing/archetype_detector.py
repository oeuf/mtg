"""Classify cards into strategic archetypes."""


class ArchetypeDetector:
    """
    Classify cards into archetypes based on mechanical profile.

    Archetypes:
    - combo: Infinite loops, game-winning combinations
    - control: Removal, counterspells, board wipes
    - aggro: Low CMC, creature-based damage
    - midrange: Value engines, card advantage, flexible threats
    - stax: Resource denial, tax effects
    - tribal: Creature type synergies
    - utility: Generic staples (ramp, draw, etc.)
    """

    # Known combo pieces (curated list of infinite combo enablers)
    KNOWN_COMBO_PIECES = {
        "Dramatic Reversal",
        "Isochron Scepter",
        "Mikaeus, the Unhallowed",
        "Walking Ballista",
        "Thassa's Oracle",
        "Demonic Consultation",
        "Underworld Breach",
        "Brain Freeze",
        "Basalt Monolith",
        "Rings of Brighthearth"
    }

    def classify_archetype(self, card: dict, known_combo_pieces: list[str] = None) -> str:
        """
        Classify card into primary archetype.

        Args:
            card: Card dict with themes, mechanics, roles, CMC, etc.
            known_combo_pieces: Optional list of known combo card names

        Returns:
            Archetype string: "combo" | "control" | "aggro" | "midrange" | "stax" | "tribal" | "utility"
        """
        card_name = card.get("name", "")
        cmc = card.get("cmc", 0)
        type_line = card.get("type_line", "")
        themes = card.get("themes", [])
        mechanics = card.get("mechanics", [])
        roles = card.get("functional_categories", [])
        subtypes = card.get("subtypes", [])

        # Use provided combo list or default
        combo_list = known_combo_pieces if known_combo_pieces is not None else self.KNOWN_COMBO_PIECES

        # Rule 1: Known combo pieces
        if card_name in combo_list:
            return "combo"

        # Rule 2: Stax effects
        if "stax" in themes or "tax_effect" in mechanics:
            return "stax"

        # Rule 3: Tribal synergies
        if "tribal" in themes:
            return "tribal"

        # Rule 4: Control (removal heavy)
        if "removal" in roles or "protection" in roles:
            # High density of interaction
            if len([r for r in roles if r in ["removal", "protection"]]) >= 1:
                return "control"

        # Rule 5: Aggro (low CMC creatures)
        if "Creature" in type_line and cmc <= 3:
            # Low CMC aggressive creatures
            if not any(theme in ["graveyard_value", "reanimation", "tokens"] for theme in themes):
                return "aggro"

        # Rule 6: Midrange (value engines)
        graveyard_themes = ["graveyard_value", "reanimation", "aristocrats"]
        value_roles = ["recursion", "card_draw"]

        if any(theme in graveyard_themes for theme in themes):
            return "midrange"

        if len([r for r in roles if r in value_roles]) >= 2:
            return "midrange"

        # Default: Utility (generic staples)
        return "utility"
