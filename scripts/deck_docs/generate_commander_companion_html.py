#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

BUILD_HEADING_RE = re.compile(r"^###\s+((?:MUL|TEV)-[A-Z0-9]+)\s+—\s+(.+)$")
CAT_HEADING_RE = re.compile(
    r"^#####\s+(Creatures|Artifacts|Enchantments|Instants|Sorceries|Lands)\s+\((\d+)\)$"
)
BULLET_RE = re.compile(r"^-\s+(.+?)\s*$")
H1_RE = re.compile(r"^#\s+(.+)$")


@dataclass
class DeckSection:
    declared_count: int
    cards: list[str] = field(default_factory=list)


@dataclass
class BuildFlavor:
    build_id: str
    title: str
    commander: str
    source_paths: list[str] = field(default_factory=list)
    status: str = ""
    game_changers: list[str] = field(default_factory=list)
    deck_sections: dict[str, DeckSection] = field(default_factory=dict)
    summary: list[str] = field(default_factory=list)
    swaps: list[str] = field(default_factory=list)
    validation: list[str] = field(default_factory=list)

    @property
    def full_99(self) -> bool:
        return bool(self.deck_sections)

    @property
    def total_cards(self) -> int:
        return sum(len(section.cards) for section in self.deck_sections.values())

    @property
    def degeneracy_level(self) -> str:
        status_norm = self.status.casefold()
        title_norm = self.title.casefold()
        if "genuine-new-shell" in status_norm or "genuine new shell" in status_norm or "locked g shell" in title_norm:
            return "Maximum (New Shell)"
        if "max-degeneracy" in status_norm or "maximum degeneracy" in title_norm or "max degeneracy" in title_norm:
            return "Maximum"
        if "authoritative" in status_norm or "tuned" in status_norm:
            return "Tuned"
        return "Variant / Support"


def clean_text(text: str) -> str:
    cleaned = text.replace("**", "").replace("*", "")
    cleaned = cleaned.replace("`", "")
    return cleaned.strip()


def parse_reference(path: Path) -> tuple[str, list[BuildFlavor]]:
    lines = path.read_text(encoding="utf-8").splitlines()

    commander_name = path.stem
    builds: list[BuildFlavor] = []
    current_build: BuildFlavor | None = None
    current_block: str | None = None
    current_category: str | None = None

    for raw in lines:
        s = raw.strip()
        h1_match = H1_RE.match(s)
        if h1_match:
            maybe_commander = h1_match.group(1).replace(" Reference", "").strip()
            if maybe_commander:
                commander_name = maybe_commander

        m = BUILD_HEADING_RE.match(s)
        if m:
            current_build = BuildFlavor(build_id=m.group(1), title=m.group(2), commander=commander_name)
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
            source_blob = s[len("Source(s):") :].strip()
            current_build.source_paths = [clean_text(item.strip()) for item in source_blob.split(",") if item.strip()]
            continue
        if s.startswith("Status:"):
            current_build.status = clean_text(s[len("Status:") :].strip())
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

        bullet = BULLET_RE.match(s)
        if not bullet:
            continue
        value = clean_text(bullet.group(1))
        if current_block == "commander":
            if value:
                current_build.commander = value
        elif current_block == "gcs":
            if value:
                current_build.game_changers.append(re.sub(r"\s*\(GC\)\s*$", "", value).strip())
        elif current_block == "deck" and current_category:
            current_build.deck_sections[current_category].cards.append(value)
        elif current_block == "summary":
            current_build.summary.append(value)
        elif current_block == "swaps":
            current_build.swaps.append(value)
        elif current_block == "validation":
            current_build.validation.append(value)

    return commander_name, builds


def package_name(gcs: list[str]) -> str:
    return " / ".join(gcs) if gcs else "No GCs listed"


