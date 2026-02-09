# MTG Commander Web Application - Updated Implementation Plan

## Executive Summary

**Goal:** Expand the production-ready Neo4j knowledge graph into a full-stack web application using Agent Teams, test-driven development, and Claude Code plugins.

**Timeline:** 8 weeks across 7 milestones with parallel agent work

**Team Structure:** Multi-agent with specialized roles (see Agent Teams section below)

**Innovation:** TDD-first approach with superpowers integration, automated code review, and collaborative feature development

---

## Part 1: Agent Teams & Model Assignments

### Team Composition

```
┌─────────────────────────────────────────────────────────────────┐
│                      PROJECT LEADERSHIP                          │
│  Lead Architect (Opus 4.6) - Decision maker, design review      │
│  Tech Lead (Sonnet 4.5) - Implementation oversight, mentoring   │
└─────────────────────────────────────────────────────────────────┘
                                 ↓
┌──────────────────────┬──────────────────────┬──────────────────────┐
│   BACKEND TEAM       │   FRONTEND TEAM      │   QA & DEVOPS TEAM   │
├──────────────────────┼──────────────────────┼──────────────────────┤
│ Backend Dev (S 4.5)  │ Frontend Dev (S 4.5) │ QA Lead (O 4.6)      │
│ API Dev (S 4.5)      │ UI/UX Dev (S 4.5)    │ DevOps (S 4.5)       │
│ Data Scientist (H)   │ Frontend Tests (H)   │ Test Engineer (H)    │
└──────────────────────┴──────────────────────┴──────────────────────┘

Legend: O=Opus 4.6, S=Sonnet 4.5, H=Haiku 4.5
```

### Detailed Role Assignments

#### Leadership Layer

**1. Lead Architect (Opus 4.6)**
- **Responsibilities:**
  - System design & architecture decisions
  - Code review at milestone completion
  - Resolve design conflicts between teams
  - Validate plan adherence
  - Make trade-off decisions

- **Tools/Skills:**
  - `superpowers:code-reviewer` - Final approval of milestones
  - `feature-dev:code-architect` - Design guidance for complex features
  - `pr-review-toolkit:code-reviewer` - PR validation
  - `pr-review-toolkit:type-design-analyzer` - Ensure type safety across stack

- **Interactions:** Receives summaries from team leads, provides weekly guidance

**2. Tech Lead (Sonnet 4.5)**
- **Responsibilities:**
  - Mentor backend/frontend leads
  - Ensure consistency across teams
  - Handle cross-team integration
  - Build quality standards (linting, testing patterns)
  - Troubleshoot blockers

- **Tools/Skills:**
  - `pr-review-toolkit:code-simplifier` - Refactor and simplify code
  - `feature-dev:code-explorer` - Understand existing patterns
  - `hookify:conversation-analyzer` - Learn from mistakes, prevent recurrence

- **Interactions:** Daily stand-up with team leads, code reviews before Lead Architect

---

#### Backend Team (Weeks 1-4, then 6-7)

**3. Backend Developer - APIs (Sonnet 4.5)**
- **Sprint 1 (Week 1-2): Milestone 1 - Foundation & Backend API**
  - Create FastAPI project structure
  - Implement Neo4j connection & dependency injection
  - Build Pydantic models for all domain objects
  - Create 15+ core API endpoints (commanders, cards, decks, graph)

- **Sprint 2 (Week 3-4): Milestone 3 - Enhanced Synergy APIs**
  - Implement synergy computation endpoints
  - Add recommendation scoring endpoints
  - Create deck analysis endpoints

- **Tools/Skills:**
  - `feature-dev:code-architect` - API design (Week 1 kickoff)
  - `pr-review-toolkit:silent-failure-hunter` - Error handling review
  - `superpowers:test-driven-development` - TDD for endpoints
  - `agent-sdk-dev:agent-sdk-verifier-py` - Verify Python quality

- **Testing Strategy:** Write tests BEFORE implementation (see TDD section)

---

**4. Backend Developer - Services (Sonnet 4.5)**
- **Sprint 1 (Week 1-2): Milestone 1 - Service Layer**
  - Wrap existing `DeckbuildingQueries` class methods
  - Create `QueryService` with proper error handling
  - Implement `SynergyService` wrapping `CardSynergyEngine`
  - Create `RecommendationService` for 7-dimensional scoring

- **Parallel Task (Week 3-4): Refactor as needed**
  - Performance optimization of frequently called queries
  - Add caching layer design

- **Tools/Skills:**
  - `feature-dev:code-explorer` - Understand existing query patterns
  - `pr-review-toolkit:code-simplifier` - Simplify wrapper logic
  - `superpowers:test-driven-development` - TDD for services

---

**5. Data Scientist / ML Engineer (Haiku 4.5)**
- **Parallel Task (Weeks 2-3): Milestone 2.5 - ML Optimization**
  - Validate embedding quality (FastRP 128-dim)
  - Optimize kNN similarity scoring
  - Analyze Leiden community quality
  - Create "explain recommendation" feature

