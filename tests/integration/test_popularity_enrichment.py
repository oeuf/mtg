"""Integration tests for popularity enrichment."""

from src.data.enrich_with_popularity import enrich_cards_with_popularity


def test_enrich_with_popularity():
    """Test that cards get popularity scores added."""
    cards = [
        {"name": "Sol Ring", "edhrec_rank": 1},
        {"name": "Island", "edhrec_rank": None},
    ]

    precon_counts = {
        "Sol Ring": 50,
        "Island": 100,
    }
    total_precons = 100

    enriched = enrich_cards_with_popularity(cards, precon_counts, total_precons)

    # Sol Ring should have high score
    sol_ring = next(c for c in enriched if c["name"] == "Sol Ring")
    assert sol_ring["popularity_score"] > 0.8
    assert sol_ring["precon_count"] == 50

    # Island has no rank but high precon count
    island = next(c for c in enriched if c["name"] == "Island")
    assert island["precon_count"] == 100
    assert "popularity_score" in island
