"""Test subtype extraction from type_line."""

import pytest
from src.parsing.properties import PropertyCalculator


def test_extract_creature_subtypes():
    """Should extract creature subtypes from type_line."""
    calc = PropertyCalculator()

    # Single creature type
    subtypes = calc.extract_subtypes("Legendary Creature — Spirit Dragon")
    assert subtypes == ["Spirit", "Dragon"]

    # Multiple creature types
    subtypes = calc.extract_subtypes("Creature — Human Wizard")
    assert subtypes == ["Human", "Wizard"]

    # Artifact creature
    subtypes = calc.extract_subtypes("Artifact Creature — Golem")
    assert subtypes == ["Golem"]


def test_extract_land_subtypes():
    """Should extract land subtypes."""
    calc = PropertyCalculator()

    subtypes = calc.extract_subtypes("Land — Forest Island")
    assert subtypes == ["Forest", "Island"]

    subtypes = calc.extract_subtypes("Basic Land — Swamp")
    assert subtypes == ["Swamp"]


def test_extract_planeswalker_subtypes():
    """Should extract planeswalker subtypes."""
    calc = PropertyCalculator()

    subtypes = calc.extract_subtypes("Legendary Planeswalker — Jace")
    assert subtypes == ["Jace"]


def test_no_subtypes():
    """Should return empty list for cards without subtypes."""
    calc = PropertyCalculator()

    subtypes = calc.extract_subtypes("Instant")
    assert subtypes == []

    subtypes = calc.extract_subtypes("Enchantment")
    assert subtypes == []


def test_multitype_with_subtypes():
    """Should extract all subtypes from multitype cards."""
    calc = PropertyCalculator()

    # Artifact Creature with subtypes
    subtypes = calc.extract_subtypes("Legendary Artifact Creature — Golem Warrior")
    assert subtypes == ["Golem", "Warrior"]