- **Tools/Skills:**
  - `feature-dev:code-explorer` - Understand existing ML pipeline
  - `superpowers:verification-before-completion` - Validate metrics

- **Deliverable:** ML metrics report + optimized query functions

---

#### Frontend Team (Weeks 2-6)

**6. Frontend Developer - Architecture (Sonnet 4.5)**
- **Sprint 1 (Week 2-3): Milestone 2 - Foundation & Routing**
  - Initialize Vite + React + TypeScript project
  - Set up Tailwind + component library
  - Implement React Router with all routes
  - Create API client layer (Axios + React Query)

- **Ongoing (Weeks 3-6):** Architecture oversight for feature teams

- **Tools/Skills:**
  - `feature-dev:code-architect` - Design component hierarchy (Week 2 kickoff)
  - `pr-review-toolkit:type-design-analyzer` - Ensure TypeScript quality
  - `superpowers:test-driven-development` - TDD for architecture

---

**7. Frontend Developer - UI/UX (Sonnet 4.5)**
- **Sprint 1 (Week 2-3): Milestone 2 - Design System**
  - Create Tailwind theme (mana colors, brand colors)
  - Build base component library:
    - Button (primary, secondary, ghost)
    - Card, Input, Select, Checkbox, Badge
    - Layout components (Header, Sidebar, Grid)
  - Implement responsive design patterns
  - Create error boundary & loading skeletons

- **Sprint 2 (Weeks 3-6): Feature UI**
  - Implement designs for each feature milestone
  - Ensure consistency across all features

- **Tools/Skills:**
  - `pr-review-toolkit:comment-analyzer` - Review design documentation
  - `superpowers:test-driven-development` - TDD for components
  - `agent-sdk-dev:agent-sdk-verifier-ts` - TS quality verification

---

**8. Frontend Developer - Deck Builder (Sonnet 4.5)**
- **Sprint 2 (Week 3-4): Milestone 3 - Deck Builder**
  - Build commander selection page
  - Implement deck builder main interface
  - Create deck list organization (by type)
  - Build recommendations panel with tabs
  - Implement mana curve visualization
  - Create deck statistics display

- **State Management:** Zustand store for deck state

- **Tools/Skills:**
  - `superpowers:test-driven-development` - TDD for components
  - `pr-review-toolkit:silent-failure-hunter` - Catch state bugs
  - `feature-dev:code-explorer` - Understand card data patterns

---

**9. Frontend Developer - Search (Sonnet 4.5)**
- **Sprint 3 (Week 4-5): Milestone 4 - Card Search**
  - Build advanced card search page
  - Implement all 7 filter types (color, type, CMC, rarity, mechanic, role, text)
  - Create filter state management
  - Implement real-time search with debouncing
  - Build pagination UI

- **Tools/Skills:**
  - `superpowers:test-driven-development` - TDD for filters
  - `pr-review-toolkit:silent-failure-hunter` - Edge case handling

---

**10. Frontend Developer - Features (Sonnet 4.5)**
- **Sprint 4 (Week 5-6): Milestone 5 - Similarity & Synergy**
  - Build card detail page
  - Implement similar cards section
  - Create synergy visualization (7-dim breakdown)
  - Build combo finder UI

- **Sprint 5 (Week 6-7): Milestone 6 - Collection**
  - Implement collection management page
  - Create collection filters & search
  - Build collection statistics
  - Implement CSV export/import

- **Tools/Skills:**
  - `superpowers:test-driven-development` - TDD for all features
  - `pr-review-toolkit:code-simplifier` - Refactor complex logic

---

#### QA & DevOps Team (Weeks 4-8, then intensifies Week 7-8)

**11. QA Lead (Opus 4.6)**
- **Responsibilities:**
  - Design test strategy for entire project
  - Define test coverage targets (80%+ backend, 70%+ frontend)
  - Review test quality from all teams
  - Create E2E test scenarios
  - Oversee production readiness checklist

- **Tools/Skills:**
  - `pr-review-toolkit:code-reviewer` - Validate test implementation
  - `pr-review-toolkit:pr-test-analyzer` - Ensure adequate test coverage
  - `superpowers:verification-before-completion` - Pre-deploy validation

- **Deliverable:** Test dashboard + coverage reports

---

**12. Test Engineer (Haiku 4.5)**
- **Weeks 4-5 (Parallel to feature development):**
  - Write backend integration tests (pytest)
  - Write frontend unit tests (Vitest)
  - Create API contract tests

- **Weeks 6-7:**
  - Write E2E tests (Playwright)
  - Load testing for search/synergy endpoints
  - Accessibility testing (WCAG 2.1 AA)

- **Tools/Skills:**
  - `superpowers:test-driven-development` - Collaborate with feature teams on TDD
  - `pr-review-toolkit:pr-test-analyzer` - Validate coverage
  - `feature-dev:code-explorer` - Understand features to test

- **Testing Stack:**
  - Backend: pytest, pytest-asyncio, httpx
  - Frontend: Vitest, React Testing Library, @testing-library/jest-dom
  - E2E: Playwright
  - Coverage: coverage.py (Python), nyc (TypeScript)

