"""Unit tests for zone and phase loaders."""

import pytest
from unittest.mock import MagicMock
from src.graph.loaders import (
    create_zone_nodes,
    create_phase_nodes,
    create_zone_relationships,
    create_phase_relationships
)


@pytest.fixture
def mock_conn():
    """Create a mock connection."""
    conn = MagicMock()
    conn.execute_query = MagicMock(return_value=[])
    return conn


@pytest.fixture
def zones_data():
    """Sample zones data."""
    return {
        "graveyard": {
            "rule_number": "404",
            "is_public": True,
            "is_ordered": True,
            "description": "Public zone for dead cards"
        },
        "exile": {
            "rule_number": "406",
            "is_public": True,
            "is_ordered": False,
            "description": "Zone for exiled cards"
        }
    }


@pytest.fixture
def phases_data():
    """Sample phases data."""
    return {
        "upkeep": {
            "rule_number": "503",
            "order": 2,
            "parent": "beginning",
            "is_step": True
        },
        "combat_damage": {
            "rule_number": "510",
            "order": 8,
            "parent": "combat",
            "is_step": True
        }
    }


def test_create_zone_nodes(mock_conn, zones_data):
    """Test creating zone nodes."""
    create_zone_nodes(mock_conn, zones_data)

    # Should call execute_query for each zone
    assert mock_conn.execute_query.call_count == len(zones_data)

    # Check that Zone nodes are created with correct properties
    calls = [call[0][0] for call in mock_conn.execute_query.call_args_list]
    assert any("Zone" in call and "graveyard" in str(mock_conn.execute_query.call_args_list) for call in calls)


def test_create_phase_nodes(mock_conn, phases_data):
    """Test creating phase nodes."""
    create_phase_nodes(mock_conn, phases_data)

    # Should call execute_query for each phase
    assert mock_conn.execute_query.call_count == len(phases_data)

    # Check that Phase nodes are created
    calls = [call[0][0] for call in mock_conn.execute_query.call_args_list]
    assert any("Phase" in call for call in calls)


def test_create_zone_relationships(mock_conn):
    """Test creating zone interaction relationships."""
    card_data = {
        "name": "Test Card",
        "zone_interactions": [
            {"zone": "graveyard", "interaction_type": "reads"},
            {"zone": "exile", "interaction_type": "moves_to"}
        ]
    }

    create_zone_relationships(mock_conn, card_data)

    # Should create relationships for each zone interaction
    assert mock_conn.execute_query.call_count == len(card_data["zone_interactions"])


def test_create_phase_relationships(mock_conn):
    """Test creating phase trigger relationships."""
    card_data = {
        "name": "Test Card",
        "phase_triggers": [
            {"phase": "upkeep", "trigger_type": "beginning"},
            {"phase": "end_step", "trigger_type": "beginning"}
        ]
    }

    create_phase_relationships(mock_conn, card_data)

    # Should create relationships for each phase trigger
    assert mock_conn.execute_query.call_count == len(card_data["phase_triggers"])


def test_create_zone_relationships_empty_list(mock_conn):
    """Test handling cards with no zone interactions."""
    card_data = {
        "name": "Test Card",
        "zone_interactions": []
    }

    create_zone_relationships(mock_conn, card_data)

    # Should not call execute_query
    assert mock_conn.execute_query.call_count == 0


def test_create_phase_relationships_empty_list(mock_conn):
    """Test handling cards with no phase triggers."""
    card_data = {
        "name": "Test Card",
        "phase_triggers": []
    }

    create_phase_relationships(mock_conn, card_data)

    # Should not call execute_query
    assert mock_conn.execute_query.call_count == 0
