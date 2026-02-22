/**
 * Shared MTG constants used across multiple components.
 */

/** The five MTG mana colors in WUBRG order. */
export const MANA_COLORS = ["W", "U", "B", "R", "G"] as const;

export type ManaColor = (typeof MANA_COLORS)[number];

type BadgeVariant = "mana-W" | "mana-U" | "mana-B" | "mana-R" | "mana-G";

/** Maps a mana color code to its Badge variant string. */
export const colorVariantMap: Record<ManaColor, BadgeVariant> = {
  W: "mana-W",
  U: "mana-U",
  B: "mana-B",
  R: "mana-R",
  G: "mana-G",
};

/**
 * Functional roles used for card filtering and recommendations.
 * The full 7-role list is used in FilterPanel; the first 5 are used in
 * RecommendationsPanel's by-role tab.
 */
export const ROLES: string[] = [
  "Ramp",
  "Draw",
  "Removal",
  "Counterspell",
  "Board Wipe",
  "Tutor",
  "Protection",
];

/** The 5-role subset displayed in the RecommendationsPanel by-role tab. */
export const RECOMMENDATION_ROLES: string[] = ROLES.slice(0, 5);
