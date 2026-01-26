"""Tests for card-to-card synergy inference."""

import pytest
from unittest.mock import Mock
from src.synergy.card_synergies import CardSynergyEngine


def test_find_mechanic_synergies():
    """Test finding cards with shared mechanics."""
    mock_conn = Mock()
    mock_conn.execute_query.return_value = [{
        "card1": "Eternal Witness",
        "card2": "Archaeomancer",
        "shared_mechanics": ["etb_trigger", "recursion"],
        "mechanic_overlap": 2
    }]

    engine = CardSynergyEngine()
    result = engine.find_mechanic_synergies(mock_conn, min_shared_mechanics=2)

    assert len(result) == 1
    assert result[0]["mechanic_overlap"] >= 2


def test_calculate_role_compatibility():
    """Test role compatibility scoring."""
    engine = CardSynergyEngine()

    score = engine.calculate_role_compatibility(
        roles1=["etb_trigger"], roles2=["sacrifice_outlet"]
    )
    assert score > 0.7

    score = engine.calculate_role_compatibility(
        roles1=["ramp"], roles2=["ramp"]
    )
    assert score < 0.3


def test_create_synergy_relationships():
    """Test creating SYNERGIZES_WITH relationships."""
    mock_conn = Mock()
    mock_conn.execute_query.return_value = [{"created": 1000}]

    engine = CardSynergyEngine()
    result = engine.create_synergy_relationships(mock_conn, min_shared_mechanics=2, min_synergy_score=0.6)

    assert result["created"] > 0
