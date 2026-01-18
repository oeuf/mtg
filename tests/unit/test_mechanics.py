"""Tests for mechanic extractor."""

from src.parsing.mechanics import MechanicExtractor


def test_etb_trigger_detection():
    """Test ETB trigger detection."""
    card = {
        "name": "Eternal Witness",
        "oracle_text": "When Eternal Witness enters the battlefield, you may return target card from your graveyard to your hand.",
        "keywords": []
    }
    mechanics = MechanicExtractor.extract_mechanics(card)
    assert "etb_trigger" in mechanics


def test_dies_trigger_detection():
    """Test dies trigger detection."""
    card = {
        "name": "Blood Artist",
        "oracle_text": "Whenever Blood Artist or another creature dies, target player loses 1 life.",
        "keywords": []
    }
    mechanics = MechanicExtractor.extract_mechanics(card)
    assert "dies_trigger" in mechanics


def test_keywords_extracted():
    """Test that keywords are included."""
    card = {
        "name": "Shriekmaw",
        "oracle_text": "When Shriekmaw enters the battlefield, destroy target nonartifact, nonblack creature.",
        "keywords": ["Flash", "Evoke"]
    }
    mechanics = MechanicExtractor.extract_mechanics(card)
    assert "Flash" in mechanics
    assert "Evoke" in mechanics
    assert "etb_trigger" in mechanics


def test_cost_reduction_detection():
    """Test cost reduction detection."""
    card = {
        "name": "Cost Reducer",
        "oracle_text": "Spells you cast cost {1} less to cast.",
        "keywords": []
    }
    mechanics = MechanicExtractor.extract_mechanics(card)
    assert "cost_reduction" in mechanics


def test_cast_trigger_detection():
    """Test cast trigger detection."""
    card = {
        "name": "Talrand",
        "oracle_text": "Whenever you cast an instant or sorcery spell, create a 2/2 blue Drake creature token with flying.",
        "keywords": []
    }
    mechanics = MechanicExtractor.extract_mechanics(card)
    assert "cast_trigger" in mechanics


def test_multiple_mechanics():
    """Test card with multiple mechanics."""
    card = {
        "name": "Complex Card",
        "oracle_text": "When this enters the battlefield, draw a card. Whenever you cast a spell, you may pay {1}.",
        "keywords": ["Flash"]
    }
    mechanics = MechanicExtractor.extract_mechanics(card)
    assert "Flash" in mechanics
    assert "etb_trigger" in mechanics
    assert "cast_trigger" in mechanics


def test_no_mechanics():
    """Test card with no special mechanics."""
    card = {
        "name": "Vanilla Card",
        "oracle_text": "",
        "keywords": []
    }
    mechanics = MechanicExtractor.extract_mechanics(card)
    assert mechanics == []
