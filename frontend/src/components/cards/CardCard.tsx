import type { Card } from '../../types/card';
import { Badge } from '../ui/Badge';

type BadgeVariant = 'default' | 'mana-W' | 'mana-U' | 'mana-B' | 'mana-R' | 'mana-G';

interface CardCardProps {
  card: Card;
  onClick?: (name: string) => void;
}

function colorToVariant(color: string): BadgeVariant {
  const map: Record<string, BadgeVariant> = {
    W: 'mana-W',
    U: 'mana-U',
    B: 'mana-B',
    R: 'mana-R',
    G: 'mana-G',
  };
  return map[color] ?? 'default';
}

function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}

export function CardCard({ card, onClick }: CardCardProps) {
  const interactive = !!onClick;

  const handleClick = () => {
    onClick?.(card.name);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onClick?.(card.name);
    }
  };

  return (
    <div
      className={`bg-gray-800 rounded-lg p-4${interactive ? ' hover:ring-2 hover:ring-brand-500 cursor-pointer' : ''}`}
      {...(interactive
        ? {
            role: 'button',
            tabIndex: 0,
            onClick: handleClick,
            onKeyDown: handleKeyDown,
          }
        : {})}
    >
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-bold text-lg">{card.name}</h3>
        <span className="text-gray-400 text-sm">{card.mana_cost}</span>
      </div>
      <p className="text-gray-400 text-sm mb-2">{card.type_line}</p>
      {card.oracle_text && (
        <p className="text-gray-300 text-sm mb-3">
          {truncateText(card.oracle_text, 100)}
        </p>
      )}
      {card.color_identity.length > 0 && (
        <div className="flex gap-1">
          {card.color_identity.map((color) => (
            <Badge key={color} variant={colorToVariant(color)}>
              {color}
            </Badge>
          ))}
        </div>
      )}
    </div>
  );
}
