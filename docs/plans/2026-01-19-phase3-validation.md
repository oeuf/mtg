# Phase 3: Validation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create validation tools to measure recommendation quality against a reference Muldrotha deck using Mean Reciprocal Rank (MRR).

**Architecture:** Load reference deck from Moxfield-format file, get ranked recommendations from the system, calculate MRR and overlap metrics, provide CLI for iteration.

**Tech Stack:** Python, pytest

**Prerequisites:** Phase 1 and Phase 2 complete

---

## Task 1: Create Reference Deck Loader

**Files:**
- Create: `src/validation/reference_deck.py`
- Test: `tests/unit/test_reference_deck.py`

**Step 1: Examine reference deck format**

Read `Muldrotha/DECKLIST.md` to understand format:
```
1	Muldrotha, the Gravetide
1	Sol Ring
1	Eternal Witness
...
```

**Step 2: Write the failing test**

Create `tests/unit/test_reference_deck.py`:

```python
"""Unit tests for reference deck loader."""

import tempfile
import os
from src.validation.reference_deck import load_reference_deck, parse_decklist_line


def test_parse_decklist_line_tab_separated():
    """Test parsing tab-separated format."""
    line = "1\tSol Ring"
    result = parse_decklist_line(line)
    assert result == "Sol Ring"


def test_parse_decklist_line_space_separated():
    """Test parsing space-separated format."""
    line = "1 Eternal Witness"
    result = parse_decklist_line(line)
    assert result == "Eternal Witness"


def test_parse_decklist_line_with_quantity():
    """Test parsing line with quantity > 1."""
    line = "4\tForest"
    result = parse_decklist_line(line)
    assert result == "Forest"


def test_parse_decklist_line_empty():
    """Test parsing empty line."""
    line = ""
    result = parse_decklist_line(line)
    assert result is None


def test_parse_decklist_line_comment():
    """Test parsing comment line."""
    line = "# This is a comment"
    result = parse_decklist_line(line)
    assert result is None


def test_load_reference_deck():
    """Test loading full deck from file."""
    content = """# Muldrotha Deck
1\tMuldrotha, the Gravetide
1\tSol Ring
1\tEternal Witness
4\tForest
"""

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
        f.write(content)
        temp_path = f.name

    try:
        cards = load_reference_deck(temp_path)

        assert "Muldrotha, the Gravetide" in cards
        assert "Sol Ring" in cards
        assert "Eternal Witness" in cards
        assert "Forest" in cards
        assert len(cards) == 4
    finally:
        os.unlink(temp_path)


def test_load_reference_deck_excludes_commander():
    """Test loading deck excluding commander."""
    content = """1\tMuldrotha, the Gravetide
1\tSol Ring
"""

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
        f.write(content)
        temp_path = f.name

    try:
        cards = load_reference_deck(temp_path, exclude_commander=True)

        assert "Muldrotha, the Gravetide" not in cards
        assert "Sol Ring" in cards
    finally:
        os.unlink(temp_path)
```

**Step 3: Run test to verify it fails**

Run: `pytest tests/unit/test_reference_deck.py::test_parse_decklist_line_tab_separated -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 4: Write minimal implementation**

Create `src/validation/__init__.py`:

```python
"""Validation tools for recommendation quality."""
```

Create `src/validation/reference_deck.py`:

```python
"""Load reference decklists for validation."""

import re
from pathlib import Path


def parse_decklist_line(line: str) -> str | None:
    """Parse a single line from a decklist.

    Formats supported:
    - "1\tCard Name" (tab-separated)
    - "1 Card Name" (space-separated)
    - "4\tForest" (multiple copies)

    Returns:
        Card name or None if line should be skipped
    """
    line = line.strip()

    # Skip empty lines
    if not line:
        return None

    # Skip comments and headers
    if line.startswith("#") or line.startswith("*") or line.startswith("-"):
        return None

    # Skip section headers
    if line.startswith("##"):
        return None

    # Match quantity + card name (tab or space separated)
    match = re.match(r'^(\d+)\s+(.+)$', line)
    if match:
        return match.group(2).strip()

    return None


