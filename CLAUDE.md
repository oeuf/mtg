# MTG Commander Knowledge Graph - Project Memory

## Project Overview

**Goal:** Build an ML-powered knowledge graph for Magic: The Gathering Commander format, providing intelligent deck recommendations, card synergy analysis, and deck building tools.

**Tech Stack:**
- **Backend:** Python 3.9+, Neo4j 5.26.0 with GDS plugin
- **Data:** MTGJSON (AtomicCards.json, RelatedCards.json, Precons)
- **ML/Graph:** Neo4j Graph Data Science (FastRP embeddings, Leiden communities, kNN)
- **Future:** FastAPI backend + Next.js frontend

## Architecture

```
Data Pipeline:
MTGJSON → Parsing/Enrichment → Neo4j Graph → GDS Algorithms → Enhanced Recommendations

Graph Schema:
- Nodes: Card, Commander, Mechanic, Functional_Role, Theme, Subtype, Zone, Phase
- Relationships: HAS_MECHANIC, FILLS_ROLE, SUPPORTS_THEME, SYNERGIZES_WITH,
                 COMBOS_WITH, EMBEDDING_SIMILAR, INTERACTS_WITH_ZONE, TRIGGERS_IN_PHASE
```

## Key Files

### Data Pipeline
- `main.py` - Main pipeline orchestrator (Phases 1-14)
- `src/data/mtgjson_downloader.py` - Downloads MTGJSON data
- `src/data/atomic_cards_parser.py` - Parses card data
- `src/parsing/mechanics.py` - Extracts mechanics from oracle text
- `src/parsing/functional_roles.py` - Categorizes functional roles
- `src/parsing/properties.py` - Extracts card properties

### Graph & ML
- `src/graph/connection.py` - Neo4j connection management
- `src/graph/loaders.py` - Batch loading cards/relationships
- `src/graph/gds_scoring.py` - GDS algorithms (FastRP, kNN, Leiden)
- `src/synergy/feature_scorers.py` - 7-dimensional synergy scoring
- `src/synergy/card_synergies.py` - Synergy relationship engine
- `run_enhanced_synergy.py` - Standalone script for Phases 9.5 & 13.5

### Configuration
- `docker-compose.yml` - Neo4j container setup
- `requirements.txt` - Python dependencies
- `.env` - Neo4j credentials (NEO4J_PASSWORD)

## Current State (2026-02-01)

### ✅ Completed Features

**Phase 1: Foundation**
- ✅ Node types: Card, Commander, Mechanic, Functional_Role, Theme, Subtype, Zone, Phase
- ✅ Relationship types: 10+ types including HAS_MECHANIC, FILLS_ROLE, INTERACTS_WITH_ZONE
- ✅ Card properties: 20+ properties including mechanics, themes, functional_categories
- ✅ Data loading: 27,619 cards, 658 mechanics, 39,144 mechanic relationships

**Phase 2: GDS & ML**
- ✅ FastRP embeddings: 128-dimensional graph embeddings for 28,722 nodes
- ✅ kNN similarity: 2.76M EMBEDDING_SIMILAR relationships (topK=100)
- ✅ Leiden communities: 21,107 communities detected (modularity: 0.630)
- ✅ Community boosting: 861,686 synergy relationships boosted for same-community cards

**Enhanced SYNERGIZES_WITH**
- ✅ 7-dimensional feature scoring:
  1. Mechanic overlap (Jaccard + count bonus)
  2. Role compatibility (enabler/payoff pairs)
  3. Theme alignment (shared + complementary)
  4. Zone chains (write→read interactions)
  5. Phase alignment (shared triggers)
  6. Color compatibility (5 levels)
  7. Type synergy (tribal + card types)
- ✅ Ensemble scoring with configurable weights
- ✅ 30 passing tests (100% test coverage for synergy scoring)

### 🚧 Known Issues

1. **Mechanics Extraction** - FIXED (2026-02-01)
   - Added patterns: discard_trigger, exile_mechanic, life_payment, skip_draw
   - Necropotence/Necrodominance now properly tagged

2. **Phase 9.5 Batch Limit**
   - `create_enhanced_synergy_relationships()` creates 0 relationships
   - Issue: Batch size 1000 + LIMIT without pagination
   - Workaround: Use `run_enhanced_synergy.py` separately

### ❌ Not Implemented

**Phase 3: Validation**
- Muldrotha reference deck comparison
- Ranking accuracy metrics

**Phase 4: FastAPI Backend**
- `/api/commanders` endpoint
- `/api/cards` endpoint
- `/api/decks` endpoint
- `/api/graph` endpoint

**Phase 5: Next.js Frontend**
- Deck Builder, Analyzer, Explorer, Lookup UIs

