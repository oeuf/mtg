import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, it, expect, vi, beforeEach } from "vitest";
import CommanderSelectPage from "../CommanderSelectPage";

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

const mockSetSearchText = vi.fn();
const mockToggleColor = vi.fn();
const mockSetColorFilter = vi.fn();

const defaultHookReturn = {
  commanders: [],
  isLoading: false,
  error: null,
  searchText: "",
  setSearchText: mockSetSearchText,
  colorFilter: [] as string[],
  setColorFilter: mockSetColorFilter,
  toggleColor: mockToggleColor,
};

vi.mock("../useCommanderSearch", () => ({
  useCommanderSearch: vi.fn(() => defaultHookReturn),
}));

import { useCommanderSearch } from "../useCommanderSearch";
const mockUseCommanderSearch = vi.mocked(useCommanderSearch);

function renderPage() {
  return render(
    <MemoryRouter>
      <CommanderSelectPage />
    </MemoryRouter>,
  );
}

const mockCommanders = [
  {
    name: "Muldrotha, the Gravetide",
    mana_cost: "{3}{B}{G}{U}",
    cmc: 6,
    type_line: "Legendary Creature — Elemental Avatar",
    oracle_text: "Play permanents from graveyard",
    color_identity: ["B", "G", "U"],
    colors: ["B", "G", "U"],
    keywords: [],
    is_legendary: true as const,
    edhrec_rank: 5,
    functional_categories: [],
    mechanics: [],
    themes: [],
    archetype: null,
    popularity_score: 95,
    power: 6,
    toughness: 6,
  },
  {
    name: "Atraxa, Praetors' Voice",
    mana_cost: "{G}{W}{U}{B}",
    cmc: 4,
    type_line: "Legendary Creature — Phyrexian Angel Horror",
    oracle_text: "Proliferate at end step",
    color_identity: ["B", "G", "U", "W"],
    colors: ["B", "G", "U", "W"],
    keywords: ["flying", "vigilance", "deathtouch", "lifelink"],
    is_legendary: true as const,
    edhrec_rank: 1,
    functional_categories: [],
    mechanics: [],
    themes: [],
    archetype: null,
    popularity_score: 99,
    power: 4,
    toughness: 4,
  },
];

describe("CommanderSelectPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseCommanderSearch.mockReturnValue(defaultHookReturn);
  });

  it("renders the page title", () => {
    renderPage();
    expect(
      screen.getByRole("heading", { name: /select a commander/i }),
    ).toBeInTheDocument();
  });

  it("shows loading spinner when isLoading", () => {
    mockUseCommanderSearch.mockReturnValue({
      ...defaultHookReturn,
      isLoading: true,
    });
    renderPage();
    expect(screen.getByRole("status", { name: /loading/i })).toBeInTheDocument();
  });

  it("renders commander cards from mock data", () => {
    mockUseCommanderSearch.mockReturnValue({
      ...defaultHookReturn,
      commanders: mockCommanders,
    });
    renderPage();
    expect(screen.getByText("Muldrotha, the Gravetide")).toBeInTheDocument();
    expect(screen.getByText("Atraxa, Praetors' Voice")).toBeInTheDocument();
    expect(
      screen.getByText("Legendary Creature — Elemental Avatar"),
    ).toBeInTheDocument();
    expect(screen.getByText("{3}{B}{G}{U}")).toBeInTheDocument();
  });

  it('shows "No commanders found" when list is empty and not loading', () => {
    mockUseCommanderSearch.mockReturnValue({
      ...defaultHookReturn,
      commanders: [],
      isLoading: false,
    });
    renderPage();
    expect(screen.getByText(/no commanders found/i)).toBeInTheDocument();
  });

  it("search input calls setSearchText on change", () => {
    renderPage();
    const input = screen.getByLabelText(/search commanders/i);
    fireEvent.change(input, { target: { value: "Muldrotha" } });
    expect(mockSetSearchText).toHaveBeenCalledWith("Muldrotha");
  });

  it("renders color filter buttons for all 5 colors", () => {
    renderPage();
    expect(screen.getByRole("button", { name: /W/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /U/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /B/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /R/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /G/i })).toBeInTheDocument();
  });

  it("color filter button calls toggleColor on click", () => {
    renderPage();
    fireEvent.click(screen.getByRole("button", { name: /^W$/i }));
    expect(mockToggleColor).toHaveBeenCalledWith("W");
    fireEvent.click(screen.getByRole("button", { name: /^U$/i }));
    expect(mockToggleColor).toHaveBeenCalledWith("U");
  });

  it("active color filters have visual distinction", () => {
    mockUseCommanderSearch.mockReturnValue({
      ...defaultHookReturn,
      colorFilter: ["W", "B"],
    });
    renderPage();
    const wButton = screen.getByRole("button", { name: /^W$/i });
    const uButton = screen.getByRole("button", { name: /^U$/i });
    expect(wButton.className).toContain("ring");
    expect(uButton.className).not.toContain("ring");
  });

  it("clicking a commander navigates to deck builder", () => {
    mockUseCommanderSearch.mockReturnValue({
      ...defaultHookReturn,
      commanders: mockCommanders,
    });
    renderPage();
    fireEvent.click(screen.getByText("Muldrotha, the Gravetide"));
    expect(mockNavigate).toHaveBeenCalledWith(
      `/deck-builder/${encodeURIComponent("Muldrotha, the Gravetide")}`,
    );
  });
});
