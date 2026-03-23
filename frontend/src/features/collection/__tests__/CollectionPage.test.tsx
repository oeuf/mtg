import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, beforeEach } from 'vitest';
import CollectionPage from '../CollectionPage';
import { useCollection } from '../useCollection';
import type { Card } from '../../../types';

function makeCard(overrides: Partial<Card> = {}): Card {
  return {
    name: 'Sol Ring',
    mana_cost: '{1}',
    cmc: 1,
    type_line: 'Artifact',
    oracle_text: '{T}: Add {C}{C}.',
    color_identity: [],
    colors: [],
    keywords: [],
    is_legendary: false,
    edhrec_rank: 1,
    functional_categories: ['ramp'],
    mechanics: ['mana_ability'],
    themes: [],
    archetype: null,
    popularity_score: 99,
    ...overrides,
  };
}

describe('CollectionPage', () => {
  beforeEach(() => {
    useCollection.setState({ cards: {} });
  });

  it('renders page title', () => {
    render(<CollectionPage />);
    expect(screen.getByRole('heading', { name: /my collection/i })).toBeInTheDocument();
  });

  it('shows empty state when no cards', () => {
    render(<CollectionPage />);
    expect(screen.getByText(/no cards in your collection/i)).toBeInTheDocument();
  });

  it('shows collection stats when cards exist', () => {
    useCollection.setState({
      cards: {
        'Sol Ring': { card: makeCard(), quantity: 4 },
        'Arcane Signet': { card: makeCard({ name: 'Arcane Signet' }), quantity: 2 },
      },
    });
    render(<CollectionPage />);
    expect(screen.getByText(/6 cards/i)).toBeInTheDocument();
    expect(screen.getByText(/2 unique/i)).toBeInTheDocument();
  });

  it('renders cards in collection', () => {
    useCollection.setState({
      cards: {
        'Sol Ring': { card: makeCard(), quantity: 4 },
      },
    });
    render(<CollectionPage />);
    expect(screen.getByText('Sol Ring')).toBeInTheDocument();
    expect(screen.getByText('4x')).toBeInTheDocument();
  });

  it('can remove a card from collection', () => {
    useCollection.setState({
      cards: {
        'Sol Ring': { card: makeCard(), quantity: 1 },
      },
    });
    render(<CollectionPage />);
    fireEvent.click(screen.getByRole('button', { name: /remove/i }));
    expect(useCollection.getState().cards['Sol Ring']).toBeUndefined();
  });

  it('filters cards by search text', () => {
    useCollection.setState({
      cards: {
        'Sol Ring': { card: makeCard(), quantity: 1 },
        'Arcane Signet': { card: makeCard({ name: 'Arcane Signet' }), quantity: 1 },
      },
    });
    render(<CollectionPage />);
    const input = screen.getByPlaceholderText(/search collection/i);
    fireEvent.change(input, { target: { value: 'Sol' } });
    expect(screen.getByText('Sol Ring')).toBeInTheDocument();
    expect(screen.queryByText('Arcane Signet')).not.toBeInTheDocument();
  });
});
