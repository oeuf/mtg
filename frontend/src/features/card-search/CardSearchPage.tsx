import { useCardSearch } from './useCardSearch';
import { FilterPanel } from '../../components/filters';
import { CardGrid } from '../../components/cards';
import { LoadingSpinner } from '../../components/LoadingSpinner';
import type { CardSearchFilters } from '../../types';

export default function CardSearchPage() {
  const {
    results,
    isLoading,
    filters,
    updateFilter,
    clearFilters,
    page,
    setPage,
  } = useCardSearch();

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-3xl font-bold mb-4">Card Search</h1>

      <input
        type="text"
        placeholder="Search cards by name or text..."
        value={(filters.text_search as string) ?? ''}
        onChange={(e) => updateFilter('text_search' as keyof CardSearchFilters, e.target.value)}
        className="w-full mb-6 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-500"
      />

      {isLoading && !results ? (
        <LoadingSpinner size="lg" />
      ) : (
        <div className="flex gap-8">
          <aside>
            <FilterPanel
              filters={filters as unknown as Record<string, unknown>}
              onUpdateFilter={updateFilter as unknown as (key: string, value: unknown) => void}
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
            />
          </main>
        </div>
      )}
    </div>
  );
}
