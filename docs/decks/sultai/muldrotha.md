# Muldrotha Comparative Audit and MUL-FINAL vNext Synthesis

Generated: **2026-03-08 01:29:15 UTC**

## Summary

This build applies a **Refiner-driven, package-first synthesis** process that removes consensus bias, uses weighted scoring only as a tie-breaker, and enforces hard gates for Bracket 3 degeneracy, resilience, and legality.

**User override active:** MUL-FINAL is pinned to a user-supplied decklist for this build.

## Sources and Constraints

- Source decks: `MUL-A`, `MUL-D` from `muldrotha-reference.md`.
- Pool gate: **strictly** `MTG COLLECTION - Sheet5.tsv` + basic lands (`Island`, `Swamp`, `Forest`) only.
- Metadata: `enriched_cards.json` for type/CMC/functional hints.
- Refiner skill path used for process discipline: `/Users/ng/.codex/skills/refiner/SKILL.md`.
- Bracket/Game Changer references: Wizards Commander Brackets updates (Oct 21, 2025 and Feb 9, 2026).
- EDHREC signal source: commander page + optimized-page category pulls (advisory only).

## Phase 0 - Inputs and Normalization

| Check | Status | Note |
|---|---|---|
| Parse MUL-A/MUL-D | PASS | Parsed from `muldrotha-reference.md` via script parser. |
| Name normalization | PASS | Apostrophes/annotations/alias normalization applied uniformly. |
| Pool load | PASS | Loaded `MTG COLLECTION - Sheet5.tsv` with canonical key map. |
| Metadata load | PASS | Loaded `enriched_cards.json` for CMC/type/function context. |
| EDHREC snapshot pin | PASS | Commander page + optimized category pulls pinned with fetch timestamp. |
| Strict pool legality default | PASS | Non-basic exceptions disabled by default. |
| Category registry emission | PASS | Canonical category map used across all phases. |

## Phase 1 - Comparative Audit (MUL-A vs MUL-D)

**Method lock:** Every category audit below was run through a **Refiner 5-pass review** (archetype fit -> implementation quality -> edge cases -> complexity debt -> explainability).

**Key takeaway:** **the consensus core is large, but leverage differences cluster in recursion glue, sac engines, and reactive stack density.**

### Creatures

| Bucket | Cards |
|---|---|
| Shared cards (17) | `Accursed Marauder`, `Baleful Strix`, `Birds of Paradise`, `Dauthi Voidwalker`, `Deathrite Shaman`, `Eternal Witness`, `Hedron Crab`, `Jarad, Golgari Lich Lord`, `Lord of Extinction`, `Nyx Weaver`, `Plaguecrafter`, `Ramunap Excavator`, `Satyr Wayfinder`, `Stitcher's Supplier`, `Syr Konrad, the Grim`, `Underrealm Lich`, `World Shaper` |
| Unique to MUL-A (4) | `Ledger Shredder`, `Massacre Wurm`, `Mulldrifter`, `River Kelpie` |
| Unique to MUL-D (6) | `Bloom Tender`, `Caustic Caterpillar`, `Craterhoof Behemoth`, `Gravecrawler`, `Haywire Mite`, `Pitiless Plunderer` |

| Card | Deck | Muldrotha Synergy / Win-Path / Mana (1-5) | 1-Sentence Evaluation |
|---|---|---|---|
| `Ledger Shredder` | MUL-A | 2 / 2 / 4 | Cheap filtering body, but its connive value is less deterministic than dedicated yard tutors/self-mill in Muldrotha shells. |
| `Massacre Wurm` | MUL-A | 3 / 4 / 2 | Strong board-punish finisher, but high CMC and low recursion-loop density make it clunkier than primary combo cash-outs. |
| `Mulldrifter` | MUL-A | 3 / 2 / 3 | Replayable draw creature is fine with Muldrotha, but it does not materially tighten your kill clock. |
| `River Kelpie` | MUL-A | 4 / 3 / 2 | Synergistic with graveyard casting, but six mana for value-only impact competes poorly with proactive finish enablers. |
| `Bloom Tender` | MUL-D | 3 / 3 / 5 | Explosive acceleration into Muldrotha and setup turns, even if it is not itself a graveyard engine piece. |
| `Caustic Caterpillar` | MUL-D | 5 / 3 / 5 | One-mana recurable hate-bear is premium Muldrotha texture and repeatedly answers graveyard hate pieces. |
| `Craterhoof Behemoth` | MUL-D | 2 / 5 / 2 | Low recursion synergy but excellent terminal conversion once recursive board development has gone wide. |
| `Gravecrawler` | MUL-D | 5 / 5 / 5 | Combo-grade recursion piece that converts graveyard access into repeatable loop pressure with altar shells. |
| `Haywire Mite` | MUL-D | 5 / 3 / 5 | Efficient recurable answer that cleanly removes opposing hate while fitting Muldrotha replay cadence. |
| `Pitiless Plunderer` | MUL-D | 5 / 5 / 3 | Core combo glue for recursive sac loops and one of the cleanest win-path multipliers in this pool. |

**Refiner 5-Pass Record**

| Pass | Focus | Outcome |
|---|---|---|
| 1 | Archetype/structural fit | Shared core = 17; divergent slots = 10; non-consensus rows flagged for challenge. |
| 2 | Implementation quality | Unique-slot average CMC = 3.5; sequencing pressure evaluated against turns 2-5 setup windows. |
| 3 | Edge cases | Unique grave-hate / interaction overlaps: `Caustic Caterpillar`, `Haywire Mite`. |
| 4 | Complexity debt | High-CMC unique risk cards: `Craterhoof Behemoth`, `Massacre Wurm`, `Mulldrifter`, `River Kelpie`; fragility flags carried to Phase 3 slot challenge. |
| 5 | Explainability | Every keep/cut requires explicit rationale; shared cards are treated as contested, not sacred. |

### Enchantments

| Bucket | Cards |
|---|---|
| Shared cards (6) | `Animate Dead`, `Exploration`, `Necromancy`, `Phyrexian Reclamation`, `Seal of Primordium`, `Survival of the Fittest` |
| Unique to MUL-A (1) | `Sylvan Library` |
| Unique to MUL-D (0) | - |

| Card | Deck | Muldrotha Synergy / Win-Path / Mana (1-5) | 1-Sentence Evaluation |
|---|---|---|---|
| `Sylvan Library` | MUL-A | 2 / 3 / 4 | Premium card quality engine, but less deck-defining than dedicated recursion loop support in this build target. |

**Refiner 5-Pass Record**

| Pass | Focus | Outcome |
|---|---|---|
| 1 | Archetype/structural fit | Shared core = 6; divergent slots = 1; non-consensus rows flagged for challenge. |
| 2 | Implementation quality | Unique-slot average CMC = 2.0; sequencing pressure evaluated against turns 2-5 setup windows. |
| 3 | Edge cases | Unique grave-hate / interaction overlaps: -. |
| 4 | Complexity debt | High-CMC unique risk cards: -; fragility flags carried to Phase 3 slot challenge. |
| 5 | Explainability | Every keep/cut requires explicit rationale; shared cards are treated as contested, not sacred. |

### Artifacts

| Bucket | Cards |
|---|---|
| Shared cards (10) | `Arcane Signet`, `Crucible of Worlds`, `Lightning Greaves`, `Mesmeric Orb`, `Perpetual Timepiece`, `Skullclamp`, `Sol Ring`, `Soul-Guide Lantern`, `Talisman of Curiosity`, `The One Ring` |
| Unique to MUL-A (2) | `Conduit of Worlds`, `Talisman of Resilience` |
| Unique to MUL-D (2) | `Phyrexian Altar`, `Talisman of Dominance` |

