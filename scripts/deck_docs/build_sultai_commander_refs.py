#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "docs" / "decks" / "sultai"

CATEGORY_ORDER = ["Creatures", "Artifacts", "Enchantments", "Instants", "Sorceries", "Lands"]
CATEGORY_RE = re.compile(r"^(#{1,6}\s+)?(Creatures|Artifacts|Enchantments|Instants|Sorceries|Lands) \((\d+)\)\s*$")
BULLET_RE = re.compile(r"^\*\s+(.+?)\s*$")
NUMBERED_RE = re.compile(r"^\d+\.\s+(.+?)\s*$")


@dataclass
class DeckBuild:
    build_id: str
    flavor: str
    commander: str
    sources: list[Path]
    status: str
    deck_sections: OrderedDict[str, list[str]] = field(default_factory=OrderedDict)
    gc_cards: list[str] = field(default_factory=list)
    summary_bullets: list[str] = field(default_factory=list)
    swap_bullets: list[str] = field(default_factory=list)
    validation_notes: list[str] = field(default_factory=list)
    source_repairs: list[str] = field(default_factory=list)

    def total_cards(self) -> int:
        return sum(len(v) for v in self.deck_sections.values())


@dataclass
class ValidationFinding:
    severity: str  # error | warning | info
    build_id: str
    message: str


def normalize_whitespace(text: str) -> str:
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    out: list[str] = []
    blank_run = 0
    for line in lines:
        if line == "":
            blank_run += 1
            if blank_run <= 1:
                out.append("")
            continue
        blank_run = 0
        out.append(line)
    while out and out[-1] == "":
        out.pop()
    return "\n".join(out) + "\n"


def cleanup_markdown_files(directory: Path) -> list[Path]:
    changed: list[Path] = []
    for path in sorted(directory.glob("*.md")):
        original = path.read_text(encoding="utf-8")
        cleaned = normalize_whitespace(original)
        if cleaned != original:
            path.write_text(cleaned, encoding="utf-8")
            changed.append(path)
    return changed


def strip_ref_links(s: str) -> str:
    s = re.sub(r"\s*\(\[[^\]]+\]\[[^\]]+\]\)", "", s)
    s = re.sub(r"\s*\[[^\]]+\]\[[^\]]+\]", "", s)
    return s.strip()


def strip_markdown_inline(s: str) -> str:
    s = s.replace("**", "").replace("*", "")
    return strip_ref_links(s)


