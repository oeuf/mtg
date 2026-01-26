# MTG Commander Knowledge Graph v2

A Neo4j knowledge graph for Magic: The Gathering Commander format, enriched with comprehensive rules parsing, zone interactions, and phase triggers.

## Quick Start

### 1. Start Neo4j

```bash
./scripts/start_neo4j.sh
```

This starts a Neo4j 5.15.0 container with Graph Data Science plugin.

**Verify it's running:**
```bash
docker ps | grep neo4j
```

You should see output showing the container is up.

### 2. Access Neo4j Browser

Open http://localhost:7474 in your browser.

**Login credentials:**
- Username: `neo4j`
- Password: `password` (or `mtg-commander` if using existing container)

### 3. Run the Pipeline

```bash
source venv/bin/activate
python main.py
```

This executes 14 phases:
1. Download MTGJSON data
2. Parse comprehensive rules (2025-11-14)
3. Parse card data
4. Enrich cards with derived properties
5. Connect to Neo4j
6. Create constraints
7. Create Theme nodes
8. Load cards
9. Create relationships (mechanics, roles, zones, phases, themes, subtypes, card synergies)
10. Integrate combos
11. Analyze commanders
12. Calculate popularity scores
13. Compute GDS similarity
14. Example queries

### 4. Run Test Queries

**Query cards that interact with graveyards:**
```bash
python scripts/test_queries.py --query graveyard_cards --colors B G
```

**Query cards with upkeep triggers:**
```bash
python scripts/test_queries.py --query upkeep_triggers --colors U
```

**View all zone interactions:**
```bash
python scripts/test_queries.py --query zone_interactions
```

**View phase trigger statistics:**
```bash
python scripts/test_queries.py --query phase_triggers
```

## V2 Features

### 1. Popularity Scoring
- **EDHREC Rank Integration**: Cards scored 0.0-1.0 based on EDHREC popularity
- **Logarithmic Scaling**: Rank 1 = 1.0, Rank 30000 = 0.0
- **Property**: `card.popularity_score`
- **Indexed**: Fast filtering by popularity

### 2. GDS-Based Similarity (SIMILAR_TO Relationships)
- **Neo4j Graph Data Science**: Node similarity algorithm
- **Based on**: Shared mechanics, roles, themes, subtypes
- **Relationship**: `(Card)-[:SIMILAR_TO {score}]->(Card)`
- **Query**: Find cards similar to Sol Ring, Eternal Witness, etc.
- **Parameters**: topK=10, similarity_cutoff=0.5

### 3. Card-to-Card Synergies (SYNERGIZES_WITH Relationships)
- **Mechanic Overlap**: Cards sharing 2+ mechanics
- **Role Complementarity**: etb_trigger + sacrifice_outlet = 0.9
- **Relationship**: `(Card)-[:SYNERGIZES_WITH {synergy_score, shared_mechanics}]->(Card)`
- **Query**: Build synergistic packages around key cards

### 4. Enhanced Theme Detection (20 Categories)
**Original 10 themes:**
- reanimation, aristocrats, tokens, lands_matter, spellslinger
- graveyard_value, lifegain, tribal, voltron, stax

**New 10 themes:**
- **draw_engines**: Repeatable card draw effects
- **blink**: Exile and return for ETB value
- **counters**: +1/+1 counters and proliferate
- **storm**: Spell copying and storm count
- **artifacts_matter**: Artifact synergies
- **enchantments_matter**: Enchantment synergies and constellation
- **group_hug**: Symmetrical benefits for all players
- **wheels**: Mass discard and draw
- **superfriends**: Planeswalker synergies
- **x_spells**: X spell cost manipulation

### 5. Subtype Relationships
- **HAS_SUBTYPE**: Cards linked to creature types (Elf, Goblin, Zombie, etc.)
- **Tribal Queries**: Find all Goblins, all Dragons, etc.

## Graph Schema

### Nodes

**Card/Commander**
- Properties: name, mana_cost, cmc, oracle_text, color_identity, types, keywords
- Derived: mana_efficiency, color_pip_intensity, is_fast_mana, zone_interactions, phase_triggers

**Zone** (8 nodes)
- library, hand, battlefield, graveyard, stack, exile, command, ante
- Properties: rule_number, is_public, is_ordered, description

**Phase** (12 nodes)
- untap, upkeep, draw, main_1, combat phases, main_2, end_step, cleanup
- Properties: rule_number, order, parent, is_step

**Mechanic**
- ETB triggers, dies triggers, keywords, cost reduction

**Functional_Role**
- ramp, card_draw, removal, recursion, protection

**Theme** (20 nodes)
- reanimation, aristocrats, tokens, draw_engines, blink, counters, storm, etc.
- Properties: description

**Subtype** (415+ nodes)
- Creature types: Elf, Goblin, Dragon, Zombie, etc.
- Properties: name

### Relationships

- `(Card)-[:HAS_MECHANIC]->(Mechanic)`
- `(Card)-[:FILLS_ROLE]->(Functional_Role)`
- `(Card)-[:INTERACTS_WITH_ZONE {interaction_type}]->(Zone)`
- `(Card)-[:TRIGGERS_IN_PHASE {trigger_type}]->(Phase)`
- `(Card)-[:COMBOS_WITH {strength}]->(Card)`
- `(Card)-[:SUPPORTS_THEME]->(Theme)` **[V2]**
- `(Card)-[:HAS_SUBTYPE]->(Subtype)` **[V2]**
- `(Card)-[:SIMILAR_TO {score}]->(Card)` **[V2]**
- `(Card)-[:SYNERGIZES_WITH {synergy_score, shared_mechanics}]->(Card)` **[V2]**
- `(Commander)-[:SYNERGIZES_WITH_MECHANIC]->(Mechanic)`

