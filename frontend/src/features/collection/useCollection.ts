import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Card } from '../../types';

interface CollectionEntry {
  card: Card;
  quantity: number;
}

interface CollectionState {
  cards: Record<string, CollectionEntry>;
  addCard: (card: Card, quantity?: number) => void;
  removeCard: (cardName: string) => void;
  updateQuantity: (cardName: string, quantity: number) => void;
  hasCard: (cardName: string) => boolean;
  totalCards: () => number;
  totalUnique: () => number;
}

export const useCollection = create<CollectionState>()(
  persist(
    (set, get) => ({
      cards: {},
      addCard: (card, quantity = 1) =>
        set((state) => {
          const existing = state.cards[card.name];
          return {
            cards: {
              ...state.cards,
              [card.name]: {
                card,
                quantity: existing ? existing.quantity + quantity : quantity,
              },
            },
          };
        }),
      removeCard: (cardName) =>
        set((state) => {
          const { [cardName]: _, ...rest } = state.cards;
          return { cards: rest };
        }),
      updateQuantity: (cardName, quantity) =>
        set((state) => {
          const existing = state.cards[cardName];
          if (!existing) return state;
          return {
            cards: {
              ...state.cards,
              [cardName]: { ...existing, quantity },
            },
          };
        }),
      hasCard: (cardName) => cardName in get().cards,
      totalCards: () =>
        Object.values(get().cards).reduce((sum, entry) => sum + entry.quantity, 0),
      totalUnique: () => Object.keys(get().cards).length,
    }),
    { name: 'mtg-collection' },
  ),
);
