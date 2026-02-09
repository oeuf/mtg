/** Represents a Magic: The Gathering card. */
export interface Card {
  name: string;
  mana_cost: string;
  cmc: number;
  type_line: string;
  oracle_text: string;
  color_identity: string[];
  colors: string[];
  keywords: string[];
  is_legendary: boolean;
  edhrec_rank: number | null;
  functional_categories: string[];
  mechanics: string[];
  themes: string[];
  archetype: string | null;
  popularity_score: number;
}

/** Filters for card search. */
export interface CardSearchFilters {
  colors?: string[] | null;
  color_identity?: string[] | null;
  types?: string[] | null;
  cmc_min?: number | null;
  cmc_max?: number | null;
  rarity?: string[] | null;
  mechanics?: string[] | null;
  roles?: string[] | null;
  text_search?: string | null;
  page: number;
  limit: number;
}
