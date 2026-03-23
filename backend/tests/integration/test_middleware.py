"""Tests for middleware: CORS, logging, error handling, rate limiting."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestCORS:
    def test_cors_headers_present(self, client):
        """OPTIONS request returns CORS headers."""
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert "access-control-allow-origin" in response.headers

    def test_cors_allows_frontend_origin(self, client):
        """Verify localhost:5173 is allowed."""
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.headers.get("access-control-allow-origin") in [
            "http://localhost:5173",
            "*",
        ]


class TestGlobalExceptionHandler:
    def test_unhandled_exception_returns_json(self):
        """Unhandled error returns JSON with 500."""

        @app.get("/test-error")
        async def error_route():
            raise RuntimeError("Test unhandled error")

        # raise_server_exceptions=False lets us inspect the 500 response
        with TestClient(app, raise_server_exceptions=False) as c:
            response = c.get("/test-error")
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data

    def test_health_still_works(self, client):
        """Health check still returns 200."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestRequestLogging:
    def test_request_logging_doesnt_break_requests(self, client):
        """Logging middleware doesn't break normal requests."""
        response = client.get("/health")
        assert response.status_code == 200


class TestRateLimiting:
    def test_slowapi_middleware_installed(self, client):
        """SlowAPI middleware is installed on the app."""
        assert hasattr(app.state, "limiter")
