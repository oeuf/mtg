"""FastAPI application entry point."""

import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from neo4j.exceptions import ServiceUnavailable, SessionExpired
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.config import settings
from app.limiter import limiter
from app.dependencies import lifespan
from app.routers import cards, commanders, decks, graph

logger = logging.getLogger("mtg_api")

# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.app_name,
    description="ML-powered Magic: The Gathering Commander deck builder and analyzer",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    try:
        response = await call_next(request)
    except Exception:
        duration = time.time() - start
        logger.info("%s %s 500 %.3fs", request.method, request.url.path, duration)
        raise
    duration = time.time() - start
    logger.info("%s %s %s %.3fs", request.method, request.url.path, response.status_code, duration)
    return response


@app.exception_handler(ServiceUnavailable)
async def neo4j_unavailable_handler(request: Request, exc: ServiceUnavailable):
    return JSONResponse(status_code=503, content={"detail": "Database unavailable"})


@app.exception_handler(SessionExpired)
async def neo4j_session_expired_handler(request: Request, exc: SessionExpired):
    return JSONResponse(status_code=503, content={"detail": "Database session expired"})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


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
