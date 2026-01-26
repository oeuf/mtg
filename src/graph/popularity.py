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

    def update_all_cards(self, conn: Neo4jConnection):
        """Update popularity_score for all cards in graph."""
        print("Updating card popularity scores...")

        query = """
        MATCH (c:Card)
        WHERE c.edhrec_rank IS NOT NULL
        SET c.popularity_score = 1.0 - (log(toFloat(c.edhrec_rank)) / log(30000.0))
        RETURN count(c) AS updated
        """

        result = conn.execute_query(query)
        updated = result[0]["updated"] if result else 0

        query_no_rank = """
        MATCH (c:Card)
        WHERE c.edhrec_rank IS NULL
        SET c.popularity_score = 0.0
        RETURN count(c) AS updated
        """

        result2 = conn.execute_query(query_no_rank)
        updated_no_rank = result2[0]["updated"] if result2 else 0

        print(f"✓ Updated {updated} cards with EDHREC scores")
        print(f"✓ Set {updated_no_rank} cards without EDHREC to 0.0")
