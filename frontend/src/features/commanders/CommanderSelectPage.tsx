import { useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useCommanderSearch } from "./useCommanderSearch";
import { CommanderCard } from "./CommanderCard";
import { SearchAutocomplete } from "../../components/SearchAutocomplete";
import type { AutocompleteItem } from "../../components/SearchAutocomplete";
import { Badge } from "../../components/ui/Badge";
import { LoadingSpinner } from "../../components/LoadingSpinner";
import { cardsAPI } from "../../services/api";
import { MANA_COLORS, colorVariantMap } from "../../constants/mtg";

export default function CommanderSelectPage() {
  const navigate = useNavigate();
  const {
    commanders,
    isLoading,
    searchText,
    setSearchText,
    colorFilter,
    toggleColor,
  } = useCommanderSearch();

  const fetchCommanderSuggestions = useCallback(
    async (query: string): Promise<AutocompleteItem[]> => {
      const response = await cardsAPI.autocomplete(query, true);
      return response.data;
    },
    [],
  );

  const handleSelect = useCallback(
    (item: AutocompleteItem) => {
      navigate(`/deck-builder/${encodeURIComponent(item.name)}`);
    },
    [navigate],
  );

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-4xl font-bold mb-4">Select a Commander</h1>
      <p className="text-gray-400 mb-6">
        Browse and search for commanders to start building your deck.
      </p>

      <SearchAutocomplete
        label="Search commanders"
        placeholder="Search by name..."
        fetchSuggestions={fetchCommanderSuggestions}
        onSelect={handleSelect}
        onChange={setSearchText}
        value={searchText}
      />

      <div className="flex gap-2 mt-4 mb-6">
        {MANA_COLORS.map((color) => {
          const active = colorFilter.includes(color);
          return (
            <button
              key={color}
              type="button"
              onClick={() => toggleColor(color)}
              className={`rounded-full transition-all ${active ? "ring-2 ring-white" : "opacity-60"}`}
            >
              <Badge variant={colorVariantMap[color]}>{color}</Badge>
            </button>
          );
        })}
      </div>

      {isLoading && <LoadingSpinner size="lg" />}

      {!isLoading && commanders.length === 0 && (
        <p className="text-gray-400 text-center mt-8">No commanders found</p>
      )}

      {!isLoading && commanders.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {commanders.map((commander) => (
            <CommanderCard
              key={commander.name}
              commander={commander}
              onClick={(name) =>
                navigate(`/deck-builder/${encodeURIComponent(name)}`)
              }
            />
          ))}
        </div>
      )}
    </div>
  );
}
