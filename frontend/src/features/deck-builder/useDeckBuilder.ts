import { create } from 'zustand';
import type { Card, Commander } from '../../types';
import { extractPrimaryType } from '../../utils/cardUtils';

export { extractPrimaryType };

interface DeckBuilderState {
  commander: Commander | null;
  deck: Card[];
  setCommander: (commander: Commander) => void;
  addCard: (card: Card) => void;
  removeCard: (cardName: string) => void;
  clearDeck: () => void;
  getDeckByType: () => Record<string, Card[]>;
  getDeckStats: () => { totalCards: number; avgCmc: number; colorDistribution: Record<string, number> };
}

export const useDeckBuilder = create<DeckBuilderState>((set, get) => ({
  commander: null,
  deck: [],

  setCommander: (commander) =>
    set((state) => {
      if (state.commander?.name === commander.name) return { commander };
      return { commander, deck: [] };
    }),

  addCard: (card) =>
    set((state) => {
      if (state.deck.length >= 99) return state;
      if (state.deck.some((c) => c.name === card.name)) return state;
      return { deck: [...state.deck, card] };
    }),

  removeCard: (cardName) =>
    set((state) => ({
      deck: state.deck.filter((c) => c.name !== cardName),
    })),

  clearDeck: () => set({ deck: [], commander: null }),

  getDeckByType: () => {
    const { deck } = get();
    const grouped: Record<string, Card[]> = {};
    for (const card of deck) {
      const type = extractPrimaryType(card.type_line);
      if (!grouped[type]) grouped[type] = [];
      grouped[type].push(card);
    }
    return grouped;
  },

  getDeckStats: () => {
    const { deck } = get();
    const totalCards = deck.length;
    if (totalCards === 0) return { totalCards: 0, avgCmc: 0, colorDistribution: {} };

    const avgCmc = deck.reduce((sum, c) => sum + c.cmc, 0) / totalCards;
    const colorDistribution: Record<string, number> = {};
    for (const card of deck) {
      for (const color of card.colors) {
        colorDistribution[color] = (colorDistribution[color] || 0) + 1;
      }
    }
    return { totalCards, avgCmc, colorDistribution };
  },
}));
