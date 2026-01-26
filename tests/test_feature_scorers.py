"""Tests for feature scoring functions."""

import pytest
from src.synergy.feature_scorers import FeatureScorers


def test_mechanic_overlap_high():
    """Test high mechanic overlap."""
    mechanics1 = ["etb_trigger", "recursion", "self_mill"]
    mechanics2 = ["etb_trigger", "recursion"]

    score, details = FeatureScorers.score_mechanic_overlap(mechanics1, mechanics2)

    assert score > 0.5
    assert len(details["shared"]) == 2
    assert "etb_trigger" in details["shared"]


def test_mechanic_overlap_none():
    """Test no mechanic overlap."""
    mechanics1 = ["flying", "vigilance"]
    mechanics2 = ["trample", "haste"]

    score, details = FeatureScorers.score_mechanic_overlap(mechanics1, mechanics2)

    assert score == 0.0
    assert len(details["shared"]) == 0


def test_mechanic_overlap_empty():
    """Test empty mechanic lists."""
    score, details = FeatureScorers.score_mechanic_overlap([], ["etb_trigger"])

    assert score == 0.0
    assert details["shared"] == []


def test_role_compatibility_complementary():
    """Test complementary roles score high."""
    roles1 = ["etb_trigger"]
    roles2 = ["sacrifice_outlet"]

    score, details = FeatureScorers.score_role_compatibility(roles1, roles2)

    assert score == 0.9  # From ROLE_COMPATIBILITY table
    assert details["best_pair"] == ("etb_trigger", "sacrifice_outlet")


def test_role_compatibility_redundant():
    """Test redundant roles score low."""
    roles1 = ["etb_trigger", "recursion"]
    roles2 = ["etb_trigger", "card_draw"]

    score, details = FeatureScorers.score_role_compatibility(roles1, roles2)

    # Should be penalized for sharing etb_trigger
    assert score < 0.9


def test_role_compatibility_none():
    """Test no role compatibility."""
    roles1 = ["ramp"]
    roles2 = ["flying"]

    score, details = FeatureScorers.score_role_compatibility(roles1, roles2)

    assert score == 0.0
    assert details["matches"] == []


def test_theme_alignment_shared():
    """Test shared themes."""
    themes1 = ["reanimation", "graveyard_value"]
    themes2 = ["reanimation", "aristocrats"]

    score, details = FeatureScorers.score_theme_alignment(themes1, themes2)

    assert score > 0.4
    assert "reanimation" in details["shared"]


def test_theme_alignment_complementary():
    """Test complementary themes."""
    themes1 = ["reanimation"]
    themes2 = ["graveyard_value"]

    score, details = FeatureScorers.score_theme_alignment(themes1, themes2)

    # Should score based on complementarity
    assert score > 0.0


def test_theme_alignment_empty():
    """Test empty theme lists."""
    score, details = FeatureScorers.score_theme_alignment([], ["reanimation"])

    assert score == 0.0


def test_zone_chain_write_read():
    """Test zone chain detection."""
    zones1 = [{"zone": "graveyard", "interaction_type": "writes"}]
    zones2 = [{"zone": "graveyard", "interaction_type": "reads"}]

    score, details = FeatureScorers.score_zone_chain(zones1, zones2)

    assert score == 0.8
    assert details["chains"][0]["type"] == "write_read"


def test_zone_chain_same_interaction():
    """Test same zone interaction."""
    zones1 = [{"zone": "graveyard", "interaction_type": "reads"}]
    zones2 = [{"zone": "graveyard", "interaction_type": "reads"}]

    score, details = FeatureScorers.score_zone_chain(zones1, zones2)

    assert score == 0.4
    assert details["chains"][0]["type"] == "same_interaction"


def test_zone_chain_no_match():
    """Test different zones."""
    zones1 = [{"zone": "graveyard", "interaction_type": "writes"}]
    zones2 = [{"zone": "exile", "interaction_type": "reads"}]

    score, details = FeatureScorers.score_zone_chain(zones1, zones2)

    assert score == 0.0
    assert details["chains"] == []


def test_phase_alignment():
    """Test phase alignment."""
    phases1 = [{"phase": "upkeep"}, {"phase": "main"}]
    phases2 = [{"phase": "upkeep"}, {"phase": "combat"}]

    score, details = FeatureScorers.score_phase_alignment(phases1, phases2)

    assert score > 0.0
    assert "upkeep" in details["shared_phases"]
    assert details["count"] == 1