def normalize_card_name(name: str) -> str:
    s = strip_markdown_inline(name)
    s = re.sub(r"\s*\((?:GC|gc|FINISHER[^)]*|finisher[^)]*|graveyard-hate / anti-hate tool|anti-exile / yard insurance|remove hate pieces|not a GC|explicitly not a GC|primary cash-out finisher|primary cash-out|graveyard-hate / anti-hate tool)\)\s*$", "", s)
    s = re.sub(r"\s*\((?:GC|gc)\)\s*$", "", s)
    s = re.sub(r"\s*\([^)]*finisher[^)]*\)\s*$", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def extract_lines_between(text: str, start_pat: str, end_pat: str | None = None) -> list[str]:
    lines = text.splitlines()
    start_idx = None
    for i, line in enumerate(lines):
        if re.search(start_pat, line):
            start_idx = i
            break
    if start_idx is None:
        return []
    end_idx = len(lines)
    if end_pat:
        for i in range(start_idx + 1, len(lines)):
            if re.search(end_pat, lines[i]):
                end_idx = i
                break
    return lines[start_idx:end_idx]


def parse_structured_deck(path: Path, commander: str) -> OrderedDict[str, list[str]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    current_cat: str | None = None
    sections: OrderedDict[str, list[str]] = OrderedDict()
    for line in lines:
        m = re.match(r"^##\s+(Creatures|Artifacts|Enchantments|Instants|Sorceries|Lands) \((\d+)\)\s*$", line.strip())
        if m:
            current_cat = m.group(1)
            sections[current_cat] = []
            continue
        if line.strip().startswith("## ") and current_cat:
            current_cat = None
            continue
        if not current_cat:
            continue
        s = line.strip()
        if not s:
            continue
        if s.startswith("✅"):
            current_cat = None
            continue
        if s.startswith("---") or s.startswith("# "):
            current_cat = None
            continue
        bm = BULLET_RE.match(s)
        if bm:
            item = bm.group(1).strip()
            sections[current_cat].append(item)
            continue
        nm = NUMBERED_RE.match(s)
        if nm:
            item = nm.group(1).strip()
            sections[current_cat].append(item)
            continue
        # plain line deck item style (muldrotha-3)
        if s.startswith("[") and s.endswith("]"):
            continue
        if ":" in s:
            current_cat = None
            continue
        if s.startswith(("(", "If ", "This ", "That ", "You ", "Lower ")):
            current_cat = None
            continue
        sections[current_cat].append(s)
    return sections


def parse_chat_deck(path: Path, start_marker: str | None = None, end_marker: str | None = None) -> tuple[str | None, OrderedDict[str, list[str]], dict[str, int]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    start_idx = 0
    end_idx = len(lines)
    if start_marker is not None:
        for i, line in enumerate(lines):
            if start_marker in line:
                start_idx = i
                break
    if end_marker is not None:
        for i in range(start_idx + 1, len(lines)):
            if end_marker in lines[i]:
                end_idx = i
                break
    deck_lines = lines[start_idx:end_idx]
    commander_name: str | None = None
    sections: OrderedDict[str, list[str]] = OrderedDict()
    declared: dict[str, int] = {}
    current_cat: str | None = None
    expecting_commander = False
    for raw in deck_lines:
        s = raw.strip()
        if not s:
            continue
        if s == "Commander (1)":
            expecting_commander = True
            current_cat = None
            continue
        if expecting_commander:
            if s in {"Main Deck (99)", "Locked 99", "99-card main deck (plus commander)"}:
                continue
            if s.startswith("Creatures ("):
                expecting_commander = False
            elif not s.endswith(":") and not s.startswith(("Here’s", "Commander reference")):
                commander_name = s
                expecting_commander = False
                continue
        m = re.match(r"^(Creatures|Artifacts|Enchantments|Instants|Sorceries|Lands) \((\d+)\)$", s)
        if m:
            current_cat = m.group(1)
            declared[current_cat] = int(m.group(2))
            sections[current_cat] = []
            continue
        if current_cat is None:
            continue
        if s.startswith(("Wincon snapshot:", "Graveyard-hate plan:", "Brutal note on")):
            current_cat = None
            continue
        if s.startswith(("✅", "Why this is", "What makes this", "If you meant", "Say so and I’ll", "sets", "and pick the most degenerate")):
            current_cat = None
            continue
        if ":" in s:
            # prose line, not deck item
            current_cat = None
            continue
        if s in {"Game Changers (exactly 3)", "The degeneracy", "99-card main deck (plus commander)", "Main Deck (99)", "Locked 99"}:
            continue
        sections[current_cat].append(s)
    return commander_name, sections, declared


def extract_bullets_from_heading(text: str, heading_regex: str) -> list[str]:
    lines = text.splitlines()
    out: list[str] = []
    in_section = False
    start_level = None
    for line in lines:
        s = line.rstrip()
        h = re.match(r"^(#{1,6})\s+(.*)$", s)
        if h:
            level = len(h.group(1))
            title = h.group(2).strip()
            if in_section and level <= (start_level or 6):
                break
            if re.search(heading_regex, title):
                in_section = True
                start_level = level
                continue
        if not in_section:
            continue
        if not s.strip():
            continue
        if s.strip().startswith("[") and re.match(r"^\[[0-9]+\]:", s.strip()):
            break
        out.append(s)
    return out


def pick_gc_cards(sections: OrderedDict[str, list[str]]) -> list[str]:
    gcs: list[str] = []
    for cards in sections.values():
        for item in cards:
            if "(GC" in item or item.endswith("(GC)") or "GC)" in item:
                gcs.append(item)
    # Dedup preserving order by normalized card name
    seen: set[str] = set()
    deduped: list[str] = []
    for item in gcs:
        key = normalize_card_name(item).casefold()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def format_card_list(cards: Iterable[str]) -> list[str]:
    return [f"- {strip_ref_links(c).strip()}" for c in cards]


def trim_chat_overflow(build: DeckBuild, declared: dict[str, int], trim_map: dict[str, list[str]]) -> None:
    for cat, target in declared.items():
        if cat not in build.deck_sections:
            continue
        cards = build.deck_sections[cat]
        if len(cards) <= target:
            continue
        overflow = len(cards) - target
        planned = trim_map.get(cat, [])
        removed: list[str] = []
        for candidate in planned:
            for i, card in enumerate(cards):
                if normalize_card_name(card).casefold() == normalize_card_name(candidate).casefold():
                    removed.append(cards.pop(i))
                    break
            if len(cards) == target:
                break
        while len(cards) > target:
            removed.append(cards.pop())
        if removed:
            build.source_repairs.append(
                f"Source declared `{cat} ({target})` but listed {target + overflow}; trimmed overflow to match declared 99: {', '.join(strip_markdown_inline(r) for r in removed)}."
            )


def apply_card_replacements(build: DeckBuild, replacements: dict[str, str]) -> None:
    for cat, cards in build.deck_sections.items():
        for i, card in enumerate(cards):
            normalized = normalize_card_name(card)
            for src, dst in replacements.items():
                if normalized.casefold() == src.casefold():
                    # preserve annotations if any (none needed here)
                    cards[i] = re.sub(re.escape(normalized), dst, card, flags=re.IGNORECASE)
                    build.source_repairs.append(f"Corrected source typo `{normalized}` -> `{dst}` in `{cat}`.")
                    break


def remove_card_by_name(build: DeckBuild, category: str, card_name: str) -> bool:
    cards = build.deck_sections[category]
    for i, card in enumerate(cards):
        if normalize_card_name(card).casefold() == card_name.casefold():
            cards.pop(i)
            return True
    return False


def build_from_structured(path: Path, build_id: str, flavor: str, commander: str, status: str) -> DeckBuild:
    sections = parse_structured_deck(path, commander)
    return DeckBuild(build_id=build_id, flavor=flavor, commander=commander, sources=[path], status=status, deck_sections=sections)


def build_from_chat(path: Path, build_id: str, flavor: str, commander: str, status: str, start_marker: str | None = None, end_marker: str | None = None, trim_map: dict[str, list[str]] | None = None) -> DeckBuild:
    parsed_commander, sections, declared = parse_chat_deck(path, start_marker, end_marker)
    build = DeckBuild(build_id=build_id, flavor=flavor, commander=commander, sources=[path], status=status, deck_sections=sections)
    if parsed_commander and normalize_card_name(parsed_commander).casefold() != commander.casefold():
        build.validation_notes.append(f"Source commander parsed as `{parsed_commander}`; canonical commander set to `{commander}`.")
    if trim_map:
        trim_chat_overflow(build, declared, trim_map)
    return build


def format_build(build: DeckBuild) -> str:
    lines: list[str] = []
    lines.append(f"### {build.build_id} — {build.flavor}")
    lines.append("")
    lines.append("Source(s): " + ", ".join(f"`{p}`" for p in build.sources))
    lines.append(f"Status: {build.status}")
    lines.append("")
    lines.append("#### Commander")
    lines.append("")
    lines.append(f"- {build.commander}")
    lines.append("")
    gcs = build.gc_cards or pick_gc_cards(build.deck_sections)
    if gcs:
        lines.append("#### Game Changers")
        lines.append("")
        lines.extend(format_card_list(gcs))
        lines.append("")
    lines.append("#### 99-card decklist")
    lines.append("")
    for cat in CATEGORY_ORDER:
        if cat not in build.deck_sections:
            continue
        cards = build.deck_sections[cat]
        lines.append(f"##### {cat} ({len(cards)})")
        lines.append("")
        lines.extend(format_card_list(cards))
        lines.append("")
    lines.append("#### Summary / How it wins")
    lines.append("")
    if build.summary_bullets:
        lines.extend(f"- {b}" for b in build.summary_bullets)
    else:
        lines.append("- None explicitly provided in source.")
    lines.append("")
    lines.append("#### Swaps / Variants / Package options")
    lines.append("")
    if build.swap_bullets:
        lines.extend(f"- {b}" for b in build.swap_bullets)
    else:
        lines.append("- None explicitly provided in source.")
    lines.append("")
    lines.append("#### Validation notes")
    lines.append("")
    notes = []
    notes.extend(build.validation_notes)
    notes.extend(build.source_repairs)
    if not notes:
        notes.append("No source-specific repairs were required during consolidation.")
    for note in notes:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)


def parse_more_sultai_notes(path: Path) -> dict[str, list[str]]:
    text = path.read_text(encoding="utf-8")
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    seen = set()
    deduped = []
    for p in paras:
        key = re.sub(r"\s+", " ", p).casefold()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(p)
    notes = {"muldrotha": [], "teval": []}
    for p in deduped:
        if "Muldrotha" in p or "Sheoldred" in p or "Volrath’s Stronghold" in p or "Bloom Tender" in p:
            notes["muldrotha"].append(p)
        if "Teval" in p or "Craterhoof" in p or "Biomass Mutation" in p or "Unnatural Growth" in p:
            notes["teval"].append(p)
    return notes


def build_index_table(rows: list[tuple[str, str, str, str, str, str]]) -> list[str]:
    lines = [
        "| Build ID | Flavor | Source | Full 99? | GC Package | Status |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return lines


def validate_builds(builds: list[DeckBuild]) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    for build in builds:
        total = build.total_cards()
        if total != 99:
            findings.append(ValidationFinding("error", build.build_id, f"Deck total is {total}, expected 99."))
        else:
            findings.append(ValidationFinding("info", build.build_id, "Deck total verified at 99."))
        gc_names = [normalize_card_name(c) for c in (build.gc_cards or pick_gc_cards(build.deck_sections))]
        if len(gc_names) != 3:
            findings.append(ValidationFinding("error", build.build_id, f"GC count is {len(gc_names)}, expected 3."))
        else:
            findings.append(ValidationFinding("info", build.build_id, "GC count verified at 3."))
        seen: dict[str, str] = {}
        for cat, cards in build.deck_sections.items():
            for card in cards:
                norm = normalize_card_name(card).casefold()
                if norm in {"plains", "island", "swamp", "mountain", "forest", "wastes"}:
                    continue
                if norm in seen:
                    findings.append(ValidationFinding("error", build.build_id, f"Duplicate card `{normalize_card_name(card)}` in `{cat}` and `{seen[norm]}`."))
                else:
                    seen[norm] = cat
        if build.commander.casefold().startswith("muldrotha"):
            if any("Teval, the Balanced Scale" in normalize_card_name(c) for cards in build.deck_sections.values() for c in cards):
                findings.append(ValidationFinding("error", build.build_id, "Teval card name appears as commander within Muldrotha build."))
        if build.commander.casefold().startswith("teval"):
            if any("Muldrotha, the Gravetide" in normalize_card_name(c) for cards in build.deck_sections.values() for c in cards):
                findings.append(ValidationFinding("error", build.build_id, "Muldrotha card name appears as commander within Teval build."))
    return findings


def build_muldrotha_reference() -> tuple[str, list[DeckBuild]]:
    src_m3 = DOCS_DIR / "muldrotha-3.md"
    src_m2 = DOCS_DIR / "muldrotha-2.md"
    src_mdeg = DOCS_DIR / "muldrotha-max-degen.md"
    src_shared = DOCS_DIR / "muldrotha-teval-max-degen.md"
    src_more = DOCS_DIR / "more-sultai-.md"

    mul_a = build_from_structured(src_m3, "MUL-A", "Authoritative Bracket 3 (Default)", "Muldrotha, the Gravetide", "authoritative (full-99)")
    mul_a.sources.append(src_m2)
    mul_a.gc_cards = ["Survival of the Fittest (GC)", "The One Ring (GC)", "Force of Will (GC)"]
    mul_a.summary_bullets = [
        "Primary cash-out is `Living Death`, backed by `Syr Konrad` drain and `Lord of Extinction` + `Jarad` conversion lines.",
        "The list is tuned for durability: `Perpetual Timepiece`, `Soul-Guide Lantern`, and dense interaction keep it functional through graveyard hate.",
        "Package A prioritizes consistency and rebuild speed over the `Cyclonic Rift`-style 'reset and kill' line.",
    ]
    mul_a.swap_bullets = [
        "Package B (Control + Closer): swap `The One Ring`, `Survival of the Fittest`, `Force of Will`, and `Seal of Primordium` for `Rhystic Study`, `Cyclonic Rift`, `Fierce Guardianship`, and `Pernicious Deed` (from `muldrotha-2.md`).",
        "Package C (Turbo): swap in `Ancient Tomb`, `Mana Vault`, and `Chrome Mox` for `Exotic Orchard`, `Arcane Signet`, and `Talisman of Resilience` (from `muldrotha-2.md`).",
        "Creature swap knobs (from `muldrotha-2.md`): `Ledger Shredder` -> `Glen Elendra Archmage`, `Accursed Marauder` -> `Meren of Clan Nel Toth`, `Massacre Wurm` -> `Toxrill, the Corrosive`, `Satyr Wayfinder` -> `Emry, Lurker of the Loch`.",
    ]

    mul_d = build_from_chat(src_mdeg, "MUL-D", "Max Degeneracy (The One Ring / Survival / Fierce)", "Muldrotha, the Gravetide", "max-degeneracy (full-99)")
    mul_d.gc_cards = ["The One Ring (GC)", "Survival of the Fittest (GC)", "Fierce Guardianship (GC)"]
    mul_d.summary_bullets = [
        "Uses `Survival of the Fittest` plus Muldrotha recursion to turn the graveyard into a second hand every turn.",
        "Supports multiple lethal cash-outs: `Living Death`, `Syr Konrad`, `Jarad + Lord of Extinction`, and `Craterhoof Behemoth`.",
        "Built to fight graveyard hate with removal density plus `Perpetual Timepiece`, `Soul-Guide Lantern`, `Bojuka Bog`, and channel lands.",
    ]
    mul_d.swap_bullets = ["None explicitly provided in source; this source is a locked degen list with a short rationale section."]

    mul_e = build_from_chat(
        src_shared,
        "MUL-E",
        "Max Degeneracy Turbo (Ancient Tomb / Mana Vault / Chrome Mox)",
        "Muldrotha, the Gravetide",
        "max-degeneracy (full-99)",
        start_marker="2) Muldrotha",
        end_marker="Brutal note on “Bracket 3”",
        trim_map={"Instants": ["Lim-Dul’s Vault", "Fact or Fiction"]},
    )
    mul_e.gc_cards = ["Ancient Tomb (GC)", "Mana Vault (GC)", "Chrome Mox (GC)"]
    mul_e.summary_bullets = [
        "Turbo-Muldrotha plan: deploy Muldrotha early with fast mana, then loop self-mill and recursion engines for inevitability.",
        "Wincon snapshot from source: `Living Death`, `Syr Konrad`, and `Jarad/Lord of Extinction` finishers after engine setup.",
        "Graveyard-hate plan in source emphasizes removal, `Perpetual Timepiece`, and graveyard disruption (`Dauthi`, `Bog`, `Lantern`).",
    ]
    mul_e.swap_bullets = ["None explicitly provided in source; this source is a locked turbo-degen variant."]

    notes = parse_more_sultai_notes(src_more)
    mul_notes = [
        "`Bloom Tender` -> `Satyr Wayfinder` is suggested as a power upgrade when acceleration matters more than extra self-mill setup.",
        "`Sheoldred, the Apocalypse` -> `Mulldrifter` is suggested for a higher-impact threat / life-total stabilizer line.",
        "`Volrath’s Stronghold` (land) -> `Exotic Orchard` is suggested to improve graveyard-independent recursion versus exile hate.",
        "These swaps originated in `more-sultai-.md`; duplicate blocks were deduplicated during consolidation.",
    ]
    if notes["muldrotha"]:
        mul_notes.append("Raw-note provenance retained: `more-sultai-.md` contains repeated versions of the same Muldrotha swap block; only one copy is included here.")

    index_rows = [
        ("MUL-A", "Authoritative Bracket 3 (Default)", "`muldrotha-3.md` + `muldrotha-2.md`", "Yes", "Survival / One Ring / Force of Will", "authoritative"),
        ("MUL-A Packages", "GC swap packages B/C", "`muldrotha-2.md` + `muldrotha-3.md`", "No", "Package B / C", "variant package"),
        ("MUL-D", "Max Degeneracy (Ring/Survival/Fierce)", "`muldrotha-max-degen.md`", "Yes", "The One Ring / Survival / Fierce", "max-degeneracy"),
        ("MUL-E", "Max Degeneracy Turbo", "`muldrotha-teval-max-degen.md`", "Yes", "Ancient Tomb / Mana Vault / Chrome Mox", "max-degeneracy"),
    ]

    builds = [mul_a, mul_d, mul_e]
    findings = validate_builds(builds)
    err_count = sum(1 for f in findings if f.severity == "error")
    warn_count = sum(1 for f in findings if f.severity == "warning")

    lines: list[str] = []
    lines.append("# Muldrotha, the Gravetide Reference")
    lines.append("")
    lines.append("## Scope and Sources")
    lines.append("")
    for p in [src_m3, src_m2, src_mdeg, src_shared, src_more]:
        lines.append(f"- `{p}`")
    lines.append("- Consolidation excludes `.xlsx` files and trims duplicate conversational residue while preserving actionable swaps and deck content.")
    lines.append("")
    lines.append("## Build Index")
    lines.append("")
    lines.extend(build_index_table(index_rows))
    lines.append("")
    lines.append("## Build Flavors")
    lines.append("")
    lines.append(format_build(mul_a).rstrip())
    lines.append("")
    lines.append("### MUL-A Packages — GC Swap Packages (B/C)")
    lines.append("")
    lines.append("Source(s): `docs/decks/sultai/muldrotha-2.md`, `docs/decks/sultai/muldrotha-3.md`")
    lines.append("Status: variant package (non-full-99; applies to MUL-A)")
    lines.append("")
    lines.append("#### Summary / How it wins")
    lines.append("")
    lines.append("- Package B (Rhystic/Rift/Fierce) increases stack control and end-step Rift conversion at the cost of toolbox inevitability.")
    lines.append("- Package C (Ancient Tomb/Mana Vault/Chrome Mox) increases deployment speed and spike factor while staying at 3 GCs.")
    lines.append("- `muldrotha-3.md` rates Package A as the best Bracket-3-feel default and calls out tradeoffs for B/C.")
    lines.append("")
    lines.append("#### Swaps / Variants / Package options")
    lines.append("")
    lines.append("- Package B exact swap set (`muldrotha-2.md`): OUT `The One Ring`, `Survival`, `Force of Will`, `Seal of Primordium`; IN `Rhystic Study`, `Cyclonic Rift`, `Fierce Guardianship`, `Pernicious Deed`.")
    lines.append("- Package C exact swap set (`muldrotha-2.md`): IN `Mana Vault` -> OUT `Arcane Signet`; IN `Chrome Mox` -> OUT `Talisman of Resilience`; IN `Ancient Tomb` -> OUT `Exotic Orchard`.")
    lines.append("- Tier notes from `muldrotha-3.md`: Package A = top Bracket 3 durability, Package B = higher conversion/salt, Package C = strongest speed but weakest 'Bracket 3 vibe'.")
    lines.append("")
    lines.append("#### Validation notes")
    lines.append("")
    lines.append("- This is a package/variant section, not a standalone full 99 build, so the 99-card validator intentionally skips it.")
    lines.append("")
    lines.append(format_build(mul_d).rstrip())
    lines.append("")
    lines.append(format_build(mul_e).rstrip())
    lines.append("")
    lines.append("## Additional Actionable Notes / Swaps")
    lines.append("")
    for n in mul_notes:
        lines.append(f"- {n}")
    lines.append("")
    lines.append("## Validation Summary")
    lines.append("")
    lines.append(f"- Generated UTC: {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    lines.append("- Full builds validated in this file: `MUL-A`, `MUL-D`, `MUL-E`.")
    lines.append(f"- Structural validation status (generator pre-check): {err_count} hard errors, {warn_count} warnings.")
    for build in builds:
        lines.append(f"- `{build.build_id}`: 99-card total = {build.total_cards()}, GC count = {len(build.gc_cards or pick_gc_cards(build.deck_sections))}.")
    lines.append("- Shared-source overflow repairs were documented per build where the source listed more cards than the declared category counts.")
    lines.append("- Optional card-pool membership validation is supported by `scripts/deck_docs/validate_commander_refs.py --pool-file <file>`.")
    lines.append("")

    return normalize_whitespace("\n".join(lines)), builds


def build_teval_reference() -> tuple[str, list[DeckBuild]]:
    src_t1 = DOCS_DIR / "teval-1.md"
    src_t2 = DOCS_DIR / "teval-2.md"
    src_tdeg = DOCS_DIR / "teval-max-degen.md"
    src_compare = DOCS_DIR / "teval-1-and-2-compared.md"
    src_shared = DOCS_DIR / "muldrotha-teval-max-degen.md"
    src_more = DOCS_DIR / "more-sultai-.md"

    tev_a = build_from_structured(src_t1, "TEV-A", "Tuned Bracket 3 (teval-1)", "Teval, the Balanced Scale", "tuned (full-99)")
    apply_card_replacements(tev_a, {"Underream Lich": "Underrealm Lich"})
    tev_a.gc_cards = ["Rhystic Study (GC)", "Cyclonic Rift (GC)", "Fierce Guardianship (GC)"]
    tev_a.summary_bullets = [
        "Teval engine plan: attack to mill/recur lands, then convert repeated graveyard churn into tokens and board pressure.",
        "Primary closes are `Cyclonic Rift` swing turns and protected `Living Death` turns, with `Syr Konrad` as a graveyard-to-board damage engine.",
        "Source includes a five-pass audit and multiple alternative GC packages; this reference preserves the locked 99 plus those package notes.",
    ]
    tev_a.swap_bullets = [
        "Option A (Toolbox + staying power): swap in `Survival of the Fittest`, `The One Ring`, `Force of Will` for the default Rhystic/Rift/Fierce package.",
        "Option B (Turbo Teval): swap in `Ancient Tomb`, `Mana Vault`, `Chrome Mox` for Rhystic/Rift/Fierce.",
        "Option C (Tutor/disruption): swap in `Demonic Tutor`, `Vampiric Tutor`, `Opposition Agent` for Rhystic/Rift/Fierce; source warns this can push table experience into 'gotcha' territory.",
    ]

    tev_b = build_from_structured(src_t2, "TEV-B", "Tuned Bracket 3 Updated (teval-2)", "Teval, the Balanced Scale", "tuned (full-99 after source-sanctioned land cut)")
    removed_bog = remove_card_by_name(tev_b, "Lands", "Bojuka Bog")
    if removed_bog:
        tev_b.source_repairs.append("`teval-2.md` lists 37 lands and explicitly instructs cutting one land; canonical TEV-B applies the source-recommended default cut of `Bojuka Bog` to lock 36 lands / 99 cards.")
    else:
        tev_b.validation_notes.append("Expected `Bojuka Bog` land-cut repair from `teval-2.md` could not be applied automatically.")
    tev_b.gc_cards = ["Rhystic Study (GC)", "Cyclonic Rift (GC)", "Fierce Guardianship (GC)"]
    tev_b.summary_bullets = [
        "Updated tuned-pod list with `Sensei’s Divining Top`, `Soul-Guide Lantern`, and a refined interaction suite to maximize Rhystic/Rift/Fierce conversion.",
        "Source frames this as 'highest power Bracket 3' with a concrete one-land cut requirement; this reference resolves that to a locked 99.",
        "Teval remains a recursion/value engine; the GC package supplies card volume, reset/close, and free protection for the key turn.",
    ]
    tev_b.swap_bullets = [
        "Option 1 (Toolbox + resilience): `Survival`, `The One Ring`, `Force of Will` in for Rhystic/Rift/Fierce.",
        "Option 2 (Turbo Teval): `Ancient Tomb`, `Mana Vault`, `Chrome Mox` in for Rhystic/Rift/Fierce.",
        "Option 3 (Black disruption): `Demonic Tutor`, `Opposition Agent`, `Orcish Bowmasters` in for Rhystic/Rift/Fierce.",
        "Alternate TEV-B land cut (source-offered): cut `Exotic Orchard` instead of `Bojuka Bog` if the meta is graveyard-heavy.",
    ]

    tev_d = build_from_chat(src_tdeg, "TEV-D", "Max Degeneracy Alternate-GC (Rhystic / Rift / Fierce)", "Teval, the Balanced Scale", "max-degeneracy (full-99)")
    tev_d.gc_cards = ["Rhystic Study (GC)", "Cyclonic Rift (GC)", "Fierce Guardianship (GC)"]
    tev_d.summary_bullets = [
        "Source describes this as 'degenerate Bracket 3 control-midrange': choke the table on cards, then reset and kill.",
        "Primary cash-outs are `Cyclonic Rift` into lethal board and `Living Death` with `Konrad/Jarad/Lord` math.",
        "Graveyard-hate plan leans on interaction density plus `Soul-Guide Lantern` and `Endurance` as insurance.",
    ]
    tev_d.swap_bullets = ["None explicitly provided in source; this is a locked alternate-GC degen build."]

    tev_e = build_from_chat(
        src_shared,
        "TEV-E",
        "Max Degeneracy Lands-Lock (Crop / Field / Glacial Chasm)",
        "Teval, the Balanced Scale",
        "max-degeneracy (full-99 after source-overflow trim)",
        start_marker="1) Teval",
        end_marker="2) Muldrotha",
        trim_map={
            "Instants": ["Heroic Intervention"],
            "Sorceries": ["Kodama’s Reach"],
            "Lands": ["Volrath’s Stronghold"],
        },
    )
    tev_e.gc_cards = ["Crop Rotation (GC)", "Field of the Dead (GC)", "Glacial Chasm (GC)"]
    tev_e.summary_bullets = [
        "Field + Chasm lands-engine Teval build focused on inevitability via land recursion, token generation, and soft-lock pressure.",
        "Wincon snapshot from source: `Field/Scute + Teval` tokens overwhelm; `Living Death`, `Syr Konrad`, and `Jarad/Lord` close; `Strip Mine/Wasteland` recursion adds pressure.",
        "Source graveyard-hate note emphasizes sequencing, countermagic, and pivoting to the Field plan rather than dedicated anti-exile artifacts.",
    ]
    tev_e.swap_bullets = ["None explicitly provided in the TEV-E source block; related lands-engine package tuning guidance is captured in `TEV-C` and Additional Notes."]

    more_notes = parse_more_sultai_notes(src_more)
    teval_notes = [
        "Postscript note from `muldrotha-teval-max-degen.md`: `Icetill Explorer` is suggested over `Satyr Wayfinder` in the Field/Chasm/Crop package for higher ceiling and recurring engine support.",
        "Postscript note from `muldrotha-teval-max-degen.md`: if `Craterhoof Behemoth` is available, swap it in over `Massacre Wurm` for the Field/Scute Teval build to convert token inevitability into immediate lethal more reliably.",
        "`more-sultai-.md` duplicates the same Teval Craterhoof guidance block; only one deduped version is represented here.",
        "`more-sultai-.md` also notes pool-constrained alternatives (`Biomass Mutation`, `Unnatural Growth`) for token-finisher roles when Craterhoof is unavailable in the chosen pool subset.",
    ]
    if more_notes["teval"]:
        teval_notes.append("Raw-note provenance retained: `more-sultai-.md` includes both 'Craterhoof available' and 'not in restricted pool' contexts; this reference keeps only actionable swap guidance and flags context dependence.")

    compare_text = src_compare.read_text(encoding="utf-8")
    compare_lines = [
        "### TEV-C — Package Comparison (from `teval-1-and-2-compared.md`)",
        "",
        "Source(s): `docs/decks/sultai/teval-1-and-2-compared.md`",
        "Status: comparison-derived (non-full-99)",
        "",
        "#### Summary / How it wins",
        "",
        "- Package 1 (Field / Chasm / Crop Rotation) is positioned as the most Teval-specific inevitability engine with a Crop -> Chasm panic button.",
        "- Package 2 (Rhystic / Rift / Fierce) is positioned as the highest generic tuned-pod conversion package with cleaner closes and less salt than repeated Chasm loops.",
        "- The source explicitly recommends choosing based on pod goals: inevitability/Teval identity vs tuned-pod win rate and faster closes.",
        "",
        "#### Swaps / Variants / Package options",
        "",
        "- Package 1 non-GC adds (source): `Zuran Orb`, `Icetill Explorer`, `Perpetual Timepiece`, `Strip Mine`, `Wasteland`.",
        "- Package 1 non-GC trims (source): `Mana Drain`, `Force of Negation`, trim `Counterspell/Arcane Denial`, and other slow draw artifacts if present.",
        "- Package 2 non-GC adds (source): `Mystic Remora`, `Sensei’s Divining Top`, `Fact or Fiction`, `Soul-Guide Lantern`, `Pernicious Deed`.",
        "- Package 2 trims (source): `Putrefy` and slower lands-only tech depending on slots/meta.",
        "",
        "#### Validation notes",
        "",
        "- This comparison source does not include a full 99 decklist and is intentionally excluded from full-build count validation.",
        "",
    ]
    if "Warning (social, not rules)" in compare_text:
        compare_lines.insert(compare_lines.index("", 8), "- Source also includes a social warning that repeated Chasm recursion can create 'archenemy' table dynamics even when technically Bracket 3.")

    index_rows = [
        ("TEV-A", "Tuned Bracket 3 (teval-1)", "`teval-1.md`", "Yes", "Rhystic / Rift / Fierce", "tuned"),
        ("TEV-B", "Tuned Bracket 3 Updated (teval-2)", "`teval-2.md`", "Yes", "Rhystic / Rift / Fierce", "tuned"),
        ("TEV-C", "Package comparison / swap rationale", "`teval-1-and-2-compared.md`", "No", "Package 1 vs 2", "comparison"),
        ("TEV-D", "Max Degeneracy Alternate-GC", "`teval-max-degen.md`", "Yes", "Rhystic / Rift / Fierce", "max-degeneracy"),
        ("TEV-E", "Max Degeneracy Lands-Lock", "`muldrotha-teval-max-degen.md`", "Yes", "Crop / Field / Glacial Chasm", "max-degeneracy"),
    ]

    builds = [tev_a, tev_b, tev_d, tev_e]
    findings = validate_builds(builds)
    err_count = sum(1 for f in findings if f.severity == "error")
    warn_count = sum(1 for f in findings if f.severity == "warning")

    lines: list[str] = []
    lines.append("# Teval, the Balanced Scale Reference")
    lines.append("")
    lines.append("## Scope and Sources")
    lines.append("")
    for p in [src_t1, src_t2, src_tdeg, src_compare, src_shared, src_more]:
        lines.append(f"- `{p}`")
    lines.append("- Consolidation preserves full deck builds and actionable package notes while trimming duplicated conversational residue.")
    lines.append("")
    lines.append("## Build Index")
    lines.append("")
    lines.extend(build_index_table(index_rows))
    lines.append("")
    lines.append("## Build Flavors")
    lines.append("")
    lines.append(format_build(tev_a).rstrip())
    lines.append("")
    lines.append(format_build(tev_b).rstrip())
    lines.append("")
    lines.append(format_build(tev_d).rstrip())
    lines.append("")
    lines.append(format_build(tev_e).rstrip())
    lines.append("")
    lines.append("## Cross-Build Comparisons")
    lines.append("")
    lines.extend(compare_lines)
    lines.append("")
    lines.append("## Additional Actionable Notes / Swaps")
    lines.append("")
    for n in teval_notes:
        lines.append(f"- {n}")
    lines.append("")
    lines.append("## Validation Summary")
    lines.append("")
    lines.append(f"- Generated UTC: {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    lines.append("- Full builds validated in this file: `TEV-A`, `TEV-B`, `TEV-D`, `TEV-E`.")
    lines.append(f"- Structural validation status (generator pre-check): {err_count} hard errors, {warn_count} warnings.")
    for build in builds:
        lines.append(f"- `{build.build_id}`: 99-card total = {build.total_cards()}, GC count = {len(build.gc_cards or pick_gc_cards(build.deck_sections))}.")
    lines.append("- TEV-B applies the source-specified one-land cut to resolve `teval-2.md` into a locked 99.")
    lines.append("- TEV-E applies explicit overflow trimming to match the shared source's declared 99-card category totals; repairs are documented in `TEV-E` validation notes.")
    lines.append("- Optional card-pool membership validation is supported by `scripts/deck_docs/validate_commander_refs.py --pool-file <file>`.")
    lines.append("")

    return normalize_whitespace("\n".join(lines)), builds


def write_output(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build consolidated Sultai commander reference docs.")
    parser.add_argument("--skip-cleanup", action="store_true", help="Skip whitespace cleanup on source markdown files.")
    args = parser.parse_args()

    if not args.skip_cleanup:
        changed = cleanup_markdown_files(DOCS_DIR)
        print(f"Whitespace cleanup touched {len(changed)} markdown files.")
        for p in changed:
            print(f"  - {p}")

    mul_doc, _ = build_muldrotha_reference()
    tev_doc, _ = build_teval_reference()

    mul_path = DOCS_DIR / "muldrotha-reference.md"
    tev_path = DOCS_DIR / "teval-reference.md"
    write_output(mul_path, mul_doc)
    write_output(tev_path, tev_doc)

    print(f"Wrote {mul_path}")
    print(f"Wrote {tev_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
