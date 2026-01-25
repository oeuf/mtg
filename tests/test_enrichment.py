"""Unit tests for card enrichment."""

import pytest
from src.parsing.enrichment import enrich_card_data


def test_enrich_adds_zone_interactions():
    """Enrichment should add zone_interactions to cards."""
    cards = [{
        "name": "Test Card",
        "oracle_text": "Exile target creature from a graveyard."
    }]

    enriched = enrich_card_data(cards)

    assert "zone_interactions" in enriched[0]
    zones = enriched[0]["zone_interactions"]
    assert any(z["zone"] == "exile" for z in zones)
    assert any(z["zone"] == "graveyard" for z in zones)


def test_enrich_adds_phase_triggers():
    """Enrichment should add phase_triggers to cards."""
    cards = [{
        "name": "Test Card",
        "oracle_text": "At the beginning of your upkeep, draw a card."
    }]

    enriched = enrich_card_data(cards)

    assert "phase_triggers" in enriched[0]
    phases = enriched[0]["phase_triggers"]
    assert any(p["phase"] == "upkeep" for p in phases)


def test_enrich_preserves_existing_properties():
    """Enrichment should preserve existing card properties."""
    cards = [{
        "name": "Test Card",
        "mana_cost": "{2}{U}",
        "cmc": 3,
        "oracle_text": "Draw a card."
    }]

    enriched = enrich_card_data(cards)

    assert enriched[0]["name"] == "Test Card"
    assert enriched[0]["mana_cost"] == "{2}{U}"
    assert enriched[0]["cmc"] == 3


def test_enrich_handles_cards_without_oracle_text():
    """Enrichment should handle cards without oracle text."""
    cards = [{
        "name": "Test Card",
        "mana_cost": "{1}"
    }]

    enriched = enrich_card_data(cards)

    assert "zone_interactions" in enriched[0]
    assert "phase_triggers" in enriched[0]
    assert enriched[0]["zone_interactions"] == []
    assert enriched[0]["phase_triggers"] == []


def test_enrich_multiple_cards():
    """Enrichment should process multiple cards."""
    cards = [
        {"name": "Card 1", "oracle_text": "At the beginning of your upkeep, draw a card."},
        {"name": "Card 2", "oracle_text": "Exile target creature."}
    ]

    enriched = enrich_card_data(cards)

    assert len(enriched) == 2
    assert all("zone_interactions" in card for card in enriched)
    assert all("phase_triggers" in card for card in enriched)


def test_zone_interactions_structure():
    """Zone interactions should have correct structure."""
    cards = [{
        "name": "Test Card",
        "oracle_text": "Search your library for a card."
    }]

    enriched = enrich_card_data(cards)
    interactions = enriched[0]["zone_interactions"]

    assert isinstance(interactions, list)
    if interactions:
        assert "zone" in interactions[0]
        assert "interaction_type" in interactions[0]


def test_phase_triggers_structure():
    """Phase triggers should have correct structure."""
    cards = [{
        "name": "Test Card",
        "oracle_text": "At the beginning of your end step, sacrifice this."
    }]

    enriched = enrich_card_data(cards)
    triggers = enriched[0]["phase_triggers"]

    assert isinstance(triggers, list)
    if triggers:
        assert "phase" in triggers[0]
        assert "trigger_type" in triggers[0]


def test_enrich_adds_subtypes():
    """Enrichment should add subtypes to cards."""
    cards = [{
        "name": "Teval, the Balanced Scale",
        "type_line": "Legendary Creature — Spirit Dragon",
        "oracle_text": "Flying"
    }]

    enriched = enrich_card_data(cards)

    assert "subtypes" in enriched[0]
    assert enriched[0]["subtypes"] == ["Spirit", "Dragon"]
