# Fix Demo Mode: Require Neo4j with Real Data

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Remove mock data fallback and require a properly configured Neo4j database with real MTG card data, fixing all UI issues along the way.

**Architecture:** The API will require NEO4J_PASSWORD to be set and will fail fast with a helpful error if not configured. The frontend will display the commander name correctly and the card search will use the real database. We'll add a data loading script that users can run to populate Neo4j.

**Tech Stack:** FastAPI, Neo4j, Next.js, React Query

---

## Task 1: Remove Mock Mode from API Dependencies

**Files:**
- Modify: `api/dependencies.py`

**Step 1: Replace MockNeo4jConnection with proper error handling**

Replace the entire file content:

```python
"""FastAPI dependencies for dependency injection."""

import os
from src.graph.connection import Neo4jConnection


_connection: Neo4jConnection | None = None


def get_neo4j_connection() -> Neo4jConnection:
    """Get Neo4j connection. Raises error if not configured."""
    global _connection

    if _connection is not None:
        return _connection

    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD")

    if not password:
        raise RuntimeError(
            "NEO4J_PASSWORD environment variable not set. "
            "Please configure Neo4j and run 'python main.py' to load card data."
        )

    _connection = Neo4jConnection(uri, user, password)
    return _connection


def get_db() -> Neo4jConnection:
    """Dependency for Neo4j connection."""
    return get_neo4j_connection()
```

**Step 2: Verify API fails gracefully without Neo4j**

Run: `curl http://localhost:8000/api/commanders/`
Expected: 500 error with message about NEO4J_PASSWORD

**Step 3: Commit**

```bash
git add api/dependencies.py
git commit -m "fix: remove mock mode, require real Neo4j connection"
```

---

## Task 2: Fix Commanders Router to Use Real Queries

**Files:**
- Modify: `api/routers/commanders.py`

**Step 1: Simplify the recommendations endpoint**

Replace the entire file:

```python
"""Commander API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from api.dependencies import get_db
from api.schemas import CommanderResponse, RecommendationResponse
from src.graph.connection import Neo4jConnection
from src.synergy.queries import DeckbuildingQueries

router = APIRouter(prefix="/api/commanders", tags=["commanders"])


@router.get("/", response_model=list[CommanderResponse])
async def list_commanders(
    limit: int = Query(50, ge=1, le=500),
    search: Optional[str] = None,
    colors: Optional[str] = None,
    db: Neo4jConnection = Depends(get_db)
):
    """List all commanders with optional filtering."""
    query = """
    MATCH (c:Commander)
    WHERE ($search IS NULL OR toLower(c.name) CONTAINS toLower($search))
      AND ($colors IS NULL OR ALL(color IN $color_list WHERE color IN c.color_identity))
    RETURN c.name AS name,
           c.mana_cost AS mana_cost,
           c.cmc AS cmc,
           c.type_line AS type_line,
           c.oracle_text AS oracle_text,
           c.color_identity AS color_identity,
           c.mechanics AS mechanics,
           c.functional_categories AS functional_categories
    ORDER BY c.edhrec_rank ASC NULLS LAST
    LIMIT $limit
    """

    color_list = colors.split(",") if colors else None

    results = db.execute_query(query, {
        "search": search,
        "colors": colors,
        "color_list": color_list,
        "limit": limit
    })

    return [CommanderResponse(**r) for r in results]


@router.get("/{commander_name}", response_model=CommanderResponse)
async def get_commander(
    commander_name: str,
    db: Neo4jConnection = Depends(get_db)
):
    """Get details for a specific commander."""
    query = """
    MATCH (c:Commander {name: $name})
    OPTIONAL MATCH (c)-[s:SYNERGIZES_WITH_MECHANIC]->(m:Mechanic)
    RETURN c.name AS name,
           c.mana_cost AS mana_cost,
           c.cmc AS cmc,
           c.type_line AS type_line,
           c.oracle_text AS oracle_text,
           c.color_identity AS color_identity,
           c.mechanics AS mechanics,
           c.functional_categories AS functional_categories,
           collect(DISTINCT m.name) AS synergies
    """

    results = db.execute_query(query, {"name": commander_name})

    if not results:
        raise HTTPException(status_code=404, detail=f"Commander '{commander_name}' not found")

    return CommanderResponse(**results[0])


@router.get("/{commander_name}/recommendations", response_model=list[RecommendationResponse])
async def get_recommendations(
    commander_name: str,
    max_cmc: int = Query(10, ge=0, le=20),
    limit: int = Query(50, ge=1, le=200),
    db: Neo4jConnection = Depends(get_db)
):
    """Get card recommendations for a commander."""
    # Try v2 (GDS-enhanced) first, fall back to v1
    try:
        results = DeckbuildingQueries.find_synergistic_cards_v2(
            db,
            commander_name=commander_name,
            max_cmc=max_cmc,
            limit=limit
        )
    except Exception:
        results = DeckbuildingQueries.find_synergistic_cards(
            db,
            commander_name=commander_name,
            max_cmc=max_cmc,
            min_strength=0.0,
            limit=limit
        )

    return [
        RecommendationResponse(
            name=r["name"],
            mana_cost=r.get("mana_cost"),
            type_line=r.get("type"),
            cmc=r.get("cmc"),
            score=r.get("combined_score", r.get("synergy_strength", 0)),
            shared_mechanics=r.get("shared_mechanics", []),
            roles=r.get("roles", [])
        )
        for r in results
    ]
```

