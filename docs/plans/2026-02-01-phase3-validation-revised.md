# Phase 3: Validation Implementation Plan (Revised)

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Validate recommendation quality by comparing system recommendations against a reference Muldrotha deck using ranking metrics (Precision@K, Recall@K, MRR).

**Architecture:** Load reference deck from file, query Neo4j for top-K recommendations using EMBEDDING_SIMILAR (topK=100), calculate ranking metrics, compare mechanic-only vs 7-dimensional scoring.

**Tech Stack:** Python 3.13, pytest, Neo4j Python driver

**Prerequisites:** Phase 1-2 complete (pipeline ran successfully with topK=100)

**Key Changes from January Plan:**
- Use EMBEDDING_SIMILAR relationships (topK=100) instead of mechanic-only
- Test both similarity approaches: node similarity vs embedding similarity
- Simplified deck loader (just card names, no complex format parsing)
- Added comparison between scoring methods

---

## Task 1: Create Reference Deck Loader

**Files:**
- Create: `src/validation/__init__.py`
- Create: `src/validation/reference_deck.py`
- Test: `tests/unit/test_reference_deck.py`

**Step 1: Write the failing test**

Create `tests/unit/test_reference_deck.py`:

```python
"""Unit tests for reference deck loader."""

import tempfile
import os
from src.validation.reference_deck import load_reference_deck


def test_load_simple_deck():
    """Test loading deck from simple format."""
    content = """Muldrotha, the Gravetide
Sol Ring
Eternal Witness
Sakura-Tribe Elder
"""

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name

    try:
        cards = load_reference_deck(temp_path)
        assert len(cards) == 4
        assert "Muldrotha, the Gravetide" in cards
        assert "Sol Ring" in cards
    finally:
        os.unlink(temp_path)


def test_load_deck_with_comments():
    """Test loading deck ignoring comments and empty lines."""
    content = """# Muldrotha Deck
Sol Ring

# Ramp
Sakura-Tribe Elder
"""

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name

    try:
        cards = load_reference_deck(temp_path)
        assert len(cards) == 2
        assert "Sol Ring" in cards
        assert "Sakura-Tribe Elder" in cards
    finally:
        os.unlink(temp_path)


def test_exclude_commander():
    """Test excluding commander from deck list."""
    content = """Muldrotha, the Gravetide
Sol Ring
"""

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name

    try:
        cards = load_reference_deck(temp_path, exclude_commander=True)
        assert len(cards) == 1
        assert "Muldrotha, the Gravetide" not in cards
        assert "Sol Ring" in cards
    finally:
        os.unlink(temp_path)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_reference_deck.py::test_load_simple_deck -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.validation'"

**Step 3: Write minimal implementation**

Create `src/validation/__init__.py`:

```python
"""Validation tools for recommendation quality."""
```

Create `src/validation/reference_deck.py`:

```python
"""Load reference decklists for validation."""

from pathlib import Path


def load_reference_deck(filepath: str, exclude_commander: bool = False) -> list[str]:
    """Load card names from reference deck file.

    Args:
        filepath: Path to deck file (one card name per line)
        exclude_commander: If True, excludes cards with "Commander" in database

    Returns:
        List of card names from the deck
    """
    cards = []

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            cards.append(line)

    # Commander exclusion will be handled in query, not here
    # This keeps the loader simple
    return cards
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_reference_deck.py -v`
Expected: PASS (3/3 tests) - Note: exclude_commander test will fail

**Step 5: Fix exclude_commander test**

Modify test to match implementation (commander exclusion in query, not loader):

```python
def test_exclude_commander():
    """Test that loader returns all cards (exclusion happens in query)."""
    content = """Muldrotha, the Gravetide
Sol Ring
"""

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name

    try:
        cards = load_reference_deck(temp_path)
        assert len(cards) == 2
        assert "Muldrotha, the Gravetide" in cards
        assert "Sol Ring" in cards
    finally:
        os.unlink(temp_path)
