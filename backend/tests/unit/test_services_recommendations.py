"""Tests for RecommendationService - TDD RED phase.

Tests ensemble recommendation functions. These tests will fail until
backend/app/services/recommendation_service.py is implemented.
"""

import pytest
from app.models.synergy import RecommendationResponse


class TestRecommendationService:
    """RecommendationService method tests - TDD RED phase."""

    def test_get_embedding_recommendations_returns_cards(self, mock_connection):
        """RecommendationService.get_embedding_recommendations returns embedding-based recommendations."""
        from app.services.recommendation_service import RecommendationService
        service = RecommendationService(mock_connection)
        result = service.get_embedding_recommendations(
            commander_name="Muldrotha, the Gravetide",
            top_k=20
        )
        assert isinstance(result, list)
        assert all(isinstance(c, RecommendationResponse) for c in result)
        assert len(result) <= 20
        if result:
            assert all(0 <= c.synergy_score <= 1 for c in result)
            assert all(c.category == "embedding_similarity" for c in result)

    def test_get_similarity_recommendations_returns_cards(self, mock_connection):
        """RecommendationService.get_similarity_recommendations returns similarity-based recommendations."""
        from app.services.recommendation_service import RecommendationService
        service = RecommendationService(mock_connection)
        result = service.get_similarity_recommendations(
            commander_name="Muldrotha, the Gravetide",
            top_k=20
        )
        assert isinstance(result, list)
        assert all(isinstance(c, RecommendationResponse) for c in result)
        assert len(result) <= 20
        if result:
            assert all(0 <= c.synergy_score <= 1 for c in result)
            assert all(c.category == "similarity_based" for c in result)

    def test_ensemble_recommendations_combines_scores(self, mock_connection):
        """RecommendationService.ensemble_recommendations combines all recommendation approaches."""
        from app.services.recommendation_service import RecommendationService
        service = RecommendationService(mock_connection)
        result = service.ensemble_recommendations(
            commander_name="Muldrotha, the Gravetide",
            top_k=30,
            weights={
                "mechanic_based": 0.3,
                "embedding_similarity": 0.3,
                "role_based": 0.25,
                "community_boost": 0.15
            }
        )
        assert isinstance(result, list)
        assert len(result) <= 30
        # Results should be sorted by score descending
        if len(result) > 1:
            scores = [c.synergy_score for c in result]
            assert scores == sorted(scores, reverse=True)
        # All scores should be 0-1
        assert all(0 <= c.synergy_score <= 1 for c in result)

    def test_get_role_based_recommendations_returns_cards(self, mock_connection):
        """RecommendationService includes role-based recommendations."""
        from app.services.recommendation_service import RecommendationService
        service = RecommendationService(mock_connection)
        result = service.ensemble_recommendations(
            commander_name="Muldrotha, the Gravetide",
            top_k=30
        )
        # Should include cards from different roles
        categories = {c.category for c in result}
        assert "mechanic_based" in categories or "embedding_similarity" in categories
        # Each recommendation should have explanation or role info
        assert all(c.category is not None for c in result)
