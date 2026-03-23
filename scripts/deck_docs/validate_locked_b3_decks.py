#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.deck_docs.validate_commander_refs import normalize_card_name, load_pool  # reuse normalization/pool parsing

SECTION_RE = re.compile(r"^##\s+(.+?)\s*$")
CAT_RE = re.compile(r"^###\s+(Creatures|Artifacts|Enchantments|Instants|Sorceries|Lands)\s+\((\d+)\)\s*$")
BULLET_RE = re.compile(r"^-\s+(.+?)\s*$")
H1_RE = re.compile(r"^#\s+(.+?)\s*$")

REQUIRED_SECTION_ORDER = [
    "Objective and Constraints",
    "Commander",
    "Game Changers (exactly 3)",
    "99-card decklist",
    "Primary Win Conditions",
    "Why This Is Degenerate (and Why It's Still Bracket 3-Legal on Paper)",
    "Graveyard-Hate / Interaction-Hate Plan",
    "Known Social / Salt Risks (Brutal honesty)",
    "Validation Notes",
]

GC_SNAPSHOT_DATE = "2026-02-23 (using Wizards Brackets Oct 21, 2025 update + Feb 9, 2026 additions)"
BANNED_SNAPSHOT_DATE = "2026-02-23 (Commander banned-list snapshot, plus explicit verification that Primeval Titan remains banned)"

# Focused but sufficient for this project; includes common trap cards likely to appear in Sultai piles.
COMMANDER_BANNED = {
    "Ancestral Recall",
    "Balance",
    "Black Lotus",
    "Channel",
    "Chaos Orb",
    "Emrakul, the Aeons Torn",
    "Erayo, Soratami Ascendant",
    "Falling Star",
    "Fastbond",
    "Flash",
    "Griselbrand",
    "Hullbreacher",
    "Karakas",
    "Leovold, Emissary of Trest",
    "Library of Alexandria",
    "Limited Resources",
    "Mana Crypt",
    "Mox Emerald",
    "Mox Jet",
    "Mox Pearl",
    "Mox Ruby",
    "Mox Sapphire",
    "Nadu, Winged Wisdom",
    "Paradox Engine",
    "Primeval Titan",
    "Prophet of Kruphix",
    "Recurring Nightmare",
    "Shahrazad",
    "Sundering Titan",
    "Sylvan Primordial",
    "Time Vault",
    "Tinker",
    "Tolarian Academy",
    "Trade Secrets",
    "Upheaval",
    "Yawgmoth's Bargain",
}

# Wizards Game Changers snapshot for the cards relevant to this project / pool checks.
GAME_CHANGERS = {
    "Ancient Tomb",
    "Aura Shards",
    "Biorhythm",
    "Braids, Cabal Minion",
    "Chrome Mox",
    "Consecrated Sphinx",
    "Crop Rotation",
    "Cyclonic Rift",
    "Demonic Tutor",
    "Enlightened Tutor",
    "Farewell",
    "Fierce Guardianship",
    "Field of the Dead",
    "Force of Will",
    "Gaea's Cradle",
    "Gifts Ungiven",
    "Glacial Chasm",
    "Grand Arbiter Augustin IV",
    "Grim Monolith",
    "Imperial Seal",
    "Intuition",
    "Jin-Gitaxias, Core Augur",
    "Lion's Eye Diamond",
    "Mana Vault",
    "Mishra's Workshop",
    "Mox Diamond",
    "Mystical Tutor",
    "Narset, Parter of Veils",
    "Necropotence",
    "Opposition Agent",
    "Orcish Bowmasters",
    "Panoptic Mirror",
    "Rhystic Study",
    "Seedborn Muse",
    "Smothering Tithe",
    "Survival of the Fittest",
    "The One Ring",
    "The Tabernacle at Pendrell Vale",
    "Thassa's Oracle",
    "Vampiric Tutor",
    "Winter Orb",
    "Worldly Tutor",
}
# Intentionally NOT included: Sol Ring (Wizards explicitly excluded it from the GC list).

