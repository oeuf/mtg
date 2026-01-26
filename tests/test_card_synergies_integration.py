"""Integration tests for CardSynergyEngine with enhanced scoring."""

import pytest
from src.synergy.card_synergies import CardSynergyEngine


def test_compute_synergy_score_high_mechanic_overlap():
    """Test synergy scoring with high mechanic overlap."""
    engine = CardSynergyEngine()

    card1 = {
        "mechanics": ["etb_trigger", "recursion", "self_mill"],
        "functional_categories": ["etb_trigger"],
        "themes": ["reanimation"],
        "color_identity": ["B", "G"],
        "subtypes": ["Elf"],
        "type_line": "Creature — Elf Shaman",
        "zone_interactions": [{"zone": "graveyard", "interaction_type": "writes"}],
        "phase_triggers": [{"phase": "upkeep"}]
    }

    card2 = {
        "mechanics": ["etb_trigger", "recursion"],
        "functional_categories": ["sacrifice_outlet"],
        "themes": ["reanimation", "graveyard_value"],
        "color_identity": ["B", "G"],
        "subtypes": ["Elf"],
        "type_line": "Creature — Elf Cleric",
        "zone_interactions": [{"zone": "graveyard", "interaction_type": "reads"}],
        "phase_triggers": [{"phase": "upkeep"}]
    }

    score, details = engine.compute_synergy_score(card1, card2)

    # Should score high due to multiple synergies
    assert score > 0.5
    assert "final_score" in details
    assert details["mechanic_overlap"]["score"] > 0
    assert details["role_compatibility"]["score"] > 0  # etb_trigger + sacrifice_outlet
    assert details["theme_alignment"]["score"] > 0
    assert details["zone_chain"]["score"] > 0  # write -> read
    assert details["phase_alignment"]["score"] > 0
    assert details["color_compatibility"]["score"] == 1.0  # exact match
    assert details["type_synergy"]["score"] > 0  # shared Elf subtype


def test_compute_synergy_score_low_overlap():
    """Test synergy scoring with minimal overlap."""
    engine = CardSynergyEngine()

    card1 = {
        "mechanics": ["flying", "vigilance"],
        "functional_categories": ["ramp"],
        "themes": ["tokens"],
        "color_identity": ["W", "U"],
        "subtypes": ["Angel"],
        "type_line": "Creature — Angel",
        "zone_interactions": [],
        "phase_triggers": []
    }

    card2 = {
        "mechanics": ["trample", "haste"],
        "functional_categories": ["removal"],
        "themes": ["burn"],
        "color_identity": ["R", "G"],
        "subtypes": ["Dragon"],
        "type_line": "Creature — Dragon",
        "zone_interactions": [],
        "phase_triggers": []
    }

    score, details = engine.compute_synergy_score(card1, card2)

    # Should score low due to minimal synergies
    assert score < 0.3
    assert details["mechanic_overlap"]["score"] == 0
    assert details["role_compatibility"]["score"] == 0
    assert details["theme_alignment"]["score"] == 0
    assert details["zone_chain"]["score"] == 0
    assert details["phase_alignment"]["score"] == 0
    assert details["color_compatibility"]["score"] == 0.3  # disjoint colors


def test_compute_synergy_score_role_complementarity():
    """Test that complementary roles boost score."""
    engine = CardSynergyEngine()

    card1 = {
        "mechanics": ["etb_trigger"],
        "functional_categories": ["etb_trigger"],
        "themes": ["blink"],
        "color_identity": ["U"],
        "subtypes": [],
        "type_line": "Creature — Human Wizard",
        "zone_interactions": [],
        "phase_triggers": []
    }

    card2 = {
        "mechanics": ["sacrifice"],
        "functional_categories": ["sacrifice_outlet"],
        "themes": ["aristocrats"],
        "color_identity": ["B"],
        "subtypes": [],
        "type_line": "Enchantment",
        "zone_interactions": [],
        "phase_triggers": []
    }

    score, details = engine.compute_synergy_score(card1, card2)

    # Role compatibility should be high (0.9 from ROLE_COMPATIBILITY)
    assert details["role_compatibility"]["score"] == 0.9
    assert details["role_compatibility"]["info"]["best_pair"] == ("etb_trigger", "sacrifice_outlet")


def test_compute_synergy_score_zone_chains():
    """Test zone interaction chains."""
    engine = CardSynergyEngine()

    card1 = {
        "mechanics": ["self_mill"],
        "functional_categories": ["self_mill"],
        "themes": ["graveyard_value"],
        "color_identity": ["G"],
        "subtypes": [],
        "type_line": "Sorcery",
        "zone_interactions": [{"zone": "graveyard", "interaction_type": "writes"}],
        "phase_triggers": []
    }

    card2 = {
        "mechanics": ["recursion"],
        "functional_categories": ["recursion"],
        "themes": ["reanimation"],
        "color_identity": ["B"],
        "subtypes": [],
        "type_line": "Creature — Zombie",
        "zone_interactions": [{"zone": "graveyard", "interaction_type": "reads"}],
        "phase_triggers": []
    }

    score, details = engine.compute_synergy_score(card1, card2)

    # Zone chain should be detected (write -> read)
    assert details["zone_chain"]["score"] == 0.8
    assert details["zone_chain"]["info"]["chains"][0]["type"] == "write_read"
    assert details["zone_chain"]["info"]["chains"][0]["zone"] == "graveyard"


def test_compute_synergy_score_empty_cards():
    """Test handling of cards with minimal data."""
    engine = CardSynergyEngine()

    card1 = {
        "mechanics": [],
        "functional_categories": [],
        "themes": [],
        "color_identity": [],
        "subtypes": [],
        "type_line": "Land",
        "zone_interactions": [],
        "phase_triggers": []
    }

    card2 = {
        "mechanics": ["etb_trigger"],
        "functional_categories": ["card_draw"],
        "themes": ["spellslinger"],
        "color_identity": ["U"],
        "subtypes": [],
        "type_line": "Creature — Wizard",
        "zone_interactions": [],
        "phase_triggers": []
    }

    score, details = engine.compute_synergy_score(card1, card2)

    # Should still compute without errors
    assert score >= 0
    assert "final_score" in details


def test_init_creates_scorers():
    """Test that CardSynergyEngine initializes with FeatureScorers."""
    engine = CardSynergyEngine()

    assert hasattr(engine, 'scorers')
    assert engine.scorers is not None
