import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi } from 'vitest';

vi.mock('../../components/ToastContext', () => ({
  useToast: () => ({ addToast: vi.fn(), removeToast: vi.fn() }),
}));
import HomePage from '../home/HomePage';
import CommanderSelectPage from '../commanders/CommanderSelectPage';
import DeckBuilderPage from '../deck-builder/DeckBuilderPage';
import CardSearchPage from '../card-search/CardSearchPage';
import CardDetailPage from '../cards/CardDetailPage';
import CollectionPage from '../collection/CollectionPage';

function renderWithRouter(initialEntries: string[]) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={initialEntries}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/commanders" element={<CommanderSelectPage />} />
          <Route path="/deck-builder/:commander" element={<DeckBuilderPage />} />
          <Route path="/cards" element={<CardSearchPage />} />
          <Route path="/cards/:name" element={<CardDetailPage />} />
          <Route path="/collection" element={<CollectionPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('Route rendering', () => {
  it('renders HomePage at /', () => {
    renderWithRouter(['/']);
    expect(screen.getByRole('heading', { name: /mtg commander/i })).toBeInTheDocument();
  });

  it('renders CommanderSelectPage at /commanders', () => {
    renderWithRouter(['/commanders']);
    expect(screen.getByRole('heading', { name: /select a commander/i })).toBeInTheDocument();
  });

  it('renders DeckBuilderPage at /deck-builder/:commander', () => {
    renderWithRouter(['/deck-builder/Muldrotha']);
    expect(screen.getByRole('heading', { name: /deck builder/i })).toBeInTheDocument();
  });

  it('renders CardSearchPage at /cards', () => {
    renderWithRouter(['/cards']);
    expect(screen.getByRole('heading', { name: /card search/i })).toBeInTheDocument();
  });

  it('renders CollectionPage at /collection', () => {
    renderWithRouter(['/collection']);
    expect(screen.getByRole('heading', { name: /my collection/i })).toBeInTheDocument();
  });
});