def load_reference_deck(
    filepath: str,
    exclude_commander: bool = False,
    commander_name: str = "Muldrotha, the Gravetide"
) -> set[str]:
    """Load card names from a Moxfield-format decklist.

    Args:
        filepath: Path to decklist file
        exclude_commander: Whether to exclude the commander from results
        commander_name: Commander name to exclude if exclude_commander=True

    Returns:
        Set of card names in the deck
    """
    cards = set()
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"Deck file not found: {filepath}")

    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            card_name = parse_decklist_line(line)
            if card_name:
                if exclude_commander and card_name == commander_name:
                    continue
                cards.add(card_name)

    return cards
```

**Step 5: Run tests to verify they pass**

Run: `pytest tests/unit/test_reference_deck.py -v`
Expected: All PASS

**Step 6: Commit**

```bash
mkdir -p src/validation
git add src/validation/__init__.py src/validation/reference_deck.py tests/unit/test_reference_deck.py
git commit -m "feat: add reference deck loader for validation"
```

---

## Task 2: Create MRR Metrics Calculator

**Files:**
- Create: `src/validation/metrics.py`
- Test: `tests/unit/test_metrics.py`

**Step 1: Write the failing test**

Create `tests/unit/test_metrics.py`:

```python
"""Unit tests for validation metrics."""

from src.validation.metrics import (
    mean_reciprocal_rank,
    overlap_at_k,
    find_missing_cards
)


def test_mrr_perfect_ranking():
    """Test MRR when all reference cards are ranked first."""
    reference = {"A", "B", "C"}
    ranked = ["A", "B", "C", "D", "E"]

    mrr = mean_reciprocal_rank(reference, ranked)

    # Perfect ranking: 1/1 + 1/2 + 1/3 = 1.833, avg = 0.611
    assert abs(mrr - 0.611) < 0.01


def test_mrr_worst_ranking():
    """Test MRR when reference cards are at the end."""
    reference = {"A", "B"}
    ranked = ["X", "Y", "Z", "A", "B"]

    mrr = mean_reciprocal_rank(reference, ranked)

    # A at rank 4, B at rank 5: (1/4 + 1/5) / 2 = 0.225
    assert abs(mrr - 0.225) < 0.01


def test_mrr_missing_cards():
    """Test MRR when some reference cards not in ranking."""
    reference = {"A", "B", "C"}
    ranked = ["A", "X", "Y"]

    mrr = mean_reciprocal_rank(reference, ranked)

    # Only A found at rank 1: 1/3 * (1/1 + 0 + 0) = 0.333
    assert abs(mrr - 0.333) < 0.01


def test_overlap_at_k():
    """Test overlap percentage calculation."""
    reference = {"A", "B", "C", "D", "E"}  # 5 cards
    ranked = ["A", "B", "X", "Y", "Z"]

    # Top 5 contains A, B from reference = 40%
    overlap = overlap_at_k(reference, ranked, k=5)
    assert abs(overlap - 0.40) < 0.01

    # Top 2 contains A, B from reference = 40%
    overlap = overlap_at_k(reference, ranked, k=2)
    assert abs(overlap - 0.40) < 0.01


def test_find_missing_cards():
    """Test finding reference cards not in top K."""
    reference = {"A", "B", "C", "D"}
    ranked = ["A", "X", "B", "Y", "Z"]

    missing = find_missing_cards(reference, ranked, k=5)

    assert "C" in missing
    assert "D" in missing
    assert "A" not in missing
    assert "B" not in missing


