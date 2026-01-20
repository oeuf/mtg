"""Calculate combined popularity scores from EDHREC rank and precon frequency."""

from typing import Optional


class PopularityCalculator:
    """Calculate card popularity scores."""

    MAX_EDHREC_RANK = 20000  # Normalization cap
    EDHREC_WEIGHT = 0.7
    PRECON_WEIGHT = 0.3

    def __init__(self, total_precons: int):
        """Initialize with total precon count for normalization.

        Args:
            total_precons: Total number of Commander precons parsed
        """
        self.total_precons = total_precons

    def calculate(self, edhrec_rank: Optional[int], precon_count: int) -> float:
        """Calculate combined popularity score.

        Args:
            edhrec_rank: EDHREC popularity rank (lower = more popular), or None
            precon_count: Number of precons this card appears in

        Returns:
            Float between 0.0 and 1.0 (higher = more popular)
        """
        # Normalize EDHREC rank (invert so higher = better)
        if edhrec_rank is None:
            edhrec_score = 0.5  # Default for unranked cards
        else:
            edhrec_score = max(0, 1 - (edhrec_rank / self.MAX_EDHREC_RANK))

        # Precon frequency (already 0-1 range)
        if self.total_precons > 0:
            precon_score = precon_count / self.total_precons
        else:
            precon_score = 0

        # Weighted combination
        return self.EDHREC_WEIGHT * edhrec_score + self.PRECON_WEIGHT * precon_score
