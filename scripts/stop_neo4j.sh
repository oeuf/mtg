#!/bin/bash
# Stop Neo4j container for MTG Knowledge Graph

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "Stopping Neo4j container..."
docker-compose down

echo "Neo4j stopped."
