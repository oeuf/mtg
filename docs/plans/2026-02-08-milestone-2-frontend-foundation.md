# Milestone 2: Frontend Foundation & Routing

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create the React frontend foundation with routing, API client, TypeScript types, and layout shell so feature pages can be built in Milestones 3-5.

**Architecture:** Vite + React 19 + TypeScript + React Router v7 + TanStack Query for data fetching + Tailwind CSS v4 for styling. The frontend lives in `frontend/` and talks to the FastAPI backend at `http://localhost:8000/api`.

**Tech Stack:** Node 23, npm, Vite, React 19, TypeScript, React Router v7, TanStack Query v5, Tailwind CSS v4, Vitest + React Testing Library

---

## Backend API Reference

These endpoints exist and are tested (53/53 passing):

```
GET  /health
GET  /api/cards?colors=&cmc_min=&cmc_max=&types=&mechanics=&roles=&page=&limit=
GET  /api/cards/{name}
GET  /api/cards/{name}/similar
GET  /api/cards/{name}/synergies
GET  /api/commanders?limit=&offset=
GET  /api/commanders/{name}
GET  /api/commanders/{name}/synergies
GET  /api/commanders/{name}/recommendations
POST /api/decks/build-shell        body: {"commander": "Name"}
POST /api/decks/analyze            body: {"commander": {}, "cards": []}
GET  /api/graph/stats
GET  /api/graph/health
GET  /api/mechanics
GET  /api/themes
GET  /api/roles
```

---

## Task 1: Initialize Vite + React + TypeScript Project

**Files:**
- Create: `frontend/package.json` (via npm create vite)
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`

**Step 1: Scaffold project**

```bash
cd /Users/ng/cc-projects/mtg
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

If `frontend/` already has files, delete them first:
```bash
rm -rf frontend/src frontend/.DS_Store
```
Then scaffold fresh.

**Step 2: Verify it builds**

```bash
cd /Users/ng/cc-projects/mtg/frontend && npm run build
```

Expected: Build succeeds with no errors.

**Step 3: Verify dev server starts**

```bash
cd /Users/ng/cc-projects/mtg/frontend && npm run dev &
sleep 3 && curl -s http://localhost:5173 | head -5
kill %1
```

Expected: HTML response with `<div id="root">`.

**Step 4: Commit**

```bash
git add frontend/
git commit -m "feat: scaffold Vite + React + TypeScript frontend"
```

**Note:** Add `frontend/node_modules/` and `frontend/dist/` to `.gitignore`.

---

## Task 2: Install Dependencies and Configure Tailwind

**Files:**
- Modify: `frontend/package.json`
- Create: `frontend/src/index.css`
- Modify: `frontend/vite.config.ts` (add proxy)

**Step 1: Install dependencies**

```bash
cd /Users/ng/cc-projects/mtg/frontend
npm install react-router-dom @tanstack/react-query
npm install -D tailwindcss @tailwindcss/vite vitest @testing-library/react @testing-library/jest-dom jsdom @types/react @types/react-dom
```

**Step 2: Configure Tailwind via Vite plugin**

`frontend/vite.config.ts`:
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test-setup.ts',
  },
})
```

**Step 3: Create CSS entry with Tailwind import**

`frontend/src/index.css`:
```css
@import "tailwindcss";
```

**Step 4: Create test setup file**

`frontend/src/test-setup.ts`:
```typescript
import '@testing-library/jest-dom/vitest'
```

**Step 5: Add test script to package.json**

Add to `"scripts"` in `frontend/package.json`:
```json
"test": "vitest run",
"test:watch": "vitest"
```

**Step 6: Verify build still works**

```bash
cd /Users/ng/cc-projects/mtg/frontend && npm run build
```

Expected: Build succeeds.

**Step 7: Commit**

```bash
git add frontend/
git commit -m "feat: add Tailwind, React Router, TanStack Query, Vitest"
```

---

## Task 3: TypeScript Types Matching Backend

**Files:**
- Create: `frontend/src/types/api.ts`
- Create: `frontend/src/types/index.ts`

**Step 1: Create shared types**

`frontend/src/types/api.ts`:
```typescript
// Card types
export interface Card {
  name: string
  mana_cost: string
  cmc: number
  type_line: string
  oracle_text: string
  color_identity: string[]
  colors: string[]
  keywords: string[]
  is_legendary: boolean
  edhrec_rank: number | null
  functional_categories: string[]
  mechanics: string[]
  themes: string[]
}