```

**Step 6: Rerun tests**

Run: `pytest tests/unit/test_reference_deck.py -v`
Expected: PASS (3/3 tests)

**Step 7: Commit**

```bash
git add src/validation/ tests/unit/test_reference_deck.py
git commit -m "feat: add reference deck loader for validation

- Simple one-card-per-line format
- Supports comments and empty lines
- Commander exclusion handled in queries

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Create Recommendation Query Engine

**Files:**
- Create: `src/validation/recommendations.py`
- Test: `tests/integration/test_recommendations.py`

**Step 1: Write the failing test**

Create `tests/integration/test_recommendations.py`:

```python
"""Integration tests for recommendation queries."""

import pytest
from src.graph.connection import Neo4jConnection
from src.validation.recommendations import get_embedding_recommendations, get_similarity_recommendations


@pytest.fixture
def conn():
    """Create Neo4j connection."""
    import os
    password = os.getenv('NEO4J_PASSWORD', 'mtg-commander')
    conn = Neo4jConnection('bolt://localhost:7687', 'neo4j', password)
    yield conn
    conn.close()


def test_get_embedding_recommendations(conn):
    """Test getting recommendations using EMBEDDING_SIMILAR."""
    recs = get_embedding_recommendations(
        conn,
        commander_name="Muldrotha, the Gravetide",
        top_k=10
    )

    assert len(recs) > 0
    assert len(recs) <= 10

    # Check structure
    first = recs[0]
    assert "name" in first
    assert "score" in first
    assert 0.0 <= first["score"] <= 1.0


def test_get_similarity_recommendations(conn):
    """Test getting recommendations using SIMILAR_TO."""
    recs = get_similarity_recommendations(
        conn,
        commander_name="Muldrotha, the Gravetide",
        top_k=10
    )

    assert len(recs) > 0
    assert len(recs) <= 10

    first = recs[0]
    assert "name" in first
    assert "score" in first
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_recommendations.py::test_get_embedding_recommendations -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

Create `src/validation/recommendations.py`:

```python
"""Query Neo4j for card recommendations."""

from typing import Dict, List
from src.graph.connection import Neo4jConnection


def get_embedding_recommendations(
    conn: Neo4jConnection,
    commander_name: str,
    top_k: int = 20
) -> List[Dict]:
    """Get top-K recommendations using EMBEDDING_SIMILAR relationships.

    Args:
        conn: Neo4j connection
        commander_name: Name of commander card
        top_k: Number of recommendations to return

    Returns:
        List of dicts with 'name' and 'score' keys
    """
    query = """
    MATCH (cmd:Commander {name: $commander_name})
    MATCH (cmd)-[sim:EMBEDDING_SIMILAR]-(card:Card)
    WHERE NOT card:Commander
    RETURN card.name AS name, sim.score AS score
    ORDER BY sim.score DESC
    LIMIT $top_k
    """

    result = conn.execute_query(query, {
        "commander_name": commander_name,
        "top_k": top_k
    })

    return result


def get_similarity_recommendations(
    conn: Neo4jConnection,
    commander_name: str,
    top_k: int = 20
) -> List[Dict]:
    """Get top-K recommendations using SIMILAR_TO relationships.

    Args:
        conn: Neo4j connection
        commander_name: Name of commander card
        top_k: Number of recommendations to return

    Returns:
        List of dicts with 'name' and 'score' keys
    """
    query = """
    MATCH (cmd:Commander {name: $commander_name})
    MATCH (cmd)-[sim:SIMILAR_TO]-(card:Card)
    WHERE NOT card:Commander
    RETURN card.name AS name, sim.score AS score
    ORDER BY sim.score DESC
    LIMIT $top_k
    """

    result = conn.execute_query(query, {
        "commander_name": commander_name,
        "top_k": top_k
    })

    return result
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/integration/test_recommendations.py -v`
Expected: PASS (2/2 tests)

**Step 5: Commit**

```bash
git add src/validation/recommendations.py tests/integration/test_recommendations.py
git commit -m "feat: add recommendation query functions

