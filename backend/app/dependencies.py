"""Dependency injection for FastAPI."""

from contextlib import asynccontextmanager
from typing import Generator

from neo4j import GraphDatabase, Session

from app.config import settings


class Neo4jDriver:
    """Manages Neo4j driver singleton."""

    _driver = None

    @classmethod
    def initialize(cls):
        """Initialize the Neo4j driver."""
        if cls._driver is None:
            cls._driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )

    @classmethod
    def get_driver(cls):
        """Get the Neo4j driver instance."""
        if cls._driver is None:
            cls.initialize()
        return cls._driver

    @classmethod
    def close(cls):
        """Close the Neo4j driver."""
        if cls._driver is not None:
            cls._driver.close()
            cls._driver = None


def get_neo4j_session() -> Generator[Session, None, None]:
    """Dependency to get a Neo4j session."""
    driver = Neo4jDriver.get_driver()
    session = driver.session()
    try:
        yield session
    finally:
        session.close()


@asynccontextmanager
async def lifespan(app):
    """FastAPI lifespan context manager."""
    # Startup
    Neo4jDriver.initialize()
    yield
    # Shutdown
    Neo4jDriver.close()


from app.services.recommendation_service import RecommendationService


def get_recommendation_service() -> RecommendationService:
    """FastAPI dependency that provides a RecommendationService instance."""
    driver = Neo4jDriver.get_driver()
    return RecommendationService(driver)
