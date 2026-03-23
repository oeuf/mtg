# Code Review Findings — MTG Commander Project
**Date:** 2026-02-22
**Branch:** feature/frontend
**Passes completed:** 5 (Bugs, Security, Architecture, Type Safety, Test Coverage)

---

## Consolidated Findings (Deduplicated & Prioritized)

### CRITICAL

| ID | Source | File | Issue |
|----|--------|------|-------|
| F-C1 | P3-002, P5-001 | `api.ts:79`, `cards.py` | `cardsAPI.getByRole` calls `/api/cards/by-role/{role}` — endpoint does not exist. "By Role" tab is silently broken (404 at runtime). |
| F-C2 | P1-001 | `commanders.py:65-77` | `GET /commanders/{name}` returns only 10 of 17 required fields — missing `keywords`, `is_legendary`, `functional_categories`, `mechanics`, `themes`, `archetype`, `popularity_score`. |
| F-C3 | P1-002 | `Header.tsx:7,20` | "Deck Builder" nav link points to `/commanders` (duplicate); also creates duplicate React `key={to}` collision. |
| F-C4 | P2-001 | `graph.py:108` | `str(e)` in health endpoint leaks Neo4j URI, auth errors, internal topology. |
| F-C5 | P3-001 | All 4 routers | Service layer completely bypassed — all routers query Neo4j directly; 3 service classes tested but never called. |
| F-C6 | P3-003 | `synergy_service.py:5` | Imports `src.synergy.card_synergies` — couples API layer to pipeline layer; will raise `ModuleNotFoundError` at runtime. |

---

### HIGH

| ID | Source | File | Issue |
|----|--------|------|-------|
| F-H1 | P2-002, P3-004, P4-007 | `decks.py:14,61` | Both POST endpoints accept raw `dict` — no Pydantic validation, causes 500s on malformed input. `BuildDeckRequest` model exists but unused. |
| F-H2 | P2-003 | `config.py:11` | Default password `"password"` with no startup validation. |
| F-H3 | P1-003 | `api.ts:40` vs `commanders.py:109` | `top_k` param mismatch — backend reads `limit`; custom counts silently ignored. |
| F-H4 | P1-005 | `RecommendationsPanel.tsx:72,114` | `.toFixed(2)` on `synergy_score`/`score` — can be `null` from Neo4j → runtime `TypeError`. |
| F-H5 | P1-006 | `CardDetailPage.tsx:77,79` | `card.color_identity.map()` without null guard → crashes on colorless cards. |
| F-H6 | P4-001, P4-002 | `CardSearchPage.tsx:65-66`, `FilterPanel.tsx:11-13` | `as unknown as` double-cast + `Record<string, unknown>` props — erases all type safety at FilterPanel boundary. |
| F-H7 | P4-003 | `commander.ts:6-7`, `commander.py:13-14` | `power`/`toughness` typed as `number\|null` but MTG has `"*"`, `"1+*"` string values. |
| F-H8 | P2-005 | `cards.py:66-93`, `commanders.py:28-53` | Dynamic WHERE clause via f-string — structurally injectable pattern (values parameterized now, but one refactor away from injection). |
| F-H9 | P3-005 | `FilterPanel.tsx:7`, `RecommendationsPanel.tsx:14` | `ROLES` constant duplicated with **different values** (7 vs 5 items) — user sees inconsistent roles. |
| F-H10 | P3-006, P3-008 | 3 frontend files | `colorVariantMap` duplicated 3×, `COLORS` duplicated 2× — divergence risk. |
| F-H11 | P2-006 | `connection.py:12` | Neo4j URI printed to stdout unconditionally — leaks internal network topology in production logs. |
| F-H12 | P2-007, P2-008, P2-009 | `connection.py:50`, `loaders.py:227,270`, `gds_scoring.py:23` | 4 bare `except Exception: pass` blocks — silently hide auth failures, network errors, corrupt graph data. |
| F-H13 | P3-004 | `models/` | 9 Pydantic models defined but never used as router annotations — no request validation, no OpenAPI schema. |
| F-H14 | P5-002 | `conftest.py:93` vs `test_services_query.py:13` | `mock_connection` fixture duplicated with different implementations — unit tests use weaker mock. |
| F-H15 | P5-003 | `main.py:59-66` | Neo4j exception handlers (`ServiceUnavailable`, `SessionExpired`) have zero tests. |
| F-H16 | P5-004 | `graph.py:99-109` | Health endpoint error branch untested — 503 path never exercised. |
| F-H17 | P5-010 | `test_api_cards.py` | Card endpoint success paths untested — only 404 path tested; flat-object regression (commit `48b5726`) happened before with no test catching it. |

---

### MEDIUM

