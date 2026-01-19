# Phase 1: Foundation (Ontology + Data) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Expand the ontology with subtypes and new properties, download precon data, and calculate popularity scores.

**Architecture:** Add subtype parsing to card loading, download MTGJSON deck files, combine EDHREC rank with precon frequency into a unified popularity score stored on card nodes.

**Tech Stack:** Python, Neo4j, MTGJSON AllDeckFiles

---

## Task 1: Add Subtype Extraction

**Files:**
- Modify: `src/parsing/properties.py`
- Test: `tests/unit/test_properties.py`

**Step 1: Write the failing test**

Add to `tests/unit/test_properties.py`:

```python
def test_extract_subtypes_creature():
    """Test subtype extraction from creature type line."""
    type_line = "Legendary Creature — Elf Druid"
    result = PropertyCalculator.extract_subtypes(type_line)
    assert result == ["Elf", "Druid"]


def test_extract_subtypes_land():
    """Test subtype extraction from land type line."""
    type_line = "Basic Land — Island"
    result = PropertyCalculator.extract_subtypes(type_line)
    assert result == ["Island"]


def test_extract_subtypes_no_subtypes():
    """Test cards without subtypes."""
    type_line = "Instant"
    result = PropertyCalculator.extract_subtypes(type_line)
    assert result == []


def test_extract_subtypes_artifact_creature():
    """Test artifact creature subtypes."""
    type_line = "Artifact Creature — Golem"
    result = PropertyCalculator.extract_subtypes(type_line)
    assert result == ["Golem"]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_properties.py::test_extract_subtypes_creature -v`
Expected: FAIL with "AttributeError: type object 'PropertyCalculator' has no attribute 'extract_subtypes'"

**Step 3: Write minimal implementation**

Add to `src/parsing/properties.py` in the `PropertyCalculator` class:

```python
@staticmethod
def extract_subtypes(type_line: str) -> list[str]:
    """Extract subtypes from card type line.

    Examples:
        "Legendary Creature — Elf Druid" -> ["Elf", "Druid"]
        "Basic Land — Island" -> ["Island"]
        "Instant" -> []
    """
    if not type_line or "—" not in type_line:
        return []

    # Split on em dash and take everything after
    parts = type_line.split("—")
    if len(parts) < 2:
        return []

    subtypes_str = parts[1].strip()
    if not subtypes_str:
        return []

    return subtypes_str.split()
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/unit/test_properties.py -v -k "subtype"`
Expected: 4 tests PASS

**Step 5: Commit**

```bash
git add src/parsing/properties.py tests/unit/test_properties.py
git commit -m "feat: add subtype extraction from type_line"
```

---

## Task 2: Add Subtypes to Enrichment Pipeline

**Files:**
- Modify: `src/parsing/enrichment.py`
- Test: `tests/integration/test_enrichment.py`

**Step 1: Write the failing test**

Add to `tests/integration/test_enrichment.py`:

```python
def test_enrichment_adds_subtypes():
    """Test that enrichment extracts subtypes from type_line."""
    from src.parsing.enrichment import enrich_card_data

    cards = [
        {
            "name": "Llanowar Elves",
            "mana_cost": "{G}",
            "cmc": 1,
            "type_line": "Creature — Elf Druid",
            "oracle_text": "{T}: Add {G}.",
            "color_identity": ["G"],
            "colors": ["G"],
            "keywords": [],
            "is_legendary": False,
            "is_reserved_list": False,
            "can_be_commander": False,
        }
    ]

    enriched = enrich_card_data(cards)

    assert enriched[0]["subtypes"] == ["Elf", "Druid"]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_enrichment.py::test_enrichment_adds_subtypes -v`
Expected: FAIL with "KeyError: 'subtypes'"

**Step 3: Write minimal implementation**

Modify `src/parsing/enrichment.py` in the `enrich_card_data` function, add after `is_free_spell`:

```python
        card["subtypes"] = PropertyCalculator.extract_subtypes(
            card.get("type_line", "")
        )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/integration/test_enrichment.py::test_enrichment_adds_subtypes -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/parsing/enrichment.py tests/integration/test_enrichment.py
git commit -m "feat: add subtypes to enrichment pipeline"
```