---

**13. DevOps Engineer (Sonnet 4.5)**
- **Sprint 1 (Week 1-2): Initial Setup**
  - Create Dockerfiles (backend, frontend)
  - Update docker-compose.yml with all services
  - Set up environment configuration (.env.example)
  - Create development startup scripts

- **Sprint 2-3 (Weeks 3-5): Monitoring & CI/CD**
  - Create GitHub Actions CI workflow
  - Add pre-commit hooks (Biome, pytest)
  - Set up logging & error tracking
  - Create production deployment guide

- **Sprint 3 (Week 7-8): Production Hardening**
  - Optimize Docker images (multi-stage builds)
  - Configure production docker-compose
  - Set up health checks
  - Create backup/restore procedures

- **Tools/Skills:**
  - `superpowers:verification-before-completion` - Validate deployment
  - `pr-review-toolkit:code-simplifier` - Simplify scripts
  - `agent-sdk-dev:agent-sdk-verifier-py` - Verify Python setup
  - `agent-sdk-dev:agent-sdk-verifier-ts` - Verify Node setup

---

### Team Workflow & Communication

**Daily Standup (15 min):**
- Tech Lead runs standup with team leads only
- Each lead reports: progress, blockers, next 24h plan
- Tech Lead escalates to Lead Architect if needed

**Weekly Planning (Friday 30 min):**
- Lead Architect + Tech Lead + all leads
- Review milestone progress
- Adjust priorities if needed
- Plan next week's work

**Code Review Cadence:**
- Features: Tech Lead (initial) → Lead Architect (final)
- Tests: QA Lead (review) → Tech Lead (approval)
- Docs: Tech Lead (review)

**Milestone Completion:**
- All feature PRs merged by team
- QA Lead validates test coverage
- Tech Lead runs simplifier/reviewer agents
- Lead Architect does final review
- Mark milestone as complete

---

## Part 2: Test-Driven Development Strategy

### TDD Workflow (All Teams)

**Phase 1: Write Tests First**
```
1. Team lead writes test spec for feature
2. Developers write failing tests BEFORE implementation
3. Tests fail (Red phase)
```

**Phase 2: Implement Feature**
```
4. Developers implement feature code
5. Run tests → tests pass (Green phase)
6. Tech Lead runs code-simplifier agent
7. Tests still pass (Refactor phase)
```

**Phase 3: Validate**
```
8. Tech Lead runs code-reviewer agent
9. QA Lead reviews test quality with pr-test-analyzer
10. Lead Architect approves
```

### Backend Testing Structure

**File:** `backend/tests/conftest.py`
```python
# Shared fixtures for Neo4j testing
# Mock Neo4j session
# Seed test data
```

**Test Organization:**
```
backend/tests/
├── conftest.py                    # Shared fixtures
├── unit/
│   ├── test_models.py             # Pydantic model validation
│   ├── test_services.py           # Business logic
│   └── test_validators.py         # Input validation
├── integration/
│   ├── test_api_commanders.py      # Endpoint tests
│   ├── test_api_cards.py
│   ├── test_api_decks.py
│   ├── test_api_graph.py
│   └── test_api_collections.py
└── e2e/
    ├── test_deck_builder_flow.py   # Full workflows
    └── test_search_flow.py
```

**Minimum Coverage Targets:**
- Models: 95% (validation is critical)
- Services: 85% (business logic)
- Routers: 80% (API endpoints, some integration)
- Overall: 80%+

**Command:** `pytest --cov=app --cov-report=html`

---

### Frontend Testing Structure

**Test Organization:**
```
frontend/src/
├── __tests__/
│   ├── unit/
│   │   ├── components/
│   │   │   └── Button.test.tsx
│   │   ├── hooks/
│   │   │   └── useCardSearch.test.ts
│   │   └── services/
│   │       └── api.test.ts
│   ├── integration/
│   │   ├── DeckBuilder.test.tsx
│   │   ├── CardSearch.test.tsx
│   │   └── Collection.test.tsx
│   └── e2e/
│       └── *.spec.ts              # Playwright tests
```

**Minimum Coverage Targets:**
- Components: 70%
- Hooks: 80%
- Services: 85%
- Overall: 70%+

**Commands:**
```bash
pnpm test              # Vitest
pnpm test:coverage     # Coverage report
pnpm test:e2e          # Playwright
```

---

### Test-First Example (Deck Builder)

**Step 1: Write Failing Test**
```python
# backend/tests/integration/test_api_decks.py
def test_build_deck_shell_returns_37_cards(async_client, muldrotha_commander):
    """Test deck building shell for Muldrotha."""
    response = await async_client.post(
        "/api/decks/build-shell",
        json={"commander": "Muldrotha, the Gravetide"}
    )

    assert response.status_code == 200
    deck = response.json()
    assert len(deck["cards"]) == 37
    assert deck["commander"]["name"] == "Muldrotha, the Gravetide"
    assert all(card["cmc"] <= 4 for card in deck["cards"])
```

**Step 2: Test Fails (RED)**
```
FAILED test_api_decks.py::test_build_deck_shell_returns_37_cards - 404 Not Found
```

