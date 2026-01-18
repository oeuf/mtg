"""Tests for functional role parser."""

from src.parsing.functional_roles import FunctionalRoleParser


def test_ramp_detection():
    """Test ramp card detection."""
    oracle_text = "Search your library for a basic land card and put it onto the battlefield tapped."
    roles = FunctionalRoleParser.identify_roles(oracle_text)
    assert "ramp" in roles


def test_card_draw_detection():
    """Test card draw detection."""
    oracle_text = "Draw two cards."
    roles = FunctionalRoleParser.identify_roles(oracle_text)
    assert "card_draw" in roles


def test_removal_detection():
    """Test removal detection."""
    oracle_text = "Destroy target creature."
    roles = FunctionalRoleParser.identify_roles(oracle_text)
    assert "removal" in roles


def test_counterspell_detection():
    """Test counterspell detection."""
    oracle_text = "Counter target spell."
    roles = FunctionalRoleParser.identify_roles(oracle_text)
    assert "counterspell" in roles


def test_recursion_detection():
    """Test recursion detection."""
    oracle_text = "Return target card from your graveyard to your hand."
    roles = FunctionalRoleParser.identify_roles(oracle_text)
    assert "recursion" in roles


def test_protection_detection():
    """Test protection detection."""
    oracle_text = "Target creature gains hexproof until end of turn."
    roles = FunctionalRoleParser.identify_roles(oracle_text)
    assert "protection" in roles


def test_multiple_roles():
    """Test card with multiple roles."""
    oracle_text = "Draw a card. Add {G}{G}."
    roles = FunctionalRoleParser.identify_roles(oracle_text)
    assert "card_draw" in roles
    assert "ramp" in roles


def test_empty_text():
    """Test empty oracle text."""
    roles = FunctionalRoleParser.identify_roles("")
    assert roles == []


def test_no_roles():
    """Test card with no recognized roles."""
    oracle_text = "This is a vanilla creature."
    roles = FunctionalRoleParser.identify_roles(oracle_text)
    assert roles == []