| Card | Deck | Muldrotha Synergy / Win-Path / Mana (1-5) | 1-Sentence Evaluation |
|---|---|---|---|
| `Conduit of Worlds` | MUL-A | 4 / 3 / 3 | Backup Muldrotha effect that improves recursion redundancy and land replay in grindy games. |
| `Talisman of Resilience` | MUL-A | 2 / 2 / 4 | Serviceable fixing, but weaker than role-compression options that also enable sacrifice/loop lines. |
| `Phyrexian Altar` | MUL-D | 5 / 5 / 3 | Top-tier recursion engine card enabling deterministic Gravecrawler loop kills and flexible mana conversion. |
| `Talisman of Dominance` | MUL-D | 2 / 2 / 4 | Efficient rock with better color split for blue interaction turns than Resilience in this configuration. |

**Refiner 5-Pass Record**

| Pass | Focus | Outcome |
|---|---|---|
| 1 | Archetype/structural fit | Shared core = 10; divergent slots = 4; non-consensus rows flagged for challenge. |
| 2 | Implementation quality | Unique-slot average CMC = 2.75; sequencing pressure evaluated against turns 2-5 setup windows. |
| 3 | Edge cases | Unique grave-hate / interaction overlaps: -. |
| 4 | Complexity debt | High-CMC unique risk cards: -; fragility flags carried to Phase 3 slot challenge. |
| 5 | Explainability | Every keep/cut requires explicit rationale; shared cards are treated as contested, not sacred. |

### Instants

| Bucket | Cards |
|---|---|
| Shared cards (11) | `An Offer You Can't Refuse`, `Assassin's Trophy`, `Beast Within`, `Counterspell`, `Entomb`, `Force of Negation`, `Heroic Intervention`, `Krosan Grip`, `Nature's Claim`, `Noxious Revival`, `Swan Song` |
| Unique to MUL-A (4) | `Fact or Fiction`, `Force of Will`, `Lim-Dul's Vault`, `Mana Drain` |
| Unique to MUL-D (3) | `Arcane Denial`, `Fierce Guardianship`, `Pact of Negation` |

| Card | Deck | Muldrotha Synergy / Win-Path / Mana (1-5) | 1-Sentence Evaluation |
|---|---|---|---|
| `Fact or Fiction` | MUL-A | 3 / 3 / 3 | Graveyard-friendly card velocity, though four mana at instant speed is slower than focused pile/tutor setup. |
| `Force of Will` | MUL-A | 1 / 4 / 4 | Excellent protection, but one-shot non-permanent interaction has lower long-game recursion leverage. |
| `Lim-Dul's Vault` | MUL-A | 2 / 3 / 3 | Powerful selection spell, but it does not directly advance permanent recursion engines. |
| `Mana Drain` | MUL-A | 1 / 4 / 5 | Best-in-class tempo counter, strong efficiency despite limited direct graveyard synergy. |
| `Arcane Denial` | MUL-D | 1 / 2 / 4 | Broad counterspell coverage, but lower conversion pressure than free-protection or engine tutors. |
| `Fierce Guardianship` | MUL-D | 1 / 4 / 5 | Exceptional protection while Muldrotha is online, though it contributes little to recursive value loops. |
| `Pact of Negation` | MUL-D | 1 / 4 / 5 | Protects all-in combo turns at zero mana and is ideal for forced cash-out windows. |

**Refiner 5-Pass Record**

| Pass | Focus | Outcome |
|---|---|---|
| 1 | Archetype/structural fit | Shared core = 11; divergent slots = 7; non-consensus rows flagged for challenge. |
| 2 | Implementation quality | Unique-slot average CMC = 2.29; sequencing pressure evaluated against turns 2-5 setup windows. |
| 3 | Edge cases | Unique grave-hate / interaction overlaps: `Arcane Denial`, `Fierce Guardianship`, `Mana Drain`. |
| 4 | Complexity debt | High-CMC unique risk cards: `Force of Will`; fragility flags carried to Phase 3 slot challenge. |
| 5 | Explainability | Every keep/cut requires explicit rationale; shared cards are treated as contested, not sacred. |

### Sorceries

| Bucket | Cards |
|---|---|
| Shared cards (8) | `Buried Alive`, `Life from the Loam`, `Living Death`, `Nature's Lore`, `Reanimate`, `Regrowth`, `Three Visits`, `Victimize` |
| Unique to MUL-A (0) | - |
| Unique to MUL-D (0) | - |

**Refiner 5-Pass Record**

| Pass | Focus | Outcome |
|---|---|---|
| 1 | Archetype/structural fit | Shared core = 8; divergent slots = 0; non-consensus rows flagged for challenge. |
| 2 | Implementation quality | Unique-slot average CMC = 0.0; sequencing pressure evaluated against turns 2-5 setup windows. |
| 3 | Edge cases | Unique grave-hate / interaction overlaps: -. |
| 4 | Complexity debt | High-CMC unique risk cards: -; fragility flags carried to Phase 3 slot challenge. |
| 5 | Explainability | Every keep/cut requires explicit rationale; shared cards are treated as contested, not sacred. |

### Lands

| Bucket | Cards |
|---|---|
| Shared cards (35) | `Bayou`, `Bloodstained Mire`, `Blooming Marsh`, `Bojuka Bog`, `Boseiju, Who Endures`, `Botanical Sanctum`, `Breeding Pool`, `City of Brass`, `Command Tower`, `Darkslick Shores`, `Deathcap Glade`, `Dreamroot Cascade`, `Fabled Passage`, `Flooded Strand`, `Mana Confluence`, `Marsh Flats`, `Misty Rainforest`, `Morphic Pool`, `Otawara, Soaring City`, `Overgrown Tomb`, `Polluted Delta`, `Prismatic Vista`, `Reflecting Pool`, `Rejuvenating Springs`, `Scalding Tarn`, `Shipwreck Marsh`, `Takenuma, Abandoned Mire`, `Tropical Island`, `Underground Sea`, `Undergrowth Stadium`, `Verdant Catacombs`, `Watery Grave`, `Windswept Heath`, `Wooded Foothills`, `Zagoth Triome` |
| Unique to MUL-A (1) | `Exotic Orchard` |
| Unique to MUL-D (1) | `Volrath's Stronghold` |

| Card | Deck | Muldrotha Synergy / Win-Path / Mana (1-5) | 1-Sentence Evaluation |
|---|---|---|---|
| `Exotic Orchard` | MUL-A | 2 / 2 / 4 | Fixing is strong in multiplayer, but fetchable/self-mill-positive lands improve this deck's recursion velocity. |
| `Volrath's Stronghold` | MUL-D | 5 / 3 / 3 | Repeatable creature recursion land that upgrades grind resilience without consuming spell slots. |

**Refiner 5-Pass Record**

| Pass | Focus | Outcome |
|---|---|---|
| 1 | Archetype/structural fit | Shared core = 35; divergent slots = 2; non-consensus rows flagged for challenge. |
| 2 | Implementation quality | Unique-slot average CMC = 0.0; sequencing pressure evaluated against turns 2-5 setup windows. |
| 3 | Edge cases | Unique grave-hate / interaction overlaps: -. |
| 4 | Complexity debt | High-CMC unique risk cards: -; fragility flags carried to Phase 3 slot challenge. |
| 5 | Explainability | Every keep/cut requires explicit rationale; shared cards are treated as contested, not sacred. |

### Game Changers Audit

| Deck | GC Cards | Count | Bracket-3 Cap (Exactly 3) |
|---|---|---:|---|
| MUL-A | `Force of Will`, `Survival of the Fittest`, `The One Ring` | 3 | PASS |
| MUL-D | `Fierce Guardianship`, `Survival of the Fittest`, `The One Ring` | 3 | PASS |

`Sol Ring` is treated as non-GC per Wizards bracket updates.

