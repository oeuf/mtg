# CLAUDE.md - AI Assistant Guide for MTG Commander Archetype Suite

## Repository Overview

This is a **Magic: The Gathering Commander (EDH) deck database and reference system**. It contains comprehensive documentation for four core Commander deck archetypes, each tuned at three different power levels ("salt tiers"). This is a **documentation and data repository**, not a software project.

### Purpose
- Provide structured, filterable deck lists for casual to high-power Commander play
- Enable players to match deck power to their playgroup
- Document archetype matchups, strategies, and card choices
- Serve as a "Commander lab" for testing different playstyles and power levels

### Target Audience
- Experienced Commander/EDH players who want structured deck options
- Players building multiple decks at different power levels
- Groups that want balanced, well-documented archetype matchups

---

## Repository Structure

### Core Files

#### `README.md` (459 lines)
**Purpose**: Comprehensive archetype guide and strategy documentation

**Contains**:
- Jargon and acronym primer (EDH terminology)
- Detailed descriptions of all 4 archetypes (GA4, CA, SU, RGX)
- Salt tier system (Extreme/Mid/Low) explained
- Complete matchup analysis (what beats what)
- Strategic guidance for each archetype
- Meta considerations and deck selection advice
- Future archetype ideas (TODO section)

**Key Sections**:
- Lines 1-110: Introduction, jargon, salt tiers, when to use which tier
- Lines 111-173: GA4 (Azorius Prison) - strategy, matchups, counters
- Lines 175-237: CA (Bant Hatebears/Blink) - strategy, matchups, counters
- Lines 240-296: SU (Sultai Graveyard) - strategy, matchups, counters
- Lines 299-354: RGX (Simic Lands/Big Mana) - strategy, matchups, counters
- Lines 356-417: Cross-archetype matchup matrix and other archetypes
- Lines 420-449: Future archetype ideas (TODOs)

#### `HOWTO.md` (476 lines)
**Purpose**: User manual for working with the Master Reference Table

**Contains**:
- Spreadsheet setup instructions (Google Sheets, Excel)
- How to filter and build 100-card decks from the table
- Techniques for comparing decks and finding overlaps
- Cost estimation methods
- Workflow for upgrading/downgrading between salt tiers
- Export procedures for deckbuilding sites (Moxfield, Archidekt)

**Critical for understanding**:
- How the `Decks` column tagging system works
- Filter formulas for finding cards shared between tiers
- The intended use-case: treating the table as a filterable menu, not static lists

#### `main-reference-table.md` (577 lines)
**Purpose**: Primary card database with full metadata

**Structure**: Markdown table with these columns:
- `Row`: Sequential index
- `Name`: Exact card name
- `Type`: Card type line (e.g., "Legendary Creature — Human Wizard")
- `Description`: Functional summary of what the card does
- `Casting Cost`: Mana cost (e.g., "2WU", "—" for lands)
- `Decks`: **Comma-separated deck tags** (e.g., "GA4-Ext,GA4-Mid,CA-Ext")
- `IsCommander`: "Y" or "N"
- `Price (USD)`: Approximate card cost
- `Printing`: Which Magic set/printing
- `Price Source`: Where price was retrieved
- `Price Date`: When price was checked

**Critical**: The `Decks` column uses this exact format:
- `{ARCHETYPE}-{TIER}` where:
  - ARCHETYPE: `GA4`, `CA`, `SU`, `RGX`
  - TIER: `Ext`, `Mid`, `Low`
- Multiple decks separated by commas (no spaces)
- Wildcards like `GA4-*` mean "all GA4 tiers"

#### `main-reference-table-deduped.md` (575 lines)
**Purpose**: Deduplicated version of the main reference table

**Difference**: Some rows show "(see row X)" to avoid duplicating card information when the same card appears in multiple contexts.

---

## The 4 Core Archetypes

### Naming Convention & Acronyms

All deck identifiers follow this pattern: `{ARCHETYPE}-{TIER}`

#### GA4 - Grand Arbiter Augustin IV (Azorius Prison)
- **Commander**: Grand Arbiter Augustin IV
- **Colors**: White-Blue (Azorius)
- **Strategy**: Prison/stax deck that taxes mana and spells, limits untap steps, pillowforts against combat
- **Experience**: "Everything is expensive and nothing untaps"
- **Role**: The "fun police" / archenemy deck
- **Tiers**: `GA4-Ext`, `GA4-Mid`, `GA4-Low`

