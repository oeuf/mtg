#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.deck_docs.validate_locked_b3_decks import parse_locked_doc

SULTAI = ROOT / "docs" / "decks" / "sultai"
MUL_REF = SULTAI / "muldrotha-reference.md"
TEV_REF = SULTAI / "teval-reference.md"
MUL_LOCKED = SULTAI / "muldrotha-max-degeneracy-bracket3-locked.md"
TEV_LOCKED = SULTAI / "teval-max-degeneracy-bracket3-locked.md"
LOCKED_NOTES = SULTAI / "max-degen-bracket3-build-notes.md"
LOCKED_REPORT = SULTAI / "max-degen-bracket3-build-validation-report.txt"


def md_bullets(lines: list[str]) -> list[str]:
    return [f"- {line}" for line in lines]


def render_reference_build(doc_path: Path, build_id: str, flavor_title: str, status: str) -> str:
    d = parse_locked_doc(doc_path)
    lines: list[str] = []
    lines.append(f"### {build_id} — {flavor_title}")
    lines.append("")
    lines.append(f"Source(s): `{doc_path}`")
    lines.append(f"Status: {status}")
    lines.append("")
    lines.append("#### Commander")
    lines.append("")
    lines.extend(md_bullets(d.commander_bullets))
    lines.append("")
    lines.append("#### Game Changers")
    lines.append("")
    lines.extend(md_bullets(d.gc_bullets))
    lines.append("")
    lines.append("#### 99-card decklist")
    lines.append("")
    for cat in ("Creatures", "Artifacts", "Enchantments", "Instants", "Sorceries", "Lands"):
        sec = d.deck_sections[cat]
        lines.append(f"##### {cat} ({sec.declared})")
        lines.append("")
        lines.extend(md_bullets(sec.cards))
        lines.append("")
    lines.append("#### Summary / How it wins")
    lines.append("")
    # Use first 3-4 win lines directly plus anti-hate summary pointer.
    lines.extend(md_bullets(d.win_lines[:4]))
    lines.append(f"- Full anti-hate plan, degeneracy rationale, and social-risk notes are documented in the standalone locked build doc `{doc_path}`.")
    lines.append("")
    lines.append("#### Swaps / Variants / Package options")
    lines.append("")
    lines.append("- None intentionally; this is a locked maximum-degeneracy Bracket 3 build.")
    lines.append(f"- For cut/add rationale and rejected candidates, see `{LOCKED_NOTES}`.")
    lines.append("")
    lines.append("#### Validation notes")
    lines.append("")
    lines.extend(md_bullets(d.validation_lines))
    lines.append(f"- Dedicated locked-build validation report: `{LOCKED_REPORT}` (task-specific validator includes GC snapshot, pool-only, banned-card, and required-package checks).")
    return "\n".join(lines).rstrip() + "\n\n"


def ensure_source_bullet(text: str, path: Path) -> str:
    bullet = f"- `{path}`"
    if bullet in text:
        return text
    marker = "- Consolidation"
    idx = text.find(marker)
    if idx == -1:
        raise RuntimeError(f"Could not find Scope and Sources insertion marker `{marker}`")
    return text[:idx] + bullet + "\n" + text[idx:]


def ensure_build_index_row(text: str, row: str, after_row_prefix: str) -> str:
    if row in text:
        return text
    target = after_row_prefix
    idx = text.find(target)
    if idx == -1:
        raise RuntimeError(f"Could not find build index row marker `{after_row_prefix}`")
    line_end = text.find("\n", idx)
    if line_end == -1:
        line_end = len(text)
    return text[: line_end + 1] + row + "\n" + text[line_end + 1 :]


def ensure_build_block(text: str, build_heading: str, block: str, before_header: str) -> str:
    if build_heading in text:
        return text
    marker = text.find(before_header)
    if marker == -1:
        raise RuntimeError(f"Could not find insertion header `{before_header}`")
    return text[:marker] + block + text[marker:]