**Step 2: Commit**

```bash
git add api/routers/commanders.py
git commit -m "fix: use real Neo4j queries for commanders"
```

---

## Task 3: Fix Cards Router to Use Real Queries

**Files:**
- Modify: `api/routers/cards.py`

**Step 1: Read current cards router**

Check current implementation to understand what needs updating.

**Step 2: Update cards router with real queries**

Ensure the search endpoint uses proper Neo4j queries with color identity filtering.

**Step 3: Commit**

```bash
git add api/routers/cards.py
git commit -m "fix: use real Neo4j queries for card search"
```

---

## Task 4: Fix Commander Name Visibility in UI

**Files:**
- Modify: `frontend/src/components/CommanderSelector.tsx`

**Step 1: Fix the text color contrast issue**

The `bg-blue-100` background needs dark text. Update the selected commander display:

```typescript
{selected ? (
  <div className="flex items-center gap-2 p-2 bg-blue-100 dark:bg-blue-900 rounded">
    <span className="font-medium text-blue-900 dark:text-blue-100">{selected.name}</span>
    <span className="text-sm text-blue-700 dark:text-blue-300">{selected.mana_cost}</span>
    <button
      onClick={() => onSelect(null)}
      className="ml-auto text-red-500 hover:text-red-700"
    >
      x
    </button>
  </div>
) : (
```

**Step 2: Verify commander name is visible**

Open browser, select a commander, verify the name is visible on both light and dark backgrounds.

**Step 3: Commit**

```bash
git add frontend/src/components/CommanderSelector.tsx
git commit -m "fix: ensure commander name is visible on all backgrounds"
```

---

## Task 5: Add Startup Health Check for Neo4j

**Files:**
- Modify: `api/main.py`

**Step 1: Add startup event to verify database connection**

```python
"""FastAPI application for MTG Knowledge Graph API."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import commanders, cards, decks, graph
from api.dependencies import get_neo4j_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Verify Neo4j connection on startup."""
    try:
        conn = get_neo4j_connection()
        # Verify we have data
        result = conn.execute_query("MATCH (c:Commander) RETURN count(c) as count")
        count = result[0]["count"] if result else 0
        if count == 0:
            print("WARNING: No commanders found in database. Run 'python main.py' to load data.")
        else:
            print(f"Connected to Neo4j. Found {count} commanders.")
    except Exception as e:
        print(f"ERROR: Failed to connect to Neo4j: {e}")
        print("Please set NEO4J_PASSWORD and ensure Neo4j is running.")
        raise
    yield


app = FastAPI(
    title="MTG Commander Knowledge Graph API",
    description="API for Commander deck building recommendations",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "MTG Commander Knowledge Graph API",
        "docs": "/docs",
        "version": "1.0.0"
    }


# Include routers
app.include_router(commanders.router)
app.include_router(cards.router)
app.include_router(decks.router)
app.include_router(graph.router)
```

**Step 2: Commit**

```bash
git add api/main.py
git commit -m "feat: add startup health check for Neo4j connection"
```

---

## Task 6: Update E2E Tests to Require Neo4j

**Files:**
- Modify: `frontend/playwright.config.ts`
- Modify: `frontend/e2e/build.spec.ts`

