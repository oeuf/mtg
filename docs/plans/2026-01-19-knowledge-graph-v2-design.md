# Knowledge Graph V2 - Design Document

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Enhance the MTG Commander knowledge graph with statistical scoring, validation, popularity data, and a web frontend.

**Features (in priority order):**
1. #5 Validation - Compare recommendations against reference Muldrotha deck (ranking accuracy)
2. #4 ML Features - Neo4j GDS for statistical synergy scoring
3. #3 Meta Analysis - EDHREC rank + precon frequency for popularity
4. #1 Frontend - FastAPI + Next.js with Deck Builder, Analyzer, Explorer, Lookup

**Constraints:**
- MTGJSON-only data sources (no Forge, no external APIs)
- Use Neo4j Graph Data Science (GDS) for ML features
- Commit and push changes incrementally
- Use worktrees and subagents when beneficial

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Next.js Frontend                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐│
│  │  Deck    │ │  Deck    │ │  Graph   │ │    Commander     ││
│  │ Builder  │ │ Analyzer │ │ Explorer │ │     Lookup       ││
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────────┬─────────┘│
└───────┼────────────┼────────────┼────────────────┼──────────┘
        │            │            │                │
        ▼            ▼            ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                         │
│  /api/commanders  /api/cards  /api/decks  /api/graph        │
└───────────────────────────┬─────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Neo4j      │   │  Neo4j GDS   │   │   MTGJSON    │
│   Graph DB   │   │  (ML/Stats)  │   │   Precons    │
└──────────────┘   └──────────────┘   └──────────────┘
```

---

## Phase 1: Foundation (Ontology + Data)

### Task 1.1: Ontology Expansion

**New Node Types:**

1. **Archetype** - Strategy clusters
   ```python
   {
     "name": str,        # "Aristocrats", "Graveyard", "Tokens"
     "description": str,
     "key_mechanics": list[str]
   }
   ```

2. **Subtype** - Creature/land subtypes for tribal
   ```python
   {
     "name": str,        # "Elf", "Zombie", "Island"
     "category": str     # "creature", "land", "artifact"
   }
   ```

**New Relationships:**
- `[:HAS_SUBTYPE]` - Card → Subtype
- `[:BELONGS_TO_ARCHETYPE]` - Card → Archetype
- `[:SIMILAR_TO {score}]` - Card → Card

**New Card Properties:**
```python
{
    "pagerank_score": float,      # From GDS
    "community_id": int,          # From GDS Louvain
    "precon_count": int,          # From precon parsing
    "popularity_score": float,    # Combined score
    "subtypes": list[str]         # Parsed from type_line
}
```

**Files to modify:**
- `src/graph/loaders.py` - Add subtype extraction and loading
- `src/graph/connection.py` - Add new constraints/indexes

**Steps:**
1. Add `extract_subtypes()` function to parse type_line
2. Create Subtype nodes during card loading
3. Create HAS_SUBTYPE relationships
4. Add new constraints for Subtype and Archetype nodes
5. Run tests to verify

**Verification:**
```bash
pytest tests/unit tests/integration -v
```

---

### Task 1.2: Precon Data Download & Parsing

**Goal:** Download MTGJSON deck files and count card appearances.

**Files to create:**
- `src/data/precon_downloader.py` - Download AllDeckFiles
- `src/data/precon_parser.py` - Parse and count appearances

**Steps:**
1. Download `https://mtgjson.com/api/v5/AllDeckFiles.zip`
2. Extract and parse each deck JSON file
3. Count appearances per card across all Commander precons
4. Store as `{card_name: count}` dictionary

**Implementation:**
```python
class PreconParser:
    def parse_all_decks(self, deck_dir: str) -> dict[str, int]:
        """Return {card_name: appearance_count}."""
        counts = {}
        for deck_file in Path(deck_dir).glob("*.json"):
            deck = json.load(open(deck_file))
            if deck.get("type") != "Commander":
                continue
            for card in deck.get("mainBoard", []):
                name = card["name"]
                counts[name] = counts.get(name, 0) + 1
        return counts
```

**Verification:**
```bash
python -c "from src.data.precon_parser import PreconParser; print(len(PreconParser().parse_all_decks('data/decks')))"
```

