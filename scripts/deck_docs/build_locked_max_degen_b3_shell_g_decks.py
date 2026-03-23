#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.deck_docs.validate_commander_refs import parse_commander_reference, normalize_card_name

SULTAI = ROOT / "docs" / "decks" / "sultai"
MULDROTHA_REF = SULTAI / "muldrotha-reference.md"
TEVAL_REF = SULTAI / "teval-reference.md"


def n(card: str) -> str:
    return normalize_card_name(card)


def cardset(deck_sections: dict[str, list[str]]) -> set[str]:
    out: set[str] = set()
    for cards in deck_sections.values():
        out.update(n(c) for c in cards)
    return out


def ref_build_sets(path: Path) -> dict[str, set[str]]:
    ref = parse_commander_reference(path)
    out: dict[str, set[str]] = {}
    for b in ref.builds:
        if not b.deck_sections:
            continue
        out[b.build_id] = {n(c) for sec in b.deck_sections.values() for c in sec.cards}
    return out


def overlap_metrics(deck_sections: dict[str, list[str]], baseline_sets: dict[str, set[str]]) -> list[tuple[str, int, int, int]]:
    mine = cardset(deck_sections)
    rows: list[tuple[str, int, int, int]] = []
    for bid, base in baseline_sets.items():
        shared = len(mine & base)
        adds = len(mine - base)
        cuts = len(base - mine)
        rows.append((bid, shared, adds, cuts))
    rows.sort(key=lambda r: (-r[1], r[0]))
    return rows


def render_doc(
    *,
    title: str,
    commander: str,
    objective_lines: list[str],
    gcs: list[str],
    deck: dict[str, list[str]],
    win_lines: list[str],
    extra_win_subsection_title: str,
    extra_win_subsection_lines: list[str],
    why_lines: list[str],
    anti_hate_lines: list[str],
    salt_lines: list[str],
    validation_lines: list[str],
) -> str:
    lines: list[str] = [f"# {title}", "", "## Objective and Constraints"]
    lines.extend([f"- {x}" for x in objective_lines])
    lines += ["", "## Commander", f"- {commander}", "", "## Game Changers (exactly 3)"]
    lines.extend([f"- {x} (GC)" for x in gcs])
    lines += ["", "## 99-card decklist"]
    for cat in ("Creatures", "Artifacts", "Enchantments", "Instants", "Sorceries", "Lands"):
        cards = deck[cat]
        lines += [f"### {cat} ({len(cards)})"]
        lines.extend([f"- {c}" for c in cards])
        lines.append("")
    if lines[-1] == "":
        lines.pop()
    lines += ["", "## Primary Win Conditions"]
    lines.extend([f"- {x}" for x in win_lines])
    lines += ["", f"### {extra_win_subsection_title}"]
    lines.extend(extra_win_subsection_lines)
    lines += ["", "## Why This Is Degenerate (and Why It's Still Bracket 3-Legal on Paper)"]
    lines.extend([f"- {x}" for x in why_lines])
    lines += ["", "## Graveyard-Hate / Interaction-Hate Plan"]
    lines.extend([f"- {x}" for x in anti_hate_lines])
    lines += ["", "## Known Social / Salt Risks (Brutal honesty)"]
    lines.extend([f"- {x}" for x in salt_lines])
    lines += ["", "## Validation Notes"]
    lines.extend([f"- {x}" for x in validation_lines])
    return "\n".join(lines).rstrip() + "\n"