// Commander extends Card with power/toughness
export interface Commander extends Card {
  power: number | null
  toughness: number | null
}

// API response types
export interface CardSearchResponse {
  total: number
  page: number
  limit: number
  results: Card[]
}

export interface CommanderListResponse {
  total: number
  commanders: Array<{
    name: string
    color_identity: string[]
    edhrec_rank: number | null
  }>
}

export interface SynergyItem {
  card_name: string
  synergy_score: number
}

export interface SimilarCard {
  name: string
  score: number
}

export interface CommanderSynergiesResponse {
  commander: string
  synergies: SynergyItem[]
}

export interface CommanderRecommendationsResponse {
  commander: string
  recommendations: Array<{
    card_name: string
    score: number
  }>
}

export interface CardSimilarResponse {
  card: string
  similar_cards: SimilarCard[]
}

export interface CardSynergiesResponse {
  card: string
  synergies: Array<{
    name: string
    score: number
  }>
}

export interface DeckShellResponse {
  commander: string
  cards_by_role: Record<string, string[]>
  total_cards: number
}

export interface DeckAnalysisResponse {
  total_cards: number
  avg_cmc: number
  color_distribution: Record<string, number>
  type_distribution: Record<string, number>
  role_distribution: Record<string, number>
  mana_curve: Record<string, number>
}

export interface GraphStatsResponse {
  total_cards: number
  total_commanders: number
  total_mechanics: number
  total_relationships: number
  last_updated: string | null
}

export interface MechanicItem {
  name: string
  description: string | null
  card_count: number
}

export interface ThemeItem {
  name: string
  description: string | null
  card_count: number
}

export interface RoleItem {
  name: string
  description: string | null
  card_count: number
}

// Search filter params
export interface CardSearchParams {
  colors?: string
  cmc_min?: number
  cmc_max?: number
  types?: string
  mechanics?: string
  roles?: string
  page?: number
  limit?: number
}
```

`frontend/src/types/index.ts`:
```typescript
export * from './api'
```

**Step 2: Verify no type errors**

```bash
cd /Users/ng/cc-projects/mtg/frontend && npx tsc --noEmit
```

Expected: No errors.

**Step 3: Commit**

```bash
git add frontend/src/types/
git commit -m "feat: add TypeScript types matching backend API"
```

---

## Task 4: API Client Layer

**Files:**
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/api/index.ts`
- Create: `frontend/src/__tests__/api-client.test.ts`

**Step 1: Write the failing test**

`frontend/src/__tests__/api-client.test.ts`:
```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { api } from '../api/client'

// Mock fetch globally
const mockFetch = vi.fn()
global.fetch = mockFetch

beforeEach(() => {
  mockFetch.mockReset()
})

describe('API client', () => {
  it('searchCards calls correct endpoint', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ total: 0, page: 1, limit: 20, results: [] }),
    })

    const result = await api.searchCards({ colors: 'U,B' })
    expect(mockFetch).toHaveBeenCalledWith(
      '/api/cards?colors=U%2CB',
      expect.objectContaining({ method: 'GET' }),
    )
    expect(result.total).toBe(0)
  })

  it('getCommanders calls correct endpoint', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ total: 0, commanders: [] }),
    })

    const result = await api.getCommanders()
    expect(mockFetch).toHaveBeenCalledWith(
      '/api/commanders?limit=50&offset=0',
      expect.objectContaining({ method: 'GET' }),
    )
    expect(result.total).toBe(0)
  })

  it('throws on non-ok response', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: async () => ({ detail: 'Not found' }),
    })

    await expect(api.getCard('nonexistent')).rejects.toThrow()
  })
})
```

