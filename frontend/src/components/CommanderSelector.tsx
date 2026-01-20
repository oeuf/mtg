'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { commandersApi, Commander } from '@/lib/api';

interface Props {
  onSelect: (commander: Commander | null) => void;
  selected?: Commander;
}

export function CommanderSelector({ onSelect, selected }: Props) {
  const [search, setSearch] = useState('');

  const { data: commanders, isLoading } = useQuery({
    queryKey: ['commanders', search],
    queryFn: () => commandersApi.list({ search, limit: 20 }).then(r => r.data),
    enabled: search.length >= 2,
  });

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium">Commander</label>
      {selected ? (
        <div className="flex items-center gap-2 p-2 bg-blue-100 rounded">
          <span className="font-medium">{selected.name}</span>
          <span className="text-sm text-gray-600">{selected.mana_cost}</span>
          <button
            onClick={() => onSelect(null)}
            className="ml-auto text-red-500 hover:text-red-700"
          >
            x
          </button>
        </div>
      ) : (
        <>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search for a commander..."
            className="w-full p-2 border rounded"
          />
          {isLoading && <p className="text-sm text-gray-500">Loading...</p>}
          {commanders && commanders.length > 0 && (
            <ul className="border rounded max-h-60 overflow-y-auto">
              {commanders.map((c) => (
                <li
                  key={c.name}
                  onClick={() => {
                    onSelect(c);
                    setSearch('');
                  }}
                  className="p-2 hover:bg-gray-100 cursor-pointer"
                >
                  <span className="font-medium">{c.name}</span>
                  <span className="ml-2 text-sm text-gray-600">{c.mana_cost}</span>
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </div>
  );
}
