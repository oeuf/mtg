#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.deck_docs.validate_locked_b3_decks import parse_locked_doc

SULTAI = ROOT / "docs" / "decks" / "sultai"
MUL_REF = SULTAI / "muldrotha-reference.md"
TEV_REF = SULTAI / "teval-reference.md"
MUL_G_DOC = SULTAI / "muldrotha-max-degeneracy-bracket3-locked-g.md"
TEV_G_DOC = SULTAI / "teval-max-degeneracy-bracket3-locked-g.md"
G_NOTES = SULTAI / "max-degen-bracket3-shell-g-build-notes.md"
G_REPORT = SULTAI / "max-degen-bracket3-shell-g-validation-report.txt"


def md_bullets(lines: list[str]) -> list[str]:
    return [f"- {x}" for x in lines]


def render_reference_build(doc_path: Path, build_id: str, flavor_title: str, status: str, notes_path: Path, report_path: Path) -> str:
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
    lines.extend(md_bullets(d.win_lines[:6]))
    lines.append(f"- Full shell-specific subplans (pile templates / Crop target matrix), anti-hate plan, and social-risk notes are documented in the standalone G-shell doc `{doc_path}`.")
    lines.append("")
    lines.append("#### Swaps / Variants / Package options")
    lines.append("")
    lines.append("- None intentionally; this is a locked genuinely-new max-degeneracy Bracket 3 shell.")
    lines.append(f"- Novelty metrics and baseline diffs are documented in `{notes_path}`.")
    lines.append("")
    lines.append("#### Validation notes")
    lines.append("")
    lines.extend(md_bullets(d.validation_lines))
    lines.append(f"- Dedicated G-shell validation report: `{report_path}` (includes novelty overlap thresholds vs prior builds, shell-identity checks, and pool/GC/banned-card validation).")
    return "\n".join(lines).rstrip() + "\n\n"


def ensure_source_bullet(text: str, path: Path) -> str:
    bullet = f"- `{path}`"
    if bullet in text:
        return text
    marker = "- Consolidation"
    idx = text.find(marker)
    if idx == -1:
        raise RuntimeError("Could not find Scope and Sources insertion marker")
    return text[:idx] + bullet + "\n" + text[idx:]


def ensure_build_index_row(text: str, row: str, after_row: str) -> str:
    if row in text:
        return text
    idx = text.find(after_row)
    if idx == -1:
        raise RuntimeError(f"Could not find build index anchor row: {after_row}")
    line_end = text.find("\n", idx)
    if line_end == -1:
        line_end = len(text)
    return text[: line_end + 1] + row + "\n" + text[line_end + 1 :]


def ensure_build_block(text: str, heading_prefix: str, block: str, before_header: str) -> str:
    if heading_prefix in text:
        return text
    marker = text.find(before_header)
    if marker == -1:
        raise RuntimeError(f"Could not find insertion header `{before_header}`")
    return text[:marker] + block + text[marker:]


def ensure_line_after(text: str, anchor_line: str, new_line: str) -> str:
    if new_line in text:
        return text
    if anchor_line not in text:
        return text
    return text.replace(anchor_line, anchor_line + new_line)


def patch_muldrotha_validation_summary(text: str) -> str:
    text = text.replace(
        "- Full builds validated in this file: `MUL-A`, `MUL-D`, `MUL-E`, `MUL-F`.\n",
        "- Full builds validated in this file: `MUL-A`, `MUL-D`, `MUL-E`, `MUL-F`, `MUL-G`.\n",
    )
    text = ensure_line_after(
        text,
        "- `MUL-F`: 99-card total = 99, GC count = 3 (integrated from the locked standalone max-degen B3 build).\n",
        "- `MUL-G`: 99-card total = 99, GC count = 3 (integrated from the locked standalone max-degen B3 G-shell build).\n",
    )
    text = text.replace(
        "- Pool validation was run against `docs/decks/sultai/user-card-pool-2026-02-22.txt`; this file contributed 4 warnings in this reference (including `MUL-F`), all due to the pool typo `Underream Lich` vs the normalized deck card `Underrealm Lich`.\n",
        "- Pool validation was run against `docs/decks/sultai/user-card-pool-2026-02-22.txt`; this file contributed 5 warnings in this reference (including `MUL-F` and `MUL-G`), all due to the pool typo `Underream Lich` vs the normalized deck card `Underrealm Lich`.\n",
    )
    extra = "- G-shell integration addendum: `MUL-G` is sourced from `docs/decks/sultai/muldrotha-max-degeneracy-bracket3-locked-g.md` and validated by `docs/decks/sultai/max-degen-bracket3-shell-g-validation-report.txt`.\n"
    if extra not in text:
        tail_anchor = "- Locked max-degen integration addendum: `MUL-F` is sourced from `docs/decks/sultai/muldrotha-max-degeneracy-bracket3-locked.md` and validated by `docs/decks/sultai/max-degen-bracket3-build-validation-report.txt`.\n"
        text = ensure_line_after(text, tail_anchor, extra)
    return text