**Step 2: Run test to verify it fails**

```bash
cd /Users/ng/cc-projects/mtg/frontend && npx vitest run src/__tests__/api-client.test.ts
```

Expected: FAIL (module not found).

**Step 3: Write the API client**

`frontend/src/api/client.ts`:
```typescript
import type {
  CardSearchParams,
  CardSearchResponse,
  CommanderListResponse,
  Commander,
  Card,
  CommanderSynergiesResponse,
  CommanderRecommendationsResponse,
  CardSimilarResponse,
  CardSynergiesResponse,
  DeckShellResponse,
  DeckAnalysisResponse,
  GraphStatsResponse,
} from '../types'

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = 'ApiError'
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }))
    throw new ApiError(res.status, body.detail || res.statusText)
  }
  return res.json()
}

function toQuery(params: Record<string, unknown>): string {
  const search = new URLSearchParams()
  for (const [key, val] of Object.entries(params)) {
    if (val !== undefined && val !== null) {
      search.set(key, String(val))
    }
  }
  return search.toString()
}

export const api = {
  // Cards
  searchCards: (params: CardSearchParams = {}) =>
    request<CardSearchResponse>(`/api/cards?${toQuery(params)}`, { method: 'GET' }),

  getCard: (name: string) =>
    request<Card>(`/api/cards/${encodeURIComponent(name)}`, { method: 'GET' }),

  getSimilarCards: (name: string, limit = 10) =>
    request<CardSimilarResponse>(
      `/api/cards/${encodeURIComponent(name)}/similar?limit=${limit}`,
      { method: 'GET' },
    ),

  getCardSynergies: (name: string, limit = 10) =>
    request<CardSynergiesResponse>(
      `/api/cards/${encodeURIComponent(name)}/synergies?limit=${limit}`,
      { method: 'GET' },
    ),

  // Commanders
  getCommanders: (limit = 50, offset = 0) =>
    request<CommanderListResponse>(
      `/api/commanders?limit=${limit}&offset=${offset}`,
      { method: 'GET' },
    ),

  getCommander: (name: string) =>
    request<Commander>(
      `/api/commanders/${encodeURIComponent(name)}`,
      { method: 'GET' },
    ),

  getCommanderSynergies: (name: string, limit = 20) =>
    request<CommanderSynergiesResponse>(
      `/api/commanders/${encodeURIComponent(name)}/synergies?limit=${limit}`,
      { method: 'GET' },
    ),

  getCommanderRecommendations: (name: string, limit = 20) =>
    request<CommanderRecommendationsResponse>(
      `/api/commanders/${encodeURIComponent(name)}/recommendations?limit=${limit}`,
      { method: 'GET' },
    ),

  // Decks
  buildDeckShell: (commander: string) =>
    request<DeckShellResponse>('/api/decks/build-shell', {
      method: 'POST',
      body: JSON.stringify({ commander }),
    }),

  analyzeDeck: (commander: Record<string, unknown>, cards: Record<string, unknown>[]) =>
    request<DeckAnalysisResponse>('/api/decks/analyze', {
      method: 'POST',
      body: JSON.stringify({ commander, cards }),
    }),

  // Graph
  getGraphStats: () =>
    request<GraphStatsResponse>('/api/graph/stats', { method: 'GET' }),

  getHealth: () =>
    request<{ status: string }>('/health', { method: 'GET' }),
}
```

`frontend/src/api/index.ts`:
```typescript
export { api } from './client'
```

**Step 4: Run test to verify it passes**

```bash
cd /Users/ng/cc-projects/mtg/frontend && npx vitest run src/__tests__/api-client.test.ts
```

Expected: 3/3 PASS.

**Step 5: Commit**

```bash
git add frontend/src/api/ frontend/src/__tests__/
git commit -m "feat: add API client with fetch wrapper and tests"
```

---

