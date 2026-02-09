"""Unit tests for zone detector."""

import pytest
from src.parsing.zone_detector import ZoneDetector


@pytest.fixture
def detector():
    """Create zone detector instance."""
    return ZoneDetector()


def test_detect_graveyard_zone(detector):
    """Detect graveyard zone interactions."""
    text = "When this creature dies, return it to your hand from your graveyard."
    zones = detector.detect_zones(text)

    assert "graveyard" in zones
    assert zones["graveyard"]["interaction_type"] == "reads"


def test_detect_exile_zone(detector):
    """Detect exile zone interactions."""
    text = "Exile target creature. Its controller may cast it from exile."
    zones = detector.detect_zones(text)

    assert "exile" in zones
    assert "writes" in zones["exile"]["interaction_type"] or "moves_to" in zones["exile"]["interaction_type"]


def test_detect_library_zone(detector):
    """Detect library zone interactions."""
    text = "Search your library for a basic land card and put it onto the battlefield."
    zones = detector.detect_zones(text)

    assert "library" in zones
    assert zones["library"]["interaction_type"] == "reads"


def test_detect_hand_zone(detector):
    """Detect hand zone interactions."""
    text = "Discard a card from your hand to draw three cards."
    zones = detector.detect_zones(text)

    assert "hand" in zones


def test_detect_command_zone(detector):
    """Detect command zone interactions."""
    text = "You may cast your commander from the command zone."
    zones = detector.detect_zones(text)

    assert "command" in zones


def test_detect_multiple_zones(detector):
    """Detect multiple zone interactions in one text."""
    text = "Exile target card from a graveyard. Search your library for a card."
    zones = detector.detect_zones(text)

    assert "exile" in zones
    assert "graveyard" in zones
    assert "library" in zones


def test_no_zones_detected(detector):
    """Return empty dict when no zones mentioned."""
    text = "This creature gets +1/+1 until end of turn."
    zones = detector.detect_zones(text)

    assert zones == {}


def test_battlefield_zone_implicit(detector):
    """Battlefield is implicit, not usually detected from text."""
    text = "Put a +1/+1 counter on target creature."
    zones = detector.detect_zones(text)

    # Battlefield not explicitly mentioned in most card text
    assert "battlefield" not in zones or len(zones) == 0


def test_case_insensitive_detection(detector):
    """Zone detection should be case insensitive."""
    text = "EXILE target creature. Search your LIBRARY."
    zones = detector.detect_zones(text)

    assert "exile" in zones
    assert "library" in zones


def test_interaction_types_are_valid(detector):
    """All interaction types should be valid."""
    text = "Exile a card from your graveyard. Search your library."
    zones = detector.detect_zones(text)

    valid_types = ["reads", "writes", "moves_to", "moves_from"]
    for zone, data in zones.items():
        assert data["interaction_type"] in valid_types
