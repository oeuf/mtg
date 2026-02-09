# MTG Commander Knowledge Graph

## Quick Start

```bash
docker-compose up -d && sleep 10         # Start Neo4j
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
export NEO4J_PASSWORD="password"         # Matches docker-compose.yml
python -u main.py                        # Run pipeline
open http://localhost:7474               # Neo4j Browser
```

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
- `docker-compose.yml` - Neo4j 5.15.0-enterprise (hardcoded auth: neo4j/password)
- `requirements.txt` - Python dependencies
- Password: Set `NEO4J_PASSWORD=password` for Python scripts (matches docker-compose)

## Status

**Loaded:**
- 27,619 cards, 658 mechanics, 39,144 HAS_MECHANIC relationships
- 28,722 FastRP embeddings (128-dim), 2.76M kNN similarities (topK=100)
- 21,107 Leiden communities (modularity: 0.630)
- 861,686 community-boosted synergies

**Synergy Scoring:**
7 dimensions (mechanic overlap, role compatibility, theme alignment, zone chains, phase triggers, color compatibility, type synergy) with ensemble weighting. 30 passing tests.

**Known Issues:**
- **Phase 9.5:** `create_enhanced_synergy_relationships()` creates 0 relationships (batch limit without pagination). Run `python run_enhanced_synergy.py` instead.

**Roadmap:**
- Phase 3: Validation (Muldrotha deck comparison, ranking metrics)
- Phase 4: FastAPI (`/api/commanders`, `/api/cards`, `/api/decks`, `/api/graph`)
- Phase 5: Next.js UI (Deck Builder, Analyzer, Explorer, Lookup)

## How to Run

### Initial Setup
```bash
# Verify Python 3.9+
python3 --version

# Start Neo4j
docker-compose up -d && sleep 10

# Verify Neo4j running
docker ps | grep mtg-neo4j
curl -f http://localhost:7474 && echo "✓ Neo4j accessible"

# Install dependencies
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# Set password (matches docker-compose.yml)
export NEO4J_PASSWORD="password"

# Run pipeline
python -u main.py
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
pytest tests/unit/ -v  # Integration tests hit memory limits on full DB
pytest tests/test_feature_scorers.py -v  # Synergy scoring tests
```

## Development Patterns

### Adding New Mechanics
1. Add pattern to `src/parsing/mechanics.py`
2. Test with `MechanicExtractor.extract_mechanics()`
3. Rerun pipeline to populate
4. Verify in Neo4j

**Recent patterns:** `discard_trigger`, `exile_mechanic`, `life_payment`, `skip_draw` (case-insensitive with optional modifiers)

### GDS Algorithm Workflow
1. Create projection with `gds.create_*_projection()`
2. Run algorithm with `gds.compute_*()`
3. Write results back to graph
4. Drop projection when done

### Synergy Scoring
- **Multi-dimensional:** Use `CardSynergyEngine.compute_synergy_score()`
- **Returns:** (score: float, details: dict) with dimension breakdown
- **Dimensions:** mechanic_overlap, role_compatibility, theme_alignment, zone_chain, phase_alignment, color_compatibility, type_synergy

## Cypher Queries

```cypher
-- Find similar cards
MATCH (c1:Card {name: 'Necropotence'})-[emb:EMBEDDING_SIMILAR]-(c2:Card)
RETURN c2.name, emb.score ORDER BY emb.score DESC LIMIT 20

-- Check communities
MATCH (c:Card) WHERE c.community IS NOT NULL
RETURN c.community, count(*) AS size, collect(c.name)[0..5] AS samples
ORDER BY size DESC LIMIT 10

-- Cards with mechanic
MATCH (c:Card)-[:HAS_MECHANIC]->(m:Mechanic {name: 'etb_trigger'})
RETURN c.name, c.mana_cost LIMIT 10

-- Synergy breakdown
MATCH (c1:Card {name: 'Eternal Witness'})-[s:SYNERGIZES_WITH]-(c2:Card)
WHERE s.source = 'ml_enhanced'
RETURN c2.name, s.synergy_score, s.dimension_scores
ORDER BY s.synergy_score DESC LIMIT 5
```


## Troubleshooting

**Neo4j Connection Failures:**
```bash
# Verify container runs
docker ps | grep mtg-neo4j

# Fix AuthenticationRateLimit
docker restart mtg-neo4j && sleep 15 && export NEO4J_PASSWORD="password"
```

**Python Buffering:** Use `python -u main.py` for unbuffered output in background tasks.

**Memory:** Neo4j defaults to 1.3 GiB. GDS algorithms run in-memory; increase `docker-compose.yml` limits if OOM errors occur.

**Tests:** Integration tests need Neo4j. Auth rate limits: restart container.

**APOC Missing:** Container lacks APOC. Use `json.dumps(data)` instead of `apoc.convert.toJson()`.

## Documentation

- `ENHANCED_SYNERGY_IMPLEMENTATION.md` - Synergy scoring details
- `VERIFICATION_EVIDENCE.md` - Test evidence
- `docs/plans/` - Implementation plans
- **MTGJSON:** https://mtgjson.com
- **Neo4j GDS:** https://neo4j.com/docs/graph-data-science/current/
