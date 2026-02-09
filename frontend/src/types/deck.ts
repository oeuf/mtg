import type { Card } from "./card";
import type { Commander } from "./commander";

/** A deck shell with commander and cards. */
export interface DeckShell {
  commander: Commander;
  cards: Card[];
}

/** Analysis of a deck's composition. */
export interface DeckAnalysis {
  total_cards: number;
  avg_cmc: number;
  color_distribution: Record<string, number>;
  type_distribution: Record<string, number>;
  role_distribution: Record<string, number>;
  mana_curve: Record<string, number>;
}

/** Request to build an initial deck shell. */
export interface BuildDeckRequest {
  commander: string;
  max_cmc: number;
  min_strength: number;
}

/** Result of deck validation. */
export interface DeckValidation {
  is_valid: boolean;
  errors: string[];
  warnings: string[];
  color_identity: string[];
}
