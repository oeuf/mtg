import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { describe, it, expect, vi, beforeEach } from "vitest";
import DeckBuilderPage from "../DeckBuilderPage";
import { useDeckBuilder } from "../useDeckBuilder";
import type { Card, Commander } from "../../../types";

// Mock useParams
const mockCommanderParam = "Atraxa, Praetors' Voice";
vi.mock("react-router-dom", () => ({
  useParams: () => ({ commander: mockCommanderParam }),
}));

const makeCard = (overrides: Partial<Card> = {}): Card => ({
  name: "Test Card",
  mana_cost: "{2}{U}",
  cmc: 3,
  type_line: "Creature — Human Wizard",
  oracle_text: "Draw a card.",
  color_identity: ["U"],
  colors: ["U"],
  keywords: [],
  is_legendary: false,
  edhrec_rank: null,
  functional_categories: [],
  mechanics: [],
  themes: [],
  archetype: null,
  popularity_score: 0,
  ...overrides,
});

// Mock the API
const mockCommanderData: Commander = {
  name: "Atraxa, Praetors' Voice",
  mana_cost: "{G}{W}{U}{B}",
  cmc: 4,
  type_line: "Legendary Creature — Phyrexian Angel Horror",
  oracle_text: "Proliferate at end step",
  color_identity: ["B", "G", "U", "W"],
  colors: ["B", "G", "U", "W"],
  keywords: ["flying", "vigilance", "deathtouch", "lifelink"],
  is_legendary: true,
  edhrec_rank: 1,
  functional_categories: [],
  mechanics: [],
  themes: [],
  archetype: null,
  popularity_score: 99,
  power: 4,
  toughness: 4,
};

let mockApiResolve: (value: { data: Commander }) => void;
let mockApiReject: (reason: Error) => void;
let mockApiPromise: Promise<{ data: Commander }>;

function resetMockApi() {
  mockApiPromise = new Promise((resolve, reject) => {
    mockApiResolve = resolve;
    mockApiReject = reject;
  });
}

const solRingCard = makeCard({
  name: "Sol Ring",
  mana_cost: "{1}",
  cmc: 1,
  type_line: "Artifact",
  oracle_text: "{T}: Add {C}{C}.",
  colors: [],
  color_identity: [],
});

vi.mock("../../../services/api", () => ({
  commandersAPI: {
    get: vi.fn(() => mockApiPromise),
    getSynergies: vi.fn(() => Promise.resolve({ data: [] })),
    getRecommendations: vi.fn(() => Promise.resolve({ data: [] })),
  },
  cardsAPI: {
    get: vi.fn(() => Promise.resolve({ data: solRingCard })),
    getByRole: vi.fn(() => Promise.resolve({ data: [] })),
  },
}));

// Mock child components to isolate DeckBuilderPage tests
vi.mock("../../../components/deck/DeckList", () => ({
  DeckList: ({ cards, onRemoveCard }: { cards: unknown[]; onRemoveCard: (name: string) => void }) => (
    <div data-testid="deck-list">
      <span data-testid="deck-list-count">{(cards as unknown[]).length}</span>
      <button type="button" data-testid="mock-remove" onClick={() => onRemoveCard("Test Card")}>
        Remove
      </button>
    </div>
  ),
}));

vi.mock("../../../components/deck/DeckStats", () => ({
  DeckStats: () => <div data-testid="deck-stats" />,
}));

vi.mock("../../../components/deck/ManaCurve", () => ({
  ManaCurve: () => <div data-testid="mana-curve" />,
}));

vi.mock("../../../components/deck/RecommendationsPanel", () => ({
  RecommendationsPanel: ({ onAddCard }: { onAddCard: (name: string) => void }) => (
    <div data-testid="recommendations-panel">
      <button type="button" data-testid="mock-add" onClick={() => onAddCard("Sol Ring")}>
        Add Card
      </button>
    </div>
  ),
}));

function createQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
}

function renderPage() {
  const queryClient = createQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <DeckBuilderPage />
    </QueryClientProvider>,
  );
}

describe("DeckBuilderPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    resetMockApi();
    useDeckBuilder.setState({ commander: null, deck: [] });
  });

  it("shows loading spinner while fetching commander", () => {
    renderPage();
    expect(screen.getByRole("status", { name: /loading/i })).toBeInTheDocument();
  });

  it("renders commander name after loading", async () => {
    renderPage();
    mockApiResolve({ data: mockCommanderData });

    await waitFor(() => {
      expect(screen.getByText("Atraxa, Praetors' Voice")).toBeInTheDocument();
    });
  });

  it("shows 'Commander not found' when fetch fails", async () => {
    renderPage();
    mockApiReject(new Error("Not found"));

    await waitFor(() => {
      expect(screen.getByText(/commander not found/i)).toBeInTheDocument();
    });
  });

  it("renders DeckStats component", async () => {
    renderPage();
    mockApiResolve({ data: mockCommanderData });

    await waitFor(() => {
      expect(screen.getByTestId("deck-stats")).toBeInTheDocument();
    });
  });

  it("renders ManaCurve component", async () => {
    renderPage();
    mockApiResolve({ data: mockCommanderData });

    await waitFor(() => {
      expect(screen.getByTestId("mana-curve")).toBeInTheDocument();
    });
  });

  it("renders DeckList component", async () => {
    renderPage();
    mockApiResolve({ data: mockCommanderData });

    await waitFor(() => {
      expect(screen.getByTestId("deck-list")).toBeInTheDocument();
    });
  });

  it("renders RecommendationsPanel component", async () => {
    renderPage();
    mockApiResolve({ data: mockCommanderData });

    await waitFor(() => {
      expect(screen.getByTestId("recommendations-panel")).toBeInTheDocument();
    });
  });

  it("sets commander in store when data loads", async () => {
    renderPage();
    mockApiResolve({ data: mockCommanderData });

    await waitFor(() => {
      const storeCommander = useDeckBuilder.getState().commander;
      expect(storeCommander).not.toBeNull();
      expect(storeCommander!.name).toBe("Atraxa, Praetors' Voice");
    });
  });

  it("wires addCard: clicking add in RecommendationsPanel adds card to store", async () => {
    renderPage();
    mockApiResolve({ data: mockCommanderData });

    await waitFor(() => {
      expect(screen.getByTestId("recommendations-panel")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId("mock-add"));

    await waitFor(() => {
      const storeDeck = useDeckBuilder.getState().deck;
      expect(storeDeck).toHaveLength(1);
      expect(storeDeck[0].name).toBe("Sol Ring");
    });
  });
});
