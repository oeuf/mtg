# Parallel Multi-Agent Codebase Migrations

## Problem

Large changes spanning 10+ files across multiple modules (backend, frontend, tests) are slow when done sequentially. A single agent working through a migration file-by-file can take 30+ minutes of wall-clock time on changes that are logically independent. Claude Code supports agent teams via `TeamCreate`, `TaskCreate`, and `SendMessage`, but there is no documented workflow for coordinating parallel migrations across the MTG Commander Knowledge Graph codebase.

The MTG project has clear module boundaries -- Python backend (`src/`, `main.py`), future FastAPI API layer (`src/api/`), future Next.js frontend, and tests (`tests/`) -- making it a strong candidate for parallel agent work. When Phase 4 (FastAPI) and Phase 5 (Next.js UI) begin, full-stack features will require simultaneous changes to the graph layer, API routes, React components, and test suites.

## Proposed Workflow

### Team Structure

| Agent | Role | File Ownership | Tools |
|-------|------|----------------|-------|
| **Architect (lead)** | Creates task list, assigns work, reviews integration | `CLAUDE.md`, `docs/`, orchestration only | All tools, `TeamCreate`, `SendMessage` |
| **Backend agent** | Python/API changes | `src/`, `main.py`, `requirements.txt` | Full capability (read, write, bash) |
| **Frontend agent** | TypeScript/React changes | `frontend/src/`, `frontend/package.json` | Full capability (read, write, bash) |
| **Test runner** | Runs tests continuously, reports failures | `tests/`, read-only on `src/` and `frontend/` | Full capability for test files, bash for `pytest` and `npm test` |

The architect is the only agent that sends `broadcast` messages. Backend and frontend agents communicate through the architect or via direct messages when coordinating on shared interfaces (e.g., API contracts).

### Coordination Protocol

1. **Architect analyzes the codebase** to identify every file that needs changes. This produces a file manifest grouped by module.

2. **Architect creates a task dependency graph** using `TaskCreate` and `TaskUpdate` with `addBlockedBy` to encode dependencies. Tasks are granular enough that each touches 1-3 files.

3. **Independent tasks are assigned in parallel.** The architect uses `TaskUpdate` with `owner` to assign unblocked tasks to the backend and frontend agents simultaneously.

4. **Agents work and report.** Each agent marks tasks complete via `TaskUpdate` when done, then checks `TaskList` for the next available task. The architect receives automatic notifications.

5. **Architect reviews at checkpoints.** Before starting any dependent task, the architect reads the changed files and verifies correctness. This is a hard gate -- no dependent task begins until the architect approves.

6. **Test runner validates after each milestone.** The test runner agent runs `pytest tests/unit/ -v` and (once the frontend exists) `npm test` after each checkpoint. Failures are reported to the architect, who decides whether to block further work.

7. **Architect sends shutdown requests** once all tasks are complete and the final test run passes.

### Example: Adding a Full-Stack `/api/decks/analyze` Endpoint

This walks through a concrete migration for the MTG project: adding a deck analysis endpoint that takes a list of card names, queries the Neo4j knowledge graph for synergy data, and displays results in a React component.

#### Task Dependency Graph

```
Task 1 (backend) -----> Task 3 (frontend)
                  \        |
Task 2 (backend) --+----> Task 5 (test)
                   |       |
Task 4 (frontend) -+-------+
```

#### Task Definitions

**Task 1 -- Create FastAPI route and service layer** (backend agent)
- Owner: backend
- Blocked by: nothing
- Files: `src/api/routes/decks.py`, `src/api/services/deck_analyzer.py`
- Acceptance: POST `/api/decks/analyze` accepts `{"card_names": ["Necropotence", "Dark Ritual", ...]}` and returns a JSON response with synergy scores and recommendations. Route is registered in the FastAPI app.

**Task 2 -- Add Neo4j query for deck analysis** (backend agent)
- Owner: backend
- Blocked by: nothing
- Files: `src/graph/queries/deck_analysis.py`
- Acceptance: Function `analyze_deck_synergies(card_names: list[str]) -> dict` queries the graph for `SYNERGIZES_WITH` and `EMBEDDING_SIMILAR` relationships between the given cards, returns aggregated synergy scores, community overlap, and top recommended additions. Uses the existing `Neo4jConnection` from `src/graph/connection.py`.

**Task 3 -- Create DeckAnalyzer React component** (frontend agent)
- Owner: frontend
- Blocked by: Task 1 (needs the API contract / response shape)
- Files: `frontend/src/components/DeckAnalyzer.tsx`, `frontend/src/components/DeckAnalyzer.css`
- Acceptance: Component accepts a deck list, displays a synergy matrix heatmap, top synergy pairs, and recommended card additions. Handles loading and error states.

**Task 4 -- Wire up API client** (frontend agent)
- Owner: frontend
- Blocked by: nothing (can code against the API contract before the backend is done)
- Files: `frontend/src/api/decks.ts`, `frontend/src/types/deck.ts`
- Acceptance: Typed API client function `analyzeDeck(cardNames: string[]): Promise<DeckAnalysis>` with proper error handling. TypeScript types match the API response schema.

**Task 5 -- Integration tests** (test runner)
- Owner: test-runner
- Blocked by: Tasks 1, 2, 3, 4
- Files: `tests/integration/test_deck_analysis_api.py`, `frontend/src/components/__tests__/DeckAnalyzer.test.tsx`
- Acceptance: Backend test hits the real `/api/decks/analyze` endpoint with a known deck (e.g., Muldrotha precon cards) and validates response structure. Frontend test renders the DeckAnalyzer component with mocked API data and verifies the synergy matrix renders.

