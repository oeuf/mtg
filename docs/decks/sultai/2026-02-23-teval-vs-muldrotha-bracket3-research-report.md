# Teval vs Muldrotha (Pool-Constrained) Bracket 3 Research Report

Snapshot date: **February 23, 2026**

## Executive Verdict

### Bottom line (brutal version)

- **Best actual Bracket-3 build in this local corpus:** `MUL-A` (Muldrotha authoritative Package A).
- **Best Teval build for tuned Bracket 3 pods:** `TEV-B` (updated tuned list, after the documented land-cut repair).
- **Most “technically legal, socially radioactive” build:** `TEV-E` (Field / Chasm / Crop lands-lock shell).
- **Most obvious Bracket-4 bleed while still 3-GC legal:** `MUL-E` (Ancient Tomb / Mana Vault / Chrome Mox).

### Commander verdict (with your exact pool)

- **Muldrotha is the better default commander for Bracket 3** with this pool because it converts your pool into a resilient, interactive, resource-accrual deck without needing to lean on lock patterns or turbo starts.
- **Teval has the nastier ceiling in terms of table experience** (especially lands-lock lines), but it is easier to accidentally build into “B3 on paper, B4 in feel” or “B3 legal, salt-maximizing” territory.

### Recommendation summary

- If the pod says “tuned Bracket 3” and actually means it: start with **`MUL-A`** or **`TEV-B`**.
- If the pod is secretly playing optimized decks and calling it Bracket 3: **`MUL-D`** or **`TEV-D`** are the honest upgrades.
- Do not call **`MUL-E`** or repeated **`TEV-E` Chasm/Strip/Waste lines** “normal Bracket 3” without explicit pregame consent.

## Methodology and Constraints

## Local sources (authoritative)

- [`teval-reference.md`](./teval-reference.md)
- [`muldrotha-reference.md`](./muldrotha-reference.md)
- [`user-card-pool-2026-02-22.txt`](./user-card-pool-2026-02-22.txt)
- Supporting local validation artifacts:
  - [`commander-reference-validation-report-with-pool.txt`](./commander-reference-validation-report-with-pool.txt)
  - [`local-build-analysis-2026-02-23.csv`](./local-build-analysis-2026-02-23.csv)
  - [`bracket3-scoring-matrix-2026-02-23.csv`](./bracket3-scoring-matrix-2026-02-23.csv)
  - [`benchmark-sample-2026-02-23.csv`](./benchmark-sample-2026-02-23.csv)

## External benchmark sources