---

## Task 3: Create Subtype Nodes and Relationships in Graph

**Files:**
- Modify: `src/graph/loaders.py`
- Modify: `src/graph/connection.py`
- Test: `tests/integration/test_graph_loaders_mock.py`

**Step 1: Add constraint for Subtype nodes**

Add to `src/graph/connection.py` in the `create_constraints` method, add to the constraints list:

```python
"CREATE CONSTRAINT subtype_name IF NOT EXISTS FOR (s:Subtype) REQUIRE s.name IS UNIQUE",
```

**Step 2: Write the failing test**

Add to `tests/integration/test_graph_loaders_mock.py`:

```python
from src.graph.loaders import create_subtype_relationships


def test_create_subtype_relationships():
    """Test subtype relationship creation."""
    mock_conn = Mock(spec=Neo4jConnection)

    card_data = {
        "name": "Llanowar Elves",
        "subtypes": ["Elf", "Druid"]
    }

    create_subtype_relationships(mock_conn, card_data)

    # Should call execute_query 4 times: 2 MERGE subtypes + 2 relationships
    assert mock_conn.execute_query.call_count == 4

    # Verify HAS_SUBTYPE relationship created
    calls = mock_conn.execute_query.call_args_list
    # Check that relationship queries contain HAS_SUBTYPE
    relationship_queries = [c[0][0] for c in calls if "HAS_SUBTYPE" in c[0][0]]
    assert len(relationship_queries) == 2
```

**Step 3: Run test to verify it fails**

Run: `pytest tests/integration/test_graph_loaders_mock.py::test_create_subtype_relationships -v`
Expected: FAIL with "ImportError: cannot import name 'create_subtype_relationships'"

**Step 4: Write minimal implementation**

Add to `src/graph/loaders.py`:

```python
def create_subtype_relationships(conn: Neo4jConnection, card_data: dict):
    """Create [:HAS_SUBTYPE] relationships."""

    card_name = card_data["name"]
    subtypes = card_data.get("subtypes", [])

    for subtype in subtypes:
        # Create subtype node if doesn't exist
        query_subtype = """
        MERGE (s:Subtype {name: $subtype_name})
        """
        conn.execute_query(query_subtype, {"subtype_name": subtype})

        # Create relationship
        query_rel = """
        MATCH (c:Card {name: $card_name})
        MATCH (s:Subtype {name: $subtype_name})
        MERGE (c)-[:HAS_SUBTYPE]->(s)
        """

        conn.execute_query(query_rel, {
            "card_name": card_name,
            "subtype_name": subtype
        })
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/integration/test_graph_loaders_mock.py::test_create_subtype_relationships -v`
Expected: PASS

**Step 6: Commit**

```bash
git add src/graph/loaders.py src/graph/connection.py tests/integration/test_graph_loaders_mock.py
git commit -m "feat: add Subtype nodes and HAS_SUBTYPE relationships"
```

---

## Task 4: Create Precon Downloader

**Files:**
- Create: `src/data/precon_downloader.py`
- Test: `tests/unit/test_precon_downloader.py`

**Step 1: Write the failing test**

Create `tests/unit/test_precon_downloader.py`:

```python
"""Unit tests for precon downloader."""

import os
import tempfile
from unittest.mock import patch, Mock
from src.data.precon_downloader import PreconDownloader


def test_precon_downloader_url():
    """Test that downloader has correct URL."""
    assert PreconDownloader.DECK_URL == "https://mtgjson.com/api/v5/AllDeckFiles.zip"


def test_precon_downloader_creates_directory():
    """Test that downloader creates data directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        downloader = PreconDownloader(data_dir=tmpdir)
        deck_dir = os.path.join(tmpdir, "decks")

        # Directory should be created
        assert os.path.exists(tmpdir)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_precon_downloader.py::test_precon_downloader_url -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.data.precon_downloader'"

**Step 3: Write minimal implementation**

Create `src/data/precon_downloader.py`:

```python
"""Download and extract MTGJSON deck files."""

import os
import zipfile
import requests
from pathlib import Path


