import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import CardDetailPage from '../CardDetailPage';

vi.mock('../../../services/api', () => ({
  cardsAPI: {
    get: vi.fn().mockResolvedValue({
      data: {
        name: 'Eternal Witness',
        mana_cost: '{1}{G}{G}',
        cmc: 3,
        type_line: 'Creature — Human Shaman',
        oracle_text: 'When Eternal Witness enters the battlefield, you may return target card from your graveyard to your hand.',
        color_identity: ['G'],
        colors: ['G'],
        keywords: [],
        is_legendary: false,
        edhrec_rank: 10,
        functional_categories: ['recursion'],
        mechanics: ['etb_trigger'],
        themes: ['graveyard'],
        archetype: null,
        popularity_score: 95,
      },
    }),
    getSimilar: vi.fn().mockResolvedValue({
      data: { card: 'Eternal Witness', similar_cards: [{ name: 'Regrowth', score: 0.92 }] },
    }),
    getSynergies: vi.fn().mockResolvedValue({
      data: { card: 'Eternal Witness', synergies: [{ name: 'Muldrotha, the Gravetide', score: 0.85 }] },
    }),
    getCombos: vi.fn().mockResolvedValue({
      data: { card: 'Eternal Witness', combos: [] },
    }),
  },
}));

function renderPage(cardName = 'Eternal Witness') {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[`/cards/${cardName}`]}>
        <Routes>
          <Route path="/cards/:name" element={<CardDetailPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('CardDetailPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders card name as heading', async () => {
    renderPage();
    expect(await screen.findByRole('heading', { name: /eternal witness/i })).toBeInTheDocument();
  });

  it('renders card type line', async () => {
    renderPage();
    expect(await screen.findByText(/creature — human shaman/i)).toBeInTheDocument();
  });

  it('renders oracle text', async () => {
    renderPage();
    expect(await screen.findByText(/when eternal witness enters/i)).toBeInTheDocument();
  });

  it('renders mana cost', async () => {
    renderPage();
    expect(await screen.findByText('{1}{G}{G}')).toBeInTheDocument();
  });

  it('renders back to search link', async () => {
    renderPage();
    expect(await screen.findByRole('link', { name: /back to search/i })).toBeInTheDocument();
  });

  it('renders similar cards section', async () => {
    renderPage();
    expect(await screen.findByText(/similar cards/i)).toBeInTheDocument();
  });

  it('renders synergies section', async () => {
    renderPage();
    expect(await screen.findByText(/synergies/i)).toBeInTheDocument();
  });

  it('renders combos section', async () => {
    renderPage();
    expect(await screen.findByRole('heading', { name: /combos/i })).toBeInTheDocument();
  });
});
