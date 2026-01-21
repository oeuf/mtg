'use client';

import { useParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { commandersApi, Recommendation } from '@/lib/api';
import Link from 'next/link';

export default function CommanderPage() {
  const params = useParams();
  const name = decodeURIComponent(params.name as string);

  const { data: commander, isLoading } = useQuery({
    queryKey: ['commander', name],
    queryFn: () => commandersApi.get(name).then(r => r.data),
  });

  const { data: recommendations } = useQuery({
    queryKey: ['recommendations', name],
    queryFn: () => commandersApi.getRecommendations(name, { limit: 50 }).then(r => r.data),
    enabled: !!commander,
  });

  if (isLoading) return <p>Loading...</p>;
  if (!commander) return <p>Commander not found</p>;

  // Group recommendations by role
  const byRole: Record<string, Recommendation[]> = {};
  recommendations?.forEach(rec => {
    const role = rec.roles[0] || 'other';
    if (!byRole[role]) byRole[role] = [];
    byRole[role].push(rec);
  });

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Commander Header */}
      <div className="p-6 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg">
        <h1 className="text-3xl font-bold">{commander.name}</h1>
        <p className="text-xl">{commander.mana_cost} - {commander.type_line}</p>
        <p className="mt-2 opacity-90">{commander.oracle_text}</p>
        <div className="mt-4 flex gap-2">
          {commander.color_identity.map(c => (
            <span key={c} className="px-2 py-1 bg-white/20 rounded">{c}</span>
          ))}
        </div>
      </div>

      {/* Synergies */}
      <div className="p-4 bg-gray-100 rounded">
        <h2 className="font-bold text-lg mb-2">Key Synergies</h2>
        <div className="flex flex-wrap gap-2">
          {commander.synergies?.map(s => (
            <span key={s} className="px-3 py-1 bg-green-200 rounded-full text-sm">
              {s}
            </span>
          ))}
        </div>
      </div>

      {/* Start Building */}
      <Link
        href={`/build?commander=${encodeURIComponent(commander.name)}`}
        className="block w-full py-3 bg-blue-500 text-white text-center rounded-lg hover:bg-blue-600"
      >
        Start Building with {commander.name}
      </Link>

      {/* Recommendations by Role */}
      <div>
        <h2 className="font-bold text-lg mb-4">Recommended Cards by Role</h2>
        <div className="grid grid-cols-2 gap-4">
          {Object.entries(byRole).map(([role, cards]) => (
            <div key={role} className="p-4 border rounded">
              <h3 className="font-medium capitalize mb-2">
                {role.replace('_', ' ')} ({cards?.length})
              </h3>
              <ul className="space-y-1 text-sm">
                {cards?.slice(0, 8).map(card => (
                  <li key={card.name} className="flex justify-between">
                    <span>{card.name}</span>
                    <span className="text-gray-500">{card.mana_cost}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
