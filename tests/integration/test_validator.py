"""Integration tests for validation runner."""

from unittest.mock import Mock, patch
from src.validation.validator import DeckValidator
from src.graph.connection import Neo4jConnection


def test_validator_initialization():
    """Test validator initializes with connection."""
    mock_conn = Mock(spec=Neo4jConnection)

    validator = DeckValidator(mock_conn)

    assert validator.conn == mock_conn


def test_validator_get_recommendations():
    """Test getting ranked recommendations."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = [
        {"name": "Eternal Witness"},
        {"name": "Spore Frog"},
        {"name": "Sol Ring"},
    ]

    validator = DeckValidator(mock_conn)
    recommendations = validator.get_recommendations(
        commander_name="Muldrotha, the Gravetide",
        limit=100
    )

    assert recommendations == ["Eternal Witness", "Spore Frog", "Sol Ring"]


def test_validator_validate():
    """Test full validation run."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = [
        {"name": "Eternal Witness"},
        {"name": "Sol Ring"},
        {"name": "Other Card"},
    ]

    validator = DeckValidator(mock_conn)

    # Mock reference deck
    reference = {"Eternal Witness", "Sol Ring", "Missing Card"}

    result = validator.validate(
        reference_cards=reference,
        commander_name="Muldrotha, the Gravetide",
        top_k=100
    )

    assert "mrr" in result
    assert "overlap_100" in result
    assert "missing_cards" in result
    assert result["reference_count"] == 3
