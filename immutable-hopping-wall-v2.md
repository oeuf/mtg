# MTG Commander Web Application - Implementation Plan

## Context

**Why we're building this:** Expand the existing MTG Commander Knowledge Graph from a data pipeline into a full-stack web application that makes intelligent deck recommendations accessible to Commander players.

---

## Execution Methodology (MANDATORY for ALL Milestones)

### 1. Agent Teams (ALWAYS)

Every milestone MUST be executed using Agent Teams. No exceptions.

**Workflow:**
```
TeamCreate → TaskCreate (with dependencies) → Task (spawn agents with team_name + run_in_background + mode: bypassPermissions) → Monitor → Verify → SendMessage (shutdown) → TeamDelete
```

**Team structure per milestone:**
- **Team Lead (you):** Creates team, tasks, dependencies. Spawns agents. Monitors progress. Runs final verification. Shuts down agents.
- **Implementation agents (Sonnet 4.5 or general-purpose):** Each agent gets ONE task with clear file boundaries. Agents MUST NOT modify files outside their assignment.
- **Code reviewer agent:** After all implementation agents finish, spawn a `feature-dev:code-reviewer` agent to review the full diff before committing.

**Rules:**
- Set `mode: bypassPermissions` on all spawned agents so they can run without human approval
- Set `run_in_background: true` on all spawned agents
- Always set task dependencies with `addBlockedBy` to prevent race conditions
- Give agents EXPLICIT lists of files they may create/modify and files they must NOT touch
- Parallelize tasks that have no file overlap
- Wait for blocked tasks to unblock before spawning their agents

### 2. Test-Driven Development (ALWAYS)

Every feature MUST follow TDD. No production code without a failing test first.

**For each task given to an agent:**
1. Agent writes tests FIRST
2. Agent runs tests to verify they FAIL
3. Agent writes minimal code to make tests pass
4. Agent runs tests to verify they PASS
5. Agent runs `pnpm build` (frontend) or `pytest` (backend) to verify nothing else broke

**Test requirements:**
- Backend: pytest with mocked Neo4j session
- Frontend: Vitest + @testing-library/react
- Every new component, hook, service, or utility MUST have tests
- Tests run via: `cd frontend && pnpm test` or `cd /Users/ng/cc-projects/mtg && PYTHONPATH=backend:. pytest backend/tests/ -v`

**Include in every agent prompt:**
```
Follow TDD:
1. Write tests first in [test file path]
2. Run tests to verify they fail: [test command]
3. Implement the minimal code to pass
4. Run tests to verify all pass: [test command]
5. Run full suite to verify nothing broke: [full test command]
```

### 3. Code Review (ALWAYS)

After all implementation agents complete and before committing:

1. **Run full test suites** (backend + frontend) to verify everything passes
2. **Spawn a code reviewer agent** using `feature-dev:code-reviewer` subagent_type to review all changes
3. **Fix any issues** the reviewer identifies
4. **Run verification again** after fixes
5. **Only then** commit

**Code reviewer agent prompt template:**
```
Review all uncommitted changes in /Users/ng/cc-projects/mtg for:
- Bugs and logic errors
- TypeScript/Python type safety
- Missing error handling
- Test coverage gaps
- Adherence to project conventions (Tailwind v4, Biome, pnpm, pytest)
Report only HIGH confidence issues.
```

### 4. Verification Before Completion (ALWAYS)

Before claiming any milestone is done:
- Run `cd /Users/ng/cc-projects/mtg && PYTHONPATH=backend:. pytest backend/tests/ -v` → all pass
- Run `cd /Users/ng/cc-projects/mtg/frontend && pnpm test` → all pass
- Run `cd /Users/ng/cc-projects/mtg/frontend && pnpm build` → succeeds
- Count total tests and report: "X backend + Y frontend = Z total tests passing"

---

## Answers to Stories.md Questions

### 1. What types of algorithms for card similarity? (Pros and cons)

**Current Implementation (Already in graph):**
- **FastRP Embeddings (128-dim)** - Graph-based neural embeddings
  - ✅ Pros: Captures structural similarity, works with 2.76M relationships, already computed
  - ❌ Cons: Computationally expensive to recompute, black-box features

**Recommendation: Use existing FastRP + kNN for v1.0**
- Already has 2.76M EMBEDDING_SIMILAR relationships (topK=100)
- Performance tested and validated
- No additional computation needed

**Future Enhancements (Phase 2):**
- **Content-based similarity:** TF-IDF on oracle text + cosine similarity
  - ✅ Pros: Interpretable, finds text pattern matches
  - ❌ Cons: Misses structural synergies, computationally cheaper than embeddings
- **Hybrid approach:** Combine FastRP (structural) + TF-IDF (textual) with weighted ensemble
  - ✅ Pros: Best of both worlds
  - ❌ Cons: More complex, requires tuning weights

### 2. What algorithms for recommendations? (Pros and cons)

**Current Multi-Algorithm Approach (Already implemented):**

**A. Mechanic-Based Synergy (Rule-based)**
- Algorithm: Traverse Commander → HAS_MECHANIC → Mechanic → HAS_MECHANIC ← Card
- ✅ Pros: Interpretable, fast queries, matches player mental models
- ❌ Cons: Misses implicit synergies, limited by mechanic extraction quality
- **Use case:** Primary recommendations in deck builder

**B. Embedding Similarity (ML-based)**
- Algorithm: kNN on FastRP embeddings with topK=100
- ✅ Pros: Captures latent patterns, discovers unexpected synergies
- ❌ Cons: Less interpretable, one-time computation cost
- **Use case:** "Similar cards" and "You might also like" sections

**C. Role Compatibility (7-dimensional scoring)**
- Algorithm: Multi-dimensional weighted ensemble (mechanic_overlap 20%, role_compatibility 25%, theme 20%, zone 15%, phase 10%, color 5%, type 5%)
- ✅ Pros: Granular control, highly accurate for known patterns
- ❌ Cons: Requires manual weight tuning, complex to explain
- **Use case:** Advanced synergy analysis and combo detection

