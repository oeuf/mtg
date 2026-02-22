import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { RecommendationsPanel } from "../RecommendationsPanel";

// Mock the API module
vi.mock("../../../services/api", () => ({
  commandersAPI: {
    getSynergies: vi.fn(),
    getRecommendations: vi.fn(),
  },
  cardsAPI: {
    getByRole: vi.fn(),
  },
}));

import { commandersAPI, cardsAPI } from "../../../services/api";

const mockSynergies = [
  { card_name: "Sol Ring", synergy_score: 0.95 },
  { card_name: "Mana Crypt", synergy_score: 0.90 },
];

const mockRecommendations = [
  { card_name: "Rhystic Study", score: 0.88 },
  { card_name: "Cyclonic Rift", score: 0.85 },
];

const mockRoleCards = [
  { name: "Cultivate", mana_cost: "{2}{G}", cmc: 3, type_line: "Sorcery", oracle_text: "", color_identity: ["G"], colors: ["G"], keywords: [], is_legendary: false, edhrec_rank: null, functional_categories: ["Ramp"], mechanics: [], themes: [], archetype: null, popularity_score: 0 },
];

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  };
}

describe("RecommendationsPanel", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (commandersAPI.getSynergies as ReturnType<typeof vi.fn>).mockResolvedValue({
      data: { commander: "Atraxa", synergies: mockSynergies },
    });
    (commandersAPI.getRecommendations as ReturnType<typeof vi.fn>).mockResolvedValue({
      data: { commander: "Atraxa", recommendations: mockRecommendations },
    });
    (cardsAPI.getByRole as ReturnType<typeof vi.fn>).mockResolvedValue({ data: mockRoleCards });
  });

  it("renders 3 tabs", () => {
    render(
      <RecommendationsPanel commanderName="Atraxa" onAddCard={vi.fn()} deckCardNames={[]} />,
      { wrapper: createWrapper() },
    );

    expect(screen.getByText("Synergies")).toBeInTheDocument();
    expect(screen.getByText("By Role")).toBeInTheDocument();
    expect(screen.getByText("Similar")).toBeInTheDocument();
  });

  it("switches between tabs on click", async () => {
    render(
      <RecommendationsPanel commanderName="Atraxa" onAddCard={vi.fn()} deckCardNames={[]} />,
      { wrapper: createWrapper() },
    );

    // Default tab is Synergies - wait for data
    await waitFor(() => {
      expect(screen.getByText("Sol Ring")).toBeInTheDocument();
    });

    // Click Similar tab
    fireEvent.click(screen.getByText("Similar"));
    await waitFor(() => {
      expect(screen.getByText("Rhystic Study")).toBeInTheDocument();
    });
  });

  it("shows loading state while fetching", () => {
    (commandersAPI.getSynergies as ReturnType<typeof vi.fn>).mockReturnValue(new Promise(() => {}));

    render(
      <RecommendationsPanel commanderName="Atraxa" onAddCard={vi.fn()} deckCardNames={[]} />,
      { wrapper: createWrapper() },
    );

    expect(screen.getByRole("status")).toBeInTheDocument();
  });

  it("displays synergy card recommendations", async () => {
    render(
      <RecommendationsPanel commanderName="Atraxa" onAddCard={vi.fn()} deckCardNames={[]} />,
      { wrapper: createWrapper() },
    );

    await waitFor(() => {
      expect(screen.getByText("Sol Ring")).toBeInTheDocument();
      expect(screen.getByText("Mana Crypt")).toBeInTheDocument();
    });
  });

  it("Add button calls onAddCard", async () => {
    const onAddCard = vi.fn();
    render(
      <RecommendationsPanel commanderName="Atraxa" onAddCard={onAddCard} deckCardNames={[]} />,
      { wrapper: createWrapper() },
    );

    await waitFor(() => {
      expect(screen.getByText("Sol Ring")).toBeInTheDocument();
    });

    const addButtons = screen.getAllByText("Add");
    fireEvent.click(addButtons[0]);
    expect(onAddCard).toHaveBeenCalledWith("Sol Ring");
  });

  it("cards in deck show Added badge instead of Add button", async () => {
    render(
      <RecommendationsPanel commanderName="Atraxa" onAddCard={vi.fn()} deckCardNames={["Sol Ring"]} />,
      { wrapper: createWrapper() },
    );

    await waitFor(() => {
      expect(screen.getByText("Sol Ring")).toBeInTheDocument();
    });

    // Sol Ring should show "Added", Mana Crypt should show "Add"
    expect(screen.getByText("Added")).toBeInTheDocument();
    expect(screen.getAllByText("Add")).toHaveLength(1);
  });
});
