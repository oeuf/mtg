import type { SynergyDimensions } from '../../types';

interface SynergyBreakdownProps {
  dimensions: SynergyDimensions;
}

const DIMENSION_CONFIG = [
  { key: 'role_compatibility' as const, label: 'Role Compatibility', weight: 25 },
  { key: 'mechanic_overlap' as const, label: 'Mechanic Overlap', weight: 20 },
  { key: 'theme_alignment' as const, label: 'Theme Alignment', weight: 20 },
  { key: 'zone_chain' as const, label: 'Zone Chains', weight: 15 },
  { key: 'phase_alignment' as const, label: 'Phase Alignment', weight: 10 },
  { key: 'color_compatibility' as const, label: 'Color Compatibility', weight: 5 },
  { key: 'type_synergy' as const, label: 'Type Synergy', weight: 5 },
];

export function SynergyBreakdown({ dimensions }: SynergyBreakdownProps) {
  return (
    <div className="space-y-2">
      {DIMENSION_CONFIG.map(({ key, label, weight }) => {
        const value = dimensions[key];
        return (
          <div key={key} className="flex items-center gap-2">
            <span className="text-sm text-gray-300 w-40 shrink-0">
              {label} ({weight}%)
            </span>
            <div className="flex-1 bg-gray-700 rounded-full h-3">
              <div
                className="bg-brand-500 h-3 rounded-full transition-all"
                style={{ width: `${value * 100}%` }}
              />
            </div>
            <span className="text-xs text-gray-400 w-10 text-right">
              {(value * 100).toFixed(0)}%
            </span>
          </div>
        );
      })}
    </div>
  );
}
