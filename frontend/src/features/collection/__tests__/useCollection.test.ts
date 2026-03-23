import { describe, it, expect, beforeEach } from 'vitest';
import { useCollection } from '../useCollection';
import type { Card } from '../../../types';

function makeCard(overrides: Partial<Card> = {}): Card {
  return {
    name: 'Sol Ring',
    mana_cost: '{1}',
    cmc: 1,
    type_line: 'Artifact',
    oracle_text: '{T}: Add {C}{C}.',
    color_identity: [],
    colors: [],
    keywords: [],
    is_legendary: false,
    edhrec_rank: 1,
    functional_categories: ['ramp'],
    mechanics: ['mana_ability'],
    themes: [],
    archetype: null,
    popularity_score: 99,
    ...overrides,
  };
}

describe('useCollection', () => {
  beforeEach(() => {
    useCollection.setState({ cards: {} });
  });

  it('starts with empty collection', () => {
    const state = useCollection.getState();
    expect(Object.keys(state.cards)).toHaveLength(0);
  });

  it('addCard adds a card with quantity 1', () => {
    useCollection.getState().addCard(makeCard());
    const state = useCollection.getState();
    expect(state.cards['Sol Ring']).toBeDefined();
    expect(state.cards['Sol Ring'].quantity).toBe(1);
  });

  it('addCard increments quantity for existing card', () => {
    useCollection.getState().addCard(makeCard());
    useCollection.getState().addCard(makeCard());
    const state = useCollection.getState();
    expect(state.cards['Sol Ring'].quantity).toBe(2);
  });

  it('addCard with custom quantity', () => {
    useCollection.getState().addCard(makeCard(), 4);
    const state = useCollection.getState();
    expect(state.cards['Sol Ring'].quantity).toBe(4);
  });

  it('removeCard removes a card', () => {
    useCollection.getState().addCard(makeCard());
    useCollection.getState().removeCard('Sol Ring');
    const state = useCollection.getState();
    expect(state.cards['Sol Ring']).toBeUndefined();
  });

  it('updateQuantity changes card quantity', () => {
    useCollection.getState().addCard(makeCard());
    useCollection.getState().updateQuantity('Sol Ring', 3);
    const state = useCollection.getState();
    expect(state.cards['Sol Ring'].quantity).toBe(3);
  });

  it('hasCard returns true for owned cards', () => {
    useCollection.getState().addCard(makeCard());
    expect(useCollection.getState().hasCard('Sol Ring')).toBe(true);
  });

  it('hasCard returns false for unowned cards', () => {
    expect(useCollection.getState().hasCard('Black Lotus')).toBe(false);
  });

  it('totalCards returns sum of all quantities', () => {
    useCollection.getState().addCard(makeCard(), 4);
    useCollection.getState().addCard(makeCard({ name: 'Arcane Signet' }), 2);
    expect(useCollection.getState().totalCards()).toBe(6);
  });

  it('totalUnique returns number of unique cards', () => {
    useCollection.getState().addCard(makeCard(), 4);
    useCollection.getState().addCard(makeCard({ name: 'Arcane Signet' }), 2);
    expect(useCollection.getState().totalUnique()).toBe(2);
  });
});
