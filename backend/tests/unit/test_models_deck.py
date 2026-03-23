"""Tests for Deck model - GREEN phase."""

import pytest
from pydantic import ValidationError

from app.models.deck import DeckShell, DeckAnalysis


class TestDeckModel:
    """Deck model validation tests."""

    def test_deck_valid_shell(self):
        """DeckShell model accepts valid deck data."""
        deck = DeckShell(
            commander="Muldrotha, the Gravetide",
            cards_by_role={"ramp": ["Sol Ring", "Arcane Signet"], "utility": ["Brainstorm"]},
            total_cards=4,
        )
        assert deck.commander == "Muldrotha, the Gravetide"
        assert deck.total_cards == 4
        assert "ramp" in deck.cards_by_role

    def test_deck_commander_required(self):
        """Deck requires commander."""
        with pytest.raises(ValidationError):
            DeckShell(
                cards_by_role={},
                total_cards=1,
            )

    def test_deck_analysis_has_statistics(self):
        """Deck analysis includes statistics."""
        analysis = DeckAnalysis(
            total_cards=100,
            avg_cmc=3.5,
            color_distribution={"W": 10, "U": 20, "B": 15, "R": 20, "G": 25, "C": 10},
            type_distribution={"Creature": 35, "Instant": 10, "Sorcery": 8},
            role_distribution={"Ramp": 15, "Draw": 12, "Removal": 10},
            mana_curve={"0": 5, "1": 10, "2": 15, "3": 20, "4": 15, "5": 10, "6": 5},
        )
        assert analysis.total_cards == 100
        assert analysis.avg_cmc == 3.5
