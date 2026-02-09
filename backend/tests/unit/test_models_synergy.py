"""Tests for Synergy response models - GREEN phase."""

import pytest
from pydantic import ValidationError

from app.models.synergy import SynergyResponse, SynergyDimensions


class TestSynergyResponse:
    """Synergy response model validation tests."""

    def test_synergy_score_between_0_1(self):
        """Synergy score is between 0 and 1."""
        synergy = SynergyResponse(
            card_name="Eternal Witness",
            synergy_score=0.75,
            dimensions=SynergyDimensions(
                mechanic_overlap=0.8,
                role_compatibility=0.7,
                theme_alignment=0.6,
                zone_chain=0.5,
                phase_alignment=0.4,
                color_compatibility=0.3,
                type_synergy=0.2,
            ),
        )
        assert 0 <= synergy.synergy_score <= 1

    def test_synergy_score_invalid_high(self):
        """Synergy score > 1 is invalid."""
        with pytest.raises(ValidationError):
            SynergyResponse(
                card_name="Test",
                synergy_score=1.5,
                dimensions=SynergyDimensions(
                    mechanic_overlap=0.8,
                    role_compatibility=0.7,
                    theme_alignment=0.6,
                    zone_chain=0.5,
                    phase_alignment=0.4,
                    color_compatibility=0.3,
                    type_synergy=0.2,
                ),
            )

    def test_synergy_dimensions_valid(self):
        """Synergy dimensions are valid."""
        dims = SynergyDimensions(
            mechanic_overlap=0.8,
            role_compatibility=0.7,
            theme_alignment=0.6,
            zone_chain=0.5,
            phase_alignment=0.4,
            color_compatibility=0.3,
            type_synergy=0.2,
        )
        synergy = SynergyResponse(
            card_name="Eternal Witness",
            synergy_score=0.75,
            dimensions=dims,
        )
        dim_dict = synergy.dimensions.to_dict()
        assert all(0 <= v <= 1 for v in dim_dict.values())

    def test_synergy_breakdow_explainable(self):
        """Synergy response is human-explainable."""
        synergy = SynergyResponse(
            card_name="Eternal Witness",
            synergy_score=0.75,
            dimensions=SynergyDimensions(
                mechanic_overlap=0.8,
                role_compatibility=0.7,
                theme_alignment=0.6,
                zone_chain=0.5,
                phase_alignment=0.4,
                color_compatibility=0.3,
                type_synergy=0.2,
            ),
            explanation="High mechanic overlap (ETB trigger synergy)",
        )
        assert "synergy" in synergy.explanation.lower()
