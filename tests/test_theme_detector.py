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


def test_detect_draw_engines_theme():
    """Should detect draw engines theme."""
    detector = ThemeDetector()
    card = {
        "oracle_text": "Whenever a creature enters the battlefield, draw a card.",
        "functional_categories": ["card_draw"],
        "mechanics": ["etb_trigger"],
        "zone_interactions": []
    }
    themes = detector.detect_themes(card)
    assert "draw_engines" in themes


def test_detect_blink_theme():
    """Should detect blink (flicker) theme."""
    detector = ThemeDetector()
    card = {
        "oracle_text": "Exile target creature, then return it to the battlefield under your control.",
        "functional_categories": [],
        "mechanics": [],
        "zone_interactions": [
            {"zone": "exile", "interaction_type": "writes"},
            {"zone": "battlefield", "interaction_type": "writes"}
        ]
    }
    themes = detector.detect_themes(card)
    assert "blink" in themes


def test_detect_counters_theme():
    """Should detect +1/+1 counters theme."""
    detector = ThemeDetector()
    card = {
        "oracle_text": "Put two +1/+1 counters on target creature.",
        "functional_categories": [],
        "mechanics": [],
        "zone_interactions": []
    }
    themes = detector.detect_themes(card)
    assert "counters" in themes


def test_detect_storm_theme():
    """Should detect storm/spell copy theme."""
    detector = ThemeDetector()
    card = {
        "oracle_text": "Copy target instant or sorcery spell. You may choose new targets.",
        "functional_categories": [],
        "mechanics": [],
        "zone_interactions": []
    }
    themes = detector.detect_themes(card)
    assert "storm" in themes


def test_detect_artifacts_matter_theme():
    """Should detect artifacts matter theme."""
    detector = ThemeDetector()
    card = {
        "oracle_text": "Whenever an artifact enters the battlefield under your control, draw a card.",
        "functional_categories": [],
        "mechanics": [],
        "zone_interactions": []
    }
    themes = detector.detect_themes(card)
    assert "artifacts_matter" in themes


def test_detect_enchantments_matter_theme():
    """Should detect enchantments matter theme."""
    detector = ThemeDetector()
    card = {
        "oracle_text": "Constellation — Whenever an enchantment enters the battlefield, gain 2 life.",
        "functional_categories": [],
        "mechanics": [],
        "zone_interactions": []
    }
    themes = detector.detect_themes(card)
    assert "enchantments_matter" in themes


def test_detect_group_hug_theme():
    """Should detect group hug theme."""
    detector = ThemeDetector()
    card = {
        "oracle_text": "At the beginning of each player's draw step, that player draws an additional card.",
        "functional_categories": [],
        "mechanics": [],
        "zone_interactions": []
    }
    themes = detector.detect_themes(card)
    assert "group_hug" in themes


def test_detect_wheels_theme():
    """Should detect wheels (mass draw/discard) theme."""
    detector = ThemeDetector()
    card = {
        "oracle_text": "Each player discards their hand, then draws seven cards.",
        "functional_categories": [],
        "mechanics": [],
        "zone_interactions": []
    }
    themes = detector.detect_themes(card)
    assert "wheels" in themes


def test_detect_superfriends_theme():
    """Should detect superfriends (planeswalker synergy) theme."""
    detector = ThemeDetector()
    card = {
        "oracle_text": "Whenever you activate a loyalty ability of a planeswalker, draw a card.",
        "functional_categories": [],
        "mechanics": [],
        "zone_interactions": []
    }
    themes = detector.detect_themes(card)
    assert "superfriends" in themes


def test_detect_x_spells_theme():
    """Should detect X spells theme."""
    detector = ThemeDetector()
    card = {
        "oracle_text": "Draw X cards, where X is the number of creatures you control.",
        "functional_categories": [],
        "mechanics": [],
        "zone_interactions": []
    }
    themes = detector.detect_themes(card)
    assert "x_spells" in themes