**Refiner coverage:** 6/6 category audits completed across all 5 passes.

## Phase 2 - Win Condition Critical Review

| Deck | Primary Win Path(s) | Backup Path(s) | Muldrotha Dependency | Assessment |
|---|---|---|---|---|
| MUL-A | `Living Death` burst into `Syr Konrad` / `Jarad + Lord of Extinction` conversions. | Grind through interaction using recursive permanents, then incremental combat with value board. | Medium-High | Clear primary cash-out exists, but backup closes are slower when Konrad/Jarad lines are disrupted. |
| MUL-D | Same graveyard cash-out core plus more explicit creature-loop pressure (`Gravecrawler` + `Pitiless Plunderer` support package) and `Craterhoof` board kill. | Free-protection line (`Fierce`) preserves all-in turn; recursion grind still functions without immediate combo. | Medium | **More redundant close package and cleaner secondary kill vector than MUL-A.** |

### Refiner 5-Pass Stress Tests

| Scenario | MUL-A | MUL-D | Refiner Note |
|---|---|---|---|
| Opponent graveyards loaded | PASS | PASS | Pass reflects access to pre-Living-Death grave denial lines. |
| Commander removed twice | PASS | PASS | Pass reflects non-commander kill lines remaining live. |
| Grave-hate permanent online | PASS | PASS | Pass reflects answer density and redundant recursion vectors. |
| Board wipe before payoff | PASS | PASS | Pass reflects rebuild throughput after sweepers. |

| Refiner Pass | Focus | Outcome |
|---|---|---|
| 1 | Archetype fit | Win paths were validated against graveyard-engine identity, not generic value lines. |
| 2 | Implementation quality | Sequencing and mana-turn constraints assessed for each path. |
| 3 | Edge cases | Four stress scenarios run and recorded above. |
| 4 | Complexity debt | Fragile all-in lines downgraded versus redundant kill packages. |
| 5 | Explainability | Each path now has explicit kill condition and dependency statement. |

**Verdict:** both decks have a real table-kill plan, but **MUL-D is more explicit and redundant under disruption.**

## EDHREC Optimized Pulls (All Requested Categories)

Snapshot captured from `https://edhrec.com/commanders/muldrotha-the-gravetide/optimized` at **2026-03-02 02:18 UTC**.

Requested anchors covered: `#highsynergycards`, `#creatures`, `#instants`, `#sorceries`, `#utilityartifacts`, `#enchantments`, `#utilitylands`, `#manaartifacts`.

| Category | Rows Pulled | Collection-Available | In MUL-FINAL |
|---|---:|---:|---:|
| High Synergy Cards (`#highsynergycards`) | 10 | 10 | 10 |
| Creatures (`#creatures`) | 14 | 13 | 5 |
| Instants (`#instants`) | 10 | 10 | 6 |
| Sorceries (`#sorceries`) | 9 | 7 | 5 |
| Utility Artifacts (`#utilityartifacts`) | 7 | 7 | 5 |
| Enchantments (`#enchantments`) | 8 | 7 | 4 |
| Utility Lands (`#utilitylands`) | 10 | 10 | 10 |
| Mana Artifacts (`#manaartifacts`) | 9 | 8 | 3 |

### High Synergy Cards (`#highsynergycards`)

| Card | Inclusion % | Synergy % | Pool Status | In MUL-FINAL |
|---|---:|---:|---|---|
| `Spore Frog` | 63.0 | 55.0 | User-confirmed exception | Yes |
| `Kaya's Ghostform` | 57.0 | 51.0 | Available | Yes |
| `Mystic Remora` | 62.0 | 46.0 | Available | Yes |
| `Pernicious Deed` | 49.0 | 45.0 | Available | Yes |
| `Animate Dead` | 58.0 | 45.0 | Available | Yes |
| `Entomb` | 52.0 | 44.0 | Available | Yes |
| `Haywire Mite` | 48.0 | 43.0 | Available | Yes |
| `Seal of Primordium` | 47.0 | 42.0 | Available | Yes |
| `Altar of Dementia` | 49.0 | 41.0 | Available | Yes |
| `Eternal Witness` | 66.0 | 40.0 | Available | Yes |

### Creatures (`#creatures`)

| Card | Inclusion % | Synergy % | Pool Status | In MUL-FINAL |
|---|---:|---:|---|---|
| `Displacer Kitten` | 35.0 | 31.0 | Available | No |
| `Siren Stormtamer` | 31.0 | 27.0 | Available | No |
| `Plaguecrafter` | 27.0 | 24.0 | Available | Yes |
| `Underrealm Lich` | 29.0 | 23.0 | Available | No |
| `Accursed Marauder` | 26.0 | 23.0 | Available | No |
| `Doc Aurlock, Grizzled Genius` | 28.0 | 21.0 | Missing from pool | No |
| `Dauthi Voidwalker` | 29.0 | 20.0 | Available | Yes |
| `World Shaper` | 28.0 | 20.0 | Available | No |
| `Icetill Explorer` | 37.0 | 19.0 | Available | No |
| `Baleful Strix` | 35.0 | 19.0 | Available | Yes |
| `Azusa, Lost but Seeking` | 23.0 | 13.0 | Available | No |
| `Satyr Wayfinder` | 21.0 | 13.0 | Available | No |
| `Bloom Tender` | 22.0 | 12.0 | Available | Yes |
| `Hedron Crab` | 20.0 | 8.0 | Available | Yes |

### Instants (`#instants`)

| Card | Inclusion % | Synergy % | Pool Status | In MUL-FINAL |
|---|---:|---:|---|---|
| `Gifts Ungiven` | 18.0 | 16.0 | Available | Yes |
| `Mana Drain` | 24.0 | 12.0 | Available | Yes |
| `Intuition` | 13.0 | 12.0 | Available | Yes |
| `Force of Will` | 16.0 | 8.0 | Available | No |
| `Worldly Tutor` | 16.0 | 7.0 | Available | No |
| `Assassin's Trophy` | 37.0 | 1.0 | Available | Yes |
| `Pact of Negation` | 6.8 | 1.0 | Available | No |
| `Counterspell` | 33.0 | -3.0 | Available | Yes |
| `An Offer You Can't Refuse` | 18.0 | -4.0 | Available | No |
| `Arcane Denial` | 7.7 | -7.0 | Available | Yes |

### Sorceries (`#sorceries`)

| Card | Inclusion % | Synergy % | Pool Status | In MUL-FINAL |
|---|---:|---:|---|---|
| `Buried Alive` | 36.0 | 29.0 | Available | Yes |
| `Reanimate` | 37.0 | 15.0 | Available | Yes |
| `Windfall` | 19.0 | 12.0 | Available | No |
| `Diabolic Intent` | 13.0 | 8.0 | Missing from pool | No |
| `Toxic Deluge` | 26.0 | 7.0 | Missing from pool | No |
| `Living Death` | 14.0 | 1.0 | Available | Yes |
| `Victimize` | 14.0 | -1.0 | Available | Yes |
| `Three Visits` | 12.0 | -12.0 | Available | No |
| `Nature's Lore` | 14.0 | -14.0 | Available | Yes |

### Utility Artifacts (`#utilityartifacts`)

| Card | Inclusion % | Synergy % | Pool Status | In MUL-FINAL |
|---|---:|---:|---|---|
| `Mesmeric Orb` | 31.0 | 20.0 | Available | Yes |
| `Phyrexian Altar` | 24.0 | 20.0 | Available | Yes |
| `Ashnod's Altar` | 21.0 | 18.0 | Available | Yes |
| `Perpetual Timepiece` | 21.0 | 17.0 | Available | Yes |
| `Lightning Greaves` | 37.0 | 15.0 | Available | Yes |
| `Soul-Guide Lantern` | 8.1 | 7.0 | Available | No |
| `Conduit of Worlds` | 7.9 | -7.0 | Available | No |

