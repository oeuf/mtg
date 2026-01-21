'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { graphApi, GraphNode } from '@/lib/api';
import { GraphVisualization } from '@/components/GraphVisualization';

export default function ExplorePage() {
  const [cardName, setCardName] = useState('');
  const [searchInput, setSearchInput] = useState('');
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  const { data: graphData, isLoading } = useQuery({
    queryKey: ['graph', cardName],
    queryFn: () => graphApi.getCardGraph(cardName, { depth: 2 }).then(r => r.data),
    enabled: !!cardName,
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCardName(searchInput);
  };

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Graph Explorer</h1>

      <form onSubmit={handleSearch} className="flex gap-2">
        <input
          type="text"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          placeholder="Enter card name to explore..."
          className="flex-1 p-2 border rounded"
        />
        <button
          type="submit"
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Explore
        </button>
      </form>

      <div className="grid grid-cols-4 gap-4">
        <div className="col-span-3">
          {isLoading && <p>Loading graph...</p>}
          {graphData && (
            <GraphVisualization
              data={graphData}
              onNodeClick={setSelectedNode}
            />
          )}
        </div>

        <div className="p-4 border rounded">
          <h3 className="font-bold mb-2">Node Details</h3>
          {selectedNode ? (
            <div className="space-y-2 text-sm">
              <p><strong>Name:</strong> {selectedNode.label}</p>
              <p><strong>Type:</strong> {selectedNode.type}</p>
              {selectedNode.type === 'Card' && (
                <button
                  onClick={() => setCardName(selectedNode.label)}
                  className="text-blue-500 underline"
                >
                  Explore this card
                </button>
              )}
            </div>
          ) : (
            <p className="text-gray-500 text-sm">Click a node to see details</p>
          )}

          <div className="mt-4">
            <h4 className="font-medium text-sm">Legend</h4>
            <div className="space-y-1 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded-full bg-blue-500" />
                <span>Card</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded-full bg-green-500" />
                <span>Mechanic</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded-full bg-orange-500" />
                <span>Role</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
