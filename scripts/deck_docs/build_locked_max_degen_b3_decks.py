#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.deck_docs.validate_commander_refs import parse_commander_reference, normalize_card_name
SULTAI_DIR = ROOT / "docs" / "decks" / "sultai"
MULDROTHA_REF = SULTAI_DIR / "muldrotha-reference.md"
TEVAL_REF = SULTAI_DIR / "teval-reference.md"


def key(name: str) -> str:
    return normalize_card_name(name).casefold()


def remove_cards(build, category: str, names: list[str]) -> None:
    remove_keys = {key(n) for n in names}
    build.deck_sections[category].cards = [c for c in build.deck_sections[category].cards if key(c) not in remove_keys]


def add_cards(build, category: str, names: list[str]) -> None:
    build.deck_sections[category].cards.extend(names)


def render_deck_doc(*, title: str, commander: str, objective_lines: list[str], gc_cards: list[str], deck_sections, win_lines: list[str], why_lines: list[str], anti_hate_lines: list[str], social_lines: list[str], validation_lines: list[str]) -> str:
    lines: list[str] = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append("## Objective and Constraints")
    for line in objective_lines:
        lines.append(f"- {line}")
    lines.append("")
    lines.append("## Commander")
    lines.append(f"- {commander}")
    lines.append("")
    lines.append("## Game Changers (exactly 3)")
    for gc in gc_cards:
        lines.append(f"- {gc} (GC)")
    lines.append("")
    lines.append("## 99-card decklist")
    for category in ("Creatures", "Artifacts", "Enchantments", "Instants", "Sorceries", "Lands"):
        cards = deck_sections[category]
        lines.append(f"### {category} ({len(cards)})")
        for card in cards:
            lines.append(f"- {card}")
        lines.append("")
    if lines[-1] == "":
        lines.pop()
    lines.append("")
    lines.append("## Primary Win Conditions")
    for line in win_lines:
        lines.append(f"- {line}")
    lines.append("")
    lines.append("## Why This Is Degenerate (and Why It's Still Bracket 3-Legal on Paper)")
    for line in why_lines:
        lines.append(f"- {line}")
    lines.append("")
    lines.append("## Graveyard-Hate / Interaction-Hate Plan")
    for line in anti_hate_lines:
        lines.append(f"- {line}")
    lines.append("")
    lines.append("## Known Social / Salt Risks (Brutal honesty)")
    for line in social_lines:
        lines.append(f"- {line}")
    lines.append("")
    lines.append("## Validation Notes")
    for line in validation_lines:
        lines.append(f"- {line}")
    return "\n".join(lines).rstrip() + "\n"


