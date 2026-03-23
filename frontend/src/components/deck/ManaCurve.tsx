import type { Card } from "../../types";

interface ManaCurveProps {
  cards: Card[];
}

const BUCKETS = ["0", "1", "2", "3", "4", "5", "6", "7+"] as const;

export function ManaCurve({ cards }: ManaCurveProps) {
  const counts = new Array(8).fill(0);

  for (const card of cards) {
    const idx = card.cmc >= 7 ? 7 : Math.floor(card.cmc);
    counts[idx]++;
  }

  return (
    <div className="flex items-end gap-2">
      {BUCKETS.map((label, i) => (
        <div key={label} data-testid="mana-curve-bar" className="flex flex-col items-center">
          <span className="text-xs">{counts[i]}</span>
          <div
            className="w-8 bg-brand-500"
            style={{ height: `${counts[i] * 16}px` }}
          />
          <span className="text-xs mt-1">{label}</span>
        </div>
      ))}
    </div>
  );
}
