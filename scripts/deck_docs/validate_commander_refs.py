#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
import re
import sys
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

BUILD_HEADING_RE = re.compile(r"^###\s+((?:MUL|TEV)-[A-Z0-9]+)\s+—\s+(.+)$")
CAT_HEADING_RE = re.compile(r"^#####\s+(Creatures|Artifacts|Enchantments|Instants|Sorceries|Lands)\s+\((\d+)\)$")
H1_RE = re.compile(r"^#\s+(.+)$")
BULLET_RE = re.compile(r"^-\s+(.+?)\s*$")


@dataclass
class DeckSection:
    declared_count: int
    cards: list[str] = field(default_factory=list)


@dataclass
class BuildFlavor:
    build_id: str
    title: str
    sources: list[str] = field(default_factory=list)
    status: str | None = None
    commander_lines: list[str] = field(default_factory=list)
    gc_lines: list[str] = field(default_factory=list)
    deck_sections: OrderedDict[str, DeckSection] = field(default_factory=OrderedDict)
    summary_lines: list[str] = field(default_factory=list)
    swap_lines: list[str] = field(default_factory=list)
    validation_lines: list[str] = field(default_factory=list)

    @property
    def is_full_build(self) -> bool:
        return bool(self.deck_sections)

    def total_cards(self) -> int:
        return sum(len(s.cards) for s in self.deck_sections.values())


@dataclass
class CommanderReference:
    path: Path
    commander_name: str
    builds: list[BuildFlavor]


@dataclass
class ValidationResult:
    severity: str  # error | warning | info
    file: Path
    build_id: str | None
    code: str
    message: str


def strip_md(s: str) -> str:
    return s.replace("**", "").replace("*", "").strip()


def normalize_card_name(name: str) -> str:
    s = strip_md(name)
    s = re.sub(r"^`|`$", "", s)
    s = re.sub(r"\s*\([^)]*\)\s*$", "", s)
    s = s.replace("’", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"\s+", " ", s).strip()
    return s


def parse_commander_reference(path: Path) -> CommanderReference:
    lines = path.read_text(encoding="utf-8").splitlines()
    commander_name = ""
    builds: list[BuildFlavor] = []
    current_build: BuildFlavor | None = None
    current_block: str | None = None
    current_category: str | None = None

    for raw in lines:
        line = raw.rstrip("\n")
        s = line.strip()
        if not commander_name:
            m = H1_RE.match(s)
            if m:
                commander_name = m.group(1)
        m = BUILD_HEADING_RE.match(s)
        if m:
            current_build = BuildFlavor(build_id=m.group(1), title=m.group(2))
            builds.append(current_build)
            current_block = None
            current_category = None
            continue
        if current_build is None:
            continue
        if s.startswith("### "):
            current_build = None
            current_block = None
            current_category = None
            continue
        if s.startswith("Source(s):"):
            current_build.sources = [x.strip().strip('`') for x in s[len("Source(s):"):].split(",") if x.strip()]
            continue
        if s.startswith("Status:"):
            current_build.status = s[len("Status:"):].strip()
            continue
        if s == "#### Commander":
            current_block = "commander"
            current_category = None
            continue
        if s == "#### Game Changers":
            current_block = "gcs"
            current_category = None
            continue
        if s == "#### 99-card decklist":
            current_block = "deck"
            current_category = None
            continue
        if s == "#### Summary / How it wins":
            current_block = "summary"
            current_category = None
            continue
        if s == "#### Swaps / Variants / Package options":
            current_block = "swaps"
            current_category = None
            continue
        if s == "#### Validation notes":
            current_block = "validation"
            current_category = None
            continue
        cat = CAT_HEADING_RE.match(s)
        if cat and current_block == "deck":
            current_category = cat.group(1)
            current_build.deck_sections[current_category] = DeckSection(declared_count=int(cat.group(2)))
            continue

        bm = BULLET_RE.match(s)
        if not bm:
            continue
        value = bm.group(1).strip()
        if current_block == "commander":
            current_build.commander_lines.append(value)
        elif current_block == "gcs":
            current_build.gc_lines.append(value)
        elif current_block == "deck" and current_category:
            current_build.deck_sections[current_category].cards.append(value)
        elif current_block == "summary":
            current_build.summary_lines.append(value)
        elif current_block == "swaps":
            current_build.swap_lines.append(value)
        elif current_block == "validation":
            current_build.validation_lines.append(value)

    if not commander_name:
        commander_name = path.stem
    return CommanderReference(path=path, commander_name=commander_name, builds=builds)


def load_pool(path: Path) -> tuple[set[str], list[ValidationResult], list[str]]:
    entries = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    entries = [e for e in entries if e]
    norm_to_original: dict[str, str] = {}
    duplicates: list[str] = []
    for e in entries:
        n = normalize_card_name(e).casefold()
        if n in norm_to_original:
            duplicates.append(e)
        else:
            norm_to_original[n] = e
    return set(norm_to_original), [], duplicates


def suggest_pool_match(card: str, pool: set[str]) -> str | None:
    card_norm = normalize_card_name(card).casefold()
    candidates = difflib.get_close_matches(card_norm, list(pool), n=1, cutoff=0.84)
    return candidates[0] if candidates else None


