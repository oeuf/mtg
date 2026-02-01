"""Unit tests for reference deck loader."""

import tempfile
import os
from src.validation.reference_deck import load_reference_deck


def test_load_simple_deck():
    """Test loading deck from simple format."""
    content = """Muldrotha, the Gravetide
Sol Ring
Eternal Witness
Sakura-Tribe Elder
"""

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name

    try:
        cards = load_reference_deck(temp_path)
        assert len(cards) == 4
        assert "Muldrotha, the Gravetide" in cards
        assert "Sol Ring" in cards
    finally:
        os.unlink(temp_path)


def test_load_deck_with_comments():
    """Test loading deck ignoring comments and empty lines."""
    content = """# Muldrotha Deck
Sol Ring

# Ramp
Sakura-Tribe Elder
"""

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name

    try:
        cards = load_reference_deck(temp_path)
        assert len(cards) == 2
        assert "Sol Ring" in cards
        assert "Sakura-Tribe Elder" in cards
    finally:
        os.unlink(temp_path)


def test_exclude_commander():
    """Test that loader returns all cards (exclusion happens in query)."""
    content = """Muldrotha, the Gravetide
Sol Ring
"""

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name

    try:
        cards = load_reference_deck(temp_path)
        assert len(cards) == 2
        assert "Muldrotha, the Gravetide" in cards
        assert "Sol Ring" in cards
    finally:
        os.unlink(temp_path)