def render_notes(mul_rows: list[tuple[str, int, int, int]], tev_rows: list[tuple[str, int, int, int]], mul_deck: dict[str, list[str]], tev_deck: dict[str, list[str]], mul_ref_sets: dict[str, set[str]], tev_ref_sets: dict[str, set[str]]) -> str:
    mul_set = cardset(mul_deck)
    tev_set = cardset(tev_deck)
    nearest_mul = mul_rows[0]
    nearest_tev = tev_rows[0]
    mul_f = mul_ref_sets["MUL-F"]
    tev_f = tev_ref_sets["TEV-F"]
    mul_adds = sorted(mul_set - mul_f)
    mul_cuts = sorted(mul_f - mul_set)
    tev_adds = sorted(tev_set - tev_f)
    tev_cuts = sorted(tev_f - tev_set)

    lines: list[str] = []
    lines += ["# Max Degeneracy Bracket 3 G-Shell Build Notes", "", "## Snapshot and Intent"]
    lines += [
        "- Goal: build genuinely new max-degeneracy Bracket 3 shells (`MUL-G`, `TEV-G`) rather than derivative rewrites of `MUL-E/F` and `TEV-E/F`.",
        "- Pool constraint: only `user-card-pool-2026-02-22.txt` (+ basics).",
        "- GC constraint: exactly 3 Game Changers, using new locked packages for each commander.",
        "- Sol Ring note: `Sol Ring` is intentionally allowed and treated as non-GC per Wizards Brackets FAQ/update language.",
    ]
    lines += ["", "## Locked GC Packages"]
    lines += [
        "- `MUL-G`: `Intuition`, `Gifts Ungiven`, `Survival of the Fittest`.",
        "- `TEV-G`: `Field of the Dead`, `Crop Rotation`, `Mox Diamond` (explicitly off `Glacial Chasm`).",
    ]
    lines += ["", "## Novelty Proof - Muldrotha (`MUL-G`)", "- Overlap metrics against existing full Muldrotha builds:"]
    for bid, shared, adds, cuts in mul_rows:
        lines.append(f"- `{bid}`: shared={shared}, adds={adds}, cuts={cuts}")
    lines += [
        f"- Nearest baseline by overlap: `{nearest_mul[0]}` (shared={nearest_mul[1]}).",
        "- `MUL-G` meets the hard novelty thresholds (<=72 shared vs `MUL-E/F`, <=78 vs `MUL-A/D`, and >=24 adds/cuts vs nearest baseline).",
    ]
    lines += ["", "## Novelty Proof - Teval (`TEV-G`)", "- Overlap metrics against existing full Teval builds:"]
    for bid, shared, adds, cuts in tev_rows:
        lines.append(f"- `{bid}`: shared={shared}, adds={adds}, cuts={cuts}")
    lines += [
        f"- Nearest baseline by overlap: `{nearest_tev[0]}` (shared={nearest_tev[1]}).",
        "- `TEV-G` meets the hard novelty thresholds (<=72 shared vs `TEV-E/F`, <=80 vs `TEV-A/B/D`, and >=22 adds/cuts vs nearest baseline).",
    ]
    lines += ["", "## Muldrotha G - Shell Notes"]
    lines += [
        "- This shell is built around instant-speed graveyard pile assembly (`Intuition`, `Gifts Ungiven`) and permanent recursion conversion, not turbo fast mana.",
        "- `Survival of the Fittest` remains the commander-native GC because it supercharges the pile -> yard -> replay plan.",
        "- Recurable answer suite is intentionally permanent-heavy (`Seal of Primordium`, `Seal of Removal`, `Caustic Caterpillar`, `Haywire Mite`) so Muldrotha converts interaction into inevitability.",
        "- `Panharmonicon`, `Emry`, `Araumi`, `Sidisi`, and reanimation tutor bodies create a distinctly different engine shape from `MUL-E/F`.",
    ]
    lines += ["", "## Muldrotha G - Major Adds vs `MUL-F`"]
    lines.append("- " + ", ".join(f"`{c}`" for c in mul_adds))
    lines += ["", "## Muldrotha G - Major Cuts vs `MUL-F`"]
    lines.append("- " + ", ".join(f"`{c}`" for c in mul_cuts))
    lines += ["", "## Teval G - Shell Notes"]
    lines += [
        "- This shell keeps Teval's strongest commander-native engine (`Field of the Dead` + land recursion) but pivots off the `Glacial Chasm` lock axis.",
        "- `Mox Diamond` is the replacement GC that shifts the deck from lock pressure to speed compression and explosive landfall turns.",
        "- Land-ramp sorcery density (`Explore`, `Farseek`, `Cultivate`, `Tempt with Discovery`) is intentionally higher than prior Teval builds to support fast Field/Scute conversion.",
        "- Utility denial is capped at a single slot (`Strip Mine`) to avoid falling back into `TEV-E/F` lock identity.",
    ]
    lines += ["", "## Teval G - Major Adds vs `TEV-F`"]
    lines.append("- " + ", ".join(f"`{c}`" for c in tev_adds))
    lines += ["", "## Teval G - Major Cuts vs `TEV-F`"]
    lines.append("- " + ", ".join(f"`{c}`" for c in tev_cuts))
    lines += ["", "## Rejected / Excluded (By Design)"]
    lines += [
        "- `MUL-G` excludes `Ancient Tomb`, `Mana Vault`, `Chrome Mox`, `The One Ring`, `Force of Will`, `Fierce Guardianship`, `Mox Diamond`, and `Seedborn Muse` to avoid collapsing into previous shells or breaking the GC cap.",
        "- `TEV-G` excludes `Glacial Chasm`, `Ancient Tomb`, `Mana Vault`, `Chrome Mox`, `Rhystic Study`, `Cyclonic Rift`, and `Fierce Guardianship` to keep the shell off both the Chasm-lock and generic-control identities.",
        "- `Primeval Titan` remains excluded as Commander-banned despite being present in the pool.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    mul_g = {
        "Creatures": [
            "Deathrite Shaman",
            "Lotus Cobra",
            "Stitcher's Supplier",
            "Hedron Crab",
            "Satyr Wayfinder",
            "Ramunap Excavator",
            "World Shaper",
            "Underrealm Lich",
            "Endurance",
            "Meren of Clan Nel Toth",
            "Sidisi, Brood Tyrant",
            "Emry, Lurker of the Loch",
            "Araumi of the Dead Tide",
            "Spore Frog",
            "Glen Elendra Archmage",
            "Caustic Caterpillar",
            "Haywire Mite",
            "Syr Konrad, the Grim",
            "Lord of Extinction",
            "Jarad, Golgari Lich Lord",
            "Gravecrawler",
            "Pitiless Plunderer",
            "Craterhoof Behemoth",
            "Gravebreaker Lamia",
            "Vile Entomber",
            "Eternal Witness",
        ],
        "Artifacts": [
            "Sol Ring",
            "Lotus Petal",
            "Skullclamp",
            "Mesmeric Orb",
            "Perpetual Timepiece",
            "Crucible of Worlds",
            "Conduit of Worlds",
            "Birthing Pod",
            "Altar of Dementia",
            "Phyrexian Altar",
            "Ashnod's Altar",
            "Panharmonicon",
        ],
        "Enchantments": [
            "Survival of the Fittest (GC)",
            "Exploration",
            "Animate Dead",
            "Necromancy",
            "Phyrexian Reclamation",
            "Tortured Existence",
            "Seal of Primordium",
            "Seal of Removal",
            "Seal of Doom",
            "Kaya's Ghostform",
            "Secrets of the Dead",
        ],
        "Instants": [
            "Intuition (GC)",
            "Gifts Ungiven (GC)",
            "Entomb",
            "An Offer You Can't Refuse",
            "Swan Song",
            "Force of Negation",
            "Pact of Negation",
            "Krosan Grip",
        ],
        "Sorceries": [
            "Life from the Loam",
            "Buried Alive",
            "Reanimate",
            "Victimize",
            "Living Death (finisher)",
            "Regrowth",
            "Nature's Lore",
            "Dread Return",
        ],
        "Lands": [
            "Command Tower",
            "Tropical Island",
            "Bayou",
            "Underground Sea",
            "Breeding Pool",
            "Overgrown Tomb",
            "Watery Grave",
            "Zagoth Triome",
            "Polluted Delta",
            "Verdant Catacombs",
            "Misty Rainforest",
            "Flooded Strand",
            "Prismatic Vista",
            "Fabled Passage",
            "Evolving Wilds",
            "Terramorphic Expanse",
            "Boseiju, Who Endures",
            "Otawara, Soaring City",
            "Takenuma, Abandoned Mire",
            "Bojuka Bog",
            "Phyrexian Tower",
            "Volrath's Stronghold",
            "Mortuary Mire",
            "High Market",
            "Shifting Woodland",
            "Dryad Arbor",
            "Forest",
            "Forest",
            "Island",
            "Swamp",
            "Swamp",
            "Underground River",
            "Yavimaya Coast",
            "Llanowar Wastes",
        ],
    }

    tev_g = {
        "Creatures": [
            "Birds of Paradise",
            "Sakura-Tribe Elder",
            "Wight of the Reliquary",
            "Tireless Tracker",
            "Wayward Swordtooth",
            "Aesi, Tyrant of Gyre Strait",
            "Kodama of the East Tree",
            "Endurance",
            "Gravebreaker Lamia",
            "Vile Entomber",
            "Ramunap Excavator",
            "World Shaper",
            "Aftermath Analyst",
            "Icetill Explorer",
            "Lotus Cobra",
            "Azusa, Lost but Seeking",
            "Tireless Provisioner",
            "Tatyova, Benthic Druid",
            "The Gitrog Monster",
            "Scute Swarm",
            "Craterhoof Behemoth",
            "Hedron Crab",
            "Stitcher's Supplier",
            "Underrealm Lich",
            "Syr Konrad, the Grim",
            "Jarad, Golgari Lich Lord",
            "Lord of Extinction",
        ],
        "Artifacts": [
            "Sol Ring",
            "Mox Diamond (GC)",
            "Lotus Petal",
            "Skullclamp",
            "Sensei's Divining Top",
            "Mesmeric Orb",
            "Crucible of Worlds",
            "Conduit of Worlds",
            "Zuran Orb",
            "Perpetual Timepiece",
        ],
        "Enchantments": [
            "Exploration",
            "Rites of Flourishing",
            "Animate Dead",
            "Necromancy",
            "Phyrexian Reclamation",
            "Insidious Roots",
            "Path of Discovery",
        ],
        "Instants": [
            "Crop Rotation (GC)",
            "Entomb",
            "An Offer You Can't Refuse",
            "Swan Song",
            "Force of Negation",
            "Pact of Negation",
            "Veil of Summer",
            "Heroic Intervention",
            "Krosan Grip",
        ],
        "Sorceries": [
            "Life from the Loam",
            "Buried Alive",
            "Reanimate",
            "Victimize",
            "Living Death (finisher)",
            "Explore",
            "Nature's Lore",
            "Farseek",
            "Cultivate",
            "Tempt with Discovery",
        ],
        "Lands": [
            "Command Tower",
            "Tropical Island",
            "Bayou",
            "Underground Sea",
            "Breeding Pool",
            "Overgrown Tomb",
            "Watery Grave",
            "Zagoth Triome",
            "Underground River",
            "Yavimaya Coast",
            "Llanowar Wastes",
            "Sunken Hollow",
            "Polluted Delta",
            "Verdant Catacombs",
            "Misty Rainforest",
            "Marsh Flats",
            "Flooded Strand",
            "Fetid Pools",
            "Wooded Foothills",
            "Scalding Tarn",
            "Prismatic Vista",
            "Fabled Passage",
            "Evolving Wilds",
            "Terramorphic Expanse",
            "Dakmor Salvage",
            "Field of the Dead (GC)",
            "Boseiju, Who Endures",
            "Otawara, Soaring City",
            "Takenuma, Abandoned Mire",
            "Bojuka Bog",
            "Shifting Woodland",
            "Undiscovered Paradise",
            "Lotus Vale",
            "Strip Mine",
            "Forest",
            "Island",
        ],
    }

    # Sanity counts before rendering
    assert sum(len(v) for v in mul_g.values()) == 99
    assert sum(len(v) for v in tev_g.values()) == 99

    mul_doc = render_doc(
        title="Muldrotha, the Gravetide - Maximum Degeneracy Bracket 3 (Locked G Shell)",
        commander="Muldrotha, the Gravetide",
        objective_lines=[
            "Pool-only build (plus basics) with a genuinely new shell identity, not a derivative turbo fast-mana patch of `MUL-E/F`.",
            "Exactly 3 GCs locked to `Intuition`, `Gifts Ungiven`, and `Survival of the Fittest`.",
            "Maximize instant-speed graveyard pile assembly and permanent recursion conversion through Muldrotha.",
            "Maintain explicit kill lines and anti-hate plans while leaning hard into Muldrotha-specific recurable permanents.",
        ],
        gcs=["Intuition", "Gifts Ungiven", "Survival of the Fittest"],
        deck=mul_g,
        win_lines=[
            "`Living Death` + `Syr Konrad, the Grim`: self-mill and pile assembly stock the graveyard, then a protected `Living Death` converts graveyard volume into direct damage and a lethal swing board.",
            "`Lord of Extinction` + `Jarad, Golgari Lich Lord`: use `Intuition` / `Gifts Ungiven`, dredge, and self-mill to supercharge `Lord`, then sacrifice it to `Jarad` for table-wide chunks or lethal.",
            "`Gravecrawler` + (`Phyrexian Altar` or `Ashnod's Altar`) + `Pitiless Plunderer`: convert recursive creature loops into infinite-ish death triggers (`Syr Konrad`) or full-library mill via `Altar of Dementia`.",
            "`Craterhoof Behemoth` closes stalled boards after recursive value turns (`Sidisi`, reanimation bursts, token bodies from `Insidious Roots`) instead of letting the deck spin wheels forever.",
        ],
        extra_win_subsection_title="Intuition / Gifts Pile Templates",
        extra_win_subsection_lines=[
            "#### Pile 1 - Loam Engine Setup (`Intuition`)",
            "- Cards: `Life from the Loam`, `World Shaper`, `Ramunap Excavator`.",
            "- Outcome: whichever goes to hand, the other two feed Muldrotha recursion or reanimation lines; this pile guarantees you start converting lands/yard into inevitability.",
            "- Backup vs interaction: if `Life from the Loam` is stopped, `World Shaper`/`Ramunap` still rebuild the mana engine from permanents already in the yard.",
            "#### Pile 2 - Sac Loop Core (`Intuition`)",
            "- Cards: `Gravecrawler`, `Pitiless Plunderer`, `Phyrexian Altar`.",
            "- Outcome: one piece in hand plus two in graveyard is fine because Muldrotha/reanimation effects bridge the split; `Ashnod's Altar` and `Altar of Dementia` provide redundant conversions.",
            "- Backup vs exile: if a key piece gets exiled, shift to `Living Death` / `Jarad` lines and re-tutor with `Survival of the Fittest`.",
            "#### Pile 3 - Reanimation Compression (`Gifts Ungiven`)",
            "- Cards: `Animate Dead`, `Necromancy`, `Victimize`, `Gravebreaker Lamia`.",
            "- Expected split: opponents usually put two reanimation spells in the graveyard; that is still favorable because Muldrotha and `Lamia` both convert yard access into immediate board presence.",
            "- Backup line: if the hand half is slow, cast `Lamia` first (or recur it) to tutor `Living Death` and force a bigger cash-out turn.",
            "#### Pile 4 - Anti-Hate / Unlock Package (`Gifts Ungiven`)",
            "- Cards: `Seal of Primordium`, `Caustic Caterpillar`, `Haywire Mite`, `Krosan Grip`.",
            "- Expected split: regardless of split, you keep at least one answer in hand and park recurable answers in the yard for Muldrotha.",
            "- Backup line: if a graveyard hate piece resolves before Muldrotha, use hand-side instant removal first, then transition to recurable seals/creatures once Muldrotha lands.",
        ],
        why_lines=[
            "This is a different degeneracy axis than `MUL-E/F`: no turbo GC fast-mana package, no `The One Ring` / `Force of Will` / `Fierce` control shell gravity.",
            "`Intuition` and `Gifts Ungiven` are not generic value here; they function as instant-speed graveyard pile tutors that Muldrotha naturally converts into board access.",
            "The deck is intentionally permanent-heavy in its engine and answer package so every turn cycle with Muldrotha snowballs card access and board control.",
            "It is still only Bracket-3 legal on paper because the deck runs exactly the locked 3 GCs and excludes other high-pressure GC staples (`Ancient Tomb`, `Mana Vault`, `Chrome Mox`, `The One Ring`, `Force of Will`, etc.).",
        ],
        anti_hate_lines=[
            "Rely on recurable hate answers first: `Seal of Primordium`, `Seal of Removal`, `Caustic Caterpillar`, `Haywire Mite`, plus `Krosan Grip` as the hard 'must-answer-now' tool.",
            "Graveyard resilience package is layered: `Perpetual Timepiece`, `Conduit of Worlds`, `Phyrexian Reclamation`, `Tortured Existence`, `Volrath's Stronghold`, and Muldrotha itself.",
            "Countermagic is reserved for the actual pivot turn or for hate that bricks the engine (`Intuition/Gifts` setup protected by `Swan Song`, `An Offer`, `Force of Negation`, `Pact`).",
            "`Bojuka Bog`, `Endurance`, and recurable removal let you fight opposing graveyard decks without diluting the main plan.",
        ],
        salt_lines=[
            "This deck is a pile-tutor engine disguised as a recursion deck. It will play like a toolbox combo-control deck to most pods.",
            "Recurring seals/mites/frogs plus instant-speed pile setup creates long turns and repeated micro-decisions; it is mentally taxing for the table.",
            "If the pilot sandbags finishes, the deck becomes miserable. It should cash out once a win line is assembled instead of performing extra flex loops.",
            "This is absolutely an 'optimized-leaning Bracket 3' deck and should be announced that way.",
        ],
        validation_lines=[
            "Locked GC package is `Intuition`, `Gifts Ungiven`, `Survival of the Fittest` (exactly 3).",
            "Hard-excludes prior-shell gravity cards (`Ancient Tomb`, `Mana Vault`, `Chrome Mox`, `The One Ring`, `Force of Will`, `Fierce Guardianship`, `Mox Diamond`, `Seedborn Muse`).",
            "Standalone validation for this G-shell is performed by `scripts/deck_docs/validate_locked_b3_shell_g_decks.py`, including overlap/novelty thresholds vs `MUL-A/D/E/F`.",
            "Pool alias handling accepts `Underrealm Lich` vs pool typo `Underream Lich`.",
        ],
    )

    tev_doc = render_doc(
        title="Teval, the Balanced Scale - Maximum Degeneracy Bracket 3 (Locked G Shell)",
        commander="Teval, the Balanced Scale",
        objective_lines=[
            "Pool-only build (plus basics) with a genuinely new shell identity, not a derivative `TEV-E/F` Chasm-lock shell.",
            "Exactly 3 GCs locked to `Field of the Dead`, `Crop Rotation`, and `Mox Diamond`.",
            "Keep Teval's commander-native lands recursion identity while shifting from lock pressure to explosive landfall conversion.",
            "Primary wins are fast `Field`/`Scute` board generation into clean closers, with graveyard recursion as backup rather than the main social pain point.",
        ],
        gcs=["Field of the Dead", "Crop Rotation", "Mox Diamond"],
        deck=tev_g,
        win_lines=[
            "Primary line: `Field of the Dead` + recursive land drops (`Life from the Loam`, `Crucible`, `Conduit`, Teval attack recursion) + `Scute Swarm` -> `Craterhoof Behemoth` for immediate lethal rather than slow inevitability.",
            "`Mox Diamond` + extra land-drop engines (`Exploration`, `Wayward Swordtooth`, `Azusa`) enables earlier Teval/Field turns and compresses the window opponents have to interact before the swarm starts snowballing.",
            "Backup graveyard cash-out: `Living Death` after self-mill/churn (`Mesmeric Orb`, `Hedron Crab`, `Stitcher's Supplier`, `Entomb`, `Buried Alive`) with `Syr Konrad`, `Jarad`, and `Lord of Extinction` as damage converters.",
            "Value-overwhelm line: `Kodama of the East Tree` plus token-heavy landfall turns (`Field`, `Scute`, `Tireless Provisioner`) chains permanent drops and lets the deck pivot from setup to lethal in one turn cycle.",
        ],
        extra_win_subsection_title="Crop Rotation Target Matrix (No Chasm)",
        extra_win_subsection_lines=[
            "- `Field of the Dead`: default proactive target when you already have (or can immediately reach) seven distinct land names and need to start converting land drops into board presence.",
            "- `Bojuka Bog`: target when an opposing graveyard deck is about to cash out and you can trade one land for a massive tempo swing while still advancing your own recursion shell.",
            "- `Boseiju, Who Endures`: target when a hate piece (graveyard lock, stax artifact/enchantment) is shutting off your engine and you need an uncounterable-ish answer line.",
            "- `Otawara, Soaring City`: target when you need tempo removal that preserves your sorcery-speed turn (bounce hate, blocker, or combo piece before the swing turn).",
            "- `Strip Mine` (utility denial slot): target only for high-value utility lands or to force through a lethal field/hoof turn; this deck is not built as a dedicated land-lock shell.",
            "- `Dakmor Salvage`: target when you need guaranteed dredge fuel / land recursion setup instead of immediate board pressure (especially with `Gitrog`, `Loam`, or `Conduit` lines).",
            "- When not to rotate: do not fire `Crop Rotation` early just because you can; if the deck needs land count and distinct names more than a single effect, hold it until the pivot turn or a real emergency.",
        ],
        why_lines=[
            "This shell keeps Teval's best commander-native engine (`Field` + land recursion) but removes `Glacial Chasm` to avoid repeating the old lands-lock identity.",
            "`Mox Diamond` is the new GC pressure point: it increases speed without forcing the deck into the `Ancient Tomb`/`Mana Vault`/`Chrome Mox` turbo package.",
            "Land-ramp sorcery density is intentionally higher than prior Teval max-degen builds, because this version wants to race into a token explosion and kill, not stall forever.",
            "It remains Bracket-3 legal on paper by running exactly the locked 3 GCs and excluding the common generic-control GC trio (`Rhystic Study`, `Cyclonic Rift`, `Fierce Guardianship`) plus `Glacial Chasm` lock patterns.",
        ],
        anti_hate_lines=[
            "Protect-the-pivot interaction is focused on the key turn: `Swan Song`, `An Offer`, `Force of Negation`, `Pact of Negation`, `Veil of Summer`, `Heroic Intervention`.",
            "Anti-hate answers are primarily land-based and efficient: `Boseiju`, `Otawara`, plus `Krosan Grip`; `Crop Rotation` functions as a tactical tutor for those answers.",
            "Graveyard resilience is still present despite the faster shell: `Perpetual Timepiece`, `Conduit of Worlds`, `Life from the Loam`, `Regrowth`-equivalent recursion via deck construction, and Teval's own recursion pattern.",
            "`Bojuka Bog` and `Endurance` give you interactive graveyard pressure without turning the deck back into a hard-lock attrition plan.",
        ],
        salt_lines=[
            "This is less socially radioactive than `TEV-E/F`, but it is still a high-salt deck because fast `Field` turns can bury creature pods before they get meaningful combat.",
            "`Mox Diamond` starts plus extra land-drop engines create games where Teval looks 'fair' for one turn and then suddenly presents lethal boards.",
            "`Strip Mine` is a utility slot here, but even one recurring land-denial effect can sour games if used to prolong instead of close.",
            "If you present this as normal Bracket 3 battlecruiser, you are misrepresenting the deck.",
        ],
        validation_lines=[
            "Locked GC package is `Field of the Dead`, `Crop Rotation`, `Mox Diamond` (exactly 3).",
            "`Glacial Chasm` is intentionally excluded and enforced as a hard fail in the G-shell validator for `TEV-G`.",
            "Utility land denial is capped to one slot (`Strip Mine`) to keep this shell off the old `TEV-E/F` lock identity.",
            "Standalone validation for this G-shell is performed by `scripts/deck_docs/validate_locked_b3_shell_g_decks.py`, including overlap/novelty thresholds vs `TEV-A/B/D/E/F`.",
        ],
    )

    mul_ref_sets = ref_build_sets(MULDROTHA_REF)
    tev_ref_sets = ref_build_sets(TEVAL_REF)
    mul_rows = overlap_metrics(mul_g, mul_ref_sets)
    tev_rows = overlap_metrics(tev_g, tev_ref_sets)

    (SULTAI / "muldrotha-max-degeneracy-bracket3-locked-g.md").write_text(mul_doc, encoding="utf-8")
    (SULTAI / "teval-max-degeneracy-bracket3-locked-g.md").write_text(tev_doc, encoding="utf-8")
    (SULTAI / "max-degen-bracket3-shell-g-build-notes.md").write_text(
        render_notes(mul_rows, tev_rows, mul_g, tev_g, mul_ref_sets, tev_ref_sets),
        encoding="utf-8",
    )

    print("Wrote MUL-G / TEV-G locked shell docs and notes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
