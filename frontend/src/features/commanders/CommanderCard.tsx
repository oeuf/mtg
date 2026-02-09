import type { Commander } from "../../types";
import { Badge } from "../../components/ui/Badge";

const colorVariantMap: Record<string, "mana-W" | "mana-U" | "mana-B" | "mana-R" | "mana-G"> = {
  W: "mana-W",
  U: "mana-U",
  B: "mana-B",
  R: "mana-R",
  G: "mana-G",
};

interface CommanderCardProps {
  commander: Commander;
  onClick: (name: string) => void;
}

export function CommanderCard({ commander, onClick }: CommanderCardProps) {
  return (
    <div
      className="bg-gray-800 rounded-lg shadow-lg p-4 cursor-pointer transition-all hover:ring-2 hover:ring-brand-500"
      onClick={() => onClick(commander.name)}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") onClick(commander.name);
      }}
      role="button"
      tabIndex={0}
    >
      <h3 className="text-lg font-bold text-white">{commander.name}</h3>
      <p className="text-gray-400 text-sm">{commander.mana_cost}</p>
      <p className="text-gray-300 text-sm mt-1">{commander.type_line}</p>
      <div className="flex gap-1 mt-2">
        {commander.color_identity.map((color) => (
          <Badge key={color} variant={colorVariantMap[color] ?? "default"}>
            {color}
          </Badge>
        ))}
      </div>
    </div>
  );
}
