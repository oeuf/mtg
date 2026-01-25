"""Detect high-level strategy themes from card properties."""

import re


class ThemeDetector:
    """
    Detect strategy themes from card mechanics, roles, and text.

    Themes are higher-level than mechanics and represent strategic archetypes:
    - reanimation: Returning creatures from graveyard to battlefield
    - aristocrats: Sacrifice outlets + death triggers
    - tokens: Token generation and payoffs
    - lands_matter: Landfall, ramp, land recursion
    - spellslinger: Cast triggers, instants/sorceries matter
    - tribal: Creature type synergies
    - voltron: Commander damage, equipment, auras
    - stax: Resource denial, tax effects
    - combo: Infinite loops, game-winning combinations
    """

    # Theme detection rules
    THEME_PATTERNS = {
        "reanimation": {
            "mechanics": ["recursion"],
            "roles": ["recursion"],
            "text_patterns": [
                r"return.*creature.*from.*graveyard.*battlefield",
                r"put.*creature.*from.*graveyard.*battlefield"
            ],
            "zones": [("graveyard", "reads"), ("battlefield", "writes")]
        },
        "aristocrats": {
            "mechanics": ["dies_trigger", "sacrifice_trigger", "sacrifice_outlet"],
            "roles": [],
            "text_patterns": [
                r"whenever.*creature.*dies",
                r"when.*dies",
                r"sacrifice.*creature"
            ],
            "zones": []
        },
        "tokens": {
            "mechanics": ["token_generation"],
            "roles": ["token_generation"],
            "text_patterns": [
                r"create.*token",
                r"creature tokens?"
            ],
            "zones": []
        },
        "lands_matter": {
            "mechanics": [],
            "roles": ["ramp"],
            "text_patterns": [
                r"search.*library.*land",
                r"landfall",
                r"play.*additional.*land",
                r"put.*land.*battlefield"
            ],
            "zones": [("library", "reads")]
        },
        "spellslinger": {
            "mechanics": ["cast_trigger"],
            "roles": [],
            "text_patterns": [
                r"whenever.*cast.*instant.*sorcery",
                r"instant.*sorcery.*cost.*less",
                r"copy.*instant.*sorcery"
            ],
            "zones": []
        },
        "graveyard_value": {
            "mechanics": ["recursion", "self_mill"],
            "roles": ["recursion"],
            "text_patterns": [
                r"from.*graveyard",
                r"in.*graveyard"
            ],
            "zones": [("graveyard", "reads")]
        },
        "lifegain": {
            "mechanics": [],
            "roles": [],
            "text_patterns": [
                r"gain.*life",
                r"whenever.*gain.*life",
                r"lifelink"
            ],
            "zones": []
        },
        "tribal": {
            "mechanics": [],
            "roles": [],
            "text_patterns": [
                r"(?:Elf|Goblin|Zombie|Dragon|Angel|Demon|Vampire|Wizard|Soldier|Merfolk).*you control",
                r"other.*(?:Elf|Goblin|Zombie|Dragon|Angel|Demon|Vampire|Wizard|Soldier|Merfolk)"
            ],
            "zones": []
        },
        "voltron": {
            "mechanics": [],
            "roles": ["protection"],
            "text_patterns": [
                r"equipped creature",
                r"attach.*equipment",
                r"aura.*you control",
                r"commander damage"
            ],
            "zones": []
        },
        "stax": {
            "mechanics": ["tax_effect"],
            "roles": [],
            "text_patterns": [
                r"costs?.*more",
                r"can't.*unless",
                r"players? can't"
            ],
            "zones": []
        }
    }

    def detect_themes(self, card: dict) -> list[str]:
        """
        Detect all themes present on a card.

        Args:
            card: Card dict with mechanics, functional_categories, oracle_text, zone_interactions

        Returns:
            List of theme names (e.g., ["reanimation", "graveyard_value"])
        """
        themes = []

        oracle_text = card.get("oracle_text", "").lower()
        mechanics = card.get("mechanics", [])
        roles = card.get("functional_categories", [])
        zone_interactions = card.get("zone_interactions", [])

        for theme_name, rules in self.THEME_PATTERNS.items():
            matched = False

            # Check mechanics
            if rules["mechanics"]:
                if any(m in mechanics for m in rules["mechanics"]):
                    matched = True

            # Check roles
            if rules["roles"]:
                if any(r in roles for r in rules["roles"]):
                    matched = True

            # Check text patterns
            if rules["text_patterns"]:
                for pattern in rules["text_patterns"]:
                    if re.search(pattern, oracle_text, re.IGNORECASE):
                        matched = True
                        break

            # Check zones
            if rules["zones"]:
                for zone_name, interaction_type in rules["zones"]:
                    for zi in zone_interactions:
                        if zi["zone"] == zone_name and zi["interaction_type"] == interaction_type:
                            matched = True
                            break

            if matched:
                themes.append(theme_name)

        return themes
