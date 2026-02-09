"""Tests for Card model - TDD RED phase."""

import pytest
from pydantic import ValidationError

from app.models.card import Card, CardSearchFilters


class TestCardModel:
    """Card model validation tests."""

    def test_card_valid_data(self):
        """Card model accepts valid card data."""
        card = Card(
            name="Eternal Witness",
            mana_cost="{1}{G}{G}",
            cmc=3,
            type_line="Creature — Human Shaman",
            oracle_text="When Eternal Witness enters the battlefield...",
            color_identity=["G"],
            colors=["G"],
            keywords=[],
            is_legendary=False,
            edhrec_rank=50,
        )
        assert card.name == "Eternal Witness"
        assert card.cmc == 3

    def test_card_missing_name(self):
        """Card model requires name."""
        with pytest.raises(ValidationError):
            Card(
                mana_cost="{1}{G}{G}",
                cmc=3,
                type_line="Creature",
                oracle_text="",
                color_identity=[],
                colors=[],
                keywords=[],
                is_legendary=False,
            )

    def test_card_invalid_cmc(self):
        """Card model validates CMC is non-negative."""
        with pytest.raises(ValidationError):
            Card(
                name="Test",
                mana_cost="",
                cmc=-1,  # Invalid
                type_line="Artifact",
                oracle_text="",
                color_identity=[],
                colors=[],
                keywords=[],
                is_legendary=False,
            )

    def test_card_color_identity_validation(self):
        """Card model validates color identity."""
        card = Card(
            name="Blue Card",
            mana_cost="{U}",
            cmc=1,
            type_line="Instant",
            oracle_text="Draw a card",
            color_identity=["U"],
            colors=["U"],
            keywords=[],
            is_legendary=False,
        )
        assert card.color_identity == ["U"]
        assert card.colors == ["U"]


class TestCardSearchFilters:
    """Card search filter model tests."""

    def test_filters_optional(self):
        """Search filters are all optional."""
        filters = CardSearchFilters()
        assert filters.colors is None
        assert filters.cmc_min is None
        assert filters.cmc_max is None

    def test_filters_with_values(self):
        """Search filters accept valid values."""
        filters = CardSearchFilters(
            colors=["U", "B"],
            cmc_min=2,
            cmc_max=5,
        )
        assert filters.colors == ["U", "B"]
        assert filters.cmc_min == 2
        assert filters.cmc_max == 5
