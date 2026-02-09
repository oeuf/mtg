"""FastAPI application entry point."""

from fastapi import FastAPI

from app.config import settings
from app.dependencies import lifespan

# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.app_name,
    description="ML-powered Magic: The Gathering Commander deck builder and analyzer",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