---

### Task 1.3: Popularity Score Calculation

**Goal:** Combine EDHREC rank with precon frequency.

**Files to create:**
- `src/data/popularity.py` - Calculate combined scores

**Formula:**
```python
def calculate_popularity(edhrec_rank: int, precon_count: int, total_precons: int) -> float:
    # Normalize EDHREC (invert: lower rank = higher score)
    edhrec_score = max(0, 1 - (edhrec_rank / 20000)) if edhrec_rank else 0.5

    # Precon frequency
    precon_score = precon_count / total_precons if total_precons > 0 else 0

    # Weighted combination
    return 0.7 * edhrec_score + 0.3 * precon_score
```

**Steps:**
1. Load precon counts from Task 1.2
2. For each card, calculate popularity_score
3. Update card nodes with new properties

**Verification:**
```cypher
MATCH (c:Card) WHERE c.popularity_score IS NOT NULL RETURN count(c)
```

---

## Phase 2: GDS Scoring (#4 ML Features)

### Task 2.1: Graph Projection for GDS

**Files to create:**
- `src/graph/gds_scoring.py` - GDS operations

**Steps:**
1. Create in-memory graph projection
2. Include Card, Commander, Mechanic, Functional_Role nodes
3. Include HAS_MECHANIC, FILLS_ROLE, COMBOS_WITH relationships

**Implementation:**
```python
def create_graph_projection(conn: Neo4jConnection):
    query = """
    CALL gds.graph.project(
        'synergy-graph',
        ['Card', 'Commander', 'Mechanic', 'Functional_Role'],
        {
            HAS_MECHANIC: {orientation: 'UNDIRECTED'},
            FILLS_ROLE: {orientation: 'UNDIRECTED'},
            COMBOS_WITH: {orientation: 'UNDIRECTED'}
        }
    )
    """
    conn.execute_query(query)
```

**Verification:**
```cypher
CALL gds.graph.list() YIELD graphName RETURN graphName
```

---

### Task 2.2: PageRank Computation

**Goal:** Compute global importance score for each card.

**Steps:**
1. Run PageRank on projected graph
2. Write scores back to card nodes

**Implementation:**
```python
def compute_pagerank(conn: Neo4jConnection):
    query = """
    CALL gds.pageRank.write('synergy-graph', {
        writeProperty: 'pagerank_score',
        maxIterations: 20,
        dampingFactor: 0.85
    })
    YIELD nodePropertiesWritten
    RETURN nodePropertiesWritten
    """
    return conn.execute_query(query)
```

**Verification:**
```cypher
MATCH (c:Card) RETURN c.name, c.pagerank_score ORDER BY c.pagerank_score DESC LIMIT 10
```

---

### Task 2.3: Community Detection (Louvain)

**Goal:** Find archetype clusters.

**Steps:**
1. Run Louvain on projected graph
2. Write community IDs to card nodes
3. Later: manually name top communities as Archetypes

**Implementation:**
```python
def detect_communities(conn: Neo4jConnection):
    query = """
    CALL gds.louvain.write('synergy-graph', {
        writeProperty: 'community_id'
    })
    YIELD communityCount, modularity
    RETURN communityCount, modularity
    """
    return conn.execute_query(query)
```

**Verification:**
```cypher
MATCH (c:Card) RETURN c.community_id, count(*) AS size ORDER BY size DESC LIMIT 10
```

---

### Task 2.4: Node Similarity

**Goal:** Find similar cards and store as relationships.

**Steps:**
1. Run node similarity on projected graph
2. Create SIMILAR_TO relationships for top matches

**Implementation:**
```python
def compute_similarity(conn: Neo4jConnection, min_similarity: float = 0.5):
    query = """
    CALL gds.nodeSimilarity.write('synergy-graph', {
        writeRelationshipType: 'SIMILAR_TO',
        writeProperty: 'score',
        similarityCutoff: $min_similarity,
        topK: 10
    })
    YIELD relationshipsWritten
    RETURN relationshipsWritten
    """
    return conn.execute_query(query, {"min_similarity": min_similarity})
```

