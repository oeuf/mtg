'use client';

import { Card } from '@/lib/api';

interface Props {
  cards: Card[];
  onRemoveCard: (name: string) => void;
}

export function DeckList({ cards, onRemoveCard }: Props) {
  // Group by role
  const byRole: Record<string, Card[]> = {};
  cards.forEach(card => {
    const role = card.functional_categories[0] || 'Other';
    if (!byRole[role]) byRole[role] = [];
    byRole[role].push(card);
  });

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="font-bold">Deck ({cards.length}/99)</h3>
        <div className="text-sm text-gray-600">
          Avg CMC: {(cards.reduce((sum, c) => sum + (c.cmc || 0), 0) / cards.length || 0).toFixed(2)}
        </div>
      </div>

      {Object.entries(byRole).sort().map(([role, roleCards]) => (
        <div key={role}>
          <h4 className="font-medium text-sm text-gray-700 capitalize">
            {role.replace('_', ' ')} ({roleCards.length})
          </h4>
          <ul className="space-y-1">
            {roleCards.sort((a, b) => (a.cmc || 0) - (b.cmc || 0)).map(card => (
              <li
                key={card.name}
                className="flex items-center text-sm p-1 hover:bg-gray-100 rounded"
              >
                <span className="flex-1">{card.name}</span>
                <span className="text-gray-500 mr-2">{card.mana_cost}</span>
                <button
                  onClick={() => onRemoveCard(card.name)}
                  className="text-red-500 hover:text-red-700"
                >
                  x
                </button>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
