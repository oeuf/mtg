"""Test archetype classification."""

import pytest
from src.parsing.archetype_detector import ArchetypeDetector


def test_classify_combo_archetype():
    """Should classify combo pieces as combo archetype."""
    detector = ArchetypeDetector()

    card = {
        "name": "Dramatic Reversal",
        "cmc": 2,
        "themes": [],
        "mechanics": [],
        "functional_categories": [],
        "zone_interactions": []
    }

    # Card is known combo piece (would be in curated list)
    archetype = detector.classify_archetype(card, known_combo_pieces=["Dramatic Reversal"])
    assert archetype == "combo"


def test_classify_control_archetype():
    """Should classify removal/counterspells as control."""
    detector = ArchetypeDetector()

    card = {
        "name": "Counterspell",
        "cmc": 2,
        "themes": [],
        "mechanics": [],
        "functional_categories": ["removal", "protection"],
        "zone_interactions": []
    }

    archetype = detector.classify_archetype(card)
    assert archetype == "control"


def test_classify_aggro_archetype():
    """Should classify low CMC creatures as aggro."""
    detector = ArchetypeDetector()

    card = {
        "name": "Goblin Guide",
        "cmc": 1,
        "type_line": "Creature — Goblin Scout",
        "themes": [],
        "mechanics": [],
        "functional_categories": [],
        "zone_interactions": []
    }

    archetype = detector.classify_archetype(card)
    assert archetype == "aggro"


def test_classify_midrange_archetype():
    """Should classify value engines as midrange."""
    detector = ArchetypeDetector()

    card = {
        "name": "Muldrotha",
        "cmc": 6,
        "type_line": "Legendary Creature — Elemental Avatar",
        "themes": ["graveyard_value", "reanimation"],
        "mechanics": ["recursion"],
        "functional_categories": ["recursion", "card_draw"],
        "zone_interactions": [{"zone": "graveyard", "interaction_type": "reads"}]
    }

    archetype = detector.classify_archetype(card)
    assert archetype == "midrange"


def test_classify_stax_archetype():
    """Should classify tax effects as stax."""
    detector = ArchetypeDetector()

    card = {
        "name": "Thalia, Guardian of Thraben",
        "cmc": 2,
        "themes": ["stax"],
        "mechanics": ["tax_effect"],
        "functional_categories": [],
        "zone_interactions": []
    }

    archetype = detector.classify_archetype(card)
    assert archetype == "stax"


def test_classify_tribal_archetype():
    """Should classify tribal synergies."""
    detector = ArchetypeDetector()

    card = {
        "name": "Goblin Chieftain",
        "cmc": 3,
        "type_line": "Creature — Goblin",
        "themes": ["tribal"],
        "mechanics": [],
        "functional_categories": [],
        "subtypes": ["Goblin"],
        "zone_interactions": []
    }

    archetype = detector.classify_archetype(card)
    assert archetype == "tribal"


def test_classify_utility_archetype():
    """Should classify generic good stuff as utility."""
    detector = ArchetypeDetector()

    card = {
        "name": "Sol Ring",
        "cmc": 1,
        "themes": [],
        "mechanics": [],
        "functional_categories": ["ramp"],
        "zone_interactions": []
    }

    archetype = detector.classify_archetype(card)
    assert archetype == "utility"