class PreconDownloader:
    """Download and manage MTGJSON deck files."""

    DECK_URL = "https://mtgjson.com/api/v5/AllDeckFiles.zip"

    def __init__(self, data_dir: str = "data"):
        """Initialize downloader with data directory."""
        self.data_dir = Path(data_dir)
        self.deck_dir = self.data_dir / "decks"
        self.zip_path = self.data_dir / "AllDeckFiles.zip"

        # Create directories
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def download(self) -> Path:
        """Download AllDeckFiles.zip if not present."""
        if self.zip_path.exists():
            print(f"✓ {self.zip_path.name} already exists, skipping download")
            return self.zip_path

        print(f"Downloading {self.zip_path.name}...")

        response = requests.get(self.DECK_URL, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(self.zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\r  Progress: {percent:.1f}%", end='')

        print(f"\n✓ Downloaded {self.zip_path.name}")
        return self.zip_path

    def extract(self) -> Path:
        """Extract deck files from zip."""
        if self.deck_dir.exists() and any(self.deck_dir.iterdir()):
            print(f"✓ Decks already extracted to {self.deck_dir}")
            return self.deck_dir

        if not self.zip_path.exists():
            self.download()

        print(f"Extracting to {self.deck_dir}...")
        self.deck_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.deck_dir)

        print(f"✓ Extracted deck files")
        return self.deck_dir

    def download_and_extract(self) -> Path:
        """Download and extract deck files."""
        self.download()
        return self.extract()
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/unit/test_precon_downloader.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/data/precon_downloader.py tests/unit/test_precon_downloader.py
git commit -m "feat: add precon downloader for MTGJSON deck files"
```

---

## Task 5: Create Precon Parser

**Files:**
- Create: `src/data/precon_parser.py`
- Test: `tests/unit/test_precon_parser.py`

**Step 1: Create test fixture**

Create `tests/fixtures/decks/test_commander_deck.json`:

```json
{
  "name": "Test Commander Deck",
  "type": "Commander",
  "mainBoard": [
    {"name": "Sol Ring", "count": 1},
    {"name": "Command Tower", "count": 1},
    {"name": "Eternal Witness", "count": 1}
  ],
  "commander": [
    {"name": "Muldrotha, the Gravetide", "count": 1}
  ]
}
```

Create `tests/fixtures/decks/test_standard_deck.json`:

```json
{
  "name": "Test Standard Deck",
  "type": "Standard",
  "mainBoard": [
    {"name": "Lightning Bolt", "count": 4}
  ]
}
```

**Step 2: Write the failing test**

Create `tests/unit/test_precon_parser.py`:

```python
"""Unit tests for precon parser."""

import os
from src.data.precon_parser import PreconParser


def test_parse_commander_deck():
    """Test parsing a single Commander deck."""
    parser = PreconParser()
    counts = parser.parse_all_decks("tests/fixtures/decks")

    # Should count cards from Commander deck only
    assert counts.get("Sol Ring", 0) == 1
    assert counts.get("Command Tower", 0) == 1
    assert counts.get("Eternal Witness", 0) == 1

    # Commander should be counted
    assert counts.get("Muldrotha, the Gravetide", 0) == 1

    # Standard deck cards should NOT be counted
    assert counts.get("Lightning Bolt", 0) == 0


def test_parse_returns_total_precon_count():
    """Test that parser returns total precon count."""
    parser = PreconParser()
    counts, total = parser.parse_all_decks_with_total("tests/fixtures/decks")

    assert total == 1  # Only 1 Commander deck
```

**Step 3: Run test to verify it fails**

Run: `pytest tests/unit/test_precon_parser.py::test_parse_commander_deck -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.data.precon_parser'"

**Step 4: Write minimal implementation**

Create `src/data/precon_parser.py`:

```python
"""Parse MTGJSON deck files and count card appearances."""

import json
from pathlib import Path
from collections import defaultdict


class PreconParser:
    """Parse preconstructed deck files."""

    def parse_all_decks(self, deck_dir: str) -> dict[str, int]:
        """Parse all Commander decks and return card appearance counts.

        Args:
            deck_dir: Directory containing deck JSON files

        Returns:
            Dictionary mapping card names to appearance counts
        """
        counts, _ = self.parse_all_decks_with_total(deck_dir)
        return counts

    def parse_all_decks_with_total(self, deck_dir: str) -> tuple[dict[str, int], int]:
        """Parse all Commander decks and return counts with total deck count.

        Returns:
            Tuple of (card_counts, total_commander_decks)
        """
        deck_path = Path(deck_dir)
        counts = defaultdict(int)
        total_decks = 0

        if not deck_path.exists():
            return dict(counts), 0

        for deck_file in deck_path.glob("*.json"):
            try:
                with open(deck_file, 'r', encoding='utf-8') as f:
                    deck = json.load(f)

                # Only count Commander decks
                if deck.get("type") != "Commander":
                    continue

                total_decks += 1

                # Count mainboard cards
                for card in deck.get("mainBoard", []):
                    name = card.get("name")
                    if name:
                        counts[name] += 1

                # Count commander(s)
                for card in deck.get("commander", []):
                    name = card.get("name")
                    if name:
                        counts[name] += 1

            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not parse {deck_file}: {e}")
                continue

        return dict(counts), total_decks
```

**Step 5: Run tests to verify they pass**

Run: `pytest tests/unit/test_precon_parser.py -v`
Expected: PASS

**Step 6: Commit**

```bash
mkdir -p tests/fixtures/decks
git add src/data/precon_parser.py tests/unit/test_precon_parser.py tests/fixtures/decks/
git commit -m "feat: add precon parser for card appearance counting"
```

---

## Task 6: Create Popularity Calculator

**Files:**
- Create: `src/data/popularity.py`
- Test: `tests/unit/test_popularity.py`

**Step 1: Write the failing test**

Create `tests/unit/test_popularity.py`:

```python
"""Unit tests for popularity score calculation."""

from src.data.popularity import PopularityCalculator


def test_calculate_popularity_high_rank_high_precon():
    """Test card with good EDHREC rank and high precon count."""
    calc = PopularityCalculator(total_precons=100)

    # Rank 100 out of 20000, appears in 50 precons
    score = calc.calculate(edhrec_rank=100, precon_count=50)

    # Should be high (close to 1.0)
    assert score > 0.8


def test_calculate_popularity_no_rank():
    """Test card with no EDHREC rank."""
    calc = PopularityCalculator(total_precons=100)

    # No rank (None), appears in 10 precons
    score = calc.calculate(edhrec_rank=None, precon_count=10)

    # Should use default 0.5 for EDHREC component
    assert 0.3 < score < 0.6


def test_calculate_popularity_low_rank():
    """Test card with bad EDHREC rank."""
    calc = PopularityCalculator(total_precons=100)

    # Very bad rank, no precon appearances
    score = calc.calculate(edhrec_rank=20000, precon_count=0)

    # Should be very low
    assert score < 0.1


def test_calculate_popularity_weights():
    """Test that EDHREC is weighted higher than precon."""
    calc = PopularityCalculator(total_precons=100)

    # Good rank, no precons vs bad rank, many precons
    score_good_rank = calc.calculate(edhrec_rank=100, precon_count=0)
    score_many_precons = calc.calculate(edhrec_rank=15000, precon_count=100)

    # Good EDHREC rank should win (0.7 weight)
    assert score_good_rank > score_many_precons
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_popularity.py::test_calculate_popularity_high_rank_high_precon -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.data.popularity'"

**Step 3: Write minimal implementation**

Create `src/data/popularity.py`:

```python
"""Calculate combined popularity scores from EDHREC rank and precon frequency."""


class PopularityCalculator:
    """Calculate card popularity scores."""

    MAX_EDHREC_RANK = 20000  # Normalization cap
    EDHREC_WEIGHT = 0.7
    PRECON_WEIGHT = 0.3

    def __init__(self, total_precons: int):
        """Initialize with total precon count for normalization.

        Args:
            total_precons: Total number of Commander precons parsed
        """
        self.total_precons = total_precons

    def calculate(self, edhrec_rank: int | None, precon_count: int) -> float:
        """Calculate combined popularity score.

        Args:
            edhrec_rank: EDHREC popularity rank (lower = more popular), or None
            precon_count: Number of precons this card appears in

        Returns:
            Float between 0.0 and 1.0 (higher = more popular)
        """
        # Normalize EDHREC rank (invert so higher = better)
        if edhrec_rank is None:
            edhrec_score = 0.5  # Default for unranked cards
        else:
            edhrec_score = max(0, 1 - (edhrec_rank / self.MAX_EDHREC_RANK))

        # Precon frequency (already 0-1 range)
        if self.total_precons > 0:
            precon_score = precon_count / self.total_precons
        else:
            precon_score = 0

        # Weighted combination
        return self.EDHREC_WEIGHT * edhrec_score + self.PRECON_WEIGHT * precon_score
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/unit/test_popularity.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/data/popularity.py tests/unit/test_popularity.py
git commit -m "feat: add popularity score calculator"
```

---

## Task 7: Integrate Popularity into Graph Loading

**Files:**
- Modify: `src/graph/loaders.py`
- Test: `tests/integration/test_graph_loaders_mock.py`

**Step 1: Write the failing test**

Add to `tests/integration/test_graph_loaders_mock.py`:

```python
def test_load_card_includes_popularity_score():
    """Test that card loading includes popularity_score property."""
    mock_conn = Mock(spec=Neo4jConnection)

    card_data = {
        "name": "Sol Ring",
        "mana_cost": "{1}",
        "cmc": 1,
        "type_line": "Artifact",
        "oracle_text": "{T}: Add {C}{C}.",
        "color_identity": [],
        "colors": [],
        "keywords": [],
        "is_legendary": False,
        "is_reserved_list": False,
        "can_be_commander": False,
        "edhrec_rank": 1,
        "functional_categories": ["ramp"],
        "mechanics": [],
        "mana_efficiency": 0.5,
        "color_pip_intensity": 0,
        "is_free_spell": False,
        "is_fast_mana": True,
        "subtypes": [],
        "popularity_score": 0.95,
        "precon_count": 50
    }

    load_card_to_graph(mock_conn, card_data)

    # Verify the query includes popularity fields
    call_args = mock_conn.execute_query.call_args
    params = call_args[0][1]

    assert params["popularity_score"] == 0.95
    assert params["precon_count"] == 50
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_graph_loaders_mock.py::test_load_card_includes_popularity_score -v`
Expected: FAIL with "KeyError: 'popularity_score'"

**Step 3: Modify load_card_to_graph**

In `src/graph/loaders.py`, update the `load_card_to_graph` function:

1. Add to the SET clause in the query:
```python
        c.subtypes = $subtypes,
        c.popularity_score = $popularity_score,
        c.precon_count = $precon_count
```

2. Add to the params dict:
```python
        "subtypes": card_data.get("subtypes", []),
        "popularity_score": card_data.get("popularity_score", 0.0),
        "precon_count": card_data.get("precon_count", 0),
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/integration/test_graph_loaders_mock.py::test_load_card_includes_popularity_score -v`
Expected: PASS

**Step 5: Run all tests to ensure no regressions**

Run: `pytest tests/unit tests/integration -v`
Expected: All PASS

**Step 6: Commit**

```bash
git add src/graph/loaders.py tests/integration/test_graph_loaders_mock.py
git commit -m "feat: add popularity_score and precon_count to card loading"
```

---

## Task 8: Create Main Enrichment with Popularity

**Files:**
- Create: `src/data/enrich_with_popularity.py`
- Test: `tests/integration/test_popularity_enrichment.py`

**Step 1: Write the failing test**

Create `tests/integration/test_popularity_enrichment.py`:

```python
"""Integration tests for popularity enrichment."""

from src.data.enrich_with_popularity import enrich_cards_with_popularity


def test_enrich_with_popularity():
    """Test that cards get popularity scores added."""
    cards = [
        {"name": "Sol Ring", "edhrec_rank": 1},
        {"name": "Island", "edhrec_rank": None},
    ]

    precon_counts = {
        "Sol Ring": 50,
        "Island": 100,
    }
    total_precons = 100

    enriched = enrich_cards_with_popularity(cards, precon_counts, total_precons)

    # Sol Ring should have high score
    sol_ring = next(c for c in enriched if c["name"] == "Sol Ring")
    assert sol_ring["popularity_score"] > 0.8
    assert sol_ring["precon_count"] == 50

    # Island has no rank but high precon count
    island = next(c for c in enriched if c["name"] == "Island")
    assert island["precon_count"] == 100
    assert "popularity_score" in island
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_popularity_enrichment.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

Create `src/data/enrich_with_popularity.py`:

```python
"""Enrich cards with popularity scores from precon data."""

from src.data.popularity import PopularityCalculator


def enrich_cards_with_popularity(
    cards: list[dict],
    precon_counts: dict[str, int],
    total_precons: int
) -> list[dict]:
    """Add popularity_score and precon_count to cards.

    Args:
        cards: List of card dictionaries
        precon_counts: Dictionary of card name -> precon appearance count
        total_precons: Total number of Commander precons

    Returns:
        Cards with added popularity_score and precon_count fields
    """
    calculator = PopularityCalculator(total_precons)

    for card in cards:
        name = card.get("name", "")
        edhrec_rank = card.get("edhrec_rank")
        precon_count = precon_counts.get(name, 0)

        card["precon_count"] = precon_count
        card["popularity_score"] = calculator.calculate(edhrec_rank, precon_count)

    return cards
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/integration/test_popularity_enrichment.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/data/enrich_with_popularity.py tests/integration/test_popularity_enrichment.py
git commit -m "feat: add popularity enrichment function"
```

---

## Task 9: Update Main Pipeline

**Files:**
- Modify: `main.py`

**Step 1: Add imports at top of main.py**

```python
from src.data.precon_downloader import PreconDownloader
from src.data.precon_parser import PreconParser
from src.data.enrich_with_popularity import enrich_cards_with_popularity
from src.graph.loaders import create_subtype_relationships
```

**Step 2: Add precon download phase after MTGJSON download**

After Phase 1 (Data Acquisition), add:

```python
    # Phase 1b: Download precon data
    print("\nPHASE 1b: Precon Data")
    print("-" * 60)

    precon_downloader = PreconDownloader(data_dir="data")
    precon_downloader.download_and_extract()

    print("\nParsing precon decks...")
    precon_parser = PreconParser()
    precon_counts, total_precons = precon_parser.parse_all_decks_with_total("data/decks")
    print(f"✓ Parsed {total_precons} Commander precons")
    print(f"✓ Found {len(precon_counts)} unique cards")
```

**Step 3: Add popularity enrichment after card enrichment**

After `enriched_cards = enrich_card_data(cards)`, add:

```python
    # Add popularity scores
    print("\nAdding popularity scores...")
    enriched_cards = enrich_cards_with_popularity(
        enriched_cards, precon_counts, total_precons
    )
    print("✓ Added popularity scores")
```

**Step 4: Add subtype relationship creation in Phase 6**

In the relationship creation section, add:

```python
    print("\nCreating subtype relationships...")
    for i, card in enumerate(enriched_cards):
        create_subtype_relationships(conn, card)
        if (i + 1) % 1000 == 0:
            print(f"  Processed {i + 1}/{len(enriched_cards)}...")
    print("✓ Created subtype relationships")
```

**Step 5: Run main.py to verify it works**

Run: `python main.py`
Expected: Pipeline runs with new phases

**Step 6: Commit**

```bash
git add main.py
git commit -m "feat: integrate popularity scoring and subtypes into main pipeline"
```

---

## Task 10: Final Verification and Push

**Step 1: Run all tests**

Run: `pytest tests/ -v`
Expected: All tests PASS

**Step 2: Check test count increased**

Run: `pytest tests/ --collect-only | grep "test session starts" -A 1`
Expected: Should show more tests than before (was 60, now should be ~70+)

**Step 3: Push changes**

```bash
git push origin feature/knowledge-graph-implementation
```

---

## Verification Checklist

After completing Phase 1:

- [ ] Subtype extraction works for creature, land, artifact types
- [ ] Subtypes added to enrichment pipeline
- [ ] Subtype nodes created in Neo4j
- [ ] HAS_SUBTYPE relationships created
- [ ] Precon downloader downloads and extracts deck files
- [ ] Precon parser counts Commander deck appearances
- [ ] Popularity calculator combines EDHREC + precon scores
- [ ] Main pipeline includes all new features
- [ ] All tests pass
- [ ] Changes committed and pushed
