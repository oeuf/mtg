"""Validation runner for deck recommendations."""

from src.graph.connection import Neo4jConnection
from src.synergy.queries import DeckbuildingQueries
from src.validation.metrics import mean_reciprocal_rank, overlap_at_k, find_missing_cards


class DeckValidator:
    """Validate recommendation quality against reference decks."""

    def __init__(self, conn: Neo4jConnection):
        """Initialize with Neo4j connection."""
        self.conn = conn

    def get_recommendations(
        self,
        commander_name: str,
        limit: int = 500
    ) -> list[str]:
        """Get ranked card recommendations for a commander.

        Returns:
            Ordered list of card names
        """
        # Try v2 query first (GDS-enhanced), fall back to v1
        try:
            results = DeckbuildingQueries.find_synergistic_cards_v2(
                self.conn,
                commander_name=commander_name,
                max_cmc=10,  # No CMC filter for validation
                limit=limit
            )
        except Exception:
            results = DeckbuildingQueries.find_synergistic_cards(
                self.conn,
                commander_name=commander_name,
                max_cmc=10,
                min_strength=0.0,
                limit=limit
            )

        return [r["name"] for r in results]

    def validate(
        self,
        reference_cards: set[str],
        commander_name: str,
        top_k: int = 100
    ) -> dict:
        """Run validation against reference deck.

        Args:
            reference_cards: Set of cards that should be recommended
            commander_name: Commander to get recommendations for
            top_k: Number of recommendations to consider

        Returns:
            Dictionary with validation metrics
        """
        # Get recommendations
        recommendations = self.get_recommendations(commander_name, limit=500)

        # Calculate metrics
        mrr = mean_reciprocal_rank(reference_cards, recommendations)

        overlaps = {}
        for k in [50, 100, 200, 300]:
            overlaps[f"overlap_{k}"] = overlap_at_k(reference_cards, recommendations, k)

        missing = find_missing_cards(
            reference_cards,
            recommendations,
            k=top_k,
            include_ranks=True
        )

        return {
            "commander": commander_name,
            "reference_count": len(reference_cards),
            "recommendations_count": len(recommendations),
            "mrr": mrr,
            **overlaps,
            "missing_cards": missing[:20],  # Top 20 missing
            "found_in_top_100": int(overlaps["overlap_100"] * len(reference_cards))
        }

    def print_report(self, result: dict):
        """Print formatted validation report."""
        print("\n" + "=" * 60)
        print("VALIDATION REPORT")
        print("=" * 60)
        print(f"\nCommander: {result['commander']}")
        print(f"Reference deck: {result['reference_count']} cards")
        print(f"Recommendations: {result['recommendations_count']} cards")

        print(f"\n--- Metrics ---")
        print(f"Mean Reciprocal Rank: {result['mrr']:.3f}")
        print(f"Found in top 50:  {result['overlap_50'] * 100:.1f}%")
        print(f"Found in top 100: {result['overlap_100'] * 100:.1f}%")
        print(f"Found in top 200: {result['overlap_200'] * 100:.1f}%")
        print(f"Found in top 300: {result['overlap_300'] * 100:.1f}%")

        if result['missing_cards']:
            print(f"\n--- Missing from Top 100 (showing first 10) ---")
            for card, rank in result['missing_cards'][:10]:
                if rank:
                    print(f"  {card} (actual rank: {rank})")
                else:
                    print(f"  {card} (not in recommendations)")

        print("\n" + "=" * 60)