#### CA - Control-Aggro (Bant Hatebears / Blink)
- **Commander**: Roon of the Hidden Realm
- **Colors**: Green-White-Blue (Bant)
- **Strategy**: Hatebears + ETB value creatures, blink effects for recursion
- **Experience**: "You can play, but your deck runs at 60-70% capacity"
- **Role**: Interactive disruption with creature-based answers
- **Tiers**: `CA-Ext`, `CA-Mid`, `CA-Low`

#### SU - Sultai Utility (Sultai Graveyard Value-Combo)
- **Commander**: Muldrotha, the Gravetide
- **Colors**: Black-Green-Blue (Sultai)
- **Strategy**: Graveyard engine that loops permanents and assembles compact combos
- **Experience**: "Kill my stuff, I'll just replay it. Also, I might win out of nowhere"
- **Role**: Resilient midrange with graveyard recursion and combo potential
- **Tiers**: `SU-Ext`, `SU-Mid`, `SU-Low`

#### RGX - Ramp-Growth-X-spells (Simic Lands / Big Mana)
- **Commander**: Aesi, Tyrant of Gyre Strait
- **Colors**: Green-Blue (Simic)
- **Strategy**: Land ramp, card draw, massive X-spells and token finishers
- **Experience**: "I'll play extra lands, draw extra cards, and eventually there are 30 power and a Craterhoof"
- **Role**: Big mana battlecruiser with explosive late-game
- **Tiers**: `RGX-Ext`, `RGX-Mid`, `RGX-Low`

---

## The Salt Tier System

Three power levels for each archetype, totaling **12 unique deck configurations**:

### Extreme (Ext)
- **Power Level**: High-power / pseudo-cEDH
- **Characteristics**: Maximal stax, fast mana (Mana Crypt, Moxen), efficient tutors, compact combos, Reserved List cards
- **Use Cases**: High-power tables, 1v1/Archenemy formats, groups that consent to maximum salt
- **Examples**: `GA4-Ext`, `CA-Ext`, `SU-Ext`, `RGX-Ext`

### Mid
- **Power Level**: Tuned but fair
- **Characteristics**: Core identity preserved, harshest locks trimmed, some fast mana removed
- **Use Cases**: Experienced EDH pods, 4-player games, tables that want real interaction without tournament feel
- **Examples**: `GA4-Mid`, `CA-Mid`, `SU-Mid`, `RGX-Mid`

### Low
- **Power Level**: Casual / battlecruiser
- **Characteristics**: Reduced prison, fewer "feel-bad" combos, more social/political cards
- **Use Cases**: Newer players, mixed power tables, large pods (5-6+ players)
- **Examples**: `GA4-Low`, `CA-Low`, `SU-Low`, `RGX-Low`

---

## Data Model & Conventions

### Deck Tagging System

Cards are tagged with one or more deck identifiers in the `Decks` column:

**Examples**:
- `GA4-Ext,GA4-Mid,GA4-Low` - Card appears in all GA4 tiers (core staple)
- `GA4-Ext,GA4-Mid` - Card only in higher-power GA4 builds
- `GA4-Ext` - Extreme-only card (usually most oppressive stax/fast mana)
- `CA-Ext,CA-Mid,CA-Low,SU-Ext,SU-Mid` - Shared between CA (all tiers) and SU (Ext/Mid only)

**Wildcards** (seen in some rows):
- `GA4-*` - Shorthand for "all GA4 tiers" (GA4-Ext, GA4-Mid, GA4-Low)
- Used to reduce repetition in the table

### Card Counts
- **Commander format**: 1 commander + 99 other cards = 100 total
- Each deck configuration should filter to exactly 100 cards
- The reference tables may contain a slightly oversized pool per tier to allow customization

### Filtering Logic (Critical)
To extract a specific deck from the reference table:
1. Filter `Decks` column for text containing the target deck code (e.g., "CA-Mid")
2. Filter `IsCommander = Y` to find the commander (should be exactly 1)
3. Count non-commander cards (should be 99)
4. If >99, use flex/meta slots or salt considerations to trim
5. If <99, add basic lands or additional staples

---

## Common Workflows

### 1. Adding a New Card to the Database

**Steps**:
1. Find the next available row number in `main-reference-table.md`
2. Add a new table row with all required columns:
   - `Row`: Sequential number
   - `Name`: Exact card name (check spelling on Scryfall)
   - `Type`: Full type line
   - `Description`: Brief functional summary
   - `Casting Cost`: Use standard notation (e.g., "2WU", "XG", "—" for lands)
   - `Decks`: Comma-separated deck codes (e.g., "SU-Ext,SU-Mid")
   - `IsCommander`: "Y" or "N"
   - `Price (USD)`: Current price
   - `Printing`: Set code/name
   - `Price Source`: Where you got the price
   - `Price Date`: YYYY-MM-DD format