**Step 3: Implement Endpoint**
```python
# backend/app/routers/decks.py
@router.post("/api/decks/build-shell")
async def build_deck_shell(
    request: BuildDeckRequest,
    session: Session = Depends(get_neo4j_session)
):
    """Build initial deck shell using 8x8 method."""
    return deck_service.build_shell(session, request.commander)
```

**Step 4: Test Passes (GREEN)**
```
PASSED test_api_decks.py::test_build_deck_shell_returns_37_cards
```

**Step 5: Code Review & Simplification**
- Tech Lead runs `superpowers:code-simplifier`
- Removes unnecessary variables, simplifies logic
- Tests still pass ✓

**Step 6: Final Approval**
- Lead Architect approves
- Feature merged

---

### TDD Benefits Tracked

**In each milestone completion:**
1. **Test Coverage Report** - % of code covered
2. **Bug Metrics** - Bugs found in testing vs. production
3. **Development Time** - TDD often faster (less debugging)
4. **Code Quality** - Cyclomatic complexity, maintainability index

---

## Part 3: Available Plugins & Skills Integration

### Claude Code Plugins in Use

#### 1. **Claude Code Guide** (Throughout project)
- Question answering about Claude Code features, SDK, API
- Used for: Understanding Claude API capabilities during development
- **When to trigger:** When team asks "Can Claude...", "How do I..."

#### 2. **PR Review Toolkit** (Weeks 2-8)
Multiple specialized reviewers:

**a) code-reviewer**
- After each major feature completion
- Checks: Style violations, logic errors, security issues
- Triggered: After feature branch completed

**b) silent-failure-hunter**
- After implementing error handling
- Checks: Missing error cases, inadequate fallbacks
- Triggered: After auth, payments, critical paths

**c) code-simplifier**
- After GREEN phase (tests passing)
- Refactors: Variable names, function length, complexity
- Triggered: Before final code review

**d) comment-analyzer**
- Before PR merge
- Checks: Comment accuracy, outdated docs
- Triggered: During final review

**e) pr-test-analyzer**
- Before marking feature complete
- Checks: Test coverage, edge case coverage
- Triggered: QA validation phase

**f) type-design-analyzer**
- When adding new types/models
- Checks: Type safety, invariant expression
- Triggered: After data model changes

---

#### 3. **Feature Dev Agents** (Weeks 1-2, then 5-6)
Available when complexity requires deep analysis:

**a) code-architect** (Used with Opus 4.6)
- Design decisions for complex features
- Triggers: Deck builder architecture (W3), Search filter design (W4)
- Agent: `feature-dev:code-architect`

**b) code-explorer** (Used with Sonnet 4.5)
- Understand existing codebase before wrapping
- Triggers: Week 1 - explore DeckbuildingQueries, CardSynergyEngine
- Agent: `feature-dev:code-explorer`

**c) code-reviewer** (Used with Sonnet 4.5)
- Quick code quality checks during development
- Triggers: After each component implemented
- Agent: `feature-dev:code-reviewer`

---

#### 4. **Agent SDK Verifiers** (Weeks 1 & 2 during setup)

**a) agent-sdk-verifier-py**
- Verify Python project structure post-setup
- Checks: Dependencies, configs, entry points
- Triggered: After backend Dockerfile/requirements.txt created

**b) agent-sdk-verifier-ts**
- Verify TypeScript project post-setup
- Checks: tsconfig, build config, type safety
- Triggered: After frontend Vite setup complete

---

#### 5. **Superpowers Agents** (Throughout development)

**a) test-driven-development**
- Guide teams on TDD best practices
- Implement test specs and test examples
- Triggered: Start of each feature milestone
- Usage: Each team lead runs this before feature development begins

**b) verification-before-completion**
- QA-focused agent to validate features
- End-to-end testing, manual verification
- Triggered: Before milestone completion
- Usage: QA Lead uses this before marking milestone done

**c) subagent-driven-development**
- Coordinate parallel agents on related tasks
- Triggered: When multiple teams work same domain
- Usage: For coordinating backend + frontend feature pairs

---

#### 6. **Hookify Conversation Analyzer** (Weekly, Fridays)
- Analyze conversation to prevent repeated mistakes
- Learn from: TDD mistakes, design errors, integration issues
- Triggered: Weekly team retrospective
- Output: Prevention hooks for common errors

---

### Plugin Usage Timeline