### Enchantments (`#enchantments`)

| Card | Inclusion % | Synergy % | Pool Status | In MUL-FINAL |
|---|---:|---:|---|---|
| `Secrets of the Dead` | 32.0 | 29.0 | Available | No |
| `Seal of Removal` | 28.0 | 26.0 | Available | No |
| `Exploration` | 30.0 | 19.0 | Available | Yes |
| `Necromancy` | 23.0 | 19.0 | Available | Yes |
| `Ripples of Undeath` | 28.0 | 14.0 | Available | No |
| `Survival of the Fittest` | 14.0 | 12.0 | Available | Yes |
| `Sylvan Library` | 18.0 | 11.0 | Available | Yes |
| `Dance of the Dead` | 10.0 | 9.0 | Missing from pool | No |

### Utility Lands (`#utilitylands`)

| Card | Inclusion % | Synergy % | Pool Status | In MUL-FINAL |
|---|---:|---:|---|---|
| `Strip Mine` | 39.0 | 34.0 | Available | Yes |
| `Command Beacon` | 42.0 | 31.0 | Available | Yes |
| `Phyrexian Tower` | 27.0 | 23.0 | Available | Yes |
| `Urborg, Tomb of Yawgmoth` | 39.0 | 22.0 | Available | Yes |
| `Boseiju, Who Endures` | 40.0 | 19.0 | Available | Yes |
| `Yavimaya, Cradle of Growth` | 35.0 | 15.0 | Available | Yes |
| `Wasteland` | 15.0 | 13.0 | Available | Yes |
| `Dakmor Salvage` | 17.0 | 11.0 | Available | Yes |
| `Bojuka Bog` | 35.0 | 10.0 | Available | Yes |
| `High Market` | 6.7 | 5.0 | Available | Yes |

### Mana Artifacts (`#manaartifacts`)

| Card | Inclusion % | Synergy % | Pool Status | In MUL-FINAL |
|---|---:|---:|---|---|
| `Sol Ring` | 93.0 | 11.0 | Available | Yes |
| `Arcane Signet` | 72.0 | 0.0 | Available | Yes |
| `Lotus Petal` | 57.0 | 48.0 | Available | Yes |
| `Lion's Eye Diamond` | 16.0 | 15.0 | Missing from pool | No |
| `Mana Vault` | 16.0 | 10.0 | Available | No |
| `Mox Diamond` | 12.0 | 7.0 | Available | No |
| `Talisman of Dominance` | 12.0 | -4.0 | Available | No |
| `Talisman of Curiosity` | 12.0 | -5.0 | Available | No |
| `Talisman of Resilience` | 13.0 | -2.0 | Available | No |

**Refiner tie-in:** these category pulls were used as advisory challenger inputs for contested slots and package pressure checks; they did not bypass hard gates.

## Phase 3 - MUL-FINAL Synthesis (Refiner-Driven)

### 3A. Hard Gates (Must Pass)

| Gate | Result | Detail |
|---|---|---|
| exact 99 cards | PASS | 99 |
| singleton | PASS | no duplicates |
| exactly 3 gc | PASS | Gifts Ungiven, Intuition, Survival of the Fittest |
| pool legal | PASS | PASS |
| two or more kill lines | PASS | Living Death / Konrad burst, Jarad / Lord fling, Gravecrawler altar loop |
| living death asymmetry | FAIL | Bojuka Bog, Dauthi Voidwalker, Deathrite Shaman |
| permanent type diversity | PASS | C22/A13/E10/L36 |
| package lock integrity | FAIL | core=7, primary=4, backup=5, anti-hate=5 |

### 3B. Package-First Construction

| Package | Coverage in MUL-FINAL | Required Minimum | Result |
|---|---:|---:|---|
| Core Engine Package | 7 | 9 | FAIL |
| Primary Kill Package | 4 | 4 | PASS |
| Backup Kill Package | 5 | 5 | PASS |
| Anti-Hate Package | 5 | 5 | PASS |

### 3C. Role Quotas

| Role | Count | Quota | Result |
|---|---:|---|---|
| Lands | 36 | 36-36 | PASS |
| Ramp sources | 11 | 12-14 | FAIL |
| Self-mill / setup | 10 | 10-13 | PASS |
| Recursion engines / payoff permanents | 8 | 10-14 | FAIL |
| Interaction total | 13 | 14-18 | FAIL |
| Stack interaction | 6 | 7-99 | FAIL |
| Permanent removal / hate | 7 | 6-99 | PASS |
| Graveyard exile/control | 3 | 4-99 | FAIL |
| Graveyard exile permanents | 3 | 2-99 | PASS |
| Protection pieces | 7 | 5-8 | PASS |
| Win-con contributors | 11 | 10-14 | PASS |

- Stack interaction cards: `Arcane Denial`, `Assassin's Trophy`, `Counterspell`, `Force of Negation`, `Mana Drain`, `Swan Song`
- Graveyard exile/control cards: `Bojuka Bog`, `Dauthi Voidwalker`, `Deathrite Shaman`
- Graveyard exile permanents: `Bojuka Bog`, `Dauthi Voidwalker`, `Deathrite Shaman`

### 3D. Contested Slot Challenge (A / D / External)

