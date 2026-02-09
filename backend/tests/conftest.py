"""Shared test fixtures and configuration."""

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.card import Card
from app.models.commander import Commander


@pytest.fixture
def client():
    """Synchronous test client for testing."""
    return TestClient(app)


@pytest.fixture
def sample_card() -> Card:
    """Sample card for testing."""
    return Card(
        name="Eternal Witness",
        mana_cost="{1}{G}{G}",
        cmc=3,
        type_line="Creature — Human Shaman",
        oracle_text="When Eternal Witness enters the battlefield, you may return target card from your graveyard to your hand.",
        color_identity=["G"],
        colors=["G"],
        keywords=[""],
        is_legendary=False,
        edhrec_rank=50,
        functional_categories=["recursion"],
        mechanics=["etb_trigger", "recursion"],
        themes=["graveyard_value"],
    )


@pytest.fixture
def sample_commander() -> Commander:
    """Sample commander for testing."""
    return Commander(
        name="Muldrotha, the Gravetide",
        mana_cost="{2}{B}{G}{U}",
        cmc=5,
        type_line="Legendary Creature — Elemental",
        oracle_text="During each of your turns, you may play cards from your graveyard.",
        color_identity=["B", "G", "U"],
        colors=["B", "G", "U"],
        keywords=[],
        is_legendary=True,
        edhrec_rank=100,
        power=6,
        toughness=6,
        functional_categories=["recursion", "value"],
        mechanics=["recursion", "graveyard_interaction"],
        themes=["graveyard_value", "reanimation"],
    )


@pytest.fixture
def muldrotha_commander_name() -> str:
    """Muldrotha commander name for integration tests."""
    return "Muldrotha, the Gravetide"


@pytest.fixture
def color_identity_blue_black() -> list[str]:
    """Blue-black color identity for tests."""
    return ["U", "B"]


@pytest.fixture
def mock_connection():
    """Mock Neo4j connection for service tests."""
    conn = MagicMock()
    session = MagicMock()
    conn.session.return_value.__enter__ = MagicMock(return_value=session)
    conn.session.return_value.__exit__ = MagicMock(return_value=False)

    sample_records = [
        {
            "card_name": "Eternal Witness",
            "score": 0.85,
            "mechanic_overlap_count": 3,
            "has_color_match": True,
            "edhrec_rank": 50,
        },
        {
            "card_name": "Satyr Wayfinder",
            "score": 0.72,
            "mechanic_overlap_count": 2,
            "has_color_match": True,
            "edhrec_rank": 120,
        },
        {
            "card_name": "Mulldrifter",
            "score": 0.65,
            "mechanic_overlap_count": 1,
            "has_color_match": True,
            "edhrec_rank": 80,
        },
    ]

    # Make records behave like neo4j Record objects (dict-like)
    mock_records = []
    for rec in sample_records:
        mock_rec = MagicMock()
        mock_rec.__getitem__ = lambda self, key, r=rec: r[key]
        mock_rec.get = lambda key, default=None, r=rec: r.get(key, default)
        mock_rec.data.return_value = rec
        mock_records.append(mock_rec)

    result = MagicMock()
    result.__iter__ = MagicMock(return_value=iter(mock_records))
    session.run.return_value = result

    return conn