```
Week 1:
  - agent-sdk-verifier-py (backend setup)
  - code-explorer (understand existing code)
  - code-architect (API design)
  - test-driven-development (TDD kickoff)

Week 2:
  - agent-sdk-verifier-ts (frontend setup)
  - pr-review-toolkit:code-reviewer (backend review)
  - pr-review-toolkit:type-design-analyzer (models review)
  - test-driven-development (TDD for components)

Week 3:
  - code-architect (deck builder design)
  - superpowers:test-driven-development (start deck builder TDD)
  - pr-review-toolkit:code-simplifier (simplify backend code)
  - pr-review-toolkit:silent-failure-hunter (review error handling)

Week 4:
  - code-architect (search filter design)
  - pr-review-toolkit:pr-test-analyzer (verify test coverage)
  - pr-review-toolkit:code-simplifier (refactor components)
  - feature-dev:code-reviewer (quick quality checks)

Week 5:
  - pr-review-toolkit:comment-analyzer (documentation review)
  - pr-review-toolkit:code-simplifier (simplify synergy code)
  - superpowers:verification-before-completion (validate features)

Week 6:
  - pr-review-toolkit:type-design-analyzer (collection types)
  - hookify:conversation-analyzer (lessons learned)

Week 7:
  - superpowers:verification-before-completion (production readiness)
  - pr-review-toolkit:code-reviewer (final review)
  - pr-review-toolkit:silent-failure-hunter (edge cases)

Week 8:
  - superpowers:verification-before-completion (deployment validation)
  - All review agents (final sprint)
```

---

## Part 4: Updated Milestone Structure

### Milestone 1: Foundation & Backend API (Week 1-2)
**Lead:** Backend Developer (APIs) + Backend Developer (Services)
**Support:** Tech Lead, Lead Architect
**Skills Used:**
- `test-driven-development` (TDD kickoff)
- `code-architect` (API design)
- `code-explorer` (explore existing functions)
- `agent-sdk-verifier-py` (verify setup)

