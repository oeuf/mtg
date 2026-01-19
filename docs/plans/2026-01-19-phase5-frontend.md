# Phase 5: Frontend Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a Next.js frontend with Deck Builder, Deck Analyzer, Graph Explorer, and Commander Lookup pages.

**Architecture:** Next.js 14 App Router with TypeScript, Tailwind CSS, React Query for data fetching, and D3.js for graph visualization.

**Tech Stack:** Next.js 14, TypeScript, Tailwind CSS, React Query, D3.js

**Prerequisites:** Phase 4 complete (API running)

---

## Task 1: Create Next.js Project

**Step 1: Create Next.js app**

Run from `mtg/` directory:

```bash
npx create-next-app@latest frontend --typescript --tailwind --app --src-dir --import-alias "@/*"
```

Select options:
- Would you like to use ESLint? → Yes
- Would you like to use `src/` directory? → Yes
- Would you like to customize the default import alias? → No

**Step 2: Install dependencies**

```bash
cd frontend
npm install @tanstack/react-query axios d3 @types/d3
```

**Step 3: Verify it runs**

```bash
npm run dev
```

Visit http://localhost:3000

**Step 4: Commit**

```bash
cd ..
git add frontend/
git commit -m "feat: create Next.js frontend project"
```

---

## Task 2: Set Up API Client and React Query

**Files:**
- Create: `frontend/src/lib/api.ts`
- Create: `frontend/src/lib/queries.ts`
- Modify: `frontend/src/app/layout.tsx`
- Create: `frontend/src/app/providers.tsx`

**Step 1: Create API client**

Create `frontend/src/lib/api.ts`:

```typescript
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Card {
  name: string;
  mana_cost?: string;
  cmc?: number;
  type_line?: string;
  oracle_text?: string;
  color_identity: string[];
  mechanics: string[];
  functional_categories: string[];
  synergy_score?: number;
  popularity_score?: number;
}

export interface Commander extends Card {
  can_be_commander: boolean;
  synergies: string[];
}

export interface Recommendation {
  name: string;
  mana_cost?: string;
  type_line?: string;
  cmc?: number;
  score: number;
  shared_mechanics: string[];
  roles: string[];
}

export interface DeckAnalysis {
  commander: string;
  card_count: number;
  role_coverage: Record<string, number>;
  missing_roles: string[];
  suggested_additions: Recommendation[];
  suggested_cuts: string[];
}

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  properties: Record<string, unknown>;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
  properties: Record<string, unknown>;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

// API functions
export const commandersApi = {
  list: (params?: { limit?: number; search?: string; colors?: string }) =>
    api.get<Commander[]>('/api/commanders', { params }),

  get: (name: string) =>
    api.get<Commander>(`/api/commanders/${encodeURIComponent(name)}`),

  getRecommendations: (name: string, params?: { max_cmc?: number; limit?: number }) =>
    api.get<Recommendation[]>(`/api/commanders/${encodeURIComponent(name)}/recommendations`, { params }),
};

export const cardsApi = {
  search: (params: { q: string; max_cmc?: number; colors?: string; role?: string; limit?: number }) =>
    api.get<Card[]>('/api/cards/search', { params }),

  get: (name: string) =>
    api.get<Card>(`/api/cards/${encodeURIComponent(name)}`),

  getCombos: (name: string) =>
    api.get<{ piece1: string; piece2: string; description?: string }[]>(
      `/api/cards/${encodeURIComponent(name)}/combos`
    ),

  getByRole: (role: string, params?: { colors?: string; max_cmc?: number; limit?: number }) =>
    api.get<Card[]>(`/api/cards/role/${encodeURIComponent(role)}`, { params }),
};

export const decksApi = {
  create: (data: { commander: string; name?: string }) =>
    api.post('/api/decks', data),

  get: (id: string) =>
    api.get(`/api/decks/${id}`),

  addCard: (id: string, cardName: string) =>
    api.post(`/api/decks/${id}/cards`, { card_name: cardName }),

  removeCard: (id: string, cardName: string) =>
    api.delete(`/api/decks/${id}/cards/${encodeURIComponent(cardName)}`),

  analyze: (data: { commander: string; cards: string[] }) =>
    api.post<DeckAnalysis>('/api/decks/analyze', data),
};

export const graphApi = {
  getCardGraph: (name: string, params?: { depth?: number }) =>
    api.get<GraphData>(`/api/graph/card/${encodeURIComponent(name)}`, { params }),

  getCommunity: (id: number, params?: { limit?: number }) =>
    api.get<GraphData>(`/api/graph/community/${id}`, { params }),

  getSimilar: (name: string, params?: { limit?: number }) =>
    api.get(`/api/graph/similar/${encodeURIComponent(name)}`, { params }),
};
```

