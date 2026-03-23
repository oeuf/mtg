"""Tests for Commander model - GREEN phase."""

import pytest
from pydantic import ValidationError

from app.models.commander import Commander


class TestCommanderModel:
    """Commander model validation tests."""

    def test_commander_valid_data(self):
        """Commander model accepts valid commander data."""
        commander = Commander(
            name="Muldrotha, the Gravetide",
            mana_cost="{2}{B}{G}{U}",
            cmc=5,
            type_line="Legendary Creature — Elemental",
            oracle_text="...",
            color_identity=["B", "G", "U"],
            colors=["B", "G", "U"],
            keywords=[],
            is_legendary=True,
            power="6",
            toughness="6",
        )
        assert commander.name == "Muldrotha, the Gravetide"
        assert commander.is_legendary is True

    def test_commander_legendary_required(self):
        """Commander must be legendary creature."""
        with pytest.raises(ValidationError):
            Commander(
                name="Test Card",
                mana_cost="{1}",
                cmc=1,
                type_line="Creature — Human",
                oracle_text="",
                color_identity=[],
                colors=[],
                keywords=[],
                is_legendary=False,
                power="1",
                toughness="1",
            )

    def test_commander_power_toughness(self):
        """Commander has power and toughness."""
        commander = Commander(
            name="Test",
            mana_cost="{1}",
            cmc=1,
            type_line="Legendary Creature",
            oracle_text="",
            color_identity=[],
            colors=[],
            keywords=[],
            is_legendary=True,
            power="2",
            toughness="2",
        )
        assert commander.power == "2"
        assert commander.toughness == "2"
