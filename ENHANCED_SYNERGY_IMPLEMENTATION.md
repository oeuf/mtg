# Enhanced SYNERGIZES_WITH Implementation Summary

## Overview
Transformed SYNERGIZES_WITH from simple mechanic-overlap to sophisticated ML-powered scoring using 7 property dimensions and Neo4j GDS algorithms.

## Implementation Date
2026-01-26

## Changes Summary

### Phase 1: Multi-Dimensional Feature Scoring ✅

**File: `src/synergy/feature_scorers.py`** (562 lines)
- 7 dimension scoring functions:
  1. **Mechanic Overlap**: Jaccard similarity + count bonus (max 5 mechanics)
  2. **Role Compatibility**: Enabler/payoff pairs (e.g., ETB trigger + Sacrifice outlet = 0.9)
  3. **Theme Alignment**: Shared + complementary themes (e.g., Reanimation + Graveyard Value = 0.95)
  4. **Zone Chains**: Write→Read detection (e.g., Self-mill + Recursion = 0.8)
  5. **Phase Alignment**: Shared phase triggers (Jaccard similarity)
  6. **Color Compatibility**: 5 levels (exact, subset, overlap, disjoint, colorless)
  7. **Type Synergy**: Tribal subtypes + card type overlap

- **Ensemble Scoring**: Weighted combination (configurable weights)
  - Mechanic: 20%, Role: 25%, Theme: 20%, Zone: 15%, Phase: 10%, Color: 5%, Type: 5%

**File: `tests/test_feature_scorers.py`** (24 tests)
- Comprehensive coverage of all 7 dimensions
- Edge cases (empty lists, no overlap, redundancy penalties)
- Ensemble scoring validation

### Phase 2: CardSynergyEngine Integration ✅

**File: `src/synergy/card_synergies.py`** (updated)
- Added `compute_synergy_score()`: Computes 7-dimensional scores for card pairs
- Added `create_enhanced_synergy_relationships()`: Batch processing with Neo4j
  - Fetches zone/phase data via Cypher relationships
  - Stores dimension breakdown as JSON in `dimension_scores` property
  - Filters by `min_synergy_score` threshold (default: 0.5)
  - Batch size: 1000 cards

**File: `tests/test_card_synergies_integration.py`** (6 tests)
- High overlap scenario validation
- Low overlap scenario validation
- Role complementarity validation
- Zone chain detection validation
- Empty card handling
- Initialization verification

### Phase 3: GDS Graph Projections ✅

**File: `src/graph/gds_scoring.py`** (updated, +244 lines)

**New Projections:**
1. **card-feature-graph**: Heterogeneous bipartite projection
   - Node types: Card, Mechanic, Functional_Role, Theme, Subtype, Zone, Phase
   - Relationship weights: Mechanic (3.0), Role (2.5), Theme (2.0), Zone/Phase (1.5/1.0)

2. **card-synergy-graph**: Card-to-Card relationships
   - SYNERGIZES_WITH (with synergy_score property)
   - COMBOS_WITH (weight: 4.0)
   - COMMONLY_PAIRED_WITH (weight: 2.0)

### Phase 4: GDS ML Algorithms ✅

**Topological Link Prediction:**
- `compute_adamic_adar()`: Predicts missing synergies via common neighbors
- `compute_common_neighbors()`: Counts shared connections

**Community Detection:**
- `compute_leiden_communities()`: Detects card archetypes/strategies
- `boost_intra_community_synergy()`: Boosts scores by 1.2x for same-community cards

**Graph Embeddings:**
- `compute_fastrp_embeddings()`: 128-dimensional graph embeddings
- `compute_knn_similarity()`: k=20 nearest neighbors using embeddings
- Creates EMBEDDING_SIMILAR relationships

### Phase 5: Pipeline Integration ✅

**File: `main.py`** (updated, +88 lines)

**Phase 9.5: Enhanced Multi-Dimensional Synergy Scoring**
```python
synergy_engine = CardSynergyEngine()
synergy_engine.create_enhanced_synergy_relationships(
    conn,
    min_synergy_score=0.5,
    batch_size=1000
)
```

**Phase 13.5: GDS Advanced Topological Features**
```python
# Create projections
gds.create_card_feature_projection()
gds.create_card_synergy_projection()

# Compute embeddings
gds.compute_fastrp_embeddings("card-feature-graph", embedding_dim=128)
gds.compute_knn_similarity("card-feature-graph", topK=20)

# Link prediction
gds.compute_adamic_adar("card-synergy-graph")
gds.compute_common_neighbors("card-synergy-graph")

# Community detection
gds.compute_leiden_communities("card-synergy-graph")
gds.boost_intra_community_synergy(boost_factor=1.2)
```