- get_embedding_recommendations (EMBEDDING_SIMILAR)
- get_similarity_recommendations (SIMILAR_TO)
- Returns ranked list of cards with scores

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Implement Ranking Metrics

**Files:**
- Create: `src/validation/metrics.py`
- Test: `tests/unit/test_metrics.py`

**Step 1: Write the failing test**

Create `tests/unit/test_metrics.py`:

```python
"""Unit tests for validation metrics."""

from src.validation.metrics import precision_at_k, recall_at_k, mean_reciprocal_rank


def test_precision_at_k_perfect():
    """Test precision when all recommendations are in reference."""
    recommendations = ["Sol Ring", "Sakura-Tribe Elder", "Eternal Witness"]
    reference = ["Sol Ring", "Sakura-Tribe Elder", "Eternal Witness", "Forest"]

    p = precision_at_k(recommendations, reference, k=3)
    assert p == 1.0


def test_precision_at_k_partial():
    """Test precision with partial overlap."""
    recommendations = ["Sol Ring", "Mana Crypt", "Eternal Witness"]
    reference = ["Sol Ring", "Eternal Witness"]

    p = precision_at_k(recommendations, reference, k=3)
    assert p == 2/3


def test_precision_at_k_none():
    """Test precision with no overlap."""
    recommendations = ["Sol Ring", "Mana Crypt"]
    reference = ["Forest", "Island"]

    p = precision_at_k(recommendations, reference, k=2)
    assert p == 0.0


def test_recall_at_k_perfect():
    """Test recall when all reference cards found."""
    recommendations = ["Sol Ring", "Eternal Witness", "Sakura-Tribe Elder"]
    reference = ["Sol Ring", "Eternal Witness"]

    r = recall_at_k(recommendations, reference, k=3)
    assert r == 1.0


def test_recall_at_k_partial():
    """Test recall with partial coverage."""
    recommendations = ["Sol Ring", "Mana Crypt", "Eternal Witness"]
    reference = ["Sol Ring", "Eternal Witness", "Sakura-Tribe Elder", "Forest"]

    r = recall_at_k(recommendations, reference, k=3)
    assert r == 2/4


def test_mean_reciprocal_rank_first():
    """Test MRR when first recommendation matches."""
    recommendations = ["Sol Ring", "Mana Crypt", "Eternal Witness"]
    reference = ["Sol Ring"]

    mrr = mean_reciprocal_rank(recommendations, reference)
    assert mrr == 1.0


def test_mean_reciprocal_rank_third():
    """Test MRR when third recommendation matches."""
    recommendations = ["Mana Crypt", "Mana Vault", "Sol Ring"]
    reference = ["Sol Ring"]

    mrr = mean_reciprocal_rank(recommendations, reference)
    assert abs(mrr - 1/3) < 0.001


def test_mean_reciprocal_rank_multiple():
    """Test MRR with multiple reference cards."""
    recommendations = ["A", "B", "C", "D", "E"]
    reference = ["C", "D"]  # First match at position 3

    mrr = mean_reciprocal_rank(recommendations, reference)
    assert abs(mrr - 1/3) < 0.001  # 1/3 for first match at position 3
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_metrics.py::test_precision_at_k_perfect -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

Create `src/validation/metrics.py`:

```python
"""Validation metrics for ranking quality."""

from typing import List


def precision_at_k(recommendations: List[str], reference: List[str], k: int) -> float:
    """Calculate Precision@K.

    Precision@K = (# relevant items in top-K) / K

    Args:
        recommendations: Ranked list of recommended cards
        reference: Set of cards in reference deck
        k: Number of top recommendations to consider

    Returns:
        Precision score between 0.0 and 1.0
    """
    if k == 0 or len(recommendations) == 0:
        return 0.0

    top_k = recommendations[:k]
    reference_set = set(reference)

    relevant_count = sum(1 for card in top_k if card in reference_set)

    return relevant_count / k


