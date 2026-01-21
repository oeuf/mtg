# MTG Commander Knowledge Graph - Setup Guide

## Prerequisites

1. **Neo4j** - Install and start Neo4j Desktop or use Docker:
   ```bash
   docker run -d --name neo4j \
     -p 7474:7474 -p 7687:7687 \
     -e NEO4J_AUTH=neo4j/your_password \
     neo4j:5
   ```

2. **Python 3.9+** with dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **Node.js 18+** for the frontend:
   ```bash
   cd frontend && npm install
   ```

## Load Data into Neo4j

Set environment variables:
```bash
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=your_password
```

Run the data loader:
```bash
python main.py
```

This will:
- Download card data from MTGJSON
- Parse and enrich Commander-legal cards
- Load cards, relationships, and synergies into Neo4j
- Run graph algorithms (PageRank, community detection)

## Start the Application

Terminal 1 - API:
```bash
export NEO4J_PASSWORD=your_password
python -m uvicorn api.main:app --port 8000 --reload
```

Terminal 2 - Frontend:
```bash
cd frontend && npm run dev
```

Visit http://localhost:3000

## Running Tests

```bash
# Backend unit tests
pytest tests/ -v

# E2E tests (requires Neo4j running with data)
cd frontend && npm run test:e2e
```