def test_find_missing_cards_with_ranks():
    """Test finding missing cards with their actual ranks."""
    reference = {"A", "B", "C"}
    ranked = ["X", "Y", "A", "Z", "B", "W", "C"]

    missing = find_missing_cards(reference, ranked, k=2, include_ranks=True)

    # A is at rank 3, B at 5, C at 7 - all outside top 2
    assert ("A", 3) in missing
    assert ("B", 5) in missing
    assert ("C", 7) in missing
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_metrics.py::test_mrr_perfect_ranking -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

Create `src/validation/metrics.py`:

```python
"""Validation metrics for recommendation quality."""


def mean_reciprocal_rank(reference: set[str], ranked: list[str]) -> float:
    """Calculate Mean Reciprocal Rank (MRR).

    For each reference card, find its rank in the recommendations.
    MRR = average of (1/rank) for all reference cards.

    Args:
        reference: Set of card names that should be recommended
        ranked: Ordered list of recommended card names

    Returns:
        MRR score between 0 and 1 (higher is better)
    """
    if not reference:
        return 0.0

    total_reciprocal = 0.0

    for card in reference:
        if card in ranked:
            rank = ranked.index(card) + 1  # 1-indexed
            total_reciprocal += 1.0 / rank
        # Cards not found contribute 0

    return total_reciprocal / len(reference)


def overlap_at_k(reference: set[str], ranked: list[str], k: int) -> float:
    """Calculate what percentage of reference cards appear in top K.

    Args:
        reference: Set of card names that should be recommended
        ranked: Ordered list of recommended card names
        k: Number of top recommendations to consider

    Returns:
        Overlap percentage between 0 and 1
    """
    if not reference:
        return 0.0

    top_k = set(ranked[:k])
    overlap = reference & top_k

    return len(overlap) / len(reference)


def find_missing_cards(
    reference: set[str],
    ranked: list[str],
    k: int,
    include_ranks: bool = False
) -> list:
    """Find reference cards not in top K recommendations.

    Args:
        reference: Set of card names that should be recommended
        ranked: Ordered list of recommended card names
        k: Number of top recommendations to consider
        include_ranks: If True, return (card, rank) tuples for found cards

    Returns:
        List of missing card names, or (name, rank) tuples if include_ranks
    """
    top_k = set(ranked[:k])
    missing_from_top_k = reference - top_k

    if not include_ranks:
        return list(missing_from_top_k)

    # Find actual ranks for missing cards
    result = []
    for card in missing_from_top_k:
        if card in ranked:
            rank = ranked.index(card) + 1
            result.append((card, rank))
        else:
            result.append((card, None))  # Not in list at all

    return sorted(result, key=lambda x: x[1] if x[1] else float('inf'))
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/unit/test_metrics.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add src/validation/metrics.py tests/unit/test_metrics.py
git commit -m "feat: add MRR and overlap metrics for validation"
```

---

## Task 3: Create Validation Runner

**Files:**
- Create: `src/validation/validator.py`
- Test: `tests/integration/test_validator.py`

**Step 1: Write the failing test**

Create `tests/integration/test_validator.py`:

```python
"""Integration tests for validation runner."""

from unittest.mock import Mock, patch
from src.validation.validator import DeckValidator
from src.graph.connection import Neo4jConnection


def test_validator_initialization():
    """Test validator initializes with connection."""
    mock_conn = Mock(spec=Neo4jConnection)

    validator = DeckValidator(mock_conn)

    assert validator.conn == mock_conn


def test_validator_get_recommendations():
    """Test getting ranked recommendations."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = [
        {"name": "Eternal Witness"},
        {"name": "Spore Frog"},
        {"name": "Sol Ring"},
    ]

    validator = DeckValidator(mock_conn)
    recommendations = validator.get_recommendations(
        commander_name="Muldrotha, the Gravetide",
        limit=100
    )

    assert recommendations == ["Eternal Witness", "Spore Frog", "Sol Ring"]


def test_validator_validate():
    """Test full validation run."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = [
        {"name": "Eternal Witness"},
        {"name": "Sol Ring"},
        {"name": "Other Card"},
    ]

    validator = DeckValidator(mock_conn)

    # Mock reference deck
    reference = {"Eternal Witness", "Sol Ring", "Missing Card"}

    result = validator.validate(
        reference_cards=reference,
        commander_name="Muldrotha, the Gravetide",
        top_k=100
    )

    assert "mrr" in result
    assert "overlap_100" in result
    assert "missing_cards" in result
    assert result["reference_count"] == 3
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_validator.py::test_validator_initialization -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

Create `src/validation/validator.py`:

```python
"""Validation runner for deck recommendations."""

