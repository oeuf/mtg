interface RangeSliderProps {
  label: string;
  min: number;
  max: number;
  value: [number, number];
  onChange: (range: [number, number]) => void;
}

export function RangeSlider({ label, min, max, value, onChange }: RangeSliderProps) {
  return (
    <div className="mb-4">
      <h4 className="text-sm font-semibold text-gray-300 mb-2">{label}</h4>
      <div className="flex items-center gap-2">
        <input
          type="number"
          min={min}
          max={max}
          value={value[0]}
          onChange={(e) => onChange([Number(e.target.value), value[1]])}
          className="w-16 bg-gray-700 text-gray-200 rounded px-2 py-1 text-sm"
        />
        <span className="text-gray-400 text-sm">to</span>
        <input
          type="number"
          min={min}
          max={max}
          value={value[1]}
          onChange={(e) => onChange([value[0], Number(e.target.value)])}
          className="w-16 bg-gray-700 text-gray-200 rounded px-2 py-1 text-sm"
        />
      </div>
    </div>
  );
}
