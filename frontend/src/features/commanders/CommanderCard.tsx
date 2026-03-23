import type { Commander } from "../../types";
import { Badge } from "../../components/ui/Badge";
import { colorVariantMap } from "../../constants/mtg";

interface CommanderCardProps {
  commander: Commander;
  onClick: (name: string) => void;
}

export function CommanderCard({ commander, onClick }: CommanderCardProps) {
  return (
    <button
      type="button"
      className="bg-gray-800 rounded-lg shadow-lg p-4 cursor-pointer transition-all hover:ring-2 hover:ring-brand-500 w-full text-left"
      onClick={() => onClick(commander.name)}
    >
      <h3 className="text-lg font-bold text-white">{commander.name}</h3>
      <p className="text-gray-400 text-sm">{commander.mana_cost}</p>
      <p className="text-gray-300 text-sm mt-1">{commander.type_line}</p>
      <div className="flex gap-1 mt-2">
        {commander.color_identity.map((color) => (
          <Badge key={color} variant={colorVariantMap[color as keyof typeof colorVariantMap] ?? "default"}>
            {color}
          </Badge>
        ))}
      </div>
    </button>
  );
}
