"""Unit tests for precon parser."""

from src.data.precon_parser import PreconParser


def test_parse_commander_deck():
    """Test parsing Commander decks only, ignoring non-Commander decks."""
    parser = PreconParser()
    counts = parser.parse_all_decks("tests/fixtures/decks")

    # Should count cards from Commander deck only
    assert counts.get("Sol Ring", 0) == 1
    assert counts.get("Command Tower", 0) == 1
    assert counts.get("Eternal Witness", 0) == 1

    # Commander should be counted
    assert counts.get("Muldrotha, the Gravetide", 0) == 1

    # Standard deck cards should NOT be counted
    assert counts.get("Lightning Bolt", 0) == 0


def test_parse_returns_total_precon_count():
    """Test that parser returns total precon count."""
    parser = PreconParser()
    counts, total = parser.parse_all_decks_with_total("tests/fixtures/decks")

    assert total == 1  # Only 1 Commander deck