def patch_teval_validation_summary(text: str) -> str:
    text = text.replace(
        "- Full builds validated in this file: `TEV-A`, `TEV-B`, `TEV-D`, `TEV-E`, `TEV-F`.\n",
        "- Full builds validated in this file: `TEV-A`, `TEV-B`, `TEV-D`, `TEV-E`, `TEV-F`, `TEV-G`.\n",
    )
    text = ensure_line_after(
        text,
        "- `TEV-F`: 99-card total = 99, GC count = 3 (integrated from the locked standalone max-degen B3 build).\n",
        "- `TEV-G`: 99-card total = 99, GC count = 3 (integrated from the locked standalone max-degen B3 G-shell build).\n",
    )
    text = text.replace(
        "- Pool validation was run against `docs/decks/sultai/user-card-pool-2026-02-22.txt`; this file contributed 5 warnings in this reference (including `TEV-F`), all due to the pool typo `Underream Lich` vs the normalized deck card `Underrealm Lich`.\n",
        "- Pool validation was run against `docs/decks/sultai/user-card-pool-2026-02-22.txt`; this file contributed 6 warnings in this reference (including `TEV-F` and `TEV-G`), all due to the pool typo `Underream Lich` vs the normalized deck card `Underrealm Lich`.\n",
    )
    extra = "- G-shell integration addendum: `TEV-G` is sourced from `docs/decks/sultai/teval-max-degeneracy-bracket3-locked-g.md` and validated by `docs/decks/sultai/max-degen-bracket3-shell-g-validation-report.txt`.\n"
    if extra not in text:
        tail_anchor = "- Locked max-degen integration addendum: `TEV-F` is sourced from `docs/decks/sultai/teval-max-degeneracy-bracket3-locked.md` and validated by `docs/decks/sultai/max-degen-bracket3-build-validation-report.txt`.\n"
        text = ensure_line_after(text, tail_anchor, extra)
    return text


def main() -> int:
    mul_text = MUL_REF.read_text(encoding="utf-8")
    tev_text = TEV_REF.read_text(encoding="utf-8")

    mul_block = render_reference_build(
        MUL_G_DOC,
        "MUL-G",
        "Maximum Degeneracy Bracket 3 (Locked Intuition / Gifts / Survival)",
        "max-degeneracy (full-99; locked bracket-3; genuine new shell)",
        G_NOTES,
        G_REPORT,
    )
    tev_block = render_reference_build(
        TEV_G_DOC,
        "TEV-G",
        "Maximum Degeneracy Bracket 3 (Locked Field / Crop / Mox Diamond)",
        "max-degeneracy (full-99; locked bracket-3; genuine new shell)",
        G_NOTES,
        G_REPORT,
    )

    mul_text = ensure_source_bullet(mul_text, MUL_G_DOC)
    mul_text = ensure_build_index_row(
        mul_text,
        "| MUL-G | Maximum Degeneracy Bracket 3 (Locked G Shell) | `muldrotha-max-degeneracy-bracket3-locked-g.md` | Yes | Intuition / Gifts Ungiven / Survival | max-degeneracy (locked, genuine-new-shell) |",
        "| MUL-F | Maximum Degeneracy Bracket 3 (Locked) | `muldrotha-max-degeneracy-bracket3-locked.md` | Yes | Ancient Tomb / Mana Vault / Chrome Mox | max-degeneracy (locked) |",
    )
    mul_text = ensure_build_block(mul_text, "### MUL-G —", mul_block, "## Additional Actionable Notes / Swaps")
    mul_text = patch_muldrotha_validation_summary(mul_text)
    MUL_REF.write_text(mul_text, encoding="utf-8")

    tev_text = ensure_source_bullet(tev_text, TEV_G_DOC)
    tev_text = ensure_build_index_row(
        tev_text,
        "| TEV-G | Maximum Degeneracy Bracket 3 (Locked G Shell) | `teval-max-degeneracy-bracket3-locked-g.md` | Yes | Field / Crop / Mox Diamond | max-degeneracy (locked, genuine-new-shell) |",
        "| TEV-F | Maximum Degeneracy Bracket 3 (Locked) | `teval-max-degeneracy-bracket3-locked.md` | Yes | Crop / Field / Glacial Chasm | max-degeneracy (locked) |",
    )
    # keep full builds grouped before TEV-C comparison section
    tev_text = ensure_build_block(tev_text, "### TEV-G —", tev_block, "## Cross-Build Comparisons")
    tev_text = patch_teval_validation_summary(tev_text)
    TEV_REF.write_text(tev_text, encoding="utf-8")

    print("Integrated MUL-G and TEV-G into commander reference docs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
