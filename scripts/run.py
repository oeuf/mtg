#!/usr/bin/env python3
"""Helper script for testing and running the MTG Commander Knowledge Graph application."""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path


ROOT_DIR = Path(__file__).parent.parent
API_DIR = ROOT_DIR
FRONTEND_DIR = ROOT_DIR / "frontend"


def check_neo4j_env():
    """Check if Neo4j environment variables are set."""
    password = os.environ.get("NEO4J_PASSWORD")
    if not password:
        print("ERROR: NEO4J_PASSWORD environment variable not set.")
        print("\nSet it with:")
        print("  export NEO4J_PASSWORD=your_password")
        return False
    return True


def run_api(port: int = 8000, reload: bool = True):
    """Start the FastAPI server."""
    if not check_neo4j_env():
        sys.exit(1)

    print(f"Starting API server on port {port}...")
    cmd = [
        sys.executable, "-m", "uvicorn",
        "api.main:app",
        "--port", str(port),
    ]
    if reload:
        cmd.append("--reload")

    subprocess.run(cmd, cwd=API_DIR)


def run_frontend():
    """Start the Next.js development server."""
    print("Starting frontend server...")
    subprocess.run(["npm", "run", "dev"], cwd=FRONTEND_DIR)


def run_tests(test_type: str = "all"):
    """Run tests."""
    if test_type in ("all", "unit", "backend"):
        print("Running backend tests...")
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v"],
            cwd=API_DIR
        )
        if result.returncode != 0 and test_type != "all":
            sys.exit(result.returncode)

    if test_type in ("all", "e2e", "frontend"):
        if not check_neo4j_env():
            print("Skipping E2E tests - Neo4j not configured")
            if test_type != "all":
                sys.exit(1)
            return

        print("Running E2E tests...")
        result = subprocess.run(
            ["npm", "run", "test:e2e"],
            cwd=FRONTEND_DIR
        )
        if result.returncode != 0:
            sys.exit(result.returncode)


def load_data():
    """Load card data into Neo4j."""
    if not check_neo4j_env():
        sys.exit(1)

    print("Loading card data into Neo4j...")
    subprocess.run([sys.executable, "main.py"], cwd=API_DIR)


def check_status():
    """Check the status of required services."""
    import urllib.request
    import urllib.error

    print("Checking service status...\n")

    # Check Neo4j env
    if os.environ.get("NEO4J_PASSWORD"):
        print("  NEO4J_PASSWORD: Set")
    else:
        print("  NEO4J_PASSWORD: NOT SET")

    # Check API
    try:
        urllib.request.urlopen("http://localhost:8000/health", timeout=2)
        print("  API (port 8000): Running")
    except (urllib.error.URLError, ConnectionRefusedError):
        print("  API (port 8000): Not running")

    # Check Frontend
    try:
        urllib.request.urlopen("http://localhost:3000", timeout=2)
        print("  Frontend (port 3000): Running")
    except (urllib.error.URLError, ConnectionRefusedError):
        print("  Frontend (port 3000): Not running")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="MTG Commander Knowledge Graph - Development Helper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run.py api          # Start the API server
  python scripts/run.py frontend     # Start the frontend
  python scripts/run.py test         # Run all tests
  python scripts/run.py test --type unit    # Run only unit tests
  python scripts/run.py test --type e2e     # Run only E2E tests
  python scripts/run.py load         # Load data into Neo4j
  python scripts/run.py status       # Check service status
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # API command
    api_parser = subparsers.add_parser("api", help="Start the API server")
    api_parser.add_argument("--port", type=int, default=8000, help="Port number")
    api_parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")

    # Frontend command
    subparsers.add_parser("frontend", help="Start the frontend server")

    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument(
        "--type",
        choices=["all", "unit", "e2e", "backend", "frontend"],
        default="all",
        help="Type of tests to run"
    )

    # Load command
    subparsers.add_parser("load", help="Load card data into Neo4j")

    # Status command
    subparsers.add_parser("status", help="Check service status")

    args = parser.parse_args()

    if args.command == "api":
        run_api(port=args.port, reload=not args.no_reload)
    elif args.command == "frontend":
        run_frontend()
    elif args.command == "test":
        run_tests(args.type)
    elif args.command == "load":
        load_data()
    elif args.command == "status":
        check_status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
