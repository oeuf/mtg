# End-to-End Tests

These tests require a running Neo4j database.

## Setup

1. Start Neo4j (Docker or local):
   ```bash
   docker run --rm -p 7687:7687 -e NEO4J_AUTH=neo4j/testpass neo4j:latest
   ```

2. Set environment variable:
   ```bash
   export NEO4J_TEST_PASSWORD=testpass
   ```

3. Run E2E tests:
   ```bash
   pytest tests/e2e/ -m e2e -v
   ```

## What E2E Tests Cover

- Complete pipeline: parse → enrich → load → query
- Real Neo4j database operations
- Schema creation
- All relationship types
- Synergy inference
- Query functions

These tests are slower but catch integration bugs that unit tests miss.
