import { Link } from 'react-router-dom';

interface SynergyCard {
  name: string;
  score: number;
}

interface SynergyCardsProps {
  cards: SynergyCard[];
}

export function SynergyCards({ cards }: SynergyCardsProps) {
  if (cards.length === 0) {
    return <p className="text-gray-500 text-sm">No synergies found.</p>;
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
          <div className="flex items-center gap-2 mt-1">
            <div className="flex-1 bg-gray-700 rounded-full h-2">
              <div
                className="bg-brand-500 h-2 rounded-full"
                style={{ width: `${card.score * 100}%` }}
              />
            </div>
            <span className="text-xs text-gray-400">
              {(card.score * 100).toFixed(0)}%
            </span>
          </div>
        </Link>
      ))}
    </div>
  );
}
