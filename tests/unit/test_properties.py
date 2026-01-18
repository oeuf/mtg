"""Tests for property calculator."""

from src.parsing.properties import PropertyCalculator


def test_mana_efficiency_free_spell():
    """Test that free spells have max efficiency."""
    card = {
        "cmc": 0,
        "functional_categories": ["card_draw"],
        "keywords": []
    }
    efficiency = PropertyCalculator.calculate_mana_efficiency(card)
    assert efficiency == 1.0


def test_mana_efficiency_with_roles():
    """Test efficiency calculation with roles."""
    card = {
        "cmc": 2,
        "functional_categories": ["ramp", "card_draw"],
        "keywords": []
    }
    efficiency = PropertyCalculator.calculate_mana_efficiency(card)
    assert efficiency > 0
    assert efficiency <= 1.0


def test_count_color_pips():
    """Test color pip counting."""
    assert PropertyCalculator.count_color_pips("{2}{U}{U}") == 2
    assert PropertyCalculator.count_color_pips("{W}{U}{B}{R}{G}") == 5
    assert PropertyCalculator.count_color_pips("{3}") == 0
    assert PropertyCalculator.count_color_pips("") == 0


def test_is_fast_mana():
    """Test fast mana detection."""
    # Sol Ring
    card = {
        "cmc": 1,
        "oracle_text": "{T}: Add {C}{C}."
    }
    assert PropertyCalculator.is_fast_mana(card) is True

    # Not fast mana (too expensive)
    card = {
        "cmc": 3,
        "oracle_text": "{T}: Add {G}."
    }
    assert PropertyCalculator.is_fast_mana(card) is False

    # Not mana producer
    card = {
        "cmc": 1,
        "oracle_text": "Draw a card."
    }
    assert PropertyCalculator.is_fast_mana(card) is False


def test_is_free_spell():
    """Test free spell detection."""
    # Force of Will style
    card = {
        "oracle_text": "You may exile a blue card from your hand rather than pay this spell's mana cost."
    }
    assert PropertyCalculator.is_free_spell(card) is True

    # Regular spell
    card = {
        "oracle_text": "Counter target spell."
    }
    assert PropertyCalculator.is_free_spell(card) is False
