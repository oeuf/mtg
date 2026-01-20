"""Unit tests for reference deck loader."""

import tempfile
import os
from src.validation.reference_deck import load_reference_deck, parse_decklist_line


def test_parse_decklist_line_tab_separated():
    """Test parsing tab-separated format."""
    line = "1\tSol Ring"
    result = parse_decklist_line(line)
    assert result == "Sol Ring"


def test_parse_decklist_line_space_separated():
    """Test parsing space-separated format."""
    line = "1 Eternal Witness"
    result = parse_decklist_line(line)
    assert result == "Eternal Witness"


def test_parse_decklist_line_with_quantity():
    """Test parsing line with quantity > 1."""
    line = "4\tForest"
    result = parse_decklist_line(line)
    assert result == "Forest"


def test_parse_decklist_line_empty():
    """Test parsing empty line."""
    line = ""
    result = parse_decklist_line(line)
    assert result is None


def test_parse_decklist_line_comment():
    """Test parsing comment line."""
    line = "# This is a comment"
    result = parse_decklist_line(line)
    assert result is None


def test_load_reference_deck():
    """Test loading full deck from file."""
    content = """# Muldrotha Deck
1\tMuldrotha, the Gravetide
1\tSol Ring
1\tEternal Witness
4\tForest
"""

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
        f.write(content)
        temp_path = f.name

    try:
        cards = load_reference_deck(temp_path)

        assert "Muldrotha, the Gravetide" in cards
        assert "Sol Ring" in cards
        assert "Eternal Witness" in cards
        assert "Forest" in cards
        assert len(cards) == 4
    finally:
        os.unlink(temp_path)


def test_load_reference_deck_excludes_commander():
    """Test loading deck excluding commander."""
    content = """1\tMuldrotha, the Gravetide
1\tSol Ring
"""

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
        f.write(content)
        temp_path = f.name

    try:
        cards = load_reference_deck(temp_path, exclude_commander=True)

        assert "Muldrotha, the Gravetide" not in cards
        assert "Sol Ring" in cards
    finally:
        os.unlink(temp_path)
