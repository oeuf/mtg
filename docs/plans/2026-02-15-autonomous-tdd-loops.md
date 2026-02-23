# Autonomous TDD Loops

## Problem

Claude Code sessions lack automated test-driven feedback loops. When a developer asks Claude to implement a feature, the typical workflow looks like this:

1. Claude writes code.
2. The developer manually runs `pytest tests/unit/ -v`.
3. The developer pastes the output back into the conversation.
4. Claude reads the output and makes corrections.
5. Repeat.

Each round-trip wastes tokens (re-reading pasted output, regenerating context) and developer time (switching between editor and terminal, copy-pasting results). For the MTG Commander Knowledge Graph project, where the test suite covers synergy scoring, mechanics parsing, and graph loading across 30+ tests, this friction compounds quickly. A single feature like adding a new mechanic pattern to `src/parsing/mechanics.py` can require three or four manual test cycles before all assertions pass.

The core issue: Claude can run tests itself via the Bash tool, but nothing enforces the discipline of running them at the right time or stopping when the loop goes off the rails.

## Proposed Workflow

A strict red-green-refactor loop where Claude drives the entire cycle autonomously:

1. **Red** -- Write a failing test that defines the desired behavior. Run `pytest` to confirm it fails with the expected error. If it passes immediately, the test is not capturing new behavior; rewrite it.
2. **Green** -- Implement the minimum code to make the failing test pass. No more. Run `pytest` to confirm the new test passes and no existing tests regress.
3. **Refactor** -- Clean up the implementation (extract helpers, rename variables, reduce duplication) while keeping the full test suite green. Run `pytest` after each refactor step.
4. **Repeat** -- Return to step 1 for the next slice of behavior. Cap at 5 iterations to prevent infinite loops.

### Exit conditions

- The feature is complete (all intended behaviors are covered by passing tests).
- 5 red-green-refactor iterations have been reached.
- A test failure persists for more than 2 consecutive green attempts (likely a design problem that needs human input).

### Three Approaches

#### 1. Single-prompt instruction

Tell Claude "use TDD" in the prompt. Claude follows the red-green-refactor discipline based on the instruction alone.

**Pros:**
- Zero setup. Works immediately in any Claude Code session.
- No configuration files, hooks, or agents required.

**Cons:**
- Relies entirely on Claude's discipline. Nothing enforces test execution.
- Claude may skip the "red" step and jump straight to implementation.
- No automatic feedback if Claude forgets to run tests after an edit.

**Best for:** Quick one-off tasks where adding infrastructure is not worth it.

#### 2. Hook-driven auto-test

Configure PostToolUse hooks that automatically run the relevant test suite after every `Edit` or `Write` to `.py` or `.ts` files. Claude sees test output immediately after every file change without needing to remember to run tests.

Example hook configuration (`.claude/hooks/post-edit-test.sh`):

```bash
#!/bin/bash
# PostToolUse hook: run after Edit/Write to .py files
CHANGED_FILE="$1"
if [[ "$CHANGED_FILE" == *.py ]]; then
    cd /Users/ng/cc-projects/mtg
    source venv/bin/activate
    pytest tests/unit/ -x -q --tb=short 2>&1 | tail -20
fi
```

**Pros:**
- Automatic feedback loop. Claude never forgets to run tests.
- Immediate failure visibility. Claude sees regressions the moment they are introduced.
- Works within a single Claude Code session; no multi-agent coordination needed.

**Cons:**
- Runs tests on every file save, including documentation or config changes. Needs file-pattern filtering.
- May slow down rapid multi-file edits (e.g., renaming a function across five files triggers five test runs).
- Hook configuration is session-specific; must be set up per project.

**Best for:** Projects with fast test suites (under 10 seconds) where continuous feedback is valuable.

#### 3. Agent team with test-runner

Spawn a dedicated `test-runner` agent that watches for file changes and reports results back to the implementing agent. The test-runner operates in parallel: while the implementer edits code, the test-runner runs the suite and sends a message with pass/fail status.

**Pros:**
- Parallel execution. Tests run while implementation continues.
- Clear separation of concerns. The test-runner can also enforce coverage thresholds or lint checks.
- Scales to larger teams where multiple agents edit different parts of the codebase.

**Cons:**
- Significantly more complex. Requires team creation, task coordination, and message passing.
- Higher token cost (two agents running simultaneously).
- Race conditions: the test-runner may test stale code if the implementer is mid-edit.

**Best for:** Large features that span multiple files and benefit from parallel work, such as building out the FastAPI layer (Phase 4) alongside its test suite.

### Recommended Approach

Combine a `tdd-loop` skill with PostToolUse hooks:

- **The `tdd-loop` skill** (`.claude/skills/tdd-loop.md`) defines the red-green-refactor discipline as a reusable instruction set. It tells Claude exactly when to write a test, when to implement, when to refactor, and when to stop. It enforces the 5-iteration cap and the exit conditions.

- **PostToolUse hooks** (from Phase 2 of the insights implementation) provide automatic test execution after every `.py` file edit. Claude does not need to remember to run `pytest`; the hook does it and pipes the output back into the conversation.

This combination gives structure (the skill enforces the workflow) plus automation (the hook provides immediate feedback) without the complexity of multi-agent coordination. For the MTG project specifically:

