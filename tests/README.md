# Test Suite Documentation

## Test Structure

```
tests/
├── unit/               # Fast, isolated unit tests
│   ├── test_functional_roles.py
│   ├── test_mechanics.py
│   └── test_properties.py
├── integration/        # Integration tests with mocked dependencies
│   ├── test_enrichment.py
│   ├── test_mtgjson_parsers.py
│   ├── test_graph_loaders_mock.py
│   ├── test_graph_loading.py
│   ├── test_neo4j_integration.py
│   ├── test_muldrotha_validation.py
│   └── test_pipeline_errors.py
├── e2e/               # End-to-end tests (require Neo4j with test env)
│   ├── test_full_pipeline.py
│   └── conftest.py
└── fixtures/          # Test data
    └── mtgjson/
        ├── sample_atomic_cards.json
        ├── sample_related_cards.json
        └── sample_keywords.json
```

## Running Tests

### Quick Test (Unit only - ~1s)
```bash
pytest tests/unit -v
```

### Integration Tests (~3s)
```bash
pytest tests/integration -v
```

### E2E Tests (requires Neo4j with test credentials)
```bash
# Set test password (different from main database)
export NEO4J_TEST_PASSWORD=testpass

# Run E2E tests
pytest tests/e2e -m e2e -v
```

### All Tests
```bash
pytest tests/ -v
```

### With Coverage
```bash
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

## Test Fixtures

Test fixtures in `tests/fixtures/mtgjson/` contain 5 sample cards:
- **Sol Ring** - Fast mana artifact
- **Muldrotha, the Gravetide** - Commander with graveyard synergy
- **Eternal Witness** - ETB recursion creature
- **Dramatic Reversal** - Instant (combos with Isochron Scepter)
- **Isochron Scepter** - Artifact (combo piece)

These cards cover all major mechanics and provide combo relationships for testing.

## Adding New Tests

### Unit Test
1. Create test in `tests/unit/test_<module>.py`
2. Test single function/class in isolation
3. Use simple assertions, no external dependencies

### Integration Test
1. Create test in `tests/integration/test_<feature>.py`
2. Test multiple components working together
3. Use mocks for expensive operations (database, network)
4. Use fixtures for test data

### E2E Test
1. Create test in `tests/e2e/test_<scenario>.py`
2. Test complete user workflow
3. Use real Neo4j database via `neo4j_test_connection` fixture
4. Mark with `@pytest.mark.e2e`

## Current Coverage

- **Unit Tests**: 21 tests (parsing modules)
- **Integration Tests**: ~40 tests (parsers, loaders, enrichment, validation)
- **E2E Tests**: 2 tests (full pipeline, queries)
- **Total**: 60+ tests

Target: 90% coverage for critical paths