def validate_reference(ref: CommanderReference, pool: set[str] | None = None) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    expected_commander = "Muldrotha, the Gravetide" if "Muldrotha" in ref.commander_name else "Teval, the Balanced Scale" if "Teval" in ref.commander_name else None
    build_ids = {b.build_id for b in ref.builds}

    for build in ref.builds:
        if not build.is_full_build:
            results.append(ValidationResult("info", ref.path, build.build_id, "SKIP_NON_FULL", "Skipped 99-card checks (no decklist sections in this build block)."))
            continue
        if not build.commander_lines:
            results.append(ValidationResult("error", ref.path, build.build_id, "MISSING_COMMANDER", "Missing commander section entry."))
        else:
            commander_line = normalize_card_name(build.commander_lines[0])
            if expected_commander and commander_line.casefold() != expected_commander.casefold():
                results.append(ValidationResult("error", ref.path, build.build_id, "COMMANDER_MISMATCH", f"Commander `{commander_line}` does not match file commander `{expected_commander}`."))
        total = 0
        all_cards_norm: dict[str, str] = {}
        for cat, section in build.deck_sections.items():
            actual = len(section.cards)
            total += actual
            if actual != section.declared_count:
                results.append(ValidationResult("error", ref.path, build.build_id, "SECTION_COUNT_MISMATCH", f"{cat} declared {section.declared_count} but lists {actual}."))
            for card in section.cards:
                norm = normalize_card_name(card).casefold()
                if norm in {"plains", "island", "swamp", "mountain", "forest", "wastes"}:
                    continue
                if norm in all_cards_norm:
                    results.append(ValidationResult("error", ref.path, build.build_id, "DUPLICATE_CARD", f"Duplicate card `{normalize_card_name(card)}` in decklist."))
                else:
                    all_cards_norm[norm] = cat
        if total != 99:
            results.append(ValidationResult("error", ref.path, build.build_id, "TOTAL_NOT_99", f"Deck total is {total}, expected 99."))
        else:
            results.append(ValidationResult("info", ref.path, build.build_id, "TOTAL_OK", "Deck total verified at 99."))
        gc_count = len(build.gc_lines)
        if gc_count != 3:
            results.append(ValidationResult("error", ref.path, build.build_id, "GC_COUNT", f"GC count is {gc_count}, expected 3."))
        else:
            results.append(ValidationResult("info", ref.path, build.build_id, "GC_OK", "GC count verified at 3."))

        if not build.summary_lines:
            results.append(ValidationResult("warning", ref.path, build.build_id, "MISSING_SUMMARY", "Missing summary section bullets."))
        if not build.swap_lines:
            results.append(ValidationResult("warning", ref.path, build.build_id, "MISSING_SWAPS", "Missing swaps/variants section bullets."))

        if pool is not None:
            for cat, section in build.deck_sections.items():
                for card in section.cards:
                    norm = normalize_card_name(card).casefold()
                    if norm in {"plains", "island", "swamp", "mountain", "forest", "wastes"}:
                        continue
                    if norm not in pool:
                        suggestion = suggest_pool_match(card, pool)
                        msg = f"Card `{normalize_card_name(card)}` not found in provided pool."
                        if suggestion:
                            msg += f" Closest match: `{suggestion}`."
                        results.append(ValidationResult("warning", ref.path, build.build_id, "POOL_MISSING", msg))

    # Simple cross-reference sanity: any explicit build IDs mentioned in non-build sections should exist.
    text = ref.path.read_text(encoding="utf-8")
    mentioned = set(re.findall(r"\b(?:MUL|TEV)-[A-Z0-9]+\b", text))
    for mid in sorted(mentioned - build_ids):
        results.append(ValidationResult("warning", ref.path, None, "UNKNOWN_BUILD_REF", f"Build ID `{mid}` is mentioned but not defined as a `###` build heading."))

    return results


def render_report(results: list[ValidationResult]) -> str:
    grouped = {"error": [], "warning": [], "info": []}
    for r in results:
        grouped.setdefault(r.severity, []).append(r)

    lines: list[str] = []
    for severity in ("error", "warning", "info"):
        items = grouped.get(severity, [])
        if not items:
            continue
        lines.append(f"[{severity.upper()}] {len(items)}")
        for r in items:
            loc = f"{r.file}"
            if r.build_id:
                loc += f"::{r.build_id}"
            lines.append(f"- {loc} [{r.code}] {r.message}")
        lines.append("")

    lines.append(
        f"Summary: {sum(1 for r in results if r.severity == 'error')} errors, "
        f"{sum(1 for r in results if r.severity == 'warning')} warnings, "
        f"{sum(1 for r in results if r.severity == 'info')} info"
    )
    return "\n".join(lines).rstrip() + "\n"


def print_report(results: list[ValidationResult]) -> None:
    sys.stdout.write(render_report(results))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate consolidated commander reference markdown docs.")
    parser.add_argument("--docs", nargs="+", required=True, help="Paths to consolidated commander reference markdown files.")
    parser.add_argument("--pool-file", type=Path, help="Optional newline-separated card pool file for soft membership warnings.")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures.")
    parser.add_argument("--write-report", type=Path, help="Optional path to write the rendered validation report.")
    args = parser.parse_args(argv)

    pool: set[str] | None = None
    duplicates: list[str] = []
    if args.pool_file:
        pool, _, duplicates = load_pool(args.pool_file)

    all_results: list[ValidationResult] = []
    for doc in args.docs:
        ref = parse_commander_reference(Path(doc))
        all_results.extend(validate_reference(ref, pool))

    if duplicates:
        all_results.append(ValidationResult("info", args.pool_file, None, "POOL_DUPLICATES", f"Pool file contains {len(duplicates)} duplicate entries (case-insensitive)."))

    report_text = render_report(all_results)
    sys.stdout.write(report_text)
    if args.write_report:
        args.write_report.write_text(report_text, encoding="utf-8")
    errors = sum(1 for r in all_results if r.severity == "error")
    warnings = sum(1 for r in all_results if r.severity == "warning")

    if errors:
        return 1
    if args.strict and warnings:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