**D. Community-Boosted Synergies**
- Algorithm: Leiden community detection (21,107 communities) → 1.2x boost for intra-community cards
- ✅ Pros: Discovers archetype clusters, improves recommendation diversity
- ❌ Cons: Depends on community quality (modularity=0.630)
- **Use case:** Archetype-aware recommendations

**Recommendation for v1.0: Use all four in ensemble**
- Primary: Mechanic-based (fast, interpretable)
- Secondary: Embedding similarity (discovery)
- Advanced: 7-dim scoring (combo finder)
- Context: Community boost (archetype cohesion)

**Future: Add collaborative filtering (Phase 2)**
- "Decks that include Muldrotha also include..."
- Requires user deck dataset (collect from Moxfield/EDHREC or user submissions)

### 3. Do we also need Postgres?

**Answer: Not for v1.0 MVP**

**Neo4j handles:**
- ✅ Card data (27,619 cards with properties)
- ✅ Relationships (2.76M similarities, 861K synergies)
- ✅ Graph queries (synergy traversals, recommendations)

**When to add PostgreSQL (Phase 2):**
- User accounts (username, email, password_hash)
- Deck metadata (deck_name, created_at, updated_at, description)
- User collections (user_id, card_name, quantity)
- Activity logs (search history, deck views)

**Hybrid Architecture (Future):**
```
PostgreSQL: User data, decks, collections (relational)
Neo4j: Card graph, synergies, recommendations (graph)
Redis: Query caching, session storage (cache)
```

**For MVP: Use localStorage for collections (client-side only)**
- No backend storage needed initially
- Add PostgreSQL when adding user accounts

### 4. Roadmap Prioritization

**Answered in main plan:** 7 milestones over 8 weeks (see "Implementation Roadmap" section)

**Priority order rationale:**
1. **Backend API first** - Foundation for all features
2. **Deck builder** - Highest user value (addresses "How do I build a deck?")
3. **Search & filters** - Essential discovery tool
4. **Similarity & synergy** - Unique differentiator (ML-powered insights)
5. **Collection management** - Nice-to-have for v1.0
6. **Polish & production** - Deploy-ready quality

### 5. Brainstorm Other Features or Design of Features

**Additional features to consider (beyond Stories.md):**

**High Priority (v1.1):**
- **Deck validation:** Check color identity violations, illegal cards, commander legality
- **Mana curve optimizer:** Suggest swaps to improve curve distribution
- **Budget mode:** Filter recommendations by card price (integrate TCGPlayer/Scryfall API)
- **Deck exporter:** Export to Moxfield, Archidekt, MTGO, Arena formats
- **Sample hand drawer:** Mulligan simulator with opening hand stats

**Medium Priority (v2.0):**
- **Deck comparator:** Upload two decklists, show differences and upgrades
- **Meta analysis:** "This deck is strong against X archetype, weak against Y"
- **Alternate commander suggestions:** "Similar commanders for this strategy"
- **Proxy generator:** Print-friendly card proxies for playtesting
- **Deck tags & notes:** Add custom notes to cards in your deck

**Low Priority (Future):**
- **Visual deck builder:** Drag-and-drop interface with card images
- **Deck goldfishing:** Simulate games against AI (complex)
- **Trading system:** Match owned cards with wanted cards (requires user base)
- **Tournament mode:** Track match results, sideboarding notes
- **Deck sharing social features:** Comments, upvotes, featured decks

**Design Principles (from Stories.md goals):**
- **Elegant:** Stripe-inspired minimalism (plenty of whitespace, clear hierarchy)
- **Modern:** 2026 web standards (CSS Grid, dark mode support, glassmorphism)
- **Intuitive:** User completes task without instructions (progressive disclosure)
- **Lightning fast:** < 2s page loads, < 100ms filter updates (use Vite HMR, React Query caching)
- **Modular:** Component-based architecture (reusable Card, Filter, DeckSlot components)

### 6. What Agent Team and Model for Each Team Member?

**All milestones follow the mandatory Execution Methodology defined above (Agent Teams + TDD + Code Review).**

**Agent types per task:**
- **Implementation agents:** `general-purpose` subagent_type (has full tool access: Read, Write, Edit, Bash, Glob, Grep)
- **Code reviewer agent:** `feature-dev:code-reviewer` subagent_type (read-only, reports issues)
- **Team lead (you):** Creates team, spawns agents, monitors, verifies, commits

**Model selection:**
- **Team lead:** Opus 4.6 (architecture decisions, final verification)
- **Implementation agents:** Sonnet 4.5 via `general-purpose` (fast, accurate for code)
- **Code reviewer:** Sonnet 4.5 via `feature-dev:code-reviewer` (thorough analysis)

**Parallelization strategy:**
- Group tasks by file boundaries (no two agents touch the same file)
- Use `addBlockedBy` for sequential dependencies
- Spawn independent tasks in the same message (parallel launch)
- Wait for wave to complete before starting next wave

**Per-milestone workflow:**
```
1. TeamCreate (name: milestone-N-description)
2. TaskCreate × N tasks (with descriptions, TDD instructions, file boundaries)
3. TaskUpdate to set addBlockedBy dependencies
4. Wave 1: Task × M agents (unblocked tasks, run_in_background, bypassPermissions)
5. Monitor: check file creation, run tests periodically
6. Wave 2: Task × K agents (newly unblocked tasks)
7. ... repeat waves until all tasks done ...
8. Run full test suite (backend + frontend)
9. Task: spawn code reviewer agent on full diff
10. Fix any issues reviewer found
11. Run full test suite again
12. Commit
13. SendMessage shutdown to all agents
14. TeamDelete
```

---

**Current state:**
- Production-ready Neo4j knowledge graph with 27,619 cards, 658 mechanics, 2.76M ML-powered similarity relationships
- Complete Python data pipeline (main.py) with 7-dimensional synergy scoring
- 13+ API-ready query functions in `DeckbuildingQueries` class
- No user-facing interface currently

**What we're building:**
- Modern web application with FastAPI backend + React frontend
- Stripe-inspired elegant UI with lightning-fast, responsive design
- Core features: deck builder, card search/filters, similarity/synergy finder, collection management
- Target: Production-ready MVP in 1-2 months

