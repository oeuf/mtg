"""Unit tests for phase detector."""

import pytest
from src.parsing.phase_detector import PhaseDetector


@pytest.fixture
def detector():
    """Create phase detector instance."""
    return PhaseDetector()


def test_detect_upkeep_phase(detector):
    """Detect upkeep phase triggers."""
    text = "At the beginning of your upkeep, draw a card."
    phases = detector.detect_phases(text)

    assert "upkeep" in phases
    assert phases["upkeep"]["trigger_type"] == "beginning"


def test_detect_end_step_phase(detector):
    """Detect end step triggers."""
    text = "At the beginning of your end step, sacrifice this creature."
    phases = detector.detect_phases(text)

    assert "end_step" in phases
    assert phases["end_step"]["trigger_type"] == "beginning"


def test_detect_combat_phase(detector):
    """Detect combat phase interactions."""
    text = "Whenever this creature attacks, it gets +2/+2 until end of turn."
    phases = detector.detect_phases(text)

    assert "combat" in phases or "declare_attackers" in phases


def test_detect_draw_step(detector):
    """Detect draw step triggers."""
    text = "At the beginning of your draw step, you may draw an additional card."
    phases = detector.detect_phases(text)

    assert "draw" in phases


def test_detect_multiple_phases(detector):
    """Detect multiple phase triggers."""
    text = "At the beginning of your upkeep and at the beginning of your end step, create a token."
    phases = detector.detect_phases(text)

    assert "upkeep" in phases
    assert "end_step" in phases


def test_detect_combat_damage(detector):
    """Detect combat damage step."""
    text = "Whenever this creature deals combat damage to a player, draw a card."
    phases = detector.detect_phases(text)

    assert "combat_damage" in phases or "combat" in phases


def test_no_phases_detected(detector):
    """Return empty dict when no phases mentioned."""
    text = "This creature gets +1/+1 for each artifact you control."
    phases = detector.detect_phases(text)

    assert phases == {}


def test_untap_step(detector):
    """Detect untap step (rare but exists)."""
    text = "At the beginning of your untap step, you may untap target permanent."
    phases = detector.detect_phases(text)

    assert "untap" in phases


def test_case_insensitive_detection(detector):
    """Phase detection should be case insensitive."""
    text = "At the beginning of your UPKEEP, draw a card."
    phases = detector.detect_phases(text)

    assert "upkeep" in phases


def test_trigger_types_are_valid(detector):
    """All trigger types should be valid."""
    text = "At the beginning of your upkeep, draw. Whenever you attack, gain life."
    phases = detector.detect_phases(text)

    valid_types = ["beginning", "end", "during"]
    for phase, data in phases.items():
        assert data["trigger_type"] in valid_types
