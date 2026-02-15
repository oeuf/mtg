import { useState, useEffect, useRef, useCallback, type KeyboardEvent } from 'react';

export interface AutocompleteItem {
  name: string;
  type_line?: string;
  mana_cost?: string;
}

interface SearchAutocompleteProps {
  placeholder?: string;
  label?: string;
  onSelect: (item: AutocompleteItem) => void;
  onChange?: (value: string) => void;
  fetchSuggestions: (query: string) => Promise<AutocompleteItem[]>;
  value?: string;
  minChars?: number;
  debounceMs?: number;
  className?: string;
}

export function SearchAutocomplete({
  placeholder,
  label,
  onSelect,
  onChange,
  fetchSuggestions,
  value,
  minChars = 2,
  debounceMs = 300,
  className = '',
}: SearchAutocompleteProps) {
  const [inputValue, setInputValue] = useState(value ?? '');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const [suggestions, setSuggestions] = useState<AutocompleteItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>(undefined);
  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (value !== undefined) {
      setInputValue(value);
    }
  }, [value]);

  // Debounce: set debouncedQuery after delay
  useEffect(() => {
    if (inputValue.length < minChars) {
      setSuggestions([]);
      setIsOpen(false);
      setDebouncedQuery('');
      return;
    }

    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setDebouncedQuery(inputValue);
    }, debounceMs);

    return () => clearTimeout(debounceRef.current);
  }, [inputValue, minChars, debounceMs]);

  // Fetch when debouncedQuery changes
  useEffect(() => {
    if (!debouncedQuery) return;

    let cancelled = false;
    setIsLoading(true);

    fetchSuggestions(debouncedQuery).then((results) => {
      if (cancelled) return;
      setSuggestions(results);
      setIsOpen(true);
      setHighlightedIndex(-1);
      setIsLoading(false);
    });

    return () => {
      cancelled = true;
    };
  }, [debouncedQuery, fetchSuggestions]);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const val = e.target.value;
      setInputValue(val);
      onChange?.(val);
    },
    [onChange],
  );

  const selectItem = useCallback(
    (item: AutocompleteItem) => {
      setInputValue(item.name);
      setIsOpen(false);
      setSuggestions([]);
      onSelect(item);
    },
    [onSelect],
  );

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLInputElement>) => {
      if (!isOpen) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setHighlightedIndex((prev) =>
          prev < suggestions.length - 1 ? prev + 1 : prev,
        );
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setHighlightedIndex((prev) => (prev > 0 ? prev - 1 : prev));
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (highlightedIndex >= 0 && highlightedIndex < suggestions.length) {
          selectItem(suggestions[highlightedIndex]);
        }
      } else if (e.key === 'Escape') {
        setIsOpen(false);
      }
    },
    [isOpen, highlightedIndex, suggestions, selectItem],
  );

  const handleBlur = useCallback(() => {
    setTimeout(() => setIsOpen(false), 150);
  }, []);

  const inputId = label ? label.toLowerCase().replace(/\s+/g, '-') : undefined;

  return (
    <div ref={wrapperRef} className={`relative ${className}`}>
      {label && (
        <label
          htmlFor={inputId}
          className="block text-sm font-medium text-gray-300 mb-1"
        >
          {label}
        </label>
      )}
      <input
        id={inputId}
        type="text"
        placeholder={placeholder}
        value={inputValue}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        onBlur={handleBlur}
        className="w-full rounded-md border border-gray-600 bg-gray-800 px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-500"
      />
      {isOpen && (
        <div className="absolute z-10 w-full mt-1 bg-gray-800 border border-gray-600 rounded-md shadow-lg max-h-64 overflow-y-auto">
          {isLoading && (
            <div className="px-3 py-2 text-gray-400">Loading...</div>
          )}
          {!isLoading && suggestions.length === 0 && (
            <div className="px-3 py-2 text-gray-400">No results found</div>
          )}
          {!isLoading &&
            suggestions.map((item, index) => (
              <button
                key={item.name}
                type="button"
                className={`w-full text-left px-3 py-2 cursor-pointer ${
                  index === highlightedIndex
                    ? 'bg-gray-700'
                    : 'hover:bg-gray-700'
                }`}
                onMouseDown={() => selectItem(item)}
              >
                <span className="font-bold text-white">{item.name}</span>
                {item.type_line && (
                  <span className="ml-2 text-sm text-gray-400">
                    {item.type_line}
                  </span>
                )}
                {item.mana_cost && (
                  <span className="ml-2 text-xs text-gray-500">
                    {item.mana_cost}
                  </span>
                )}
              </button>
            ))}
        </div>
      )}
    </div>
  );
}