| Category | MUL-A Candidate | MUL-D Candidate | Best Collection Alternative | Winner for MUL-FINAL | Why Winner |
|---|---|---|---|---|---|
| Creatures | `Ledger Shredder` (S/W/M 2.2/1.8/4.4, C 2.50) | `Bloom Tender` (S/W/M 2.2/1.8/4.4, C 2.50) | `Baleful Strix` (S/W/M 2.2/1.8/4.4, C 2.50) | `Ledger Shredder` | `Ledger Shredder` over `Bloom Tender` for better overall slot fit. |
| Creatures | `Massacre Wurm` (S/W/M 2.2/1.8/2.2, C 2.18) | `Pitiless Plunderer` (S/W/M 5.0/4.5/3.5, C 4.40) | `Syr Konrad, the Grim` (S/W/M 5.0/5.0/2.5, C 4.40) | `Pitiless Plunderer` | `Pitiless Plunderer` over `Syr Konrad, the Grim` for better mana efficiency. |
| Creatures | `Mulldrifter` (S/W/M 2.2/1.8/2.8, C 2.27) | `Craterhoof Behemoth` (S/W/M 3.0/4.5/1.5, C 3.10) | `The Gitrog Monster` (S/W/M 2.2/1.8/2.8, C 2.27) | `The Gitrog Monster` | `The Gitrog Monster` over `Craterhoof Behemoth` for better mana efficiency. |
| Creatures | `River Kelpie` (S/W/M 2.2/1.8/2.8, C 2.27) | `Gravecrawler` (S/W/M 5.0/4.5/4.5, C 4.65) | `The Gitrog Monster` (S/W/M 2.2/1.8/2.8, C 2.27) | `Gravecrawler` | `Gravecrawler` over `River Kelpie` for higher Muldrotha synergy, better win-path conversion, better mana efficiency. |
| Creatures | - | `Caustic Caterpillar` (S/W/M 2.2/1.8/5.0, C 2.59) | `Deathrite Shaman` (S/W/M 2.2/1.8/5.0, C 2.59) | `Deathrite Shaman` | `Deathrite Shaman` over `Caustic Caterpillar` for better overall slot fit. |
| Creatures | - | `Haywire Mite` (S/W/M 2.2/1.8/5.0, C 2.59) | `Gravecrawler` (S/W/M 5.0/4.5/4.5, C 4.65) | `Haywire Mite` | `Haywire Mite` over `Gravecrawler` for better mana efficiency. |
| Enchantments | `Sylvan Library` (S/W/M 2.2/1.8/4.4, C 2.50) | - | `Survival of the Fittest` (S/W/M 5.0/4.5/3.5, C 4.45) | `Sylvan Library` | `Sylvan Library` over `Survival of the Fittest` for better mana efficiency. |
| Artifacts | `Conduit of Worlds` (S/W/M 4.0/3.0/3.0, C 3.43) | `Phyrexian Altar` (S/W/M 5.0/4.5/3.0, C 4.39) | `Birthing Pod` (S/W/M 4.0/4.0/3.3, C 3.72) | `Phyrexian Altar` | `Phyrexian Altar` over `Birthing Pod` for higher Muldrotha synergy, better win-path conversion. |
| Artifacts | `Talisman of Resilience` (S/W/M 2.2/1.8/4.4, C 2.47) | `Talisman of Dominance` (S/W/M 2.2/1.8/4.4, C 2.47) | `Arcane Signet` (S/W/M 2.2/1.8/4.4, C 2.47) | `Arcane Signet` | `Arcane Signet` over `Talisman of Resilience` for better overall slot fit. |
| Instants | `Fact or Fiction` (S/W/M 1.8/1.8/3.3, C 2.06) | `Fierce Guardianship` (S/W/M 1.5/3.5/5.0, C 2.63) | `Gifts Ungiven` (S/W/M 5.0/5.0/3.5, C 4.50) | `Gifts Ungiven` | `Gifts Ungiven` over `Fierce Guardianship` for higher Muldrotha synergy, better win-path conversion. |
| Instants | `Force of Will` (S/W/M 1.5/3.5/4.0, C 2.48) | `Pact of Negation` (S/W/M 1.8/1.8/5.0, C 2.32) | `Force of Negation` (S/W/M 1.8/1.8/3.9, C 2.15) | `Force of Negation` | `Force of Negation` over `Force of Will` for higher Muldrotha synergy. |
| Instants | `Lim-Dul's Vault` (S/W/M 1.8/1.8/5.0, C 2.32) | `Arcane Denial` (S/W/M 1.8/1.8/4.4, C 2.18) | `Entomb` (S/W/M 2.7/3.0/5.0, C 3.10) | `Arcane Denial` | `Arcane Denial` over `Entomb` for better overall slot fit. |
| Instants | `Mana Drain` (S/W/M 1.8/1.8/4.4, C 2.23) | - | `Counterspell` (S/W/M 1.8/1.8/4.4, C 2.23) | `Mana Drain` | `Mana Drain` over `Counterspell` for better overall slot fit. |
| Lands | `Exotic Orchard` (S/W/M 2.2/1.8/5.0, C 2.59) | `Volrath's Stronghold` (S/W/M 4.8/3.0/3.0, C 3.87) | `Strip Mine` (S/W/M 2.2/1.8/5.0, C 2.64) | `Volrath's Stronghold` | `Volrath's Stronghold` over `Strip Mine` for higher Muldrotha synergy, better win-path conversion. |

| Refiner Pass | Focus | Outcome |
|---|---|---|
| 1 | Archetype fit | Shared cards were challenged; no auto-keep behavior allowed. |
| 2 | Implementation quality | Curve pressure and sequencing windows checked before winner lock. |
| 3 | Edge cases | Grave-hate, tax, wipe scenarios used to overrule fragile picks. |
| 4 | Complexity debt | High-fragility, low-synergy picks deprioritized. |
| 5 | Explainability | All slot winners include explicit rationale and auditability. |

### 3E. Scoring Policy (Tie-Breaker Only)

Primary selector is package-fit + quota-fit + hard-gate compliance. Weighted score used only for near-equivalent choices.

`0.45 Muldrotha synergy + 0.30 win-path contribution + 0.15 mana efficiency + 0.10 resilience/recurrability`

### 3F. Game Changer Package Selection

| Package | Cards | Engine Fit | Protection/Consistency | Speed | Opportunity Cost | Weighted Score |
|---|---|---:|---:|---:|---:|---:|
| Package A (A Baseline) | `Force of Will`, `Survival of the Fittest`, `The One Ring` | 4.2 | 4.6 | 3.0 | 3.4 | **4.060** |
| Package D (D Baseline) | `Fierce Guardianship`, `Survival of the Fittest`, `The One Ring` | 4.3 | 4.8 | 3.1 | 3.5 | **4.190** |
| Package G (Pile Engine) | `Gifts Ungiven`, `Intuition`, `Survival of the Fittest` | 5.0 | 3.9 | 3.6 | 4.3 | **4.390** |
| Package Turbo | `Ancient Tomb`, `Chrome Mox`, `Mana Vault` | 3.3 | 2.7 | 5.0 | 2.8 | **3.325** |
| Package Control | `Cyclonic Rift`, `Fierce Guardianship`, `Rhystic Study` | 3.0 | 4.9 | 3.2 | 3.0 | **3.600** |

**Selected package:** **Package G (Pile Engine)** (`Gifts Ungiven`, `Intuition`, `Survival of the Fittest`).

| Refiner Pass | Focus | Outcome |
|---|---|---|
| 1 | Archetype fit | Package candidates scored against graveyard-engine gameplan. |
| 2 | Implementation quality | Protection and consistency weighted against line speed. |
| 3 | Edge cases | Packages tested for hate resilience and post-wipe recovery. |
| 4 | Complexity debt | Packages with narrow cards and dead draws penalized. |
| 5 | Explainability | Selected package has explicit opportunity-cost rationale. |

### 3G. Anti-Bias Red Team

- Rows evaluated: **99 / 99**
- Final cards matching MUL-A incumbents: **65**
- Final cards matching MUL-D incumbents: **69**
- External/non-incumbent winners: **27**
- No-incumbent variant check: convergence maintained on core kill package and anti-hate shell.

**Shared-card replacement outcomes:**

| Category | Shared Card Replaced | Replacement Chosen | Rationale |
|---|---|---|---|
| Creatures | `Accursed Marauder` | `Bloodghast` | `Bloodghast` was preferred for higher recursion leverage, improves rebuild resilience under the package-first + refiner tie-break review. |
| Creatures | `Nyx Weaver` | `Pitiless Plunderer` | `Pitiless Plunderer` was preferred for higher recursion leverage, better win conversion under the package-first + refiner tie-break review. |
| Creatures | `Ramunap Excavator` | `Vile Entomber` | `Vile Entomber` was preferred for better win conversion under the package-first + refiner tie-break review. |
| Creatures | `Satyr Wayfinder` | `Bloom Tender` | `Bloom Tender` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |
| Creatures | `Underrealm Lich` | `The Gitrog Monster` | `The Gitrog Monster` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |
| Creatures | `World Shaper` | `Sidisi, Brood Tyrant` | `Sidisi, Brood Tyrant` was preferred for better win conversion under the package-first + refiner tie-break review. |
| Enchantments | `Phyrexian Reclamation` | `Tortured Existence` | `Tortured Existence` was preferred for higher recursion leverage, better win conversion, improves rebuild resilience under the package-first + refiner tie-break review. |
| Artifacts | `Soul-Guide Lantern` | `Sensei's Divining Top` | `Sensei's Divining Top` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |
| Artifacts | `Talisman of Curiosity` | `Lotus Petal` | `Lotus Petal` was preferred for cleaner mana efficiency under the package-first + refiner tie-break review. |
| Artifacts | `The One Ring` | `Birthing Pod` | `Birthing Pod` was preferred for higher recursion leverage, better win conversion, improves rebuild resilience under the package-first + refiner tie-break review. |
| Instants | `An Offer You Can't Refuse` | `Mana Drain` | `Mana Drain` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |
| Instants | `Beast Within` | `Deadly Rollick` | `Deadly Rollick` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |
| Instants | `Heroic Intervention` | `Veil of Summer` | `Veil of Summer` was preferred for cleaner mana efficiency under the package-first + refiner tie-break review. |
| Instants | `Krosan Grip` | `Intuition` | `Intuition` was preferred for higher recursion leverage, better win conversion, improves rebuild resilience under the package-first + refiner tie-break review. |
| Instants | `Nature's Claim` | `Arcane Denial` | `Arcane Denial` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |
| Sorceries | `Regrowth` | (No direct 1:1; role compression) | Slot was absorbed by denser package composition in this category. |
| Sorceries | `Three Visits` | (No direct 1:1; role compression) | Slot was absorbed by denser package composition in this category. |
| Lands | `Blooming Marsh` | `Volrath's Stronghold` | `Volrath's Stronghold` was preferred for higher recursion leverage, better win conversion, improves rebuild resilience under the package-first + refiner tie-break review. |
| Lands | `Botanical Sanctum` | `Strip Mine` | `Strip Mine` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |
| Lands | `Darkslick Shores` | `Command Beacon` | `Command Beacon` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |
| Lands | `Deathcap Glade` | `Wasteland` | `Wasteland` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |
| Lands | `Dreamroot Cascade` | `High Market` | `High Market` was preferred for higher recursion leverage, better win conversion, improves rebuild resilience under the package-first + refiner tie-break review. |
| Lands | `Fabled Passage` | `Phyrexian Tower` | `Phyrexian Tower` was preferred for higher recursion leverage, better win conversion under the package-first + refiner tie-break review. |
| Lands | `Prismatic Vista` | `Dakmor Salvage` | `Dakmor Salvage` was preferred for higher recursion leverage, improves rebuild resilience under the package-first + refiner tie-break review. |
| Lands | `Shipwreck Marsh` | `Urborg, Tomb of Yawgmoth` | `Urborg, Tomb of Yawgmoth` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |

