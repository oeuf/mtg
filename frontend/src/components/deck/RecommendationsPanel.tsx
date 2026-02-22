import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { commandersAPI, cardsAPI } from "../../services/api";
import { LoadingSpinner } from "../LoadingSpinner";
import { RECOMMENDATION_ROLES } from "../../constants/mtg";

type Tab = "synergies" | "by-role" | "similar";

const TABS: { key: Tab; label: string }[] = [
  { key: "synergies", label: "Synergies" },
  { key: "by-role", label: "By Role" },
  { key: "similar", label: "Similar" },
];

interface RecommendationsPanelProps {
  commanderName: string;
  onAddCard: (cardName: string) => void;
  deckCardNames: string[];
}

export function RecommendationsPanel({
  commanderName,
  onAddCard,
  deckCardNames,
}: RecommendationsPanelProps) {
  const [activeTab, setActiveTab] = useState<Tab>("synergies");
  const [selectedRole, setSelectedRole] = useState<string | null>(null);

  const deckSet = new Set(deckCardNames);

  const synergiesQuery = useQuery({
    queryKey: ["synergies", commanderName],
    queryFn: () => commandersAPI.getSynergies(commanderName).then((r) => r.data.synergies),
    enabled: activeTab === "synergies",
  });

  const recommendationsQuery = useQuery({
    queryKey: ["recommendations", commanderName],
    queryFn: () => commandersAPI.getRecommendations(commanderName).then((r) => r.data.recommendations),
    enabled: activeTab === "similar",
  });

  const roleQuery = useQuery({
    queryKey: ["role-cards", selectedRole],
    queryFn: () => cardsAPI.getByRole(selectedRole!).then((r) => r.data),
    enabled: activeTab === "by-role" && selectedRole !== null,
  });

  return (
    <div>
      <div className="flex border-b border-gray-700 mb-3">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            type="button"
            className={`px-3 py-2 text-sm ${activeTab === tab.key ? "border-b-2 border-brand-500 text-white" : "text-gray-400"}`}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === "synergies" && (
        <>
          {synergiesQuery.isLoading && <LoadingSpinner size="sm" />}
          {synergiesQuery.data?.map((s) => (
            <CardRecommendationRow
              key={s.card_name}
              cardName={s.card_name}
              detail={`Score: ${(s.synergy_score ?? 0).toFixed(2)}`}
              inDeck={deckSet.has(s.card_name)}
              onAdd={onAddCard}
            />
          ))}
        </>
      )}

      {activeTab === "by-role" && (
        <>
          <div className="flex flex-wrap gap-2 mb-3">
            {RECOMMENDATION_ROLES.map((role) => (
              <button
                key={role}
                type="button"
                className={`px-2 py-1 text-xs rounded ${selectedRole === role ? "bg-brand-500 text-white" : "bg-gray-700 text-gray-300"}`}
                onClick={() => setSelectedRole(role)}
              >
                {role}
              </button>
            ))}
          </div>
          {roleQuery.isLoading && <LoadingSpinner size="sm" />}
          {roleQuery.data?.map((card) => (
            <CardRecommendationRow
              key={card.name}
              cardName={card.name}
              detail={card.mana_cost}
              inDeck={deckSet.has(card.name)}
              onAdd={onAddCard}
            />
          ))}
        </>
      )}

      {activeTab === "similar" && (
        <>
          {recommendationsQuery.isLoading && <LoadingSpinner size="sm" />}
          {recommendationsQuery.data?.map((r) => (
            <CardRecommendationRow
              key={r.card_name}
              cardName={r.card_name}
              detail={`Score: ${(r.score ?? 0).toFixed(2)}`}
              inDeck={deckSet.has(r.card_name)}
              onAdd={onAddCard}
            />
          ))}
        </>
      )}
    </div>
  );
}

function CardRecommendationRow({
  cardName,
  detail,
  inDeck,
  onAdd,
}: {
  cardName: string;
  detail: string;
  inDeck: boolean;
  onAdd: (name: string) => void;
}) {
  return (
    <div className="flex items-center py-1 border-b border-gray-700">
      <span className="flex-1 text-sm">{cardName}</span>
      <span className="text-xs text-gray-400 mr-2">{detail}</span>
      {inDeck ? (
        <span className="text-xs text-green-400">Added</span>
      ) : (
        <button
          type="button"
          className="text-xs text-brand-400 hover:text-brand-300"
          onClick={() => onAdd(cardName)}
        >
          Add
        </button>
      )}
    </div>
  );
}
