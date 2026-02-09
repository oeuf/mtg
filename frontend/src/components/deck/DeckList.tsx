import type { Card } from "../../types";
import { extractPrimaryType } from "../../features/deck-builder/useDeckBuilder";
import { CardRow } from "./CardRow";

interface DeckListProps {
  cards: Card[];
  onRemoveCard: (name: string) => void;
}

const TYPE_ORDER = ["Creature", "Planeswalker", "Instant", "Sorcery", "Artifact", "Enchantment", "Land"] as const;

const TYPE_LABELS: Record<string, string> = {
  Creature: "Creatures",
  Planeswalker: "Planeswalkers",
  Instant: "Instants",
  Sorcery: "Sorceries",
  Artifact: "Artifacts",
  Enchantment: "Enchantments",
  Land: "Lands",
};

export function DeckList({ cards, onRemoveCard }: DeckListProps) {
  const groups = new Map<string, Card[]>();

  for (const card of cards) {
    const type = extractPrimaryType(card.type_line);
    const group = groups.get(type) ?? [];
    group.push(card);
    groups.set(type, group);
  }

  // Sort each group by CMC
  for (const group of groups.values()) {
    group.sort((a, b) => a.cmc - b.cmc);
  }

  return (
    <div>
      {TYPE_ORDER.map((type) => {
        const group = groups.get(type);
        if (!group || group.length === 0) return null;
        return (
          <div key={type} className="mb-4">
            <h3 className="font-semibold text-sm text-gray-300 mb-1">
              {TYPE_LABELS[type]} ({group.length})
            </h3>
            {group.map((card) => (
              <CardRow key={card.name} card={card} onRemove={onRemoveCard} />
            ))}
          </div>
        );
      })}
      {/* Render "Other" if any */}
      {groups.has("Other") && (
        <div className="mb-4">
          <h3 className="font-semibold text-sm text-gray-300 mb-1">
            Other ({groups.get("Other")!.length})
          </h3>
          {groups.get("Other")!.map((card) => (
            <CardRow key={card.name} card={card} onRemove={onRemoveCard} />
          ))}
        </div>
      )}
    </div>
  );
}
