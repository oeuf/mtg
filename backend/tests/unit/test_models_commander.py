"""Tests for Commander model - TDD RED phase."""

import pytest
from pydantic import ValidationError


class TestCommanderModel:
    """Commander model validation tests."""

    def test_commander_valid_data(self):
        """Commander model accepts valid commander data."""
        pytest.skip("Model not yet implemented")
        # from app.models.commander import Commander
        # commander = Commander(
        #     name="Muldrotha, the Gravetide",
        #     mana_cost="{2}{B}{G}{U}",
        #     cmc=5,
        #     type_line="Legendary Creature — Elemental",
        #     oracle_text="...",
        #     color_identity=["B", "G", "U"],
        #     colors=["B", "G", "U"],
        #     keywords=[],
        #     is_legendary=True,
        #     power=6,
        #     toughness=6,
        # )
        # assert commander.name == "Muldrotha, the Gravetide"
        # assert commander.is_legendary is True

    def test_commander_legendary_required(self):
        """Commander must be legendary creature."""
        pytest.skip("Model not yet implemented")
        # from app.models.commander import Commander
        # with pytest.raises(ValidationError):
        #     Commander(
        #         name="Test Card",
        #         mana_cost="{1}",
        #         cmc=1,
        #         type_line="Creature — Human",
        #         oracle_text="",
        #         color_identity=[],
        #         colors=[],
        #         keywords=[],
        #         is_legendary=False,  # Invalid for commander
        #         power=1,
        #         toughness=1,
        #     )

    def test_commander_power_toughness(self):
        """Commander has power and toughness."""
        pytest.skip("Model not yet implemented")
        # from app.models.commander import Commander
        # commander = Commander(
        #     name="Test",
        #     mana_cost="{1}",
        #     cmc=1,
        #     type_line="Legendary Creature",
        #     oracle_text="",
        #     color_identity=[],
        #     colors=[],
        #     keywords=[],
        #     is_legendary=True,
        #     power=2,
        #     toughness=2,
        # )
        # assert commander.power == 2
        # assert commander.toughness == 2
