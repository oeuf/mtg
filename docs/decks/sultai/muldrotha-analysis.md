# Muldrotha Analysis: Making It Degenerate, Keeping It Bracket 3

---

## The First Problem: This Deck Is Currently Illegal

The deck header declares **Cyclonic Rift, Intuition, Survival of the Fittest** as Game Changers (3 GCs — at the Bracket 3 cap). But **Cyclonic Rift is not in the decklist**, and **Gifts Ungiven is** — tagged `(GC)` in the Instants section but not declared in the header. The deck has 4 distinct Game Changers spread across header and list. That's a rule violation.

**Resolution:** Keep Cyclonic Rift (irreplaceable table reset), ditch Gifts Ungiven. Reasoning below. This also fixes the header.

---

## What This Deck Actually Is

Muldrotha is a **permanent-type recursion engine**. She turns your graveyard into a second hand and generates value every turn at no additional cost. The deck's identity should be: **you accrue resources while opponents hemorrhage them**. Every card should do at least one of: (1) put permanents in the graveyard, (2) abuse Muldrotha's recursion, (3) restrict what opponents can do.

Cards that don't hit any of those three criteria are wasted slots.

The current build has the right bones but several cards are either wrong-archetype tourists or two-card packages that eat slots for a single narrow function.

---

## Game Changer Verdict

**Bracket 3 cap: 3 GCs.** Current effective GCs: 4. Must cut one.

| GC | Keep/Cut | Rationale |
|----|----------|-----------|
| Cyclonic Rift | **Keep** | The premier kill-turn setup. Overloaded at instant speed, it clears all opposing boards and creates an uncontested window. Nothing else does this at this efficiency. Put it back in the list where it belongs. |
| Intuition | **Keep** | Strictly better than Gifts Ungiven in Muldrotha. You choose which 1 goes to hand and which 2 go to graveyard — both piles are live with Muldrotha in play. Instant speed. Game-defining. |
| Survival of the Fittest | **Keep** | The primary tutor engine. Pitches creatures to graveyard while fetching what the board demands. Enables every creature-based line. Non-negotiable. |
| Gifts Ungiven | **Cut** | Worse than Intuition in this deck. Opponents choose which 2 of the 4 cards go to graveyard — they'll always split your pile to minimize your gain. Intuition already does what you need. The 4th GC slot is simply not worth burning on a strictly-weaker version of a card you already run. |

---

## Card-by-Card Critique

### Cards to Cut

**The Gitrog Monster**
Verdict: **Cut.**
It draws cards when lands enter the graveyard. That sounds good until you examine the actual rate. You need Dakmor Salvage in the yard plus a discard outlet to loop it — Dakmor is in the deck, but there is no dedicated discard outlet. Without the Dakmor loop it's a 6-mana 6/6 deathtouch that occasionally draws you a card when a fetchland cracks. That is not a 6-drop. The deck already has Syr Konrad, Sylvan Library, Mystic Remora, and Underrealm Lich (proposed) for draw. Gitrog is a high-cost, low-consistency card that needs a piece you don't have to be broken and is merely fine otherwise. Cut it.

**Lord of Extinction + Jarad, Golgari Lich Lord**
Verdict: **Cut both.**
This is a two-card package that requires both pieces to do anything. Individually: Jarad is a 5/5 for 4 that occasionally lets you fling things. Lord of Extinction is a 0/0 that grows based on all graveyards. Neither does anything alone. Together they're a telegraphed, slow kill line that requires tutoring two specific cards AND having a large graveyard count AND having {B}{G} available three times. The Gravecrawler loop (Gravecrawler + Pitiless Plunderer + any altar) is faster, more deterministic, and needs no dedicated pair. These two cards are dead weight 70% of the time. Cutting both frees 2 slots for cards that are independently useful.

**Gifts Ungiven**
Verdict: **Cut.** (See GC audit above.)

**Ledger Shredder**
Verdict: **Cut.**
Good in spell-heavy decks. This is a permanent-heavy Muldrotha build. You cast 1-2 spells per turn average, so Shredder triggers infrequently. Connive helps fill the graveyard but you're competing with Stitcher's Supplier, Hedron Crab, and Mesmeric Orb for that role — all of which mill more consistently without needing to survive combat. Shredder is doing approximately 60% of what a dedicated mill piece would do, with the upside of card selection that's already covered by Sylvan Library and Sensei's Divining Top. Cut.

