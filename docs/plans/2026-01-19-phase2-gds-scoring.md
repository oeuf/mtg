# Phase 2: GDS Scoring Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Use Neo4j Graph Data Science (GDS) to compute PageRank, community detection, and node similarity for enhanced synergy scoring.

**Architecture:** Create in-memory graph projection, run GDS algorithms, write computed scores back to card nodes, create SIMILAR_TO relationships, and update recommendation queries to use new scores.

**Tech Stack:** Python, Neo4j, Neo4j GDS plugin

**Prerequisites:** Phase 1 complete, Neo4j running with GDS plugin installed

---

## Task 1: Create GDS Scoring Module

**Files:**
- Create: `src/graph/gds_scoring.py`
- Test: `tests/integration/test_gds_scoring.py`

**Step 1: Write the failing test for graph projection**

Create `tests/integration/test_gds_scoring.py`:

```python
"""Integration tests for GDS scoring module."""

import pytest
from unittest.mock import Mock, MagicMock
from src.graph.gds_scoring import GDSScoring
from src.graph.connection import Neo4jConnection


def test_create_graph_projection():
    """Test that graph projection is created with correct parameters."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = [{"graphName": "synergy-graph"}]

    gds = GDSScoring(mock_conn)
    result = gds.create_projection()

    # Verify projection query was called
    assert mock_conn.execute_query.called
    call_args = mock_conn.execute_query.call_args[0][0]

    assert "gds.graph.project" in call_args
    assert "synergy-graph" in call_args
    assert "Card" in call_args
    assert "HAS_MECHANIC" in call_args


def test_drop_projection():
    """Test dropping existing projection."""
    mock_conn = Mock(spec=Neo4jConnection)

    gds = GDSScoring(mock_conn)
    gds.drop_projection()

    assert mock_conn.execute_query.called
    call_args = mock_conn.execute_query.call_args[0][0]
    assert "gds.graph.drop" in call_args
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_gds_scoring.py::test_create_graph_projection -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

Create `src/graph/gds_scoring.py`:

```python
"""Neo4j Graph Data Science scoring operations."""

from src.graph.connection import Neo4jConnection


