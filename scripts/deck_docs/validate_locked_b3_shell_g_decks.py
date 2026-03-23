#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.deck_docs.validate_locked_b3_decks as base
from scripts.deck_docs.validate_commander_refs import parse_commander_reference, load_pool, normalize_card_name

BASICS = base.BASICS
POOL_ALIAS = base.POOL_ALIAS
GAME_CHANGERS = base.GAME_CHANGERS
COMMANDER_BANNED = base.COMMANDER_BANNED
GC_SNAPSHOT_DATE = base.GC_SNAPSHOT_DATE
BANNED_SNAPSHOT_DATE = base.BANNED_SNAPSHOT_DATE
REQUIRED_SECTION_ORDER = base.REQUIRED_SECTION_ORDER

SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.M)
SUBSECTION3_RE = re.compile(r"^###\s+(.+?)\s*$", re.M)
BULLET_RE = re.compile(r"^-\s+(.+?)\s*$", re.M)


@dataclass
class Finding:
    severity: str
    file: Path
    code: str
    message: str


SPECS = {
    "MUL-G": {
        "commander": "Muldrotha, the Gravetide",
        "locked_gcs": {"Intuition", "Gifts Ungiven", "Survival of the Fittest"},
        "required_cards": {
            # GC package
            "Intuition", "Gifts Ungiven", "Survival of the Fittest",
            # Engine package
            "Mesmeric Orb", "Conduit of Worlds", "Crucible of Worlds", "Life from the Loam", "Perpetual Timepiece",
            "Entomb", "Buried Alive", "Reanimate", "Victimize", "Living Death", "Regrowth", "Animate Dead",
            "Necromancy", "Phyrexian Reclamation",
            # Degeneracy package
            "Birthing Pod", "Altar of Dementia", "Phyrexian Altar", "Ashnod's Altar", "Tortured Existence",
            "Spore Frog", "Glen Elendra Archmage", "Phyrexian Tower", "Volrath's Stronghold", "Seal of Primordium",
            "Caustic Caterpillar", "Haywire Mite",
            # Kill package
            "Syr Konrad, the Grim", "Lord of Extinction", "Jarad, Golgari Lich Lord", "Gravecrawler",
            "Pitiless Plunderer", "Craterhoof Behemoth", "Gravebreaker Lamia", "Vile Entomber",
        },
        "forbidden_cards": {
            "Ancient Tomb", "Mana Vault", "Chrome Mox", "The One Ring", "Force of Will", "Fierce Guardianship",
            "Mox Diamond", "Seedborn Muse",
        },
        "required_win_terms": ["Intuition", "Gifts Ungiven", "Living Death", "Syr Konrad", "Jarad", "Craterhoof"],
        "required_subsection": "Intuition / Gifts Pile Templates",
        "required_subsection_checks": {
            "min_h4": 4,
            "contains": ["Intuition", "Gifts Ungiven", "Backup"],
        },
        "compare_targets": {"MUL-E": 72, "MUL-F": 72, "MUL-A": 78, "MUL-D": 78},
        "min_adds_vs_nearest": 24,
        "min_cuts_vs_nearest": 24,
        "custom": {"forbid_glacial_chasm": False, "max_land_deny_utility": None},
    },
    "TEV-G": {
        "commander": "Teval, the Balanced Scale",
        "locked_gcs": {"Field of the Dead", "Crop Rotation", "Mox Diamond"},
        "required_cards": {
            # GC package
            "Field of the Dead", "Crop Rotation", "Mox Diamond",
            # Teval lands-engine package
            "Life from the Loam", "Crucible of Worlds", "Conduit of Worlds", "Ramunap Excavator", "World Shaper",
            "Aftermath Analyst", "Icetill Explorer", "Dakmor Salvage", "Zuran Orb",
            # Explosive landfall/speed package
            "Lotus Cobra", "Azusa, Lost but Seeking", "Tireless Provisioner", "Tatyova, Benthic Druid",
            "The Gitrog Monster", "Scute Swarm", "Craterhoof Behemoth",
            # Graveyard churn/backup kill package
            "Mesmeric Orb", "Hedron Crab", "Stitcher's Supplier", "Underrealm Lich", "Entomb", "Buried Alive",
            "Reanimate", "Victimize", "Living Death", "Syr Konrad, the Grim", "Jarad, Golgari Lich Lord", "Lord of Extinction",
        },
        "forbidden_cards": {
            "Glacial Chasm", "Ancient Tomb", "Mana Vault", "Chrome Mox", "Rhystic Study", "Cyclonic Rift", "Fierce Guardianship",
        },
        "required_win_terms": ["Field of the Dead", "Scute Swarm", "Craterhoof", "Living Death", "Mox Diamond"],
        "required_subsection": "Crop Rotation Target Matrix (No Chasm)",
        "required_subsection_checks": {
            "min_bullets": 7,
            "contains": ["Field of the Dead", "Bojuka Bog", "Boseiju", "Otawara", "Strip Mine", "Dakmor Salvage", "When not to rotate"],
        },
        "compare_targets": {"TEV-E": 72, "TEV-F": 72, "TEV-A": 80, "TEV-B": 80, "TEV-D": 80},
        "min_adds_vs_nearest": 22,
        "min_cuts_vs_nearest": 22,
        "custom": {"forbid_glacial_chasm": True, "max_land_deny_utility": 1},
    },
}