**Sidisi, Brood Tyrant**
Verdict: **Cut.**
Decent but outclassed. Sidisi mills 3 on ETB and on attack, generating Zombie tokens if you hit a creature. The tokens have no synergy — they're not sac fodder targets, they don't combo with anything specific, and they die to any board wipe you want to deploy. Underrealm Lich does everything Sidisi does for graveyard-filling purposes and does it better, without needing to attack and without leaving disposable tokens. The slot is better spent.

**Birthing Pod**
Verdict: **Cut.**
Pod requires a living creature to activate. This deck kills its own creatures constantly — sacrificing to altars, Plaguecrafter triggers, Entomb, Survival of the Fittest discards. Pod wants a continuous creature chain available, but between recursive creatures (Gravecrawler, Bloodghast) and sac outlets consuming bodies, maintaining a curve for Pod is awkward. It's also 4 mana and {2} to activate. The tutor density from Survival of the Fittest and Buried Alive + Entomb is already high; Pod is solving a problem the deck doesn't have at a cost the deck doesn't want.

**Bloodghast**
Verdict: **Cut.**
Free recurring 2/1 haste — sounds good. The issue: this deck wants recursive value engines, not beaters. Bloodghast is a 2/1 you can't block with (no relevant abilities defensively), and attacking is often wrong since Spore Frog locks down combat. It synergizes with Skullclamp (sac for 2 cards) and altars, but so does Gravecrawler — which is the actual combo piece. Bloodghast is a redundant, weaker Gravecrawler slot that doesn't advance any combo line and doesn't lock opponents out of anything.

---

### Cards That Are Fine

Keep without qualification: **Baleful Strix, Birds of Paradise, Bloom Tender, Dauthi Voidwalker, Deathrite Shaman, Eternal Witness, Gravebreaker Lamia, Gravecrawler, Haywire Mite, Hedron Crab, Pitiless Plunderer, Plaguecrafter, Spore Frog, Stitcher's Supplier, Syr Konrad, Vile Entomber** — all earn their slots through direct synergy with the engine.

Keep: **Animate Dead, Exploration, Kaya's Ghostform, Mystic Remora, Necromancy, Pernicious Deed, Seal of Primordium, Survival of the Fittest, Sylvan Library, Tortured Existence** — enchantment package is strong, Pernicious Deed recursion is genuinely oppressive.

Keep: **All artifacts except Birthing Pod** — the altar suite is the combo engine, Crucible + Life from the Loam is land value, Mesmeric Orb is the best self-mill available, the rest are utility.

Keep: **All instants except Gifts Ungiven** — counterspell suite is clean and efficient.

Keep: **All sorceries** — Buried Alive + Living Death is a kill package, Reanimate is efficient reanimation, Life from the Loam is self-mill + land recursion.

**Dakmor Salvage note:** With Gitrog cut, Dakmor Salvage loses its combo function. However, Dredge 2 is still legitimate graveyard fuel — every time you would draw it, you instead mill 2. In a graveyard deck that's not nothing. Keep it for now, but it's a marginal land without Gitrog.

---

## Cards to Add

### Must-Adds

**Cyclonic Rift** *(already declared as GC in header — add it back to the list)*
This was apparently removed by accident. The entire closing strategy in the piloting guide references it. Put it back in Instants.

---

**Kheru Goldkeeper** *(Creature, {1}{B}{G}{U}, 3/3 Flying)*
New from Tarkir: Dragonstorm. Whenever one or more cards leave your graveyard during your turn, create a Treasure token. With Muldrotha replaying 2-3 permanents from the graveyard every turn, this generates 1 Treasure per turn minimum — and on combo turns where you're replaying multiple permanents, it chains. The Renew ability ({2}{B}{G}{U}, exile a card from your graveyard → put two +1/+1 counters and flying on a creature) is gravy. This card is purpose-built for Muldrotha and was almost certainly designed with her in mind.

**Underrealm Lich** *(Creature, {3}{B}{G})*
Replaces both Gitrog Monster and Sidisi in one card. Whenever you draw a card, instead look at the top 3 cards of your library, put one in hand and two in graveyard. This is better than drawing — you get selection AND consistent graveyard loading. Also makes you indestructible for 4 life. As a creature it's replayed by Muldrotha. Removes the inconsistency of hoping to mill creatures when Sidisi attacks. The card selection stacks beautifully with Sylvan Library and Sensei's Divining Top.

