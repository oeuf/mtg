import { useState, useMemo, useCallback } from 'react';
import { useCollection } from './useCollection';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { SearchAutocomplete } from '../../components/SearchAutocomplete';
import type { AutocompleteItem } from '../../components/SearchAutocomplete';

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

  const fetchCollectionSuggestions = useCallback(
    async (query: string): Promise<AutocompleteItem[]> => {
      const lower = query.toLowerCase();
      return Object.values(cards)
        .filter(
          (entry) =>
            entry.card.name.toLowerCase().includes(lower) ||
            entry.card.type_line.toLowerCase().includes(lower),
        )
        .slice(0, 8)
        .map((entry) => ({
          name: entry.card.name,
          type_line: entry.card.type_line,
          mana_cost: entry.card.mana_cost,
        }));
    },
    [cards],
  );

  const handleSelect = useCallback((item: AutocompleteItem) => {
    setSearch(item.name);
  }, []);

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
          <SearchAutocomplete
            placeholder="Search collection..."
            fetchSuggestions={fetchCollectionSuggestions}
            onSelect={handleSelect}
            onChange={setSearch}
            value={search}
            className="mb-6"
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
