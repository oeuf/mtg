'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { cardsApi, Card } from '@/lib/api';

interface Props {
  colorIdentity: string[];
  onAddCard: (card: Card) => void;
}

export function CardSearch({ colorIdentity, onAddCard }: Props) {
  const [search, setSearch] = useState('');
  const [maxCmc, setMaxCmc] = useState<number | undefined>();
  const [role, setRole] = useState<string>('');

  const { data: cards, isLoading } = useQuery({
    queryKey: ['cards', search, maxCmc, role, colorIdentity],
    queryFn: () =>
      cardsApi.search({
        q: search,
        max_cmc: maxCmc,
        colors: colorIdentity.join(','),
        role: role || undefined,
        limit: 30,
      }).then(r => r.data),
    enabled: search.length >= 2,
  });

  return (
    <div className="space-y-2">
      <div className="flex gap-2">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search cards..."
          className="flex-1 p-2 border rounded"
        />
        <select
          value={maxCmc ?? ''}
          onChange={(e) => setMaxCmc(e.target.value ? parseInt(e.target.value) : undefined)}
          className="p-2 border rounded"
        >
          <option value="">Any CMC</option>
          {[1, 2, 3, 4, 5, 6, 7].map(n => (
            <option key={n} value={n}>≤{n} CMC</option>
          ))}
        </select>
        <select
          value={role}
          onChange={(e) => setRole(e.target.value)}
          className="p-2 border rounded"
        >
          <option value="">Any Role</option>
          <option value="ramp">Ramp</option>
          <option value="card_draw">Card Draw</option>
          <option value="removal">Removal</option>
          <option value="recursion">Recursion</option>
          <option value="protection">Protection</option>
        </select>
      </div>

      {isLoading && <p className="text-sm text-gray-500">Searching...</p>}

      {cards && (
        <ul className="border rounded max-h-80 overflow-y-auto">
          {cards.map((card) => (
            <li
              key={card.name}
              className="p-2 hover:bg-gray-100 flex items-center"
            >
              <div className="flex-1">
                <span className="font-medium">{card.name}</span>
                <span className="ml-2 text-sm text-gray-600">{card.mana_cost}</span>
                <div className="text-xs text-gray-500">
                  {card.functional_categories.join(', ')}
                </div>
              </div>
              <button
                onClick={() => onAddCard(card)}
                className="px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                Add
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