**Contamination** *(Enchantment, {2}{B})*
All lands tap for {B} only. Replayed from graveyard by Muldrotha if it falls off or gets destroyed. With Gravecrawler as sac fodder (or Bitterblossom tokens), this locks non-black decks out of casting spells. Your lands produce B, G, U through Urborg, Yavimaya, and Muldrotha's color identity — opponents tap all their lands for black and can't cast anything. This is the single highest-impact "salty" addition available in Bracket 3. It's not a Game Changer. It will make people hate you. Correct.

**Bitterblossom** *(Enchantment, {1}{B})*
Creates a 1/1 Faerie Rogue token each upkeep. Primary function here: provides Contamination with an inbuilt sac outlet. Secondary function: tokens synergize with Skullclamp (sac a 1/1 for 2 cards), altars (sacrifice for mana), and Syr Konrad (dies for drain triggers). As an enchantment it's recurrable with Muldrotha. The 1 life per turn is trivial.

**Secrets of the Dead** *(Enchantment, {2}{U})*
Draw a card whenever you cast a spell from your graveyard. Muldrotha casts 2-3 permanents from graveyard every turn. That's 2-3 extra draw triggers per turn cycle, on an enchantment that Muldrotha replays if removed. This is raw card advantage that scales directly with the engine running correctly. Absurd in practice.

**Glen Elendra Archmage** *(Creature, {3}{U})*
Persist + {U}, sacrifice: counter target noncreature spell. Dies, comes back with a -1/-1 counter, and can be sacrificed again for another counter. With Muldrotha, once she's gone permanently you just replay it from the graveyard and start over. Creates a soft recurring counterspell lock on noncreature spells. Extremely oppressive and thematically perfect — this is the kind of card that generates the "kill on sight" response, which is appropriate for this deck's identity.

**Stinkweed Imp** *(Creature, {2}{B})*
Dredge 5. Every time you would draw it, mill 5 instead. 1/2 Flying deathtouch. Plays both roles: self-mill engine and recurring blocker. With Muldrotha it's replayed from graveyard. With Tortured Existence you can cycle it continuously. This is one of the best self-mill cards in the format and costs almost nothing.

---

### Strong Considers

