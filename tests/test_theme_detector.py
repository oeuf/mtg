"""Test theme detection from card properties."""

import pytest
from src.parsing.theme_detector import ThemeDetector


def test_detect_reanimation_theme():
    """Should detect reanimation theme."""
    detector = ThemeDetector()

    card = {
        "oracle_text": "Return target creature card from your graveyard to the battlefield.",
        "functional_categories": ["recursion"],
        "mechanics": ["recursion"],
        "zone_interactions": [
            {"zone": "graveyard", "interaction_type": "reads"},
            {"zone": "battlefield", "interaction_type": "writes"}
        ]
    }

    themes = detector.detect_themes(card)
    assert "reanimation" in themes


def test_detect_aristocrats_theme():
    """Should detect aristocrats (sacrifice + death triggers) theme."""
    detector = ThemeDetector()

    card = {
        "oracle_text": "Whenever a creature dies, each opponent loses 1 life.",
        "functional_categories": [],
        "mechanics": ["dies_trigger"],
        "zone_interactions": []
    }

    themes = detector.detect_themes(card)
    assert "aristocrats" in themes


def test_detect_token_theme():
    """Should detect token generation theme."""
    detector = ThemeDetector()

    card = {
        "oracle_text": "Create two 1/1 white Soldier creature tokens.",
        "functional_categories": ["token_generation"],
        "mechanics": ["token_generation"],
        "zone_interactions": []
    }

    themes = detector.detect_themes(card)
    assert "tokens" in themes


def test_detect_ramp_theme():
    """Should detect ramp/lands matter theme."""
    detector = ThemeDetector()

    card = {
        "oracle_text": "Search your library for a Forest card.",
        "functional_categories": ["ramp"],
        "mechanics": [],
        "zone_interactions": [
            {"zone": "library", "interaction_type": "reads"}
        ]
    }

    themes = detector.detect_themes(card)
    assert "lands_matter" in themes


def test_detect_spellslinger_theme():
    """Should detect spellslinger theme."""
    detector = ThemeDetector()

    card = {
        "oracle_text": "Whenever you cast an instant or sorcery spell, create a token.",
        "functional_categories": [],
        "mechanics": ["cast_trigger"],
        "zone_interactions": []
    }

    themes = detector.detect_themes(card)
    assert "spellslinger" in themes


def test_detect_multiple_themes():
    """Should detect multiple themes on one card."""
    detector = ThemeDetector()

    card = {
        "oracle_text": "When this creature dies, return another target creature from your graveyard to your hand.",
        "functional_categories": ["recursion"],
        "mechanics": ["dies_trigger", "recursion"],
        "zone_interactions": [
            {"zone": "graveyard", "interaction_type": "reads"}
        ]
    }

    themes = detector.detect_themes(card)
    assert "aristocrats" in themes
    assert "graveyard_value" in themes
