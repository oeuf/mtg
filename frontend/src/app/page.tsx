'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { commandersApi } from '@/lib/api';
import Link from 'next/link';

export default function Home() {
  const [search, setSearch] = useState('');

  const { data: commanders } = useQuery({
    queryKey: ['commanders', search],
    queryFn: () => commandersApi.list({ search, limit: 20 }).then(r => r.data),
    enabled: search.length >= 2,
  });

  return (
    <div className="max-w-2xl mx-auto space-y-8 py-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">MTG Commander Deck Builder</h1>
        <p className="text-gray-600">
          Build optimized Commander decks with AI-powered recommendations
        </p>
      </div>

      <div>
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search for a commander to get started..."
          className="w-full p-4 text-lg border-2 rounded-lg focus:border-blue-500 outline-none"
        />

        {commanders && commanders.length > 0 && (
          <ul className="mt-2 border rounded-lg divide-y">
            {commanders.map(c => (
              <li key={c.name}>
                <Link
                  href={`/commander/${encodeURIComponent(c.name)}`}
                  className="block p-4 hover:bg-gray-50"
                >
                  <span className="font-medium">{c.name}</span>
                  <span className="ml-2 text-gray-600">{c.mana_cost}</span>
                  <span className="block text-sm text-gray-500">{c.type_line}</span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="grid grid-cols-3 gap-4 text-center">
        <Link href="/build" className="p-6 border rounded-lg hover:bg-gray-50">
          <h2 className="font-bold text-lg">Deck Builder</h2>
          <p className="text-sm text-gray-600">Build a new deck</p>
        </Link>
        <Link href="/analyze" className="p-6 border rounded-lg hover:bg-gray-50">
          <h2 className="font-bold text-lg">Deck Analyzer</h2>
          <p className="text-sm text-gray-600">Analyze existing deck</p>
        </Link>
        <Link href="/explore" className="p-6 border rounded-lg hover:bg-gray-50">
          <h2 className="font-bold text-lg">Graph Explorer</h2>
          <p className="text-sm text-gray-600">Explore card synergies</p>
        </Link>
      </div>
    </div>
  );
}
