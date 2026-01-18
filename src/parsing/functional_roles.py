"""Parse oracle text to identify functional roles."""

import re


class FunctionalRoleParser:
    """Parse oracle text to identify functional roles."""

    PATTERNS = {
        "ramp": [
            r"search (?:your library|a library) for (?:a|up to \d+).*\bland",
            r"put (?:a|up to \d+).*\bland.*onto the battlefield",
            r"add \{[WUBRGC]\}",
            r"(?:add|adds) [WUBRGC] to your mana pool",
            r"add .*mana",
        ],
        "card_draw": [
            r"draw (?:a|an|\d+|X) cards?",
            r"draw cards equal to",
            r"draws? (?:a|an|\d+) cards?",
        ],
        "removal": [
            r"destroy target (?:creature|permanent|artifact|enchantment)",
            r"exile target (?:creature|permanent|artifact|enchantment)",
            r"return target .* to (?:its owner's|their owner's) hand",
            r"(?:put|puts) target .* on (?:top|bottom) of (?:its|their) owner's library",
            r"-X/-X",
            r"destroy all creatures",
            r"exile all creatures",
        ],
        "counterspell": [
            r"counter target spell",
            r"counter (?:target )?(noncreature |instant |sorcery )?spell",
        ],
        "tutor": [
            r"search (?:your library|a library) for a card",
            r"search (?:your library|a library) for (?:a|an|up to \d+) (?:creature|instant|sorcery|artifact|enchantment|planeswalker)",
        ],
        "recursion": [
            r"return (?:target )?.*from (?:your|a|an) graveyard",
            r"return (?:target )?.*card from your graveyard to",
            r"put .*from your graveyard onto the battlefield",
        ],
        "token_generation": [
            r"create (?:a|an|\d+|X|one|two|three) .*tokens?",
            r"(?:put|puts) (?:a|an|\d+|X) .*tokens? onto the battlefield",
        ],
        "sacrifice_outlet": [
            r"sacrifice (?:a|an|one) (?:creature|permanent|artifact|enchantment)",
            r"sac a creature",
        ],
        "protection": [
            r"\bhexproof\b",
            r"\bindestructible\b",
            r"\bprotection from\b",
            r"\bshroud\b",
            r"\bward\b",
        ],
        "win_condition": [
            r"you win the game",
            r"(?:target player|each opponent) loses the game",
            r"(?:target player's?|each opponent's?) life total becomes",
        ],
    }

    @classmethod
    def identify_roles(cls, oracle_text: str) -> list[str]:
        """Return list of functional roles this card fills."""
        if not oracle_text:
            return []

        roles = []
        oracle_lower = oracle_text.lower()

        for role, patterns in cls.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, oracle_lower):
                    roles.append(role)
                    break  # Don't double-count same role

        return roles