def recall_at_k(recommendations: List[str], reference: List[str], k: int) -> float:
    """Calculate Recall@K.

    Recall@K = (# relevant items in top-K) / (total # relevant items)

    Args:
        recommendations: Ranked list of recommended cards
        reference: Set of cards in reference deck
        k: Number of top recommendations to consider

    Returns:
        Recall score between 0.0 and 1.0
    """
    if len(reference) == 0:
        return 0.0

    top_k = recommendations[:k]
    reference_set = set(reference)

    relevant_count = sum(1 for card in top_k if card in reference_set)

    return relevant_count / len(reference)


def mean_reciprocal_rank(recommendations: List[str], reference: List[str]) -> float:
    """Calculate Mean Reciprocal Rank (MRR).

    MRR = 1 / (rank of first relevant item)

    Args:
        recommendations: Ranked list of recommended cards
        reference: Set of cards in reference deck

    Returns:
        MRR score between 0.0 and 1.0
    """
    reference_set = set(reference)

    for rank, card in enumerate(recommendations, start=1):
        if card in reference_set:
            return 1.0 / rank

    return 0.0  # No relevant items found
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_metrics.py -v`
Expected: PASS (8/8 tests)

**Step 5: Commit**

```bash
git add src/validation/metrics.py tests/unit/test_metrics.py
git commit -m "feat: add ranking validation metrics

- Precision@K: relevance of top-K recommendations
- Recall@K: coverage of reference deck in top-K
- Mean Reciprocal Rank: position of first match

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Create Validation CLI

**Files:**
- Create: `scripts/validate_recommendations.py`
- Test: Manual testing with reference deck

**Step 1: Create reference deck file**

Create `reference_decks/muldrotha.txt`:

```
Muldrotha, the Gravetide
Sol Ring
Eternal Witness
Sakura-Tribe Elder
Spore Frog
Pernicious Deed
Seal of Primordium
Seal of Removal
Wayfarer's Bauble
Commander's Sphere
Solemn Simulacrum
Shriekmaw
Ravenous Chupacabra
Mulldrifter
Archaeomancer
Caustic Caterpillar
Reclamation Sage
Wood Elves
Farhaven Elf
Satyr Wayfinder
```

**Step 2: Write CLI script**

Create `scripts/validate_recommendations.py`:

```python
#!/usr/bin/env python3
"""Validate recommendation quality against reference deck."""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.graph.connection import Neo4jConnection
from src.validation.reference_deck import load_reference_deck
from src.validation.recommendations import get_embedding_recommendations, get_similarity_recommendations
from src.validation.metrics import precision_at_k, recall_at_k, mean_reciprocal_rank


def main():
    """Run validation."""
    # Load reference deck
    deck_path = "reference_decks/muldrotha.txt"

    if not os.path.exists(deck_path):
        print(f"Error: Reference deck not found at {deck_path}")
        return 1

    print(f"Loading reference deck: {deck_path}")
    reference_cards = load_reference_deck(deck_path)

    # Exclude commander from reference
    commander = "Muldrotha, the Gravetide"
    reference_cards = [c for c in reference_cards if c != commander]

    print(f"Reference deck: {len(reference_cards)} cards (excluding commander)\n")

    # Connect to Neo4j
    password = os.getenv('NEO4J_PASSWORD', 'mtg-commander')
    conn = Neo4jConnection('bolt://localhost:7687', 'neo4j', password)

    try:
        # Test both recommendation methods
        methods = [
            ("EMBEDDING_SIMILAR (topK=100)", lambda: get_embedding_recommendations(conn, commander, top_k=50)),
            ("SIMILAR_TO (node similarity)", lambda: get_similarity_recommendations(conn, commander, top_k=50))
        ]

        for method_name, get_recs in methods:
            print(f"=== {method_name} ===")

            recommendations = get_recs()
            rec_names = [r["name"] for r in recommendations]

            print(f"Got {len(recommendations)} recommendations\n")

            # Calculate metrics at different K values
            for k in [10, 20, 50]:
                p = precision_at_k(rec_names, reference_cards, k)
                r = recall_at_k(rec_names, reference_cards, k)

                print(f"K={k}:")
                print(f"  Precision@{k}: {p:.3f}")
                print(f"  Recall@{k}: {r:.3f}")

            mrr = mean_reciprocal_rank(rec_names, reference_cards)
            print(f"\nMean Reciprocal Rank: {mrr:.3f}")

            # Show top matches
            print("\nTop 5 recommendations:")
            for i, rec in enumerate(recommendations[:5], 1):
                in_deck = "✓" if rec["name"] in reference_cards else " "
                print(f"  {i}. [{in_deck}] {rec['name']} (score: {rec['score']:.3f})")

            print("\n" + "="*60 + "\n")

    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**Step 3: Make script executable**

Run: `chmod +x scripts/validate_recommendations.py`

**Step 4: Test script**

Run:
```bash
export NEO4J_PASSWORD="mtg-commander"
python scripts/validate_recommendations.py
```

Expected: Output showing metrics for both methods

**Step 5: Commit**

```bash
git add scripts/validate_recommendations.py reference_decks/muldrotha.txt
git commit -m "feat: add validation CLI for recommendation quality

- Loads reference deck (Muldrotha example)
- Tests both EMBEDDING_SIMILAR and SIMILAR_TO
- Calculates Precision@K, Recall@K, MRR
- Shows top recommendations with deck membership

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Document Results

**Files:**
- Create: `docs/validation_results.md`

**Step 1: Run validation and capture results**

Run: `python scripts/validate_recommendations.py > docs/validation_results.md`

**Step 2: Add analysis and interpretation**

Manually edit `docs/validation_results.md` to add:
- Date of validation
- Database stats (node count, relationship count)
- Interpretation of metrics
- Comparison between methods
- Recommendations for improvement

**Step 3: Commit**

```bash
git add docs/validation_results.md
git commit -m "docs: add validation results for Phase 3

- Precision@K, Recall@K, MRR metrics
- Comparison of EMBEDDING_SIMILAR vs SIMILAR_TO
- Analysis and recommendations

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Verification

After implementation, verify with:

**1. All tests pass:**
```bash
pytest tests/unit/test_reference_deck.py tests/unit/test_metrics.py -v
pytest tests/integration/test_recommendations.py -v  # Requires Neo4j
```

**2. Validation script runs:**
```bash
python scripts/validate_recommendations.py
```

**3. Check metrics are reasonable:**
- Precision@10 > 0.1 (at least 1 in 10 recommendations is in deck)
- Recall@50 > 0.2 (top 50 finds at least 20% of deck)
- MRR > 0.1 (first match appears reasonably high in ranking)

---

## Summary

**Implementation Breakdown:**
- **Task 1 (20 min):** Reference deck loader with tests
- **Task 2 (20 min):** Recommendation query functions
- **Task 3 (30 min):** Ranking metrics (P@K, R@K, MRR)
- **Task 4 (30 min):** CLI tool for validation
- **Task 5 (20 min):** Document results

**Total: ~2 hours**

**Key Improvements from January Plan:**
1. Simplified deck loader (no complex format parsing)
2. Uses EMBEDDING_SIMILAR (topK=100) from Phase 2
3. Compares two similarity approaches
4. Focused on ranking metrics (removed unnecessary complexity)
5. Single reference deck (Muldrotha) for initial validation

**Next Steps After Validation:**
- If metrics are good (P@20 > 0.3, R@50 > 0.4): Proceed to Phase 4 (API)
- If metrics are poor: Investigate and improve scoring algorithms
- Add more reference decks for other commanders