#### Execution Timeline

```
t=0   Architect creates Tasks 1-5 with dependencies
t=0   Architect assigns Task 1 + Task 2 to backend, Task 4 to frontend
      (Task 3 is blocked, Task 5 is blocked)

t=1   Backend completes Task 1 (route + service layer)
      Backend starts Task 2 (may already be in progress in parallel)
      Architect reviews Task 1, unblocks Task 3
      Architect assigns Task 3 to frontend

t=2   Backend completes Task 2
      Frontend completes Task 3 and Task 4
      Architect reviews all, unblocks Task 5
      Architect assigns Task 5 to test-runner

t=3   Test runner completes Task 5, reports results
      Architect does final review and shuts down the team
```

Wall-clock time is roughly halved compared to sequential execution because backend and frontend work proceeds simultaneously during t=0 through t=2.

## Copyable Prompt

Use this prompt to launch a parallel migration team in Claude Code:

```
Create an agent team to implement [feature]. Use an architect lead with backend
and frontend agents plus a test runner. The architect should:

1. Analyze the codebase to identify all files that need changes
2. Create a task dependency graph with TaskCreate and TaskUpdate (addBlockedBy)
3. Assign independent tasks to backend and frontend agents in parallel
4. Review at checkpoints before unblocking dependent tasks
5. Have the test runner validate after each milestone

File ownership:
- Backend agent owns: src/, main.py, requirements.txt
- Frontend agent owns: frontend/src/, frontend/package.json
- Test runner owns: tests/ (read-only access to src/ and frontend/)

Start by reading CLAUDE.md for project context, then analyze the codebase to
build the task list.
```

For MTG-project-specific migrations, append:

```
This is the MTG Commander Knowledge Graph project. The graph schema uses Card,
Commander, Mechanic, Functional_Role, Theme, Subtype, Zone, and Phase nodes.
Key relationships: HAS_MECHANIC, FILLS_ROLE, SUPPORTS_THEME, SYNERGIZES_WITH,
EMBEDDING_SIMILAR. Neo4j connection is in src/graph/connection.py. Backend uses
Python 3.9+ with Neo4j GDS. Frontend will use Next.js + TypeScript.
```

## Prerequisites

- **Agent teams enabled.** Claude Code supports `TeamCreate`, `TaskCreate`, `TaskUpdate`, `SendMessage` natively. No additional configuration needed.
- **Clear file ownership boundaries.** The MTG project already separates backend (`src/`) from future frontend (`frontend/`) and tests (`tests/`). Two agents should never edit the same file simultaneously.
- **Existing test suite for regression detection.** The project has 30 passing unit tests in `tests/unit/` and `tests/test_feature_scorers.py`. Integration tests require a running Neo4j instance (`docker-compose up -d`).
- **Well-defined API contracts between layers.** Before frontend work begins, the backend agent must produce a response schema (or the architect must define one in the task description). TypeScript types and Python Pydantic models should match.
- **Neo4j running.** Backend tasks that touch the graph need the database: `docker-compose up -d && sleep 10 && export NEO4J_PASSWORD="password"`.

## When to Use

Use parallel multi-agent migrations when:

- **10+ files across 2+ modules.** The coordination overhead of spinning up a team (creating tasks, managing dependencies, reviewing checkpoints) is only worth it for larger changes.
- **Clear separation of concerns.** Backend and frontend (or multiple backend modules) can proceed independently for most of the work.
- **Tasks have parallelizable subtasks.** If every task depends on the previous one, a single agent is simpler.
- **The change is well-understood upfront.** The architect needs to build the full task graph before work begins. Exploratory or research-heavy work does not benefit from parallelism.

Do NOT use parallel agents for:

- Bug fixes touching fewer than 5 files.
- Changes confined to a single module (e.g., only modifying `src/parsing/`).
- Refactors where every file change depends on the previous one.
- Exploratory work where the scope is not yet known.

## Risks

### Merge Conflicts
Two agents editing the same file will produce conflicts or silently overwrite each other's changes. **Mitigation:** Strict file ownership enforced by the architect. Each task description explicitly lists the files it touches. If two tasks must modify the same file, they are serialized with a dependency.

### Integration Failures
Components built in isolation may not fit together at the boundaries. A backend agent might return `synergy_score` as a float while the frontend expects a string. **Mitigation:** The architect defines shared contracts (API response shapes, type definitions) before assigning work. Checkpoint reviews catch mismatches before dependent tasks begin.

### Coordination Overhead
For small changes, the time spent creating tasks, assigning agents, and reviewing checkpoints exceeds the time a single agent would need. **Mitigation:** Only use this workflow for changes touching 10+ files across 2+ modules. The copyable prompt above includes this guidance.

### Token Cost
Each agent consumes tokens independently. A four-agent team uses roughly 3-4x the tokens of a single agent for the same total work, because each agent reads shared context (project files, `CLAUDE.md`). **Mitigation:** Reserve parallel teams for genuinely large migrations where wall-clock time savings justify the cost. Keep task descriptions precise to minimize unnecessary file reads.

### Stale Task State
Agents may read task status that has changed since their last check. **Mitigation:** Agents call `TaskList` after completing each task to get the latest state. The architect is the single source of truth for unblocking dependent tasks -- agents do not self-assign blocked tasks.