- [EDHREC: Teval, the Balanced Scale](https://edhrec.com/commanders/teval-the-balanced-scale)
- [EDHREC: Muldrotha, the Gravetide](https://edhrec.com/commanders/muldrotha-the-gravetide)
- [Archidekt Teval search](https://archidekt.com/search/decks?commanders=Teval,%20the%20Balanced%20Scale)
- [Archidekt Muldrotha search](https://archidekt.com/search/decks?commanders=Muldrotha,%20the%20Gravetide)
- [Moxfield Teval search](https://www.moxfield.com/decks/public?format=commander&q=Teval%2C%20the%20Balanced%20Scale)
- [Moxfield Muldrotha search](https://www.moxfield.com/decks/public?format=commander&q=Muldrotha%2C%20the%20Gravetide)
- [Wizards: Introducing Commander Brackets Beta](https://magic.wizards.com/en/news/announcements/introducing-commander-brackets-beta)
- [Wizards: Brackets Beta Update (Oct 21, 2025)](https://magic.wizards.com/en/news/announcements/commander-brackets-beta-update-october-21-2025)

## Constraints enforced

- Recommendations are **pool-legal only** (plus basic lands).
- External decks are benchmark/context only.
- No direct recommendations are made from external lists unless the card exists in `user-card-pool-2026-02-22.txt`.

## Platform limitations (documented)

- **Moxfield** was JS-gated in this environment for deck-page metadata/decklist extraction. Moxfield findings are based on public search results and deck titles/URLs, not full deck parsing.
- **Archidekt** search snippets exposed useful metadata (deck size, cost, salt, tags, last update), which was enough for trend analysis and sample QA.
- **EDHREC** commander pages were accessible enough for aggregate/tag/game-changer/synergy snapshots.

## Local Build Inventory (Scored Full Builds)

### Teval builds

- `TEV-A` Tuned Bracket 3 (teval-1)
- `TEV-B` Tuned Bracket 3 Updated (teval-2, repaired to 36 lands / 99)
- `TEV-D` Max Degeneracy Alternate-GC (Rhystic / Rift / Fierce)
- `TEV-E` Max Degeneracy Lands-Lock (Crop / Field / Glacial Chasm, repaired to declared 99)
- `TEV-C` is comparison-only context (not a full 99 build)

### Muldrotha builds

- `MUL-A` Authoritative Bracket 3 (Default)
- `MUL-D` Max Degeneracy (The One Ring / Survival / Fierce)
- `MUL-E` Max Degeneracy Turbo (Ancient Tomb / Mana Vault / Chrome Mox)
- `MUL-A Packages` is variant guidance (not a full 99 build)

## Commander Review: Teval vs Muldrotha

## High-level comparison (with this pool)

| Axis | Teval | Muldrotha | Verdict |
|---|---|---|---|
| Commander-native engine identity | Lands/graveyard churn, attack-trigger pressure, token scaling | Permanent recursion engine that turns graveyard into a second hand | Tie on identity strength; different flavors |
| Bracket 3 default fit | Good, but often pushed toward generic blue power or lands-lock salt | Excellent; easy to build as strong, interactive, resource-accrual | **Muldrotha wins** |
| “Technically B3 but awful to play against” ceiling | Very high (`TEV-E`) | High (`MUL-E`, some lock packages) | **Teval wins (for worse reasons)** |
| Anti-hate resilience in your local builds | Good, but more sequencing-sensitive | Better; commander text + permanent recursion supports recovery | **Muldrotha wins** |
| Tuned-pod conversion (B3-upgraded meta) | Very good (`TEV-B`, `TEV-D`) | Very good (`MUL-A Package B`, `MUL-D`) | Tie, preference-dependent |
| Social risk / salt misread | High variance; lands-lock Teval draws heat fast | High when turbo, moderate when default | **Muldrotha safer by default** |

## Candid commander-level take

- **Teval is easier to overbuild into a miserable deck** while still being able to claim “I only have 3 GCs.” That is not a compliment.
- **Muldrotha is easier to build into a strong and legitimate Bracket-3 deck** because the commander naturally rewards value recursion and interactive permanents, not just speed compression or lock loops.
- With your pool specifically, you can build both commanders to be gross. The difference is: **Muldrotha gross looks like resilient midrange inevitability**, while **Teval gross often looks like land-based hostage-taking**.

## Intra-Commander Comparison (What Actually Changes)

## Teval build differences (local corpus)

Local pairwise overlap is high, but the package swaps change the table experience dramatically.

- `TEV-A` vs `TEV-B`: **88 shared cards** (11 changed each way)
- `TEV-A` vs `TEV-E`: **84 shared cards** (15 changed each way)
- `TEV-B` vs `TEV-E`: **81 shared cards** (18 changed each way)
- `TEV-D` vs `TEV-E`: **87 shared cards** (12 changed each way)

### What matters in practice

- `TEV-A` and `TEV-B` are both “Rhystic/Rift/Fierce tuned Teval,” but `TEV-B` is cleaner as a tuned pod list after the land-count repair and interaction smoothing.
- `TEV-D` is not just “another tuned Teval.” It adds more free stack leverage and degen texture, so it reads hotter than its GC count implies.
- `TEV-E` is a completely different social contract. The deck is commander-native and powerful, but the **Chasm + Strip/Waste pressure** is where “Bracket 3” stops meaning what most people think it means.

## Muldrotha build differences (local corpus)

Muldrotha variants are tighter and more interchangeable at the shell level.

- `MUL-A` vs `MUL-D`: **87 shared cards** (12 changed each way)
- `MUL-A` vs `MUL-E`: **90 shared cards** (9 changed each way)
- `MUL-D` vs `MUL-E`: **86 shared cards** (13 changed each way)

### What matters in practice

- Muldrotha’s identity remains stable across variants: self-mill/recursion/value, then cash out with `Living Death`, `Syr Konrad`, `Jarad + Lord`, etc.
- The **GC package** and a handful of support swaps create most of the power-shift.
- This is why `MUL-A` is so strong as a baseline: you can move it up/down without rewriting the deck’s identity.

## Cross-Commander Overlap (Important Reality Check)

The Sultai overlap is enormous across the corpus (**79-84 shared cards** in many cross-commander comparisons). The difference is not raw card pool size. The difference is:

- commander text,
- GC package choice,
- win conversion pattern,
- and social pressure profile.

This is exactly why “only 3 GCs” is not enough to judge power or experience.

## Bracket 3 Assessment (Brutal, Using the Local Rubric)

Bracket-3 scoring is in [`bracket3-scoring-matrix-2026-02-23.csv`](./bracket3-scoring-matrix-2026-02-23.csv).
Higher `b3_fit_score` means better Bracket-3 fit (not raw power).

## Scoreboard (full builds only)

| Build | B3 Fit Score | B4 Bleed Risk | Salt Risk | Candid read |
|---|---:|---|---|---|
| `MUL-A` | **83** | Low-Medium | Medium | Best Bracket-3-faithful list in the set |
| `TEV-B` | **72** | Medium | Medium | Best Teval tuned B3 default |
| `MUL-D` | **71** | Medium | Medium-High | Strong and spiky, but still defendable |
| `TEV-A` | **70** | Medium | Medium | Solid tuned B3, slightly rougher than TEV-B |
| `TEV-D` | **64** | Medium-High | Medium-High | Legal B3, plays hotter than it looks |
| `TEV-E` | **55** | Medium | **High** | Commander-native salt engine; pregame warning required |
| `MUL-E` | **50** | **High** | **High** | “Bracket 4 in a Bracket 3 trench coat” |

## Bracket-3 legality vs spirit (direct call-out)

### Pass on paper, questionable in spirit

- `TEV-E`: Passes 3-GC legality. Fails many pods’ expectation of fair Bracket-3 gameplay when the lands-lock lines are emphasized repeatedly.
- `MUL-E`: Passes 3-GC legality. Fast mana GC package (`Ancient Tomb`, `Mana Vault`, `Chrome Mox`) aligns closely with Wizards’ Bracket-4 optimization descriptors.

### Strongest legitimate Bracket-3 fits

- `MUL-A`: Best fit overall.
- `TEV-B`: Best Teval fit if the pod expects tuned but interactive games with cleaner closes.

## External Benchmark Comparison (EDHREC / Archidekt / Moxfield)

## EDHREC (macro identity + commander-native patterns)

### Teval (EDHREC)

EDHREC snapshot shows Teval as a **popular, high-velocity commander** (ranked highly with a large deck count), and its top tags emphasize:

- Reanimator
- Lands Matter
- Mill / Self-Mill

This matches the local Teval builds.

More importantly, EDHREC’s Teval page reinforces a key conclusion:

- **Field of the Dead + Crop Rotation + Glacial Chasm** appears as a highly relevant GC package for Teval’s commander-specific plan.
- Generic blue power cards (`Rhystic`, `Rift`) show up, but not as commander-native “best fit” signals in the same way.

Candid read:
- `TEV-E` is not a random meme. It is a commander-native endpoint.
- It is also the build most likely to make the table hate you.

### Muldrotha (EDHREC)

EDHREC snapshot for Muldrotha shows a long-established graveyard/value commander with tags that reflect what Muldrotha has always done well:

- Sacrifice
- Mill
- Reanimator
- Graveyard

High-synergy cards include classic Muldrotha recursion pieces (e.g., `Spore Frog`, `Seal of Primordium`, `Gravebreaker Lamia`, `Kaya's Ghostform` on the page snapshot), which strongly supports the local thesis that:

- `MUL-A` is the most “honest strong” Bracket-3 list here,
- and Muldrotha can scale up or down without losing its identity.

## Archidekt (public deck metadata trends + data quality)

Archidekt was the most useful public benchmark source in this environment because search snippets exposed **deck size, cost, salt score, tags, and update date**.

### Teval Archidekt sample (from benchmark CSV)

Strict 100-card sample stats (7 rows in the curated sample):

- Salt score range: **27.71 to 53.76**
- Salt score median: **37.96**
- Budget range: **$168.75 to $2,787.38**
- Budget median: **$749.64**

Data quality note:
- 4 sampled Teval rows were not 100 cards (`102`, `116`, `101`, `99`) and were treated as benchmark context only, not strict list comparisons.

Candid read:
- Teval public builds are all over the place, and **a lot of the public data is “unfinished list” noise**.
- Even with that noise, the salt range and combo/dredge/reanimator tags show Teval is being built well above casual expectations a lot of the time.

### Muldrotha Archidekt sample (from benchmark CSV)

Strict 100-card sample stats (9 rows in the curated sample):

- Salt score range: **35.95 to 59.05**
- Salt score median: **49.10**
- Budget range: **$152.64 to $4,996.86**
- Budget median: **$1,420.56**

Data quality note:
- 1 sampled Muldrotha row was 101 cards and excluded from strict comparison.

Candid read:
- Public Muldrotha builds trend **expensive and salty** in this sample.
- That does **not** mean Muldrotha is inherently less Bracket-3-friendly than Teval. It means public Muldrotha pilots also love tuning the commander hard.
- Muldrotha’s broad archetype spread makes it easier to hide optimization under “value pile” branding.

## Moxfield (title-level trend only in this environment)

Moxfield deck pages were JS-gated here, so this section is based on public search result titles/URLs (captured in the benchmark CSV).

### Teval Moxfield title sample (6 rows)

- **3/6 titles explicitly used “cEDH / cedh”**
- Other titles included variants like “Unbalanced Scale” / “Disbalance”

Candid read:
- Public Teval brewing culture is clearly comfortable pushing the commander into optimized territory.
- That makes Teval harder to evaluate by internet osmosis if your actual goal is “strong Bracket 3” and not “cEDH-adjacent graveyard deck.”

### Muldrotha Moxfield title sample (6 rows)

Sample titles leaned more archetype-descriptive than explicit cEDH branding:

- Dredge
- Graveyard Shenanigans
- Land killer
- Planeswalker/Lands
- Moxes and Mana

Candid read:
- Muldrotha titles were more varied and less uniformly cEDH-branded in the sample.
- But “land killer” and “moxes and mana” still confirm the commander can be tuned into highly oppressive shells quickly.

## Pros / Cons by Build (Brutal and Useful)

## Teval build review

### `TEV-A` (Tuned Bracket 3 baseline)

Pros:
- Strong tuned-pod conversion with `Rhystic / Rift / Fierce`.
- Clean Teval engine plan and real closers.
- Good starting point if you want power without jumping straight to degenerate Teval.

Cons:
- Feels more like “good Sultai blue-power shell with Teval” than pure commander-native lands identity.
- Free interaction + Rift package can still trigger “this is basically B4” complaints in some pods.
- Slightly rougher than `TEV-B` in list polish.

### `TEV-B` (Updated tuned Teval)

Pros:
- Best Teval default for tuned Bracket 3 in this corpus.
- Good interaction density and better list texture than `TEV-A`.
- Keeps strong conversion without leaning on Chasm-lock gameplay.

Cons:
- Same generic-power package optics (`Rhystic / Rift / Fierce`).
- Still easy to over-tune into `TEV-D` territory with just a few swaps.
- Source had a land-count error (fixed in the consolidated reference, but worth remembering when copying from older docs).

### `TEV-D` (Max degen alt-GC, Rhystic/Rift/Fierce)

Pros:
- High conversion rate and strong stack protection texture.
- Still wins with recognizable Teval graveyard/cash-out patterns.
- Excellent if the pod is actually playing spikier “Bracket 3” games.

Cons:
- Reads hot immediately (Pact + free interaction + degen posture).
- Less commander-unique than `TEV-E`.
- Strong chance of table perception mismatch (“you said B3…”).

### `TEV-E` (Field / Chasm / Crop lands-lock)

Pros:
- Most commander-native Teval power expression.
- Extremely strong inevitability and defensive panic-button lines.
- If the pod consents to this style, it is one of the strongest things you can do while staying 3-GC legal.

Cons:
- High salt risk even by tuned-pod standards.
- The problem is not just power; it is **experience** (repeated Chasm/land denial loops).
- Easy to cross from “cool engine” into “hostage simulator.”

## Muldrotha build review

### `MUL-A` (Authoritative default)

Pros:
- Best overall Bracket-3 fit in the corpus.
- Powerful, resilient, interactive, and still resource-accrual based.
- Easier to defend socially because the deck wins through pressure and inevitability, not speed compression.

Cons:
- Slightly slower raw ceiling than turbo variants if the pod is secretly optimized.
- Can still attract heat if pilots over-sequence self-mill into obvious `Living Death` turns.
- Not the highest win-rate option in every spike pod.

### `MUL-D` (Ring / Survival / Fierce degen)

Pros:
- Very high pressure with strong resilience and protection.
- Keeps Muldrotha identity intact while increasing conversion and threat density.
- Good “spikier but still recognizable Muldrotha” option.

Cons:
- Noticeably hotter than `MUL-A` in table feel.
- More likely to trigger anti-optimized table reactions.
- Starts to compress interactive windows more than many B3 pods expect.

### `MUL-E` (Ancient Tomb / Mana Vault / Chrome Mox turbo)

Pros:
- Explosive starts and higher raw win-rate pressure.
- Lets Muldrotha come online early and snowball hard.
- If your pod is actually optimized, this is the honest adaptation.

Cons:
- This is the clearest B4-bleed build in the entire set.
- Fast mana GC trio makes the deck feel optimized even when “legal.”
- Weakest Bracket-3 social fit despite technical compliance.

## Pool-Legal Recommendations (Explicitly Gated)

All recommendations below are **pool-legal against** [`user-card-pool-2026-02-22.txt`](./user-card-pool-2026-02-22.txt), plus basics. The pool file contains a typo (`Underream Lich`) which is treated as `Underrealm Lich` for validation.

## If your goal is “best real Bracket 3”

### Primary recommendation: start from `MUL-A`

Why:
- It scores highest on Bracket-3 fit in the local rubric.
- It aligns best with Wizards’ Bracket-3 “strong synergy + big turns after resources accrue” framing.
- It is the least likely to create immediate table expectation conflict compared to `TEV-E` and `MUL-E`.

#### Pool-legal tuning package for `MUL-A` (B3-faithful upgrades)

1. **IN `Spore Frog` / OUT `Accursed Marauder`**
- Why: EDHREC Muldrotha synergy strongly supports `Spore Frog`, and it is one of the most commander-native ways to buy time without turboing or hard-locking.
- Pool-legal: **Yes**

2. **IN `Bloom Tender` / OUT `Satyr Wayfinder`**
- Why: Cleaner acceleration and better ceiling when your shell already has sufficient self-mill and yard setup.
- Pool-legal: **Yes**

3. **IN `Glen Elendra Archmage` / OUT `Ledger Shredder`**
- Why: Better stack resilience and stronger recursion pattern for Muldrotha in tuned pods.
- Pool-legal: **Yes**

4. **IN `Volrath's Stronghold` / OUT `Exotic Orchard`**
- Why: Improves graveyard-independent recursion against hate and increases late-game inevitability.
- Pool-legal: **Yes**

### Secondary recommendation: `TEV-B` if you want Teval and tuned games

Why:
- It is the best Teval balance between power, conversion, and not immediately weaponizing the table experience.
- It avoids the social cliff of `TEV-E` while still being very strong.

#### Pool-legal tuning package for `TEV-B` (slightly higher conversion, still B3-defensible)

1. **IN `Entomb` / OUT `Farseek`**
- Why: Improves graveyard setup speed and consistency without changing the GC package.
- Pool-legal: **Yes**

2. **IN `Pact of Negation` / OUT `Tireless Tracker`**
- Why: Raises conversion on critical turns in tuned pods; use only if your pod is truly high-power B3.
- Pool-legal: **Yes**

3. **IN `Conduit of Worlds` / OUT `Sensei's Divining Top`**
- Why: Moves the list back toward a more commander-native recursion posture and improves post-hate recovery texture.
- Pool-legal: **Yes**

## If your goal is “maximum power while still 3-GC legal” (with honesty about the vibe)

### Teval option: `TEV-E` (only with explicit pod consent)

Candid recommendation:
- This is a valid strategic endpoint for Teval.
- It is also the build most likely to create “you lied about Bracket 3” reactions even when you technically did not.

#### Pool-legal TEV-E improvements (commander-native degen, but cleaner closes)

1. **IN `Icetill Explorer` / OUT `Satyr Wayfinder`**
- Why: Improves the lands/Chasm engine ceiling and supports repeated land recursion play patterns.
- Pool-legal: **Yes**

2. **IN `Craterhoof Behemoth` / OUT `Massacre Wurm`**
- Why: Converts `Field of the Dead` / `Scute Swarm` boards into immediate lethal more reliably.
- Pool-legal: **Yes** (important update; this is in the current pool file)

#### Social warning (serious)

- If you run `TEV-E`, announce the deck honestly as a **lands-lock-leaning Teval deck** in pregame conversation.
- If you don’t, you are going to create bad games and then argue semantics about GC counts.

### Muldrotha option: `MUL-E` (honest “optimized-leaning” choice)

Candid recommendation:
- `MUL-E` is the better choice than pretending `MUL-A` is enough if your pod is effectively Bracket 4.
- But do not present `MUL-E` as a normal Bracket-3 social experience.

#### De-escalation path (pool-legal, better B3 fit)

If `MUL-E` is drawing heat, swap GC package off turbo fast mana:

- **Option A (best B3 fit):** move to `MUL-A` package (`Survival of the Fittest`, `The One Ring`, `Force of Will`)
- **Option B (high conversion tuned pods):** move to `MUL-A Package B` (`Rhystic Study`, `Cyclonic Rift`, `Fierce Guardianship`)

All cards are pool-legal.

## If your goal is “lower salt, still strong”

### Choose `MUL-A` over any Teval degen shell

Reason:
- Muldrotha’s strongest lines still look like interactive recursion/value to most tables.
- Teval’s strongest commander-native lines (`TEV-E`) look like lock gameplay.

### If you insist on Teval, choose `TEV-B`, not `TEV-E`

Reason:
- `TEV-B` wins cleaner and faster without repeatedly denying combat or normal game pacing.
- `TEV-E` is powerful, but power is not the only variable that matters in Bracket-3 pods.

## External Benchmark vs Local Builds: What You Should Actually Learn

### 1. Teval’s internet ceiling is real, and it will distort your expectations

- EDHREC and Moxfield evidence both point to Teval being pushed hard.
- If you copy Teval internet vibes blindly, you will end up in `TEV-D/TEV-E` land fast.
- For actual Bracket-3 play, **treat `TEV-B` as the baseline and `TEV-E` as an opt-in social contract deck**.

### 2. Muldrotha is easier to tune responsibly, but not automatically responsible

- EDHREC and Archidekt both show Muldrotha scales into very expensive, very salty shells.
- `MUL-A` is good because it is intentionally constrained by play pattern, not because Muldrotha is inherently fair.
- If you hand the deck to a spike mindset and add turbo pressure, it becomes `MUL-E` quickly.

### 3. GC count is a weak proxy for Bracket fit

This corpus demonstrates the problem clearly:

- `MUL-A` and `MUL-E` both pass 3-GC legality.
- `TEV-B` and `TEV-E` both pass 3-GC legality.
- They are **not remotely the same Bracket-3 experience**.

## Final Recommendations (by Goal)

## Goal: Strongest fair-ish Bracket 3 deck

- **Pick:** `MUL-A`
- **Tuning package:** `Spore Frog`, `Bloom Tender`, `Glen Elendra Archmage`, `Volrath's Stronghold` swaps listed above
- **Why:** Best balance of power, resilience, and table-read honesty

## Goal: Tuned Bracket 3 Teval without social self-sabotage

- **Pick:** `TEV-B`
- **Tuning package:** `Entomb`, `Pact of Negation`, `Conduit of Worlds` swaps listed above (choose how hot you want it)
- **Why:** Best Teval conversion while avoiding the worst lands-lock optics

## Goal: Maximum pain (still 3-GC legal) with honest pregame disclosure

- **Pick:** `TEV-E` if you want commander-native degeneracy; `MUL-E` if the pod is effectively optimized
- **Required behavior:** Tell the pod what the deck actually does before the game starts
- **Why:** These decks are not “normal B3” experiences even when technically legal

## Appendix A: Key Evidence Snapshots (What I Actually Used)

## Wizards Bracket framing (used for the rubric)

- Wizards explicitly frames Bracket 3 around **strong, upgraded decks** with interaction and “big turns” after resources accrue, while Bracket 4 signals include **fast mana** and stronger optimization pressure.
- This is why `MUL-E` scores poorly on B3 fit despite passing the 3-GC cap.

## EDHREC snapshots (commander identity + GC trends)

- Teval page supports the local conclusion that **lands-lock / lands-recursion Teval** is a commander-native power route.
- Muldrotha page supports the local conclusion that **permanent-recursion value loops** are the commander’s strongest and most natural identity.

## Archidekt sample QA note

- Public deck searches contain a non-trivial number of non-100-card lists. Those rows were included as metadata context but excluded from strict “ready-to-play Commander list” comparisons.

## Moxfield QA note

- JS-gated pages prevented decklist extraction in this environment. Moxfield findings are title/URL trend signals only and are labeled as such in the benchmark CSV.

## Appendix B: Data Quality Notes

- Pool file typo: `Underream Lich` should be interpreted as `Underrealm Lich` for recommendation gating and build validation.
- Pool file contains duplicates (see validation report), but recommendations were checked against the deduplicated normalized pool.
- Consolidated reference docs already contain documented source repairs for overflow/typo issues and pass structural validation.
