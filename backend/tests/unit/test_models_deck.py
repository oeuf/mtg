"""Tests for Deck model - GREEN phase."""

import pytest
from pydantic import ValidationError

from app.models.card import Card
from app.models.commander import Commander
from app.models.deck import DeckShell, DeckAnalysis


def _make_commander():
    return Commander(
        name="Muldrotha, the Gravetide",
        mana_cost="{2}{B}{G}{U}",
        cmc=5,
        type_line="Legendary Creature — Elemental",
        oracle_text="...",
        color_identity=["B", "G", "U"],
        colors=["B", "G", "U"],
        keywords=[],
        is_legendary=True,
        power=6,
        toughness=6,
    )


def _make_card(name="Test Card"):
    return Card(
        name=name,
        mana_cost="{1}",
        cmc=1,
        type_line="Creature — Human",
        oracle_text="",
        color_identity=[],
        colors=[],
        keywords=[],
    )


class TestDeckModel:
    """Deck model validation tests."""

    def test_deck_valid_shell(self):
        """DeckShell model accepts valid deck data."""
        commander = _make_commander()
        cards = [_make_card(f"Card {i}") for i in range(37)]

        deck = DeckShell(
            commander=commander,
            cards=cards,
        )
        assert deck.commander.name == "Muldrotha, the Gravetide"
        assert len(deck.cards) == 37

    def test_deck_max_100_cards(self):
        """Deck can have at most 99 non-commander cards (100 total)."""
        commander = _make_commander()
        cards = [_make_card(f"Card {i}") for i in range(101)]

        with pytest.raises(ValidationError):
            DeckShell(
                commander=commander,
                cards=cards,
            )

    def test_deck_commander_required(self):
        """Deck requires commander."""
        with pytest.raises(ValidationError):
            DeckShell(
                commander=None,
                cards=[],
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
