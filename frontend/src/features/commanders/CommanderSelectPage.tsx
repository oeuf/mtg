import { useNavigate } from "react-router-dom";
import { useCommanderSearch } from "./useCommanderSearch";
import { CommanderCard } from "./CommanderCard";
import { Input } from "../../components/ui/Input";
import { Badge } from "../../components/ui/Badge";
import { LoadingSpinner } from "../../components/LoadingSpinner";

const COLORS = ["W", "U", "B", "R", "G"] as const;

const colorVariantMap: Record<string, "mana-W" | "mana-U" | "mana-B" | "mana-R" | "mana-G"> = {
  W: "mana-W",
  U: "mana-U",
  B: "mana-B",
  R: "mana-R",
  G: "mana-G",
};

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

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-4xl font-bold mb-4">Select a Commander</h1>
      <p className="text-gray-400 mb-6">
        Browse and search for commanders to start building your deck.
      </p>

      <Input
        label="Search commanders"
        placeholder="Search by name..."
        value={searchText}
        onChange={(e) => setSearchText(e.target.value)}
      />

      <div className="flex gap-2 mt-4 mb-6">
        {COLORS.map((color) => {
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
