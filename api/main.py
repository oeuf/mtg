"""FastAPI application for MTG Knowledge Graph API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import commanders, cards

app = FastAPI(
    title="MTG Commander Knowledge Graph API",
    description="API for Commander deck building recommendations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
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