**Architecture decisions:**
- **Monorepo** structure (backend + frontend + shared types)
- **Keep data pipeline separate** (main.py remains standalone; API reads from populated Neo4j)
- **Tech stack:** FastAPI + React + TypeScript + Vite + Tailwind + Neo4j
- **Tooling:** uv (Python), pnpm (Node), Biome (linting), Vitest + Playwright (testing)

---

## Implementation Roadmap

### Milestone 1: Foundation & Backend API (Week 1-2)

**Goal:** Production-ready FastAPI backend with core endpoints serving data from existing Neo4j graph.

**Deliverables:**

#### 1.1 Project Structure Setup
- Create monorepo structure:
  ```
  /backend          # FastAPI application
  /frontend         # React + TypeScript + Vite
  /shared           # Shared types/schemas
  docker-compose.yml # Updated to include backend service
  ```
- Initialize backend with uv: `uv pip install fastapi uvicorn neo4j pydantic python-dotenv`
- Setup backend structure:
  ```
  backend/
  ├── app/
  │   ├── main.py              # FastAPI app initialization
  │   ├── config.py            # Settings (Neo4j URI, password from env)
  │   ├── dependencies.py      # Neo4j connection dependency injection
  │   ├── models/              # Pydantic response models
  │   │   ├── card.py
  │   │   ├── commander.py
  │   │   ├── synergy.py
  │   │   └── deck.py
  │   ├── routers/             # API endpoints
  │   │   ├── commanders.py
  │   │   ├── cards.py
  │   │   ├── decks.py
  │   │   ├── graph.py
  │   │   └── collections.py
  │   └── services/            # Business logic wrapping existing functions
  │       ├── query_service.py      # Wraps DeckbuildingQueries
  │       ├── synergy_service.py    # Wraps CardSynergyEngine
  │       └── recommendation_service.py
  └── tests/
  ```

#### 1.2 Pydantic Models
Create models matching existing data structures from exploration:

**File:** `backend/app/models/card.py`
```python
from pydantic import BaseModel, Field
from typing import List, Optional

class Card(BaseModel):
    name: str
    mana_cost: str
    cmc: int
    type_line: str
    oracle_text: str
    color_identity: List[str]
    colors: List[str]
    keywords: List[str]
    is_legendary: bool
    edhrec_rank: Optional[int] = None
    functional_categories: List[str] = Field(default_factory=list)
    mechanics: List[str] = Field(default_factory=list)
    themes: List[str] = Field(default_factory=list)
    archetype: Optional[str] = None
    popularity_score: float = 0.0

class CardSearchFilters(BaseModel):
    colors: Optional[List[str]] = None
    color_identity: Optional[List[str]] = None
    types: Optional[List[str]] = None
    cmc_min: Optional[int] = None
    cmc_max: Optional[int] = None
    rarity: Optional[List[str]] = None
    mechanics: Optional[List[str]] = None
    roles: Optional[List[str]] = None
    text_search: Optional[str] = None
```

**File:** `backend/app/models/commander.py`
**File:** `backend/app/models/synergy.py` (for similarity/synergy responses)
**File:** `backend/app/models/deck.py`

#### 1.3 Neo4j Connection Setup
**File:** `backend/app/dependencies.py`
```python
from contextlib import asynccontextmanager
from neo4j import GraphDatabase
from app.config import settings

# Initialize driver at startup (connection pooling)
driver = None

@asynccontextmanager
async def lifespan(app):
    global driver
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password)
    )
    yield
    driver.close()

def get_neo4j_session():
    with driver.session() as session:
        yield session
```

**File:** `backend/app/config.py`
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"

    class Config:
        env_file = ".env"

settings = Settings()
```

#### 1.4 Core API Endpoints

**Priority endpoints based on existing functions:**

**File:** `backend/app/routers/commanders.py`
- `GET /api/commanders` - List all commanders (with pagination)
- `GET /api/commanders/{name}` - Get commander details
- `GET /api/commanders/{name}/synergies` - Wraps `DeckbuildingQueries.find_synergistic_cards()`
- `GET /api/commanders/{name}/recommendations` - Wraps `get_embedding_recommendations()`

**File:** `backend/app/routers/cards.py`
- `GET /api/cards` - Search/list cards with filters (wraps custom Cypher query)
- `GET /api/cards/{name}` - Get card details
- `GET /api/cards/{name}/similar` - Wraps `find_similar_cards()`
- `GET /api/cards/{name}/synergies` - Cards that synergize with this card
- `GET /api/cards/by-role/{role}` - Wraps `find_cards_by_role()`

**File:** `backend/app/routers/decks.py`
- `POST /api/decks/build-shell` - Wraps `build_deck_shell()` (8x8 method)
- `POST /api/decks/analyze` - Analyze deck composition (role distribution, mana curve)

**File:** `backend/app/routers/graph.py`
- `GET /api/graph/stats` - Graph statistics (node counts, relationship counts)
- `GET /api/mechanics` - List all 658 mechanics
- `GET /api/themes` - List all 19 themes with descriptions
- `GET /api/roles` - List all 10+ functional roles

**File:** `backend/app/routers/collections.py`
- `POST /api/collections` - Create user collection
- `GET /api/collections/{id}` - Get collection
- `PATCH /api/collections/{id}/cards` - Add/remove cards from collection
- `GET /api/collections/{id}/stats` - Collection statistics

#### 1.5 Service Layer
Wrap existing functions from `src/synergy/queries.py`, `src/validation/recommendations.py`:

**File:** `backend/app/services/query_service.py`
```python
from typing import List, Dict, Any
from neo4j import Session