def test_phase_alignment_no_overlap():
    """Test no phase overlap."""
    phases1 = [{"phase": "upkeep"}]
    phases2 = [{"phase": "combat"}]

    score, details = FeatureScorers.score_phase_alignment(phases1, phases2)

    assert score == 0.0


def test_color_compatibility_exact():
    """Test exact color match."""
    colors1 = ["B", "G"]
    colors2 = ["B", "G"]

    score, details = FeatureScorers.score_color_compatibility(colors1, colors2)

    assert score == 1.0
    assert details["type"] == "exact_match"


def test_color_compatibility_subset():
    """Test subset color match."""
    colors1 = ["B"]
    colors2 = ["B", "G"]

    score, details = FeatureScorers.score_color_compatibility(colors1, colors2)

    assert score == 0.95
    assert details["type"] == "subset"


def test_color_compatibility_overlap():
    """Test overlapping colors."""
    colors1 = ["B", "G"]
    colors2 = ["B", "R"]

    score, details = FeatureScorers.score_color_compatibility(colors1, colors2)

    assert score > 0.3
    assert details["type"] == "overlap"
    assert "B" in details["shared"]


def test_color_compatibility_disjoint():
    """Test completely different colors."""
    colors1 = ["W", "U"]
    colors2 = ["B", "R"]

    score, details = FeatureScorers.score_color_compatibility(colors1, colors2)

    assert score == 0.3
    assert details["type"] == "disjoint"


def test_color_compatibility_colorless():
    """Test colorless cards."""
    score, details = FeatureScorers.score_color_compatibility([], [])

    assert score == 1.0
    assert details["type"] == "both_colorless"


def test_type_synergy_shared_subtypes():
    """Test shared creature subtypes."""
    subtypes1 = ["Elf", "Warrior"]
    subtypes2 = ["Elf", "Scout"]
    type_line1 = "Creature — Elf Warrior"
    type_line2 = "Creature — Elf Scout"

    score, details = FeatureScorers.score_type_synergy(subtypes1, subtypes2, type_line1, type_line2)

    assert score >= 0.7
    assert "Elf" in details["shared_subtypes"]


def test_type_synergy_shared_types():
    """Test shared card types."""
    subtypes1 = []
    subtypes2 = []
    type_line1 = "Artifact Creature — Golem"
    type_line2 = "Artifact — Equipment"

    score, details = FeatureScorers.score_type_synergy(subtypes1, subtypes2, type_line1, type_line2)

    assert score > 0.0
    assert "Artifact" in details["shared_types"]


def test_type_synergy_none():
    """Test no type synergy."""
    subtypes1 = ["Elf"]
    subtypes2 = ["Goblin"]
    type_line1 = "Creature — Elf"
    type_line2 = "Creature — Goblin"

    score, details = FeatureScorers.score_type_synergy(subtypes1, subtypes2, type_line1, type_line2)

    # Should still get points for shared "Creature" type
    assert score > 0.0


def test_ensemble_score():
    """Test ensemble scoring."""
    dimension_scores = {
        "mechanic_overlap": (0.8, {"shared": ["etb"]}),
        "role_compatibility": (0.9, {"best_pair": ("etb", "sac")}),
        "theme_alignment": (0.7, {"shared": ["aristocrats"]}),
        "zone_chain": (0.0, {"chains": []}),
        "phase_alignment": (0.0, {"shared_phases": []}),
        "color_compatibility": (1.0, {"type": "exact"}),
        "type_synergy": (0.5, {"shared_types": ["Creature"]})
    }

    score, details = FeatureScorers.calculate_ensemble_score(dimension_scores)

    assert 0 <= score <= 1.0
    assert "final_score" in details
    assert details["mechanic_overlap"]["weight"] == 0.20
    assert details["role_compatibility"]["weight"] == 0.25
    assert details["final_score"] == score


def test_ensemble_score_partial_dimensions():
    """Test ensemble with only some dimensions."""
    dimension_scores = {
        "mechanic_overlap": (0.6, {"shared": ["etb"]}),
        "role_compatibility": (0.0, {}),
    }

    score, details = FeatureScorers.calculate_ensemble_score(dimension_scores)

    assert 0 <= score <= 1.0
    # Should only weight the provided dimensions
    expected = (0.6 * 0.20) + (0.0 * 0.25)
    assert abs(score - expected) < 0.001