class GDSScoring:
    """Compute graph-based scores using Neo4j GDS."""

    GRAPH_NAME = "synergy-graph"

    def __init__(self, conn: Neo4jConnection):
        """Initialize with Neo4j connection."""
        self.conn = conn

    def drop_projection(self):
        """Drop existing graph projection if it exists."""
        query = f"""
        CALL gds.graph.drop('{self.GRAPH_NAME}', false)
        YIELD graphName
        RETURN graphName
        """
        try:
            self.conn.execute_query(query)
            print(f"✓ Dropped existing projection '{self.GRAPH_NAME}'")
        except Exception:
            # Graph doesn't exist, that's fine
            pass

    def create_projection(self) -> dict:
        """Create in-memory graph projection for GDS algorithms.

        Returns:
            Projection metadata
        """
        # Drop existing projection first
        self.drop_projection()

        query = """
        CALL gds.graph.project(
            'synergy-graph',
            ['Card', 'Commander', 'Mechanic', 'Functional_Role'],
            {
                HAS_MECHANIC: {orientation: 'UNDIRECTED'},
                FILLS_ROLE: {orientation: 'UNDIRECTED'},
                COMBOS_WITH: {orientation: 'UNDIRECTED'},
                SYNERGIZES_WITH_MECHANIC: {orientation: 'UNDIRECTED'}
            }
        )
        YIELD graphName, nodeCount, relationshipCount
        RETURN graphName, nodeCount, relationshipCount
        """

        result = self.conn.execute_query(query)
        if result:
            print(f"✓ Created projection '{self.GRAPH_NAME}'")
            print(f"  Nodes: {result[0]['nodeCount']}")
            print(f"  Relationships: {result[0]['relationshipCount']}")
        return result[0] if result else {}

    def projection_exists(self) -> bool:
        """Check if projection exists."""
        query = """
        CALL gds.graph.exists($name) YIELD exists
        RETURN exists
        """
        result = self.conn.execute_query(query, {"name": self.GRAPH_NAME})
        return result[0]["exists"] if result else False
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/integration/test_gds_scoring.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/graph/gds_scoring.py tests/integration/test_gds_scoring.py
git commit -m "feat: add GDS scoring module with graph projection"
```

---

## Task 2: Add PageRank Computation

**Files:**
- Modify: `src/graph/gds_scoring.py`
- Test: `tests/integration/test_gds_scoring.py`

**Step 1: Write the failing test**

Add to `tests/integration/test_gds_scoring.py`:

```python
def test_compute_pagerank():
    """Test PageRank computation."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = [{"nodePropertiesWritten": 100}]

    gds = GDSScoring(mock_conn)
    result = gds.compute_pagerank()

    assert mock_conn.execute_query.called
    call_args = mock_conn.execute_query.call_args[0][0]

    assert "gds.pageRank" in call_args
    assert "pagerank_score" in call_args
    assert result["nodePropertiesWritten"] == 100
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_gds_scoring.py::test_compute_pagerank -v`
Expected: FAIL with "AttributeError: 'GDSScoring' object has no attribute 'compute_pagerank'"

**Step 3: Add PageRank method**

Add to `src/graph/gds_scoring.py` in the `GDSScoring` class:

```python
    def compute_pagerank(self, max_iterations: int = 20, damping_factor: float = 0.85) -> dict:
        """Compute PageRank and write to node properties.

        Args:
            max_iterations: Maximum iterations for PageRank
            damping_factor: Damping factor (default 0.85)

        Returns:
            Computation statistics
        """
        query = f"""
        CALL gds.pageRank.write('{self.GRAPH_NAME}', {{
            writeProperty: 'pagerank_score',
            maxIterations: $max_iterations,
            dampingFactor: $damping_factor
        }})
        YIELD nodePropertiesWritten, ranIterations, didConverge
        RETURN nodePropertiesWritten, ranIterations, didConverge
        """

        result = self.conn.execute_query(query, {
            "max_iterations": max_iterations,
            "damping_factor": damping_factor
        })

        if result:
            print(f"✓ Computed PageRank")
            print(f"  Nodes updated: {result[0]['nodePropertiesWritten']}")
            print(f"  Iterations: {result[0]['ranIterations']}")
            print(f"  Converged: {result[0]['didConverge']}")

        return result[0] if result else {}
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/integration/test_gds_scoring.py::test_compute_pagerank -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/graph/gds_scoring.py tests/integration/test_gds_scoring.py
git commit -m "feat: add PageRank computation to GDS scoring"
```

---

## Task 3: Add Community Detection (Louvain)

**Files:**
- Modify: `src/graph/gds_scoring.py`
- Test: `tests/integration/test_gds_scoring.py`

**Step 1: Write the failing test**

Add to `tests/integration/test_gds_scoring.py`:

```python
def test_detect_communities():
    """Test Louvain community detection."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = [{
        "communityCount": 15,
        "modularity": 0.65,
        "nodePropertiesWritten": 100
    }]

    gds = GDSScoring(mock_conn)
    result = gds.detect_communities()

    assert mock_conn.execute_query.called
    call_args = mock_conn.execute_query.call_args[0][0]

    assert "gds.louvain" in call_args
    assert "community_id" in call_args
    assert result["communityCount"] == 15
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_gds_scoring.py::test_detect_communities -v`
Expected: FAIL with "AttributeError"

**Step 3: Add Louvain method**

Add to `src/graph/gds_scoring.py`:

```python
    def detect_communities(self) -> dict:
        """Detect communities using Louvain algorithm.

        Returns:
            Computation statistics including community count
        """
        query = f"""
        CALL gds.louvain.write('{self.GRAPH_NAME}', {{
            writeProperty: 'community_id'
        }})
        YIELD communityCount, modularity, nodePropertiesWritten
        RETURN communityCount, modularity, nodePropertiesWritten
        """

        result = self.conn.execute_query(query)

        if result:
            print(f"✓ Detected communities (Louvain)")
            print(f"  Communities found: {result[0]['communityCount']}")
            print(f"  Modularity: {result[0]['modularity']:.3f}")
            print(f"  Nodes updated: {result[0]['nodePropertiesWritten']}")

        return result[0] if result else {}
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/integration/test_gds_scoring.py::test_detect_communities -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/graph/gds_scoring.py tests/integration/test_gds_scoring.py
git commit -m "feat: add Louvain community detection to GDS scoring"
```

---

## Task 4: Add Node Similarity

**Files:**
- Modify: `src/graph/gds_scoring.py`
- Test: `tests/integration/test_gds_scoring.py`

**Step 1: Write the failing test**

Add to `tests/integration/test_gds_scoring.py`:

```python
def test_compute_similarity():
    """Test node similarity computation."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = [{
        "relationshipsWritten": 500,
        "nodesCompared": 100
    }]

    gds = GDSScoring(mock_conn)
    result = gds.compute_similarity(min_similarity=0.5, top_k=10)

    assert mock_conn.execute_query.called
    call_args = mock_conn.execute_query.call_args[0][0]

    assert "gds.nodeSimilarity" in call_args
    assert "SIMILAR_TO" in call_args
    assert result["relationshipsWritten"] == 500
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_gds_scoring.py::test_compute_similarity -v`
Expected: FAIL

**Step 3: Add similarity method**

Add to `src/graph/gds_scoring.py`:

```python
    def compute_similarity(self, min_similarity: float = 0.5, top_k: int = 10) -> dict:
        """Compute node similarity and create SIMILAR_TO relationships.

        Args:
            min_similarity: Minimum similarity threshold (0-1)
            top_k: Maximum similar nodes per card

        Returns:
            Computation statistics
        """
        query = f"""
        CALL gds.nodeSimilarity.write('{self.GRAPH_NAME}', {{
            writeRelationshipType: 'SIMILAR_TO',
            writeProperty: 'score',
            similarityCutoff: $min_similarity,
            topK: $top_k
        }})
        YIELD relationshipsWritten, nodesCompared
        RETURN relationshipsWritten, nodesCompared
        """

        result = self.conn.execute_query(query, {
            "min_similarity": min_similarity,
            "top_k": top_k
        })

        if result:
            print(f"✓ Computed node similarity")
            print(f"  Nodes compared: {result[0]['nodesCompared']}")
            print(f"  SIMILAR_TO relationships: {result[0]['relationshipsWritten']}")

        return result[0] if result else {}
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/integration/test_gds_scoring.py::test_compute_similarity -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/graph/gds_scoring.py tests/integration/test_gds_scoring.py
git commit -m "feat: add node similarity to GDS scoring"
```

---

## Task 5: Add Run All Scores Method

**Files:**
- Modify: `src/graph/gds_scoring.py`
- Test: `tests/integration/test_gds_scoring.py`

**Step 1: Write the failing test**

Add to `tests/integration/test_gds_scoring.py`:

```python
def test_run_all_algorithms():
    """Test running all GDS algorithms in sequence."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = [{"nodeCount": 100}]

    gds = GDSScoring(mock_conn)
    gds.run_all()

    # Should call execute_query multiple times (projection + 3 algorithms)
    assert mock_conn.execute_query.call_count >= 4
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_gds_scoring.py::test_run_all_algorithms -v`
Expected: FAIL

**Step 3: Add run_all method**

Add to `src/graph/gds_scoring.py`:

```python
    def run_all(self, min_similarity: float = 0.5, top_k: int = 10) -> dict:
        """Run all GDS algorithms in sequence.

        Args:
            min_similarity: Similarity threshold for node similarity
            top_k: Max similar nodes per card

        Returns:
            Combined results from all algorithms
        """
        print("\n" + "=" * 60)
        print("Running GDS Algorithms")
        print("=" * 60)

        results = {}

        # 1. Create projection
        print("\n1. Creating graph projection...")
        results["projection"] = self.create_projection()

        # 2. PageRank
        print("\n2. Computing PageRank...")
        results["pagerank"] = self.compute_pagerank()

        # 3. Community detection
        print("\n3. Detecting communities...")
        results["communities"] = self.detect_communities()

        # 4. Node similarity
        print("\n4. Computing node similarity...")
        results["similarity"] = self.compute_similarity(min_similarity, top_k)

        print("\n" + "=" * 60)
        print("GDS Algorithms Complete")
        print("=" * 60)

        return results
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/integration/test_gds_scoring.py::test_run_all_algorithms -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/graph/gds_scoring.py tests/integration/test_gds_scoring.py
git commit -m "feat: add run_all method to run all GDS algorithms"
```

---

## Task 6: Update Recommendation Query with GDS Scores

**Files:**
- Modify: `src/synergy/queries.py`
- Test: `tests/integration/test_queries_gds.py`

**Step 1: Write the failing test**

Create `tests/integration/test_queries_gds.py`:

```python
"""Integration tests for GDS-enhanced queries."""