**Verification:**
```cypher
MATCH (c1:Card)-[s:SIMILAR_TO]->(c2:Card) RETURN count(s)
```

---

### Task 2.5: Enhanced Recommendation Query

**Goal:** Update queries to use GDS scores.

**Files to modify:**
- `src/synergy/queries.py` - Update find_synergistic_cards

**New query logic:**
```python
def find_synergistic_cards(conn, commander_name, ...):
    query = """
    MATCH (cmd:Commander {name: $commander_name})
    MATCH (card:Card)
    WHERE card.cmc <= $max_cmc
      AND ALL(c IN card.color_identity WHERE c IN cmd.color_identity)

    // Mechanic synergy
    OPTIONAL MATCH (cmd)-[s:SYNERGIZES_WITH_MECHANIC]->(m:Mechanic)<-[:HAS_MECHANIC]-(card)

    // Same community bonus
    WITH card, cmd, max(coalesce(s.strength, 0)) AS synergy_score

    // Combined score: synergy + pagerank + popularity + community match
    WITH card,
         synergy_score,
         coalesce(card.pagerank_score, 0) AS pagerank,
         coalesce(card.popularity_score, 0) AS popularity,
         CASE WHEN card.community_id = cmd.community_id THEN 0.2 ELSE 0 END AS community_bonus

    WITH card,
         (synergy_score * 0.4 + pagerank * 0.2 + popularity * 0.2 + community_bonus) AS final_score
    WHERE final_score > 0

    RETURN card.name, final_score
    ORDER BY final_score DESC
    LIMIT $limit
    """
```

**Verification:**
```bash
pytest tests/integration -v -k "synergistic"
```

---

## Phase 3: Validation (#5)

### Task 3.1: Reference Deck Loader

**Files to create:**
- `src/validation/reference_deck.py`

**Implementation:**
```python
def load_reference_deck(filepath: str) -> set[str]:
    """Load card names from Moxfield-format decklist."""
    cards = set()
    with open(filepath) as f:
        for line in f:
            # Format: "1\tCard Name" or "1 Card Name"
            match = re.match(r'^\d+\s+(.+)$', line.strip())
            if match:
                cards.add(match.group(1))
    return cards
```

**Verification:**
```python
cards = load_reference_deck("Muldrotha/DECKLIST.md")
assert len(cards) == 99  # Commander deck minus commander
```

---

### Task 3.2: MRR Metric Calculation

**Files to create:**
- `src/validation/metrics.py`

**Implementation:**
```python
def mean_reciprocal_rank(reference: set[str], ranked_recommendations: list[str]) -> float:
    """Calculate MRR for reference cards in ranked list."""
    reciprocal_ranks = []
    for card in reference:
        if card in ranked_recommendations:
            rank = ranked_recommendations.index(card) + 1
            reciprocal_ranks.append(1.0 / rank)
        # Cards not found contribute 0

    if not reciprocal_ranks:
        return 0.0
    return sum(reciprocal_ranks) / len(reference)

def overlap_at_k(reference: set[str], ranked: list[str], k: int) -> float:
    """What % of reference cards appear in top k recommendations."""
    top_k = set(ranked[:k])
    overlap = reference & top_k
    return len(overlap) / len(reference)
```

---

### Task 3.3: Validation CLI

**Files to create:**
- `src/validation/validate_deck.py`

**Usage:**
```bash
python -m src.validation.validate_deck \
  --commander "Muldrotha, the Gravetide" \
  --reference Muldrotha/DECKLIST.md
```

**Output:**
```
Reference deck: 99 cards
Found in top 100: 45 cards (45%)
Found in top 200: 72 cards (73%)
Mean Reciprocal Rank: 0.42

Missing high-synergy cards:
- Animate Dead (rank: 312)
- Entomb (rank: 445)
```

---

### Task 3.4: Iterate on Scoring

**Goal:** Adjust weights until MRR improves.

**Steps:**
1. Run validation, note baseline MRR
2. Adjust query weights (synergy, pagerank, popularity, community)
3. Re-run validation
4. Repeat until MRR > 0.5 or diminishing returns

---

## Phase 4: API Layer

### Task 4.1: FastAPI Setup

