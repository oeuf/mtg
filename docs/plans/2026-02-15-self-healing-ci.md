# Self-Healing CI Pipeline

## Problem

The MTG Commander Knowledge Graph project currently has no CI pipeline. When CI is added, failures require manual diagnosis and fixing. Claude Code could automate the diagnosis and fix cycle.

The project has a Python backend (Neo4j graph pipeline, pytest test suite) and a planned Next.js frontend. Both need automated checks on every push and pull request. Without CI, regressions slip through. With CI but without self-healing, every red build requires a human to read logs, find the root cause, and push a fix. Claude Code can close that loop.

## Proposed Workflow

### Phase 1: CI Generation

Generate a GitHub Actions workflow for the MTG project:

- **Python linting** (ruff/flake8) -- catch style and import errors before tests run
- **Python tests** (pytest) -- run `pytest tests/unit/ -v` for unit tests; integration tests require Neo4j
- **TypeScript type-check** (tsc --noEmit) -- once the Next.js frontend exists
- **TypeScript tests** (vitest) -- once the Next.js frontend exists
- **Neo4j service container** for integration tests -- mirrors the `docker-compose.yml` setup (Neo4j 5.15.0-enterprise with GDS plugin, auth `neo4j/password`)

This is the concrete first step -- the project needs CI before it can self-heal.

### Phase 2: Failure Diagnosis

When CI fails:

1. Fetch the failure log (`gh run view --log-failed`)
2. Identify the failing step and error type (lint error, test assertion, import failure, timeout, service unavailability)
3. Locate the relevant source files using the traceback or linter output
4. Propose a fix with explanation

Failure types specific to this project:

| Failure Type | Example | Typical Fix |
|---|---|---|
| Import error | Missing dependency in `requirements.txt` | Add the dependency |
| Neo4j connection | Auth rate limit or container not ready | Increase `sleep` or restart service |
| Test assertion | Synergy score out of expected range | Update test threshold or fix scorer |
| Lint error | Unused import in `src/parsing/mechanics.py` | Remove the import |
| Type error | Wrong argument type in API handler | Fix the type annotation or call site |
| Timeout | GDS algorithm takes too long in CI | Reduce test data size or increase timeout |

### Phase 3: Self-Healing Loop

1. CI fails on a push or pull request
2. GitHub Actions triggers a webhook or scheduled check
3. Claude Code is invoked with the failure context (run ID, branch, failure logs)
4. Claude diagnoses the issue and creates a fix
5. Fix is committed to a new branch (`fix/ci-<run-id>`) and pushed
6. CI runs again on the fix branch
7. If CI passes, a PR is opened targeting the original branch for human review
8. If CI fails again, retry up to 3 times with cumulative context from prior attempts
9. After 3 failures, escalate to a human with a summary of all attempted fixes

```
┌─────────┐     ┌──────────┐     ┌───────────┐     ┌──────────┐
│ CI Fails │────>│ Diagnose │────>│ Apply Fix │────>│ Re-run   │
└─────────┘     └──────────┘     └───────────┘     │ CI       │
                                                    └────┬─────┘
                                                         │
                                              ┌──────────┴──────────┐
                                              │                     │
                                         Pass │                Fail │
                                              v                     v
                                        ┌──────────┐       ┌──────────────┐
                                        │ Open PR  │       │ Retry (<=3)  │
                                        │ for      │       │ or escalate  │
                                        │ review   │       │ to human     │
                                        └──────────┘       └──────────────┘
```

## Copyable Prompt

For diagnosing CI failures:

```
The CI pipeline failed. Run `gh run view --log-failed` to get the failure details. Diagnose the root cause, identify the files that need changes, and implement a fix. Run the relevant tests locally to verify before committing.
```

For generating the initial CI workflow:

```
Create a .github/workflows/ci.yml for this project. The backend is Python 3.9+ with pytest tests in tests/unit/. The frontend will be Next.js with vitest. Neo4j 5.15.0-enterprise with GDS plugin is needed for integration tests. Use the auth credentials neo4j/password. Trigger on push to main and on pull requests.
```

## MTG Project First Step

Generate a `.github/workflows/ci.yml` for the project with:

- **Trigger:** on push to `main` and on all pull requests
- **Python matrix:** 3.9, 3.10, 3.11
- **Node 20:** for the frontend job (once it exists)
- **Neo4j service container:** `neo4j:5.15.0-enterprise` with `NEO4J_AUTH=neo4j/password`, `NEO4J_ACCEPT_LICENSE_AGREEMENT=yes`, and the GDS plugin enabled via `NEO4J_PLUGINS='["graph-data-science"]'`
- **Separate jobs:**
  - `backend-lint` -- install ruff, run `ruff check src/ tests/`
  - `backend-test` -- install dependencies from `requirements.txt`, wait for Neo4j, run `pytest tests/unit/ -v`
  - `backend-integration` -- same as above but runs integration tests with the Neo4j service container
  - `frontend-lint` -- (placeholder, gated on frontend directory existing)
  - `frontend-test` -- (placeholder, gated on frontend directory existing)

Example skeleton for the backend test job:

```yaml
backend-test:
  runs-on: ubuntu-latest
  strategy:
    matrix:
      python-version: ["3.9", "3.10", "3.11"]
  services:
    neo4j:
      image: neo4j:5.15.0-enterprise
      env:
        NEO4J_AUTH: neo4j/password
        NEO4J_ACCEPT_LICENSE_AGREEMENT: "yes"
        NEO4J_PLUGINS: '["graph-data-science"]'
      ports:
        - 7474:7474
        - 7687:7687
      options: >-
        --health-cmd "cypher-shell -u neo4j -p password 'RETURN 1'"
        --health-interval 10s
        --health-timeout 5s
        --health-retries 10
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    - run: pip install -r requirements.txt
    - run: pytest tests/unit/ -v
      env:
        NEO4J_PASSWORD: password
```

## Prerequisites

- GitHub repository with Actions enabled
- Test suite that runs reliably in CI (currently 30 passing unit tests in `tests/test_feature_scorers.py`)
- `gh` CLI authenticated for local diagnosis workflows
- Clear understanding of what "passing" means for each check:
  - Lint: zero errors (warnings acceptable initially)
  - Unit tests: all pass, no Neo4j required
  - Integration tests: all pass with Neo4j service container running
  - Type-check: zero errors from `tsc --noEmit`
  - Frontend tests: all vitest suites pass

## Safety Constraints

- **Never auto-merge** -- all fixes require human review via PR
- **Never expose CI secrets** in logs or commit messages; sanitize Neo4j credentials and any API keys from output
- **Rate-limit retries** -- max 3 attempts per failure, then escalate
- **Never modify CI workflow files** in the self-healing loop (to prevent recursive breakage where a bad workflow change triggers another self-healing attempt that makes another bad workflow change)
- **Log all automated changes** for audit -- each fix commit message should reference the CI run ID and include the diagnosis summary
- **Branch isolation** -- fixes go to `fix/ci-<run-id>` branches, never directly to `main`
- **No dependency version bumps** without human approval -- automated fixes should not change `requirements.txt` or `package.json` versions

## Risks

- **Recursive failures**: A fix attempt breaks something else, triggering another self-healing cycle. Mitigation: cap retries at 3 per run, and never let a fix branch trigger another self-healing invocation.
- **Security**: CI secrets (Neo4j password, GitHub tokens) could leak in error messages or automated commit messages. Mitigation: sanitize all log output before passing to Claude Code; use GitHub's built-in secret masking.
- **Flaky tests**: Non-deterministic failures (Neo4j connection timing, GDS algorithm variance) waste retry cycles. Mitigation: identify and fix flaky tests before enabling self-healing; add retry logic to known flaky steps in the workflow itself.
- **Over-automation**: Some failures need human judgment -- architecture decisions, dependency upgrades, changes to the graph schema. Mitigation: classify failure types and only auto-fix categories like lint errors, simple test failures, and import issues. Route everything else to humans.
- **Cost**: Each self-healing cycle consumes CI minutes and API tokens. Mitigation: rate-limit invocations per day; skip self-healing for draft PRs and WIP branches.
- **Stale fixes**: The self-healing branch may conflict with concurrent changes to `main`. Mitigation: rebase the fix branch before opening the PR; if rebase fails, escalate to human.
