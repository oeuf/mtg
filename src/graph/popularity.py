"""Calculate popularity scores for cards."""

import math
from src.graph.connection import Neo4jConnection


class PopularityScorer:
    """Calculate popularity scores from EDHREC rank."""

    MAX_RANK = 30000.0

    @staticmethod
    def calculate_edhrec_score(edhrec_rank: int | None) -> float:
        """
        Convert EDHREC rank to popularity score (0.0-1.0).
        Lower rank = more popular = higher score.
        """
        if edhrec_rank is None:
            return 0.0

        rank = max(1, min(edhrec_rank, PopularityScorer.MAX_RANK))
        score = 1.0 - (math.log(rank) / math.log(PopularityScorer.MAX_RANK))
        return max(0.0, min(1.0, score))