**Step 2: Create React Query provider**

Create `frontend/src/app/providers.tsx`:

```typescript
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
```

**Step 3: Update layout**

Update `frontend/src/app/layout.tsx`:

```typescript
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'MTG Commander Deck Builder',
  description: 'Build Commander decks with AI-powered recommendations',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <nav className="bg-gray-900 text-white p-4">
            <div className="container mx-auto flex gap-6">
              <a href="/" className="font-bold text-xl">MTG KB</a>
              <a href="/build" className="hover:text-blue-400">Build</a>
              <a href="/analyze" className="hover:text-blue-400">Analyze</a>
              <a href="/explore" className="hover:text-blue-400">Explore</a>
            </div>
          </nav>
          <main className="container mx-auto p-4">
            {children}
          </main>
        </Providers>
      </body>
    </html>
  );
}
```

**Step 4: Commit**

```bash
git add frontend/
git commit -m "feat: add API client and React Query setup"
```

---

## Task 3: Create Deck Builder Page

**Files:**
- Create: `frontend/src/app/build/page.tsx`
- Create: `frontend/src/components/CommanderSelector.tsx`
- Create: `frontend/src/components/CardSearch.tsx`
- Create: `frontend/src/components/DeckList.tsx`

**Step 1: Create CommanderSelector component**

Create `frontend/src/components/CommanderSelector.tsx`:

```typescript
'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { commandersApi, Commander } from '@/lib/api';

interface Props {
  onSelect: (commander: Commander) => void;
  selected?: Commander;
}

export function CommanderSelector({ onSelect, selected }: Props) {
  const [search, setSearch] = useState('');

  const { data: commanders, isLoading } = useQuery({
    queryKey: ['commanders', search],
    queryFn: () => commandersApi.list({ search, limit: 20 }).then(r => r.data),
    enabled: search.length >= 2,
  });

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium">Commander</label>
      {selected ? (
        <div className="flex items-center gap-2 p-2 bg-blue-100 rounded">
          <span className="font-medium">{selected.name}</span>
          <span className="text-sm text-gray-600">{selected.mana_cost}</span>
          <button
            onClick={() => onSelect(null as any)}
            className="ml-auto text-red-500 hover:text-red-700"
          >
            ×
          </button>
        </div>
      ) : (
        <>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search for a commander..."
            className="w-full p-2 border rounded"
          />
          {isLoading && <p className="text-sm text-gray-500">Loading...</p>}
          {commanders && commanders.length > 0 && (
            <ul className="border rounded max-h-60 overflow-y-auto">
              {commanders.map((c) => (
                <li
                  key={c.name}
                  onClick={() => {
                    onSelect(c);
                    setSearch('');
                  }}
                  className="p-2 hover:bg-gray-100 cursor-pointer"
                >
                  <span className="font-medium">{c.name}</span>
                  <span className="ml-2 text-sm text-gray-600">{c.mana_cost}</span>
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </div>
  );
}
```

**Step 2: Create CardSearch component**

Create `frontend/src/components/CardSearch.tsx`:

```typescript
'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { cardsApi, Card } from '@/lib/api';

interface Props {
  colorIdentity: string[];
  onAddCard: (card: Card) => void;
}

export function CardSearch({ colorIdentity, onAddCard }: Props) {
  const [search, setSearch] = useState('');
  const [maxCmc, setMaxCmc] = useState<number | undefined>();
  const [role, setRole] = useState<string>('');

  const { data: cards, isLoading } = useQuery({
    queryKey: ['cards', search, maxCmc, role, colorIdentity],
    queryFn: () =>
      cardsApi.search({
        q: search,
        max_cmc: maxCmc,
        colors: colorIdentity.join(','),
        role: role || undefined,
        limit: 30,
      }).then(r => r.data),
    enabled: search.length >= 2,
  });

  return (
    <div className="space-y-2">
      <div className="flex gap-2">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search cards..."
          className="flex-1 p-2 border rounded"
        />
        <select
          value={maxCmc ?? ''}
          onChange={(e) => setMaxCmc(e.target.value ? parseInt(e.target.value) : undefined)}
          className="p-2 border rounded"
        >
          <option value="">Any CMC</option>
          {[1, 2, 3, 4, 5, 6, 7].map(n => (
            <option key={n} value={n}>≤{n} CMC</option>
          ))}
        </select>
        <select
          value={role}
          onChange={(e) => setRole(e.target.value)}
          className="p-2 border rounded"
        >
          <option value="">Any Role</option>
          <option value="ramp">Ramp</option>
          <option value="card_draw">Card Draw</option>
          <option value="removal">Removal</option>
          <option value="recursion">Recursion</option>
          <option value="protection">Protection</option>
        </select>
      </div>

      {isLoading && <p className="text-sm text-gray-500">Searching...</p>}

      {cards && (
        <ul className="border rounded max-h-80 overflow-y-auto">
          {cards.map((card) => (
            <li
              key={card.name}
              className="p-2 hover:bg-gray-100 flex items-center"
            >
              <div className="flex-1">
                <span className="font-medium">{card.name}</span>
                <span className="ml-2 text-sm text-gray-600">{card.mana_cost}</span>
                <div className="text-xs text-gray-500">
                  {card.functional_categories.join(', ')}
                </div>
              </div>
              <button
                onClick={() => onAddCard(card)}
                className="px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                Add
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

**Step 3: Create DeckList component**

Create `frontend/src/components/DeckList.tsx`:

```typescript
'use client';

import { Card } from '@/lib/api';

interface Props {
  cards: Card[];
  onRemoveCard: (name: string) => void;
}

