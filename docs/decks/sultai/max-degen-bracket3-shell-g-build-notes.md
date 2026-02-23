# Max Degeneracy Bracket 3 G-Shell Build Notes

## Snapshot and Intent
- Goal: build genuinely new max-degeneracy Bracket 3 shells (`MUL-G`, `TEV-G`) rather than derivative rewrites of `MUL-E/F` and `TEV-E/F`.
- Pool constraint: only `user-card-pool-2026-02-22.txt` (+ basics).
- GC constraint: exactly 3 Game Changers, using new locked packages for each commander.
- Sol Ring note: `Sol Ring` is intentionally allowed and treated as non-GC per Wizards Brackets FAQ/update language.

## Locked GC Packages
- `MUL-G`: `Intuition`, `Gifts Ungiven`, `Survival of the Fittest`.
- `TEV-G`: `Field of the Dead`, `Crop Rotation`, `Mox Diamond` (explicitly off `Glacial Chasm`).

## Novelty Proof - Muldrotha (`MUL-G`)
- Overlap metrics against existing full Muldrotha builds:
- `MUL-F`: shared=71, adds=26, cuts=28
- `MUL-D`: shared=60, adds=37, cuts=39
- `MUL-A`: shared=53, adds=44, cuts=46
- `MUL-E`: shared=53, adds=44, cuts=46
- Nearest baseline by overlap: `MUL-F` (shared=71).
- `MUL-G` meets the hard novelty thresholds (<=72 shared vs `MUL-E/F`, <=78 vs `MUL-A/D`, and >=24 adds/cuts vs nearest baseline).

## Novelty Proof - Teval (`TEV-G`)
- Overlap metrics against existing full Teval builds:
- `TEV-F`: shared=72, adds=27, cuts=27
- `TEV-A`: shared=58, adds=41, cuts=41
- `TEV-B`: shared=57, adds=42, cuts=42
- `TEV-D`: shared=57, adds=42, cuts=42
- `TEV-E`: shared=56, adds=43, cuts=43
- Nearest baseline by overlap: `TEV-F` (shared=72).
- `TEV-G` meets the hard novelty thresholds (<=72 shared vs `TEV-E/F`, <=80 vs `TEV-A/B/D`, and >=22 adds/cuts vs nearest baseline).

## Muldrotha G - Shell Notes
- This shell is built around instant-speed graveyard pile assembly (`Intuition`, `Gifts Ungiven`) and permanent recursion conversion, not turbo fast mana.
- `Survival of the Fittest` remains the commander-native GC because it supercharges the pile -> yard -> replay plan.
- Recurable answer suite is intentionally permanent-heavy (`Seal of Primordium`, `Seal of Removal`, `Caustic Caterpillar`, `Haywire Mite`) so Muldrotha converts interaction into inevitability.
- `Panharmonicon`, `Emry`, `Araumi`, `Sidisi`, and reanimation tutor bodies create a distinctly different engine shape from `MUL-E/F`.

## Muldrotha G - Major Adds vs `MUL-F`
- `Araumi of the Dead Tide`, `Ashnod's Altar`, `Dread Return`, `Dryad Arbor`, `Emry, Lurker of the Loch`, `Flooded Strand`, `Forest`, `Gifts Ungiven`, `High Market`, `Intuition`, `Island`, `Llanowar Wastes`, `Lotus Cobra`, `Lotus Petal`, `Meren of Clan Nel Toth`, `Mortuary Mire`, `Panharmonicon`, `Seal of Doom`, `Seal of Removal`, `Secrets of the Dead`, `Shifting Woodland`, `Survival of the Fittest`, `Swamp`, `Terramorphic Expanse`, `Underground River`, `Yavimaya Coast`

## Muldrotha G - Major Cuts vs `MUL-F`
- `Ancient Tomb`, `Assassin's Trophy`, `Birds of Paradise`, `Bloodstained Mire`, `Bloom Tender`, `Blooming Marsh`, `Botanical Sanctum`, `Chrome Mox`, `City of Brass`, `Darkslick Shores`, `Dauthi Voidwalker`, `Deathcap Glade`, `Heroic Intervention`, `Lightning Greaves`, `Mana Confluence`, `Mana Drain`, `Mana Vault`, `Marsh Flats`, `Morphic Pool`, `Nature's Claim`, `Reflecting Pool`, `Rejuvenating Springs`, `Scalding Tarn`, `Talisman of Curiosity`, `Talisman of Dominance`, `Undergrowth Stadium`, `Windswept Heath`, `Wooded Foothills`

## Teval G - Shell Notes
- This shell keeps Teval's strongest commander-native engine (`Field of the Dead` + land recursion) but pivots off the `Glacial Chasm` lock axis.
- `Mox Diamond` is the replacement GC that shifts the deck from lock pressure to speed compression and explosive landfall turns.
- Land-ramp sorcery density (`Explore`, `Farseek`, `Cultivate`, `Tempt with Discovery`) is intentionally higher than prior Teval builds to support fast Field/Scute conversion.
- Utility denial is capped at a single slot (`Strip Mine`) to avoid falling back into `TEV-E/F` lock identity.

## Teval G - Major Adds vs `TEV-F`
- `Aesi, Tyrant of Gyre Strait`, `Cultivate`, `Explore`, `Farseek`, `Fetid Pools`, `Flooded Strand`, `Forest`, `Insidious Roots`, `Island`, `Kodama of the East Tree`, `Llanowar Wastes`, `Lotus Petal`, `Lotus Vale`, `Mox Diamond`, `Path of Discovery`, `Rites of Flourishing`, `Sakura-Tribe Elder`, `Sensei's Divining Top`, `Shifting Woodland`, `Sunken Hollow`, `Tatyova, Benthic Druid`, `Tempt with Discovery`, `Tireless Tracker`, `Underground River`, `Undiscovered Paradise`, `Wayward Swordtooth`, `Yavimaya Coast`

## Teval G - Major Cuts vs `TEV-F`
- `Assassin's Trophy`, `Beast Within`, `Bloodstained Mire`, `Bloom Tender`, `Botanical Sanctum`, `Deathcap Glade`, `Deathrite Shaman`, `Dreamroot Cascade`, `Eternal Witness`, `Ghost Quarter`, `Glacial Chasm`, `Lightning Greaves`, `Mana Drain`, `Morphic Pool`, `Nature's Claim`, `Reflecting Pool`, `Regrowth`, `Rejuvenating Springs`, `Satyr Wayfinder`, `Seal of Primordium`, `Talisman of Curiosity`, `Talisman of Dominance`, `Talisman of Resilience`, `Three Visits`, `Undergrowth Stadium`, `Wasteland`, `Windswept Heath`

## Rejected / Excluded (By Design)
- `MUL-G` excludes `Ancient Tomb`, `Mana Vault`, `Chrome Mox`, `The One Ring`, `Force of Will`, `Fierce Guardianship`, `Mox Diamond`, and `Seedborn Muse` to avoid collapsing into previous shells or breaking the GC cap.
- `TEV-G` excludes `Glacial Chasm`, `Ancient Tomb`, `Mana Vault`, `Chrome Mox`, `Rhystic Study`, `Cyclonic Rift`, and `Fierce Guardianship` to keep the shell off both the Chasm-lock and generic-control identities.
- `Primeval Titan` remains excluded as Commander-banned despite being present in the pool.
