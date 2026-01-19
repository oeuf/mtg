"""Integration test for card enrichment pipeline."""

from src.parsing.enrichment import enrich_card_data


def test_enrichment_integration():
    """Test that enrichment adds all expected properties."""
    # Sample card data (like what comes from MTGJSON)
    sample_cards = [
        {
            "name": "Sol Ring",
            "mana_cost": "{1}",
            "cmc": 1,
            "type_line": "Artifact",
            "oracle_text": "{T}: Add {C}{C}.",
            "color_identity": [],
            "colors": [],
            "keywords": [],
            "is_legendary": False,
            "is_reserved_list": False,
            "can_be_commander": False,
            "edhrec_rank": 1
        },
        {
            "name": "Eternal Witness",
            "mana_cost": "{1}{G}{G}",
            "cmc": 3,
            "type_line": "Creature — Human Shaman",
            "oracle_text": "When Eternal Witness enters the battlefield, you may return target card from your graveyard to your hand.",
            "color_identity": ["G"],
            "colors": ["G"],
            "keywords": [],
            "is_legendary": False,
            "is_reserved_list": False,
            "can_be_commander": False,
            "edhrec_rank": 50
        }
    ]

    enriched = enrich_card_data(sample_cards)

    # Verify enrichment added properties
    assert len(enriched) == 2

    # Check Sol Ring
    sol_ring = enriched[0]
    assert "functional_categories" in sol_ring
    assert "ramp" in sol_ring["functional_categories"]
    assert "mechanics" in sol_ring
    assert "mana_efficiency" in sol_ring
    assert sol_ring["is_fast_mana"] is True
    assert "color_pip_intensity" in sol_ring

    # Check Eternal Witness
    witness = enriched[1]
    assert "functional_categories" in witness
    assert "recursion" in witness["functional_categories"]
    assert "mechanics" in witness
    assert "etb_trigger" in witness["mechanics"]
    assert "mana_efficiency" in witness
    assert witness["color_pip_intensity"] == 2  # Two {G} symbols


def test_enrichment_preserves_original_data():
    """Test that enrichment doesn't lose original card data."""
    sample_card = {
        "name": "Test Card",
        "mana_cost": "{2}{U}",
        "cmc": 3,
        "type_line": "Instant",
        "oracle_text": "Draw two cards.",
        "color_identity": ["U"],
        "colors": ["U"],
        "keywords": [],
        "is_legendary": False,
        "is_reserved_list": False,
        "can_be_commander": False,
        "edhrec_rank": 100
    }

    enriched = enrich_card_data([sample_card])
    result = enriched[0]

    # Original properties preserved
    assert result["name"] == "Test Card"
    assert result["mana_cost"] == "{2}{U}"
    assert result["cmc"] == 3
    assert result["oracle_text"] == "Draw two cards."

    # New properties added
    assert "card_draw" in result["functional_categories"]
    assert result["mana_efficiency"] > 0
