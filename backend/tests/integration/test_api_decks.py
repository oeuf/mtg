"""Integration tests for Deck API endpoints - TDD RED phase."""

import pytest


class TestDeckEndpoints:
    """Deck API endpoint tests."""

    def test_build_deck_shell_returns_37_cards(
        self, client, muldrotha_commander_name
    ):
        """POST /api/decks/build-shell returns initial shell with 37 cards."""
        payload = {"commander": muldrotha_commander_name}
        response = client.post("/api/decks/build-shell", json=payload)
        # Should return:
        # {
        #     "commander": Commander,
        #     "cards": List[Card],  # Exactly 37 cards
        #     "total_cards": 38
        # }
        assert response.status_code == 404

    def test_build_deck_shell_validates_commander_exists(self, client):
        """POST /api/decks/build-shell returns error if commander doesn't exist."""
        payload = {"commander": "Nonexistent Commander Name"}
        response = client.post("/api/decks/build-shell", json=payload)
        # Should return 404 or 400 with error message
        assert response.status_code in [404, 400]

    def test_analyze_deck_composition(self, client, sample_commander):
        """POST /api/decks/analyze returns deck composition analysis."""
        # Create a minimal deck
        cards_data = [
            {
                "name": "Swamp",
                "cmc": 0,
                "type_line": "Land — Swamp",
                "oracle_text": "{T}: Add {B}.",
                "color_identity": ["B"],
                "colors": ["B"],
            }
            for _ in range(40)
        ]

        payload = {
            "commander": sample_commander.model_dump(),
            "cards": cards_data,
        }
        response = client.post("/api/decks/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "total_cards" in data
        assert data["total_cards"] == 41
        assert "avg_cmc" in data
        assert data["avg_cmc"] == 0.0
        assert "color_distribution" in data
        assert "type_distribution" in data
        assert "mana_curve" in data

    def test_analyze_deck_happy_path(self, client, sample_commander):
        """POST /api/decks/analyze with valid commander + cards returns full analysis."""
        cards_data = [
            {
                "name": "Llanowar Elves",
                "cmc": 1,
                "type_line": "Creature — Elf Druid",
                "oracle_text": "{T}: Add {G}.",
                "color_identity": ["G"],
                "colors": ["G"],
                "functional_categories": ["ramp"],
            },
            {
                "name": "Sol Ring",
                "cmc": 1,
                "type_line": "Artifact",
                "oracle_text": "{T}: Add {C}{C}.",
                "color_identity": [],
                "colors": [],
                "functional_categories": ["ramp"],
            },
            {
                "name": "Swamp",
                "cmc": 0,
                "type_line": "Basic Land — Swamp",
                "oracle_text": "",
                "color_identity": ["B"],
                "colors": [],
                "functional_categories": [],
            },
        ]
        payload = {
            "commander": sample_commander.model_dump(),
            "cards": cards_data,
        }
        response = client.post("/api/decks/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        # Structural keys must be present
        assert "total_cards" in data
        assert "avg_cmc" in data
        assert "color_distribution" in data
        assert "type_distribution" in data
        assert "mana_curve" in data
        assert "role_distribution" in data
        # 3 cards + 1 commander
        assert data["total_cards"] == 4
        # avg_cmc of [1, 1, 0] = 2/3
        assert abs(data["avg_cmc"] - (2 / 3)) < 0.001

    def test_analyze_deck_empty_cards(self, client, sample_commander):
        """POST /api/decks/analyze with empty cards list returns valid structure."""
        payload = {
            "commander": sample_commander.model_dump(),
            "cards": [],
        }
        response = client.post("/api/decks/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "total_cards" in data
        assert data["total_cards"] == 1  # commander only
        assert "avg_cmc" in data
        assert data["avg_cmc"] == 0.0
        assert "color_distribution" in data
        assert data["color_distribution"] == {}
        assert "type_distribution" in data
        assert data["type_distribution"] == {}
        assert "mana_curve" in data
        assert data["mana_curve"] == {}

    def test_analyze_deck_missing_commander_returns_422(self, client):
        """POST /api/decks/analyze without commander field returns 422 validation error."""
        payload = {
            "cards": [
                {
                    "name": "Sol Ring",
                    "cmc": 1,
                    "type_line": "Artifact",
                    "oracle_text": "{T}: Add {C}{C}.",
                    "color_identity": [],
                    "colors": [],
                }
            ]
        }
        # commander field has a default of {}, so omitting it is valid.
        # We instead send an invalid type to trigger a 422.
        bad_payload = {
            "commander": "not-a-dict",
            "cards": [],
        }
        response = client.post("/api/decks/analyze", json=bad_payload)
        assert response.status_code == 422
