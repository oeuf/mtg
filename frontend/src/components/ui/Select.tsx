import type { SelectHTMLAttributes } from 'react';

interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps extends Omit<SelectHTMLAttributes<HTMLSelectElement>, 'children'> {
  label: string;
  options: SelectOption[];
}

export function Select({ label, options, className = '', id, ...rest }: SelectProps) {
  const selectId = id || label.toLowerCase().replace(/\s+/g, '-');
  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={selectId} className="text-sm font-medium text-gray-300">
        {label}
      </label>
      <select
        id={selectId}
        className={`rounded-md border border-gray-600 bg-gray-800 px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-brand-500 ${className}`}
        {...rest}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}