| ID | Source | File | Issue |
|----|--------|------|-------|
| F-M1 | P2-010 | `main.py:30-36` | `allow_methods=["*"]` + `allow_credentials=True` — overly permissive CORS. |
| F-M2 | P2-013 | `commanders.py:17` | `limit` allows up to 5000 — DoS vector bypassing rate limiter. |
| F-M3 | P2-014 | `cards.py:21` | `text_search` has no `max_length` — DoS via large CONTAINS operations. |
| F-M4 | P3-009 | `decks.py:22` | Uses `Card` label instead of `Commander` label for deck building — accepts non-commander-legal cards. |
| F-M5 | P3-007, P3-010 | `dependencies.py`, `services/` | Two incompatible Neo4j connection abstractions — structurally blocks service wiring. |
| F-M6 | P4-004, P4-005 | `connection.py:19`, `queries.py:83` | `parameters: dict = None` and `color_identity: list[str] = None` — wrong type annotations for nullable defaults. |
| F-M7 | P4-008 | `card.py`, `deck.py`, `synergy_service.py` | Deprecated `typing.List`/`Dict`/`Tuple` — inconsistent with modern `list`/`dict` used elsewhere. |
| F-M8 | P4-009 | `synergy_service.py:11`, `query_service.py:9` | Connection arguments untyped (`conn`, `connection` with no annotation). |
| F-M9 | P1-004 | `query_service.py:133` | Returns `{"error": ...}` dict instead of raising — 200 OK with error body if wired to router. |
| F-M10 | P5-005 | `test_api_decks.py` | `analyze_deck` only tested with 40 identical cards — missing empty input, missing fields, float CMC edge cases. |
| F-M11 | P5-007 | `CardDetailPage.test.tsx` | No error state test — regression in error branch undetectable. |
| F-M12 | P5-008 | `recommendations-panel.test.tsx` | "By Role" tab functionality entirely untested. |
| F-M13 | P5-009 | `test_middleware.py` | CORS test only checks allowed origin — never verifies disallowed origins are rejected. |
| F-M14 | P5-017 | `test_api_decks.py:9` | `test_build_deck_shell_returns_37_cards` actually tests 404, not 200 — misleading test name masks missing coverage. |
| F-M15 | P2-012 | `cards.py:147`, `commanders.py:76` | User-supplied name echoed verbatim in 404 detail — reflected content injection risk. |
| F-M16 | P5-006 | `api.test.ts` | `autocomplete` and `getCombos` API functions have no tests. |

---

### LOW

| ID | Source | File | Issue |
|----|--------|------|-------|
| F-L1 | P4-015 | `CardDetailPage.tsx:80` | `as 'default'` cast on mana variant suppresses missing-variant compile error. |
| F-L2 | P4-016 | `inference_engine.py:10` | `analyze_commander` missing return type annotation. |
| F-L3 | P5-019 | `types.test.ts` | Test file only validates JS object assignment — TypeScript already enforces this at compile time; tests add no value. |
| F-L4 | P2-011 | `dependencies.py:40-47` | Session acquisition has no error handling — loses context on pool exhaustion. |
| F-L5 | P5-016 | `layout.test.tsx:30` | Test asserts "Deck Builder" link points to `/deck-builder/select` — conflicts with actual implementation. |

---

## Fix Plan (5 Batches)

### Batch 1: Critical + High Runtime Bugs (1 agent, ~45 min)
Fix things that actively break functionality at runtime.

| Fix | File | Change |
|-----|------|--------|
| B1-1 | `backend/app/routers/commanders.py:65-77` | Add missing 7 fields to `GET /commanders/{name}` RETURN clause |
| B1-2 | `backend/app/routers/commanders.py:109` | Rename `limit` param to `top_k` (or update frontend to send `limit`) |
| B1-3 | `backend/app/routers/cards.py` | Implement missing `GET /cards/by-role/{role}` endpoint (before `/{name}`) |
| B1-4 | `frontend/src/components/deck/RecommendationsPanel.tsx:72,114` | Add `?? 0` before `.toFixed(2)` for null score safety |
| B1-5 | `frontend/src/features/cards/CardDetailPage.tsx:77,79` | Add `?? []` null guard on `color_identity` |
| B1-6 | `frontend/src/components/layout/Header.tsx:3-9` | Fix duplicate nav link — use unique `key={label}` and correct "Deck Builder" path |

**Verify:** `pnpm build && pnpm test` + `PYTHONPATH=backend:. pytest backend/tests/ -v`
**Commit:** `fix: runtime bugs - missing endpoint, null guards, nav link, field mismatches`

---

### Batch 2: Security (2 parallel agents — backend / pipeline)

**Agent A — backend/app/:**

| Fix | File | Change |
|-----|------|--------|
| B2-1 | `graph.py:108` | Replace `str(e)` with static message; log error server-side |
| B2-2 | `decks.py:14,61` | Replace `request: dict` with `BuildDeckRequest`; create `AnalyzeDeckRequest` Pydantic model |
| B2-3 | `main.py:30-36` | Restrict `allow_methods=["GET","POST"]`, remove `allow_credentials=True`; make origins configurable |
| B2-4 | `commanders.py:17` | Lower `limit` max from 5000 to 200 |
| B2-5 | `cards.py:21` | Add `max_length=200` to `text_search` |

**Agent B — src/:**