**Deliverables:**
1. FastAPI project structure + Docker setup
2. Neo4j connection layer with DI
3. 20 Pydantic models for all domains
4. 15+ API endpoints (all routes from Stories.md #1, #2)
5. Service layer wrapping existing functions
6. 80%+ test coverage (pytest)
7. OpenAPI docs at /docs

**Tests Created (TDD):**
- `test_models.py` - Model validation
- `test_api_*.py` - All 15+ endpoints
- `test_services.py` - Service logic

**Code Review Gate:**
- Tech Lead: code-simplifier, silent-failure-hunter
- Lead Architect: final code-reviewer

---

### Milestone 2: Frontend Foundation (Week 2-3)
**Lead:** Frontend Developer (Architecture) + Frontend Developer (UI/UX)
**Support:** Tech Lead, Lead Architect
**Skills Used:**
- `test-driven-development` (TDD for components)
- `code-architect` (component architecture)
- `agent-sdk-verifier-ts` (verify TS setup)
- `type-design-analyzer` (validate types)

**Deliverables:**
1. Vite + React + TypeScript project
2. Tailwind CSS design system (mana colors, spacing scale)
3. 8 base UI components (Button, Card, Input, etc.)
4. React Router with all 5+ routes
5. API client (Axios + React Query)
6. Shared TypeScript types matching backend
7. 70%+ test coverage (Vitest)
8. Error boundary & loading skeletons

**Tests Created:**
- `test_components/` - Base component tests
- `test_services/api.test.ts` - API client tests
- `test_hooks/useCardSearch.test.ts` - Hook tests

**Code Review Gate:**
- Tech Lead: code-simplifier, type-design-analyzer
- Lead Architect: final code-reviewer

---

### Milestone 3: Core Features - Deck Builder (Week 3-4)
**Lead:** Frontend Developer (Deck Builder)
**Support:** Backend Developer (Services for recommendations)
**Skills Used:**
- `test-driven-development` (TDD for deck builder)
- `code-architect` (deck builder UI architecture)
- `superpowers:verification-before-completion` (end-to-end validation)
- `silent-failure-hunter` (edge cases in deck logic)

**Deliverables:**
1. Commander selection page
2. Deck builder main interface (organized by type)
3. Recommendations panel (3 tabs: synergies, roles, similar)
4. Mana curve visualization
5. Deck statistics display
6. Zustand state management for deck
7. 70%+ test coverage
8. E2E test: full deck building workflow

**Tests Created:**
- `test_DeckBuilder.tsx` - Component tests
- `test_useDeckBuilder.ts` - Hook tests
- `test_deck_builder_flow.spec.ts` - E2E test

**Backend Enhancement:**
- Add recommendations endpoints (if not in Milestone 1)
- Implement 7-dimensional synergy scoring endpoint

**Code Review Gate:**
- Tech Lead: code-simplifier, silent-failure-hunter
- QA Lead: pr-test-analyzer
- Lead Architect: final code-reviewer

---

### Milestone 4: Advanced Search & Filters (Week 4-5)
**Lead:** Frontend Developer (Search)
**Support:** Backend Developer (APIs)
**Skills Used:**
- `test-driven-development` (TDD for filters)
- `code-architect` (filter architecture)
- `pr-test-analyzer` (verify filter test coverage)
- `silent-failure-hunter` (filter edge cases)

**Deliverables:**
1. Card search page with 7 filter types:
   - Card Type (checkboxes)
   - Color (checkboxes)
   - CMC (range slider)
   - Rarity (checkboxes)
   - Mechanic (searchable dropdown)
   - Functional Role (checkboxes)
   - Text search (input)
2. Real-time search with debouncing
3. Pagination (20 results/page)
4. Filter state management (Zustand)
5. URL parameter sync (bookmarkable searches)
6. 70%+ test coverage

**Tests Created:**
- `test_CardSearch.tsx` - Component tests
- `test_useCardSearch.ts` - Hook tests
- `test_filters/` - Individual filter tests
- `test_search_flow.spec.ts` - E2E test

**Backend Enhancement:**
- Optimize card search Cypher query
- Add pagination support
- Add filter validation

**Code Review Gate:**
- Tech Lead: code-simplifier
- QA Lead: pr-test-analyzer
- Lead Architect: final code-reviewer

---

### Milestone 5: Similarity & Synergy Features (Week 5-6)
**Lead:** Frontend Developer (Features)
**Support:** Data Scientist (ML validation)
**Skills Used:**
- `test-driven-development` (TDD for visualization)
- `code-explorer` (understand embedding relationships)
- `superpowers:verification-before-completion` (validate synergy scores)
- `comment-analyzer` (document synergy dimensions)

**Deliverables:**
1. Card detail page
2. Similar cards section (top 10 via EMBEDDING_SIMILAR)
3. Synergies section (via SYNERGIZES_WITH)
4. Synergy breakdown visualization (7 dimensions):
   - Mechanic overlap
   - Role compatibility
   - Theme alignment
   - Zone chains
   - Phase alignment
   - Color compatibility
   - Type synergy
5. Known combos section
6. 70%+ test coverage

**Tests Created:**
- `test_CardDetail.tsx` - Component tests
- `test_SynergyVisualization.tsx` - Chart tests
- `test_card_detail_flow.spec.ts` - E2E test

**Backend Enhancement:**
- Add `/api/cards/{name}/synergies` endpoint
- Add `/api/synergy/compute` endpoint (detailed breakdown)
- Validate synergy score accuracy

**Code Review Gate:**
- Tech Lead: code-simplifier, comment-analyzer
- QA Lead: pr-test-analyzer
- Lead Architect: final code-reviewer

---

### Milestone 6: Collection Management (Week 6-7)
**Lead:** Frontend Developer (Features)
**Support:** Tech Lead (state management patterns)
**Skills Used:**
- `test-driven-development` (TDD for collection state)
- `superpowers:verification-before-completion` (validate persistence)
- `pr-test-analyzer` (localStorage tests)

**Deliverables:**
1. Collection page with card grid
2. Add/remove cards from collection
3. Update card quantities
4. Search within collection
5. Filter by type/color/etc.
6. Collection statistics (color distribution, type breakdown)
7. CSV export/import
8. localStorage persistence
9. 70%+ test coverage

**Tests Created:**
- `test_Collection.tsx` - Component tests
- `test_useCollection.ts` - Zustand store tests (persistence!)
- `test_collection_flow.spec.ts` - E2E test

**Future Backend (Phase 2):**
- Database models for persistent collections
- User authentication endpoints
- Cloud sync endpoints

**Code Review Gate:**
- Tech Lead: code-simplifier
- QA Lead: pr-test-analyzer
- Lead Architect: final code-reviewer

---

### Milestone 7: Polish & Production (Week 7-8)
**Lead:** QA Lead + DevOps Engineer + Tech Lead
**Support:** All teams for fixes
**Skills Used:**
- `superpowers:verification-before-completion` (production readiness)
- `silent-failure-hunter` (final edge case review)
- `pr-test-analyzer` (final coverage validation)
- `code-reviewer` (final code quality)
- `hookify:conversation-analyzer` (learn lessons)

**Deliverables:**
1. Full test suite integration:
   - Backend: pytest with 80%+ coverage
   - Frontend: Vitest + Playwright with 70%+ coverage
   - E2E: 20+ Playwright scenarios
2. Performance optimization:
   - < 2s initial page load (Lighthouse)
   - < 500ms API response times (p95)
   - < 100ms filter updates
3. Error handling & logging:
   - Global error boundary
   - Backend error logging
   - Sentry integration (optional)
4. Documentation:
   - User guide (FAQ, tooltips)
   - API documentation (OpenAPI)
   - Development guide (README)
5. Deployment package:
   - Docker Compose (all services)
   - .env configuration
   - Health checks
   - Nginx reverse proxy
6. Production hardening:
   - Security headers
   - Rate limiting
   - Input validation
   - SQL injection protection (if applicable)

**Tests:**
- All previous tests + integration tests
- 80%+ backend coverage
- 70%+ frontend coverage
- 20+ E2E scenarios
- Load testing (100+ concurrent users)
- Accessibility testing (WCAG 2.1 AA)

**Deployment Verification:**
```bash
# Pre-deployment checklist
- [ ] All tests passing
- [ ] Coverage >= targets
- [ ] No console errors
- [ ] Lighthouse score >= 80
- [ ] Security headers present
- [ ] Rate limiting working
- [ ] Error tracking working
- [ ] Documentation complete
- [ ] .env example created
- [ ] Docker images optimized
```

**Code Review Gate:**
- Tech Lead: final code-simplifier pass
- QA Lead: superpowers:verification-before-completion
- Lead Architect: final code-reviewer + type-design-analyzer

---

## Part 5: Critical Implementation Flow

### Week-by-Week Execution

**Week 1: Foundation**
```
Mon-Tue: Backend setup + TDD kickoff
  - Backend Dev (APIs): Milestone 1 planning
  - Backend Dev (Services): Understand existing code
  - Tech Lead: Setup, mentoring
  - Action: code-explorer agent (Week 1 Day 1)
  - Action: test-driven-development agent (Week 1 Day 1)

Wed-Thu: Tests written (RED phase)
  - Test Engineer: Write all tests
  - Backend Devs: Review test specs
  - Action: Provide test cases to teams

Fri: Implementation begins
  - Backend Devs: Code to pass tests (GREEN phase)
  - Tech Lead: Code review
  - Action: code-simplifier agent (end of week)
```

**Week 2: Backend Complete + Frontend Starts**
```
Mon-Tue: Backend finalization
  - Backend Devs: Complete remaining endpoints
  - Test Engineer: Add integration tests
  - Action: agent-sdk-verifier-py (verify setup)

Wed-Thu: Frontend setup + Backend review
  - Frontend Devs: Milestone 2 planning + initialization
  - Tech Lead: Final backend code review
  - Action: code-architect agent (frontend design)
  - Action: test-driven-development (frontend kickoff)

Fri: Frontend foundation complete
  - Frontend Devs: Router, API client, design system
  - Tech Lead: Frontend setup review
  - Action: agent-sdk-verifier-ts (verify TS setup)
  - Action: type-design-analyzer (validate types)
```

**Week 3: Feature Development Parallel**
```
Mon-Wed: Deck builder + Search planning
  - Frontend (Deck Builder): TDD + implementation
  - Frontend (Search): TDD + implementation
  - Test Engineer: Write integration tests
  - Backend Dev: Add recommendation endpoints
  - Action: code-architect agents (both features)
  - Action: test-driven-development (both teams)

Thu-Fri: Code review + simplification
  - Tech Lead: Review both features
  - Backend Dev: Optimize queries
  - Action: code-simplifier (both features)
  - Action: silent-failure-hunter (deck builder edge cases)
```

**Week 4-5: Search Complete + Similarity Starts**
```
Mon-Wed: Search finalization
  - Frontend (Search): Complete filters + pagination
  - Test Engineer: Add E2E tests
  - Action: pr-test-analyzer (verify filter coverage)

Thu-Fri: Similarity feature begins
  - Frontend (Features): Similarity/synergy UI
  - Backend Dev: Synergy endpoints
  - Action: code-explorer (understand synergy data)
  - Action: test-driven-development (similarity TDD)
```

**Week 6: Similarity + Collection**
```
Mon-Wed: Similarity complete
  - Frontend (Features): Detail page + visualization
  - Data Scientist: Validate synergy scores
  - Action: verification-before-completion (ML validation)

Thu-Fri: Collection begins
  - Frontend (Features): Collection state + UI
  - Test Engineer: Zustand store tests
  - Action: comment-analyzer (document state)
```

**Week 7: Collection Complete + Testing Ramps**
```
Mon-Wed: Collection finalization
  - Frontend (Features): CSV export/import, persistence
  - Test Engineer: E2E collection tests
  - QA Lead: Accessibility testing

Thu-Fri: Testing intensifies
  - Test Engineer: Load testing, integration tests
  - QA Lead: Production readiness checklist
  - All teams: Bug fixes from testing
  - Action: pr-test-analyzer (final coverage check)
```

**Week 8: Production Release**
```
Mon-Wed: Final polish
  - All teams: Critical bug fixes
  - DevOps: Docker optimization, health checks
  - Tech Lead: Final code review pass
  - Action: code-simplifier (final pass)
  - Action: silent-failure-hunter (final edge cases)

Thu: Pre-deployment validation
  - QA Lead: superpowers:verification-before-completion
  - All agents: Final review
  - Deployment checklist sign-off

Fri: Deployment
  - DevOps: Production deployment
  - QA Lead: Smoke testing
  - Tech Lead: Monitor logs
```

---

## Part 6: Integration Points

### Backend ↔ Frontend Integration Checkpoints

**Milestone 1 ↔ 2 (Week 1-2 transition):**
- Backend API specification finalized (OpenAPI docs)
- Frontend API client generated from spec
- Verify 5 core endpoints work from frontend

**Milestone 3 ↔ 3 (Within Week 3-4):**
- Deck builder frontend awaits recommendations endpoint
- Backend ensures recommendations tested & performant
- E2E test: Select commander → recommendations load

**Milestone 4 ↔ 4 (Within Week 4-5):**
- Search filters defined before frontend implementation
- Backend search endpoint signature locked in
- E2E test: Apply filters → results update

**Milestone 5 ↔ 5 (Within Week 5-6):**
- Synergy endpoint specs agreed before viz implementation
- ML team validates scoring accuracy
- E2E test: View synergy breakdown → dimensions render

---

## Part 7: Success Metrics & Monitoring

### Code Quality Metrics (Tracked Weekly)

**Backend:**
```
- Test Coverage: ≥ 80%
- Cyclomatic Complexity: Avg < 6
- Code Duplication: < 5%
- Security Issues: 0
- Type Coverage: 100%
```

**Frontend:**
```
- Test Coverage: ≥ 70%
- Cyclomatic Complexity: Avg < 8
- Bundle Size: < 300KB (gzipped)
- Lighthouse Score: ≥ 90
- Type Coverage: 100%
```

### TDD Metrics (Tracked Per Milestone)

```
Milestone | Tests Written | Coverage | Bugs Found | Red→Green Time
1         | 45            | 82%      | 3          | 2.5 days
2         | 38            | 75%      | 2          | 2 days
3         | 52            | 78%      | 4          | 3 days
4         | 41            | 72%      | 2          | 2.5 days
5         | 38            | 74%      | 2          | 2 days
6         | 35            | 71%      | 1          | 1.5 days
7         | 95            | 80%      | 8          | 4 days
```

### Performance Metrics (Target)

```
Metric                  | Target   | Monitor Tool
Initial Page Load       | < 2s     | Lighthouse, WebPageTest
API Response (p95)      | < 500ms  | Backend logs, Datadog
Filter Updates          | < 100ms  | React DevTools
Search Results Load     | < 300ms  | Network tab
Deck Render            | < 150ms  | Profiler
```

---

## Part 8: Risk Mitigation

### Known Risks & Mitigation

**Risk 1: TDD Slow-Down in Early Weeks**
- **Mitigation:** Tech Lead provides test templates; code-reviewer agent validates test quality
- **Contingency:** Add 1 extra day per early milestone if needed

**Risk 2: Neo4j Query Performance**
- **Mitigation:** Data Scientist validates query plans week 2; backend devs optimize week 3
- **Contingency:** Add caching layer (Redis) if p95 > 500ms

**Risk 3: Frontend State Complexity**
- **Mitigation:** Use Zustand (simpler than Redux); PR review for state changes
- **Contingency:** Refactor to Recoil if needed (week 5)

**Risk 4: Integration Issues Between Teams**
- **Mitigation:** Code freeze API specs week 1; frozen until week 6
- **Contingency:** Tech Lead acts as integration point; daily standup

**Risk 5: Test Coverage Not Met**
- **Mitigation:** QA Lead reviews coverage daily; Test Engineer writes missing tests immediately
- **Contingency:** Lower targets to 75%/65% (not ideal)

---

## Part 9: Critical Files to Create

### Backend (New)
1. `backend/app/main.py` - FastAPI initialization
2. `backend/app/config.py` - Settings
3. `backend/app/dependencies.py` - Neo4j DI
4. `backend/app/models/*.py` - 5 Pydantic models
5. `backend/app/routers/*.py` - 5 route files
6. `backend/app/services/*.py` - 3 service files
7. `backend/tests/conftest.py` - Fixtures
8. `backend/tests/unit/*.py` - Unit tests
9. `backend/tests/integration/*.py` - Integration tests
10. `backend/Dockerfile` - Production build

### Frontend (New)
1. `frontend/src/App.tsx` - Routing
2. `frontend/src/services/api.ts` - API client
3. `frontend/src/types/*.ts` - TypeScript types
4. `frontend/src/components/ui/*.tsx` - Base components (8 files)
5. `frontend/src/features/*/*.tsx` - Feature pages (12+ files)
6. `frontend/src/features/*/use*.ts` - Custom hooks (4 files)
7. `frontend/src/__tests__/**/*.test.tsx` - All tests (25+ files)
8. `frontend/tailwind.config.js` - Design system
9. `frontend/vitest.config.ts` - Test config
10. `frontend/Dockerfile` - Production build

### Configuration (New)
1. `docker-compose.yml` (update) - Add backend + frontend
2. `backend/.env.example` - Backend env template
3. `frontend/.env.example` - Frontend env template
4. `Dockerfile.backend` - Backend container
5. `Dockerfile.frontend` - Frontend container
6. `.github/workflows/ci.yml` - CI pipeline
7. `.pre-commit-config.yaml` - Pre-commit hooks

---

## Implementation Start Checklist

Before Week 1 begins:

- [ ] All team members onboarded (understand their role)
- [ ] Chat with each team: "What do you need from me?"
- [ ] Create shared Notion/GitHub Wiki for team communication
- [ ] Setup GitHub project board (Milestones + Issues)
- [ ] Create branch protection rules
- [ ] Setup CI/CD skeleton (GitHub Actions)
- [ ] Verify Neo4j running with full data
- [ ] Create requirements.txt skeleton
- [ ] Create package.json skeleton
- [ ] Schedule: Daily standup 10am, Weekly planning Friday 3pm

---

**Plan Ready for Implementation**

This plan incorporates:
✅ Agent team assignments with specific models for each role
✅ TDD-first approach with specific tests to write per milestone
✅ All available Claude Code plugins integrated into workflow
✅ Clear integration points between teams
✅ Success metrics and risk mitigation
✅ Week-by-week execution details

Proceed to Milestone 1 kickoff when ready.
