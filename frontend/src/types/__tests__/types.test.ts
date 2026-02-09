import { describe, it, expect } from "vitest";
import type {
  Card,
  CardSearchFilters,
  Commander,
  CommanderStats,
  CommanderRecommendation,
  SynergyDimensions,
  SynergyResponse,
  SimilarCardResponse,
  RecommendationResponse,
  DeckShell,
  DeckAnalysis,
  BuildDeckRequest,
  DeckValidation,
} from "../index";

describe("Card types", () => {
  it("Card has all required fields", () => {
    const card: Card = {
      name: "Muldrotha, the Gravetide",
      mana_cost: "{3}{B}{G}{U}",
      cmc: 6,
      type_line: "Legendary Creature — Elemental Avatar",
      oracle_text: "During each of your turns, you may play...",
      color_identity: ["B", "G", "U"],
      colors: ["B", "G", "U"],
      keywords: [],
      is_legendary: true,
      edhrec_rank: 5,
      functional_categories: ["recursion"],
      mechanics: ["graveyard_cast"],
      themes: ["graveyard"],
      archetype: "sultai-graveyard",
      popularity_score: 0.95,
    };
    expect(card.name).toBe("Muldrotha, the Gravetide");
    expect(card.cmc).toBe(6);
    expect(card.color_identity).toHaveLength(3);
    expect(card.is_legendary).toBe(true);
  });

  it("Card supports null optional fields", () => {
    const card: Card = {
      name: "Forest",
      mana_cost: "",
      cmc: 0,
      type_line: "Basic Land — Forest",
      oracle_text: "",
      color_identity: [],
      colors: [],
      keywords: [],
      is_legendary: false,
      edhrec_rank: null,
      functional_categories: [],
      mechanics: [],
      themes: [],
      archetype: null,
      popularity_score: 0.0,
    };
    expect(card.edhrec_rank).toBeNull();
    expect(card.archetype).toBeNull();
  });

  it("CardSearchFilters has pagination defaults", () => {
    const filters: CardSearchFilters = {
      page: 1,
      limit: 20,
    };
    expect(filters.page).toBe(1);
    expect(filters.limit).toBe(20);
    expect(filters.colors).toBeUndefined();
  });
});

describe("Commander types", () => {
  it("Commander extends Card with power/toughness", () => {
    const commander: Commander = {
      name: "Muldrotha, the Gravetide",
      mana_cost: "{3}{B}{G}{U}",
      cmc: 6,
      type_line: "Legendary Creature — Elemental Avatar",
      oracle_text: "During each of your turns, you may play...",
      color_identity: ["B", "G", "U"],
      colors: ["B", "G", "U"],
      keywords: [],
      is_legendary: true,
      edhrec_rank: 5,
      functional_categories: [],
      mechanics: [],
      themes: [],
      archetype: null,
      popularity_score: 0.9,
      power: 6,
      toughness: 6,
    };
    expect(commander.power).toBe(6);
    expect(commander.toughness).toBe(6);
    expect(commander.is_legendary).toBe(true);
  });

  it("CommanderStats has all fields", () => {
    const stats: CommanderStats = {
      name: "Muldrotha, the Gravetide",
      color_identity: ["B", "G", "U"],
      card_count_in_database: 150,
      edhrec_rank: 5,
      popularity_percentile: 99.5,
    };
    expect(stats.card_count_in_database).toBe(150);
    expect(stats.popularity_percentile).toBe(99.5);
  });

  it("CommanderRecommendation has all fields", () => {
    const rec: CommanderRecommendation = {
      card_name: "Eternal Witness",
      reason: "Strong ETB synergy",
      synergy_score: 0.85,
      mechanic_match: true,
      role_match: true,
    };
    expect(rec.synergy_score).toBe(0.85);
    expect(rec.mechanic_match).toBe(true);
  });
});

describe("Synergy types", () => {
  it("SynergyDimensions has all 7 dimensions", () => {
    const dims: SynergyDimensions = {
      mechanic_overlap: 0.8,
      role_compatibility: 0.7,
      theme_alignment: 0.6,
      zone_chain: 0.5,
      phase_alignment: 0.4,
      color_compatibility: 0.3,
      type_synergy: 0.2,
    };
    expect(Object.keys(dims)).toHaveLength(7);
  });

  it("SynergyResponse nests dimensions", () => {
    const response: SynergyResponse = {
      card_name: "Eternal Witness",
      synergy_score: 0.78,
      dimensions: {
        mechanic_overlap: 0.8,
        role_compatibility: 0.7,
        theme_alignment: 0.6,
        zone_chain: 0.5,
        phase_alignment: 0.4,
        color_compatibility: 0.3,
        type_synergy: 0.2,
      },
      explanation: "Strong ETB trigger synergy",
    };
    expect(response.dimensions.mechanic_overlap).toBe(0.8);
    expect(response.explanation).toBe("Strong ETB trigger synergy");
  });

  it("SimilarCardResponse has all fields", () => {
    const similar: SimilarCardResponse = {
      card_name: "Necropotence",
      similarity_score: 0.92,
      reason: null,
    };
    expect(similar.similarity_score).toBe(0.92);
    expect(similar.reason).toBeNull();
  });

  it("RecommendationResponse has all fields", () => {
    const rec: RecommendationResponse = {
      card_name: "Sol Ring",
      synergy_score: 0.6,
      category: "role-based",
      mechanic_overlap_count: 2,
      has_color_match: false,
      edhrec_rank: 1,
    };
    expect(rec.category).toBe("role-based");
    expect(rec.has_color_match).toBe(false);
  });
});

describe("Deck types", () => {
  it("DeckShell has commander and cards", () => {
    const deck: DeckShell = {
      commander: {
        name: "Muldrotha, the Gravetide",
        mana_cost: "{3}{B}{G}{U}",
        cmc: 6,
        type_line: "Legendary Creature — Elemental Avatar",
        oracle_text: "",
        color_identity: ["B", "G", "U"],
        colors: ["B", "G", "U"],
        keywords: [],
        is_legendary: true,
        edhrec_rank: null,
        functional_categories: [],
        mechanics: [],
        themes: [],
        archetype: null,
        popularity_score: 0.9,
        power: 6,
        toughness: 6,
      },
      cards: [],
    };
    expect(deck.commander.name).toBe("Muldrotha, the Gravetide");
    expect(deck.cards).toHaveLength(0);
  });

  it("DeckAnalysis has distribution maps", () => {
    const analysis: DeckAnalysis = {
      total_cards: 100,
      avg_cmc: 3.2,
      color_distribution: { B: 30, G: 25, U: 20 },
      type_distribution: { Creature: 35, Instant: 10, Sorcery: 8 },
      role_distribution: { ramp: 12, draw: 10, removal: 8 },
      mana_curve: { "0": 5, "1": 10, "2": 15, "3": 20, "4": 15, "5": 10 },
    };
    expect(analysis.total_cards).toBe(100);
    expect(analysis.color_distribution["B"]).toBe(30);
  });

  it("BuildDeckRequest has all fields", () => {
    const req: BuildDeckRequest = {
      commander: "Muldrotha, the Gravetide",
      max_cmc: 4,
      min_strength: 0.7,
    };
    expect(req.commander).toBe("Muldrotha, the Gravetide");
  });

  it("DeckValidation has all fields", () => {
    const validation: DeckValidation = {
      is_valid: true,
      errors: [],
      warnings: ["Missing card draw"],
      color_identity: ["B", "G", "U"],
    };
    expect(validation.is_valid).toBe(true);
    expect(validation.warnings).toHaveLength(1);
  });
});