class QueryService:
    @staticmethod
    def find_synergistic_cards(
        session: Session,
        commander_name: str,
        max_cmc: int = 4,
        min_strength: float = 0.7,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        # Reuse Cypher query from DeckbuildingQueries.find_synergistic_cards()
        # Add error handling, convert to dict
        pass
```

Similar wrappers for all 13+ existing query functions identified in exploration.

#### 1.6 Testing & Documentation
- Add pytest for backend API tests
- Configure FastAPI auto-generated OpenAPI docs (accessible at `/docs`)
- Add example requests/responses in docstrings
- Test all endpoints with realistic data from Neo4j

**Verification:**
```bash
# Start backend
cd backend && uvicorn app.main:app --reload

# Visit http://localhost:8000/docs (Swagger UI)
# Test endpoints:
curl http://localhost:8000/api/commanders
curl http://localhost:8000/api/commanders/Muldrotha,%20the%20Gravetide/synergies
curl "http://localhost:8000/api/cards?colors=B,G,U&cmc_max=4"
```

---

### Milestone 2: Frontend Foundation (Week 2-3)

**Goal:** React + TypeScript + Vite application with Tailwind CSS, core routing, and API integration.

**Deliverables:**

#### 2.1 Frontend Initialization
```bash
# Initialize with Vite
npm create vite@latest frontend -- --template react-ts
cd frontend
pnpm install
pnpm add -D tailwindcss postcss autoprefixer @biomejs/biome
pnpm add react-router-dom @tanstack/react-query axios
npx tailwindcss init -p
```

#### 2.2 Project Structure
```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── ui/              # Base components (Button, Card, Input)
│   │   ├── cards/           # Card display components
│   │   └── deck/            # Deck builder components
│   ├── features/            # Feature-based modules
│   │   ├── commanders/
│   │   ├── deck-builder/
│   │   ├── card-search/
│   │   └── collection/
│   ├── hooks/               # Custom React hooks
│   ├── services/            # API clients
│   │   └── api.ts           # Axios instance + endpoints
│   ├── types/               # TypeScript types (generated from backend)
│   ├── utils/               # Utility functions
│   ├── App.tsx
│   └── main.tsx
├── public/
├── tailwind.config.js
├── biome.json               # Biome config (linting + formatting)
└── vite.config.ts
```

#### 2.3 Design System Setup
**File:** `tailwind.config.js`
```js
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // MTG mana colors + brand colors
        mana: {
          white: '#F0F2C0',
          blue: '#0E68AB',
          black: '#150B00',
          red: '#D3202A',
          green: '#00733E',
        },
        brand: {
          // Your brand palette (inspired by Stripe/Claude)
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      }
    }
  }
}
```

**Create base component library:**
- `Button.tsx` - Primary, secondary, ghost variants
- `Card.tsx` - Container component
- `Input.tsx` - Text input with validation
- `Select.tsx` - Dropdown with multi-select support
- `Checkbox.tsx` - For filter checkboxes
- `Badge.tsx` - For mana symbols, card types

#### 2.4 API Client Setup
**File:** `frontend/src/services/api.ts`
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Endpoint functions
export const commandersAPI = {
  list: () => api.get('/api/commanders'),
  get: (name: string) => api.get(`/api/commanders/${name}`),
  getSynergies: (name: string, params?: any) =>
    api.get(`/api/commanders/${name}/synergies`, { params }),
};

export const cardsAPI = {
  search: (filters: CardSearchFilters) =>
    api.get('/api/cards', { params: filters }),
  get: (name: string) => api.get(`/api/cards/${name}`),
  getSimilar: (name: string) => api.get(`/api/cards/${name}/similar`),
};

// React Query integration
export default api;
```

#### 2.5 Routing Setup
**File:** `frontend/src/App.tsx`
```typescript
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Pages
import HomePage from './features/home/HomePage';
import CommanderSelectPage from './features/commanders/CommanderSelectPage';
import DeckBuilderPage from './features/deck-builder/DeckBuilderPage';
import CardSearchPage from './features/card-search/CardSearchPage';
import CollectionPage from './features/collection/CollectionPage';

const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/commanders" element={<CommanderSelectPage />} />
          <Route path="/deck-builder/:commander" element={<DeckBuilderPage />} />
          <Route path="/cards" element={<CardSearchPage />} />
          <Route path="/collection" element={<CollectionPage />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
```

#### 2.6 Shared Types
**Generate TypeScript types from Pydantic models:**
- Option 1: Use `pydantic2ts` to auto-generate types
- Option 2: Manually mirror Pydantic models in `frontend/src/types/`

**File:** `frontend/src/types/card.ts`
```typescript
export interface Card {
  name: string;
  mana_cost: string;
  cmc: number;
  type_line: string;
  oracle_text: string;
  color_identity: string[];
  colors: string[];
  keywords: string[];
  is_legendary: boolean;
  edhrec_rank?: number;
  functional_categories: string[];
  mechanics: string[];
  themes: string[];
  archetype?: string;
  popularity_score: number;
}

export interface CardSearchFilters {
  colors?: string[];
  color_identity?: string[];
  types?: string[];
  cmc_min?: number;
  cmc_max?: number;
  rarity?: string[];
  mechanics?: string[];
  roles?: string[];
  text_search?: string;
}
```

**Verification:**
```bash
# Start frontend dev server
pnpm dev

# Visit http://localhost:5173
# Check console for API calls
# Verify Tailwind styles load
```

---

### Milestone 3: Core Features - Deck Builder (Week 3-4)

> **Execution:** Follow mandatory Execution Methodology above (Agent Teams + TDD + Code Review).

**Goal:** Working deck builder with commander selection, card recommendations, and deck organization.

**Deliverables:**

#### 3.1 Commander Selection Page
**File:** `frontend/src/features/commanders/CommanderSelectPage.tsx`

**Features:**
- Search bar with autocomplete
- Grid display of commanders with:
  - Card image
  - Name + mana cost
  - Color identity indicators
  - Click to select
- Filters: colors, power level (via EDHREC rank)

**API Integration:**
- Use `@tanstack/react-query` for `commandersAPI.list()`
- Implement client-side filtering for responsiveness
- Add loading states and error handling

#### 3.2 Deck Builder Page
**File:** `frontend/src/features/deck-builder/DeckBuilderPage.tsx`