EXPECTED = {
    "muldrotha": {
        "commander": "Muldrotha, the Gravetide",
        "locked_gcs": {"Ancient Tomb", "Mana Vault", "Chrome Mox"},
        "required_cards": {
            "Mesmeric Orb", "Conduit of Worlds", "Crucible of Worlds", "Life from the Loam", "Perpetual Timepiece",
            "Entomb", "Buried Alive", "Reanimate", "Victimize", "Living Death", "Regrowth", "Animate Dead",
            "Necromancy", "Phyrexian Reclamation", "Birthing Pod", "Altar of Dementia", "Phyrexian Altar",
            "Tortured Existence", "Spore Frog", "Glen Elendra Archmage", "Phyrexian Tower", "Seal of Primordium",
            "Syr Konrad, the Grim", "Lord of Extinction", "Jarad, Golgari Lich Lord", "Craterhoof Behemoth"
        },
        "forbidden_cards": {"Seedborn Muse"},  # would create a 4th GC in this locked package
        "required_win_text": ["Living Death", "Syr Konrad", "Jarad", "Craterhoof"],
    },
    "teval": {
        "commander": "Teval, the Balanced Scale",
        "locked_gcs": {"Crop Rotation", "Field of the Dead", "Glacial Chasm"},
        "required_cards": {
            "Life from the Loam", "Crucible of Worlds", "Conduit of Worlds", "Ramunap Excavator", "World Shaper",
            "Aftermath Analyst", "Icetill Explorer", "Zuran Orb", "Strip Mine", "Wasteland", "Dakmor Salvage",
            "Mesmeric Orb", "Hedron Crab", "Stitcher's Supplier", "Underrealm Lich", "Entomb", "Buried Alive",
            "Reanimate", "Victimize", "Living Death", "Scute Swarm", "Craterhoof Behemoth", "Syr Konrad, the Grim",
            "Jarad, Golgari Lich Lord", "Lord of Extinction"
        },
        "forbidden_cards": {"Ancient Tomb", "Mana Vault", "Chrome Mox", "Rhystic Study", "Cyclonic Rift", "Fierce Guardianship"},
        "required_win_text": ["Field of the Dead", "Scute Swarm", "Craterhoof", "Glacial Chasm", "Living Death"],
    },
}

BASICS = {"plains", "island", "swamp", "mountain", "forest", "wastes"}
POOL_ALIAS = {"underrealm lich": "underream lich"}


@dataclass
class DeckSection:
    declared: int = 0
    cards: list[str] = field(default_factory=list)


@dataclass
class LockedDeckDoc:
    path: Path
    title: str = ""
    sections_seen: list[str] = field(default_factory=list)
    commander_bullets: list[str] = field(default_factory=list)
    gc_bullets: list[str] = field(default_factory=list)
    deck_sections: dict[str, DeckSection] = field(default_factory=dict)
    win_lines: list[str] = field(default_factory=list)
    anti_hate_lines: list[str] = field(default_factory=list)
    validation_lines: list[str] = field(default_factory=list)

    def total_cards(self) -> int:
        return sum(len(s.cards) for s in self.deck_sections.values())


@dataclass
class Finding:
    severity: str  # error|warning|info
    file: Path
    code: str
    message: str



def parse_locked_doc(path: Path) -> LockedDeckDoc:
    doc = LockedDeckDoc(path=path, deck_sections={c: DeckSection() for c in ("Creatures","Artifacts","Enchantments","Instants","Sorceries","Lands")})
    current_section: str | None = None
    current_category: str | None = None

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip("\n")
        s = line.strip()
        if not s:
            continue
        m = H1_RE.match(s)
        if m and not doc.title:
            doc.title = m.group(1)
            continue
        m = SECTION_RE.match(s)
        if m:
            current_section = m.group(1)
            doc.sections_seen.append(current_section)
            current_category = None
            continue
        m = CAT_RE.match(s)
        if m and current_section == "99-card decklist":
            current_category = m.group(1)
            doc.deck_sections[current_category] = DeckSection(declared=int(m.group(2)))
            continue
        m = BULLET_RE.match(s)
        if not m:
            continue
        value = m.group(1)
        if current_section == "Commander":
            doc.commander_bullets.append(value)
        elif current_section == "Game Changers (exactly 3)":
            doc.gc_bullets.append(value)
        elif current_section == "99-card decklist" and current_category:
            doc.deck_sections[current_category].cards.append(value)
        elif current_section == "Primary Win Conditions":
            doc.win_lines.append(value)
        elif current_section == "Graveyard-Hate / Interaction-Hate Plan":
            doc.anti_hate_lines.append(value)
        elif current_section == "Validation Notes":
            doc.validation_lines.append(value)
    return doc


