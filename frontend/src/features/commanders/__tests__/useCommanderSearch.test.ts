import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createElement, type ReactNode } from "react";
import { useCommanderSearch } from "../useCommanderSearch";
import { commandersAPI } from "../../../services/api";
import type { Commander } from "../../../types";

vi.mock("../../../services/api", () => ({
  commandersAPI: {
    list: vi.fn(),
  },
}));

const mockCommanders: Commander[] = [
  {
    name: "Muldrotha, the Gravetide",
    mana_cost: "{3}{B}{G}{U}",
    cmc: 6,
    type_line: "Legendary Creature — Elemental Avatar",
    oracle_text:
      "During each of your turns, you may play up to one permanent card of each permanent type from your graveyard.",
    color_identity: ["B", "G", "U"],
    colors: ["B", "G", "U"],
    keywords: [],
    is_legendary: true,
    edhrec_rank: 5,
    functional_categories: ["recursion"],
    mechanics: ["graveyard_recursion"],
    themes: ["graveyard"],
    archetype: "graveyard",
    popularity_score: 95,
    power: 6,
    toughness: 6,
  },
  {
    name: "Atraxa, Praetors' Voice",
    mana_cost: "{G}{W}{U}{B}",
    cmc: 4,
    type_line: "Legendary Creature — Phyrexian Angel Horror",
    oracle_text:
      "Flying, vigilance, deathtouch, lifelink\nAt the beginning of your end step, proliferate.",
    color_identity: ["B", "G", "U", "W"],
    colors: ["B", "G", "U", "W"],
    keywords: ["flying", "vigilance", "deathtouch", "lifelink"],
    is_legendary: true,
    edhrec_rank: 3,
    functional_categories: ["proliferate"],
    mechanics: ["proliferate"],
    themes: ["counters"],
    archetype: "counters",
    popularity_score: 98,
    power: 4,
    toughness: 4,
  },
  {
    name: "Krenko, Mob Boss",
    mana_cost: "{2}{R}{R}",
    cmc: 4,
    type_line: "Legendary Creature — Goblin Warrior",
    oracle_text:
      "{T}: Create X 1/1 red Goblin creature tokens, where X is the number of Goblins you control.",
    color_identity: ["R"],
    colors: ["R"],
    keywords: [],
    is_legendary: true,
    edhrec_rank: 20,
    functional_categories: ["token_generation"],
    mechanics: ["token_creation"],
    themes: ["tribal"],
    archetype: "tribal",
    popularity_score: 85,
    power: 3,
    toughness: 3,
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

describe("useCommanderSearch", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("returns commanders from the API", async () => {
    vi.mocked(commandersAPI.list).mockResolvedValue({
      data: { items: mockCommanders, total: mockCommanders.length },
    } as never);

    const { result } = renderHook(() => useCommanderSearch(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.commanders).toHaveLength(3);
    expect(result.current.commanders[0].name).toBe(
      "Muldrotha, the Gravetide",
    );
  });

  it("filters commanders by search text (case-insensitive)", async () => {
    vi.mocked(commandersAPI.list).mockResolvedValue({
      data: { items: mockCommanders, total: mockCommanders.length },
    } as never);

    const { result } = renderHook(() => useCommanderSearch(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    act(() => {
      result.current.setSearchText("muldrotha");
    });

    expect(result.current.commanders).toHaveLength(1);
    expect(result.current.commanders[0].name).toBe(
      "Muldrotha, the Gravetide",
    );
  });

  it("filters commanders by color identity", async () => {
    vi.mocked(commandersAPI.list).mockResolvedValue({
      data: { items: mockCommanders, total: mockCommanders.length },
    } as never);

    const { result } = renderHook(() => useCommanderSearch(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    act(() => {
      result.current.setColorFilter(["W"]);
    });

    // Only Atraxa has W in her color identity
    expect(result.current.commanders).toHaveLength(1);
    expect(result.current.commanders[0].name).toBe(
      "Atraxa, Praetors' Voice",
    );
  });

  it("applies combined text and color filters", async () => {
    vi.mocked(commandersAPI.list).mockResolvedValue({
      data: { items: mockCommanders, total: mockCommanders.length },
    } as never);

    const { result } = renderHook(() => useCommanderSearch(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Both Muldrotha and Atraxa have B and U
    act(() => {
      result.current.setColorFilter(["B", "U"]);
    });

    expect(result.current.commanders).toHaveLength(2);

    // Adding search text narrows to just Muldrotha
    act(() => {
      result.current.setSearchText("gravetide");
    });

    expect(result.current.commanders).toHaveLength(1);
    expect(result.current.commanders[0].name).toBe(
      "Muldrotha, the Gravetide",
    );
  });

  it("toggleColor adds color when not present", async () => {
    vi.mocked(commandersAPI.list).mockResolvedValue({
      data: { items: mockCommanders, total: mockCommanders.length },
    } as never);

    const { result } = renderHook(() => useCommanderSearch(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.colorFilter).toEqual([]);

    act(() => {
      result.current.toggleColor("R");
    });

    expect(result.current.colorFilter).toEqual(["R"]);
    // Only Krenko has R
    expect(result.current.commanders).toHaveLength(1);
    expect(result.current.commanders[0].name).toBe("Krenko, Mob Boss");
  });

  it("toggleColor removes color when already present", async () => {
    vi.mocked(commandersAPI.list).mockResolvedValue({
      data: { items: mockCommanders, total: mockCommanders.length },
    } as never);

    const { result } = renderHook(() => useCommanderSearch(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    act(() => {
      result.current.toggleColor("R");
    });

    expect(result.current.colorFilter).toEqual(["R"]);

    act(() => {
      result.current.toggleColor("R");
    });

    expect(result.current.colorFilter).toEqual([]);
    // All commanders should be back
    expect(result.current.commanders).toHaveLength(3);
  });

  it("shows loading state while fetching", () => {
    vi.mocked(commandersAPI.list).mockReturnValue(
      new Promise(() => {}) as never,
    );

    const { result } = renderHook(() => useCommanderSearch(), {
      wrapper: createWrapper(),
    });

    expect(result.current.isLoading).toBe(true);
    expect(result.current.commanders).toEqual([]);
  });

  it("returns error state on API failure", async () => {
    vi.mocked(commandersAPI.list).mockRejectedValue(
      new Error("Network error"),
    );

    const { result } = renderHook(() => useCommanderSearch(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toBeInstanceOf(Error);
    expect(result.current.error?.message).toBe("Network error");
    expect(result.current.commanders).toEqual([]);
  });
});