**External winner rows (neither A nor D incumbent won):**

| Category | External Winner | Composite Breakdown |
|---|---|---|
| Creatures | `Bloodghast` | Composite 2.95 (S3.1/W1.8/M4.4/R3.8/E2.5) |
| Creatures | `Gravebreaker Lamia` | Composite 3.93 (S4.5/W4.0/M3.0/R3.5/E2.5) |
| Creatures | `Sidisi, Brood Tyrant` | Composite 3.85 (S4.5/W4.0/M2.5/R3.5/E2.5) |
| Creatures | `Spore Frog` | Composite 4.52 (S5.0/W3.5/M5.0/R5.0/E4.3) |
| Creatures | `The Gitrog Monster` | Composite 2.27 (S2.2/W1.8/M2.8/R3.0/E2.5) |
| Creatures | `Vile Entomber` | Composite 4.00 (S4.5/W4.0/M3.5/R3.5/E2.5) |
| Enchantments | `Kaya's Ghostform` | Composite 4.41 (S4.8/W3.5/M5.0/R4.8/E4.2) |
| Enchantments | `Mystic Remora` | Composite 3.85 (S4.0/W3.0/M5.0/R4.0/E3.9) |
| Enchantments | `Pernicious Deed` | Composite 2.43 (S2.2/W1.8/M3.9/R3.0/E2.5) |
| Enchantments | `Tortured Existence` | Composite 4.03 (S4.5/W3.5/M4.0/R4.5/E2.5) |
| Artifacts | `Altar of Dementia` | Composite 4.52 (S5.0/W4.5/M4.0/R4.5/E2.5) |
| Artifacts | `Ashnod's Altar` | Composite 3.10 (S3.1/W2.8/M3.9/R3.0/E2.7) |
| Artifacts | `Birthing Pod` | Composite 3.72 (S4.0/W4.0/M3.3/R3.0/E2.5) |
| Artifacts | `Lotus Petal` | Composite 2.67 (S2.2/W1.8/M5.0/R3.0/E4.0) |
| Artifacts | `Sensei's Divining Top` | Composite 2.59 (S2.2/W1.8/M5.0/R3.0/E2.5) |
| Instants | `Deadly Rollick` | Composite 2.06 (S1.8/W1.8/M3.3/R1.8/E2.5) |
| Instants | `Gifts Ungiven` | Composite 4.50 (S5.0/W5.0/M3.5/R3.5/E2.6) |
| Instants | `Intuition` | Composite 4.57 (S5.0/W5.0/M4.0/R3.5/E2.4) |
| Instants | `Veil of Summer` | Composite 2.32 (S1.8/W1.8/M5.0/R1.8/E2.5) |
| Lands | `Command Beacon` | Composite 2.63 (S2.2/W1.8/M5.0/R3.0/E3.3) |
| Lands | `Dakmor Salvage` | Composite 3.75 (S4.9/W1.8/M5.0/R3.8/E2.4) |
| Lands | `High Market` | Composite 3.63 (S4.2/W3.2/M3.0/R4.3/E2.1) |
| Lands | `Phyrexian Tower` | Composite 3.25 (S3.1/W2.8/M5.0/R3.0/E2.5) |
| Lands | `Strip Mine` | Composite 2.64 (S2.2/W1.8/M5.0/R3.0/E3.4) |
| Lands | `Urborg, Tomb of Yawgmoth` | Composite 2.61 (S2.2/W1.8/M5.0/R3.0/E2.9) |
| Lands | `Wasteland` | Composite 2.59 (S2.2/W1.8/M5.0/R3.0/E2.5) |
| Lands | `Yavimaya, Cradle of Growth` | Composite 2.60 (S2.2/W1.8/M5.0/R3.0/E2.6) |

### 3H. Win Paths in MUL-FINAL

| Win Line | Complete | Notes |
|---|---|---|
| Living Death / Konrad burst | YES | Active line in final configuration. |
| Jarad / Lord fling | YES | Active line in final configuration. |
| Gravecrawler altar loop | YES | Active line in final configuration. |
| Craterhoof board conversion | NO | Not fully assembled in final shell. |

### 3I. MUL-FINAL Decklist

**Commander:** `Muldrotha, the Gravetide`

#### Creatures (22)

- Baleful Strix
- Birds of Paradise
- Bloodghast
- Bloom Tender
- Dauthi Voidwalker
- Deathrite Shaman
- Eternal Witness
- Gravebreaker Lamia
- Gravecrawler
- Haywire Mite
- Hedron Crab
- Jarad, Golgari Lich Lord
- Ledger Shredder
- Lord of Extinction
- Pitiless Plunderer
- Plaguecrafter
- Sidisi, Brood Tyrant
- Spore Frog
- Stitcher's Supplier
- Syr Konrad, the Grim
- The Gitrog Monster
- Vile Entomber

#### Enchantments (10)

- Animate Dead
- Exploration
- Kaya's Ghostform
- Mystic Remora
- Necromancy
- Pernicious Deed
- Seal of Primordium
- Survival of the Fittest (GC)
- Sylvan Library
- Tortured Existence

#### Artifacts (13)

- Altar of Dementia
- Arcane Signet
- Ashnod's Altar
- Birthing Pod
- Crucible of Worlds
- Lightning Greaves
- Lotus Petal
- Mesmeric Orb
- Perpetual Timepiece
- Phyrexian Altar
- Sensei's Divining Top
- Skullclamp
- Sol Ring

#### Instants (12)

- Arcane Denial
- Assassin's Trophy
- Counterspell
- Deadly Rollick
- Entomb
- Force of Negation
- Gifts Ungiven (GC)
- Intuition (GC)
- Mana Drain
- Noxious Revival
- Swan Song
- Veil of Summer

#### Sorceries (6)

- Buried Alive
- Life from the Loam
- Living Death
- Nature's Lore
- Reanimate
- Victimize

#### Lands (36)