| Fix | File | Change |
|-----|------|--------|
| B2-6 | `connection.py:12` | Replace `print(URI)` with `logging.debug("Connected to Neo4j")` |
| B2-7 | `connection.py:50`, `loaders.py:227,270`, `gds_scoring.py:23` | Replace bare `except: pass` with specific catches + `logger.error()` |

**Verify:** `PYTHONPATH=backend:. pytest backend/tests/ -v`
**Commit:** `fix: security hardening - error sanitization, input validation, logging`

---

### Batch 3: Type Safety (2 parallel agents — frontend / backend)

**Agent A — frontend/src/:**

| Fix | File | Change |
|-----|------|--------|
| B3-1 | `FilterPanel.tsx:11-13` | Replace `Record<string, unknown>` with `CardSearchFilters` typed props |
| B3-2 | `CardSearchPage.tsx:65-66` | Remove `as unknown as` casts (now that FilterPanel accepts proper types) |
| B3-3 | `commander.ts:6-7` | Change `power`/`toughness` from `number\|null` to `string\|number\|null` |
| B3-4 | `CardDetailPage.tsx:80` | Add `BadgeVariant` type; remove `as 'default'` cast |

**Agent B — backend/app/ + src/:**

| Fix | File | Change |
|-----|------|--------|
| B3-5 | `commander.py:13-14` | Change `power`/`toughness` to `Optional[Union[int,str]]`, remove `ge=0` |
| B3-6 | `connection.py:19` | Change `parameters: dict = None` to `parameters: Optional[dict] = None` |
| B3-7 | `queries.py:83-84` | Change `color_identity: list[str] = None` to `Optional[list[str]] = None` |
| B3-8 | `card.py`, `deck.py`, `synergy_service.py` | Replace deprecated `typing.List`/`Dict`/`Tuple` with built-in generics |
| B3-9 | `query_service.py:9`, `synergy_service.py:11` | Add `Neo4jConnection` type annotation to constructor params |

**Verify:** `pnpm build && pnpm test` + `PYTHONPATH=backend:. pytest backend/tests/ -v`
**Commit:** `fix: type safety - proper annotations, remove unsafe casts, fix nullable types`

---

### Batch 4: Architecture & DRY (2 parallel agents — frontend / backend)

**Agent A — frontend/src/:**

| Fix | File | Change |
|-----|------|--------|
| B4-1 | Create `frontend/src/constants/mtg.ts` | Extract `MTG_COLORS`, `CARD_ROLES` (7 items), `colorVariantMap`/`colorToVariant` |
| B4-2 | `CardCard.tsx`, `CommanderCard.tsx`, `CommanderSelectPage.tsx`, `FilterPanel.tsx`, `RecommendationsPanel.tsx` | Import from shared constants; unify ROLES to 7-item list |

**Agent B — backend/app/:**

| Fix | File | Change |
|-----|------|--------|
| B4-3 | `decks.py:22` | Change `MATCH (c:Card ...)` to `MATCH (c:Commander ...)` for deck building |
| B4-4 | `query_service.py:133` | Change `return {"error": ...}` to `raise ValueError(...)` |
| B4-5 | `commanders.py` (all Neo4j calls) | Standardize param passing to use `{"name": name}` dict (not `name=name` kwargs) |

**Verify:** `pnpm build && pnpm test` + `PYTHONPATH=backend:. pytest backend/tests/ -v`
**Commit:** `refactor: shared constants, standardize backend patterns`

---

### Batch 5: Test Coverage (2 parallel agents — frontend / backend)

**Agent A — frontend/src/:**

| Fix | File | Change |
|-----|------|--------|
| B5-1 | `CardDetailPage.test.tsx` | Add error state test; add `by-role` 404 test |
| B5-2 | `recommendations-panel.test.tsx` | Add "By Role" tab tests: role button click, data fetch, null score rendering |
| B5-3 | `layout.test.tsx:30` | Fix assertion to match actual Header implementation |
| B5-4 | `api.test.ts` | Add tests for `autocomplete` and `getCombos` |

**Agent B — backend/tests/:**

| Fix | File | Change |
|-----|------|--------|
| B5-5 | `test_services_query.py:13` | Remove duplicate `mock_connection` fixture — use conftest's |
| B5-6 | `test_middleware.py` | Add `ServiceUnavailable`/`SessionExpired` handler tests; add disallowed-origin CORS test |
| B5-7 | `test_api_graph.py` | Add health endpoint error branch test (503 path) |
| B5-8 | `test_api_cards.py` | Add success-path test verifying flat response object (prevent commit `48b5726` regression) |
| B5-9 | `test_api_decks.py` | Fix misleading test name; add success-path build-shell test; add analyze edge cases |

**Verify:** `pnpm test` + `PYTHONPATH=backend:. pytest backend/tests/ -v`
**Commit:** `test: improve coverage - error paths, missing endpoints, fixture dedup`

---

## Total Finding Count

| Severity | Count |
|----------|-------|
| Critical | 6 |
| High | 17 |
| Medium | 16 |
| Low | 5 |
| **Total** | **44** |