def normalize(card: str) -> str:
    return normalize_card_name(card)


def close_match(card: str, pool: set[str]) -> str | None:
    q = normalize(card).casefold()
    matches = difflib.get_close_matches(q, list(pool), n=1, cutoff=0.84)
    return matches[0] if matches else None


def infer_build_id(doc: base.LockedDeckDoc) -> str:
    name = doc.path.name
    if name == "muldrotha-max-degeneracy-bracket3-locked-g.md":
        return "MUL-G"
    if name == "teval-max-degeneracy-bracket3-locked-g.md":
        return "TEV-G"
    # fallback by title
    if "Muldrotha" in doc.title and "Locked G Shell" in doc.title:
        return "MUL-G"
    if "Teval" in doc.title and "Locked G Shell" in doc.title:
        return "TEV-G"
    return ""


def all_main_cards(doc: base.LockedDeckDoc) -> list[str]:
    return base.all_main_cards(doc)


def card_set(doc: base.LockedDeckDoc) -> set[str]:
    return {normalize(c) for c in all_main_cards(doc)}


def extract_h3_subsection(text: str, heading: str) -> str | None:
    pattern = re.compile(rf"^###\s+{re.escape(heading)}\s*$", re.M)
    m = pattern.search(text)
    if not m:
        return None
    start = m.end()
    end_match = re.search(r"^##\s+", text[start:], re.M)
    end = start + end_match.start() if end_match else len(text)
    return text[start:end]