from src.graph.connection import Neo4jConnection
from src.synergy.queries import DeckbuildingQueries
from src.validation.metrics import mean_reciprocal_rank, overlap_at_k, find_missing_cards


class DeckValidator:
    """Validate recommendation quality against reference decks."""

    def __init__(self, conn: Neo4jConnection):
        """Initialize with Neo4j connection."""
        self.conn = conn

    def get_recommendations(
        self,
        commander_name: str,
        limit: int = 500
    ) -> list[str]:
        """Get ranked card recommendations for a commander.

        Returns:
            Ordered list of card names
        """
        # Try v2 query first (GDS-enhanced), fall back to v1
        try:
            results = DeckbuildingQueries.find_synergistic_cards_v2(
                self.conn,
                commander_name=commander_name,
                max_cmc=10,  # No CMC filter for validation
                limit=limit
            )
        except Exception:
            results = DeckbuildingQueries.find_synergistic_cards(
                self.conn,
                commander_name=commander_name,
                max_cmc=10,
                min_strength=0.0,
                limit=limit
            )

        return [r["name"] for r in results]

    def validate(
        self,
        reference_cards: set[str],
        commander_name: str,
        top_k: int = 100
    ) -> dict:
        """Run validation against reference deck.

        Args:
            reference_cards: Set of cards that should be recommended
            commander_name: Commander to get recommendations for
            top_k: Number of recommendations to consider

        Returns:
            Dictionary with validation metrics
        """
        # Get recommendations
        recommendations = self.get_recommendations(commander_name, limit=500)

        # Calculate metrics
        mrr = mean_reciprocal_rank(reference_cards, recommendations)

        overlaps = {}
        for k in [50, 100, 200, 300]:
            overlaps[f"overlap_{k}"] = overlap_at_k(reference_cards, recommendations, k)

        missing = find_missing_cards(
            reference_cards,
            recommendations,
            k=top_k,
            include_ranks=True
        )

        return {
            "commander": commander_name,
            "reference_count": len(reference_cards),
            "recommendations_count": len(recommendations),
            "mrr": mrr,
            **overlaps,
            "missing_cards": missing[:20],  # Top 20 missing
            "found_in_top_100": int(overlaps["overlap_100"] * len(reference_cards))
        }

    def print_report(self, result: dict):
        """Print formatted validation report."""
        print("\n" + "=" * 60)
        print("VALIDATION REPORT")
        print("=" * 60)
        print(f"\nCommander: {result['commander']}")
        print(f"Reference deck: {result['reference_count']} cards")
        print(f"Recommendations: {result['recommendations_count']} cards")

        print(f"\n--- Metrics ---")
        print(f"Mean Reciprocal Rank: {result['mrr']:.3f}")
        print(f"Found in top 50:  {result['overlap_50'] * 100:.1f}%")
        print(f"Found in top 100: {result['overlap_100'] * 100:.1f}%")
        print(f"Found in top 200: {result['overlap_200'] * 100:.1f}%")
        print(f"Found in top 300: {result['overlap_300'] * 100:.1f}%")

        if result['missing_cards']:
            print(f"\n--- Missing from Top 100 (showing first 10) ---")
            for card, rank in result['missing_cards'][:10]:
                if rank:
                    print(f"  {card} (actual rank: {rank})")
                else:
                    print(f"  {card} (not in recommendations)")

        print("\n" + "=" * 60)
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/integration/test_validator.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add src/validation/validator.py tests/integration/test_validator.py
git commit -m "feat: add validation runner with MRR reporting"
```

---

## Task 4: Create Validation CLI

**Files:**
- Create: `src/validation/validate_deck.py`

**Step 1: Create CLI entry point**

Create `src/validation/validate_deck.py`:

```python
#!/usr/bin/env python3
"""CLI for validating deck recommendations against reference."""