from unittest.mock import Mock
from src.synergy.queries import DeckbuildingQueries
from src.graph.connection import Neo4jConnection


def test_find_synergistic_cards_uses_gds_scores():
    """Test that synergistic cards query uses GDS scores."""
    mock_conn = Mock(spec=Neo4jConnection)
    mock_conn.execute_query.return_value = [
        {
            "name": "Eternal Witness",
            "mana_cost": "{1}{G}{G}",
            "type": "Creature",
            "cmc": 3,
            "text": "When...",
            "shared_mechanics": ["etb_trigger"],
            "synergy_strength": 0.9,
            "roles": ["recursion"],
            "combined_score": 0.85,
            "pagerank_score": 0.02,
            "community_match": True
        }
    ]

    results = DeckbuildingQueries.find_synergistic_cards_v2(
        mock_conn,
        commander_name="Muldrotha, the Gravetide",
        max_cmc=4,
        limit=10
    )

    # Verify the query includes GDS fields
    call_args = mock_conn.execute_query.call_args[0][0]

    assert "pagerank_score" in call_args
    assert "community_id" in call_args
    assert "popularity_score" in call_args

    assert len(results) == 1
    assert results[0]["name"] == "Eternal Witness"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_queries_gds.py -v`
Expected: FAIL with "AttributeError: no attribute 'find_synergistic_cards_v2'"

**Step 3: Add new query method**

Add to `src/synergy/queries.py`:

```python
    @staticmethod
    def find_synergistic_cards_v2(conn: Neo4jConnection,
                                  commander_name: str,
                                  max_cmc: int = 4,
                                  limit: int = 50) -> list[dict]:
        """Find synergistic cards using GDS-enhanced scoring.

        Combines:
        - Mechanic synergy (40%)
        - PageRank importance (20%)
        - Popularity score (20%)
        - Community match bonus (20%)
        """
        query = """
        MATCH (cmd:Commander {name: $commander_name})
        MATCH (card:Card)
        WHERE card.cmc <= $max_cmc
          AND NOT card:Commander
          AND ALL(c IN card.color_identity WHERE c IN cmd.color_identity)

        // Mechanic synergy
        OPTIONAL MATCH (cmd)-[s:SYNERGIZES_WITH_MECHANIC]->(m:Mechanic)<-[:HAS_MECHANIC]-(card)

        // Role matches
        OPTIONAL MATCH (card)-[:FILLS_ROLE]->(r:Functional_Role)

        WITH card, cmd,
             max(coalesce(s.strength, 0)) AS synergy_score,
             collect(DISTINCT m.name) AS shared_mechanics,
             collect(DISTINCT r.name) AS roles

        // GDS scores with defaults
        WITH card, cmd, synergy_score, shared_mechanics, roles,
             coalesce(card.pagerank_score, 0) AS pagerank,
             coalesce(card.popularity_score, 0) AS popularity,
             CASE WHEN card.community_id = cmd.community_id THEN 1 ELSE 0 END AS community_match

        // Combined score: synergy(40%) + pagerank(20%) + popularity(20%) + community(20%)
        WITH card, synergy_score, shared_mechanics, roles, pagerank, popularity, community_match,
             (synergy_score * 0.4 +
              pagerank * 10 * 0.2 +
              popularity * 0.2 +
              community_match * 0.2) AS combined_score

        WHERE combined_score > 0 OR size(roles) > 0

        RETURN DISTINCT card.name AS name,
               card.mana_cost AS mana_cost,
               card.type_line AS type,
               card.cmc AS cmc,
               card.oracle_text AS text,
               shared_mechanics,
               synergy_score AS synergy_strength,
               roles,
               combined_score,
               pagerank AS pagerank_score,
               community_match = 1 AS community_match
        ORDER BY combined_score DESC, card.cmc ASC
        LIMIT $limit
        """

        return conn.execute_query(query, {
            "commander_name": commander_name,
            "max_cmc": max_cmc,
            "limit": limit
        })
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/integration/test_queries_gds.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/synergy/queries.py tests/integration/test_queries_gds.py
git commit -m "feat: add GDS-enhanced synergistic cards query"
```

---

## Task 7: Add GDS to Main Pipeline

**Files:**
- Modify: `main.py`

**Step 1: Add import**

Add to imports in `main.py`:

```python
from src.graph.gds_scoring import GDSScoring
```

**Step 2: Add GDS phase after commander analysis**

After Phase 8 (Commander Synergy Analysis), add:

```python
    # Phase 8b: GDS Scoring
    print("\nPHASE 8b: GDS Scoring")
    print("-" * 60)

    gds = GDSScoring(conn)
    gds_results = gds.run_all(min_similarity=0.5, top_k=10)

    print(f"\nGDS Summary:")
    print(f"  PageRank nodes: {gds_results.get('pagerank', {}).get('nodePropertiesWritten', 0)}")
    print(f"  Communities: {gds_results.get('communities', {}).get('communityCount', 0)}")
    print(f"  Similar pairs: {gds_results.get('similarity', {}).get('relationshipsWritten', 0)}")
