import type { ComboResponse } from '../../types';

interface CombosListProps {
  combos: ComboResponse[];
}

export function CombosList({ combos }: CombosListProps) {
  if (combos.length === 0) {
    return <p className="text-gray-500 text-sm">No known combos found.</p>;
  }

  return (
    <div className="space-y-3">
      {combos.map((combo, idx) => (
        <div key={combo.name + idx} className="bg-gray-800 rounded-lg p-3">
          <p className="font-semibold text-white">{combo.name}</p>
          {combo.combo_name && (
            <p className="text-sm text-brand-400 mt-1">{combo.combo_name}</p>
          )}
          {combo.description && (
            <p className="text-sm text-gray-400 mt-1">{combo.description}</p>
          )}
        </div>
      ))}
    </div>
  );
}
