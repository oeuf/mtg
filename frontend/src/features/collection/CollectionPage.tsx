import { useState, useMemo } from 'react';
import { useCollection } from './useCollection';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';

export default function CollectionPage() {
  const { cards, removeCard } = useCollection();
  const totalCards = useCollection((s) => s.totalCards());
  const totalUnique = useCollection((s) => s.totalUnique());
  const [search, setSearch] = useState('');

  const filteredCards = useMemo(() => {
    const entries = Object.values(cards);
    if (!search.trim()) return entries;
    const lower = search.toLowerCase();
    return entries.filter(
      (entry) =>
        entry.card.name.toLowerCase().includes(lower) ||
        entry.card.type_line.toLowerCase().includes(lower),
    );
  }, [cards, search]);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-3xl font-bold mb-2">My Collection</h1>

      {totalUnique > 0 && (
        <p className="text-gray-400 mb-6">
          {totalCards} cards | {totalUnique} unique
        </p>
      )}

      {totalUnique === 0 ? (
        <p className="text-gray-500 mt-8">No cards in your collection yet. Search for cards and add them.</p>
      ) : (
        <>
          <input
            type="text"
            placeholder="Search collection..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full mb-6 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-500"
          />

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filteredCards.map(({ card, quantity }) => (
              <div key={card.name} className="bg-gray-800 rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-bold">{card.name}</h3>
                  <Badge variant="default">{quantity}x</Badge>
                </div>
                <p className="text-gray-400 text-sm mb-2">{card.type_line}</p>
                <p className="text-gray-500 text-xs mb-3">{card.mana_cost}</p>
                <Button
                  variant="secondary"
                  onClick={() => removeCard(card.name)}
                  className="w-full text-sm"
                >
                  Remove
                </Button>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
