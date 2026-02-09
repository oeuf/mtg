"""Unit tests for rules parser."""

import pytest
from src.parsing.rules_parser import RulesParser


@pytest.fixture
def parser():
    """Create parser instance with actual rules file."""
    return RulesParser("2025-11-14-rules.md")


def test_parse_keyword_abilities(parser):
    """Test parsing keyword abilities from Rule 702."""
    abilities = parser.parse_keyword_abilities()

    # Check we got a reasonable number of abilities
    assert len(abilities) > 100, f"Expected 100+ abilities, got {len(abilities)}"

    # Test specific well-known abilities
    assert "flying" in abilities
    assert abilities["flying"]["rule_number"] == "702.9"
    assert "flying" in abilities["flying"]["definition"].lower()

    assert "first strike" in abilities
    assert abilities["first strike"]["rule_number"] == "702.7"

    assert "haste" in abilities
    assert abilities["haste"]["rule_number"] == "702.10"

    # Check structure
    for name, data in abilities.items():
        assert "definition" in data
        assert "rule_number" in data
        assert "reminder_text" in data
        assert data["rule_number"].startswith("702.")


def test_parse_keyword_actions(parser):
    """Test parsing keyword actions from Rule 701."""
    actions = parser.parse_keyword_actions()

    # Check we got a reasonable number of actions
    assert len(actions) > 30, f"Expected 30+ actions, got {len(actions)}"

    # Test specific well-known actions
    assert "destroy" in actions
    assert actions["destroy"]["rule_number"] == "701.8"

    assert "exile" in actions
    assert actions["exile"]["rule_number"] == "701.13"

    assert "discard" in actions
    assert actions["discard"]["rule_number"] == "701.9"

    # Check structure
    for name, data in actions.items():
        assert "definition" in data
        assert "rule_number" in data
        assert data["rule_number"].startswith("701.")


def test_parse_zones(parser):
    """Test parsing zones from Rules 400-408."""
    zones = parser.parse_zones()

    # Check all 8 zones are present
    assert len(zones) == 8
    expected_zones = ["library", "hand", "battlefield", "graveyard",
                      "stack", "exile", "ante", "command"]
    for zone in expected_zones:
        assert zone in zones

    # Test specific zones
    assert zones["library"]["rule_number"] == "401"
    assert zones["library"]["is_public"] is False
    assert zones["library"]["is_ordered"] is True

    assert zones["graveyard"]["rule_number"] == "404"
    assert zones["graveyard"]["is_public"] is True
    assert zones["graveyard"]["is_ordered"] is True

    assert zones["battlefield"]["rule_number"] == "403"
    assert zones["battlefield"]["is_public"] is True
    assert zones["battlefield"]["is_ordered"] is False

    # Check structure
    for name, data in zones.items():
        assert "rule_number" in data
        assert "is_public" in data
        assert "is_ordered" in data
        assert "description" in data
        assert isinstance(data["is_public"], bool)
        assert isinstance(data["is_ordered"], bool)


def test_parse_phases(parser):
    """Test parsing phases from Rules 500-514."""
    phases = parser.parse_phases()

    # Check we got all phases/steps
    assert len(phases) >= 12

    # Test specific phases/steps
    assert "untap" in phases
    assert phases["untap"]["order"] == 1
    assert phases["untap"]["parent"] == "beginning"
    assert phases["untap"]["is_step"] is True

    assert "upkeep" in phases
    assert phases["upkeep"]["order"] == 2
    assert phases["upkeep"]["parent"] == "beginning"

    assert "combat_damage" in phases
    assert phases["combat_damage"]["parent"] == "combat"

    assert "main_1" in phases
    assert phases["main_1"]["is_step"] is False

    # Check structure
    for name, data in phases.items():
        assert "rule_number" in data
        assert "order" in data
        assert "parent" in data
        assert "is_step" in data
        assert isinstance(data["order"], int)
        assert isinstance(data["is_step"], bool)


def test_parse_commander_rules(parser):
    """Test parsing Commander rules from Rule 903."""
    rules = parser.parse_commander_rules()

    # Check expected values
    assert rules["deck_size"] == 100
    assert rules["starting_life"] == 40
    assert rules["singleton"] is True
    assert rules["commander_tax"] == 2
    assert rules["color_identity_matters"] is True
    assert rules["commander_damage_rule"] == 21
    assert rules["rule_number"] == "903"


def test_parse_all(parser):
    """Test parsing all rules sections."""
    result = parser.parse_all()

    # Check all sections are present
    assert "keyword_abilities" in result
    assert "keyword_actions" in result
    assert "zones" in result
    assert "phases" in result
    assert "commander_rules" in result

    # Verify each section has data
    assert len(result["keyword_abilities"]) > 100
    assert len(result["keyword_actions"]) > 30
    assert len(result["zones"]) == 8
    assert len(result["phases"]) >= 12
    assert result["commander_rules"]["deck_size"] == 100
