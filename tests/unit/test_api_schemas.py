"""Unit tests for API schemas."""

from api.schemas import (
    CardBase,
    CardResponse,
    CommanderResponse,
    RecommendationResponse,
    DeckAnalysis,
    ComboResponse,
    GraphNodeResponse,
    GraphEdgeResponse,
    GraphResponse
)


def test_card_base_schema():
    """Test CardBase schema."""
    card = CardBase(
        name="Sol Ring",
        mana_cost="{1}",
        cmc=1,
        type_line="Artifact",
        oracle_text="{T}: Add {C}{C}."
    )
    assert card.name == "Sol Ring"
    assert card.cmc == 1


def test_card_response_schema():
    """Test CardResponse schema with computed fields."""
    card = CardResponse(
        name="Eternal Witness",
        mana_cost="{1}{G}{G}",
        cmc=3,
        type_line="Creature",
        mechanics=["etb_trigger"],
        functional_categories=["recursion"]
    )
    assert card.name == "Eternal Witness"
    assert "etb_trigger" in card.mechanics
    assert "recursion" in card.functional_categories


def test_commander_response_schema():
    """Test CommanderResponse schema."""
    commander = CommanderResponse(
        name="Muldrotha, the Gravetide",
        mana_cost="{3}{B}{G}{U}",
        cmc=6,
        type_line="Legendary Creature — Elemental Avatar",
        synergies=["graveyard", "self_mill"]
    )
    assert commander.name == "Muldrotha, the Gravetide"
    assert commander.can_be_commander is True
    assert "graveyard" in commander.synergies


def test_recommendation_response_schema():
    """Test RecommendationResponse schema."""
    rec = RecommendationResponse(
        name="Spore Frog",
        mana_cost="{G}",
        cmc=1,
        score=0.95,
        shared_mechanics=["dies_trigger"],
        roles=["protection"]
    )
    assert rec.name == "Spore Frog"
    assert rec.score == 0.95


def test_deck_analysis_schema():
    """Test DeckAnalysis schema."""
    analysis = DeckAnalysis(
        commander="Muldrotha, the Gravetide",
        card_count=99,
        role_coverage={"ramp": 10, "card_draw": 8},
        missing_roles=["protection"],
        suggested_additions=[
            RecommendationResponse(
                name="Spore Frog",
                score=0.9,
                roles=["protection"]
            )
        ],
        suggested_cuts=[]
    )
    assert analysis.card_count == 99
    assert len(analysis.missing_roles) == 1


def test_combo_response_schema():
    """Test ComboResponse schema."""
    combo = ComboResponse(
        piece1="Dramatic Reversal",
        piece2="Isochron Scepter",
        description="Infinite mana with rocks"
    )
    assert combo.piece1 == "Dramatic Reversal"
    assert combo.piece2 == "Isochron Scepter"


def test_graph_response_schema():
    """Test GraphResponse schema."""
    graph = GraphResponse(
        nodes=[
            GraphNodeResponse(
                id="sol_ring",
                label="Sol Ring",
                type="Card",
                properties={"cmc": 1}
            )
        ],
        edges=[
            GraphEdgeResponse(
                source="sol_ring",
                target="ramp",
                type="FILLS_ROLE",
                properties={}
            )
        ]
    )
    assert len(graph.nodes) == 1
    assert len(graph.edges) == 1
    assert graph.nodes[0].type == "Card"
