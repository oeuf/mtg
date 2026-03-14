<role>
You are an expert Magic: The Gathering Commander deckbuilder specializing in
competitive Bracket 3 builds. You have deep knowledge of graveyard-based
strategies, Sultai (BUG) color identity, and value engine construction.
You evaluate cards through the lens of: Muldrotha synergy, mana efficiency,
win-path contribution, and recursion value.
</role>

<context>
  <commander>
    Muldrotha, the Gravetide (3BUG — 6/6 Legendary Elemental Avatar)
    Ability: During each of your turns, you may play up to one permanent card
    of each permanent type from your graveyard.
    (Permanent types: artifact, creature, enchantment, land, planeswalker)
  </commander>

  <format>Commander / EDH — 100-card singleton (99 + Muldrotha)</format>

  <bracket_rules>
    Bracket 3: "Optimized" — Exactly 3 Game Changers allowed.
    Game Changers = cards that dramatically warp the game state or create
    near-unbeatable advantages (e.g., Expropriate, Cyclonic Rift, Demonic Tutor).
    Use the official Commander RC / community bracket definitions as reference.
  </bracket_rules>

  <power_target>
    Power level 7-8/10. "Maximum degeneracy within Bracket 3" means:
    - Prioritize repeatable graveyard recursion loops
    - Maximize permanent-type diversity for Muldrotha triggers
    - Include self-mill engines that fuel Muldrotha's ability
    - Lean into sacrifice/reanimate value chains
    - Include stax-lite pieces that asymmetrically punish opponents
      while Muldrotha rebuilds from graveyard
    - Ensure every card either enables Muldrotha's engine, protects it,
      or converts engine value into a win
  </power_target>

  <source_decks>
    Two existing deck lists in the attached file `muldrotha-reference.md`:
    - MUL-A (Deck A)
    - MUL-D (Deck D)
    These are the starting points for audit and synthesis.
  </source_decks>

  <collection_constraint>
    HARD CONSTRAINT: The final deck may ONLY include cards that appear in
    `MTG COLLECTION - Sheet5.tsv` (attached). This is my physical collection.
    If a card is not in this file, it cannot be in any deck list.
    Exception: Basic lands (Island, Swamp, Forest) are always available.
  </collection_constraint>

  <reference>
    Use https://edhrec.com/commanders/muldrotha-the-gravetide for:
    - Staple validation (confirm high-inclusion-% cards aren't missing)
    - Synergy scoring (EDHREC synergy % as a signal, not gospel)
    - Category comparison (are we aligned with typical slot allocations?)
  </reference>
</context>

<task>
Complete the following phases in order. Present all work in a single,
well-structured analysis document, then produce the comparison artifact.

## PHASE 1: Comparative Audit of MUL-A vs. MUL-D

For each card type category (Creatures, Enchantments, Artifacts, Instants,
Sorceries, Lands), produce a side-by-side comparison that identifies:

1. **Shared cards** — Cards in both decks (the consensus core)
2. **Unique to MUL-A** — Cards only in Deck A, with a 1-sentence evaluation
   of Muldrotha synergy (how well does this card leverage her ability?)
3. **Unique to MUL-D** — Same for Deck D
4. **Game Changers audit** — Identify which cards in each deck qualify as
   Game Changers per Bracket 3 definitions. Flag any deck that exceeds 3.

For each unique card, rate on these dimensions (1-5 scale):
- **Muldrotha Synergy**: Does it benefit from graveyard recursion?
  Can Muldrotha replay it? Does it self-mill or sacrifice for value?
- **Win-Path Contribution**: Does it advance a win condition or is it
  just "good stuff"?
- **Mana Efficiency**: CMC relative to impact; does it compete for the
  crucial 3-5 CMC slots Muldrotha needs?

## PHASE 2: Win Condition Critical Review

Analyze each deck's win conditions explicitly:
- **Primary win path(s)**: What is the intended way to close out a game?
- **Backup win path(s)**: If primary is disrupted, what's Plan B?
- **Muldrotha dependency**: How central is Muldrotha to each win path?
  (Good = she accelerates wins; Bad = deck can't win without her on board)
- **Assessment**: Are the win conditions clear, redundant enough, and
  achievable within Bracket 3 constraints?

Flag any deck that lacks a clear "this is how I actually kill the table" plan.

## PHASE 3: Synthesize the Final Deck ("MUL-FINAL")

Combine the best elements of MUL-A and MUL-D into a single optimized list:

1. Start with the consensus core (shared cards) — but these are NOT
   sacred. If my collection has a strictly better option for a shared
   slot, upgrade it.
2. For each contested slot, evaluate THREE candidates: the MUL-A card,
   the MUL-D card, AND the best available alternative from `MTG COLLECTION - Sheet5.tsv`.
   Pick the strongest option regardless of source.
3. Actively scan `MTG COLLECTION - Sheet5.tsv` for high-synergy cards that neither deck
   included — especially to shore up gaps identified in Phase 2
   (missing win conditions, weak mana base, insufficient self-mill, etc.)
4. Validate:
   - Exactly 99 cards + Muldrotha = 100
   - Singleton (no duplicates)
   - Exactly 3 Game Changers
   - All cards exist in `MTG COLLECTION - Sheet5.tsv` (or are basic lands)
   - Mana curve is playable (sufficient ramp, reasonable CMC distribution)
   - At least 2 clear win paths
   - Permanent-type diversity supports Muldrotha triggers each turn

**Deck Personality**: Give MUL-FINAL a coherent strategic identity.
Not just "goodstuff Sultai" — it should have a thesis statement like:
"This deck is a relentless graveyard engine that grinds opponents out
through recursive value, then closes with [specific combo/strategy]."
Name the personality (e.g., "The Dredge Tax Collector," "Grave Tide Rising").

## PHASE 4: Change Log

For every card that differs between MUL-A/MUL-D and MUL-FINAL:
- What was cut and from which deck
- What replaced it (if applicable)
- 1-2 sentence rationale tied to the evaluation dimensions above

</task>

<deliverable id="1" type="analysis_document">
  Present Phases 1-4 as a structured markdown document with clear headers,
  tables for the audit comparisons, and concise prose for the reviews.
  Use tables, not walls of text. Bold the key takeaways.
</deliverable>

<deliverable id="2" type="html_artifact">
  Create a single-page HTML comparison tool for MUL-A, MUL-D, and MUL-FINAL.

  <layout>
    3 columns (one per deck), with grouped rows by card type:
    Creatures | Enchantments | Artifacts | Instants | Sorceries | Lands
    Within each group, cards sorted alphabetically.
  </layout>

  <design_principles>
    Channel Jony Ive's restraint and Edward Tufte's information density:
    - High data-ink ratio: every pixel earns its place
    - Color-coding: highlight cards unique to each deck vs. shared across all 3
      (e.g., shared = neutral/muted, unique = subtle accent color per deck)
    - Game Changers visually distinguished (badge, icon, or border treatment)
    - Compact typography optimized for scanning, not reading
    - Sticky column headers so deck names stay visible while scrolling
    - Category group headers that visually separate card types
    - Card count per category shown in each column header
    - Total card count per deck shown at top (must = 99 for each)
    - Clean, dark or neutral palette — no visual clutter
    - Optional: hover or click to see card type/CMC if space allows
  </design_principles>

  <interaction>
    - Filter toggle: "Show only differences" (hides cards shared by all 3)
    - Category collapse/expand
    - Responsive: readable on both desktop and tablet
  </interaction>
</deliverable>

<validation_checklist>
  Before finalizing, verify:
  - [ ] Each deck totals exactly 99 cards (Muldrotha is the 100th)
  - [ ] No duplicate cards within any deck
  - [ ] MUL-FINAL has exactly 3 Game Changers
  - [ ] Every card in MUL-FINAL exists in `MTG COLLECTION - Sheet5.tsv`(or is a basic land)
  - [ ] MUL-FINAL has at least 2 explicit win conditions documented
  - [ ] Mana curve reviewed (ramp count, average CMC, land count)
  - [ ] Every permanent type is well-represented for Muldrotha triggers
  - [ ] HTML artifact renders all 3 decks with correct card counts
</validation_checklist>
