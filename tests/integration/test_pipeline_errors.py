"""Integration tests for pipeline error handling."""

import pytest
from src.data.atomic_cards_parser import AtomicCardsParser
from src.data.related_cards_parser import RelatedCardsParser


def test_parser_handles_missing_file():
    """Test that parser raises appropriate error for missing file."""
    parser = AtomicCardsParser()

    with pytest.raises(FileNotFoundError):
        parser.parse("nonexistent_file.json")


def test_parser_handles_invalid_json():
    """Test that parser handles malformed JSON gracefully."""
    import tempfile
    import os

    # Create temp file with invalid JSON
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        f.write("{invalid json}")
        temp_path = f.name

    try:
        parser = AtomicCardsParser()
        with pytest.raises(Exception):  # JSONDecodeError or similar
            parser.parse(temp_path)
    finally:
        os.unlink(temp_path)


def test_enrichment_handles_missing_fields():
    """Test enrichment works with cards missing optional fields."""
    from src.parsing.enrichment import enrich_card_data

    minimal_card = {
        "name": "Minimal Card",
        "mana_cost": "",
        "cmc": 0,
        "type_line": "Artifact",
        "oracle_text": "",
        "color_identity": [],
        "colors": [],
        "keywords": [],
        "is_legendary": False,
        "is_reserved_list": False,
        "can_be_commander": False,
        # Missing edhrec_rank
    }

    enriched = enrich_card_data([minimal_card])

    assert len(enriched) == 1
    assert "functional_categories" in enriched[0]
    assert "mechanics" in enriched[0]


def test_related_cards_parser_handles_missing_file():
    """Test that RelatedCardsParser raises error for missing file."""
    parser = RelatedCardsParser()

    with pytest.raises(FileNotFoundError):
        parser.parse("nonexistent_related.json")


def test_enrichment_handles_empty_list():
    """Test enrichment handles empty card list gracefully."""
    from src.parsing.enrichment import enrich_card_data

    enriched = enrich_card_data([])

    assert enriched == []


def test_enrichment_handles_card_with_no_text():
    """Test enrichment handles cards with no oracle text."""
    from src.parsing.enrichment import enrich_card_data

    card = {
        "name": "Vanilla Creature",
        "mana_cost": "{2}{G}",
        "cmc": 3,
        "type_line": "Creature — Beast",
        "oracle_text": "",  # No text (vanilla creature)
        "color_identity": ["G"],
        "colors": ["G"],
        "keywords": [],
        "is_legendary": False,
        "is_reserved_list": False,
        "can_be_commander": False,
    }

    enriched = enrich_card_data([card])

    assert len(enriched) == 1
    assert enriched[0]["functional_categories"] == []  # No roles for vanilla
    assert enriched[0]["mechanics"] == []  # No mechanics
