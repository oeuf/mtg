"""Integration tests for MTGJSON parsers."""

import os
from src.data.atomic_cards_parser import AtomicCardsParser
from src.data.related_cards_parser import RelatedCardsParser


def test_atomic_cards_parser_with_fixture():
    """Test that parser correctly processes fixture data."""
    fixture_path = "tests/fixtures/mtgjson/sample_atomic_cards.json"

    parser = AtomicCardsParser()
    cards = parser.parse(fixture_path)

    # Should parse all 5 cards
    assert len(cards) == 5

    # Verify card names
    card_names = [c["name"] for c in cards]
    assert "Sol Ring" in card_names
    assert "Muldrotha, the Gravetide" in card_names
    assert "Eternal Witness" in card_names

    # Verify commander detection
    commanders = [c for c in cards if c.get("can_be_commander")]
    assert len(commanders) == 1
    assert commanders[0]["name"] == "Muldrotha, the Gravetide"

    # Verify properties are extracted
    sol_ring = next(c for c in cards if c["name"] == "Sol Ring")
    assert sol_ring["cmc"] == 1
    assert sol_ring["type_line"] == "Artifact"
    assert sol_ring["color_identity"] == []


def test_related_cards_parser_with_fixture():
    """Test that RelatedCards parser works with fixture."""
    fixture_path = "tests/fixtures/mtgjson/sample_related_cards.json"

    parser = RelatedCardsParser()
    related = parser.parse(fixture_path)

    # Should have 3 entries (NOTE: We removed the tokens field in Task 1, so this should still work)
    assert len(related) == 3

    # Verify Dramatic Reversal combo data
    assert "Dramatic Reversal" in related
    dramatic = related["Dramatic Reversal"]
    assert "Isochron Scepter" in dramatic["spellbook"]
    assert "Isochron Scepter" in dramatic["reverseRelated"]