def to_payload(builds: list[BuildFlavor]) -> dict:
    full_builds = [b for b in builds if b.full_99]
    commanders = sorted({b.commander for b in full_builds})
    levels = sorted({b.degeneracy_level for b in full_builds}, key=lambda x: ("Maximum" not in x, x))
    gc_cards = sorted({gc for b in full_builds for gc in b.game_changers})

    package_matrix: dict[str, dict[str, list[str]]] = {}
    for b in full_builds:
        package_matrix.setdefault(b.commander, {})
        package_matrix[b.commander].setdefault(package_name(b.game_changers), [])
        package_matrix[b.commander][package_name(b.game_changers)].append(b.build_id)
    for commander in package_matrix:
        for pkg in package_matrix[commander]:
            package_matrix[commander][pkg] = sorted(package_matrix[commander][pkg])

    build_payload: list[dict] = []
    for b in full_builds:
        build_payload.append(
            {
                "id": b.build_id,
                "title": b.title,
                "commander": b.commander,
                "status": b.status,
                "degeneracyLevel": b.degeneracy_level,
                "gameChangers": b.game_changers,
                "totalCards": b.total_cards,
                "sources": b.source_paths,
                "summary": b.summary,
                "swaps": b.swaps,
                "validation": b.validation,
                "deckSections": [
                    {
                        "name": name,
                        "declared": section.declared_count,
                        "cards": section.cards,
                    }
                    for name, section in b.deck_sections.items()
                ],
            }
        )

    build_payload.sort(key=lambda x: (x["commander"], x["id"]))

    if len(commanders) == 1:
        page_title = f"{commanders[0]} Deck Companion"
    else:
        page_title = "Sultai Commander Deck Companion"

    return {
        "meta": {
            "generatedAtUtc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "buildCount": len(build_payload),
            "commanderCount": len(commanders),
            "pageTitle": page_title,
        },
        "filters": {
            "commanders": commanders,
            "levels": levels,
            "gcCards": gc_cards,
        },
        "packageMatrix": package_matrix,
        "builds": build_payload,
    }