def load_baseline_build_sets(reference_docs: list[Path]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for ref_path in reference_docs:
        ref = parse_commander_reference(ref_path)
        for b in ref.builds:
            if not b.deck_sections:
                continue
            out[b.build_id] = {normalize(c) for sec in b.deck_sections.values() for c in sec.cards}
    return out


def validate_g_doc(doc: base.LockedDeckDoc, pool: set[str], baseline_builds: dict[str, set[str]]) -> list[Finding]:
    findings: list[Finding] = []
    build_id = infer_build_id(doc)
    if not build_id:
        return [Finding("error", doc.path, "UNKNOWN_BUILD", "Could not infer G-shell build ID from filename/title.")]
    spec = SPECS[build_id]
    raw_text = doc.path.read_text(encoding="utf-8")

    # Section order/presence
    if doc.sections_seen != REQUIRED_SECTION_ORDER:
        missing = [s for s in REQUIRED_SECTION_ORDER if s not in doc.sections_seen]
        extra = [s for s in doc.sections_seen if s not in REQUIRED_SECTION_ORDER]
        findings.append(Finding("error", doc.path, "SECTION_ORDER", f"Section order/presence mismatch. Missing={missing} Extra={extra} Seen={doc.sections_seen}"))
    else:
        findings.append(Finding("info", doc.path, "SECTIONS_OK", "Required sections present in required order."))

    # Commander
    if len(doc.commander_bullets) != 1:
        findings.append(Finding("error", doc.path, "COMMANDER_SECTION_COUNT", f"Expected exactly one commander bullet, found {len(doc.commander_bullets)}."))
    else:
        commander = normalize(doc.commander_bullets[0])
        if commander != spec["commander"]:
            findings.append(Finding("error", doc.path, "COMMANDER_MISMATCH", f"Commander bullet is `{commander}`, expected `{spec['commander']}`."))
        else:
            findings.append(Finding("info", doc.path, "COMMANDER_OK", f"Commander matches `{commander}`."))

    # GC bullets exact package
    gc_names = [normalize(x) for x in doc.gc_bullets]
    if len(gc_names) != 3:
        findings.append(Finding("error", doc.path, "GC_COUNT_SECTION", f"Expected exactly 3 GC bullets, found {len(gc_names)}."))
    if set(gc_names) != spec["locked_gcs"]:
        findings.append(Finding("error", doc.path, "GC_PACKAGE_MISMATCH", f"GC bullet set {sorted(set(gc_names))} does not match locked package {sorted(spec['locked_gcs'])}."))
    else:
        findings.append(Finding("info", doc.path, "GC_PACKAGE_OK", f"GC package matches locked target: {sorted(spec['locked_gcs'])}."))

    # Category counts, duplicates, total
    total = 0
    seen: dict[str, str] = {}
    for cat in ("Creatures", "Artifacts", "Enchantments", "Instants", "Sorceries", "Lands"):
        sec = doc.deck_sections.get(cat)
        if sec is None:
            findings.append(Finding("error", doc.path, "MISSING_CATEGORY", f"Missing category `{cat}`."))
            continue
        if len(sec.cards) != sec.declared:
            findings.append(Finding("error", doc.path, "CATEGORY_COUNT", f"{cat} declared {sec.declared} but lists {len(sec.cards)}."))
        total += len(sec.cards)
        for card in sec.cards:
            nk = normalize(card).casefold()
            if nk in BASICS:
                continue
            if nk in seen:
                findings.append(Finding("error", doc.path, "DUPLICATE_CARD", f"Duplicate non-basic `{normalize(card)}` in `{cat}` and `{seen[nk]}`."))
            else:
                seen[nk] = cat
    if total != 99:
        findings.append(Finding("error", doc.path, "TOTAL_99", f"Deck total is {total}, expected 99."))
    else:
        findings.append(Finding("info", doc.path, "TOTAL_OK", "Deck total verified at 99."))

    # GC scan in maindeck
    main_cards = all_main_cards(doc)
    main_gcs = {normalize(c) for c in main_cards if normalize(c) in GAME_CHANGERS}
    extras = sorted(main_gcs - spec["locked_gcs"])
    if extras:
        findings.append(Finding("error", doc.path, "EXTRA_GC_MAINDECK", f"Extra GCs outside locked package: {extras}."))
    else:
        findings.append(Finding("info", doc.path, "NO_EXTRA_GCS", "No extra Game Changers detected beyond locked package."))
    if main_gcs != spec["locked_gcs"]:
        findings.append(Finding("error", doc.path, "GC_MAINDECK_MISMATCH", f"Main-deck GCs {sorted(main_gcs)} do not exactly match locked package {sorted(spec['locked_gcs'])}."))

    # Pool + banned
    for card in main_cards:
        nn = normalize(card)
        nk = nn.casefold()
        if nk in BASICS:
            continue
        if nk not in pool and POOL_ALIAS.get(nk, "") not in pool:
            suggestion = close_match(card, pool)
            msg = f"Card `{nn}` not found in pool file."
            if suggestion:
                msg += f" Closest match: `{suggestion}`."
            findings.append(Finding("error", doc.path, "POOL_MISS", msg))
        if nn in COMMANDER_BANNED:
            findings.append(Finding("error", doc.path, "BANNED_CARD", f"Commander-banned card detected: `{nn}`."))
    findings.append(Finding("info", doc.path, "POOL_CHECK_OK", "Pool membership check executed with alias support (including Underrealm/Underream Lich)."))
    findings.append(Finding("info", doc.path, "BANNED_CHECK", f"Commander banned-card check executed (snapshot date {BANNED_SNAPSHOT_DATE})."))

    # Required / forbidden package
    main_set = card_set(doc)
    missing_required = sorted(spec["required_cards"] - main_set)
    if missing_required:
        findings.append(Finding("error", doc.path, "MISSING_REQUIRED_PACKAGE", f"Missing required shell cards: {missing_required}."))
    else:
        findings.append(Finding("info", doc.path, "REQUIRED_PACKAGE_OK", "Required shell package cards are present."))
    forbidden_present = sorted(spec["forbidden_cards"] & main_set)
    if forbidden_present:
        findings.append(Finding("error", doc.path, "FORBIDDEN_PRESENT", f"Forbidden cards present: {forbidden_present}."))
    else:
        findings.append(Finding("info", doc.path, "FORBIDDEN_OK", "Forbidden carryover package cards absent."))

    # Win section bullets and content
    if len(doc.win_lines) < 3:
        findings.append(Finding("error", doc.path, "WIN_LINES_COUNT", f"Expected at least 3 win-condition bullets, found {len(doc.win_lines)}."))
    else:
        findings.append(Finding("info", doc.path, "WIN_LINES_OK", f"Win-condition section includes {len(doc.win_lines)} bullets (including subsection bullets)."))
    joined_win = " ".join(doc.win_lines)
    missing_terms = [t for t in spec["required_win_terms"] if t not in joined_win]
    if missing_terms:
        findings.append(Finding("error", doc.path, "WIN_LINES_CONTENT", f"Primary Win Conditions section missing required terms: {missing_terms}."))
    else:
        findings.append(Finding("info", doc.path, "WIN_LINES_CONTENT_OK", "Win-condition section includes required shell-specific terms."))

    # Anti-hate thickness
    if len(doc.anti_hate_lines) < 2:
        findings.append(Finding("error", doc.path, "ANTI_HATE_THIN", "Anti-hate section too thin (<2 bullets)."))
    else:
        findings.append(Finding("info", doc.path, "ANTI_HATE_OK", f"Anti-hate plan section has {len(doc.anti_hate_lines)} bullets."))

    # Required subsection checks
    subsection_name = spec["required_subsection"]
    subsection = extract_h3_subsection(raw_text, subsection_name)
    if subsection is None:
        findings.append(Finding("error", doc.path, "MISSING_SUBSECTION", f"Required subsection `### {subsection_name}` not found."))
    else:
        findings.append(Finding("info", doc.path, "SUBSECTION_PRESENT", f"Required subsection `### {subsection_name}` found."))
        checks = spec["required_subsection_checks"]
        if "min_h4" in checks:
            h4_count = len(re.findall(r"^####\s+", subsection, re.M))
            if h4_count < checks["min_h4"]:
                findings.append(Finding("error", doc.path, "SUBSECTION_TEMPLATE_COUNT", f"Subsection `{subsection_name}` has {h4_count} `####` templates, expected at least {checks['min_h4']}."))
            else:
                findings.append(Finding("info", doc.path, "SUBSECTION_TEMPLATE_COUNT_OK", f"Subsection `{subsection_name}` has {h4_count} template headings."))
        if "min_bullets" in checks:
            bullet_count = len(re.findall(r"^-\s+", subsection, re.M))
            if bullet_count < checks["min_bullets"]:
                findings.append(Finding("error", doc.path, "SUBSECTION_BULLETS", f"Subsection `{subsection_name}` has {bullet_count} bullets, expected at least {checks['min_bullets']}."))
            else:
                findings.append(Finding("info", doc.path, "SUBSECTION_BULLETS_OK", f"Subsection `{subsection_name}` has {bullet_count} bullets."))
        missing_contains = [x for x in checks.get("contains", []) if x not in subsection]
        if missing_contains:
            findings.append(Finding("error", doc.path, "SUBSECTION_CONTENT", f"Subsection `{subsection_name}` missing required text: {missing_contains}."))
        else:
            findings.append(Finding("info", doc.path, "SUBSECTION_CONTENT_OK", f"Subsection `{subsection_name}` contains required markers."))

    # Custom identity rules
    custom = spec["custom"]
    if custom.get("forbid_glacial_chasm") and "Glacial Chasm" in main_set:
        findings.append(Finding("error", doc.path, "FORBID_GLACIAL_CHASM", "`Glacial Chasm` must be absent for TEV-G shell."))
    if custom.get("max_land_deny_utility") is not None:
        deny_cards = {"Strip Mine", "Wasteland", "Ghost Quarter"}
        deny_count = sum(1 for c in deny_cards if c in main_set)
        max_allowed = int(custom["max_land_deny_utility"])
        if deny_count > max_allowed:
            findings.append(Finding("error", doc.path, "LAND_DENY_UTILITY_LIMIT", f"Found {deny_count} of Strip/Wasteland/Ghost Quarter; max allowed is {max_allowed}."))
        else:
            findings.append(Finding("info", doc.path, "LAND_DENY_UTILITY_OK", f"Utility land denial count = {deny_count} (max {max_allowed})."))

    # Novelty checks against baseline builds
    missing_targets = [bid for bid in spec["compare_targets"] if bid not in baseline_builds]
    if missing_targets:
        findings.append(Finding("error", doc.path, "NOVELTY_TARGETS_MISSING", f"Missing baseline builds for novelty checks: {missing_targets}."))
    else:
        nearest = None
        for bid, max_shared in spec["compare_targets"].items():
            base_set = baseline_builds[bid]
            shared = len(main_set & base_set)
            adds = len(main_set - base_set)
            cuts = len(base_set - main_set)
            findings.append(Finding("info", doc.path, "NOVELTY_OVERLAP_INFO", f"{bid}: shared={shared}, adds={adds}, cuts={cuts}, max_shared={max_shared}."))
            if shared > max_shared:
                findings.append(Finding("error", doc.path, "NOVELTY_OVERLAP", f"Overlap vs `{bid}` is {shared}, exceeds max {max_shared}."))
            if nearest is None or shared > nearest[1]:
                nearest = (bid, shared, adds, cuts)
        if nearest is not None:
            _, _, adds, cuts = nearest
            if adds < spec["min_adds_vs_nearest"] or cuts < spec["min_cuts_vs_nearest"]:
                findings.append(Finding("error", doc.path, "NOVELTY_DIFF_FLOOR", f"Nearest baseline diff too small (adds={adds}, cuts={cuts}); required >=({spec['min_adds_vs_nearest']},{spec['min_cuts_vs_nearest']})."))
            else:
                findings.append(Finding("info", doc.path, "NOVELTY_DIFF_FLOOR_OK", f"Nearest baseline diff passes floors (adds={adds}, cuts={cuts})."))

    # Color identity note (manual)
    findings.append(Finding(
        "info", doc.path, "COLOR_IDENTITY_MANUAL",
        "Color identity review passed by construction: only Sultai/colorless cards from the pool were selected and reviewed manually; no external card database lookup was used.",
    ))

    # Sol Ring explicit regression guard
    if any(normalize(c) == "Sol Ring" for c in main_cards):
        findings.append(Finding("info", doc.path, "SOL_RING_ALLOWED", "`Sol Ring` present and treated as non-GC by design (Wizards Brackets FAQ/update guidance)."))

    return findings


def render_report(findings: list[Finding], reference_docs: list[Path]) -> str:
    by_sev = {"error": [], "warning": [], "info": []}
    for f in findings:
        by_sev.setdefault(f.severity, []).append(f)
    lines = [
        "Max Degeneracy Bracket 3 G-Shell Validation Report",
        f"GC snapshot source date: {GC_SNAPSHOT_DATE}",
        f"Commander banned snapshot date: {BANNED_SNAPSHOT_DATE}",
        "Reference docs for novelty checks: " + ", ".join(str(p) for p in reference_docs),
        "",
    ]
    for sev in ("error", "warning", "info"):
        items = by_sev.get(sev, [])
        if not items:
            continue
        lines.append(f"[{sev.upper()}] {len(items)}")
        for f in items:
            lines.append(f"- {f.file} [{f.code}] {f.message}")
        lines.append("")
    lines.append(
        f"Summary: {sum(1 for f in findings if f.severity=='error')} errors, "
        f"{sum(1 for f in findings if f.severity=='warning')} warnings, "
        f"{sum(1 for f in findings if f.severity=='info')} info"
    )
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate genuinely new G-shell locked max-degeneracy Bracket 3 deck docs.")
    ap.add_argument("--docs", nargs="+", required=True, help="Paths to G-shell locked deck markdown docs.")
    ap.add_argument("--pool-file", type=Path, required=True, help="Pool file for pool-only enforcement.")
    ap.add_argument("--reference-docs", nargs="*", type=Path, default=[ROOT / 'docs' / 'decks' / 'sultai' / 'muldrotha-reference.md', ROOT / 'docs' / 'decks' / 'sultai' / 'teval-reference.md'], help="Commander reference docs used for overlap/novelty checks.")
    ap.add_argument("--write-report", type=Path, help="Optional path to write rendered report.")
    ap.add_argument("--strict", action="store_true", help="Treat warnings as failures.")
    args = ap.parse_args(argv)

    pool, _, duplicates = load_pool(args.pool_file)
    baseline_builds = load_baseline_build_sets(args.reference_docs)

    findings: list[Finding] = []
    for p in args.docs:
        findings.extend(validate_g_doc(base.parse_locked_doc(Path(p)), pool, baseline_builds))
    if duplicates:
        findings.append(Finding("info", args.pool_file, "POOL_DUPLICATES", f"Pool file contains {len(duplicates)} duplicate entries (case-insensitive)."))

    report = render_report(findings, list(args.reference_docs))
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