**Layout (inspired by Moxfield/Archidekt):**
```
┌──────────────────────────────────────────┐
│ Commander: Muldrotha                     │
│ [Export] [Save] [Analyze]                │
├──────────────────┬───────────────────────┤
│ DECK (99/99)     │ RECOMMENDATIONS       │
│                  │                       │
│ Creatures (25)   │ Top Synergies:        │
│ [card] [card]... │ [card] [card]...      │
│                  │                       │
│ Instants (10)    │ By Role:              │
│ [card] [card]... │ [Ramp] [Draw]...      │
│                  │                       │
│ Sorceries (15)   │ Similar Cards:        │
│ [card] [card]... │ [card] [card]...      │
│                  │                       │
│ [other types...] │ [Filters ▼]           │
└──────────────────┴───────────────────────┘
```

**Features:**
- Auto-generate initial shell via `POST /api/decks/build-shell`
- Organize cards by type (Creatures, Instants, Sorceries, Artifacts, Enchantments, Planeswalkers, Lands)
- Drag-and-drop to add/remove cards
- Recommendations panel:
  - Top synergies tab (uses `/api/commanders/{name}/synergies`)
  - By role tab (ramp, draw, removal)
  - Similar cards tab
- Mana curve visualization (chart showing CMC distribution)
- Deck statistics: avg CMC, color breakdown, role distribution

**Components:**
- `DeckList.tsx` - Organized by type
- `CardRow.tsx` - Single card in deck list
- `RecommendationsPanel.tsx` - Sidebar with tabs
- `ManaCurve.tsx` - Chart component (use `recharts` or similar)
- `DeckStats.tsx` - Statistics display

#### 3.3 State Management
**File:** `frontend/src/features/deck-builder/useDeckBuilder.ts`

```typescript
import { create } from 'zustand';
import { Card } from '@/types/card';

interface DeckBuilderState {
  commander: Card | null;
  deck: Card[];
  setCommander: (commander: Card) => void;
  addCard: (card: Card) => void;
  removeCard: (cardName: string) => void;
  clearDeck: () => void;
  deckByType: () => Record<string, Card[]>;
}

export const useDeckBuilder = create<DeckBuilderState>((set, get) => ({
  commander: null,
  deck: [],
  setCommander: (commander) => set({ commander }),
  addCard: (card) => set((state) => ({
    deck: [...state.deck, card]
  })),
  removeCard: (cardName) => set((state) => ({
    deck: state.deck.filter(c => c.name !== cardName)
  })),
  clearDeck: () => set({ deck: [] }),
  deckByType: () => {
    const { deck } = get();
    return deck.reduce((acc, card) => {
      const type = extractPrimaryType(card.type_line);
      if (!acc[type]) acc[type] = [];
      acc[type].push(card);
      return acc;
    }, {} as Record<string, Card[]>);
  },
}));
```

**Verification:**
```bash
# Test deck builder workflow:
1. Select commander (e.g., Muldrotha)
2. Verify initial shell loads (37 cards via build-shell endpoint)
3. Add cards from recommendations
4. Remove cards from deck
5. Check deck organized by type
6. Verify mana curve updates
7. Test role distribution stats
```

---

### Milestone 4: Advanced Search & Filters (Week 4-5)

> **Execution:** Follow mandatory Execution Methodology above (Agent Teams + TDD + Code Review).

**Goal:** Comprehensive card search with all filters from Stories.md requirements.

**Deliverables:**

#### 4.1 Card Search Page
**File:** `frontend/src/features/card-search/CardSearchPage.tsx`

**Layout:**
```
┌────────────────────────────────────────────┐
│ [Search: Enter card name or text...]      │
├──────────┬─────────────────────────────────┤
│ FILTERS  │ RESULTS (Showing 1-20 of 1,243) │
│          │                                 │
│ □ Type   │ ┌──────┬──────┬──────┬──────┐  │
│ □ Crea.. │ │ Card │ Card │ Card │ Card │  │
│ □ Inst.. │ └──────┴──────┴──────┴──────┘  │
│          │ ┌──────┬──────┬──────┬──────┐  │
│ □ Color  │ │ Card │ Card │ Card │ Card │  │
│ □ W      │ └──────┴──────┴──────┴──────┘  │
│ □ U      │                                 │
│ □ B      │ [Load More]                     │
│ □ R      │                                 │
│ □ G      │                                 │
│          │                                 │
│ CMC      │                                 │
│ [0─────6]│                                 │
│          │                                 │
│ □ Rarity │                                 │
│ □ Mechanics                                │
│ □ Roles  │                                 │
└──────────┴─────────────────────────────────┘
```