**Important**:
- **Always use exact deck code spelling**: `GA4-Ext` (not `GA4-ext` or `ga4-ext`)
- No spaces after commas in the `Decks` field
- Keep descriptions concise and functional (not full Oracle text)

**After adding**:
- Verify the markdown table alignment is maintained
- Check that the new card doesn't duplicate an existing entry
- If updating `main-reference-table-deduped.md`, consider if deduplication is needed

### 2. Moving a Card Between Tiers

**Example**: Downgrade a card from Ext-only to Mid-only

1. Locate the card's row in `main-reference-table.md`
2. Edit the `Decks` column:
   - **Before**: `GA4-Ext`
   - **After**: `GA4-Mid`
3. Alternatively, add it to both: `GA4-Ext,GA4-Mid`

**Use Cases**:
- Rebalancing power levels after testing
- Responding to meta changes
- Making a card more/less accessible

### 3. Updating Card Prices

**Steps**:
1. Visit Scryfall or another price aggregator
2. Find the card and check current pricing
3. Update these columns:
   - `Price (USD)`: New price
   - `Price Date`: Current date (YYYY-MM-DD)
   - `Price Source`: If changed from Scryfall
   - `Printing`: If recommending a different printing

**Why This Matters**:
- Players use cost estimates to build within budget
- Helps identify cards that have spiked in price
- Salt tier separation often correlates with budget

### 4. Creating a New Archetype (Future Work)

Based on README lines 420-449, planned future archetypes include:
- Red-based Wheels / "Counter-Burn" (Grixis/Jeskai)
- Low-salt UW control (GA4-like but fairer)
- Mardu Aristocrats/Sacrifice
- Naya Tokens
- 5-Color Political/Group Hug
- Dedicated anti-graveyard control
- Mono-Red/Boros land destruction

**If adding a new archetype**:
1. Choose a concise acronym (e.g., "CB" for Counter-Burn)
2. Document it in README.md following the existing archetype format:
   - Commander
   - Colors
   - Strategy
   - Experience
   - Matchups (favored against / struggles against)
3. Add cards to `main-reference-table.md` with new deck tags (e.g., "CB-Ext", "CB-Mid", "CB-Low")
4. Update this CLAUDE.md file with the new archetype

### 5. Checking Deck Consistency

**Goal**: Ensure each deck configuration has exactly 100 cards and follows intended strategy

**Process**:
1. Filter for a specific deck (e.g., "RGX-Mid")
2. Count commanders (`IsCommander = Y`) - should be exactly 1
3. Count total cards - should be 100
4. Check type distribution:
   - Filter `Type` for "Land" - typically 35-38 lands
   - Filter `Type` for "Creature" - varies by archetype:
     - CA wants high creature count (30-40)
     - GA4 wants lower creature count (10-20)
     - SU and RGX are in between (20-30)
5. Verify curve by sorting `Casting Cost`
6. Cross-reference with README.md strategy sections

**Common Issues**:
- Too many/few cards: Adjust flex slots or meta-specific inclusions
- Mana curve issues: Check for too many high-CMC cards
- Missing key pieces: Verify commanders and signature cards are tagged correctly

---

## File Relationships & Dependencies

### Conceptual Flow
```
README.md (strategy guide)
    ↓
    Explains archetypes, salt tiers, matchups
    ↓
HOWTO.md (user manual)
    ↓
    Teaches how to use the reference table
    ↓
main-reference-table.md (card database)
    ↓
    Filterable source of truth for all decks
    ↓
main-reference-table-deduped.md (optimized version)
    ↓
    Same data, less repetition
```

### Update Propagation
When making changes:
1. **Card additions/changes**: Update `main-reference-table.md` first
2. **Deduplication**: Optionally update `main-reference-table-deduped.md` to match
3. **Strategy changes**: Update README.md if the change affects archetype philosophy
4. **Workflow changes**: Update HOWTO.md if adding new filtering techniques
5. **AI guidance**: Update this CLAUDE.md if adding new conventions

---

## Important Notes for AI Assistants

### This is NOT a Code Repository
- No compilation, testing, or CI/CD
- No package managers, dependencies, or build systems
- All files are human-readable Markdown documentation
- Changes are verified manually by reading the files, not by running tests

### Primary File Format: Markdown Tables
- Use proper markdown table syntax with pipes (`|`) and alignment
- Preserve column alignment when editing
- Be careful with multi-line cells (generally avoid them)
- Test that tables render correctly in Markdown viewers

### Consistency is Critical
- **Deck codes must be spelled exactly**: `GA4-Ext`, `CA-Mid`, `SU-Low`, `RGX-Ext`
- Case sensitivity matters: Always capitalize properly
- No spaces in comma-separated lists: `GA4-Ext,GA4-Mid` (not `GA4-Ext, GA4-Mid`)
- Date format: Always `YYYY-MM-DD`

