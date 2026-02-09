"""Tests for SynergyService - TDD RED phase.

Tests wrap CardSynergyEngine methods. These tests will fail until
backend/app/services/synergy_service.py is implemented.
"""

import pytest
from app.models.synergy import SynergyDimensions, SynergyResponse


class TestSynergyService:
    """SynergyService method tests - TDD RED phase."""

    def test_compute_synergy_score_returns_tuple(self):
        """SynergyService.compute_synergy_score returns score and details."""
        from app.services.synergy_service import SynergyService
        service = SynergyService()
        card1 = {
            "mechanics": ["etb_trigger", "recursion"],
            "functional_categories": ["recursion"],
            "themes": ["graveyard_value"],
            "color_identity": ["B", "G", "U"],
            "subtypes": [],
            "type_line": "Creature — Elemental",
            "zone_interactions": [{"zone": "graveyard", "interaction_type": "reads"}],
            "phase_triggers": [{"phase": "beginning_of_turn"}]
        }
        card2 = {
            "mechanics": ["etb_trigger"],
            "functional_categories": ["value"],
            "themes": ["graveyard_value"],
            "color_identity": ["G"],
            "subtypes": ["Human", "Shaman"],
            "type_line": "Creature — Human Shaman",
            "zone_interactions": [{"zone": "graveyard", "interaction_type": "reads"}],
            "phase_triggers": []
        }
        score, details = service.compute_synergy_score(card1, card2)
        assert isinstance(score, float)
        assert 0 <= score <= 1
        assert isinstance(details, dict)
        assert "mechanic_overlap" in details
        assert "role_compatibility" in details
        assert "final_score" in details

    def test_compute_synergy_dimensions_breakdown(self):
        """SynergyService synergy includes 7-dimension breakdown."""
        from app.services.synergy_service import SynergyService
        service = SynergyService()
        card1 = {
            "mechanics": ["etb_trigger", "recursion"],
            "functional_categories": ["recursion"],
            "themes": ["graveyard_value"],
            "color_identity": ["B", "G", "U"],
            "subtypes": [],
            "type_line": "Creature — Elemental",
            "zone_interactions": [{"zone": "graveyard", "interaction_type": "reads"}],
            "phase_triggers": [{"phase": "beginning_of_turn"}]
        }
        card2 = {
            "mechanics": ["etb_trigger"],
            "functional_categories": ["value"],
            "themes": ["graveyard_value"],
            "color_identity": ["G"],
            "subtypes": ["Human", "Shaman"],
            "type_line": "Creature — Human Shaman",
            "zone_interactions": [{"zone": "graveyard", "interaction_type": "reads"}],
            "phase_triggers": []
        }
        score, details = service.compute_synergy_score(card1, card2)
        required_dimensions = [
            "mechanic_overlap",
            "role_compatibility",
            "theme_alignment",
            "zone_chain",
            "phase_alignment",
            "color_compatibility",
            "type_synergy"
        ]
        for dim in required_dimensions:
            assert dim in details
            assert "score" in details[dim]
            assert "weight" in details[dim]
            assert "weighted_score" in details[dim]
            assert 0 <= details[dim]["score"] <= 1

    def test_find_mechanic_synergies_returns_card_pairs(self):
        """SynergyService.find_mechanic_synergies returns mechanic-matching pairs."""
        from unittest.mock import MagicMock
        from app.services.synergy_service import SynergyService
        mock_connection = MagicMock()
        mock_connection.execute_query.return_value = [
            {"card1": "Eternal Witness", "card2": "Mulldrifter",
             "shared_mechanics": ["etb_trigger", "recursion"], "mechanic_overlap": 2},
            {"card1": "Sakura-Tribe Elder", "card2": "Wood Elves",
             "shared_mechanics": ["etb_trigger", "ramp"], "mechanic_overlap": 2},
        ]
        service = SynergyService(mock_connection)
        result = service.find_mechanic_synergies(
            min_shared_mechanics=2
        )
        assert isinstance(result, list)
        if result:
            assert all("card1" in c and "card2" in c for c in result)
            assert all("shared_mechanics" in c for c in result)
            assert all(len(c["shared_mechanics"]) >= 2 for c in result)

    def test_calculate_role_compatibility_returns_score(self):
        """SynergyService.calculate_role_compatibility returns compatibility score."""
        from app.services.synergy_service import SynergyService
        service = SynergyService()
        score = service.calculate_role_compatibility(
            roles1=["etb_trigger", "recursion"],
            roles2=["sacrifice_outlet", "value"]
        )
        assert isinstance(score, float)
        assert 0 <= score <= 1
        # Should give high score for complementary roles
        assert score > 0.5