export function DeckList({ cards, onRemoveCard }: Props) {
  // Group by role
  const byRole: Record<string, Card[]> = {};
  cards.forEach(card => {
    const role = card.functional_categories[0] || 'Other';
    if (!byRole[role]) byRole[role] = [];
    byRole[role].push(card);
  });

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="font-bold">Deck ({cards.length}/99)</h3>
        <div className="text-sm text-gray-600">
          Avg CMC: {(cards.reduce((sum, c) => sum + (c.cmc || 0), 0) / cards.length || 0).toFixed(2)}
        </div>
      </div>

      {Object.entries(byRole).sort().map(([role, roleCards]) => (
        <div key={role}>
          <h4 className="font-medium text-sm text-gray-700 capitalize">
            {role.replace('_', ' ')} ({roleCards.length})
          </h4>
          <ul className="space-y-1">
            {roleCards.sort((a, b) => (a.cmc || 0) - (b.cmc || 0)).map(card => (
              <li
                key={card.name}
                className="flex items-center text-sm p-1 hover:bg-gray-100 rounded"
              >
                <span className="flex-1">{card.name}</span>
                <span className="text-gray-500 mr-2">{card.mana_cost}</span>
                <button
                  onClick={() => onRemoveCard(card.name)}
                  className="text-red-500 hover:text-red-700"
                >
                  ×
                </button>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
```

**Step 4: Create build page**

Create `frontend/src/app/build/page.tsx`:

```typescript
'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Commander, Card, commandersApi, Recommendation } from '@/lib/api';
import { CommanderSelector } from '@/components/CommanderSelector';
import { CardSearch } from '@/components/CardSearch';
import { DeckList } from '@/components/DeckList';

export default function BuildPage() {
  const [commander, setCommander] = useState<Commander | null>(null);
  const [deckCards, setDeckCards] = useState<Card[]>([]);

  const { data: recommendations } = useQuery({
    queryKey: ['recommendations', commander?.name],
    queryFn: () =>
      commandersApi.getRecommendations(commander!.name, { limit: 30 }).then(r => r.data),
    enabled: !!commander,
  });

  const addCard = (card: Card) => {
    if (!deckCards.find(c => c.name === card.name)) {
      setDeckCards([...deckCards, card]);
    }
  };

  const removeCard = (name: string) => {
    setDeckCards(deckCards.filter(c => c.name !== name));
  };

  return (
    <div className="grid grid-cols-3 gap-6">
      {/* Left: Commander & Search */}
      <div className="space-y-6">
        <CommanderSelector onSelect={setCommander} selected={commander || undefined} />

        {commander && (
          <CardSearch
            colorIdentity={commander.color_identity}
            onAddCard={addCard}
          />
        )}
      </div>

      {/* Middle: Recommendations */}
      <div>
        <h2 className="font-bold mb-4">Recommendations</h2>
        {recommendations ? (
          <ul className="space-y-2 max-h-[600px] overflow-y-auto">
            {recommendations.map((rec: Recommendation) => (
              <li
                key={rec.name}
                className="p-2 border rounded hover:bg-gray-50"
              >
                <div className="flex items-center">
                  <span className="font-medium flex-1">{rec.name}</span>
                  <span className="text-sm text-gray-600 mr-2">{rec.mana_cost}</span>
                  <button
                    onClick={() => addCard({
                      name: rec.name,
                      mana_cost: rec.mana_cost,
                      cmc: rec.cmc,
                      type_line: rec.type_line,
                      color_identity: [],
                      mechanics: rec.shared_mechanics,
                      functional_categories: rec.roles,
                    })}
                    className="px-2 py-1 bg-green-500 text-white rounded text-sm"
                  >
                    +
                  </button>
                </div>
                <div className="text-xs text-gray-500">
                  Score: {rec.score.toFixed(2)} | {rec.roles.join(', ')}
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-500">Select a commander to see recommendations</p>
        )}
      </div>

      {/* Right: Deck List */}
      <div>
        <DeckList cards={deckCards} onRemoveCard={removeCard} />
      </div>
    </div>
  );
}
```

**Step 5: Commit**

```bash
git add frontend/
git commit -m "feat: add deck builder page with recommendations"
```

---

## Task 4: Create Deck Analyzer Page

**Files:**
- Create: `frontend/src/app/analyze/page.tsx`

**Step 1: Create analyze page**

Create `frontend/src/app/analyze/page.tsx`:

```typescript
'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { decksApi, DeckAnalysis } from '@/lib/api';

export default function AnalyzePage() {
  const [commander, setCommander] = useState('');
  const [decklist, setDecklist] = useState('');
  const [analysis, setAnalysis] = useState<DeckAnalysis | null>(null);

  const analyzeMutation = useMutation({
    mutationFn: (data: { commander: string; cards: string[] }) =>
      decksApi.analyze(data).then(r => r.data),
    onSuccess: (data) => setAnalysis(data),
  });

  const handleAnalyze = () => {
    const cards = decklist
      .split('\n')
      .map(line => {
        const match = line.match(/^\d+\s+(.+)$/);
        return match ? match[1].trim() : null;
      })
      .filter(Boolean) as string[];

    if (commander && cards.length > 0) {
      analyzeMutation.mutate({ commander, cards });
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Deck Analyzer</h1>

      <div className="grid grid-cols-2 gap-6">
        {/* Input */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Commander</label>
            <input
              type="text"
              value={commander}
              onChange={(e) => setCommander(e.target.value)}
              placeholder="Muldrotha, the Gravetide"
              className="w-full p-2 border rounded"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Decklist (Moxfield format: "1 Card Name")
            </label>
            <textarea
              value={decklist}
              onChange={(e) => setDecklist(e.target.value)}
              placeholder="1 Sol Ring&#10;1 Eternal Witness&#10;1 Spore Frog"
              className="w-full h-80 p-2 border rounded font-mono text-sm"
            />
          </div>

          <button
            onClick={handleAnalyze}
            disabled={analyzeMutation.isPending}
            className="w-full py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
          >
            {analyzeMutation.isPending ? 'Analyzing...' : 'Analyze Deck'}
          </button>
        </div>

        {/* Results */}
        <div>
          {analysis && (
            <div className="space-y-4">
              <div className="p-4 bg-gray-100 rounded">
                <h3 className="font-bold">Overview</h3>
                <p>Commander: {analysis.commander}</p>
                <p>Cards: {analysis.card_count}</p>
              </div>

              <div className="p-4 bg-gray-100 rounded">
                <h3 className="font-bold mb-2">Role Coverage</h3>
                <div className="space-y-1">
                  {Object.entries(analysis.role_coverage).map(([role, count]) => (
                    <div key={role} className="flex items-center">
                      <span className="w-32 capitalize">{role.replace('_', ' ')}</span>
                      <div className="flex-1 bg-gray-300 rounded h-4">
                        <div
                          className="bg-blue-500 h-4 rounded"
                          style={{ width: `${Math.min(count * 10, 100)}%` }}
                        />
                      </div>
                      <span className="w-8 text-right text-sm">{count}</span>
                    </div>
                  ))}
                </div>
              </div>

              {analysis.missing_roles.length > 0 && (
                <div className="p-4 bg-yellow-100 rounded">
                  <h3 className="font-bold text-yellow-800">Missing Roles</h3>
                  <ul className="list-disc list-inside">
                    {analysis.missing_roles.map(role => (
                      <li key={role} className="capitalize">{role.replace('_', ' ')}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="p-4 bg-green-100 rounded">
                <h3 className="font-bold text-green-800 mb-2">Suggested Additions</h3>
                <ul className="space-y-1">
                  {analysis.suggested_additions.slice(0, 10).map(card => (
                    <li key={card.name} className="text-sm">
                      {card.name} ({card.mana_cost}) - {card.roles.join(', ')}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```

**Step 2: Commit**

```bash
git add frontend/
git commit -m "feat: add deck analyzer page"
```

---

## Task 5: Create Graph Explorer Page

**Files:**
- Create: `frontend/src/app/explore/page.tsx`
- Create: `frontend/src/components/GraphVisualization.tsx`

**Step 1: Create GraphVisualization component**

Create `frontend/src/components/GraphVisualization.tsx`:

```typescript
'use client';

import { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { GraphData, GraphNode, GraphEdge } from '@/lib/api';

interface Props {
  data: GraphData;
  onNodeClick?: (node: GraphNode) => void;
}

export function GraphVisualization({ data, onNodeClick }: Props) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !data.nodes.length) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = 800;
    const height = 600;

    svg.attr('viewBox', [0, 0, width, height]);

    // Color by type
    const colorScale = d3.scaleOrdinal<string>()
      .domain(['Card', 'Mechanic', 'Role'])
      .range(['#4299e1', '#48bb78', '#ed8936']);

    // Create simulation
    const simulation = d3.forceSimulation(data.nodes as any)
      .force('link', d3.forceLink(data.edges as any)
        .id((d: any) => d.id)
        .distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2));

    // Draw edges
    const link = svg.append('g')
      .selectAll('line')
      .data(data.edges)
      .join('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', 2);

    // Draw nodes
    const node = svg.append('g')
      .selectAll('g')
      .data(data.nodes)
      .join('g')
      .style('cursor', 'pointer')
      .on('click', (_, d) => onNodeClick?.(d))
      .call(d3.drag<any, any>()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on('drag', (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        }));

    node.append('circle')
      .attr('r', d => d.type === 'Card' ? 20 : 15)
      .attr('fill', d => colorScale(d.type));

    node.append('text')
      .text(d => d.label.length > 15 ? d.label.slice(0, 12) + '...' : d.label)
      .attr('text-anchor', 'middle')
      .attr('dy', 30)
      .attr('font-size', 10);

    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      node.attr('transform', (d: any) => `translate(${d.x},${d.y})`);
    });

    return () => simulation.stop();
  }, [data, onNodeClick]);

  return (
    <svg ref={svgRef} className="w-full h-[600px] border rounded bg-gray-50" />
  );
}
```

**Step 2: Create explore page**

Create `frontend/src/app/explore/page.tsx`:

```typescript
'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { graphApi, GraphNode } from '@/lib/api';
import { GraphVisualization } from '@/components/GraphVisualization';

export default function ExplorePage() {
  const [cardName, setCardName] = useState('');
  const [searchInput, setSearchInput] = useState('');
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  const { data: graphData, isLoading } = useQuery({
    queryKey: ['graph', cardName],
    queryFn: () => graphApi.getCardGraph(cardName, { depth: 2 }).then(r => r.data),
    enabled: !!cardName,
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCardName(searchInput);
  };

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Graph Explorer</h1>

      <form onSubmit={handleSearch} className="flex gap-2">
        <input
          type="text"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          placeholder="Enter card name to explore..."
          className="flex-1 p-2 border rounded"
        />
        <button
          type="submit"
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Explore
        </button>
      </form>

      <div className="grid grid-cols-4 gap-4">
        <div className="col-span-3">
          {isLoading && <p>Loading graph...</p>}
          {graphData && (
            <GraphVisualization
              data={graphData}
              onNodeClick={setSelectedNode}
            />
          )}
        </div>

        <div className="p-4 border rounded">
          <h3 className="font-bold mb-2">Node Details</h3>
          {selectedNode ? (
            <div className="space-y-2 text-sm">
              <p><strong>Name:</strong> {selectedNode.label}</p>
              <p><strong>Type:</strong> {selectedNode.type}</p>
              {selectedNode.type === 'Card' && (
                <button
                  onClick={() => setCardName(selectedNode.label)}
                  className="text-blue-500 underline"
                >
                  Explore this card
                </button>
              )}
            </div>
          ) : (
            <p className="text-gray-500 text-sm">Click a node to see details</p>
          )}

          <div className="mt-4">
            <h4 className="font-medium text-sm">Legend</h4>
            <div className="space-y-1 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded-full bg-blue-500" />
                <span>Card</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded-full bg-green-500" />
                <span>Mechanic</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded-full bg-orange-500" />
                <span>Role</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
```

**Step 3: Commit**

```bash
git add frontend/
git commit -m "feat: add graph explorer page with D3 visualization"
```

---

## Task 6: Create Commander Lookup Page

**Files:**
- Create: `frontend/src/app/commander/[name]/page.tsx`

**Step 1: Create commander page**

Create `frontend/src/app/commander/[name]/page.tsx`:

```typescript
'use client';

import { useParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { commandersApi, cardsApi } from '@/lib/api';
import Link from 'next/link';

export default function CommanderPage() {
  const params = useParams();
  const name = decodeURIComponent(params.name as string);

  const { data: commander, isLoading } = useQuery({
    queryKey: ['commander', name],
    queryFn: () => commandersApi.get(name).then(r => r.data),
  });

  const { data: recommendations } = useQuery({
    queryKey: ['recommendations', name],
    queryFn: () => commandersApi.getRecommendations(name, { limit: 50 }).then(r => r.data),
    enabled: !!commander,
  });

  if (isLoading) return <p>Loading...</p>;
  if (!commander) return <p>Commander not found</p>;

  // Group recommendations by role
  const byRole: Record<string, typeof recommendations> = {};
  recommendations?.forEach(rec => {
    const role = rec.roles[0] || 'other';
    if (!byRole[role]) byRole[role] = [];
    byRole[role].push(rec);
  });

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Commander Header */}
      <div className="p-6 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg">
        <h1 className="text-3xl font-bold">{commander.name}</h1>
        <p className="text-xl">{commander.mana_cost} • {commander.type_line}</p>
        <p className="mt-2 opacity-90">{commander.oracle_text}</p>
        <div className="mt-4 flex gap-2">
          {commander.color_identity.map(c => (
            <span key={c} className="px-2 py-1 bg-white/20 rounded">{c}</span>
          ))}
        </div>
      </div>

      {/* Synergies */}
      <div className="p-4 bg-gray-100 rounded">
        <h2 className="font-bold text-lg mb-2">Key Synergies</h2>
        <div className="flex flex-wrap gap-2">
          {commander.synergies?.map(s => (
            <span key={s} className="px-3 py-1 bg-green-200 rounded-full text-sm">
              {s}
            </span>
          ))}
        </div>
      </div>

      {/* Start Building */}
      <Link
        href={`/build?commander=${encodeURIComponent(commander.name)}`}
        className="block w-full py-3 bg-blue-500 text-white text-center rounded-lg hover:bg-blue-600"
      >
        Start Building with {commander.name}
      </Link>

      {/* Recommendations by Role */}
      <div>
        <h2 className="font-bold text-lg mb-4">Recommended Cards by Role</h2>
        <div className="grid grid-cols-2 gap-4">
          {Object.entries(byRole).map(([role, cards]) => (
            <div key={role} className="p-4 border rounded">
              <h3 className="font-medium capitalize mb-2">
                {role.replace('_', ' ')} ({cards?.length})
              </h3>
              <ul className="space-y-1 text-sm">
                {cards?.slice(0, 8).map(card => (
                  <li key={card.name} className="flex justify-between">
                    <span>{card.name}</span>
                    <span className="text-gray-500">{card.mana_cost}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

**Step 2: Update home page with commander search**

Update `frontend/src/app/page.tsx`:

```typescript
'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { commandersApi } from '@/lib/api';
import Link from 'next/link';

export default function Home() {
  const [search, setSearch] = useState('');

  const { data: commanders } = useQuery({
    queryKey: ['commanders', search],
    queryFn: () => commandersApi.list({ search, limit: 20 }).then(r => r.data),
    enabled: search.length >= 2,
  });

  return (
    <div className="max-w-2xl mx-auto space-y-8 py-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">MTG Commander Deck Builder</h1>
        <p className="text-gray-600">
          Build optimized Commander decks with AI-powered recommendations
        </p>
      </div>

      <div>
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search for a commander to get started..."
          className="w-full p-4 text-lg border-2 rounded-lg focus:border-blue-500 outline-none"
        />

        {commanders && commanders.length > 0 && (
          <ul className="mt-2 border rounded-lg divide-y">
            {commanders.map(c => (
              <li key={c.name}>
                <Link
                  href={`/commander/${encodeURIComponent(c.name)}`}
                  className="block p-4 hover:bg-gray-50"
                >
                  <span className="font-medium">{c.name}</span>
                  <span className="ml-2 text-gray-600">{c.mana_cost}</span>
                  <span className="block text-sm text-gray-500">{c.type_line}</span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="grid grid-cols-3 gap-4 text-center">
        <Link href="/build" className="p-6 border rounded-lg hover:bg-gray-50">
          <h2 className="font-bold text-lg">Deck Builder</h2>
          <p className="text-sm text-gray-600">Build a new deck</p>
        </Link>
        <Link href="/analyze" className="p-6 border rounded-lg hover:bg-gray-50">
          <h2 className="font-bold text-lg">Deck Analyzer</h2>
          <p className="text-sm text-gray-600">Analyze existing deck</p>
        </Link>
        <Link href="/explore" className="p-6 border rounded-lg hover:bg-gray-50">
          <h2 className="font-bold text-lg">Graph Explorer</h2>
          <p className="text-sm text-gray-600">Explore card synergies</p>
        </Link>
      </div>
    </div>
  );
}
```

**Step 3: Commit**

```bash
git add frontend/
git commit -m "feat: add commander lookup page and home page"
```

---

## Task 7: Final Verification and Push

**Step 1: Verify frontend builds**

```bash
cd frontend
npm run build
```

Expected: Build completes without errors

**Step 2: Test with API**

1. Start API: `uvicorn api.main:app --port 8000`
2. Start frontend: `cd frontend && npm run dev`
3. Visit http://localhost:3000
4. Test each page

**Step 3: Push changes**

```bash
cd ..
git add frontend/
git commit -m "feat: complete frontend implementation"
git push origin feature/knowledge-graph-implementation
```

---

## Verification Checklist

After completing Phase 5:

- [ ] Frontend builds without errors
- [ ] Home page loads with commander search
- [ ] Deck Builder shows recommendations
- [ ] Card search works with filters
- [ ] Deck list updates when adding/removing cards
- [ ] Deck Analyzer parses decklist
- [ ] Analysis shows role coverage
- [ ] Graph Explorer renders D3 visualization
- [ ] Node clicking works
- [ ] Commander lookup shows details
- [ ] Navigation between pages works
- [ ] All tests pass
- [ ] Changes committed and pushed