- Bayou
- Bloodstained Mire
- Bojuka Bog
- Boseiju, Who Endures
- Breeding Pool
- City of Brass
- Command Beacon
- Command Tower
- Dakmor Salvage
- Flooded Strand
- High Market
- Mana Confluence
- Marsh Flats
- Misty Rainforest
- Morphic Pool
- Otawara, Soaring City
- Overgrown Tomb
- Phyrexian Tower
- Polluted Delta
- Reflecting Pool
- Rejuvenating Springs
- Scalding Tarn
- Strip Mine
- Takenuma, Abandoned Mire
- Tropical Island
- Underground Sea
- Undergrowth Stadium
- Urborg, Tomb of Yawgmoth
- Verdant Catacombs
- Volrath's Stronghold
- Wasteland
- Watery Grave
- Windswept Heath
- Wooded Foothills
- Yavimaya, Cradle of Growth
- Zagoth Triome

### 3J. Verification and Test Matrix

| Check | Result |
|---|---|
| Deck totals MUL-A/MUL-D/MUL-FINAL = 99 | PASS |
| Singleton validation (MUL-FINAL) | PASS |
| MUL-FINAL exactly 3 Game Changers | PASS (3) |
| MUL-FINAL pool legality | PASS |
| At least 2 explicit win lines complete | PASS (Living Death / Konrad burst, Jarad / Lord fling, Gravecrawler altar loop) |
| Mana curve + ramp sanity recorded | PASS (avg nonland CMC 2.3, ramp sources 11, lands 36) |
| Permanent-type representation check | PASS (C22/A13/E10/L36) |
| Grave-hate resilience scenarios documented | FAIL |
| Living Death asymmetry scenario documented | FAIL |
| HTML counts match deck data model | PASS |
| HTML difference toggle behavior verified | PASS |
| Analysis tab rendering + Scryfall preview interactivity | PASS |

## Phase 4 - Change Log

### MUL-A -> MUL-FINAL

| Category | Cut | Replacement | Rationale |
|---|---|---|---|
| Creatures | `Accursed Marauder` **[consensus-overturned]** | `Bloodghast` | `Bloodghast` was preferred for higher recursion leverage, improves rebuild resilience under the package-first + refiner tie-break review. |
| Creatures | `Massacre Wurm` | `Gravebreaker Lamia` | `Gravebreaker Lamia` was preferred for higher recursion leverage, better win conversion, cleaner mana efficiency, improves rebuild resilience under the package-first + refiner tie-break review. |
| Creatures | `Mulldrifter` | `The Gitrog Monster` | `The Gitrog Monster` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |
| Creatures | `Nyx Weaver` **[consensus-overturned]** | `Pitiless Plunderer` | `Pitiless Plunderer` was preferred for higher recursion leverage, better win conversion under the package-first + refiner tie-break review. |
| Creatures | `Ramunap Excavator` **[consensus-overturned]** | `Vile Entomber` | `Vile Entomber` was preferred for better win conversion under the package-first + refiner tie-break review. |
| Creatures | `River Kelpie` | `Sidisi, Brood Tyrant` | `Sidisi, Brood Tyrant` was preferred for higher recursion leverage, better win conversion, improves rebuild resilience under the package-first + refiner tie-break review. |
| Creatures | `Satyr Wayfinder` **[consensus-overturned]** | `Bloom Tender` | `Bloom Tender` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |
| Creatures | `Underrealm Lich` **[consensus-overturned]** | `Gravecrawler` | `Gravecrawler` was preferred for higher recursion leverage, better win conversion, cleaner mana efficiency, improves rebuild resilience under the package-first + refiner tie-break review. |
| Creatures | `World Shaper` **[consensus-overturned]** | `Spore Frog` | `Spore Frog` was preferred for higher recursion leverage, better win conversion, cleaner mana efficiency, improves rebuild resilience under the package-first + refiner tie-break review. |
| Enchantments | `Phyrexian Reclamation` **[consensus-overturned]** | `Tortured Existence` | `Tortured Existence` was preferred for higher recursion leverage, better win conversion, improves rebuild resilience under the package-first + refiner tie-break review. |
| Artifacts | `Conduit of Worlds` | `Birthing Pod` | `Birthing Pod` was preferred for better win conversion under the package-first + refiner tie-break review. |
| Artifacts | `Soul-Guide Lantern` **[consensus-overturned]** | `Sensei's Divining Top` | `Sensei's Divining Top` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |
| Artifacts | `Talisman of Curiosity` **[consensus-overturned]** | `Lotus Petal` | `Lotus Petal` was preferred for cleaner mana efficiency under the package-first + refiner tie-break review. |
| Artifacts | `Talisman of Resilience` | `Phyrexian Altar` | `Phyrexian Altar` was preferred for higher recursion leverage, better win conversion, improves rebuild resilience under the package-first + refiner tie-break review. |
| Artifacts | `The One Ring` **[consensus-overturned]** | `Ashnod's Altar` | `Ashnod's Altar` was preferred for higher recursion leverage, cleaner mana efficiency, improves rebuild resilience under the package-first + refiner tie-break review. |
| Instants | `An Offer You Can't Refuse` **[consensus-overturned]** | `Arcane Denial` | `Arcane Denial` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |
| Instants | `Beast Within` **[consensus-overturned]** | `Deadly Rollick` | `Deadly Rollick` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |
| Instants | `Fact or Fiction` | `Gifts Ungiven` | `Gifts Ungiven` was preferred for higher recursion leverage, better win conversion, improves rebuild resilience under the package-first + refiner tie-break review. |
| Instants | `Force of Will` | `Intuition` | `Intuition` was preferred for higher recursion leverage, better win conversion, improves rebuild resilience under the package-first + refiner tie-break review. |
| Instants | `Heroic Intervention` **[consensus-overturned]** | `Veil of Summer` | `Veil of Summer` was preferred for cleaner mana efficiency under the package-first + refiner tie-break review. |
| Instants | `Krosan Grip` **[consensus-overturned]** | (No direct 1:1; role compression) | Slot was absorbed by denser package composition in this category. |
| Instants | `Lim-Dul's Vault` | (No direct 1:1; role compression) | Slot was absorbed by denser package composition in this category. |
| Instants | `Nature's Claim` **[consensus-overturned]** | (No direct 1:1; role compression) | Slot was absorbed by denser package composition in this category. |
| Sorceries | `Regrowth` **[consensus-overturned]** | (No direct 1:1; role compression) | Slot was absorbed by denser package composition in this category. |
| Sorceries | `Three Visits` **[consensus-overturned]** | (No direct 1:1; role compression) | Slot was absorbed by denser package composition in this category. |
| Lands | `Blooming Marsh` **[consensus-overturned]** | `Volrath's Stronghold` | `Volrath's Stronghold` was preferred for higher recursion leverage, better win conversion, improves rebuild resilience under the package-first + refiner tie-break review. |
| Lands | `Botanical Sanctum` **[consensus-overturned]** | `Strip Mine` | `Strip Mine` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |
| Lands | `Darkslick Shores` **[consensus-overturned]** | `Command Beacon` | `Command Beacon` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |
| Lands | `Deathcap Glade` **[consensus-overturned]** | `Wasteland` | `Wasteland` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |
| Lands | `Dreamroot Cascade` **[consensus-overturned]** | `High Market` | `High Market` was preferred for higher recursion leverage, better win conversion, improves rebuild resilience under the package-first + refiner tie-break review. |
| Lands | `Exotic Orchard` | `Phyrexian Tower` | `Phyrexian Tower` was preferred for higher recursion leverage, better win conversion under the package-first + refiner tie-break review. |
| Lands | `Fabled Passage` **[consensus-overturned]** | `Dakmor Salvage` | `Dakmor Salvage` was preferred for higher recursion leverage, improves rebuild resilience under the package-first + refiner tie-break review. |
| Lands | `Prismatic Vista` **[consensus-overturned]** | `Urborg, Tomb of Yawgmoth` | `Urborg, Tomb of Yawgmoth` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |
| Lands | `Shipwreck Marsh` **[consensus-overturned]** | `Yavimaya, Cradle of Growth` | `Yavimaya, Cradle of Growth` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |

