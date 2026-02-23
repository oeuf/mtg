# Pool Compliance Check Notes (2026-02-23)

## Scope

- Validates all explicit recommendation cards used in `2026-02-23-teval-vs-muldrotha-bracket3-research-report.md` against the normalized pool file.
- Pool file: `docs/decks/sultai/user-card-pool-2026-02-22.txt`
- Basic lands are implicitly allowed and were not enumerated in the recommendation card table.

## Pool Normalization Summary

- Raw non-empty entries: 1052
- Deduplicated normalized entries: 1006
- Duplicate entries detected (case-insensitive): 46
- Known typo retained in pool file: `Underream Lich` (used as alias for `Underrealm Lich` during validation).

## Recommendation Card Membership Results

| Group | Role | Card | In Normalized Pool? | Notes |
|---|---|---|---|---|
| MUL-A B3-faithful upgrades | IN | Spore Frog | YES |  |
| MUL-A B3-faithful upgrades | OUT | Accursed Marauder | YES |  |
| MUL-A B3-faithful upgrades | IN | Bloom Tender | YES |  |
| MUL-A B3-faithful upgrades | OUT | Satyr Wayfinder | YES |  |
| MUL-A B3-faithful upgrades | IN | Glen Elendra Archmage | YES |  |
| MUL-A B3-faithful upgrades | OUT | Ledger Shredder | YES |  |
| MUL-A B3-faithful upgrades | IN | Volrath's Stronghold | YES |  |
| MUL-A B3-faithful upgrades | OUT | Exotic Orchard | YES |  |
| TEV-B tuned B3 conversion package | IN | Entomb | YES |  |
| TEV-B tuned B3 conversion package | OUT | Farseek | YES |  |
| TEV-B tuned B3 conversion package | IN | Pact of Negation | YES |  |
| TEV-B tuned B3 conversion package | OUT | Tireless Tracker | YES |  |
| TEV-B tuned B3 conversion package | IN | Conduit of Worlds | YES |  |
| TEV-B tuned B3 conversion package | OUT | Sensei's Divining Top | YES |  |
| TEV-E commander-native degen upgrades | IN | Icetill Explorer | YES |  |
| TEV-E commander-native degen upgrades | OUT | Satyr Wayfinder | YES |  |
| TEV-E commander-native degen upgrades | IN | Craterhoof Behemoth | YES |  |
| TEV-E commander-native degen upgrades | OUT | Massacre Wurm | YES |  |
| GC package swap references (all pool-legal) | GC | Survival of the Fittest | YES |  |
| GC package swap references (all pool-legal) | GC | The One Ring | YES |  |
| GC package swap references (all pool-legal) | GC | Force of Will | YES |  |
| GC package swap references (all pool-legal) | GC | Rhystic Study | YES |  |
| GC package swap references (all pool-legal) | GC | Cyclonic Rift | YES |  |
| GC package swap references (all pool-legal) | GC | Fierce Guardianship | YES |  |
| GC package swap references (all pool-legal) | GC | Mana Vault | YES |  |
| GC package swap references (all pool-legal) | GC | Chrome Mox | YES |  |
| GC package swap references (all pool-legal) | GC | Ancient Tomb | YES |  |

## Result

- All explicit recommendation cards in the report are present in the normalized pool.
- No recommendation relies on an external-only staple outside the pool.
- Report recommendations remain subject to Commander legality and bracket/social-fit considerations; this file checks pool membership only.