**Hermit Druid** *(Creature, {1}{G})*
The deck runs zero basic lands. One activation of Hermit Druid mills your entire library. Combined with a win condition in the deck (the Gravecrawler loop needs Pitiless Plunderer, or you add Thassa's Oracle), this is an instant-win button. This is upper Bracket 3 and not a Game Changer. If you want to push to maximum degeneracy, add Hermit Druid and Thassa's Oracle. Oracle is not a Game Changer. One warning: this fully shifts the deck's identity from "grind them to nothing" to "win on demand" — decide which identity you want.

**Bone Miser** *(Creature, {4}{B})*
Whenever you discard a land, create a Zombie token. Creature — Zombie token. Something else — draw a card. Synergizes with Tortured Existence (discard to recurse, trigger Bone Miser), Life from the Loam (discard lands), and any other discard outlets. Provides both card draw and bodies. The 5-drop slot is already crowded but this generates ongoing value.

---

## The Oppression Package

The deck's new identity should be: **opponents cannot function while you grind**. The core stax loop:

- **Contamination + Bitterblossom** — lock all non-black mana permanently. Opponents tap 8 lands and get {B}. You operate normally through Urborg + Yavimaya.
- **Spore Frog (recurring)** — no combat. Ever. Replayed every turn from the graveyard for {G}.
- **Pernicious Deed (recurring)** — any attempt to rebuild a board gets wiped. Replayed from graveyard immediately after use.
- **Plaguecrafter (recurring)** — every Muldrotha turn cycle a player loses a creature or a card from hand. Grind them to nothing.
- **Glen Elendra Archmage** — soft lock on noncreature spells. Persistent across multiple dies/replays.
- **Mesmeric Orb** — everyone mills every untap. You benefit. They don't.

The result: opponents can't attack, can't cast most spells, can't keep permanents, and slowly mill out. You win by being the only functional player at the table.

---

## Thematic Coherence Check

Muldrotha's theme is **inevitable consumption**. Everything rots, everything returns, everything feeds the engine. Cards that don't fit that theme AND don't contribute mechanically are dead weight.

| Card | Thematic Fit | Mechanical Fit | Verdict |
|------|-------------|----------------|---------|
| Jarad | Low | Narrow | Cut |
| Lord of Extinction | Low | Narrow | Cut |
| Gitrog Monster | Medium | Conditional | Cut |
| Sidisi | Medium | Moderate | Cut (outclassed) |
| Ledger Shredder | Low | Weak | Cut |
| Contamination | **High** | **Strong** | Add |
| Underrealm Lich | **High** | **Strong** | Add |
| Stinkweed Imp | **High** | **Strong** | Add |
| Kheru Goldkeeper | **High** | **Strong** | Add |
| Secrets of the Dead | **High** | **Strong** | Add |
| Glen Elendra Archmage | **High** | **Strong** | Add |

---

## Recommended Changes Summary

### Cuts (8 cards)
1. **Gifts Ungiven** — illegal 4th GC, weaker than Intuition in this deck
2. **The Gitrog Monster** — conditional, no discard outlet for the Dakmor loop
3. **Lord of Extinction** — only serves the Jarad package
4. **Jarad, Golgari Lich Lord** — only serves the Lord of Extinction package
5. **Ledger Shredder** — wrong archetype; minimal contribution to graveyard engine
6. **Sidisi, Brood Tyrant** — replaced completely by Underrealm Lich
7. **Birthing Pod** — awkward in a sac-heavy deck; tutor density already sufficient
8. **Bloodghast** — beater in a non-combat deck; redundant with Gravecrawler for combo purposes

### Adds (8 cards)
1. **Cyclonic Rift** *(GC — already declared in header)* — restore the missing card
2. **Underrealm Lich** — replaces Gitrog + Sidisi simultaneously; best graveyard-filling draw engine available
3. **Contamination** — the highest-impact oppression piece that fits this archetype
4. **Bitterblossom** — Contamination fuel + Skullclamp fodder + Syr Konrad drain; recurrable enchantment
5. **Kheru Goldkeeper** — Treasure per graveyard-leave during your turn; custom-built for Muldrotha
6. **Glen Elendra Archmage** — recurring soft counterspell lock; extremely oppressive with Muldrotha
7. **Stinkweed Imp** — Dredge 5 is the best self-mill rate available on a creature
8. **Secrets of the Dead** — 2-3 extra draw triggers per turn cycle on an enchantment

### GC Header After Changes
**Game Changers:** Cyclonic Rift, Intuition, Survival of the Fittest *(3 of 3 — legal)*

---

## Revised Decklist

### Commander
- Muldrotha, the Gravetide

### Creatures (20)
- Baleful Strix
- Birds of Paradise
- Bloom Tender
- Dauthi Voidwalker
- Deathrite Shaman
- Eternal Witness
- Glen Elendra Archmage
- Gravebreaker Lamia
- Gravecrawler
- Haywire Mite
- Hedron Crab
- Kheru Goldkeeper
- Pitiless Plunderer
- Plaguecrafter
- Spore Frog
- Stitcher's Supplier
- Stinkweed Imp
- Syr Konrad, the Grim
- Underrealm Lich
- Vile Entomber

### Enchantments (13)
- Animate Dead
- Bitterblossom
- Contamination
- Exploration
- Kaya's Ghostform
- Mystic Remora
- Necromancy
- Pernicious Deed
- Seal of Primordium
- Secrets of the Dead
- Survival of the Fittest (GC)
- Sylvan Library
- Tortured Existence

### Artifacts (12)
- Altar of Dementia
- Arcane Signet
- Ashnod's Altar
- Crucible of Worlds
- Lightning Greaves
- Lotus Petal
- Mesmeric Orb
- Perpetual Timepiece
- Phyrexian Altar
- Sensei's Divining Top
- Skullclamp
- Sol Ring

### Instants (12)
- Arcane Denial
- Assassin's Trophy
- Counterspell
- Cyclonic Rift (GC)
- Deadly Rollick
- Entomb
- Force of Negation
- Intuition (GC)
- Mana Drain
- Noxious Revival
- Swan Song
- Veil of Summer

### Sorceries (6)
- Buried Alive
- Life from the Loam
- Living Death
- Nature's Lore
- Reanimate
- Victimize

### Lands (36)
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

---

*Total: 99 cards + 1 commander = 100. GCs: Cyclonic Rift, Intuition, Survival of the Fittest (3/3 — Bracket 3 legal).*