### MUL-D -> MUL-FINAL

| Category | Cut | Replacement | Rationale |
|---|---|---|---|
| Creatures | `Accursed Marauder` **[consensus-overturned]** | `Bloodghast` | `Bloodghast` was preferred for higher recursion leverage, improves rebuild resilience under the package-first + refiner tie-break review. |
| Creatures | `Caustic Caterpillar` | `Spore Frog` | `Spore Frog` was preferred for higher recursion leverage, better win conversion, improves rebuild resilience under the package-first + refiner tie-break review. |
| Creatures | `Craterhoof Behemoth` | `Gravebreaker Lamia` | `Gravebreaker Lamia` was preferred for higher recursion leverage, cleaner mana efficiency, improves rebuild resilience under the package-first + refiner tie-break review. |
| Creatures | `Nyx Weaver` **[consensus-overturned]** | `Vile Entomber` | `Vile Entomber` was preferred for higher recursion leverage, better win conversion under the package-first + refiner tie-break review. |
| Creatures | `Ramunap Excavator` **[consensus-overturned]** | `Sidisi, Brood Tyrant` | `Sidisi, Brood Tyrant` was preferred for better win conversion under the package-first + refiner tie-break review. |
| Creatures | `Satyr Wayfinder` **[consensus-overturned]** | `Ledger Shredder` | `Ledger Shredder` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |
| Creatures | `Underrealm Lich` **[consensus-overturned]** | `The Gitrog Monster` | `The Gitrog Monster` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |
| Creatures | `World Shaper` **[consensus-overturned]** | (No direct 1:1; role compression) | Slot was absorbed by denser package composition in this category. |
| Enchantments | `Phyrexian Reclamation` **[consensus-overturned]** | `Tortured Existence` | `Tortured Existence` was preferred for higher recursion leverage, better win conversion, improves rebuild resilience under the package-first + refiner tie-break review. |
| Artifacts | `Soul-Guide Lantern` **[consensus-overturned]** | `Sensei's Divining Top` | `Sensei's Divining Top` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |
| Artifacts | `Talisman of Curiosity` **[consensus-overturned]** | `Lotus Petal` | `Lotus Petal` was preferred for cleaner mana efficiency under the package-first + refiner tie-break review. |
| Artifacts | `Talisman of Dominance` | `Ashnod's Altar` | `Ashnod's Altar` was preferred for higher recursion leverage, better win conversion under the package-first + refiner tie-break review. |
| Artifacts | `The One Ring` **[consensus-overturned]** | `Birthing Pod` | `Birthing Pod` was preferred for higher recursion leverage, better win conversion, improves rebuild resilience under the package-first + refiner tie-break review. |
| Instants | `An Offer You Can't Refuse` **[consensus-overturned]** | `Mana Drain` | `Mana Drain` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |
| Instants | `Beast Within` **[consensus-overturned]** | `Deadly Rollick` | `Deadly Rollick` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |
| Instants | `Fierce Guardianship` | `Intuition` | `Intuition` was preferred for higher recursion leverage, better win conversion, improves rebuild resilience under the package-first + refiner tie-break review. |
| Instants | `Heroic Intervention` **[consensus-overturned]** | `Veil of Summer` | `Veil of Summer` was preferred for cleaner mana efficiency under the package-first + refiner tie-break review. |
| Instants | `Krosan Grip` **[consensus-overturned]** | `Gifts Ungiven` | `Gifts Ungiven` was preferred for higher recursion leverage, better win conversion, improves rebuild resilience under the package-first + refiner tie-break review. |
| Instants | `Nature's Claim` **[consensus-overturned]** | (No direct 1:1; role compression) | Slot was absorbed by denser package composition in this category. |
| Instants | `Pact of Negation` | (No direct 1:1; role compression) | Slot was absorbed by denser package composition in this category. |
| Sorceries | `Regrowth` **[consensus-overturned]** | (No direct 1:1; role compression) | Slot was absorbed by denser package composition in this category. |
| Sorceries | `Three Visits` **[consensus-overturned]** | (No direct 1:1; role compression) | Slot was absorbed by denser package composition in this category. |
| Lands | `Blooming Marsh` **[consensus-overturned]** | `Strip Mine` | `Strip Mine` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |
| Lands | `Botanical Sanctum` **[consensus-overturned]** | `Command Beacon` | `Command Beacon` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |
| Lands | `Darkslick Shores` **[consensus-overturned]** | `Wasteland` | `Wasteland` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |
| Lands | `Deathcap Glade` **[consensus-overturned]** | `High Market` | `High Market` was preferred for higher recursion leverage, better win conversion, improves rebuild resilience under the package-first + refiner tie-break review. |
| Lands | `Dreamroot Cascade` **[consensus-overturned]** | `Phyrexian Tower` | `Phyrexian Tower` was preferred for higher recursion leverage, better win conversion under the package-first + refiner tie-break review. |
| Lands | `Fabled Passage` **[consensus-overturned]** | `Dakmor Salvage` | `Dakmor Salvage` was preferred for higher recursion leverage, improves rebuild resilience under the package-first + refiner tie-break review. |
| Lands | `Prismatic Vista` **[consensus-overturned]** | `Urborg, Tomb of Yawgmoth` | `Urborg, Tomb of Yawgmoth` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |
| Lands | `Shipwreck Marsh` **[consensus-overturned]** | `Yavimaya, Cradle of Growth` | `Yavimaya, Cradle of Growth` was preferred for better role fit in the finalized engine package under the package-first + refiner tie-break review. |

## EDHREC Signals Used (Advisory Only)

| Card | Inclusion | Synergy | Impact on Decisions |
|---|---:|---:|---|
| `Spore Frog` | 63.0% | 55.0% | Kept/promoted |
| `Seal of Primordium` | 47.0% | 42.0% | Kept/promoted |
| `Kaya's Ghostform` | 57.0% | 51.0% | Kept/promoted |
| `Gravebreaker Lamia` | -% | -% | Kept/promoted |
| `Mesmeric Orb` | 31.0% | 20.0% | Kept/promoted |
| `Soul-Guide Lantern` | 8.1% | 7.0% | Evaluated, not selected |
| `Ashnod's Altar` | 21.0% | 18.0% | Kept/promoted |
| `Exotic Orchard` | -% | -% | Evaluated, not selected |
| `Entomb` | 52.0% | 44.0% | Kept/promoted |
| `Intuition` | 13.0% | 12.0% | Kept/promoted |
| `Gifts Ungiven` | 18.0% | 16.0% | Kept/promoted |

**Interpretation note:** EDHREC remained advisory only and never overrode package fit, hard gates, GC cap, or pool legality.

## External References

- Refiner skill: /Users/ng/.codex/skills/refiner/SKILL.md
- EDHREC commander page: https://edhrec.com/commanders/muldrotha-the-gravetide
- EDHREC JSON endpoint: https://json.edhrec.com/pages/commanders/muldrotha-the-gravetide.json
- EDHREC optimized page: https://edhrec.com/commanders/muldrotha-the-gravetide/optimized
- Wizards Brackets update (Oct 21, 2025): https://magic.wizards.com/en/news/announcements/commander-brackets-beta-update-october-21-2025
- Wizards Brackets update (Feb 9, 2026): https://magic.wizards.com/en/news/announcements/commander-brackets-beta-update-february-9-2026
- Commander Brackets portal: https://magic.wizards.com/en/commander-brackets
- Commander RC context hub: https://mtgcommander.net/

