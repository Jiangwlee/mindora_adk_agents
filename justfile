# justfile
# pylint: skip-file
# type: ignore
# Justfile for Mindora ADK Agents

# Install dependencies
install:
    uv sync

# Run the FastAPI server
run:
    just run-backend &
    just run-web

run-backend:
    uv run python run_server.py --agents-dir backend/agents --allow-origins "http://localhost:4200"

# Run the FastAPI server with web interface
run-web:
    cd frontend && npm run serve --backend=http://localhost:8000

# Test imports
test:
    uv run python -c "from backend.fast_api import get_fast_api_app; from backend.api.adk_web_server import AdkWebServer; print('All imports successful!')"

# Check dependencies
deps:
    uv pip list | grep -E "(google|adk|fastapi)"

# Development server with hot reload
dev:
    uv run python -m uvicorn backend.fast_api:get_fast_api_app --host 0.0.0.0 --port 8000 --reload --factory