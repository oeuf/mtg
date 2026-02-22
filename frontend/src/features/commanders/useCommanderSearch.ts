import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { commandersAPI } from "../../services/api";
import type { Commander } from "../../types";

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

  const { data, isLoading, error } = useQuery({
    queryKey: ["commanders"],
    queryFn: async () => {
      const response = await commandersAPI.list(1, 5000);
      return response.data.items;
    },
  });

  const allCommanders = data ?? [];

  const commanders = useMemo(() => {
    let filtered = allCommanders;

    if (searchText) {
      const lower = searchText.toLowerCase();
      filtered = filtered.filter((c) => c.name.toLowerCase().includes(lower));
    }

    if (colorFilter.length > 0) {
      filtered = filtered.filter((c) =>
        colorFilter.every((color) => c.color_identity.includes(color)),
      );
    }

    return filtered;
  }, [allCommanders, searchText, colorFilter]);

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
