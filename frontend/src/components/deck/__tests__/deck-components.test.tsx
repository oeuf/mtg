import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import type { Card } from "../../../types";
import { DeckList } from "../DeckList";
import { CardRow } from "../CardRow";
import { DeckStats } from "../DeckStats";
import { ManaCurve } from "../ManaCurve";

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

const sampleCards: Card[] = [
  makeCard({ name: "Llanowar Elves", type_line: "Creature — Elf Druid", cmc: 1, mana_cost: "{G}" }),
  makeCard({ name: "Birds of Paradise", type_line: "Creature — Bird", cmc: 1, mana_cost: "{G}" }),
  makeCard({ name: "Tarmogoyf", type_line: "Creature — Lhurgoyf", cmc: 2, mana_cost: "{1}{G}" }),
  makeCard({ name: "Counterspell", type_line: "Instant", cmc: 2, mana_cost: "{U}{U}" }),
  makeCard({ name: "Brainstorm", type_line: "Instant", cmc: 1, mana_cost: "{U}" }),
  makeCard({ name: "Sol Ring", type_line: "Artifact", cmc: 1, mana_cost: "{1}" }),
  makeCard({ name: "Wrath of God", type_line: "Sorcery", cmc: 4, mana_cost: "{2}{W}{W}" }),
  makeCard({ name: "Sylvan Library", type_line: "Enchantment", cmc: 2, mana_cost: "{1}{G}" }),
  makeCard({ name: "Command Tower", type_line: "Land", cmc: 0, mana_cost: "" }),
];

describe("DeckList", () => {
  it("groups cards by type correctly", () => {
    const onRemoveCard = vi.fn();
    render(<DeckList cards={sampleCards} onRemoveCard={onRemoveCard} />);

    expect(screen.getByText(/Creatures/)).toBeInTheDocument();
    expect(screen.getByText(/Instants/)).toBeInTheDocument();
    expect(screen.getByText(/Artifacts/)).toBeInTheDocument();
    expect(screen.getByText(/Sorceries/)).toBeInTheDocument();
    expect(screen.getByText(/Enchantments/)).toBeInTheDocument();
    expect(screen.getByText(/Lands/)).toBeInTheDocument();
  });

  it("shows type headers with counts", () => {
    const onRemoveCard = vi.fn();
    render(<DeckList cards={sampleCards} onRemoveCard={onRemoveCard} />);

    expect(screen.getByText("Creatures (3)")).toBeInTheDocument();
    expect(screen.getByText("Instants (2)")).toBeInTheDocument();
    expect(screen.getByText("Artifacts (1)")).toBeInTheDocument();
  });

  it("sorts cards by CMC within groups", () => {
    const onRemoveCard = vi.fn();
    render(<DeckList cards={sampleCards} onRemoveCard={onRemoveCard} />);

    const cardNames = screen.getAllByTestId("card-row-name").map((el) => el.textContent);
    // Creatures: Llanowar Elves (1), Birds of Paradise (1), Tarmogoyf (2)
    const llanowarIdx = cardNames.indexOf("Llanowar Elves");
    const tarmogoyfIdx = cardNames.indexOf("Tarmogoyf");
    expect(llanowarIdx).toBeLessThan(tarmogoyfIdx);

    // Instants: Brainstorm (1), Counterspell (2)
    const brainstormIdx = cardNames.indexOf("Brainstorm");
    const counterspellIdx = cardNames.indexOf("Counterspell");
    expect(brainstormIdx).toBeLessThan(counterspellIdx);
  });
});

describe("CardRow", () => {
  it("renders card name and mana cost", () => {
    const onRemove = vi.fn();
    const card = makeCard({ name: "Lightning Bolt", mana_cost: "{R}" });
    render(<CardRow card={card} onRemove={onRemove} />);

    expect(screen.getByText("Lightning Bolt")).toBeInTheDocument();
    expect(screen.getByText("{R}")).toBeInTheDocument();
  });

  it("calls onRemove when × clicked", () => {
    const onRemove = vi.fn();
    const card = makeCard({ name: "Lightning Bolt" });
    render(<CardRow card={card} onRemove={onRemove} />);

    fireEvent.click(screen.getByText("×"));
    expect(onRemove).toHaveBeenCalledWith("Lightning Bolt");
  });
});

describe("DeckStats", () => {
  it("shows card count and avg CMC", () => {
    const cards = [
      makeCard({ cmc: 1 }),
      makeCard({ cmc: 3 }),
      makeCard({ cmc: 5 }),
    ];
    render(<DeckStats cards={cards} commander={null} />);

    expect(screen.getByText("Cards: 3/99")).toBeInTheDocument();
    expect(screen.getByText("Avg CMC: 3.0")).toBeInTheDocument();
  });

  it("shows 0.0 avg CMC for empty deck", () => {
    render(<DeckStats cards={[]} commander={null} />);

    expect(screen.getByText("Cards: 0/99")).toBeInTheDocument();
    expect(screen.getByText("Avg CMC: 0.0")).toBeInTheDocument();
  });
});

describe("ManaCurve", () => {
  it("renders correct number of bars (8 for 0-7+)", () => {
    const cards = [
      makeCard({ cmc: 0 }),
      makeCard({ cmc: 1 }),
      makeCard({ cmc: 2 }),
      makeCard({ cmc: 3 }),
      makeCard({ cmc: 4 }),
      makeCard({ cmc: 5 }),
      makeCard({ cmc: 6 }),
      makeCard({ cmc: 8 }),
    ];
    render(<ManaCurve cards={cards} />);

    const bars = screen.getAllByTestId("mana-curve-bar");
    expect(bars).toHaveLength(8);
  });

  it("groups 7+ CMC cards into one bucket", () => {
    const cards = [
      makeCard({ cmc: 7 }),
      makeCard({ cmc: 8 }),
      makeCard({ cmc: 10 }),
    ];
    render(<ManaCurve cards={cards} />);

    const bars = screen.getAllByTestId("mana-curve-bar");
    // Last bar (7+) should show count 3
    const lastBar = bars[7];
    expect(lastBar).toHaveTextContent("3");
  });

  it("shows CMC labels", () => {
    render(<ManaCurve cards={[]} />);

    const bars = screen.getAllByTestId("mana-curve-bar");
    // Each bar has a count span and a label span; verify labels
    expect(bars[0]).toHaveTextContent("0");
    expect(bars[1]).toHaveTextContent("1");
    expect(bars[7]).toHaveTextContent("7+");
  });
});