```

**Step 3: Update example query to use v2**

In Phase 9, update the synergistic cards query:

```python
    print("\n1. Cards that synergize with Muldrotha (GDS-enhanced):")
    muldrotha_cards = DeckbuildingQueries.find_synergistic_cards_v2(
        conn,
        commander_name="Muldrotha, the Gravetide",
        max_cmc=4,
        limit=10
    )

    for i, card in enumerate(muldrotha_cards, 1):
        score = card.get('combined_score', 0)
        print(f"  {i}. {card['name']} ({card['mana_cost']}) - score: {score:.2f}")
```

**Step 4: Run main.py to verify**

Run: `python main.py`
Expected: GDS phase runs successfully

**Step 5: Commit**

```bash
git add main.py
git commit -m "feat: integrate GDS scoring into main pipeline"
```

---

## Task 8: Real Neo4j Integration Test

**Files:**
- Create: `tests/integration/test_gds_real.py`

**Step 1: Create integration test that uses real Neo4j**

Create `tests/integration/test_gds_real.py`:

```python
"""Integration tests for GDS with real Neo4j (requires running database)."""

import pytest
import os
from src.graph.connection import Neo4jConnection
from src.graph.gds_scoring import GDSScoring


# Skip if NEO4J_PASSWORD not set
pytestmark = pytest.mark.skipif(
    not os.environ.get("NEO4J_PASSWORD"),
    reason="NEO4J_PASSWORD not set"
)


