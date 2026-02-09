#!/bin/bash
# Start Neo4j container for MTG Knowledge Graph

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "Starting Neo4j container..."
docker-compose up -d

echo "Waiting for Neo4j to start..."
until curl -s http://localhost:7474 > /dev/null 2>&1; do
    echo "  Waiting..."
    sleep 2
done

echo ""
echo "Neo4j ready!"
echo "  Browser: http://localhost:7474"
echo "  Bolt:    bolt://localhost:7687"
echo "  Auth:    neo4j/password"
echo ""