## Task 5: React Router Setup with Route Shell Pages

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/main.tsx`
- Create: `frontend/src/pages/HomePage.tsx`
- Create: `frontend/src/pages/CardsPage.tsx`
- Create: `frontend/src/pages/CommandersPage.tsx`
- Create: `frontend/src/pages/CommanderDetailPage.tsx`
- Create: `frontend/src/pages/DeckBuilderPage.tsx`
- Create: `frontend/src/pages/NotFoundPage.tsx`
- Create: `frontend/src/__tests__/routing.test.tsx`

**Step 1: Write the failing test**

`frontend/src/__tests__/routing.test.tsx`:
```typescript
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import App from '../App'

describe('Routing', () => {
  it('renders home page at /', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>,
    )
    expect(screen.getByText(/mtg commander/i)).toBeInTheDocument()
  })

  it('renders cards page at /cards', () => {
    render(
      <MemoryRouter initialEntries={['/cards']}>
        <App />
      </MemoryRouter>,
    )
    expect(screen.getByText(/card search/i)).toBeInTheDocument()
  })

  it('renders commanders page at /commanders', () => {
    render(
      <MemoryRouter initialEntries={['/commanders']}>
        <App />
      </MemoryRouter>,
    )
    expect(screen.getByText(/commanders/i)).toBeInTheDocument()
  })

  it('renders deck builder page at /deck-builder', () => {
    render(
      <MemoryRouter initialEntries={['/deck-builder']}>
        <App />
      </MemoryRouter>,
    )
    expect(screen.getByText(/deck builder/i)).toBeInTheDocument()
  })

  it('renders 404 for unknown routes', () => {
    render(
      <MemoryRouter initialEntries={['/nonexistent']}>
        <App />
      </MemoryRouter>,
    )
    expect(screen.getByText(/not found/i)).toBeInTheDocument()
  })
})
```

**Step 2: Run test to verify it fails**

```bash
cd /Users/ng/cc-projects/mtg/frontend && npx vitest run src/__tests__/routing.test.tsx
```

Expected: FAIL.

**Step 3: Create page components and router**

`frontend/src/pages/HomePage.tsx`:
```typescript
export default function HomePage() {
  return (
    <div>
      <h1 className="text-3xl font-bold">MTG Commander</h1>
      <p className="mt-2 text-gray-600">Deck builder and card explorer</p>
    </div>
  )
}
```

`frontend/src/pages/CardsPage.tsx`:
```typescript
export default function CardsPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold">Card Search</h1>
    </div>
  )
}
```

`frontend/src/pages/CommandersPage.tsx`:
```typescript
export default function CommandersPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold">Commanders</h1>
    </div>
  )
}
```

`frontend/src/pages/CommanderDetailPage.tsx`:
```typescript
import { useParams } from 'react-router-dom'

export default function CommanderDetailPage() {
  const { name } = useParams<{ name: string }>()
  return (
    <div>
      <h1 className="text-2xl font-bold">Commander: {name}</h1>
    </div>
  )
}
```

`frontend/src/pages/DeckBuilderPage.tsx`:
```typescript
export default function DeckBuilderPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold">Deck Builder</h1>
    </div>
  )
}
```

`frontend/src/pages/NotFoundPage.tsx`:
```typescript
import { Link } from 'react-router-dom'

export default function NotFoundPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold">Not Found</h1>
      <p className="mt-2">The page you're looking for doesn't exist.</p>
      <Link to="/" className="mt-4 text-blue-600 underline">Go home</Link>
    </div>
  )
}
```

`frontend/src/App.tsx`:
```typescript
import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import CardsPage from './pages/CardsPage'
import CommandersPage from './pages/CommandersPage'
import CommanderDetailPage from './pages/CommanderDetailPage'
import DeckBuilderPage from './pages/DeckBuilderPage'
import NotFoundPage from './pages/NotFoundPage'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/cards" element={<CardsPage />} />
      <Route path="/commanders" element={<CommandersPage />} />
      <Route path="/commanders/:name" element={<CommanderDetailPage />} />
      <Route path="/deck-builder" element={<DeckBuilderPage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}