def render_html(payload: dict) -> str:
    json_payload = json.dumps(payload, ensure_ascii=True)
    title = str(payload.get("meta", {}).get("pageTitle") or "Sultai Commander Deck Companion")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      --bg: #f6f8f6;
      --bg-2: #eef2ee;
      --panel: #ffffff;
      --ink: #122019;
      --muted: #4d5b53;
      --line: #d6dfd8;
      --accent: #0f7a63;
      --accent-2: #d8f2ea;
      --max: #8b1e3f;
      --max-soft: #f6dbe3;
      --tuned: #2e5c8a;
      --tuned-soft: #dbe9f7;
      --mono: "IBM Plex Mono", "SFMono-Regular", Menlo, Consolas, monospace;
      --sans: "Space Grotesk", "Avenir Next", "Segoe UI", sans-serif;
      --radius: 14px;
      --shadow: 0 12px 28px rgba(18, 32, 25, 0.08);
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      font-family: var(--sans);
      color: var(--ink);
      background:
        radial-gradient(1200px 700px at 10% -10%, #d9efe6 0%, transparent 55%),
        radial-gradient(900px 520px at 92% -15%, #e8efdd 0%, transparent 45%),
        linear-gradient(170deg, var(--bg) 0%, var(--bg-2) 100%);
      min-height: 100vh;
    }}

    .shell {{
      width: min(1380px, 96vw);
      margin: 22px auto 34px;
      display: grid;
      gap: 14px;
      grid-template-columns: 340px 1fr;
    }}

    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }}

    .left {{
      display: grid;
      grid-template-rows: auto auto 1fr;
      gap: 12px;
      align-self: start;
      position: sticky;
      top: 14px;
    }}

    .hero {{
      padding: 16px 16px 14px;
      background:
        linear-gradient(150deg, #f8fbf8 0%, #ebf6f1 60%, #f7fcf9 100%);
    }}

    h1 {{
      margin: 0;
      font-size: 1.3rem;
      letter-spacing: 0.01em;
    }}

    .meta {{
      margin-top: 8px;
      color: var(--muted);
      font-size: 0.86rem;
      line-height: 1.45;
    }}

    .controls {{
      padding: 14px 14px 8px;
      display: grid;
      gap: 10px;
    }}

    .control-row {{
      display: grid;
      gap: 6px;
    }}

    label {{
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
      font-weight: 700;
    }}

    select, input[type="search"] {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 10px;
      background: #fcfffc;
      padding: 9px 10px;
      font: inherit;
      color: var(--ink);
    }}

    .gc-chip-wrap {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      max-height: 136px;
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 8px;
      background: #fcfffc;
    }}

    .gc-chip {{
      border: 1px solid #bfd4ca;
      background: #f4faf7;
      color: #164234;
      border-radius: 999px;
      font-size: 0.72rem;
      padding: 3px 8px;
      cursor: pointer;
      user-select: none;
      transition: 110ms ease;
    }}

    .gc-chip[aria-pressed="true"] {{
      background: #0f7a63;
      border-color: #0f7a63;
      color: #fff;
    }}

    .build-list {{
      padding: 10px;
      display: grid;
      gap: 8px;
      max-height: 56vh;
      overflow: auto;
    }}

    .build-btn {{
      border: 1px solid var(--line);
      background: #fff;
      text-align: left;
      border-radius: 12px;
      padding: 10px;
      cursor: pointer;
      display: grid;
      gap: 6px;
      transition: 110ms ease;
    }}

    .build-btn:hover {{
      border-color: #8eb7a7;
    }}

    .build-btn.active {{
      border-color: var(--accent);
      box-shadow: inset 0 0 0 1px var(--accent);
      background: #f4fbf8;
    }}

    .build-head {{
      display: flex;
      justify-content: space-between;
      gap: 8px;
      align-items: center;
    }}

    .build-id {{
      font-family: var(--mono);
      font-size: 0.84rem;
      color: #1a3a30;
      font-weight: 700;
    }}

    .badge {{
      display: inline-block;
      border-radius: 999px;
      padding: 2px 8px;
      font-size: 0.68rem;
      font-weight: 700;
      letter-spacing: 0.03em;
      text-transform: uppercase;
      border: 1px solid transparent;
    }}

    .badge.max {{
      background: var(--max-soft);
      border-color: #e7afc1;
      color: #6b1731;
    }}

    .badge.tuned {{
      background: var(--tuned-soft);
      border-color: #abc8e5;
      color: #214b76;
    }}

    .build-title {{
      font-size: 0.88rem;
      line-height: 1.3;
      color: #233a31;
    }}

    .build-sub {{
      color: var(--muted);
      font-size: 0.76rem;
    }}

    .main {{
      padding: 16px;
      display: grid;
      gap: 14px;
    }}

    .matrix {{
      padding: 14px;
    }}

    .matrix h2 {{
      margin: 0 0 10px;
      font-size: 1rem;
    }}

    .matrix-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.86rem;
    }}

    .matrix-table th, .matrix-table td {{
      border-bottom: 1px solid var(--line);
      text-align: left;
      padding: 8px 6px;
      vertical-align: top;
    }}

    .matrix-table th {{
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
    }}

    .detail {{
      padding: 14px;
      display: grid;
      gap: 12px;
    }}

    .detail h2 {{
      margin: 0;
      font-size: 1.26rem;
      line-height: 1.2;
    }}

    .detail-top {{
      display: grid;
      gap: 8px;
    }}

    .pill-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }}

    .pill {{
      background: var(--accent-2);
      border: 1px solid #a6dcca;
      color: #174837;
      border-radius: 999px;
      padding: 3px 8px;
      font-size: 0.74rem;
      font-weight: 600;
    }}

    .sources {{
      font-size: 0.78rem;
      color: var(--muted);
      line-height: 1.4;
    }}

    .deck-search-wrap {{
      display: grid;
      gap: 6px;
    }}

    .deck-grid {{
      display: grid;
      gap: 10px;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    }}

    .section-card {{
      border: 1px solid var(--line);
      border-radius: 12px;
      background: #fcfffd;
      padding: 10px;
      min-height: 150px;
      display: grid;
      gap: 8px;
      align-content: start;
    }}

    .section-head {{
      display: flex;
      justify-content: space-between;
      gap: 8px;
      align-items: baseline;
      border-bottom: 1px solid #edf3ef;
      padding-bottom: 6px;
    }}

    .section-name {{
      font-weight: 700;
      font-size: 0.84rem;
    }}

    .section-count {{
      font-size: 0.74rem;
      color: var(--muted);
      font-family: var(--mono);
    }}

    .cards {{
      list-style: none;
      margin: 0;
      padding: 0;
      display: grid;
      gap: 3px;
      font-size: 0.8rem;
      line-height: 1.35;
    }}

    .cards li {{
      border-radius: 6px;
      padding: 1px 4px;
    }}

    .cards li.hit {{
      background: #fff4bf;
    }}

    .two-col {{
      display: grid;
      gap: 10px;
      grid-template-columns: 1fr 1fr;
    }}

    .note-card {{
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 10px;
      background: #fcfffd;
      min-height: 120px;
    }}

    .note-card h3 {{
      margin: 0 0 7px;
      font-size: 0.86rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--muted);
    }}

    .note-card ul {{
      margin: 0;
      padding-left: 16px;
      display: grid;
      gap: 4px;
      font-size: 0.83rem;
      line-height: 1.35;
    }}

    .empty {{
      border: 1px dashed var(--line);
      border-radius: 12px;
      padding: 18px;
      color: var(--muted);
      text-align: center;
      background: #fbfdfb;
    }}

    @media (max-width: 1040px) {{
      .shell {{
        grid-template-columns: 1fr;
      }}
      .left {{
        position: static;
      }}
      .build-list {{
        max-height: 340px;
      }}
    }}

    @media (prefers-reduced-motion: reduce) {{
      * {{
        transition: none !important;
      }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <aside class="left">
      <section class="panel hero">
        <h1>{html.escape(title)}</h1>
        <div class="meta" id="meta"></div>
      </section>

      <section class="panel controls" aria-label="Filters">
        <div class="control-row">
          <label for="commanderFilter">Commander</label>
          <select id="commanderFilter"></select>
        </div>
        <div class="control-row">
          <label for="levelFilter">Degeneracy Level</label>
          <select id="levelFilter"></select>
        </div>
        <div class="control-row">
          <label for="textFilter">Build/Card Search</label>
          <input id="textFilter" type="search" placeholder="type card or build id">
        </div>
        <div class="control-row">
          <label>Game Changer Filter (must include all selected)</label>
          <div id="gcFilterWrap" class="gc-chip-wrap"></div>
        </div>
      </section>

      <section class="panel build-list" id="buildList" aria-label="Build list"></section>
    </aside>

    <main class="main">
      <section class="panel matrix">
        <h2>Game Changer Package Matrix</h2>
        <table class="matrix-table" id="matrixTable">
          <thead>
            <tr><th>Commander</th><th>GC Package</th><th>Builds</th></tr>
          </thead>
          <tbody></tbody>
        </table>
      </section>

      <section class="panel detail" id="detail"></section>
    </main>
  </div>

  <script>
    const DATA = {json_payload};

    const state = {{
      commander: "All",
      level: "All",
      query: "",
      selectedGCs: new Set(),
      selectedBuildId: null,
      deckSearch: "",
    }};

    const commanderFilter = document.getElementById("commanderFilter");
    const levelFilter = document.getElementById("levelFilter");
    const textFilter = document.getElementById("textFilter");
    const gcFilterWrap = document.getElementById("gcFilterWrap");
    const buildList = document.getElementById("buildList");
    const detail = document.getElementById("detail");
    const matrixBody = document.querySelector("#matrixTable tbody");
    const meta = document.getElementById("meta");

    function badgeClass(level) {{
      return level.startsWith("Maximum") ? "max" : "tuned";
    }}

    function setMeta() {{
      meta.innerHTML = `
        <div><strong>${{DATA.meta.buildCount}}</strong> full 99 builds across <strong>${{DATA.meta.commanderCount}}</strong> commanders.</div>
        <div>Snapshot: ${{DATA.meta.generatedAtUtc}}</div>
      `;
    }}

    function fillFilters() {{
      commanderFilter.innerHTML = `<option>All</option>` + DATA.filters.commanders.map(c => `<option>${{c}}</option>`).join("");
      levelFilter.innerHTML = `<option>All</option>` + DATA.filters.levels.map(l => `<option>${{l}}</option>`).join("");
      gcFilterWrap.innerHTML = DATA.filters.gcCards.map(gc => `<button class="gc-chip" data-gc="${{gc}}" aria-pressed="false">${{gc}}</button>`).join("");
    }}

    function renderMatrix() {{
      const rows = [];
      Object.keys(DATA.packageMatrix).sort().forEach(commander => {{
        const packages = DATA.packageMatrix[commander];
        Object.keys(packages).sort().forEach(pkg => {{
          rows.push(
            `<tr>
              <td>${{commander}}</td>
              <td>${{pkg}}</td>
              <td>${{packages[pkg].join(", ")}}</td>
            </tr>`
          );
        }});
      }});
      matrixBody.innerHTML = rows.join("");
    }}

    function buildMatches(build) {{
      if (state.commander !== "All" && build.commander !== state.commander) return false;
      if (state.level !== "All" && build.degeneracyLevel !== state.level) return false;

      if (state.selectedGCs.size) {{
        const gcSet = new Set(build.gameChangers);
        for (const gc of state.selectedGCs) {{
          if (!gcSet.has(gc)) return false;
        }}
      }}

      if (state.query) {{
        const q = state.query.toLowerCase();
        const haystack = [
          build.id,
          build.title,
          build.commander,
          build.status,
          ...build.gameChangers,
          ...build.deckSections.flatMap(s => s.cards),
        ].join(" ").toLowerCase();
        if (!haystack.includes(q)) return false;
      }}
      return true;
    }}

    function filteredBuilds() {{
      return DATA.builds.filter(buildMatches);
    }}

    function renderBuildList() {{
      const builds = filteredBuilds();
      if (!builds.length) {{
        buildList.innerHTML = `<div class="empty">No builds match current filters.</div>`;
        detail.innerHTML = `<div class="empty">Adjust filters to select a build.</div>`;
        return;
      }}

      if (!state.selectedBuildId || !builds.some(b => b.id === state.selectedBuildId)) {{
        state.selectedBuildId = builds[0].id;
      }}

      buildList.innerHTML = builds.map(b => `
        <button class="build-btn ${{b.id === state.selectedBuildId ? "active" : ""}}" data-build="${{b.id}}">
          <div class="build-head">
            <span class="build-id">${{b.id}}</span>
            <span class="badge ${{badgeClass(b.degeneracyLevel)}}">${{b.degeneracyLevel}}</span>
          </div>
          <div class="build-title">${{b.title}}</div>
          <div class="build-sub">${{b.commander}} | ${{b.totalCards}} cards</div>
        </button>
      `).join("");
      renderDetail();
    }}

    function escapeHtml(s) {{
      return s
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;");
    }}

    function renderDeckSectionCards(cards, query) {{
      const q = query.trim().toLowerCase();
      return cards.map(card => {{
        const hit = q && card.toLowerCase().includes(q);
        return `<li class="${{hit ? "hit" : ""}}">${{escapeHtml(card)}}</li>`;
      }}).join("");
    }}

    function renderDetail() {{
      const build = DATA.builds.find(b => b.id === state.selectedBuildId);
      if (!build) {{
        detail.innerHTML = `<div class="empty">No build selected.</div>`;
        return;
      }}

      const deckSectionsHtml = build.deckSections.map(section => `
        <article class="section-card">
          <div class="section-head">
            <div class="section-name">${{section.name}}</div>
            <div class="section-count">${{section.cards.length}} / declared ${{section.declared}}</div>
          </div>
          <ul class="cards">${{renderDeckSectionCards(section.cards, state.deckSearch)}}</ul>
        </article>
      `).join("");

      detail.innerHTML = `
        <div class="detail-top">
          <h2>${{build.id}} — ${{escapeHtml(build.title)}}</h2>
          <div class="pill-row">
            <span class="badge ${{badgeClass(build.degeneracyLevel)}}">${{build.degeneracyLevel}}</span>
            <span class="pill">${{escapeHtml(build.commander)}}</span>
            <span class="pill">${{build.totalCards}} cards</span>
            <span class="pill">${{escapeHtml(build.status || "status not listed")}}</span>
          </div>
          <div class="pill-row">
            ${{build.gameChangers.map(gc => `<span class="pill">${{escapeHtml(gc)}}</span>`).join("")}}
          </div>
          <div class="sources"><strong>Sources:</strong> ${{build.sources.length ? build.sources.map(escapeHtml).join(", ") : "not listed"}}</div>
        </div>

        <div class="deck-search-wrap">
          <label for="deckSearch">Highlight cards in decklist</label>
          <input id="deckSearch" type="search" placeholder="search inside selected deck" value="${{escapeHtml(state.deckSearch)}}">
        </div>

        <div class="deck-grid">${{deckSectionsHtml}}</div>

        <div class="two-col">
          <section class="note-card">
            <h3>Summary / Win Plan</h3>
            <ul>${{(build.summary.length ? build.summary : ["No summary bullets listed."]).map(x => `<li>${{escapeHtml(x)}}</li>`).join("")}}</ul>
          </section>
          <section class="note-card">
            <h3>Swaps / Variants</h3>
            <ul>${{(build.swaps.length ? build.swaps : ["No swaps listed."]).map(x => `<li>${{escapeHtml(x)}}</li>`).join("")}}</ul>
          </section>
        </div>

        <section class="note-card">
          <h3>Validation Notes</h3>
          <ul>${{(build.validation.length ? build.validation : ["No validation notes listed."]).map(x => `<li>${{escapeHtml(x)}}</li>`).join("")}}</ul>
        </section>
      `;
    }}

    function wireEvents() {{
      commanderFilter.addEventListener("change", e => {{
        state.commander = e.target.value;
        renderBuildList();
      }});
      levelFilter.addEventListener("change", e => {{
        state.level = e.target.value;
        renderBuildList();
      }});
      textFilter.addEventListener("input", e => {{
        state.query = e.target.value.trim();
        renderBuildList();
      }});
      gcFilterWrap.addEventListener("click", e => {{
        const chip = e.target.closest(".gc-chip");
        if (!chip) return;
        const gc = chip.getAttribute("data-gc");
        if (state.selectedGCs.has(gc)) {{
          state.selectedGCs.delete(gc);
          chip.setAttribute("aria-pressed", "false");
        }} else {{
          state.selectedGCs.add(gc);
          chip.setAttribute("aria-pressed", "true");
        }}
        renderBuildList();
      }});
      buildList.addEventListener("click", e => {{
        const btn = e.target.closest(".build-btn");
        if (!btn) return;
        state.selectedBuildId = btn.getAttribute("data-build");
        renderBuildList();
      }});
      detail.addEventListener("input", e => {{
        if (e.target && e.target.id === "deckSearch") {{
          state.deckSearch = e.target.value;
          renderDetail();
        }}
      }});
    }}

    function init() {{
      setMeta();
      fillFilters();
      renderMatrix();
      wireEvents();
      renderBuildList();
    }}

    init();
  </script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate interactive HTML companion for Sultai commander deck references.")
    parser.add_argument(
        "--docs",
        nargs="+",
        required=True,
        help="Input commander reference markdown docs.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Output HTML file path.",
    )
    args = parser.parse_args()

    all_builds: list[BuildFlavor] = []
    for doc in args.docs:
        _, builds = parse_reference(Path(doc))
        all_builds.extend(builds)

    payload = to_payload(all_builds)
    html_text = render_html(payload)
    args.out.write_text(html_text, encoding="utf-8")
    print(f"Wrote {args.out} with {payload['meta']['buildCount']} full builds.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
