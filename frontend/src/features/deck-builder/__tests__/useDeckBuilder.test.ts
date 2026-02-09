import { describe, it, expect, beforeEach } from 'vitest';
import { useDeckBuilder } from '../useDeckBuilder';
import { extractPrimaryType } from '../useDeckBuilder';
import type { Card, Commander } from '../../../types';

function makeCard(overrides: Partial<Card> = {}): Card {
  return {
    name: 'Test Card',
    mana_cost: '{1}{B}',
    cmc: 2,
    type_line: 'Creature — Human',
    oracle_text: 'Some text',
    color_identity: ['B'],
    colors: ['B'],
    keywords: [],
    is_legendary: false,
    edhrec_rank: null,
    functional_categories: [],
    mechanics: [],
    themes: [],
    archetype: null,
    popularity_score: 0,
    ...overrides,
  };
}

function makeCommander(overrides: Partial<Commander> = {}): Commander {
  return {
    name: 'Test Commander',
    mana_cost: '{2}{B}{G}',
    cmc: 4,
    type_line: 'Legendary Creature — Elf Shaman',
    oracle_text: 'Commander text',
    color_identity: ['B', 'G'],
    colors: ['B', 'G'],
    keywords: [],
    is_legendary: true,
    edhrec_rank: 100,
    functional_categories: [],
    mechanics: [],
    themes: [],
    archetype: null,
    popularity_score: 50,
    power: 3,
    toughness: 3,
    ...overrides,
  };
}

describe('useDeckBuilder', () => {
  beforeEach(() => {
    useDeckBuilder.setState({
      commander: null,
      deck: [],
    });
  });

  describe('setCommander', () => {
    it('stores commander', () => {
      const cmdr = makeCommander({ name: 'Muldrotha, the Gravetide' });
      useDeckBuilder.getState().setCommander(cmdr);
      expect(useDeckBuilder.getState().commander).toEqual(cmdr);
    });
  });

  describe('addCard', () => {
    it('adds card to deck', () => {
      const card = makeCard({ name: 'Sol Ring' });
      useDeckBuilder.getState().addCard(card);
      expect(useDeckBuilder.getState().deck).toHaveLength(1);
      expect(useDeckBuilder.getState().deck[0].name).toBe('Sol Ring');
    });

    it('prevents duplicates by name', () => {
      const card = makeCard({ name: 'Sol Ring' });
      useDeckBuilder.getState().addCard(card);
      useDeckBuilder.getState().addCard(card);
      expect(useDeckBuilder.getState().deck).toHaveLength(1);
    });

    it('respects 99 card limit', () => {
      for (let i = 0; i < 99; i++) {
        useDeckBuilder.getState().addCard(makeCard({ name: `Card ${i}` }));
      }
      expect(useDeckBuilder.getState().deck).toHaveLength(99);

      useDeckBuilder.getState().addCard(makeCard({ name: 'Card 100' }));
      expect(useDeckBuilder.getState().deck).toHaveLength(99);
    });
  });

  describe('removeCard', () => {
    it('removes card by name', () => {
      useDeckBuilder.getState().addCard(makeCard({ name: 'Sol Ring' }));
      useDeckBuilder.getState().addCard(makeCard({ name: 'Arcane Signet' }));
      expect(useDeckBuilder.getState().deck).toHaveLength(2);

      useDeckBuilder.getState().removeCard('Sol Ring');
      expect(useDeckBuilder.getState().deck).toHaveLength(1);
      expect(useDeckBuilder.getState().deck[0].name).toBe('Arcane Signet');
    });
  });

  describe('clearDeck', () => {
    it('empties deck', () => {
      useDeckBuilder.getState().addCard(makeCard({ name: 'Sol Ring' }));
      useDeckBuilder.getState().addCard(makeCard({ name: 'Arcane Signet' }));
      useDeckBuilder.getState().setCommander(makeCommander());
      expect(useDeckBuilder.getState().deck).toHaveLength(2);

      useDeckBuilder.getState().clearDeck();
      expect(useDeckBuilder.getState().deck).toHaveLength(0);
      expect(useDeckBuilder.getState().commander).toBeNull();
    });
  });

  describe('getDeckByType', () => {
    it('groups cards by primary type', () => {
      useDeckBuilder.getState().addCard(makeCard({ name: 'Elvish Mystic', type_line: 'Creature — Elf Druid' }));
      useDeckBuilder.getState().addCard(makeCard({ name: 'Counterspell', type_line: 'Instant' }));
      useDeckBuilder.getState().addCard(makeCard({ name: 'Sol Ring', type_line: 'Artifact' }));
      useDeckBuilder.getState().addCard(makeCard({ name: 'Rhystic Study', type_line: 'Enchantment' }));
      useDeckBuilder.getState().addCard(makeCard({ name: 'Forest', type_line: 'Basic Land — Forest' }));
      useDeckBuilder.getState().addCard(makeCard({ name: 'Cultivate', type_line: 'Sorcery' }));

      const grouped = useDeckBuilder.getState().getDeckByType();
      expect(grouped['Creature']).toHaveLength(1);
      expect(grouped['Creature'][0].name).toBe('Elvish Mystic');
      expect(grouped['Instant']).toHaveLength(1);
      expect(grouped['Artifact']).toHaveLength(1);
      expect(grouped['Enchantment']).toHaveLength(1);
      expect(grouped['Land']).toHaveLength(1);
      expect(grouped['Sorcery']).toHaveLength(1);
    });
  });

  describe('getDeckStats', () => {
    it('computes totalCards, avgCmc, colorDistribution', () => {
      useDeckBuilder.getState().addCard(makeCard({ name: 'Card A', cmc: 2, colors: ['B'] }));
      useDeckBuilder.getState().addCard(makeCard({ name: 'Card B', cmc: 4, colors: ['G'] }));
      useDeckBuilder.getState().addCard(makeCard({ name: 'Card C', cmc: 6, colors: ['B', 'G'] }));

      const stats = useDeckBuilder.getState().getDeckStats();
      expect(stats.totalCards).toBe(3);
      expect(stats.avgCmc).toBe(4);
      expect(stats.colorDistribution).toEqual({ B: 2, G: 2 });
    });

    it('returns zero avgCmc for empty deck', () => {
      const stats = useDeckBuilder.getState().getDeckStats();
      expect(stats.totalCards).toBe(0);
      expect(stats.avgCmc).toBe(0);
      expect(stats.colorDistribution).toEqual({});
    });
  });
});

describe('extractPrimaryType', () => {
  it('extracts Creature from "Creature — Human Shaman"', () => {
    expect(extractPrimaryType('Creature — Human Shaman')).toBe('Creature');
  });

  it('extracts Enchantment from "Legendary Enchantment"', () => {
    expect(extractPrimaryType('Legendary Enchantment')).toBe('Enchantment');
  });

  it('extracts Creature from "Artifact Creature — Golem" (Creature takes priority)', () => {
    expect(extractPrimaryType('Artifact Creature — Golem')).toBe('Creature');
  });

  it('extracts Instant from "Instant"', () => {
    expect(extractPrimaryType('Instant')).toBe('Instant');
  });

  it('extracts Land from "Basic Land — Forest"', () => {
    expect(extractPrimaryType('Basic Land — Forest')).toBe('Land');
  });

  it('returns Other for unknown type line', () => {
    expect(extractPrimaryType('Conspiracy')).toBe('Other');
  });
});
