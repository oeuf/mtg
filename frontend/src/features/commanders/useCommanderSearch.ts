import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { commandersAPI } from "../../services/api";
import type { Commander } from "../../types";
import { useDebounce } from "../../hooks/useDebounce";

export function useCommanderSearch(): {
  commanders: Commander[];
  isLoading: boolean;
  error: Error | null;
  searchText: string;
  setSearchText: (text: string) => void;
  colorFilter: string[];
  setColorFilter: (colors: string[]) => void;
  toggleColor: (color: string) => void;
} {
  const [searchText, setSearchText] = useState("");
  const [colorFilter, setColorFilter] = useState<string[]>([]);
  const debouncedSearch = useDebounce(searchText, 300);

  const { data, isLoading, error } = useQuery({
    queryKey: ["commanders", debouncedSearch],
    queryFn: async () => {
      const response = await commandersAPI.list(1, 50, debouncedSearch || undefined);
      return response.data.items;
    },
  });

  const allCommanders = data ?? [];

  // Color filtering remains client-side (small result set after server-side search)
  const commanders = useMemo(() => {
    if (colorFilter.length === 0) return allCommanders;
    return allCommanders.filter((c) =>
      colorFilter.every((color) => c.color_identity.includes(color)),
    );
  }, [allCommanders, colorFilter]);

  const toggleColor = (color: string) => {
    setColorFilter((prev) =>
      prev.includes(color) ? prev.filter((c) => c !== color) : [...prev, color],
    );
  };

  return {
    commanders,
    isLoading,
    error: error as Error | null,
    searchText,
    setSearchText,
    colorFilter,
    setColorFilter,
    toggleColor,
  };
}
