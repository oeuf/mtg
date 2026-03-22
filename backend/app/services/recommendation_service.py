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
            "MATCH (c {name: $name})-[s:SYNERGIZES_WITH]-(r:Card) "
            "WHERE (c:Card OR c:Commander) "
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

    def get_role_recommendations(
        self, commander_name: str, top_k: int = 20
    ) -> List[RecommendationResponse]:
        """Get cards that share roles with the commander."""
        records = self._query(
            "MATCH (cmd)-[:FILLS_ROLE]->(r:Functional_Role) "
            "<-[:FILLS_ROLE]-(card:Card) "
            "WHERE (cmd:Card OR cmd:Commander) AND cmd.name = $name "
            "AND NOT card:Commander AND card.name <> $name "
            "RETURN card.name AS card_name, "
            "coalesce(card.edhrec_rank, 99999) AS edhrec_rank, "
            "count(r) AS shared_roles "
            "ORDER BY shared_roles DESC, edhrec_rank ASC "
            "LIMIT $top_k",
            name=commander_name,
            top_k=top_k,
        )
        return [
            RecommendationResponse(
                card_name=rec["card_name"],
                synergy_score=min(1.0, rec["shared_roles"] / 5.0),  # normalize: 5+ shared roles = 1.0
                category="role_based",
                mechanic_overlap_count=0,
                has_color_match=False,
                edhrec_rank=rec.get("edhrec_rank"),
            )
            for rec in records
        ]

    def get_community_recommendations(
        self, commander_name: str, top_k: int = 20
    ) -> List[RecommendationResponse]:
        """Get highly-ranked community cards in the commander's color identity."""
        records = self._query(
            "MATCH (cmd) "
            "WHERE (cmd:Card OR cmd:Commander) AND cmd.name = $name "
            "MATCH (card:Card) "
            "WHERE NOT card:Commander "
            "AND card.edhrec_rank IS NOT NULL "
            "AND ALL(c IN card.color_identity WHERE c IN cmd.color_identity) "
            "RETURN card.name AS card_name, card.edhrec_rank AS edhrec_rank "
            "ORDER BY card.edhrec_rank ASC "
            "LIMIT $top_k",
            name=commander_name,
            top_k=top_k,
        )
        # Convert rank to score: rank 1 = 1.0, rank 5000 = 0.0
        max_rank = 5000.0
        return [
            RecommendationResponse(
                card_name=rec["card_name"],
                synergy_score=max(0.0, 1.0 - (rec["edhrec_rank"] / max_rank)),
                category="community_boost",
                mechanic_overlap_count=0,
                has_color_match=True,
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

        card_scores: Dict[str, Dict] = {}

        def _merge(recs, weight_key):
            for rec in recs:
                w = weights.get(weight_key, 0.0)
                if rec.card_name in card_scores:
                    card_scores[rec.card_name]["score"] += rec.synergy_score * w
                else:
                    card_scores[rec.card_name] = {
                        "score": rec.synergy_score * w,
                        "category": rec.category,
                        "mechanic_overlap_count": rec.mechanic_overlap_count,
                        "has_color_match": rec.has_color_match,
                        "edhrec_rank": rec.edhrec_rank,
                    }

        _merge(self.get_embedding_recommendations(commander_name, top_k=top_k), "embedding_similarity")
        _merge(self.get_similarity_recommendations(commander_name, top_k=top_k), "mechanic_based")
        _merge(self.get_role_recommendations(commander_name, top_k=top_k), "role_based")
        _merge(self.get_community_recommendations(commander_name, top_k=top_k), "community_boost")

        # No max-normalization — scores already in [0,1] range per source
        results = [
            RecommendationResponse(
                card_name=name,
                synergy_score=min(1.0, max(0.0, data["score"])),
                category=data["category"],
                mechanic_overlap_count=data.get("mechanic_overlap_count", 0),
                has_color_match=data.get("has_color_match", False),
                edhrec_rank=data.get("edhrec_rank"),
            )
            for name, data in card_scores.items()
        ]
        results.sort(key=lambda r: r.synergy_score, reverse=True)
        return results[:top_k]