## How to Run

### Initial Setup
```bash
# Start Neo4j with GDS
docker-compose up -d

# Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set Neo4j password
export NEO4J_PASSWORD="mtg-commander"

# Run main pipeline (all phases)
python main.py
```

### Run Enhanced Synergy Only
```bash
# Run Phases 9.5 and 13.5 separately
python run_enhanced_synergy.py
```

### Verify Graph
```bash
# Open Neo4j Browser
open http://localhost:7474

# Sample queries:
MATCH (c:Card)-[s:EMBEDDING_SIMILAR]->(similar:Card {name: 'Necropotence'})
RETURN c.name, s.score ORDER BY s.score DESC LIMIT 10
```

### Run Tests
```bash
pytest tests/ -v
pytest tests/test_feature_scorers.py -v  # Synergy scoring tests
pytest tests/test_card_synergies_integration.py -v  # Integration tests
```

## Development Patterns

### Adding New Mechanics
1. Add pattern to `src/parsing/mechanics.py`
2. Test with `MechanicExtractor.extract_mechanics()`
3. Rerun pipeline to populate
4. Verify in Neo4j

### GDS Algorithm Workflow
1. Create projection with `gds.create_*_projection()`
2. Run algorithm with `gds.compute_*()`
3. Write results back to graph
4. Drop projection when done

### Synergy Scoring
- **Multi-dimensional:** Use `CardSynergyEngine.compute_synergy_score()`
- **Returns:** (score: float, details: dict) with dimension breakdown
- **Dimensions:** mechanic_overlap, role_compatibility, theme_alignment, zone_chain, phase_alignment, color_compatibility, type_synergy

## Common Queries

### Find Similar Cards
```cypher
MATCH (c1:Card {name: 'Necropotence'})-[emb:EMBEDDING_SIMILAR]-(c2:Card)
RETURN c2.name, emb.score
ORDER BY emb.score DESC LIMIT 20
```

### Check Card Communities
```cypher
MATCH (c:Card)
WHERE c.community IS NOT NULL
RETURN c.community, count(*) AS size, collect(c.name)[0..5] AS samples
ORDER BY size DESC LIMIT 10
```

### Find Cards with Specific Mechanics
```cypher
MATCH (c:Card)-[:HAS_MECHANIC]->(m:Mechanic {name: 'etb_trigger'})
RETURN c.name, c.mana_cost LIMIT 10
```

### Check Synergy Score Breakdown
```cypher
MATCH (c1:Card {name: 'Eternal Witness'})-[s:SYNERGIZES_WITH]-(c2:Card)
WHERE s.source = 'ml_enhanced'
RETURN c2.name, s.synergy_score, s.dimension_scores
ORDER BY s.synergy_score DESC LIMIT 5
```

## Recent Changes

### 2026-02-01
- ✅ Reran kNN with topK=100 (was 20)
- ✅ Fixed mechanics extraction for Necropotence-like cards
- ✅ Added patterns: discard_trigger, exile_mechanic, life_payment, skip_draw
- ✅ Necrodominance similarity: 0.9451 (previously not in top-20)

### 2026-01-26
- ✅ Implemented 7-dimensional synergy scoring
- ✅ Integrated FastRP embeddings and kNN
- ✅ Added Leiden community detection
- ✅ Created 2.76M embedding similarity relationships

## Next Steps

1. **Rerun Pipeline** - Populate mechanics for all cards with new patterns
2. **Phase 3: Validation** - Compare recommendations against reference decks
3. **Phase 4: FastAPI** - Build REST API endpoints
4. **Phase 5: Frontend** - Build Next.js UI

## Troubleshooting

### Neo4j Connection Issues
- Verify container running: `docker ps | grep neo4j`
- Check password: `echo $NEO4J_PASSWORD`
- Reset auth: `docker restart neo4j-mtg`

### Memory Issues
- Neo4j memory limit: 1.3 GiB default
- Increase in `docker-compose.yml` if needed
- GDS algorithms run in-memory (require sufficient RAM)

### Test Failures
- Integration tests need Neo4j running
- Auth rate limits: Wait or restart container
- Check `pytest.ini` for configuration

## Documentation

- `ENHANCED_SYNERGY_IMPLEMENTATION.md` - Complete synergy scoring implementation details
- `VERIFICATION_EVIDENCE.md` - Test/verification evidence from Knowledge Graph V2
- `docs/plans/` - Phase-by-phase implementation plans

## Contact & Links

- **MTGJSON:** https://mtgjson.com
- **Neo4j GDS Docs:** https://neo4j.com/docs/graph-data-science/current/
- **Project Plans:** `docs/plans/2026-01-19-*.md`
