# Commander Deckbuilding Knowledge Graph

A Neo4j-based knowledge graph for Magic: The Gathering Commander deckbuilding, using MTGJSON data to provide synergy detection, card recommendations, and combo identification.

## Features

- **Synergy Detection** - Find cards that work well with a commander based on shared mechanics
- **Deck Building Assistant** - Generate deck shells by functional role (8x8 method)
- **Combo Detection** - Identify known infinite combos from MTGJSON Spellbook
- **Token Generators** - Find cards that create specific tokens
- **Card Recommendations** - Get efficient cards for specific roles in your colors

## Technology Stack

- **MTGJSON v5** - Card data source (AtomicCards, Keywords, RelatedCards)
- **Neo4j Community Edition** - Graph database
- **Python 3.9+** - Implementation language
- **pytest** - Testing framework

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Neo4j

**Option A: Neo4j Desktop** (Recommended)
- Download from https://neo4j.com/download/
- Create a new database
- Set password and note the connection details

**Option B: Docker**
```bash
docker run \
    --name neo4j \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/password \
    neo4j:latest
```

### 3. Set Neo4j Password

```bash
export NEO4J_PASSWORD="your_password_here"
```

Or update the password in `main.py`.

## Usage

### Run Complete Pipeline

```bash
python main.py
```

This will:
1. Download MTGJSON data (~60MB)
2. Parse Commander-legal cards (~20,000 cards)
3. Enrich with functional roles and mechanics
4. Load into Neo4j
5. Create relationships
6. Analyze popular commanders
7. Run example queries

### Query Examples

```python
from src.graph.connection import Neo4jConnection
from src.synergy.queries import DeckbuildingQueries

# Connect to Neo4j
conn = Neo4jConnection(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password"
)

# Find synergistic cards for Muldrotha
cards = DeckbuildingQueries.find_synergistic_cards(
    conn,
    commander_name="Muldrotha, the Gravetide",
    max_cmc=4,
    min_strength=0.7,
    limit=50
)

# Find known combos with Dramatic Reversal
combos = DeckbuildingQueries.find_known_combos(
    conn,
    card_name="Dramatic Reversal"
)

# Build deck shell
shell = DeckbuildingQueries.build_deck_shell(
    conn,
    commander_name="Muldrotha, the Gravetide"
)

# Find Goblin token generators in Jund colors
goblins = DeckbuildingQueries.find_token_generators(
    conn,
    token_type="Goblin",
    color_identity=["B", "R", "G"],
    max_cmc=4
)
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_functional_roles.py -v
```

Current test coverage: 21/21 tests passing

## Project Structure

```
mtg/
├── src/
│   ├── data/               # Data acquisition & parsing
│   │   ├── mtgjson_downloader.py
│   │   ├── atomic_cards_parser.py
│   │   └── related_cards_parser.py
│   ├── parsing/            # Text analysis
│   │   ├── functional_roles.py
│   │   ├── mechanics.py
│   │   ├── properties.py
│   │   └── enrichment.py
│   ├── graph/              # Neo4j operations
│   │   ├── connection.py
│   │   └── loaders.py
│   └── synergy/            # Synergy inference
│       ├── inference_engine.py
│       └── queries.py
├── tests/
│   └── unit/               # Unit tests
├── data/
│   └── raw/                # MTGJSON downloads
├── main.py                 # Main pipeline
└── requirements.txt
```

## Graph Schema

### Nodes
- **Card** - Non-commander cards
- **Commander** - Legendary creatures that can be commanders
- **Mechanic** - Keywords and abilities
- **Functional_Role** - Deck roles (Ramp, Draw, Removal, etc.)
- **Token** - Token creatures

### Relationships
- `[:HAS_MECHANIC]` - Card has a mechanic
- `[:FILLS_ROLE]` - Card fills a functional role
- `[:CREATES_TOKEN]` - Card creates a token
- `[:COMBOS_WITH]` - Explicit combo from MTGJSON Spellbook
- `[:COMMONLY_PAIRED_WITH]` - Community pairing from MTGJSON
- `[:SYNERGIZES_WITH_MECHANIC]` - Commander synergizes with mechanic

## Data Sources

- **MTGJSON AtomicCards.json** - Core card data
- **MTGJSON Keywords.json** - Standardized keywords
- **MTGJSON RelatedCards.json** - Combos, tokens, and pairings

Data is downloaded automatically on first run.

## License

This project uses data from MTGJSON (https://mtgjson.com/), which is licensed under CC0.

Magic: The Gathering is © Wizards of the Coast.