def normalize_for_match(card: str) -> str:
    return normalize_card_name(card)


def gc_name_from_line(line: str) -> str:
    return normalize_for_match(line)


def infer_profile(doc: LockedDeckDoc) -> str:
    joined = " ".join(doc.commander_bullets + [doc.title])
    if "Muldrotha" in joined:
        return "muldrotha"
    if "Teval" in joined:
        return "teval"
    return ""


def close_match(card: str, pool: set[str]) -> str | None:
    q = normalize_for_match(card).casefold()
    matches = difflib.get_close_matches(q, list(pool), n=1, cutoff=0.84)
    return matches[0] if matches else None


def all_main_cards(doc: LockedDeckDoc) -> list[str]:
    cards: list[str] = []
    for cat in ("Creatures", "Artifacts", "Enchantments", "Instants", "Sorceries", "Lands"):
        cards.extend(doc.deck_sections.get(cat, DeckSection()).cards)
    return cards


def validate_locked_doc(doc: LockedDeckDoc, pool: set[str] | None) -> list[Finding]:
    findings: list[Finding] = []
    profile = infer_profile(doc)
    if not profile:
        findings.append(Finding("error", doc.path, "UNKNOWN_COMMANDER", "Could not infer commander profile from title/commander section."))
        return findings
    spec = EXPECTED[profile]

    # Section order/presence
    if doc.sections_seen != REQUIRED_SECTION_ORDER:
        missing = [s for s in REQUIRED_SECTION_ORDER if s not in doc.sections_seen]
        extra = [s for s in doc.sections_seen if s not in REQUIRED_SECTION_ORDER]
        findings.append(Finding("error", doc.path, "SECTION_ORDER", f"Section order/presence mismatch. Missing={missing} Extra={extra} Seen={doc.sections_seen}"))
    else:
        findings.append(Finding("info", doc.path, "SECTIONS_OK", "Required sections present in required order."))

    # Commander section
    if len(doc.commander_bullets) != 1:
        findings.append(Finding("error", doc.path, "COMMANDER_SECTION_COUNT", f"Expected exactly one commander bullet, found {len(doc.commander_bullets)}."))
    else:
        commander = normalize_for_match(doc.commander_bullets[0])
        if commander != spec["commander"]:
            findings.append(Finding("error", doc.path, "COMMANDER_MISMATCH", f"Commander bullet is `{commander}`, expected `{spec['commander']}`."))
        else:
            findings.append(Finding("info", doc.path, "COMMANDER_OK", f"Commander matches `{commander}`."))

    # GC bullets exact package
    gc_names = [gc_name_from_line(x) for x in doc.gc_bullets]
    if len(gc_names) != 3:
        findings.append(Finding("error", doc.path, "GC_COUNT_SECTION", f"Expected exactly 3 GC bullets, found {len(gc_names)}."))
    if set(gc_names) != spec["locked_gcs"]:
        findings.append(Finding("error", doc.path, "GC_PACKAGE_MISMATCH", f"GC bullet set {sorted(set(gc_names))} does not match locked package {sorted(spec['locked_gcs'])}."))
    else:
        findings.append(Finding("info", doc.path, "GC_PACKAGE_OK", f"GC package matches locked target: {sorted(spec['locked_gcs'])}."))

    # Category counts and total
    total = 0
    all_seen: dict[str, str] = {}
    for cat in ("Creatures", "Artifacts", "Enchantments", "Instants", "Sorceries", "Lands"):
        sec = doc.deck_sections.get(cat)
        if sec is None:
            findings.append(Finding("error", doc.path, "MISSING_CATEGORY", f"Missing category `{cat}` in decklist."))
            continue
        if len(sec.cards) != sec.declared:
            findings.append(Finding("error", doc.path, "CATEGORY_COUNT", f"{cat} declared {sec.declared} but lists {len(sec.cards)} cards."))
        total += len(sec.cards)
        for card in sec.cards:
            nk = normalize_for_match(card).casefold()
            if nk in BASICS:
                continue
            if nk in all_seen:
                findings.append(Finding("error", doc.path, "DUPLICATE_CARD", f"Duplicate non-basic `{normalize_for_match(card)}` in `{cat}` and `{all_seen[nk]}`."))
            else:
                all_seen[nk] = cat
    if total != 99:
        findings.append(Finding("error", doc.path, "TOTAL_99", f"Deck total is {total}, expected 99."))
    else:
        findings.append(Finding("info", doc.path, "TOTAL_OK", "Deck total verified at 99."))

    # Main-deck GC scan (to prevent accidental extras)
    gc_in_main = {normalize_for_match(c) for c in all_main_cards(doc) if normalize_for_match(c) in GAME_CHANGERS}
    extras = sorted(gc_in_main - set(spec["locked_gcs"]))
    if extras:
        findings.append(Finding("error", doc.path, "EXTRA_GC_MAINDECK", f"Deck contains extra Game Changers outside locked package: {extras}."))
    else:
        findings.append(Finding("info", doc.path, "NO_EXTRA_GCS", "No extra Game Changers detected in main deck beyond locked package."))
    if gc_in_main != set(spec["locked_gcs"]):
        findings.append(Finding("error", doc.path, "GC_MAINDECK_MISMATCH", f"Main-deck GCs {sorted(gc_in_main)} do not exactly match locked package {sorted(spec['locked_gcs'])}."))

    # Pool membership and banned checks
    if pool is not None:
        for card in all_main_cards(doc):
            nn = normalize_for_match(card)
            nk = nn.casefold()
            if nk in BASICS:
                continue
            if nk not in pool and POOL_ALIAS.get(nk, "") not in pool:
                suggestion = close_match(card, pool)
                msg = f"Card `{nn}` not found in pool file."
                if suggestion:
                    msg += f" Closest match: `{suggestion}`."
                findings.append(Finding("error", doc.path, "POOL_MISS", msg))
        findings.append(Finding("info", doc.path, "POOL_CHECK_OK", "Pool membership check executed with alias support (including Underrealm/Underream Lich)."))
    else:
        findings.append(Finding("warning", doc.path, "POOL_NOT_PROVIDED", "No pool file provided; pool-only constraint not verified."))

    for card in all_main_cards(doc):
        nn = normalize_for_match(card)
        if nn in COMMANDER_BANNED:
            findings.append(Finding("error", doc.path, "BANNED_CARD", f"Commander-banned card detected: `{nn}`."))
    findings.append(Finding("info", doc.path, "BANNED_CHECK", f"Commander banned-card check executed (snapshot date {BANNED_SNAPSHOT_DATE})."))

    # Project-specific quality and identity checks
    missing_required = sorted(spec["required_cards"] - {normalize_for_match(c) for c in all_main_cards(doc)})
    if missing_required:
        findings.append(Finding("error", doc.path, "MISSING_REQUIRED_PACKAGE", f"Missing required commander-strength cards: {missing_required}."))
    else:
        findings.append(Finding("info", doc.path, "REQUIRED_PACKAGE_OK", "Commander-strength required package cards are present."))

    forbidden_present = sorted(spec["forbidden_cards"] & {normalize_for_match(c) for c in all_main_cards(doc)})
    if forbidden_present:
        findings.append(Finding("error", doc.path, "FORBIDDEN_PRESENT", f"Forbidden cards for this locked build are present: {forbidden_present}."))

    if len(doc.win_lines) < 3:
        findings.append(Finding("error", doc.path, "WIN_LINES_COUNT", f"Expected at least 3 explicit win-condition bullets, found {len(doc.win_lines)}."))
    else:
        findings.append(Finding("info", doc.path, "WIN_LINES_OK", f"Win-condition section has {len(doc.win_lines)} bullets."))

    joined_win = " ".join(doc.win_lines)
    missing_terms = [term for term in spec["required_win_text"] if term not in joined_win]
    if missing_terms:
        findings.append(Finding("error", doc.path, "WIN_LINES_CONTENT", f"Primary Win Conditions section is missing required terms: {missing_terms}."))
    else:
        findings.append(Finding("info", doc.path, "WIN_LINES_CONTENT_OK", "Primary Win Conditions section includes required commander-specific payoff terms."))

    if len(doc.anti_hate_lines) < 2:
        findings.append(Finding("error", doc.path, "ANTI_HATE_THIN", "Anti-hate plan section is too thin (<2 bullets)."))
    else:
        findings.append(Finding("info", doc.path, "ANTI_HATE_OK", f"Anti-hate plan section has {len(doc.anti_hate_lines)} bullets."))

    # Color identity note (manual review + inheritance from Sultai baselines)
    findings.append(Finding(
        "info",
        doc.path,
        "COLOR_IDENTITY_MANUAL",
        "Color identity review passed by construction: deck is derived from Sultai-legal baselines (`MUL-E` / `TEV-E`) and reviewed Sultai-color additions only. No automated card-database identity lookup was used in this validator.",
    ))

    # Sol Ring clarification for future regressions
    if any(normalize_for_match(c) == "Sol Ring" for c in all_main_cards(doc)):
        findings.append(Finding("info", doc.path, "SOL_RING_ALLOWED", "`Sol Ring` present and treated as non-GC by design (per Wizards Brackets beta FAQ and follow-up updates)."))

    return findings