```

`frontend/src/main.tsx`:
```typescript
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App'
import './index.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      retry: 1,
    },
  },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
)
```

**Step 4: Run test to verify it passes**

```bash
cd /Users/ng/cc-projects/mtg/frontend && npx vitest run src/__tests__/routing.test.tsx
```

Expected: 5/5 PASS.

**Step 5: Commit**

```bash
git add frontend/src/
git commit -m "feat: add React Router with 5 route shell pages"
```

---

## Task 6: Layout Shell with Navigation

**Files:**
- Create: `frontend/src/components/Layout.tsx`
- Create: `frontend/src/components/Nav.tsx`
- Modify: `frontend/src/App.tsx` (wrap routes in Layout)
- Create: `frontend/src/__tests__/nav.test.tsx`

**Step 1: Write the failing test**

`frontend/src/__tests__/nav.test.tsx`:
```typescript
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Nav from '../components/Nav'

describe('Nav', () => {
  it('renders navigation links', () => {
    render(
      <MemoryRouter>
        <Nav />
      </MemoryRouter>,
    )
    expect(screen.getByRole('link', { name: /home/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /cards/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /commanders/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /deck builder/i })).toBeInTheDocument()
  })
})
```

**Step 2: Run test to verify it fails**

```bash
cd /Users/ng/cc-projects/mtg/frontend && npx vitest run src/__tests__/nav.test.tsx
```

Expected: FAIL.

**Step 3: Create Nav and Layout components**

`frontend/src/components/Nav.tsx`:
```typescript
import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: 'Home' },
  { to: '/cards', label: 'Cards' },
  { to: '/commanders', label: 'Commanders' },
  { to: '/deck-builder', label: 'Deck Builder' },
]

export default function Nav() {
  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-7xl items-center gap-6 px-4 py-3">
        <span className="text-lg font-bold">MTG Commander</span>
        <div className="flex gap-4">
          {links.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `text-sm ${isActive ? 'font-semibold text-blue-600' : 'text-gray-600 hover:text-gray-900'}`
              }
            >
              {label}
            </NavLink>
          ))}
        </div>
      </div>
    </nav>
  )
}
```

`frontend/src/components/Layout.tsx`:
```typescript
import { Outlet } from 'react-router-dom'
import Nav from './Nav'

export default function Layout() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Nav />
      <main className="mx-auto max-w-7xl px-4 py-6">
        <Outlet />
      </main>
    </div>
  )
}
```

Update `frontend/src/App.tsx` to use Layout as a wrapper route:
```typescript
import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import CardsPage from './pages/CardsPage'
import CommandersPage from './pages/CommandersPage'
import CommanderDetailPage from './pages/CommanderDetailPage'
import DeckBuilderPage from './pages/DeckBuilderPage'
import NotFoundPage from './pages/NotFoundPage'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/cards" element={<CardsPage />} />
        <Route path="/commanders" element={<CommandersPage />} />
        <Route path="/commanders/:name" element={<CommanderDetailPage />} />
        <Route path="/deck-builder" element={<DeckBuilderPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}
```

**Step 4: Run ALL tests**

```bash
cd /Users/ng/cc-projects/mtg/frontend && npx vitest run
```

Expected: All tests PASS (routing tests + nav test + api tests).

**Step 5: Verify build**

```bash
cd /Users/ng/cc-projects/mtg/frontend && npm run build
```

Expected: Build succeeds.

**Step 6: Commit**

```bash
git add frontend/src/
git commit -m "feat: add Layout shell with navigation bar"
```

---

## Task 7: Error Boundary and Loading State

**Files:**
- Create: `frontend/src/components/ErrorBoundary.tsx`
- Create: `frontend/src/components/LoadingSpinner.tsx`
- Create: `frontend/src/__tests__/error-boundary.test.tsx`

**Step 1: Write the failing test**

`frontend/src/__tests__/error-boundary.test.tsx`:
```typescript
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import ErrorBoundary from '../components/ErrorBoundary'

