import { CheckboxGroup } from './CheckboxGroup';
import { RangeSlider } from './RangeSlider';
import { Button } from '../ui/Button';
import type { CardSearchFilters } from '../../types';
import { MANA_COLORS, ROLES } from '../../constants/mtg';

const CARD_TYPES = ['Creature', 'Instant', 'Sorcery', 'Artifact', 'Enchantment', 'Planeswalker', 'Land'];
const RARITIES = ['Common', 'Uncommon', 'Rare', 'Mythic'];

interface FilterPanelProps {
  filters: CardSearchFilters;
  onUpdateFilter: (key: keyof CardSearchFilters, value: unknown) => void;
  onClear: () => void;
}

export function FilterPanel({ filters, onUpdateFilter, onClear }: FilterPanelProps) {
  const selectedColors = filters.colors ?? [];

  const toggleColor = (color: string) => {
    if (selectedColors.includes(color)) {
      onUpdateFilter('colors', selectedColors.filter((c) => c !== color));
    } else {
      onUpdateFilter('colors', [...selectedColors, color]);
    }
  };

  return (
    <div className="min-w-[200px]">
      <h3 className="text-lg font-bold text-white mb-4">Filters</h3>

      <CheckboxGroup
        label="Card Type"
        options={CARD_TYPES}
        selected={filters.types ?? []}
        onChange={(val) => onUpdateFilter('types', val)}
      />

      <div className="mb-4">
        <h4 className="text-sm font-semibold text-gray-300 mb-2">Color</h4>
        <div className="flex gap-2">
          {MANA_COLORS.map((color) => (
            <button
              key={color}
              type="button"
              onClick={() => toggleColor(color)}
              className={`w-8 h-8 rounded-full text-xs font-bold flex items-center justify-center ${
                selectedColors.includes(color)
                  ? 'ring-2 ring-brand-500 bg-gray-600 text-white'
                  : 'bg-gray-700 text-gray-400'
              }`}
            >
              {color}
            </button>
          ))}
        </div>
      </div>

      <RangeSlider
        label="CMC"
        min={0}
        max={16}
        value={[filters.cmc_min ?? 0, filters.cmc_max ?? 16]}
        onChange={([min, max]) => {
          onUpdateFilter('cmc_min', min);
          onUpdateFilter('cmc_max', max);
        }}
      />

      <CheckboxGroup
        label="Rarity"
        options={RARITIES}
        selected={filters.rarity ?? []}
        onChange={(val) => onUpdateFilter('rarity', val)}
      />

      <CheckboxGroup
        label="Roles"
        options={ROLES}
        selected={filters.roles ?? []}
        onChange={(val) => onUpdateFilter('roles', val)}
      />

      <Button variant="secondary" onClick={onClear} className="w-full mt-4">
        Clear All Filters
      </Button>
    </div>
  );
}
