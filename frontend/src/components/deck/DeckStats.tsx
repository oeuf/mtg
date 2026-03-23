import type { Card } from "../../types";

interface DeckStatsProps {
  cards: Card[];
  commander: { name: string; color_identity: string[] } | null;
}

export function DeckStats({ cards, commander }: DeckStatsProps) {
  const avgCmc = cards.length > 0
    ? (cards.reduce((sum, c) => sum + c.cmc, 0) / cards.length).toFixed(1)
    : "0.0";

  return (
    <div className="flex gap-4 text-sm">
      <span>Cards: {cards.length}/99</span>
      <span>Avg CMC: {avgCmc}</span>
      {commander && (
        <span>Colors: {commander.color_identity.join(", ")}</span>
      )}
    </div>
  );
}