def render_notes(mul_cuts: dict[str, list[str]], mul_adds: dict[str, list[str]], tev_cuts: dict[str, list[str]], tev_adds: dict[str, list[str]]) -> str:
    lines: list[str] = []
    lines.append("# Max Degeneracy Bracket 3 Build Notes")
    lines.append("")
    lines.append("## Snapshot and Guardrails")
    lines.append("- Date target: 2026-02-23.")
    lines.append("- Pool constraint: only `user-card-pool-2026-02-22.txt` plus basics.")
    lines.append("- Bracket constraint: exactly 3 Game Changers (GCs) per deck, enforced against the Wizards Commander Brackets GC list (Oct 21, 2025 update + Feb 9, 2026 additions).")
    lines.append("- `Sol Ring` is intentionally kept in both decks because Wizards explicitly excluded it from the Game Changers list in the Brackets beta FAQ and subsequent updates.")
    lines.append("")
    lines.append("## Muldrotha - Build Philosophy")
    lines.append("- Baseline: `MUL-E` (turbo GC package) from `muldrotha-reference.md`.")
    lines.append("- Target identity: turbo Muldrotha recursion engine, not generic Sultai fast-mana pile.")
    lines.append("- Upgrades prioritize permanent-based recursion loops, sacrifice outlets, and creature-tutor bodies over fair draw/value cards.")
    lines.append("")
    lines.append("## Muldrotha - Major Adds")
    for cat, cards in mul_adds.items():
        if not cards:
            continue
        lines.append(f"- {cat}: {', '.join(f'`{c}`' for c in cards)}")
    lines.append("")
    lines.append("## Muldrotha - Major Cuts")
    for cat, cards in mul_cuts.items():
        if not cards:
            continue
        lines.append(f"- {cat}: {', '.join(f'`{c}`' for c in cards)}")
    lines.append("")
    lines.append("## Teval - Build Philosophy")
    lines.append("- Baseline: `TEV-E` (Field/Chasm/Crop) from `teval-reference.md`.")
    lines.append("- Target identity: commander-native lands recursion / soft-lock shell with explicit kill conversion (not blue-value soup).")
    lines.append("- Upgrades add landfall acceleration, extra land drops, recursive land utility, and a clean `Craterhoof Behemoth` finish.")
    lines.append("")
    lines.append("## Teval - Major Adds")
    for cat, cards in tev_adds.items():
        if not cards:
            continue
        lines.append(f"- {cat}: {', '.join(f'`{c}`' for c in cards)}")
    lines.append("")
    lines.append("## Teval - Major Cuts")
    for cat, cards in tev_cuts.items():
        if not cards:
            continue
        lines.append(f"- {cat}: {', '.join(f'`{c}`' for c in cards)}")
    lines.append("")
    lines.append("## Rejected / Excluded (Brutal)")
    lines.append("- `Seedborn Muse`: extremely strong in Muldrotha, but it is a GC; including it would break the locked turbo GC package.")
    lines.append("- `The One Ring`, `Survival of the Fittest`, `Force of Will`, `Fierce Guardianship`, `Rhystic Study`, `Cyclonic Rift`, `Demonic Tutor`, `Vampiric Tutor`, `Imperial Seal`, `Mystical Tutor`, `Worldly Tutor`, `Gifts Ungiven`, `Intuition`: all excluded because they are GCs and would exceed the exact 3-GC cap in these locked builds.")
    lines.append("- `Mox Diamond`: excluded despite strong synergy in Teval because it is a Game Changer and would break the locked Field/Chasm/Crop package.")
    lines.append("- `Primeval Titan`: present in the pool but Commander-banned; excluded by rule.")
    lines.append("")
    lines.append("## Social Contract Warning")
    lines.append("- Both decks are built to maximize pressure while remaining technically Bracket 3 legal on paper. They are intentionally miserable for underprepared tables.")
    lines.append("- Muldrotha pressures with recursive engine assembly and resilient cash-out turns; Teval pressures with land denial / Chasm survival / Field inevitability into overrun kills.")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    mul_ref = parse_commander_reference(MULDROTHA_REF)
    tev_ref = parse_commander_reference(TEVAL_REF)
    mul = deepcopy(next(b for b in mul_ref.builds if b.build_id == "MUL-E"))
    tev = deepcopy(next(b for b in tev_ref.builds if b.build_id == "TEV-E"))

    mul_cuts = {
        "Creatures": ["Nyx Weaver", "Baleful Strix", "Ledger Shredder", "Accursed Marauder", "Mulldrifter", "Massacre Wurm", "Plaguecrafter", "River Kelpie"],
        "Artifacts": ["Arcane Signet", "Talisman of Resilience", "Swiftfoot Boots", "Soul-Guide Lantern"],
        "Enchantments": [],
        "Instants": ["Noxious Revival", "Counterspell", "Beast Within"],
        "Sorceries": ["Three Visits"],
        "Lands": ["Shipwreck Marsh", "Dreamroot Cascade"],
    }
    mul_adds = {
        "Creatures": ["Satyr Wayfinder", "Caustic Caterpillar", "Haywire Mite", "Spore Frog", "Glen Elendra Archmage", "Pitiless Plunderer", "Gravecrawler", "Gravebreaker Lamia", "Vile Entomber", "Craterhoof Behemoth", "Sidisi, Brood Tyrant"],
        "Artifacts": ["Phyrexian Altar", "Altar of Dementia", "Birthing Pod"],
        "Enchantments": ["Tortured Existence", "Kaya's Ghostform"],
        "Instants": [],
        "Sorceries": [],
        "Lands": ["Phyrexian Tower", "Volrath's Stronghold"],
    }

    for cat, cards in mul_cuts.items():
        remove_cards(mul, cat, cards)
    for cat, cards in mul_adds.items():
        add_cards(mul, cat, cards)

    tev_cuts = {
        "Creatures": ["Baleful Strix", "Plaguecrafter", "Dauthi Voidwalker", "Massacre Wurm", "Nyx Weaver"],
        "Artifacts": ["Arcane Signet", "Soul-Guide Lantern", "Swiftfoot Boots"],
        "Enchantments": ["Secrets of the Dead"],
        "Instants": ["Arcane Denial", "Counterspell", "Noxious Revival"],
        "Sorceries": [],
        "Lands": ["Exotic Orchard", "City of Brass", "Blooming Marsh", "Shipwreck Marsh", "Mana Confluence", "Darkslick Shores"],
    }
    tev_adds = {
        "Creatures": ["Icetill Explorer", "Craterhoof Behemoth", "Vile Entomber", "Lotus Cobra", "Azusa, Lost but Seeking", "Tireless Provisioner", "The Gitrog Monster"],
        "Artifacts": ["Perpetual Timepiece"],
        "Enchantments": [],
        "Instants": ["Heroic Intervention", "Veil of Summer"],
        "Sorceries": [],
        "Lands": ["Boseiju, Who Endures", "Takenuma, Abandoned Mire", "Otawara, Soaring City", "Evolving Wilds", "Bojuka Bog", "Terramorphic Expanse", "Ghost Quarter"],
    }

    for cat, cards in tev_cuts.items():
        remove_cards(tev, cat, cards)
    for cat, cards in tev_adds.items():
        add_cards(tev, cat, cards)

    mul_sections = {cat: mul.deck_sections[cat].cards for cat in ("Creatures", "Artifacts", "Enchantments", "Instants", "Sorceries", "Lands")}
    tev_sections = {cat: tev.deck_sections[cat].cards for cat in ("Creatures", "Artifacts", "Enchantments", "Instants", "Sorceries", "Lands")}

    mul_doc = render_deck_doc(
        title="Muldrotha, the Gravetide - Maximum Degeneracy Bracket 3 (Locked)",
        commander="Muldrotha, the Gravetide",
        objective_lines=[
            "Pool-only build (plus basics if needed; this list does not need basics).",
            "Exactly 3 GCs locked to the turbo package: `Ancient Tomb`, `Mana Vault`, `Chrome Mox`.",
            "Maximize speed compression and recursive inevitability while keeping Muldrotha as the actual engine.",
            "Clear cash-out lines required: reanimation burst, graveyard-size conversion, and combat conversion.",
        ],
        gc_cards=["Ancient Tomb", "Mana Vault", "Chrome Mox"],
        deck_sections=mul_sections,
        win_lines=[
            "`Living Death` + `Syr Konrad, the Grim`: self-mill with `Mesmeric Orb`, `Stitcher's Supplier`, `Hedron Crab`, and tutor bodies (`Buried Alive`, `Vile Entomber`, `Gravebreaker Lamia`), then cash out with a protected `Living Death` for stacked Konrad triggers and immediate swing pressure.",
            "`Lord of Extinction` + `Jarad, Golgari Lich Lord`: fill both graveyards aggressively, land `Lord`, then fling with `Jarad`; Muldrotha recursion lets you replay missing permanent pieces and re-establish the kill after interaction.",
            "`Craterhoof Behemoth` conversion: build a wide board via recursive cheap permanents, `Sidisi, Brood Tyrant` zombie generation, reanimation bursts, and sac-loop rebuilds, then end the game with Hoof instead of durdling.",
            "Loop kill: `Gravecrawler` + `Phyrexian Altar` + `Pitiless Plunderer` (with a Zombie in play, often `Stitcher's Supplier` or a `Sidisi` token) generates effectively infinite death/ETB churn; convert with `Syr Konrad` or mill tables with `Altar of Dementia`.",
        ],
        why_lines=[
            "The deck uses the fastest legal-on-paper Muldrotha GC package (`Ancient Tomb`, `Mana Vault`, `Chrome Mox`) and then spends those tempo gains on recursion engines, not generic blue pile cards.",
            "Permanent density is intentionally high so Muldrotha functions as a multi-type replay engine (artifact, enchantment, creature, land) instead of a value mascot.",
            "The list is Bracket 3-legal on paper because it runs exactly 3 GCs and deliberately excludes additional GC staples (`Force of Will`, `Survival of the Fittest`, `The One Ring`, `Demonic Tutor`, etc.).",
            "In practice, this is still a B4-bleed deck: the fast-mana starts plus recursive combo assembly will feel oppressive in softer pods.",
        ],
        anti_hate_lines=[
            "Graveyard insurance: `Perpetual Timepiece`, `Conduit of Worlds`, `Regrowth`, `Takenuma, Abandoned Mire`, and Muldrotha's replay ability reduce the impact of one-shot graveyard disruption.",
            "Hate-piece removal is intentionally redundant and recurable: `Seal of Primordium`, `Caustic Caterpillar`, `Haywire Mite`, `Krosan Grip`, `Nature's Claim`, `Assassin's Trophy`, `Boseiju, Who Endures`.",
            "Stack protection for cash-out turns: `An Offer You Can't Refuse`, `Swan Song`, `Mana Drain`, `Force of Negation`, `Pact of Negation`, `Heroic Intervention`.",
            "Attrition/hate fallback: `Spore Frog`, `Glen Elendra Archmage`, `Tortured Existence`, and `Phyrexian Reclamation` let the deck keep playing while rebuilding a graveyard-centric finish.",
        ],
        social_lines=[
            "This is not a 'fair graveyard value' Muldrotha list. It is a turbo-recursion shell that will create repeated must-answer turns.",
            "The `Gravecrawler`/altar package plus Muldrotha replay lines can read like combo to many Bracket 3 tables, even without cEDH staples/tutors.",
            "`Spore Frog` + recursion and repeated anti-hate permanents create grind patterns many tables experience as lock-adjacent gameplay.",
            "If the pod expects midrange creature combat, this deck will feel like a rules-lawyered Bracket 4 list wearing a Bracket 3 badge.",
        ],
        validation_lines=[
            "Built from `MUL-E` in `/Users/ng/cc-projects/mtg/docs/decks/sultai/muldrotha-reference.md` with documented cuts/adds in `max-degen-bracket3-build-notes.md`.",
            "Target GC package locked to `Ancient Tomb`, `Mana Vault`, `Chrome Mox` (exactly 3).",
            "`Sol Ring` is included and does not count against the GC cap; Wizards explicitly excluded it from the Game Changers list in the Brackets beta FAQ and reiterated that position in later updates.",
            "Commander legality and pool membership are validated by `validate_locked_b3_decks.py`; `Primeval Titan` is explicitly disallowed even though present in the pool.",
            "Win-condition requirement satisfied (4 documented lines, with multiple lines directly benefiting from Muldrotha recursion sequencing).",
        ],
    )

    tev_doc = render_deck_doc(
        title="Teval, the Balanced Scale - Maximum Degeneracy Bracket 3 (Locked)",
        commander="Teval, the Balanced Scale",
        objective_lines=[
            "Pool-only build (plus basics if needed; this list does not need basics).",
            "Exactly 3 GCs locked to the lands-pressure package: `Crop Rotation`, `Field of the Dead`, `Glacial Chasm`.",
            "Maximize commander-native lands recursion, graveyard churn, and inevitability while keeping explicit kill conversion.",
            "Teval must win as Teval (land recursion and Field/Chasm pressure), not as generic Sultai control-goodstuff.",
        ],
        gc_cards=["Crop Rotation", "Field of the Dead", "Glacial Chasm"],
        deck_sections=tev_sections,
        win_lines=[
            "`Field of the Dead` + fetchlands / `Life from the Loam` / Teval recursion + `Scute Swarm` -> `Craterhoof Behemoth`: this is the cleanest commander-native kill and the primary reason the deck exists.",
            "`Living Death` + graveyard setup (`Mesmeric Orb`, `Hedron Crab`, `Stitcher's Supplier`, `Buried Alive`, `Entomb`) + `Syr Konrad, the Grim` / `Jarad, Golgari Lich Lord` / `Lord of Extinction` provides a second noncombat cash-out path.",
            "`Glacial Chasm` soft-lock survival + land recursion (`Crucible of Worlds`, `Conduit of Worlds`, `Ramunap Excavator`, `Life from the Loam`, `World Shaper`, `Aftermath Analyst`) buys time to build an inevitable token board and end the game on the turn you let Chasm go.",
            "Land-denial attrition (`Strip Mine`, `Wasteland`, `Ghost Quarter`) backed by Teval recursion and `Field of the Dead` bodies can strand opponents while you convert with `Craterhoof`, `Jarad`, or `Konrad` instead of merely prolonging the game.",
        ],
        why_lines=[
            "The locked GC package is maximally commander-native: `Crop Rotation` finds the exact lands engine piece, `Field of the Dead` is the inevitability engine, and `Glacial Chasm` is the survival/tempo distortion axis.",
            "The list pushes land recursion density hard (`Loam`, `Crucible`, `Conduit`, `Ramunap`, `World Shaper`, `Aftermath Analyst`, `Icetill Explorer`) rather than leaning on blue GC staples.",
            "The deck is Bracket 3-legal on paper because it runs exactly the locked 3 GCs and excludes additional GC staples (`Rhystic Study`, `Cyclonic Rift`, `Fierce Guardianship`, `Demonic Tutor`, `Ancient Tomb`, etc.).",
            "In practice it is high-salt and borderline B4 in play pattern: repeated land recursion, Chasm loops, and denial-backed inevitability will feel oppressive.",
        ],
        anti_hate_lines=[
            "Graveyard resilience: `Perpetual Timepiece`, `Conduit of Worlds`, `Regrowth`, `Takenuma, Abandoned Mire`, and recursive land engines make single-shot hate less final than it looks.",
            "Hate-piece answer density is deliberate: `Seal of Primordium`, `Krosan Grip`, `Nature's Claim`, `Assassin's Trophy`, `Beast Within`, `Boseiju, Who Endures`, `Otawara, Soaring City`.",
            "Protect-the-pivot suite is tuned around non-GC stack interaction: `An Offer You Can't Refuse`, `Swan Song`, `Mana Drain`, `Force of Negation`, `Pact of Negation`, `Heroic Intervention`, `Veil of Summer`.",
            "Graveyard-hate back plan exists: `Bojuka Bog`, `Endurance`, and recursive land pressure let you interact on the same axis while preserving your Teval engine.",
        ],
        social_lines=[
            "`Field of the Dead` plus recursive fetch/land loops is already table-warping; adding `Glacial Chasm` makes games feel like they are happening on your timetable only.",
            "This deck can create long 'you are not dead yet but you are not really playing' states if the pilot does not close with `Craterhoof`, `Jarad`, or `Living Death` promptly.",
            "Repeated `Strip Mine` / `Wasteland` / `Ghost Quarter` recursion is legal but will get you targeted or uninvited in casual Bracket 3 pods.",
            "If the table thinks Bracket 3 means battlecruiser synergy, this list will feel openly hostile even though it is technically within the GC cap.",
        ],
        validation_lines=[
            "Built from `TEV-E` in `/Users/ng/cc-projects/mtg/docs/decks/sultai/teval-reference.md` with documented cuts/adds in `max-degen-bracket3-build-notes.md`.",
            "Target GC package locked to `Crop Rotation`, `Field of the Dead`, `Glacial Chasm` (exactly 3).",
            "`Sol Ring` is included and does not count against the GC cap; Wizards explicitly excluded it from the Game Changers list in the Brackets beta FAQ and reiterated that position in later updates.",
            "Pool alias handling allows `Underrealm Lich` to match pool typo `Underream Lich` during validation.",
            "Win-condition requirement satisfied (4 documented lines, including a `Field/Scute -> Craterhoof` line and a `Glacial Chasm` survival-axis line).",
        ],
    )

    (SULTAI_DIR / "muldrotha-max-degeneracy-bracket3-locked.md").write_text(mul_doc, encoding="utf-8")
    (SULTAI_DIR / "teval-max-degeneracy-bracket3-locked.md").write_text(tev_doc, encoding="utf-8")
    (SULTAI_DIR / "max-degen-bracket3-build-notes.md").write_text(render_notes(mul_cuts, mul_adds, tev_cuts, tev_adds), encoding="utf-8")

    print("Wrote locked deck docs and notes to", SULTAI_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
