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

import { cardsAPI } from '../../../services/api';

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
    // Restore default mocks after each test
    (cardsAPI.get as ReturnType<typeof vi.fn>).mockResolvedValue({
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
    });
    (cardsAPI.getSimilar as ReturnType<typeof vi.fn>).mockResolvedValue({
      data: { card: 'Eternal Witness', similar_cards: [{ name: 'Regrowth', score: 0.92 }] },
    });
    (cardsAPI.getSynergies as ReturnType<typeof vi.fn>).mockResolvedValue({
      data: { card: 'Eternal Witness', synergies: [{ name: 'Muldrotha, the Gravetide', score: 0.85 }] },
    });
    (cardsAPI.getCombos as ReturnType<typeof vi.fn>).mockResolvedValue({
      data: { card: 'Eternal Witness', combos: [] },
    });
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

  // --- API response wrapper handling ---

  it('renders similar cards from similar_cards array', async () => {
    renderPage();
    // "Regrowth" comes from similar_cards[0].name in getSimilar response
    expect(await screen.findByText('Regrowth')).toBeInTheDocument();
  });

  it('renders synergies from synergies array', async () => {
    renderPage();
    // "Muldrotha, the Gravetide" comes from synergies[0].name in getSynergies response
    expect(await screen.findByText('Muldrotha, the Gravetide')).toBeInTheDocument();
  });

  it('renders combos from combos array', async () => {
    (cardsAPI.getCombos as ReturnType<typeof vi.fn>).mockResolvedValue({
      data: {
        card: 'Eternal Witness',
        combos: [{ name: 'Karmic Guide', combo_name: 'Karmic Witness Loop', description: 'Infinite recursion loop.' }],
      },
    });
    renderPage();
    expect(await screen.findByText('Karmic Guide')).toBeInTheDocument();
    expect(await screen.findByText('Karmic Witness Loop')).toBeInTheDocument();
    expect(await screen.findByText('Infinite recursion loop.')).toBeInTheDocument();
  });

  it('does not crash when color_identity is null', async () => {
    (cardsAPI.get as ReturnType<typeof vi.fn>).mockResolvedValue({
      data: {
        name: 'Eternal Witness',
        mana_cost: '{1}{G}{G}',
        cmc: 3,
        type_line: 'Creature — Human Shaman',
        oracle_text: 'When Eternal Witness enters the battlefield.',
        color_identity: null,
        colors: [],
        keywords: [],
        is_legendary: false,
        edhrec_rank: null,
        functional_categories: [],
        mechanics: [],
        themes: [],
        archetype: null,
        popularity_score: 0,
      },
    });
    renderPage();
    // Page should still render the card name without crashing on null color_identity
    expect(await screen.findByRole('heading', { name: /eternal witness/i })).toBeInTheDocument();
  });

  it('shows Similar Cards section with no cards when similar_cards is empty', async () => {
    (cardsAPI.getSimilar as ReturnType<typeof vi.fn>).mockResolvedValue({
      data: { card: 'Eternal Witness', similar_cards: [] },
    });
    renderPage();
    // The "Similar Cards" section heading should still exist
    expect(await screen.findByRole('heading', { name: /similar cards/i })).toBeInTheDocument();
    // The empty-state message from SimilarCards component is shown
    expect(await screen.findByText(/no similar cards found/i)).toBeInTheDocument();
  });
});
