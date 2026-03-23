import { Link } from 'react-router-dom';

interface SimilarCard {
  name: string;
  score: number;
}

interface SimilarCardsProps {
  cards: SimilarCard[];
}

export function SimilarCards({ cards }: SimilarCardsProps) {
  if (cards.length === 0) {
    return <p className="text-gray-500 text-sm">No similar cards found.</p>;
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
      {cards.map((card) => (
        <Link
          key={card.name}
          to={`/cards/${encodeURIComponent(card.name)}`}
          className="bg-gray-800 rounded-lg p-3 hover:ring-2 hover:ring-brand-500 transition-all"
        >
          <p className="font-semibold text-white">{card.name}</p>
          <p className="text-sm text-gray-400">
            {(card.score * 100).toFixed(0)}% similar
          </p>
        </Link>
      ))}
    </div>
  );
}
