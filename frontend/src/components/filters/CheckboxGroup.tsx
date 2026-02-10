interface CheckboxGroupProps {
  label: string;
  options: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
}

export function CheckboxGroup({ label, options, selected, onChange }: CheckboxGroupProps) {
  const toggle = (option: string) => {
    if (selected.includes(option)) {
      onChange(selected.filter((s) => s !== option));
    } else {
      onChange([...selected, option]);
    }
  };

  return (
    <div className="mb-4">
      <h4 className="text-sm font-semibold text-gray-300 mb-2">{label}</h4>
      <div className="space-y-1">
        {options.map((option) => (
          <label key={option} className="flex items-center gap-2 text-gray-300 text-sm cursor-pointer">
            <input
              type="checkbox"
              checked={selected.includes(option)}
              onChange={() => toggle(option)}
              className="rounded border-gray-600"
            />
            {option}
          </label>
        ))}
      </div>
    </div>
  );
}
