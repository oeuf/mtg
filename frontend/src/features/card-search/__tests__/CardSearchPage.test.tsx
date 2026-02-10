import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import CardSearchPage from '../CardSearchPage';
import { useCardSearch } from '../useCardSearch';
import type { Card, CardSearchFilters } from '../../../types';

// Mock react-router-dom
vi.mock('react-router-dom', () => ({
  useNavigate: () => vi.fn(),
}));

// Mock useCardSearch
vi.mock('../useCardSearch', () => ({
  useCardSearch: vi.fn(),
}));

// Mock FilterPanel
vi.mock('../../../components/filters', () => ({
  FilterPanel: ({ onClear }: { onClear: () => void }) => (
    <div data-testid="filter-panel">
      <button type="button" onClick={onClear}>Clear</button>
    </div>
  ),
}));

// Mock CardGrid
vi.mock('../../../components/cards', () => ({
  CardGrid: () => <div data-testid="card-grid" />,
}));

const mockUpdateFilter = vi.fn();
const mockClearFilters = vi.fn();
const mockSetPage = vi.fn();

const defaultHookReturn = {
  results: undefined as { items: Card[]; total: number } | undefined,
  isLoading: false,
  error: null as Error | null,
  filters: { page: 1, limit: 20 } as CardSearchFilters,
  updateFilter: mockUpdateFilter as (key: keyof CardSearchFilters, value: unknown) => void,
  clearFilters: mockClearFilters,
  page: 1,
  setPage: mockSetPage as (page: number) => void,
  totalPages: 0,
};

describe('CardSearchPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useCardSearch).mockReturnValue({ ...defaultHookReturn });
  });

  it('renders page title', () => {
    render(<CardSearchPage />);
    expect(screen.getByRole('heading', { name: /card search/i })).toBeInTheDocument();
  });

  it('renders search input', () => {
    render(<CardSearchPage />);
    expect(screen.getByPlaceholderText(/search cards/i)).toBeInTheDocument();
  });

  it('renders FilterPanel', () => {
    render(<CardSearchPage />);
    expect(screen.getByTestId('filter-panel')).toBeInTheDocument();
  });

  it('renders CardGrid', () => {
    render(<CardSearchPage />);
    expect(screen.getByTestId('card-grid')).toBeInTheDocument();
  });

  it('search input calls updateFilter', () => {
    render(<CardSearchPage />);
    const input = screen.getByPlaceholderText(/search cards/i);
    fireEvent.change(input, { target: { value: 'Sol Ring' } });
    expect(mockUpdateFilter).toHaveBeenCalledWith('text_search', 'Sol Ring');
  });

  it('shows loading state', () => {
    vi.mocked(useCardSearch).mockReturnValue({
      ...defaultHookReturn,
      isLoading: true,
    });
    render(<CardSearchPage />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });
});
