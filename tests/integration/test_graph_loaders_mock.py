"""Integration tests for graph loaders using mocked Neo4j."""

from unittest.mock import Mock, MagicMock, call
from src.graph.loaders import load_card_to_graph, batch_load_cards
from src.graph.connection import Neo4jConnection


def test_load_card_to_graph_creates_card_node():
    """Test that load_card creates proper Card node."""
    # Mock connection
    mock_conn = Mock(spec=Neo4jConnection)

    card_data = {
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
        "edhrec_rank": 1,
        "functional_categories": ["ramp"],
        "mechanics": [],
        "mana_efficiency": 0.5,
        "color_pip_intensity": 0,
        "is_free_spell": False,
        "is_fast_mana": True
    }

    load_card_to_graph(mock_conn, card_data)

    # Verify execute_query was called
    assert mock_conn.execute_query.called

    # Verify the query contains MERGE for Card node
    call_args = mock_conn.execute_query.call_args
    query = call_args[0][0]
    params = call_args[0][1]

    assert "MERGE" in query
    assert "Card" in query
    assert params["name"] == "Sol Ring"
    assert params["is_fast_mana"] is True


def test_load_commander_to_graph_creates_commander_node():
    """Test that load_card creates Commander node for commanders."""
    mock_conn = Mock(spec=Neo4jConnection)

    card_data = {
        "name": "Muldrotha, the Gravetide",
        "mana_cost": "{3}{B}{G}{U}",
        "cmc": 6,
        "type_line": "Legendary Creature — Elemental Avatar",
        "oracle_text": "During each of your turns, you may play one permanent card.",
        "color_identity": ["B", "G", "U"],
        "colors": ["B", "G", "U"],
        "keywords": [],
        "is_legendary": True,
        "is_reserved_list": False,
        "can_be_commander": True,
        "edhrec_rank": 50,
        "functional_categories": [],
        "mechanics": [],
        "mana_efficiency": 0.3,
        "color_pip_intensity": 3,
        "is_free_spell": False,
        "is_fast_mana": False
    }

    load_card_to_graph(mock_conn, card_data)

    # Verify Commander node created
    call_args = mock_conn.execute_query.call_args
    query = call_args[0][0]

    assert "Commander" in query
    assert "can_be_commander" in query


from src.graph.loaders import create_mechanic_relationships, create_role_relationships


def test_create_mechanic_relationships():
    """Test mechanic relationship creation."""
    mock_conn = Mock(spec=Neo4jConnection)

    card_data = {
        "name": "Eternal Witness",
        "mechanics": ["etb_trigger"]
    }

    create_mechanic_relationships(mock_conn, card_data)

    # Should call execute_query twice: once for MERGE mechanic, once for relationship
    assert mock_conn.execute_query.call_count == 2

    # Verify HAS_MECHANIC relationship created
    calls = mock_conn.execute_query.call_args_list
    relationship_call = calls[1]
    query = relationship_call[0][0]

    assert "HAS_MECHANIC" in query
    assert "is_primary" in query


def test_create_role_relationships():
    """Test role relationship creation."""
    mock_conn = Mock(spec=Neo4jConnection)

    card_data = {
        "name": "Sol Ring",
        "functional_categories": ["ramp"],
        "oracle_text": "{T}: Add {C}{C}.",
        "mana_efficiency": 0.5
    }

    create_role_relationships(mock_conn, card_data)

    # Should call execute_query twice: once for MERGE role, once for relationship
    assert mock_conn.execute_query.call_count == 2

    # Verify FILLS_ROLE relationship
    calls = mock_conn.execute_query.call_args_list
    relationship_call = calls[1]
    query = relationship_call[0][0]
    params = relationship_call[0][1]

    assert "FILLS_ROLE" in query
    assert "efficiency_score" in query
    assert params["role_name"] == "ramp"


def test_batch_load_cards_calls_load_for_each_card(capsys):
    """Test that batch_load_cards processes all cards."""
    mock_conn = Mock(spec=Neo4jConnection)

    cards = [
        {"name": "Card 1", "is_legendary": False, "can_be_commander": False},
        {"name": "Card 2", "is_legendary": False, "can_be_commander": False},
        {"name": "Card 3", "is_legendary": False, "can_be_commander": False},
    ]

    batch_load_cards(mock_conn, cards)

    # Should call execute_query 3 times (once per card)
    assert mock_conn.execute_query.call_count == 3

    # Check output
    captured = capsys.readouterr()
    assert "Loading 3 cards" in captured.out
    assert "Loaded 3 cards" in captured.out


from src.graph.loaders import create_subtype_relationships


def test_create_subtype_relationships():
    """Test subtype relationship creation."""
    mock_conn = Mock(spec=Neo4jConnection)

    card_data = {
        "name": "Llanowar Elves",
        "subtypes": ["Elf", "Druid"]
    }

    create_subtype_relationships(mock_conn, card_data)

    # Should call execute_query 4 times: 2 MERGE subtypes + 2 relationships
    assert mock_conn.execute_query.call_count == 4

    # Verify HAS_SUBTYPE relationship created
    calls = mock_conn.execute_query.call_args_list
    # Check that relationship queries contain HAS_SUBTYPE
    relationship_queries = [c[0][0] for c in calls if "HAS_SUBTYPE" in c[0][0]]
    assert len(relationship_queries) == 2


def test_load_card_includes_popularity_score():
    """Test that card loading includes popularity_score property."""
    mock_conn = Mock(spec=Neo4jConnection)

    card_data = {
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
        "edhrec_rank": 1,
        "functional_categories": ["ramp"],
        "mechanics": [],
        "mana_efficiency": 0.5,
        "color_pip_intensity": 0,
        "is_free_spell": False,
        "is_fast_mana": True,
        "subtypes": [],
        "popularity_score": 0.95,
        "precon_count": 50
    }

    load_card_to_graph(mock_conn, card_data)

    # Verify the query includes popularity fields
    call_args = mock_conn.execute_query.call_args
    params = call_args[0][1]

    assert params["popularity_score"] == 0.95
    assert params["precon_count"] == 50
