# MTG Commander Knowledge Graph

## Quick Start

```bash
# Neo4j
docker-compose up -d

# Backend (port 8000)
source backend_venv/bin/activate
cd backend && uvicorn app.main:app --reload

# Frontend (port 5173)
cd frontend && pnpm dev
```

## Tech Stack

- **Data pipeline:** Python, Neo4j 5.15.0 + GDS plugin
- **Backend:** FastAPI, neo4j driver, pydantic-settings, slowapi (rate limiting)
- **Frontend:** React 19, TypeScript, Vite, Tailwind v4, zustand, react-query, react-router-dom
- **Testing:** pytest (backend), Vitest + @testing-library/react (frontend)
- **Linting:** Biome (frontend) — not ESLint
- **Package manager:** pnpm (frontend)

## Commands

```bash
# Backend tests (venv required, PYTHONPATH required)
source backend_venv/bin/activate
PYTHONPATH=backend:. pytest backend/tests/ -v

# Frontend tests
cd frontend && pnpm test

# Frontend build
cd frontend && pnpm build

# Frontend lint
cd frontend && pnpm lint

# Data pipeline (standalone, uses separate venv)
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
export NEO4J_PASSWORD="password"
python -u main.py
```

## Architecture

```
backend/app/
  main.py              # FastAPI app (CORS, rate limiting, error handlers)
  config.py            # pydantic-settings (NEO4J_URI, NEO4J_PASSWORD from env/.env)
  dependencies.py      # Neo4j driver singleton + get_neo4j_session DI
  routers/             # cards, commanders, decks, graph (all under /api prefix)
  services/            # query_service, recommendation_service, synergy_service
  models/              # card, commander, deck, synergy (pydantic response models)

frontend/src/
  App.tsx              # Routes: /, /commanders, /deck-builder/:commander, /cards, /cards/:name, /collection
  features/            # card-search, cards, collection, commanders, deck-builder, home
  services/api.ts      # axios client with typed endpoint functions
  components/          # Layout, ErrorBoundary, LoadingSpinner, ToastContext

src/                   # Data pipeline (parsing, graph loading, synergy scoring)
  data/                # MTGJSON download + parsing
  parsing/             # mechanics, functional_roles, properties extraction
  graph/               # Neo4j connection, batch loaders, GDS algorithms
  synergy/             # 7-dimensional synergy scoring engine
```

## Key Patterns

- **Neo4j DI:** `get_neo4j_session` yields a Session. Override in tests via `app.dependency_overrides[get_neo4j_session]`
- **Tailwind v4:** Uses `@import "tailwindcss"` + `@theme {}` in CSS and `@tailwindcss/vite` plugin — no `tailwind.config.js` or postcss
- **Vitest config:** Embedded in `vite.config.ts` via `/// <reference types="vitest/config" />`
- **State management:** zustand store (`useDeckBuilder`) for deck state
- **API client:** axios with typed functions in `frontend/src/services/api.ts`

## Gotchas

- **Two venvs:** `backend_venv/` for FastAPI, `venv/` for data pipeline. Don't mix them
- **PYTHONPATH:** Backend tests require `PYTHONPATH=backend:.` or imports fail
- **CORS:** Backend allows `localhost:5173` (Vite dev) and `localhost` (production)
- **Neo4j auth rate limit:** If connections fail after too many attempts, `docker restart mtg-neo4j && sleep 15`
- **APOC missing:** Container doesn't have APOC. Use `json.dumps()` instead of `apoc.convert.toJson()`
- **Phase 9.5 bug:** `create_enhanced_synergy_relationships()` creates 0 relationships. Run `python run_enhanced_synergy.py` instead
- **Python buffering:** Use `python -u` for unbuffered output in background tasks

## Docker

```bash
docker-compose up -d    # Neo4j (7474/7687), Backend (8000), Frontend (80)
```

Neo4j auth: `neo4j/password` (hardcoded in docker-compose.yml and backend config)
