"""Detect zone interactions from card oracle text."""

import re


class ZoneDetector:
    """Detect which zones a card interacts with."""

    def __init__(self):
        """Initialize zone detection patterns."""
        self.zone_patterns = {
            "graveyard": {
                "reads": [
                    r"from (?:a |your |their |his or her )?graveyard",
                    r"in (?:a |your |their |his or her )?graveyard"
                ],
                "writes": [
                    r"(?:to|into) (?:a |your |their |his or her )?graveyard",
                    r"put (?:it |them )?into (?:a |your |their )?graveyard"
                ]
            },
            "exile": {
                "moves_to": [
                    r"\bexile\b(?! zone)",
                    r"exiled"
                ],
                "reads": [
                    r"from exile",
                    r"in exile"
                ]
            },
            "library": {
                "reads": [
                    r"search (?:your |their |his or her )?library",
                    r"from (?:your |their )?library",
                    r"top (?:card )?of (?:your |their )?library"
                ],
                "writes": [
                    r"(?:to|into) (?:your |their )?library",
                    r"shuffle"
                ]
            },
            "hand": {
                "reads": [
                    r"from (?:your |their |his or her )?hand",
                    r"discard"
                ],
                "writes": [
                    r"(?:to|into) (?:your |their |his or her )?hand",
                    r"return (?:it |them )?to (?:your |their |its owner's )?hand"
                ]
            },
            "command": {
                "reads": [
                    r"from the command zone",
                    r"your commander"
                ],
                "writes": [
                    r"(?:to|into) the command zone"
                ]
            },
            "battlefield": {
                "reads": [
                    r"from the battlefield"
                ],
                "writes": [
                    r"(?:onto|enters) the battlefield",
                    r"put (?:it |them )?onto the battlefield"
                ]
            }
        }

    def detect_zones(self, oracle_text: str) -> dict[str, dict]:
        """
        Detect zone interactions from oracle text.

        Args:
            oracle_text: The card's oracle text

        Returns:
            Dict mapping zone name to interaction metadata:
            {
                "graveyard": {"interaction_type": "reads"},
                "exile": {"interaction_type": "moves_to"}
            }
        """
        if not oracle_text:
            return {}

        text_lower = oracle_text.lower()
        detected_zones = {}

        for zone_name, interactions in self.zone_patterns.items():
            for interaction_type, patterns in interactions.items():
                for pattern in patterns:
                    if re.search(pattern, text_lower):
                        detected_zones[zone_name] = {
                            "interaction_type": interaction_type
                        }
                        break  # Found this zone, move to next zone
                if zone_name in detected_zones:
                    break  # Already found this zone

        return detected_zones
