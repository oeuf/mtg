"""Detect phase/step triggers from card oracle text."""

import re


class PhaseDetector:
    """Detect which phases/steps a card triggers in."""

    def __init__(self):
        """Initialize phase detection patterns."""
        self.phase_patterns = {
            "untap": {
                "beginning": [
                    r"at the beginning of (?:your |each |the )?untap"
                ]
            },
            "upkeep": {
                "beginning": [
                    r"at the beginning of (?:your |each |the )?upkeep"
                ],
                "end": [
                    r"at the end of (?:your |each )?upkeep"
                ]
            },
            "draw": {
                "beginning": [
                    r"at the beginning of (?:your |each |the )?draw step"
                ]
            },
            "combat": {
                "during": [
                    r"whenever .* attacks",
                    r"whenever .* blocks",
                    r"when .* attacks",
                    r"when .* blocks"
                ]
            },
            "declare_attackers": {
                "during": [
                    r"whenever .* attacks",
                    r"when .* attacks"
                ]
            },
            "combat_damage": {
                "during": [
                    r"whenever .* deals combat damage",
                    r"when .* deals combat damage"
                ]
            },
            "end_step": {
                "beginning": [
                    r"at the beginning of (?:your |each |the )?end step",
                    r"at the beginning of (?:your |each |the )?next end step"
                ],
                "end": [
                    r"at end of turn",
                    r"until end of turn"
                ]
            }
        }

    def detect_phases(self, oracle_text: str) -> dict[str, dict]:
        """
        Detect phase/step triggers from oracle text.

        Args:
            oracle_text: The card's oracle text

        Returns:
            Dict mapping phase/step name to trigger metadata:
            {
                "upkeep": {"trigger_type": "beginning"},
                "combat": {"trigger_type": "during"}
            }
        """
        if not oracle_text:
            return {}

        text_lower = oracle_text.lower()
        detected_phases = {}

        for phase_name, triggers in self.phase_patterns.items():
            for trigger_type, patterns in triggers.items():
                for pattern in patterns:
                    if re.search(pattern, text_lower):
                        detected_phases[phase_name] = {
                            "trigger_type": trigger_type
                        }
                        break  # Found this phase, move to next phase
                if phase_name in detected_phases:
                    break  # Already found this phase

        return detected_phases