**Files to create:**
- `api/main.py` - FastAPI app
- `api/schemas.py` - Pydantic models
- `api/routers/__init__.py`

**Steps:**
1. Create FastAPI app with CORS
2. Connect to Neo4j on startup
3. Add health check endpoint

---

### Task 4.2: Commander/Card Endpoints

**Files to create:**
- `api/routers/commanders.py`
- `api/routers/cards.py`

**Endpoints:**
```
GET  /api/commanders                        # List all commanders
GET  /api/commanders/{name}                 # Commander details
GET  /api/commanders/{name}/recommendations # Ranked cards
GET  /api/cards/{name}                      # Card details
GET  /api/cards/search?q=...                # Card search
```

---

### Task 4.3: Deck CRUD Endpoints

**Files to create:**
- `api/routers/decks.py`

**Endpoints:**
```
POST /api/decks                    # Create deck (in-memory or DB)
GET  /api/decks/{id}               # Get deck with analysis
PUT  /api/decks/{id}/cards         # Add/remove cards
POST /api/analyze                  # Analyze pasted decklist
```

---

### Task 4.4: Graph Explorer Endpoints

**Files to create:**
- `api/routers/graph.py`

**Endpoints:**
```
GET /api/graph/card/{name}         # Card connections
GET /api/graph/community/{id}      # Cards in archetype
GET /api/graph/similar/{name}      # Similar cards
```

---

## Phase 5: Frontend (#1)

### Task 5.1: Next.js Project Setup

**Steps:**
1. `npx create-next-app@latest frontend --typescript --tailwind --app`
2. Install dependencies: `axios`, `react-query`, `d3` or `vis-network`
3. Set up API client pointing to FastAPI

---

### Task 5.2: Deck Builder Page (`/build`)

**Features:**
- Commander selector dropdown
- Card search with filters (CMC, role, color)
- Drag cards to deck zones
- Live synergy score as cards added
- Role coverage meter (8x8 visualization)

---

### Task 5.3: Deck Analyzer Page (`/analyze`)

**Features:**
- Textarea to paste decklist
- Parse and analyze on submit
- Show: role gaps, missing synergies, suggested swaps
- Compare to optimal recommendations

---

### Task 5.4: Graph Explorer Page (`/explore`)

**Features:**
- Force-directed graph (D3.js or vis-network)
- Click card → show connections
- Filter by archetype/community
- Hover for card details

---

### Task 5.5: Commander Lookup Page (`/commander/[name]`)

**Features:**
- Card recommendations by role
- Known combos section
- Synergy explanations
- Link to start deck builder with this commander

---

## Project Structure (Final)

```
mtg/
├── api/                          # FastAPI backend
│   ├── main.py
│   ├── schemas.py
│   └── routers/
│       ├── commanders.py
│       ├── cards.py
│       ├── decks.py
│       └── graph.py
├── frontend/                     # Next.js
│   ├── app/
│   │   ├── build/page.tsx
│   │   ├── analyze/page.tsx
│   │   ├── explore/page.tsx
│   │   └── commander/[name]/page.tsx
│   └── components/
├── src/                          # Existing + new Python modules
│   ├── data/
│   │   ├── precon_downloader.py  # NEW
│   │   ├── precon_parser.py      # NEW
│   │   └── popularity.py         # NEW
│   ├── graph/
│   │   ├── gds_scoring.py        # NEW
│   │   └── similarity.py         # NEW
│   ├── validation/               # NEW
│   │   ├── reference_deck.py
│   │   ├── metrics.py
│   │   └── validate_deck.py
│   └── synergy/
│       └── queries.py            # MODIFIED
├── tests/
├── docs/plans/
└── Muldrotha/DECKLIST.md         # Reference deck
```

---

## Verification Checklist

After each phase:

- [ ] All tests pass: `pytest tests/ -v`
- [ ] Changes committed and pushed
- [ ] Validation MRR tracked (Phase 3+)

Final verification:
- [ ] MRR > 0.4 on Muldrotha reference deck
- [ ] API endpoints respond correctly
- [ ] Frontend pages render and function
- [ ] GDS algorithms produce reasonable scores
