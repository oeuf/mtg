import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCardSearch } from './useCardSearch';
import { FilterPanel } from '../../components/filters';
import { CardGrid } from '../../components/cards';
import { LoadingSpinner } from '../../components/LoadingSpinner';
import { SearchAutocomplete } from '../../components/SearchAutocomplete';
import type { AutocompleteItem } from '../../components/SearchAutocomplete';
import { cardsAPI } from '../../services/api';

export default function CardSearchPage() {
  const navigate = useNavigate();
  const {
    results,
    isLoading,
    filters,
    updateFilter,
    clearFilters,
    page,
    setPage,
  } = useCardSearch();

  const fetchCardSuggestions = useCallback(
    async (query: string): Promise<AutocompleteItem[]> => {
      const response = await cardsAPI.autocomplete(query);
      return response.data;
    },
    [],
  );

  const handleSelect = useCallback(
    (item: AutocompleteItem) => {
      navigate(`/cards/${encodeURIComponent(item.name)}`);
    },
    [navigate],
  );

  const handleSearchChange = useCallback(
    (value: string) => {
      updateFilter('text_search', value);
    },
    [updateFilter],
  );

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-3xl font-bold mb-4">Card Search</h1>

      <SearchAutocomplete
        placeholder="Search cards by name or text..."
        fetchSuggestions={fetchCardSuggestions}
        onSelect={handleSelect}
        onChange={handleSearchChange}
        value={filters.text_search ?? ''}
        className="mb-6"
      />

      {isLoading && !results ? (
        <LoadingSpinner size="lg" />
      ) : (
        <div className="flex gap-8">
          <aside>
            <FilterPanel
              filters={filters}
              onUpdateFilter={updateFilter}
              onClear={clearFilters}
            />
          </aside>
          <main className="flex-1">
            <CardGrid
              cards={results?.items ?? []}
              total={results?.total ?? 0}
              page={page}
              onPageChange={setPage}
              isLoading={isLoading}
              onCardClick={(name) => navigate(`/cards/${encodeURIComponent(name)}`)}
            />
          </main>
        </div>
      )}
    </div>
  );
}