@pytest.fixture
def neo4j_conn():
    """Get real Neo4j connection."""
    conn = Neo4jConnection(
        uri="bolt://localhost:7687",
        user="neo4j",
        password=os.environ.get("NEO4J_PASSWORD")
    )
    yield conn
    conn.close()


def test_gds_projection_real(neo4j_conn):
    """Test creating real GDS projection."""
    gds = GDSScoring(neo4j_conn)

    # This should work if data is loaded
    result = gds.create_projection()

    assert "nodeCount" in result
    assert result["nodeCount"] > 0


def test_gds_pagerank_real(neo4j_conn):
    """Test running real PageRank."""
    gds = GDSScoring(neo4j_conn)

    # Ensure projection exists
    if not gds.projection_exists():
        gds.create_projection()

    result = gds.compute_pagerank()

    assert "nodePropertiesWritten" in result
    assert result["nodePropertiesWritten"] > 0


def test_gds_full_pipeline_real(neo4j_conn):
    """Test full GDS pipeline with real data."""
    gds = GDSScoring(neo4j_conn)

    results = gds.run_all()

    assert "projection" in results
    assert "pagerank" in results
    assert "communities" in results
    assert "similarity" in results
```

**Step 2: Run test (will skip without Neo4j)**

Run: `pytest tests/integration/test_gds_real.py -v`
Expected: SKIP (or PASS if Neo4j running with data)

**Step 3: Commit**

```bash
git add tests/integration/test_gds_real.py
git commit -m "test: add real Neo4j GDS integration tests"
```

---

## Task 9: Final Verification and Push

**Step 1: Run all tests**

Run: `pytest tests/ -v`
Expected: All tests PASS (some skipped for real Neo4j)

**Step 2: Push changes**

```bash
git push origin feature/knowledge-graph-implementation
```

---

## Verification Checklist

After completing Phase 2:

- [ ] GDSScoring class created with all methods
- [ ] Graph projection creates successfully
- [ ] PageRank computes and writes to nodes
- [ ] Louvain detects communities
- [ ] Node similarity creates SIMILAR_TO relationships
- [ ] find_synergistic_cards_v2 uses GDS scores
- [ ] Main pipeline includes GDS phase
- [ ] All tests pass
- [ ] Changes committed and pushed