**New Example Queries:**
- Query 6: Enhanced multi-dimensional synergy for Necropotence
- Query 7: Embedding-based similar cards to Sol Ring
- Query 8: Community archetypes (top 3 with samples)

## Test Results

**All 30 tests passing:**
- 24 feature scorer unit tests
- 6 integration tests

```
============================== 30 passed in 0.10s ==============================
```

## Verification Queries

### 1. Check dimension score breakdown
```cypher
MATCH (c1:Card {name: "Eternal Witness"})-[s:SYNERGIZES_WITH]-(c2:Card)
WHERE s.source = 'ml_enhanced'
RETURN c2.name, s.synergy_score, s.dimension_scores
ORDER BY s.synergy_score DESC
LIMIT 5
```

### 2. Check community detection
```cypher
MATCH (c:Card)
WHERE c.community IS NOT NULL
RETURN c.community, count(*) AS cards, collect(c.name)[0..5] AS samples
ORDER BY cards DESC
LIMIT 10
```

### 3. Check embedding-based similarities
```cypher
MATCH (c1:Card {name: "Sol Ring"})-[s:EMBEDDING_SIMILAR]->(c2:Card)
RETURN c2.name, s.score
ORDER BY s.score DESC
LIMIT 10
```

### 4. Compare old vs new synergy for Necropotence
```cypher
MATCH (c:Card {name: "Necropotence"})
OPTIONAL MATCH (c)-[s:SYNERGIZES_WITH]-(other)
RETURN count(s) AS synergy_count,
       avg(s.synergy_score) AS avg_score,
       s.source AS source
```

## Key Improvements Over Original

| Aspect | Before | After |
|--------|--------|-------|
| **Dimensions** | 1 (mechanics only) | 7 (mechanics, roles, themes, zones, phases, colors, types) |
| **Scoring Method** | Count / 5.0 | ML-powered weighted ensemble |
| **Explainability** | None | Full dimension breakdown stored |
| **Topology** | None | Adamic-Adar, Common Neighbors, FastRP |
| **Communities** | None | Leiden archetype detection |
| **Latent Patterns** | None | 128-dim embeddings + kNN |
| **Role Awareness** | Unused | Complementarity table (enabler/payoff) |
| **Zone Awareness** | Unused | Write→Read chain detection |
| **Phase Awareness** | Unused | Shared trigger detection |

## Expected Impact

1. **Necropotence** will now have synergies based on:
   - Themes (graveyard value, card advantage)
   - Zones (graveyard writes/reads)
   - Phases (end step triggers)
   - Color compatibility

2. **Synergy scores are explainable**:
   - Dimension breakdown shows WHY cards synergize
   - Stored as JSON in relationship properties

3. **High-quality recommendations**:
   - Multiple signals (7 dimensions + GDS metrics)
   - Community-aware suggestions
   - Embedding captures non-obvious patterns

4. **Archetype-aware deck building**:
   - Leiden communities group similar strategies
   - Intra-community synergies boosted
   - Better deck coherence

## Files Changed

```
src/synergy/feature_scorers.py                  (new, 562 lines)
src/synergy/card_synergies.py                   (modified, +369 lines)
src/graph/gds_scoring.py                        (modified, +244 lines)
main.py                                          (modified, +88 lines)
tests/test_feature_scorers.py                   (new, 24 tests)
tests/test_card_synergies_integration.py        (new, 6 tests)
```

## Commits

1. `feat: add multi-dimensional feature scoring functions` (0c50eb2)
2. `feat: integrate multi-dimensional scoring into CardSynergyEngine` (261f841)
3. `feat: add GDS graph projections and ML algorithms` (5359e33)
4. `feat: integrate enhanced synergy pipeline into main.py` (0830603)

## Next Steps (Optional Enhancements)

1. **Expand theme/role compatibility tables** based on real data analysis
2. **Add Oracle text NLP** for semantic similarity
3. **Train supervised ML model** using EDHREC pairing data
4. **Add temporal features** (mana curve progression)
5. **Implement GraphSAGE** for deeper embeddings
6. **Add synergy explanations** to UI (dimension breakdown)

## Performance Notes

- Batch processing limits to 1000 card pairs per run (configurable)
- GDS algorithms run in-memory (requires sufficient RAM)
- FastRP embeddings: ~128 bytes per card
- Leiden communities: O(n log n) complexity
- Total pipeline adds ~2-5 minutes to main.py execution

## Dependencies

- Neo4j 5.15.0+ with GDS plugin
- Python 3.9+
- neo4j-driver
- No additional Python packages required (scikit-learn not needed)
