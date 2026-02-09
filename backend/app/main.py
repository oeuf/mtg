"""FastAPI application entry point."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from neo4j.exceptions import ServiceUnavailable, SessionExpired

from app.config import settings
from app.dependencies import lifespan
from app.routers import cards, commanders, decks, graph

# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.app_name,
    description="ML-powered Magic: The Gathering Commander deck builder and analyzer",
    version="0.1.0",
    lifespan=lifespan,
)


@app.exception_handler(ServiceUnavailable)
async def neo4j_unavailable_handler(request: Request, exc: ServiceUnavailable):
    return JSONResponse(status_code=503, content={"detail": "Database unavailable"})


@app.exception_handler(SessionExpired)
async def neo4j_session_expired_handler(request: Request, exc: SessionExpired):
    return JSONResponse(status_code=503, content={"detail": "Database session expired"})


app.include_router(cards.router, prefix="/api")
app.include_router(commanders.router, prefix="/api")
app.include_router(decks.router, prefix="/api")
app.include_router(graph.router, prefix="/api")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
