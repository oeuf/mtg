import type { Card } from "../../types";

interface CardRowProps {
  card: Card;
  onRemove: (name: string) => void;
}

export function CardRow({ card, onRemove }: CardRowProps) {
  return (
    <div className="flex items-center py-1 border-b border-gray-700">
      <span data-testid="card-row-name" className="flex-1">
        {card.name}
      </span>
      <span className="text-gray-400 mr-2">{card.mana_cost}</span>
      <button type="button" onClick={() => onRemove(card.name)}>
        ×
      </button>
    </div>
  );
}
