import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import type { Card } from '../../../types/card';
import { CardCard } from '../CardCard';
import { CardGrid } from '../CardGrid';

function makeCard(overrides: Partial<Card> = {}): Card {
  return {
    name: 'Eternal Witness',
    mana_cost: '{1}{G}{G}',
    cmc: 3,
    type_line: 'Creature — Human Shaman',
    oracle_text: 'When Eternal Witness enters the battlefield, you may return target card from your graveyard to your hand.',
    color_identity: ['G'],
    colors: ['G'],
    keywords: [],
    is_legendary: false,
    edhrec_rank: 50,
    functional_categories: [],
    mechanics: [],
    themes: [],
    archetype: null,
    popularity_score: 0.9,
    ...overrides,
  };
}

describe('CardCard', () => {
  it('renders card name, mana cost, and type line', () => {
    render(<CardCard card={makeCard()} />);

    expect(screen.getByText('Eternal Witness')).toBeInTheDocument();
    expect(screen.getByText('{1}{G}{G}')).toBeInTheDocument();
    expect(screen.getByText('Creature — Human Shaman')).toBeInTheDocument();
  });

  it('truncates long oracle text at 100 chars', () => {
    const longText = 'A'.repeat(120);
    render(<CardCard card={makeCard({ oracle_text: longText })} />);

    expect(screen.getByText('A'.repeat(100) + '...')).toBeInTheDocument();
  });

  it('does not truncate short oracle text', () => {
    const shortText = 'Draw a card.';
    render(<CardCard card={makeCard({ oracle_text: shortText })} />);

    expect(screen.getByText('Draw a card.')).toBeInTheDocument();
  });

  it('renders color identity badges', () => {
    render(
      <CardCard card={makeCard({ color_identity: ['W', 'U', 'B'] })} />,
    );

    expect(screen.getByText('W')).toBeInTheDocument();
    expect(screen.getByText('U')).toBeInTheDocument();
    expect(screen.getByText('B')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const onClick = vi.fn();
    render(<CardCard card={makeCard()} onClick={onClick} />);

    fireEvent.click(screen.getByRole('button'));
    expect(onClick).toHaveBeenCalledWith('Eternal Witness');
  });

  it('supports keyboard activation with Enter and Space', () => {
    const onClick = vi.fn();
    render(<CardCard card={makeCard()} onClick={onClick} />);

    const el = screen.getByRole('button');
    fireEvent.keyDown(el, { key: 'Enter' });
    expect(onClick).toHaveBeenCalledTimes(1);

    fireEvent.keyDown(el, { key: ' ' });
    expect(onClick).toHaveBeenCalledTimes(2);
  });

  it('does not have role="button" when onClick is not provided', () => {
    render(<CardCard card={makeCard()} />);

    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });
});

describe('CardGrid', () => {
  const defaultProps = {
    cards: [makeCard(), makeCard({ name: 'Sol Ring', mana_cost: '{1}', type_line: 'Artifact' })],
    total: 40,
    page: 1,
    onPageChange: vi.fn(),
    isLoading: false,
  };

  it('renders cards in grid', () => {
    render(<CardGrid {...defaultProps} />);

    expect(screen.getByText('Eternal Witness')).toBeInTheDocument();
    expect(screen.getByText('Sol Ring')).toBeInTheDocument();
  });

  it('shows result count header', () => {
    render(<CardGrid {...defaultProps} />);

    expect(screen.getByText('Showing 1-20 of 40 results')).toBeInTheDocument();
  });

  it('shows correct result count for page 2', () => {
    render(<CardGrid {...defaultProps} page={2} />);

    expect(screen.getByText('Showing 21-40 of 40 results')).toBeInTheDocument();
  });

  it('disables Previous button on page 1', () => {
    render(<CardGrid {...defaultProps} />);

    expect(screen.getByText('Previous')).toBeDisabled();
  });

  it('disables Next button on last page', () => {
    render(<CardGrid {...defaultProps} page={2} />);

    expect(screen.getByText('Next')).toBeDisabled();
  });

  it('calls onPageChange when pagination buttons are clicked', () => {
    const onPageChange = vi.fn();
    render(<CardGrid {...defaultProps} page={1} onPageChange={onPageChange} />);

    fireEvent.click(screen.getByText('Next'));
    expect(onPageChange).toHaveBeenCalledWith(2);
  });

  it('shows skeleton grid when isLoading is true', () => {
    const { container } = render(<CardGrid {...defaultProps} isLoading={true} cards={[]} />);

    const skeletons = container.querySelectorAll('[data-testid="card-skeleton"]');
    expect(skeletons.length).toBe(8);
  });

  it('shows empty state when no cards and not loading', () => {
    render(<CardGrid {...defaultProps} cards={[]} total={0} />);

    expect(screen.getByText('No cards found')).toBeInTheDocument();
  });
});
