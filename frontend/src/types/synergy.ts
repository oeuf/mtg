/** 7-dimensional synergy breakdown. */
export interface SynergyDimensions {
  mechanic_overlap: number;
  role_compatibility: number;
  theme_alignment: number;
  zone_chain: number;
  phase_alignment: number;
  color_compatibility: number;
  type_synergy: number;
}

/** Synergy analysis for a card with another card. */
export interface SynergyResponse {
  card_name: string;
  synergy_score: number;
  dimensions: SynergyDimensions;
  explanation: string | null;
}

/** Response for similar cards endpoint. */
export interface SimilarCardResponse {
  card_name: string;
  similarity_score: number;
  reason: string | null;
}

/** Combo involving a card. */
export interface ComboResponse {
  name: string;
  combo_name: string | null;
  description: string | null;
}

/** Recommendation response for deck building. */
export interface RecommendationResponse {
  card_name: string;
  synergy_score: number;
  category: string;
  mechanic_overlap_count: number;
  has_color_match: boolean;
  edhrec_rank: number | null;
}
