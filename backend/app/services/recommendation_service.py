"""Recommendation service for deck building suggestions."""

from typing import Dict, List, Optional

from app.models.synergy import RecommendationResponse


class RecommendationService:
    """Service that provides card recommendations using Neo4j graph data."""

    DEFAULT_WEIGHTS = {
        "mechanic_based": 0.3,
        "embedding_similarity": 0.3,
        "role_based": 0.25,
        "community_boost": 0.15,
    }

    def __init__(self, connection):
        self.connection = connection

    def _query(self, cypher: str, **params) -> list:
        with self.connection.session() as session:
            result = session.run(cypher, **params)
            return list(result)

    def get_embedding_recommendations(
        self, commander_name: str, top_k: int = 20
    ) -> List[RecommendationResponse]:
        records = self._query(
            "MATCH (c:Card {name: $name})-[s:EMBEDDING_SIMILAR]->(r:Card) "
            "RETURN r.name AS card_name, s.score AS score, "
            "coalesce(s.mechanic_overlap_count, 0) AS mechanic_overlap_count, "
            "coalesce(s.has_color_match, false) AS has_color_match, "
            "r.edhrec_rank AS edhrec_rank "
            "ORDER BY s.score DESC LIMIT $top_k",
            name=commander_name,
            top_k=top_k,
        )
        return [
            RecommendationResponse(
                card_name=rec["card_name"],
                synergy_score=min(1.0, max(0.0, rec["score"])),
                category="embedding_similarity",
                mechanic_overlap_count=rec.get("mechanic_overlap_count", 0),
                has_color_match=rec.get("has_color_match", False),
                edhrec_rank=rec.get("edhrec_rank"),
            )
            for rec in records
        ]

    def get_similarity_recommendations(
        self, commander_name: str, top_k: int = 20
    ) -> List[RecommendationResponse]:
        records = self._query(
            "MATCH (c:Card {name: $name})-[s:SYNERGIZES_WITH]->(r:Card) "
            "RETURN r.name AS card_name, s.synergy_score AS score, "
            "coalesce(s.mechanic_overlap_count, 0) AS mechanic_overlap_count, "
            "coalesce(s.has_color_match, false) AS has_color_match, "
            "r.edhrec_rank AS edhrec_rank "
            "ORDER BY s.synergy_score DESC LIMIT $top_k",
            name=commander_name,
            top_k=top_k,
        )
        return [
            RecommendationResponse(
                card_name=rec["card_name"],
                synergy_score=min(1.0, max(0.0, rec["score"])),
                category="similarity_based",
                mechanic_overlap_count=rec.get("mechanic_overlap_count", 0),
                has_color_match=rec.get("has_color_match", False),
                edhrec_rank=rec.get("edhrec_rank"),
            )
            for rec in records
        ]

    def ensemble_recommendations(
        self,
        commander_name: str,
        top_k: int = 30,
        weights: Optional[Dict[str, float]] = None,
    ) -> List[RecommendationResponse]:
        if weights is None:
            weights = self.DEFAULT_WEIGHTS.copy()

        # Gather recommendations from each source
        card_scores: Dict[str, Dict] = {}

        embedding_recs = self.get_embedding_recommendations(commander_name, top_k=top_k)
        for rec in embedding_recs:
            card_scores[rec.card_name] = {
                "score": rec.synergy_score * weights.get("embedding_similarity", 0.3),
                "category": "embedding_similarity",
                "mechanic_overlap_count": rec.mechanic_overlap_count,
                "has_color_match": rec.has_color_match,
                "edhrec_rank": rec.edhrec_rank,
            }

        similarity_recs = self.get_similarity_recommendations(commander_name, top_k=top_k)
        for rec in similarity_recs:
            if rec.card_name in card_scores:
                card_scores[rec.card_name]["score"] += (
                    rec.synergy_score * weights.get("mechanic_based", 0.3)
                )
                card_scores[rec.card_name]["category"] = "mechanic_based"
            else:
                card_scores[rec.card_name] = {
                    "score": rec.synergy_score * weights.get("mechanic_based", 0.3),
                    "category": "mechanic_based",
                    "mechanic_overlap_count": rec.mechanic_overlap_count,
                    "has_color_match": rec.has_color_match,
                    "edhrec_rank": rec.edhrec_rank,
                }

        # Normalize scores to 0-1
        if card_scores:
            max_score = max(d["score"] for d in card_scores.values())
            if max_score > 0:
                for name in card_scores:
                    card_scores[name]["score"] = card_scores[name]["score"] / max_score

        # Build results sorted by score descending
        results = []
        for card_name, data in card_scores.items():
            results.append(
                RecommendationResponse(
                    card_name=card_name,
                    synergy_score=min(1.0, max(0.0, data["score"])),
                    category=data["category"],
                    mechanic_overlap_count=data.get("mechanic_overlap_count", 0),
                    has_color_match=data.get("has_color_match", False),
                    edhrec_rank=data.get("edhrec_rank"),
                )
            )

        results.sort(key=lambda r: r.synergy_score, reverse=True)
        return results[:top_k]
