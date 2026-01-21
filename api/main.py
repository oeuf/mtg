"""FastAPI application for MTG Knowledge Graph API."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import commanders, cards, decks, graph
from api.dependencies import get_neo4j_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Verify Neo4j connection on startup."""
    try:
        conn = get_neo4j_connection()
        # Verify we have data
        result = conn.execute_query("MATCH (c:Commander) RETURN count(c) as count")
        count = result[0]["count"] if result else 0
        if count == 0:
            print("WARNING: No commanders found in database. Run 'python main.py' to load data.")
        else:
            print(f"Connected to Neo4j. Found {count} commanders.")
    except Exception as e:
        print(f"ERROR: Failed to connect to Neo4j: {e}")
        print("Please set NEO4J_PASSWORD and ensure Neo4j is running.")
        raise
    yield


app = FastAPI(
    title="MTG Commander Knowledge Graph API",
    description="API for Commander deck building recommendations",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "MTG Commander Knowledge Graph API",
        "docs": "/docs",
        "version": "1.0.0"
    }


# Include routers
app.include_router(commanders.router)
app.include_router(cards.router)
app.include_router(decks.router)
app.include_router(graph.router)