## Example Queries

**In Neo4j Browser (http://localhost:7474):**

Find cards that interact with graveyard:
```cypher
MATCH (c:Card)-[r:INTERACTS_WITH_ZONE]->(z:Zone {name: "graveyard"})
RETURN c.name, r.interaction_type, c.oracle_text
LIMIT 10
```

Find upkeep triggers:
```cypher
MATCH (c:Card)-[r:TRIGGERS_IN_PHASE]->(p:Phase {name: "upkeep"})
RETURN c.name, r.trigger_type, c.oracle_text
LIMIT 10
```

Zone interaction statistics:
```cypher
MATCH (z:Zone)<-[r:INTERACTS_WITH_ZONE]-(c:Card)
RETURN z.name, count(c) as card_count, r.interaction_type
ORDER BY card_count DESC
```

**V2 Example Queries:**

Find cards similar to Sol Ring:
```cypher
MATCH (c1:Card {name: "Sol Ring"})-[s:SIMILAR_TO]->(c2:Card)
WHERE s.score >= 0.6
RETURN c2.name, s.score
ORDER BY s.score DESC
LIMIT 10
```

Find high-synergy card pairs:
```cypher
MATCH (c1:Card)-[s:SYNERGIZES_WITH]-(c2:Card)
WHERE s.synergy_score > 0.8
RETURN c1.name, c2.name, s.synergy_score, s.shared_mechanics
ORDER BY s.synergy_score DESC
LIMIT 20
```

Find popular draw engines:
```cypher
MATCH (c:Card)-[:SUPPORTS_THEME]->(t:Theme {name: "draw_engines"})
WHERE c.popularity_score > 0.7
RETURN c.name, c.popularity_score, c.edhrec_rank
ORDER BY c.popularity_score DESC
LIMIT 10
```

Find all Goblins with blink synergies:
```cypher
MATCH (c:Card)-[:HAS_SUBTYPE]->(s:Subtype {name: "Goblin"})
WHERE exists((c)-[:SUPPORTS_THEME]->(:Theme {name: "blink"}))
RETURN c.name, c.mana_cost
ORDER BY c.cmc ASC
```

## Testing

Run all tests:
```bash
source venv/bin/activate
python -m pytest tests/ -v
```

Run with coverage:
```bash
python -m pytest tests/ --cov=src --cov-report=term-missing
```

**Verified test results:**
- 103 tests passing, 9 skipped
- 79% overall coverage
- 100% coverage on zone_detector, phase_detector
- 98% coverage on rules_parser

## Docker Management

**Start Neo4j:**
```bash
./scripts/start_neo4j.sh
```

**Stop Neo4j:**
```bash
./scripts/stop_neo4j.sh
```

**View logs:**
```bash
docker logs mtg-neo4j
```

**Access container shell:**
```bash
docker exec -it mtg-neo4j bash
```

## Port Configuration

- Neo4j Browser: http://localhost:7474
- Bolt Protocol: bolt://localhost:7687

Change ports in `docker-compose.yml` if needed.

## Rules Parser

The comprehensive rules parser extracts:

1. **Keyword Abilities (Rule 702):** ~150 abilities (flying, haste, etc.)
2. **Keyword Actions (Rule 701):** ~70 actions (destroy, exile, etc.)
3. **Zones (Rules 400-408):** All 8 game zones with metadata
4. **Phases (Rules 500-514):** All 12 phases/steps with ordering
5. **Commander Rules (Rule 903):** Deck size, life total, commander tax

Parser output enriches card data with:
- `zone_interactions`: Zones this card references
- `phase_triggers`: Phases where abilities trigger

## Project Structure

```
.
├── docker-compose.yml          # Neo4j container config
├── main.py                     # 11-phase pipeline
├── scripts/
│   ├── start_neo4j.sh         # Start container
│   ├── stop_neo4j.sh          # Stop container
│   └── test_queries.py        # Pre-built test queries
├── src/
│   ├── data/                  # MTGJSON parsers
│   ├── graph/                 # Neo4j loaders
│   │   ├── connection.py      # Database connection
│   │   └── loaders.py         # Node/relationship creation
│   ├── parsing/               # Card enrichment
│   │   ├── rules_parser.py    # Comprehensive rules parser
│   │   ├── zone_detector.py   # Zone interaction detection
│   │   ├── phase_detector.py  # Phase trigger detection
│   │   └── enrichment.py      # Card data enrichment
│   └── synergy/               # Synergy analysis
└── tests/                     # 103 tests (79% coverage)
```

## Troubleshooting

**Container won't start:**
- Check Docker is running: `docker ps`
- Check ports 7474/7687 aren't in use: `lsof -i :7474`

**Authentication errors:**
- Default password is `password`
- Existing containers may use `mtg-commander`
- Reset: `docker-compose down -v` then restart

**No data in graph:**
- Run the pipeline: `python main.py`
- Check Neo4j logs: `docker logs mtg-neo4j`

**Query timeouts:**
- Increase timeout in connection.py
- Check indexes created: Run `SHOW INDEXES` in Neo4j Browser

## Requirements

- Python 3.11+
- Docker Desktop
- 4GB RAM minimum
- Internet connection (for MTGJSON download)

## License

Data: MTGJSON (https://mtgjson.com)
Rules: Wizards of the Coast
