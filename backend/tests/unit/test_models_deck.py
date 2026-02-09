"""Tests for Deck model - TDD RED phase."""

import pytest
from pydantic import ValidationError


class TestDeckModel:
    """Deck model validation tests."""

    def test_deck_valid_shell(self):
        """DeckShell model accepts valid deck data."""
        pytest.skip("Model not yet implemented")
        # from app.models.deck import DeckShell
        # from app.models.card import Card
        #
        # commander = Card(name="Muldrotha, the Gravetide", ...)
        # cards = [Card(...) for _ in range(37)]
        #
        # deck = DeckShell(
        #     commander=commander,
        #     cards=cards,
        # )
        # assert deck.commander.name == "Muldrotha, the Gravetide"
        # assert len(deck.cards) == 37

    def test_deck_max_100_cards(self):
        """Deck can have at most 99 non-commander cards (100 total)."""
        pytest.skip("Model not yet implemented")
        # from app.models.deck import DeckShell
        # from app.models.card import Card
        #
        # commander = Card(name="Muldrotha, the Gravetide", ...)
        # cards = [Card(...) for _ in range(101)]  # Too many
        #
        # with pytest.raises(ValidationError):
        #     DeckShell(
        #         commander=commander,
        #         cards=cards,
        #     )

    def test_deck_commander_required(self):
        """Deck requires commander."""
        pytest.skip("Model not yet implemented")
        # from app.models.deck import DeckShell
        #
        # with pytest.raises(ValidationError):
        #     DeckShell(
        #         commander=None,
        #         cards=[],
        #     )

    def test_deck_analysis_has_statistics(self):
        """Deck analysis includes statistics."""
        pytest.skip("Model not yet implemented")
        # from app.models.deck import DeckAnalysis
        #
        # analysis = DeckAnalysis(
        #     total_cards=100,
        #     avg_cmc=3.5,
        #     color_distribution={"W": 10, "U": 20, "B": 15, "R": 20, "G": 25, "C": 10},
        #     type_distribution={"Creature": 35, "Instant": 10, "Sorcery": 8},
        #     role_distribution={"Ramp": 15, "Draw": 12, "Removal": 10},
        # )
        # assert analysis.total_cards == 100
        # assert analysis.avg_cmc == 3.5