import argparse
import os
import sys

from src.graph.connection import Neo4jConnection
from src.validation.reference_deck import load_reference_deck
from src.validation.validator import DeckValidator


def main():
    parser = argparse.ArgumentParser(
        description="Validate recommendations against a reference deck"
    )
    parser.add_argument(
        "--commander",
        type=str,
        default="Muldrotha, the Gravetide",
        help="Commander name"
    )
    parser.add_argument(
        "--reference",
        type=str,
        default="Muldrotha/DECKLIST.md",
        help="Path to reference decklist"
    )
    parser.add_argument(
        "--neo4j-uri",
        type=str,
        default="bolt://localhost:7687",
        help="Neo4j connection URI"
    )
    parser.add_argument(
        "--neo4j-user",
        type=str,
        default="neo4j",
        help="Neo4j username"
    )

    args = parser.parse_args()

    # Get password from environment
    password = os.environ.get("NEO4J_PASSWORD")
    if not password:
        print("Error: NEO4J_PASSWORD environment variable not set")
        sys.exit(1)

    # Load reference deck
    print(f"Loading reference deck: {args.reference}")
    try:
        reference_cards = load_reference_deck(
            args.reference,
            exclude_commander=True,
            commander_name=args.commander
        )
        print(f"Loaded {len(reference_cards)} cards (excluding commander)")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Connect to Neo4j
    print(f"\nConnecting to Neo4j: {args.neo4j_uri}")
    conn = Neo4jConnection(args.neo4j_uri, args.neo4j_user, password)

    try:
        # Run validation
        validator = DeckValidator(conn)
        result = validator.validate(
            reference_cards=reference_cards,
            commander_name=args.commander
        )

        # Print report
        validator.print_report(result)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
```

**Step 2: Test CLI runs**

Run: `python -m src.validation.validate_deck --help`
Expected: Help message displayed

**Step 3: Commit**

```bash
git add src/validation/validate_deck.py
git commit -m "feat: add validation CLI"
```

---

## Task 5: Test with Real Reference Deck

**Files:**
- Test: `tests/integration/test_muldrotha_validation.py` (already exists, update)

**Step 1: Verify reference deck exists and is parseable**

Run: `python -c "from src.validation.reference_deck import load_reference_deck; cards = load_reference_deck('Muldrotha/DECKLIST.md'); print(f'Loaded {len(cards)} cards')"`

Expected: "Loaded ~99 cards"

**Step 2: Run validation (requires Neo4j with data)**

Run:
```bash
export NEO4J_PASSWORD=your_password
python -m src.validation.validate_deck \
  --commander "Muldrotha, the Gravetide" \
  --reference Muldrotha/DECKLIST.md
```

Expected: Validation report with MRR score

**Step 3: Commit any fixes**

```bash
git add -A
git commit -m "fix: validation adjustments from real testing"
```

---

## Task 6: Final Verification and Push

**Step 1: Run all tests**

Run: `pytest tests/ -v`
Expected: All tests PASS

**Step 2: Push changes**

```bash
git push origin feature/knowledge-graph-implementation
```

---

## Verification Checklist

After completing Phase 3:

- [ ] Reference deck loader parses Moxfield format
- [ ] MRR calculation is correct
- [ ] Overlap-at-K calculation is correct
- [ ] Missing cards finder works with ranks
- [ ] Validator runs full validation pipeline
- [ ] CLI works with command-line arguments
- [ ] Real validation produces reasonable MRR (target > 0.3)
- [ ] All tests pass
- [ ] Changes committed and pushed