### Magic: The Gathering Domain Knowledge
If you lack MTG knowledge:
- Card names are proper nouns and must be spelled exactly as printed
- Mana costs use this notation: W=White, U=Blue, B=Black, R=Red, G=Green, C=Colorless, numbers=generic
- Type lines follow specific formats (see Gatherer or Scryfall)
- When in doubt, verify card details on Scryfall: https://scryfall.com

### User Intent Interpretation

**If a user asks to**:
- "Add a card" → Update `main-reference-table.md` with a new row
- "Update prices" → Fetch from Scryfall and update price columns
- "Build a deck" → Filter the table for the specified deck code
- "Compare decks" → Show cards unique to each tier or shared between tiers
- "Downgrade/upgrade" → Change deck tags to move between tiers
- "What beats X?" → Reference README.md matchup sections

**If a user asks about strategy/matchups**:
- Always reference specific line numbers from README.md
- Cite the "Favored Against" and "Struggles Against" sections
- Consider both archetype matchups and salt tier differences

### Common Pitfalls to Avoid
1. **Don't invent new deck codes**: Only use established ones (GA4/CA/SU/RGX + Ext/Mid/Low)
2. **Don't break table formatting**: Test complex edits to ensure markdown tables remain valid
3. **Don't add cards without deck tags**: Every card must specify which decks use it
4. **Don't ignore salt tier philosophy**: Ext cards should be significantly stronger than Mid/Low
5. **Don't duplicate entries unnecessarily**: Check if a card is already in the table before adding

### Git Workflow
- This repo uses feature branches starting with `claude/`
- Commit messages should be clear and describe what changed (e.g., "Add 15 new cards to SU-Ext", "Update GA4 matchup analysis")
- Push to the designated feature branch (see git context in system prompt)
- Create descriptive PR summaries that explain the strategic impact of changes

---

## Quick Reference Card

### Deck Codes
- **GA4-Ext**: Extreme Azorius Prison
- **GA4-Mid**: Mid Azorius Prison
- **GA4-Low**: Low Azorius Prison
- **CA-Ext**: Extreme Bant Hatebears
- **CA-Mid**: Mid Bant Hatebears
- **CA-Low**: Low Bant Hatebears
- **SU-Ext**: Extreme Sultai Graveyard
- **SU-Mid**: Mid Sultai Graveyard
- **SU-Low**: Low Sultai Graveyard
- **RGX-Ext**: Extreme Simic Lands
- **RGX-Mid**: Mid Simic Lands
- **RGX-Low**: Low Simic Lands

### File Purposes
- **README.md**: Strategy, matchups, archetype philosophy
- **HOWTO.md**: How to use the reference table
- **main-reference-table.md**: Primary card database
- **main-reference-table-deduped.md**: Deduplicated card database

### Key Column Names
- `Row`, `Name`, `Type`, `Description`, `Casting Cost`, `Decks`, `IsCommander`, `Price (USD)`, `Printing`, `Price Source`, `Price Date`

### Filtering Examples
- Filter `Decks` contains "GA4-Mid" → All cards in GA4-Mid deck
- Filter `Decks` contains "GA4-" → All GA4 cards across all tiers
- Filter `IsCommander = Y` → All commanders
- Filter `Type` contains "Land" → All lands
- Filter `Type` contains "Creature" → All creatures

---

## Changelog

### 2025-12-21: Initial CLAUDE.md creation
- Comprehensive documentation of repository structure
- Archetype and salt tier system explained
- Common workflows documented
- File relationships mapped
- AI assistant guidance provided

---

## Questions to Ask Users (If Context is Unclear)

When working on this repository, you may need to ask:

1. **When adding cards**: "Which deck(s) and tier(s) should this card be added to?"
2. **When unsure about power level**: "Is this card intended for Ext, Mid, or Low power?"
3. **When multiple archetypes could use a card**: "Should this be a cross-archetype staple or specific to one deck?"
4. **When updating strategy**: "Does this change affect the matchup analysis in README.md?"
5. **When trimming oversized decks**: "Which cards are flex slots that can be cut?"

---

## Additional Resources

- **Scryfall** (card database): https://scryfall.com
- **EDHREC** (EDH statistics): https://edhrec.com
- **Moxfield** (deckbuilding): https://www.moxfield.com
- **Archidekt** (deckbuilding): https://archidekt.com

---

**Last Updated**: 2025-12-21
**Repository Maintainer**: See git commit history
**AI Assistant Version**: Claude Code (Sonnet 4.5)
