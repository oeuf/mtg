# Next Steps - MTG Commander Knowledge Graph

**Last Updated:** 2026-02-01
**Current Status:** Phase 1-2 Complete, Mechanics Bug Fixed, Ready for Rerun

## Current State

### ✅ Completed (2026-02-01)
- Enhanced SYNERGIZES_WITH with 7-dimensional scoring
- FastRP embeddings (128-dim) for 28,722 nodes
- kNN similarity with topK=100 (2.76M relationships)
- Leiden community detection (21,107 communities)
- Fixed mechanics extraction (added discard_trigger, exile_mechanic, life_payment, skip_draw)
- Created comprehensive CLAUDE.md project memory

### 🔧 Recent Fixes
- **Mechanics Extraction Bug** - Necropotence and similar cards now properly tagged
- **kNN topK** - Increased from 20 to 100 (Necrodominance now appears: 0.9451 similarity)

## Three Paths Forward

### Option 1: Rerun Data Pipeline ⭐ RECOMMENDED

**Why:** Populate new mechanics patterns for all 27,619 cards

**Command:**
```bash
source venv/bin/activate
export NEO4J_PASSWORD="mtg-commander"
python main.py
```

**Duration:** ~10-15 minutes

**What it does:**
- Phases 1-6: Download data, parse cards, enrich with new mechanics
- Phase 7-9: Load to Neo4j, create relationships
- Phase 9.5: Enhanced synergy scoring
- Phase 10-13: Related cards, commander analysis, popularity, GDS
- Phase 13.5: FastRP embeddings, kNN, communities
- Phase 14: Example queries

**Expected outcome:**
- All cards have updated mechanics arrays
- Necropotence: ['discard_trigger', 'exile_mechanic', 'life_payment', 'skip_draw']
- Necrodominance: ['exile_mechanic', 'skip_draw']
- Improved synergy scoring accuracy

---

### Option 2: Phase 3 - Validation

**Goal:** Quantify recommendation quality against reference decks

**Plan:** `docs/plans/2026-01-19-phase3-validation.md`

**Tasks:**
1. Load reference Muldrotha deck (EDHREC or precon)
2. Generate synergy recommendations for Muldrotha
3. Calculate ranking metrics:
   - Precision@K (top K recommendations in reference deck)
   - Recall@K (reference cards found in top K)
   - Mean Reciprocal Rank (MRR)
4. Document accuracy results
5. Compare mechanic-only vs. 7-dimensional scoring

**Estimated time:** 2-3 hours

**Prerequisite:** Option 1 (rerun pipeline) recommended first

---

### Option 3: Phase 4 - FastAPI Backend

**Goal:** Build REST API for deck building tools

**Plan:** `docs/plans/2026-01-19-phase4-api.md`

**Endpoints to build:**
```python
GET  /api/commanders              # List all commanders
GET  /api/commanders/{name}       # Commander details + synergies
GET  /api/cards/{name}/synergies  # Synergistic cards
POST /api/decks/analyze           # Analyze deck composition
GET  /api/graph/explore           # Graph visualization data
```

**Tech Stack:**
- FastAPI (async Python web framework)
- Neo4j driver for queries
- Pydantic for models
- pytest for testing

**Estimated time:** 6-8 hours

**Prerequisite:** Option 1 (rerun pipeline) recommended first

---

## Recommendation

**Start with Option 1 (Rerun Data Pipeline)**

Rationale:
- Ensures all cards have proper mechanics tagging
- Improves embedding quality (mechanics are part of HAS_MECHANIC relationships)
- Provides clean foundation for validation (Option 2)
- Required before building API (Option 3) to ensure accurate results

After pipeline completes, choose between:
- **Option 2** if you want to measure/validate quality
- **Option 3** if you want to build the frontend-facing API

## How to Execute

### Running Option 1 Now:
```bash
# Ensure Neo4j is running
docker ps | grep neo4j

# Activate environment
source venv/bin/activate

# Set credentials
export NEO4J_PASSWORD="mtg-commander"

# Run pipeline (10-15 minutes)
python main.py

# Verify completion
# Open http://localhost:7474 and check card mechanics
```

### After Option 1 Completes:
```bash
# Verify Necropotence mechanics
# In Neo4j Browser:
MATCH (c:Card {name: 'Necropotence'})-[:HAS_MECHANIC]->(m:Mechanic)
RETURN m.name

# Should return: discard_trigger, exile_mechanic, life_payment, skip_draw
```

## Questions?

- **"Will rerunning delete existing data?"** - Yes, main.py drops and recreates the graph
- **"Can I run phases individually?"** - Yes, use `run_enhanced_synergy.py` for 9.5 and 13.5
- **"How do I know it worked?"** - Check Neo4j Browser for HAS_MECHANIC relationships
- **"What if it fails?"** - Check `docker restart neo4j-mtg` and verify NEO4J_PASSWORD

## Files to Reference

- **Current plan:** This file
- **Project memory:** `CLAUDE.md`
- **Phase 3 plan:** `docs/plans/2026-01-19-phase3-validation.md`
- **Phase 4 plan:** `docs/plans/2026-01-19-phase4-api.md`
- **Implementation summary:** `ENHANCED_SYNERGY_IMPLEMENTATION.md`