**Step 1: Update playwright config to check for Neo4j**

The tests should skip or fail gracefully if Neo4j isn't configured:

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: [
    {
      command: 'cd .. && NEO4J_PASSWORD=$NEO4J_PASSWORD python3 -m uvicorn api.main:app --port 8000',
      url: 'http://localhost:8000/health',
      reuseExistingServer: !process.env.CI,
      timeout: 30000,
    },
    {
      command: 'npm run dev',
      url: 'http://localhost:3000',
      reuseExistingServer: !process.env.CI,
      timeout: 30000,
    },
  ],
});
```

**Step 2: Update build spec to test real commander search**

Update the test to search for any commander (not just Muldrotha):

```typescript
test('should search and select a commander', async ({ page }) => {
  await page.goto('/build');
  await page.waitForLoadState('networkidle');

  // Search for any commander starting with "A"
  await page.getByPlaceholder('Search for a commander').fill('Atraxa');

  // Wait for search results
  await page.waitForResponse(resp => resp.url().includes('/api/commanders') && resp.status() === 200);

  // Should show results
  const results = page.locator('ul li');
  await expect(results.first()).toBeVisible();
});
```

**Step 3: Commit**

```bash
git add frontend/playwright.config.ts frontend/e2e/build.spec.ts
git commit -m "test: update E2E tests to use real Neo4j data"
```

---

## Task 7: Create Setup Documentation

**Files:**
- Create: `docs/SETUP.md`

**Step 1: Write setup instructions**

```markdown
# MTG Commander Knowledge Graph - Setup Guide

## Prerequisites

1. **Neo4j** - Install and start Neo4j Desktop or use Docker:
   ```bash
   docker run -d --name neo4j \
     -p 7474:7474 -p 7687:7687 \
     -e NEO4J_AUTH=neo4j/your_password \
     neo4j:5
   ```

2. **Python 3.9+** with dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **Node.js 18+** for the frontend:
   ```bash
   cd frontend && npm install
   ```

## Load Data into Neo4j

Set environment variables:
```bash
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=your_password
```

Run the data loader (takes ~10 minutes):
```bash
python main.py
```

This will:
- Download card data from MTGJSON
- Parse and enrich ~20,000 Commander-legal cards
- Load cards, relationships, and synergies into Neo4j
- Run graph algorithms (PageRank, community detection)

## Start the Application

Terminal 1 - API:
```bash
export NEO4J_PASSWORD=your_password
python -m uvicorn api.main:app --port 8000 --reload
```

Terminal 2 - Frontend:
```bash
cd frontend && npm run dev
```

Visit http://localhost:3000

## Running Tests

```bash
# Backend unit tests
pytest tests/ -v

# E2E tests (requires Neo4j running with data)
cd frontend && npm run test:e2e
```
```

**Step 2: Commit**

```bash
git add docs/SETUP.md
git commit -m "docs: add setup guide for Neo4j configuration"
```

---

## Task 8: Final Verification

**Step 1: Start Neo4j and load data**

```bash
export NEO4J_PASSWORD=your_password
python main.py  # If not already loaded
```

**Step 2: Start API and verify**

```bash
export NEO4J_PASSWORD=your_password
python -m uvicorn api.main:app --port 8000
```

Verify: `curl "http://localhost:8000/api/commanders/?search=mul&limit=5"` returns Muldrotha and other commanders.

**Step 3: Start frontend and test**

```bash
cd frontend && npm run dev
```

Test manually:
1. Search for "Atraxa" - should find multiple commanders
2. Select commander - name should be clearly visible
3. Card search should work with real cards
4. Recommendations should show 50+ cards
5. CMC filter should work

**Step 4: Run E2E tests**

```bash
cd frontend && npm run test:e2e
```

**Step 5: Push all changes**

```bash
git push origin feature/kg-v2-phase1
```

---

## Verification Checklist

- [ ] API fails with helpful error when NEO4J_PASSWORD not set
- [ ] API connects successfully when Neo4j configured
- [ ] Commander search returns real commanders from database
- [ ] Commander name is visible when selected (dark text on light bg)
- [ ] Card search works with real database
- [ ] Recommendations show 50+ cards
- [ ] CMC/role filters work correctly
- [ ] E2E tests pass with real data
- [ ] Setup documentation is complete