def patch_validation_summary(text: str, commander: str) -> str:
    if commander == "muldrotha":
        if "`MUL-F`" not in text:
            text = text.replace(
                "- Full builds validated in this file: `MUL-A`, `MUL-D`, `MUL-E`.\n",
                "- Full builds validated in this file: `MUL-A`, `MUL-D`, `MUL-E`, `MUL-F`.\n",
            )
            insert_after = "- `MUL-E`: 99-card total = 99, GC count = 3.\n"
            add = "- `MUL-F`: 99-card total = 99, GC count = 3 (integrated from the locked standalone max-degen B3 build).\n"
            if insert_after in text:
                text = text.replace(insert_after, insert_after + add)
            tail_anchor = "- Pool validation report with warnings is saved at `docs/decks/sultai/commander-reference-validation-report-with-pool.txt` (pool file also contains duplicate entries, reported as informational).\n"
            extra = "- Locked max-degen integration addendum: `MUL-F` is sourced from `docs/decks/sultai/muldrotha-max-degeneracy-bracket3-locked.md` and validated by `docs/decks/sultai/max-degen-bracket3-build-validation-report.txt`.\n"
            if extra not in text and tail_anchor in text:
                text = text.replace(tail_anchor, tail_anchor + extra)
        return text
    if commander == "teval":
        if "`TEV-F`" not in text:
            text = text.replace(
                "- Full builds validated in this file: `TEV-A`, `TEV-B`, `TEV-D`, `TEV-E`.\n",
                "- Full builds validated in this file: `TEV-A`, `TEV-B`, `TEV-D`, `TEV-E`, `TEV-F`.\n",
            )
            insert_after = "- `TEV-E`: 99-card total = 99, GC count = 3.\n"
            add = "- `TEV-F`: 99-card total = 99, GC count = 3 (integrated from the locked standalone max-degen B3 build).\n"
            if insert_after in text:
                text = text.replace(insert_after, insert_after + add)
            tail_anchor = "- Pool validation report with warnings is saved at `docs/decks/sultai/commander-reference-validation-report-with-pool.txt` (pool file also contains duplicate entries, reported as informational).\n"
            extra = "- Locked max-degen integration addendum: `TEV-F` is sourced from `docs/decks/sultai/teval-max-degeneracy-bracket3-locked.md` and validated by `docs/decks/sultai/max-degen-bracket3-build-validation-report.txt`.\n"
            if extra not in text and tail_anchor in text:
                text = text.replace(tail_anchor, tail_anchor + extra)
        return text
    raise ValueError(commander)


def main() -> int:
    mul_text = MUL_REF.read_text(encoding="utf-8")
    tev_text = TEV_REF.read_text(encoding="utf-8")

    mul_block = render_reference_build(
        MUL_LOCKED,
        "MUL-F",
        "Maximum Degeneracy Bracket 3 (Locked Turbo-Recursion)",
        "max-degeneracy (full-99; locked bracket-3)",
    )
    tev_block = render_reference_build(
        TEV_LOCKED,
        "TEV-F",
        "Maximum Degeneracy Bracket 3 (Locked Field/Chasm)",
        "max-degeneracy (full-99; locked bracket-3)",
    )

    mul_text = ensure_source_bullet(mul_text, MUL_LOCKED)
    mul_text = ensure_build_index_row(
        mul_text,
        "| MUL-F | Maximum Degeneracy Bracket 3 (Locked) | `muldrotha-max-degeneracy-bracket3-locked.md` | Yes | Ancient Tomb / Mana Vault / Chrome Mox | max-degeneracy (locked) |",
        "| MUL-E | Max Degeneracy Turbo | `muldrotha-teval-max-degen.md` | Yes | Ancient Tomb / Mana Vault / Chrome Mox | max-degeneracy |",
    )
    mul_text = ensure_build_block(mul_text, "### MUL-F —", mul_block, "## Additional Actionable Notes / Swaps")
    mul_text = patch_validation_summary(mul_text, "muldrotha")
    MUL_REF.write_text(mul_text, encoding="utf-8")

    tev_text = ensure_source_bullet(tev_text, TEV_LOCKED)
    # Put TEV-F before TEV-C in build index so full builds stay grouped
    tev_text = ensure_build_index_row(
        tev_text,
        "| TEV-F | Maximum Degeneracy Bracket 3 (Locked) | `teval-max-degeneracy-bracket3-locked.md` | Yes | Crop / Field / Glacial Chasm | max-degeneracy (locked) |",
        "| TEV-E | Max Degeneracy Lands-Lock | `muldrotha-teval-max-degen.md` | Yes | Crop / Field / Glacial Chasm | max-degeneracy |",
    )
    tev_text = ensure_build_block(tev_text, "### TEV-F —", tev_block, "## Cross-Build Comparisons")
    tev_text = patch_validation_summary(tev_text, "teval")
    TEV_REF.write_text(tev_text, encoding="utf-8")

    print("Integrated MUL-F and TEV-F locked builds into commander reference docs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
