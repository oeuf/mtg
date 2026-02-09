import type { Card } from "./card";

/** Represents a legendary creature that can be a Commander. */
export interface Commander extends Card {
  is_legendary: true;
  power: number | null;
  toughness: number | null;
}

/** Statistics about a commander. */
export interface CommanderStats {
  name: string;
  color_identity: string[];
  card_count_in_database: number;
  edhrec_rank: number | null;
  popularity_percentile: number;
}

/** Recommendation for cards in a commander deck. */
export interface CommanderRecommendation {
  card_name: string;
  reason: string;
  synergy_score: number;
  mechanic_match: boolean;
  role_match: boolean;
}
