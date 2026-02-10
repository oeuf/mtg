import { useState, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { cardsAPI } from '../../services/api';
import type { CardSearchFilters } from '../../types';

const DEFAULT_FILTERS: CardSearchFilters = { page: 1, limit: 20 };

export function useCardSearch() {
  const [filters, setFilters] = useState<CardSearchFilters>({ ...DEFAULT_FILTERS });

  const { data, isLoading, error } = useQuery({
    queryKey: ['cards', filters],
    queryFn: () => cardsAPI.search(filters).then((r) => r.data),
  });

  const updateFilter = useCallback(
    (key: keyof CardSearchFilters, value: unknown) => {
      setFilters((prev) => ({ ...prev, [key]: value, page: 1 }));
    },
    [],
  );

  const clearFilters = useCallback(() => {
    setFilters({ ...DEFAULT_FILTERS });
  }, []);

  const setPage = useCallback((page: number) => {
    setFilters((prev) => ({ ...prev, page }));
  }, []);

  const totalPages = data ? Math.ceil(data.total / filters.limit) : 0;

  return {
    results: data,
    isLoading,
    error: error as Error | null,
    filters,
    updateFilter,
    clearFilters,
    page: filters.page,
    setPage,
    totalPages,
  };
}
