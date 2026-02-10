import type { Card } from '../../types/card';
import { Button } from '../ui/Button';
import { LoadingSpinner } from '../LoadingSpinner';
import { CardCard } from './CardCard';

interface CardGridProps {
  cards: Card[];
  total: number;
  page: number;
  onPageChange: (page: number) => void;
  isLoading: boolean;
  onCardClick?: (name: string) => void;
}

const PAGE_SIZE = 20;

export function CardGrid({ cards, total, page, onPageChange, isLoading, onCardClick }: CardGridProps) {
  const totalPages = Math.ceil(total / PAGE_SIZE);
  const start = (page - 1) * PAGE_SIZE + 1;
  const end = Math.min(page * PAGE_SIZE, total);

  if (isLoading) {
    return <LoadingSpinner size="lg" />;
  }

  if (cards.length === 0) {
    return <p className="text-gray-400 text-center py-8">No cards found</p>;
  }

  return (
    <div>
      <p className="text-sm text-gray-400 mb-4">
        Showing {start}-{end} of {total} results
      </p>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {cards.map((card) => (
          <CardCard key={card.name} card={card} onClick={onCardClick} />
        ))}
      </div>
      <div className="flex justify-between items-center mt-6">
        <Button
          variant="secondary"
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
        >
          Previous
        </Button>
        <span className="text-sm text-gray-400">
          Page {page} of {totalPages}
        </span>
        <Button
          variant="secondary"
          disabled={page >= totalPages}
          onClick={() => onPageChange(page + 1)}
        >
          Next
        </Button>
      </div>
    </div>
  );
}
