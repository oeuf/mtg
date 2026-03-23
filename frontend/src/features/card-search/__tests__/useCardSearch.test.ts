import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createElement, type ReactNode } from "react";
import { useCardSearch } from "../useCardSearch";
import { cardsAPI } from "../../../services/api";
import type { Card } from "../../../types";

vi.mock("../../../services/api", () => ({
  cardsAPI: {
    search: vi.fn(),
  },
}));

const mockCards: Card[] = [
  {
    name: "Sol Ring",
    mana_cost: "{1}",
    cmc: 1,
    type_line: "Artifact",
    oracle_text: "{T}: Add {C}{C}.",
    color_identity: [],
    colors: [],
    keywords: [],
    is_legendary: false,
    edhrec_rank: 1,
    functional_categories: ["ramp"],
    mechanics: ["mana_production"],
    themes: ["artifacts"],
    archetype: null,
    popularity_score: 100,
  },
  {
    name: "Swords to Plowshares",
    mana_cost: "{W}",
    cmc: 1,
    type_line: "Instant",
    oracle_text:
      "Exile target creature. Its controller gains life equal to its power.",
    color_identity: ["W"],
    colors: ["W"],
    keywords: [],
    is_legendary: false,
    edhrec_rank: 2,
    functional_categories: ["removal"],
    mechanics: ["exile_mechanic"],
    themes: ["removal"],
    archetype: null,
    popularity_score: 98,
  },
];

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
  return ({ children }: { children: ReactNode }) =>
    createElement(QueryClientProvider, { client: queryClient }, children);
}

describe("useCardSearch", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("returns initial loading state", () => {
    vi.mocked(cardsAPI.search).mockReturnValue(new Promise(() => {}) as never);

    const { result } = renderHook(() => useCardSearch(), {
      wrapper: createWrapper(),
    });

    expect(result.current.isLoading).toBe(true);
    expect(result.current.results).toBeUndefined();
    expect(result.current.error).toBeNull();
  });

  it("returns results after API resolves", async () => {
    vi.mocked(cardsAPI.search).mockResolvedValue({
      data: { items: mockCards, total: 2 },
    } as never);

    const { result } = renderHook(() => useCardSearch(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.results).toEqual({ items: mockCards, total: 2 });
  });

  it("updateFilter updates the filter value", async () => {
    vi.mocked(cardsAPI.search).mockResolvedValue({
      data: { items: mockCards, total: 2 },
    } as never);

    const { result } = renderHook(() => useCardSearch(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    act(() => {
      result.current.updateFilter("text_search", "sol ring");
    });

    expect(result.current.filters.text_search).toBe("sol ring");
  });

  it("updateFilter resets page to 1", async () => {
    vi.mocked(cardsAPI.search).mockResolvedValue({
      data: { items: mockCards, total: 45 },
    } as never);

    const { result } = renderHook(() => useCardSearch(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // First go to page 3
    act(() => {
      result.current.setPage(3);
    });

    expect(result.current.page).toBe(3);

    // Then update a filter - page should reset to 1
    act(() => {
      result.current.updateFilter("colors", ["W"]);
    });

    expect(result.current.page).toBe(1);
    expect(result.current.filters.colors).toEqual(["W"]);
  });

  it("clearFilters resets all filters to defaults", async () => {
    vi.mocked(cardsAPI.search).mockResolvedValue({
      data: { items: mockCards, total: 2 },
    } as never);

    const { result } = renderHook(() => useCardSearch(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Set some filters
    act(() => {
      result.current.updateFilter("text_search", "sol");
      result.current.updateFilter("colors", ["W"]);
    });

    expect(result.current.filters.text_search).toBe("sol");
    expect(result.current.filters.colors).toEqual(["W"]);

    // Clear filters
    act(() => {
      result.current.clearFilters();
    });

    expect(result.current.filters).toEqual({ page: 1, limit: 20 });
  });

  it("setPage updates the page number", async () => {
    vi.mocked(cardsAPI.search).mockResolvedValue({
      data: { items: mockCards, total: 45 },
    } as never);

    const { result } = renderHook(() => useCardSearch(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    act(() => {
      result.current.setPage(2);
    });

    expect(result.current.page).toBe(2);
    expect(result.current.filters.page).toBe(2);
  });

  it("totalPages computes correctly", async () => {
    vi.mocked(cardsAPI.search).mockResolvedValue({
      data: { items: mockCards, total: 45 },
    } as never);

    const { result } = renderHook(() => useCardSearch(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // 45 total / 20 limit = 2.25, Math.ceil = 3
    expect(result.current.totalPages).toBe(3);
  });

  it("returns error state when API fails", async () => {
    vi.mocked(cardsAPI.search).mockRejectedValue(
      new Error("Network error"),
    );

    const { result } = renderHook(() => useCardSearch(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toBeInstanceOf(Error);
    expect(result.current.error?.message).toBe("Network error");
    expect(result.current.results).toBeUndefined();
  });
});