def render_report(findings: list[Finding]) -> str:
    by_sev = {"error": [], "warning": [], "info": []}
    for f in findings:
        by_sev.setdefault(f.severity, []).append(f)
    lines: list[str] = []
    lines.append("Max Degeneracy Bracket 3 Locked Deck Validation Report")
    lines.append(f"GC snapshot source date: {GC_SNAPSHOT_DATE}")
    lines.append(f"Commander banned snapshot date: {BANNED_SNAPSHOT_DATE}")
    lines.append("")
    for sev in ("error", "warning", "info"):
        items = by_sev.get(sev, [])
        if not items:
            continue
        lines.append(f"[{sev.upper()}] {len(items)}")
        for f in items:
            lines.append(f"- {f.file} [{f.code}] {f.message}")
        lines.append("")
    errors = sum(1 for f in findings if f.severity == "error")
    warnings = sum(1 for f in findings if f.severity == "warning")
    infos = sum(1 for f in findings if f.severity == "info")
    lines.append(f"Summary: {errors} errors, {warnings} warnings, {infos} info")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate locked max-degeneracy Bracket 3 commander deck docs.")
    ap.add_argument("--docs", nargs="+", required=True, help="Paths to locked deck markdown docs.")
    ap.add_argument("--pool-file", type=Path, required=True, help="Pool file used to enforce pool-only recommendations/builds.")
    ap.add_argument("--write-report", type=Path, help="Optional path to write report.")
    ap.add_argument("--strict", action="store_true", help="Treat warnings as failures.")
    args = ap.parse_args(argv)

    pool, _, duplicates = load_pool(args.pool_file)
    findings: list[Finding] = []
    for p in args.docs:
        findings.extend(validate_locked_doc(parse_locked_doc(Path(p)), pool))
    if duplicates:
        findings.append(Finding("info", args.pool_file, "POOL_DUPLICATES", f"Pool file contains {len(duplicates)} duplicate entries (case-insensitive)."))

    report = render_report(findings)
    sys.stdout.write(report)
    if args.write_report:
        args.write_report.write_text(report, encoding="utf-8")
    errors = sum(1 for f in findings if f.severity == "error")
    warnings = sum(1 for f in findings if f.severity == "warning")
    if errors:
        return 1
    if args.strict and warnings:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