function ThrowingComponent() {
  throw new Error('test error')
}

describe('ErrorBoundary', () => {
  it('renders fallback on error', () => {
    // Suppress console.error for this test
    vi.spyOn(console, 'error').mockImplementation(() => {})

    render(
      <ErrorBoundary>
        <ThrowingComponent />
      </ErrorBoundary>,
    )
    expect(screen.getByText(/something went wrong/i)).toBeInTheDocument()
  })

  it('renders children when no error', () => {
    render(
      <ErrorBoundary>
        <div>content works</div>
      </ErrorBoundary>,
    )
    expect(screen.getByText('content works')).toBeInTheDocument()
  })
})
```

**Step 2: Run test to verify it fails**

```bash
cd /Users/ng/cc-projects/mtg/frontend && npx vitest run src/__tests__/error-boundary.test.tsx
```

Expected: FAIL.

**Step 3: Implement**

`frontend/src/components/ErrorBoundary.tsx`:
```typescript
import { Component, type ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="rounded-lg border border-red-200 bg-red-50 p-6">
          <h2 className="text-lg font-semibold text-red-800">Something went wrong</h2>
          <p className="mt-2 text-sm text-red-600">{this.state.error?.message}</p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            className="mt-4 rounded bg-red-600 px-4 py-2 text-sm text-white hover:bg-red-700"
          >
            Try again
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
```

`frontend/src/components/LoadingSpinner.tsx`:
```typescript
export default function LoadingSpinner({ text = 'Loading...' }: { text?: string }) {
  return (
    <div className="flex items-center gap-2 text-gray-500">
      <div className="h-5 w-5 animate-spin rounded-full border-2 border-gray-300 border-t-blue-600" />
      <span className="text-sm">{text}</span>
    </div>
  )
}
```

**Step 4: Run test to verify it passes**

```bash
cd /Users/ng/cc-projects/mtg/frontend && npx vitest run src/__tests__/error-boundary.test.tsx
```

Expected: 2/2 PASS.

**Step 5: Wrap App in ErrorBoundary in main.tsx**

Add `<ErrorBoundary>` around `<App />` in `frontend/src/main.tsx`.

**Step 6: Run ALL tests**

```bash
cd /Users/ng/cc-projects/mtg/frontend && npx vitest run
```

Expected: All tests PASS.

**Step 7: Commit**

```bash
git add frontend/src/
git commit -m "feat: add ErrorBoundary and LoadingSpinner components"
```

---

## Task 8: Final Verification

**Step 1: Run full frontend test suite**

```bash
cd /Users/ng/cc-projects/mtg/frontend && npx vitest run
```

Expected: All tests PASS.

**Step 2: Type check**

```bash
cd /Users/ng/cc-projects/mtg/frontend && npx tsc --noEmit
```

Expected: No errors.

**Step 3: Build**

```bash
cd /Users/ng/cc-projects/mtg/frontend && npm run build
```

Expected: Build succeeds.

**Step 4: Run backend tests (ensure no regression)**

```bash
source backend_venv/bin/activate && PYTHONPATH=backend:. pytest backend/tests/ -v --tb=short
```

Expected: 53/53 PASS.

---

## Definition of Done

- [ ] Vite + React + TypeScript project scaffolded and builds
- [ ] Tailwind CSS configured via Vite plugin
- [ ] TypeScript types match all backend API responses
- [ ] API client with fetch wrapper for all endpoints
- [ ] React Router with 5 routes (home, cards, commanders, commander detail, deck builder)
- [ ] Layout with navigation bar
- [ ] ErrorBoundary component
- [ ] LoadingSpinner component
- [ ] TanStack Query provider configured
- [ ] Vitest + React Testing Library configured
- [ ] All frontend tests passing
- [ ] Backend tests still passing (53/53)
- [ ] Build succeeds with no errors
- [ ] Type check passes with no errors
