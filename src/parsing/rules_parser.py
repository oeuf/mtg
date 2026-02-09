"""Parse MTG Comprehensive Rules into structured dictionaries."""

import re
from pathlib import Path


class RulesParser:
    """Parse comprehensive MTG rules into structured data."""

    def __init__(self, rules_file_path: str):
        """Initialize parser with rules file path."""
        self.rules_file_path = Path(rules_file_path)
        self.rules_text = self._load_rules()

    def _load_rules(self) -> str:
        """Load rules file content."""
        with open(self.rules_file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def parse_keyword_abilities(self) -> dict[str, dict]:
        """
        Parse keyword abilities from Rule 702.

        Returns dict mapping keyword name to:
        - definition: str
        - rule_number: str
        - reminder_text: str (if available)
        """
        keyword_abilities = {}

        # Find Rule 702 section
        rule_702_pattern = r'^702\.(\d+)\.\s+(.+?)$'
        definition_pattern = r'^702\.\d+[a-z]\s+(.+?)$'

        lines = self.rules_text.split('\n')
        current_keyword = None
        current_rule_num = None

        for i, line in enumerate(lines):
            # Match keyword ability header (e.g., "702.9. Flying")
            keyword_match = re.match(rule_702_pattern, line)
            if keyword_match:
                rule_num = keyword_match.group(1)
                keyword_name = keyword_match.group(2).strip()
                current_keyword = keyword_name.lower()
                current_rule_num = f"702.{rule_num}"

                # Look ahead for definition
                definition = ""
                reminder = ""

                # Check next few lines for definition
                for j in range(i + 1, min(i + 10, len(lines))):
                    next_line = lines[j].strip()

                    # Stop at next keyword or major section
                    if re.match(r'^702\.\d+\.\s+[A-Z]', next_line):
                        break
                    if re.match(r'^###\s+', next_line):
                        break

                    # Extract definition from subrule a
                    def_match = re.match(definition_pattern, next_line)
                    if def_match and not definition:
                        definition = def_match.group(1).strip()

                        # Extract reminder text if present in quotes
                        reminder_match = re.search(r'"([^"]+)"', definition)
                        if reminder_match:
                            reminder = reminder_match.group(1)

                if current_keyword and definition:
                    keyword_abilities[current_keyword] = {
                        "definition": definition,
                        "rule_number": current_rule_num,
                        "reminder_text": reminder
                    }

        return keyword_abilities

    def parse_keyword_actions(self) -> dict[str, dict]:
        """
        Parse keyword actions from Rule 701.

        Returns dict mapping action name to:
        - definition: str
        - rule_number: str
        """
        keyword_actions = {}

        # Find Rule 701 section
        rule_701_pattern = r'^701\.(\d+)\.\s+(.+?)$'
        definition_pattern = r'^701\.\d+[a-z]\s+(.+?)$'

        lines = self.rules_text.split('\n')
        current_action = None
        current_rule_num = None

        for i, line in enumerate(lines):
            # Match keyword action header (e.g., "701.18. Scry")
            action_match = re.match(rule_701_pattern, line)
            if action_match:
                rule_num = action_match.group(1)
                action_name = action_match.group(2).strip()
                current_action = action_name.lower()
                current_rule_num = f"701.{rule_num}"

                # Look ahead for definition
                definition = ""

                # Check next few lines for definition
                for j in range(i + 1, min(i + 10, len(lines))):
                    next_line = lines[j].strip()

                    # Stop at next action or major section
                    if re.match(r'^701\.\d+\.\s+[A-Z]', next_line):
                        break
                    if re.match(r'^###\s+', next_line):
                        break

                    # Extract definition from subrule a
                    def_match = re.match(definition_pattern, next_line)
                    if def_match and not definition:
                        definition = def_match.group(1).strip()

                if current_action and definition:
                    keyword_actions[current_action] = {
                        "definition": definition,
                        "rule_number": current_rule_num
                    }

        return keyword_actions

    def parse_zones(self) -> dict[str, dict]:
        """
        Parse zones from Rules 400-408.

        Returns dict mapping zone name to:
        - rule_number: str
        - is_public: bool
        - is_ordered: bool
        - description: str
        """
        zones = {}

        # Define zones based on rules
        zone_rules = {
            "library": {"rule": "401", "public": False, "ordered": True},
            "hand": {"rule": "402", "public": False, "ordered": False},
            "battlefield": {"rule": "403", "public": True, "ordered": False},
            "graveyard": {"rule": "404", "public": True, "ordered": True},
            "stack": {"rule": "405", "public": True, "ordered": True},
            "exile": {"rule": "406", "public": True, "ordered": False},
            "ante": {"rule": "407", "public": True, "ordered": False},
            "command": {"rule": "408", "public": True, "ordered": False}
        }

        for zone_name, props in zone_rules.items():
            # Find description from rules
            rule_pattern = rf'^{props["rule"]}\.1\.\s+(.+?)$'

            description = ""
            for line in self.rules_text.split('\n'):
                match = re.match(rule_pattern, line)
                if match:
                    description = match.group(1).strip()
                    break

            zones[zone_name] = {
                "rule_number": props["rule"],
                "is_public": props["public"],
                "is_ordered": props["ordered"],
                "description": description
            }

        return zones

    def parse_phases(self) -> dict[str, dict]:
        """
        Parse phases and steps from Rules 500-514.

        Returns dict mapping phase/step name to:
        - rule_number: str
        - order: int
        - parent: str (for steps)
        - is_step: bool
        """
        phases = {}

        # Define phases and steps based on turn structure
        phase_data = [
            # Beginning phase (501)
            {"name": "untap", "rule": "502", "order": 1, "parent": "beginning", "is_step": True},
            {"name": "upkeep", "rule": "503", "order": 2, "parent": "beginning", "is_step": True},
            {"name": "draw", "rule": "504", "order": 3, "parent": "beginning", "is_step": True},

            # Main phases
            {"name": "main_1", "rule": "505", "order": 4, "parent": None, "is_step": False},

            # Combat phase (506)
            {"name": "beginning_of_combat", "rule": "507", "order": 5, "parent": "combat", "is_step": True},
            {"name": "declare_attackers", "rule": "508", "order": 6, "parent": "combat", "is_step": True},
            {"name": "declare_blockers", "rule": "509", "order": 7, "parent": "combat", "is_step": True},
            {"name": "combat_damage", "rule": "510", "order": 8, "parent": "combat", "is_step": True},
            {"name": "end_of_combat", "rule": "511", "order": 9, "parent": "combat", "is_step": True},

            # Postcombat main
            {"name": "main_2", "rule": "505", "order": 10, "parent": None, "is_step": False},

            # Ending phase (512)
            {"name": "end_step", "rule": "513", "order": 11, "parent": "ending", "is_step": True},
            {"name": "cleanup", "rule": "514", "order": 12, "parent": "ending", "is_step": True}
        ]

        for phase_info in phase_data:
            phases[phase_info["name"]] = {
                "rule_number": phase_info["rule"],
                "order": phase_info["order"],
                "parent": phase_info["parent"],
                "is_step": phase_info["is_step"]
            }

        return phases

    def parse_commander_rules(self) -> dict:
        """
        Parse Commander format rules from Rule 903.

        Returns dict with:
        - deck_size: int
        - starting_life: int
        - singleton: bool
        - commander_tax: int
        - color_identity_matters: bool
        - commander_damage_rule: int
        """
        commander_rules = {
            "deck_size": 100,
            "starting_life": 40,
            "singleton": True,
            "commander_tax": 2,
            "color_identity_matters": True,
            "commander_damage_rule": 21,
            "rule_number": "903"
        }

        # Extract from Rule 903.5a, 903.7, 903.8, 903.10a
        patterns = {
            "deck_size": r'903\.5a.+exactly\s+(\d+)\s+cards',
            "starting_life": r'903\.7.+life total to\s+(\d+)',
            "commander_tax": r'903\.8.+additional\s+\{(\d+)\}',
            "commander_damage": r'903\.10a.+dealt\s+(\d+)\s+or more combat damage'
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, self.rules_text)
            if match:
                value = int(match.group(1))
                if key == "commander_damage":
                    commander_rules["commander_damage_rule"] = value
                else:
                    commander_rules[key] = value

        return commander_rules

    def parse_all(self) -> dict:
        """
        Parse all rules sections.

        Returns dict with:
        - keyword_abilities: dict
        - keyword_actions: dict
        - zones: dict
        - phases: dict
        - commander_rules: dict
        """
        print("Parsing MTG Comprehensive Rules...")

        print("  Parsing keyword abilities (Rule 702)...")
        keyword_abilities = self.parse_keyword_abilities()
        print(f"    Found {len(keyword_abilities)} keyword abilities")

        print("  Parsing keyword actions (Rule 701)...")
        keyword_actions = self.parse_keyword_actions()
        print(f"    Found {len(keyword_actions)} keyword actions")

        print("  Parsing zones (Rules 400-408)...")
        zones = self.parse_zones()
        print(f"    Found {len(zones)} zones")

        print("  Parsing phases (Rules 500-514)...")
        phases = self.parse_phases()
        print(f"    Found {len(phases)} phases/steps")

        print("  Parsing Commander rules (Rule 903)...")
        commander_rules = self.parse_commander_rules()

        print("✓ Rules parsing complete")

        return {
            "keyword_abilities": keyword_abilities,
            "keyword_actions": keyword_actions,
            "zones": zones,
            "phases": phases,
            "commander_rules": commander_rules
        }