- Tests run via `pytest tests/unit/ -x -q --tb=short` (fast, stops on first failure, concise output).
- Integration tests that hit Neo4j are skipped during the TDD loop (they require a running database and are slower). Use `pytest tests/unit/ -v -k "not integration"` if integration markers are present.
- Neo4j test isolation is handled by running tests against a separate test database or by wrapping each test in a transaction that rolls back. The `conftest.py` should provide a `neo4j_session` fixture that cleans up after itself.

## Copyable Prompt

Paste this into a Claude Code session to start a TDD loop:

```
Use TDD to implement [feature]. Follow this workflow strictly:

1. Write a failing test in tests/unit/ that asserts the desired behavior.
2. Run: pytest tests/unit/ -x -q --tb=short
3. Confirm the test fails. If it passes, the test is wrong -- rewrite it.
4. Implement the minimum code to make the test pass. No extra features.
5. Run: pytest tests/unit/ -x -q --tb=short
6. Confirm all tests pass. If not, fix the implementation (not the test).
7. Refactor the implementation for clarity. Run tests again to confirm green.
8. Repeat from step 1 for the next behavior.

Stop after 5 red-green-refactor cycles or when the feature is complete.
If a test fails for 2 consecutive attempts, stop and explain the problem.
```

For MTG-specific features (new mechanic, new synergy dimension, new API endpoint):

```
Use TDD to add the [mechanic_name] mechanic to src/parsing/mechanics.py.

1. Write a test in tests/unit/test_mechanics.py that asserts MechanicExtractor
   correctly identifies [mechanic_name] from oracle text like "[example text]".
2. Run: pytest tests/unit/test_mechanics.py -x -q --tb=short
3. Confirm it fails (the pattern does not exist yet).
4. Add the regex pattern to MECHANIC_PATTERNS in src/parsing/mechanics.py.
5. Run tests again. Confirm the new test passes and all existing tests still pass.
6. Refactor if needed (e.g., consolidate similar patterns).

Stop after the mechanic is correctly detected and all tests pass.
```

## Prerequisites

- **Post-edit hooks configured (Phase 2):** The PostToolUse hook infrastructure must be in place so that test execution happens automatically after file edits. Without this, the loop falls back to Approach 1 (prompt-only discipline).

- **Test framework installed:** For the MTG project, `pytest` is already in `requirements.txt`. For TypeScript projects (Phase 5 frontend), install `vitest` or `jest`. The hook script must know which test runner to invoke based on file extension.

- **Existing test suite to avoid regressions:** The TDD loop adds new tests but also runs the full unit suite to catch regressions. The MTG project currently has 30 passing tests in `tests/unit/`. These must remain green throughout the loop. If the existing suite has flaky tests, fix them before starting a TDD loop.

- **Fast test execution:** The unit test suite should complete in under 10 seconds. If tests take longer (e.g., because they hit Neo4j), split them into unit and integration tiers and only run unit tests in the loop. The MTG project's unit tests (synergy scoring, mechanics parsing) run in under 2 seconds. Integration tests (graph loading, GDS algorithms) should be excluded from the TDD loop.

- **Neo4j test isolation (for integration tests):** When TDD touches graph-related code, tests need a clean database state. Options:
  - Use a dedicated test database (`NEO4J_DATABASE=test`).
  - Wrap each test in a transaction and roll back at the end.
  - Use `CALL { ... } IN TRANSACTIONS` with cleanup in `teardown`.

## Risks

### Infinite loops

Claude may iterate endlessly if the test expectations are wrong or if the implementation approach is fundamentally flawed. For example, writing a test that asserts a Neo4j query returns specific results when the test database is empty will never pass regardless of implementation.

**Mitigation:** Hard cap at 5 iterations. If a test fails for 2 consecutive green attempts, Claude must stop and explain the problem to the developer rather than continuing to try.

### Weakened assertions

Claude may write tests that are too easy to pass. The classic failure mode: asserting that a function returns "something" rather than asserting it returns the correct value. For the MTG project, this might look like `assert len(mechanics) > 0` instead of `assert 'etb_trigger' in mechanics`.

**Mitigation:** The `tdd-loop` skill should instruct Claude to write specific assertions first (exact values, exact types, exact error messages) and only relax them if the specification is genuinely flexible. Code review after the loop should check test quality.

### Token cost

Each red-green-refactor iteration involves writing test code, writing implementation code, and running `pytest` at least twice (once to see red, once to see green). A 5-iteration loop for a moderately complex feature might consume 10,000-20,000 tokens. For context-heavy features that require reading large files (e.g., `src/synergy/feature_scorers.py` at 500+ lines), token usage increases further.

**Mitigation:** Monitor token usage per loop. For simple features (adding a mechanic pattern), 2-3 iterations are typical; cap lower if possible. For complex features, consider breaking them into smaller sub-features with separate TDD loops.

### Flaky tests

Non-deterministic tests cause false failures that waste iterations. In the MTG project, potential sources of flakiness include:
- Tests that depend on Neo4j container state (connection timeouts, auth rate limits).
- Tests that depend on dictionary ordering (Python 3.7+ preserves insertion order, but set operations do not).
- Tests that use floating-point comparisons without tolerance (`assert score == 0.75` vs. `assert abs(score - 0.75) < 0.01`).

**Mitigation:** Ensure test isolation. Unit tests should not hit Neo4j. Use `pytest.approx()` for floating-point comparisons. Run the full suite once before starting the TDD loop to confirm a clean baseline. If a test fails intermittently during the loop, skip it and flag it for the developer.
