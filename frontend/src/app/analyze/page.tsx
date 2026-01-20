'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { decksApi, DeckAnalysis } from '@/lib/api';

export default function AnalyzePage() {
  const [commander, setCommander] = useState('');
  const [decklist, setDecklist] = useState('');
  const [analysis, setAnalysis] = useState<DeckAnalysis | null>(null);

  const analyzeMutation = useMutation({
    mutationFn: (data: { commander: string; cards: string[] }) =>
      decksApi.analyze(data).then(r => r.data),
    onSuccess: (data) => setAnalysis(data),
  });

  const handleAnalyze = () => {
    const cards = decklist
      .split('\n')
      .map(line => {
        const match = line.match(/^\d+\s+(.+)$/);
        return match ? match[1].trim() : null;
      })
      .filter(Boolean) as string[];

    if (commander && cards.length > 0) {
      analyzeMutation.mutate({ commander, cards });
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Deck Analyzer</h1>

      <div className="grid grid-cols-2 gap-6">
        {/* Input */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Commander</label>
            <input
              type="text"
              value={commander}
              onChange={(e) => setCommander(e.target.value)}
              placeholder="Muldrotha, the Gravetide"
              className="w-full p-2 border rounded"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Decklist (Moxfield format: &quot;1 Card Name&quot;)
            </label>
            <textarea
              value={decklist}
              onChange={(e) => setDecklist(e.target.value)}
              placeholder={"1 Sol Ring\n1 Eternal Witness\n1 Spore Frog"}
              className="w-full h-80 p-2 border rounded font-mono text-sm"
            />
          </div>

          <button
            onClick={handleAnalyze}
            disabled={analyzeMutation.isPending}
            className="w-full py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
          >
            {analyzeMutation.isPending ? 'Analyzing...' : 'Analyze Deck'}
          </button>
        </div>

        {/* Results */}
        <div>
          {analysis && (
            <div className="space-y-4">
              <div className="p-4 bg-gray-100 rounded">
                <h3 className="font-bold">Overview</h3>
                <p>Commander: {analysis.commander}</p>
                <p>Cards: {analysis.card_count}</p>
              </div>

              <div className="p-4 bg-gray-100 rounded">
                <h3 className="font-bold mb-2">Role Coverage</h3>
                <div className="space-y-1">
                  {Object.entries(analysis.role_coverage).map(([role, count]) => (
                    <div key={role} className="flex items-center">
                      <span className="w-32 capitalize">{role.replace('_', ' ')}</span>
                      <div className="flex-1 bg-gray-300 rounded h-4">
                        <div
                          className="bg-blue-500 h-4 rounded"
                          style={{ width: `${Math.min(count * 10, 100)}%` }}
                        />
                      </div>
                      <span className="w-8 text-right text-sm">{count}</span>
                    </div>
                  ))}
                </div>
              </div>

              {analysis.missing_roles.length > 0 && (
                <div className="p-4 bg-yellow-100 rounded">
                  <h3 className="font-bold text-yellow-800">Missing Roles</h3>
                  <ul className="list-disc list-inside">
                    {analysis.missing_roles.map(role => (
                      <li key={role} className="capitalize">{role.replace('_', ' ')}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="p-4 bg-green-100 rounded">
                <h3 className="font-bold text-green-800 mb-2">Suggested Additions</h3>
                <ul className="space-y-1">
                  {analysis.suggested_additions.slice(0, 10).map(card => (
                    <li key={card.name} className="text-sm">
                      {card.name} ({card.mana_cost}) - {card.roles.join(', ')}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
