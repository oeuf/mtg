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

/** Backend wrapper for GET /cards/{name}/similar */
export interface SimilarCardsResponse {
  card: string;
  similar_cards: { name: string; score: number }[];
}

/** Backend wrapper for GET /cards/{name}/synergies */
export interface CardSynergiesResponse {
  card: string;
  synergies: { name: string; score: number }[];
}

/** Backend wrapper for GET /commanders/{name}/synergies */
export interface CommanderSynergiesResponse {
  commander: string;
  synergies: { card_name: string; synergy_score: number }[];
}

/** Backend wrapper for GET /commanders/{name}/recommendations */
export interface CommanderRecommendationsResponse {
  commander: string;
  recommendations: { card_name: string; score: number }[];
}

/** Backend wrapper for GET /mechanics, /themes, /roles */
export interface GraphListResponse {
  total: number;
  mechanics?: { name: string; description: string | null; card_count: number }[];
  themes?: { name: string; description: string | null; card_count: number }[];
  roles?: { name: string; description: string | null; card_count: number }[];
}