**Filter Implementation (from Stories.md #8-14):**

1. **Card Type** (#8) - Checkboxes
   - Creature, Instant, Sorcery, Artifact, Enchantment, Planeswalker, Land

2. **Color** (#9) - Checkboxes
   - W, U, B, R, G (white, blue, black, red, green)
   - Option: "Exact match" vs "Includes"

3. **Pip Cost** (#10) - Slider or input
   - Filters by `color_pip_intensity` property

4. **CMC** (#11) - Range slider
   - Min/Max converted mana cost

5. **Rarity** (#12) - Checkboxes
   - Common, Uncommon, Rare, Mythic

6. **Card Ability/Mechanic** (#13) - Multi-select dropdown
   - Searchable dropdown of 658 mechanics
   - Examples: ETB trigger, sacrifice outlet, recursion

7. **Functional Role** - Checkboxes
   - Ramp, card draw, removal, counterspell, etc.

**Components:**
- `FilterPanel.tsx` - Left sidebar container
- `CheckboxGroup.tsx` - Reusable checkbox group
- `RangeSlider.tsx` - CMC range slider
- `MechanicSearch.tsx` - Searchable mechanic dropdown
- `CardGrid.tsx` - Results grid with pagination
- `CardCard.tsx` - Single card display component

#### 4.2 Search State & API Integration
**File:** `frontend/src/features/card-search/useCardSearch.ts`

```typescript
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { cardsAPI } from '@/services/api';
import type { CardSearchFilters } from '@/types/card';

export function useCardSearch() {
  const [filters, setFilters] = useState<CardSearchFilters>({});
  const [page, setPage] = useState(1);

  const { data, isLoading, error } = useQuery({
    queryKey: ['cards', filters, page],
    queryFn: () => cardsAPI.search({ ...filters, page, limit: 20 }),
    keepPreviousData: true,
  });

  const updateFilter = (key: keyof CardSearchFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setPage(1); // Reset to page 1 on filter change
  };

  return { data, isLoading, error, filters, updateFilter, page, setPage };
}
```

**Backend Enhancement:**
Update `backend/app/routers/cards.py` to support pagination:
```python
@router.get("/api/cards")
async def search_cards(
    filters: CardSearchFilters = Depends(),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_neo4j_session)
):
    skip = (page - 1) * limit
    # Cypher query with SKIP and LIMIT
    # Also return total_count for pagination UI
    pass
```

**Verification:**
```bash
# Test search & filters:
1. Search by card name (text search)
2. Filter by color (checkbox)
3. Filter by type (checkbox)
4. Adjust CMC range slider
5. Select mechanics from dropdown
6. Verify results update in real-time
7. Test pagination (load more)
8. Check URL params update with filters
```

---

### Milestone 5: Similarity & Synergy Features (Week 5-6)

> **Execution:** Follow mandatory Execution Methodology above (Agent Teams + TDD + Code Review).

**Goal:** Card similarity finder and synergy analysis.

**Deliverables:**

#### 5.1 Card Detail Page
**File:** `frontend/src/features/cards/CardDetailPage.tsx`

**Layout:**
```
┌────────────────────────────────────────────┐
│ ← Back to Search                           │
├────────────┬───────────────────────────────┤
│            │ Eternal Witness               │
│   [Image]  │ {1}{G}{G}                     │
│            │ Creature — Human Shaman       │
│            │                               │
│            │ When Eternal Witness enters   │
│            │ the battlefield, you may      │
│            │ return target card from your  │
│            │ graveyard to your hand.       │
│            │                               │
│            │ 2/1                           │
├────────────┴───────────────────────────────┤
│ SIMILAR CARDS        SYNERGIES             │
│ [Regrowth] [card]... [Muldrotha] [card]...│
│                                            │
│ COMBOS                                     │
│ "Boonweaver Combo" with Pattern of Rebirth│
└────────────────────────────────────────────┘
```

**Features:**
- Card details display (image, text, stats)
- "Similar Cards" section (uses `/api/cards/{name}/similar`)
  - Shows top 10 cards via EMBEDDING_SIMILAR relationships
  - Display similarity score
- "Synergies" section (uses `/api/cards/{name}/synergies`)
  - Shows cards that synergize via 7-dimensional scoring
  - Display synergy score breakdown (mechanic overlap, role compatibility, etc.)
- "Known Combos" section (uses `/api/cards/{name}/combos`)
  - Shows documented combos from MTGJSON Spellbook

**Components:**
- `CardDetail.tsx` - Main card display
- `SimilarCards.tsx` - Grid of similar cards
- `SynergyCards.tsx` - Grid with synergy scores
- `CombosList.tsx` - List of combo descriptions
- `SynergyBreakdown.tsx` - Visualization of 7 dimensions

#### 5.2 Backend Synergy Endpoints
**File:** `backend/app/routers/cards.py`

Add synergy-specific endpoints:
```python
@router.get("/api/cards/{name}/synergies")
async def get_card_synergies(
    name: str,
    min_score: float = 0.5,
    limit: int = 20,
    session: Session = Depends(get_neo4j_session)
):
    # Query SYNERGIZES_WITH relationships
    # Return cards with synergy_score, dimension_scores
    pass

@router.post("/api/synergy/compute")
async def compute_synergy(
    card1: str,
    card2: str,
    session: Session = Depends(get_neo4j_session)
):
    # Use CardSynergyEngine.compute_synergy_score()
    # Return detailed breakdown of 7 dimensions
    pass
```

#### 5.3 Synergy Visualization
**File:** `frontend/src/features/cards/SynergyBreakdown.tsx`

Visualize 7-dimensional synergy score:
- Mechanic overlap (20% weight)
- Role compatibility (25% weight)
- Theme alignment (20% weight)
- Zone chains (15% weight)
- Phase alignment (10% weight)
- Color compatibility (5% weight)
- Type synergy (5% weight)

**Implementation:**
- Radar chart or horizontal bar chart
- Show individual dimension scores + weighted total
- Tooltip with explanation of each dimension

**Verification:**
```bash
# Test similarity & synergy:
1. View card detail page (e.g., Eternal Witness)
2. Verify similar cards load (top 10)
3. Click similar card → navigate to its detail page
4. View synergies section
5. Check synergy score breakdown visualization
6. Test known combos section
7. Verify all data loads from backend API
```

---

### Milestone 6: Collection Management (Week 6-7)

> **Execution:** Follow mandatory Execution Methodology above (Agent Teams + TDD + Code Review).

**Goal:** User collection tracking (client-side first, localStorage).

**Deliverables:**

#### 6.1 Collection State Management
**File:** `frontend/src/features/collection/useCollection.ts`

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Card } from '@/types/card';

interface CollectionState {
  cards: Map<string, { card: Card; quantity: number }>;
  addCard: (card: Card, quantity?: number) => void;
  removeCard: (cardName: string) => void;
  updateQuantity: (cardName: string, quantity: number) => void;
  hasCard: (cardName: string) => boolean;
  totalCards: () => number;
  totalUnique: () => number;
}

export const useCollection = create<CollectionState>()(
  persist(
    (set, get) => ({
      cards: new Map(),
      addCard: (card, quantity = 1) => set((state) => {
        const newCards = new Map(state.cards);
        const existing = newCards.get(card.name);
        newCards.set(card.name, {
          card,
          quantity: existing ? existing.quantity + quantity : quantity,
        });
        return { cards: newCards };
      }),
      removeCard: (cardName) => set((state) => {
        const newCards = new Map(state.cards);
        newCards.delete(cardName);
        return { cards: newCards };
      }),
      updateQuantity: (cardName, quantity) => set((state) => {
        const newCards = new Map(state.cards);
        const existing = newCards.get(cardName);
        if (existing) {
          newCards.set(cardName, { ...existing, quantity });
        }
        return { cards: newCards };
      }),
      hasCard: (cardName) => get().cards.has(cardName),
      totalCards: () => {
        return Array.from(get().cards.values())
          .reduce((sum, item) => sum + item.quantity, 0);
      },
      totalUnique: () => get().cards.size,
    }),
    { name: 'mtg-collection' }
  )
);
```

#### 6.2 Collection Page
**File:** `frontend/src/features/collection/CollectionPage.tsx`

**Layout:**
```
┌────────────────────────────────────────────┐
│ My Collection                              │
│ 1,247 cards | 487 unique                   │
├──────────────────────────────────────────┬─┤
│ [Search collection...]                   │ │
│ [Filter: All Types ▼] [Sort: Name ▼]     │ │
├──────────────────────────────────────────┴─┤
│ ┌────────┬────────┬────────┬────────┐      │
│ │ Card   │ Card   │ Card   │ Card   │      │
│ │ [4x]   │ [1x]   │ [2x]   │ [1x]   │      │
│ └────────┴────────┴────────┴────────┘      │
│ ┌────────┬────────┬────────┬────────┐      │
│ │ Card   │ Card   │ Card   │ Card   │      │
│ │ [1x]   │ [3x]   │ [1x]   │ [1x]   │      │
│ └────────┴────────┴────────┴────────┘      │
│                                            │
│ [Export to CSV] [Import from CSV]          │
└────────────────────────────────────────────┘
```

**Features:**
- Display all cards in collection with quantities
- Search within collection
- Filter by type, color, etc.
- Sort by name, CMC, quantity
- Add/remove cards from collection
- Export/import collection (CSV format)
- Collection statistics (color distribution, type breakdown, avg CMC)

#### 6.3 Collection Integration
Update existing components to show collection status:

**In search results:**
- Badge showing "In Collection (2x)" for owned cards
- Click to add/remove from collection

**In deck builder:**
- Filter recommendations by "Cards I Own"
- Show availability count for each card

#### 6.4 Future Enhancement (API)
**File:** `backend/app/routers/collections.py`

Prepare for future user accounts:
```python
# For now, these endpoints can accept anonymous collections
# Later, add authentication and user association

@router.post("/api/collections")
async def create_collection(
    collection: CollectionCreate,
    session: Session = Depends(get_neo4j_session)
):
    # Store collection in Neo4j or separate DB
    pass

@router.get("/api/collections/{id}")
async def get_collection(id: str):
    pass
```

**Verification:**
```bash
# Test collection management:
1. Add cards to collection from search results
2. View collection page
3. Update quantities
4. Remove cards
5. Search within collection
6. Export collection to CSV
7. Clear localStorage and import CSV
8. Verify persistence across browser refreshes
```

---

### Milestone 7: Polish & Production (Week 7-8)

> **Execution:** Follow mandatory Execution Methodology above (Agent Teams + TDD + Code Review).

**Goal:** Production-ready deployment with testing, error handling, and documentation.

**Deliverables:**

#### 7.1 Testing Setup

**Backend Tests:**
```bash
cd backend
uv pip install pytest pytest-asyncio httpx
```

**File:** `backend/tests/test_api.py`
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_commanders():
    response = client.get("/api/commanders")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_commander_synergies():
    response = client.get("/api/commanders/Muldrotha, the Gravetide/synergies")
    assert response.status_code == 200
    assert "synergies" in response.json()
```

**Frontend Tests:**
```bash
cd frontend
pnpm add -D vitest @testing-library/react @testing-library/jest-dom
pnpm add -D @playwright/test
```

**File:** `frontend/src/features/deck-builder/DeckBuilder.test.tsx`
```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import DeckBuilderPage from './DeckBuilderPage';

describe('DeckBuilder', () => {
  it('renders deck builder page', () => {
    render(<DeckBuilderPage />);
    expect(screen.getByText(/deck builder/i)).toBeInTheDocument();
  });
});
```

**E2E Tests with Playwright:**
```typescript
import { test, expect } from '@playwright/test';

test('deck builder workflow', async ({ page }) => {
  await page.goto('/');
  await page.click('text=Start Building');
  await page.fill('input[placeholder="Search commanders"]', 'Muldrotha');
  await page.click('text=Muldrotha, the Gravetide');
  await expect(page).toHaveURL(/deck-builder\/Muldrotha/);
  await expect(page.locator('.deck-list')).toContainText('Eternal Witness');
});
```

#### 7.2 Error Handling & Loading States

**Backend:**
- Add global exception handler in FastAPI
- Return consistent error format: `{ "error": "message", "detail": {...} }`
- Add request logging middleware
- Implement Neo4j connection retry logic

**Frontend:**
- Add global error boundary component
- Implement loading skeletons for all pages
- Add toast notifications for errors/success
- Handle network failures gracefully

#### 7.3 Performance Optimization

**Backend:**
- Add response caching for expensive queries (use `@lru_cache` or Redis)
- Optimize Cypher queries with proper indexes
- Add query result pagination everywhere
- Implement rate limiting (use `slowapi`)

**Frontend:**
- Code splitting with React lazy loading
- Virtualize long lists (use `react-virtual`)
- Optimize images (WebP format, lazy loading)
- Debounce search inputs
- Prefetch data on hover (React Query prefetching)

#### 7.4 Documentation

**Backend API:**
- Enhance OpenAPI docs with examples
- Add README for API setup
- Document environment variables

**Frontend:**
- Create component library documentation (Storybook optional)
- Add README for development setup
- Document state management patterns

**User Documentation:**
- Create user guide for deck building workflow
- Add tooltips throughout UI
- Create FAQ page (Stories.md #15)

#### 7.5 Deployment Setup

**Docker Compose Enhancement:**
```yaml
version: '3.8'
services:
  neo4j:
    # Existing Neo4j service

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_PASSWORD=password
    depends_on:
      - neo4j

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

**Frontend Production Build:**
```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

**Backend Production Setup:**
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install uv && uv pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Verification:**
```bash
# Run full test suite
cd backend && pytest
cd frontend && pnpm test && pnpm test:e2e

# Build production containers
docker-compose up --build

# Test production deployment
curl http://localhost:8000/docs
open http://localhost
```

---

## Critical Files to Create/Modify

### Backend (New Files)
1. `backend/app/main.py` - FastAPI app initialization
2. `backend/app/config.py` - Settings management
3. `backend/app/dependencies.py` - Neo4j connection DI
4. `backend/app/models/*.py` - Pydantic models (4 files)
5. `backend/app/routers/*.py` - API routes (5 files)
6. `backend/app/services/*.py` - Business logic (3 files)
7. `backend/tests/test_api.py` - API tests
8. `backend/Dockerfile` - Production build

### Frontend (New Files)
1. `frontend/src/App.tsx` - Routing setup
2. `frontend/src/services/api.ts` - API client
3. `frontend/src/types/*.ts` - TypeScript types (4 files)
4. `frontend/src/components/ui/*.tsx` - Base components (6 files)
5. `frontend/src/features/*/*.tsx` - Feature pages (12+ files)
6. `frontend/src/features/*/use*.ts` - Custom hooks (4 files)
7. `frontend/tailwind.config.js` - Design system
8. `frontend/biome.json` - Linting config
9. `frontend/Dockerfile` - Production build
10. `frontend/tests/*.spec.ts` - E2E tests

### Existing Files (No Changes Required)
- `main.py` - Data pipeline (remains separate)
- `src/synergy/queries.py` - Will be wrapped by backend services
- `src/validation/recommendations.py` - Will be wrapped by backend services
- All parsing/graph code - Backend imports these modules

### Configuration (Updates)
1. `docker-compose.yml` - Add backend + frontend services
2. `.gitignore` - Add `frontend/dist`, `backend/.env`
3. Root `README.md` - Update with new architecture

---

## Tech Stack Summary

**Backend:**
- FastAPI (async Python web framework)
- Neo4j Python Driver (graph database client)
- Pydantic (data validation and settings)
- uvicorn (ASGI server)
- uv (dependency management)

**Frontend:**
- React 18 + TypeScript
- Vite (build tool, 40x faster than CRA)
- Tailwind CSS (utility-first styling)
- React Router (client-side routing)
- TanStack Query (data fetching/caching)
- Zustand (state management)
- Axios (HTTP client)
- pnpm (package manager)
- Biome (linting + formatting, 20x faster than ESLint+Prettier)

**Testing:**
- Backend: pytest
- Frontend: Vitest + React Testing Library
- E2E: Playwright

**Development:**
- Monorepo structure
- Docker Compose for local dev
- Hot reload on both frontend and backend

---

## Verification Strategy

### End-to-End Testing Checklist

**Week 2 (Backend):**
- [ ] Backend starts successfully with `uvicorn app.main:app --reload`
- [ ] OpenAPI docs accessible at http://localhost:8000/docs
- [ ] All 20+ endpoints return valid responses
- [ ] Neo4j connection successful (test with sample query)
- [ ] Pagination works on list endpoints

**Week 3 (Frontend Foundation):**
- [ ] Frontend starts with `pnpm dev`
- [ ] Routing works (navigate between pages)
- [ ] API client successfully calls backend
- [ ] Tailwind styles applied correctly
- [ ] No console errors

**Week 4 (Deck Builder):**
- [ ] Commander selection flow works
- [ ] Initial deck shell loads (37 cards)
- [ ] Add/remove cards from deck
- [ ] Deck organized by type correctly
- [ ] Mana curve updates dynamically
- [ ] Recommendations load in sidebar

**Week 5 (Search & Filters):**
- [ ] Card search returns results
- [ ] All filter types work (color, type, CMC, rarity, mechanics)
- [ ] Results update in real-time
- [ ] Pagination works
- [ ] URL params update with filters

**Week 6 (Similarity & Synergy):**
- [ ] Card detail page loads
- [ ] Similar cards section populated
- [ ] Synergy scores displayed
- [ ] Combos section shows known combos
- [ ] Synergy breakdown visualization renders

**Week 7 (Collection):**
- [ ] Add/remove cards from collection
- [ ] Collection persists across refreshes
- [ ] Search within collection works
- [ ] Export/import CSV works
- [ ] Collection stats accurate

**Week 8 (Production):**
- [ ] All tests pass (pytest + vitest + playwright)
- [ ] Docker Compose builds all services
- [ ] Production deployment accessible
- [ ] Error handling works
- [ ] Loading states display correctly
- [ ] Performance acceptable (< 2s page loads)

---

## Success Metrics

**Functionality:**
- ✅ All 15+ Stories.md features implemented
- ✅ 20+ API endpoints operational
- ✅ Complete deck building workflow
- ✅ Advanced search with 7+ filter types
- ✅ Similarity, synergy, and combo finder working
- ✅ Collection management functional

**Quality:**
- ✅ 80%+ test coverage (backend)
- ✅ Zero console errors in production
- ✅ Accessible (keyboard navigation, screen reader friendly)
- ✅ Responsive (mobile, tablet, desktop)

**Performance:**
- ✅ < 2s initial page load
- ✅ < 500ms API response times (p95)
- ✅ < 100ms search filter updates

**UX:**
- ✅ Intuitive (user can build deck without tutorial)
- ✅ Elegant (matches Stripe/Claude design inspiration)
- ✅ Fast (no loading spinners > 1s)

---

## Next Steps After MVP

**Phase 2 Enhancements:**
1. User accounts & authentication
2. Save decks to cloud
3. Deck sharing & collaboration
4. Advanced analytics (deck similarity scoring)
5. Community features (upvote decks, comments)
6. Mobile app (React Native)
7. AI-powered deck suggestions (fine-tune on successful decks)

**Infrastructure:**
- Redis caching layer
- CDN for static assets
- Database for user data (PostgreSQL)
- Monitoring (Sentry, Datadog)
- CI/CD pipeline (GitHub Actions)
