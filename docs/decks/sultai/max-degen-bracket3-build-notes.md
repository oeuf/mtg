# Max Degeneracy Bracket 3 Build Notes

## Snapshot and Guardrails
- Date target: 2026-02-23.
- Pool constraint: only `user-card-pool-2026-02-22.txt` plus basics.
- Bracket constraint: exactly 3 Game Changers (GCs) per deck, enforced against the Wizards Commander Brackets GC list (Oct 21, 2025 update + Feb 9, 2026 additions).
- `Sol Ring` is intentionally kept in both decks because Wizards explicitly excluded it from the Game Changers list in the Brackets beta FAQ and subsequent updates.

## Muldrotha - Build Philosophy
- Baseline: `MUL-E` (turbo GC package) from `muldrotha-reference.md`.
- Target identity: turbo Muldrotha recursion engine, not generic Sultai fast-mana pile.
- Upgrades prioritize permanent-based recursion loops, sacrifice outlets, and creature-tutor bodies over fair draw/value cards.

## Muldrotha - Major Adds
- Creatures: `Satyr Wayfinder`, `Caustic Caterpillar`, `Haywire Mite`, `Spore Frog`, `Glen Elendra Archmage`, `Pitiless Plunderer`, `Gravecrawler`, `Gravebreaker Lamia`, `Vile Entomber`, `Craterhoof Behemoth`, `Sidisi, Brood Tyrant`
- Artifacts: `Phyrexian Altar`, `Altar of Dementia`, `Birthing Pod`
- Enchantments: `Tortured Existence`, `Kaya's Ghostform`
- Lands: `Phyrexian Tower`, `Volrath's Stronghold`

## Muldrotha - Major Cuts
- Creatures: `Nyx Weaver`, `Baleful Strix`, `Ledger Shredder`, `Accursed Marauder`, `Mulldrifter`, `Massacre Wurm`, `Plaguecrafter`, `River Kelpie`
- Artifacts: `Arcane Signet`, `Talisman of Resilience`, `Swiftfoot Boots`, `Soul-Guide Lantern`
- Instants: `Noxious Revival`, `Counterspell`, `Beast Within`
- Sorceries: `Three Visits`
- Lands: `Shipwreck Marsh`, `Dreamroot Cascade`

## Teval - Build Philosophy
- Baseline: `TEV-E` (Field/Chasm/Crop) from `teval-reference.md`.
- Target identity: commander-native lands recursion / soft-lock shell with explicit kill conversion (not blue-value soup).
- Upgrades add landfall acceleration, extra land drops, recursive land utility, and a clean `Craterhoof Behemoth` finish.

## Teval - Major Adds
- Creatures: `Icetill Explorer`, `Craterhoof Behemoth`, `Vile Entomber`, `Lotus Cobra`, `Azusa, Lost but Seeking`, `Tireless Provisioner`, `The Gitrog Monster`
- Artifacts: `Perpetual Timepiece`
- Instants: `Heroic Intervention`, `Veil of Summer`
- Lands: `Boseiju, Who Endures`, `Takenuma, Abandoned Mire`, `Otawara, Soaring City`, `Evolving Wilds`, `Bojuka Bog`, `Terramorphic Expanse`, `Ghost Quarter`

## Teval - Major Cuts
- Creatures: `Baleful Strix`, `Plaguecrafter`, `Dauthi Voidwalker`, `Massacre Wurm`, `Nyx Weaver`
- Artifacts: `Arcane Signet`, `Soul-Guide Lantern`, `Swiftfoot Boots`
- Enchantments: `Secrets of the Dead`
- Instants: `Arcane Denial`, `Counterspell`, `Noxious Revival`
- Lands: `Exotic Orchard`, `City of Brass`, `Blooming Marsh`, `Shipwreck Marsh`, `Mana Confluence`, `Darkslick Shores`

## Rejected / Excluded (Brutal)
- `Seedborn Muse`: extremely strong in Muldrotha, but it is a GC; including it would break the locked turbo GC package.
- `The One Ring`, `Survival of the Fittest`, `Force of Will`, `Fierce Guardianship`, `Rhystic Study`, `Cyclonic Rift`, `Demonic Tutor`, `Vampiric Tutor`, `Imperial Seal`, `Mystical Tutor`, `Worldly Tutor`, `Gifts Ungiven`, `Intuition`: all excluded because they are GCs and would exceed the exact 3-GC cap in these locked builds.
- `Mox Diamond`: excluded despite strong synergy in Teval because it is a Game Changer and would break the locked Field/Chasm/Crop package.
- `Primeval Titan`: present in the pool but Commander-banned; excluded by rule.

## Social Contract Warning
- Both decks are built to maximize pressure while remaining technically Bracket 3 legal on paper. They are intentionally miserable for underprepared tables.
- Muldrotha pressures with recursive engine assembly and resilient cash-out turns; Teval pressures with land denial / Chasm survival / Field inevitability into overrun kills.
