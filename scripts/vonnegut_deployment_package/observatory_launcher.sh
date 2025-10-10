#!/bin/bash
# Observatory Launcher Script for macOS LaunchAgent
# This wrapper handles PATH and environment setup

# Set up environment
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="$HOME"

# Change to project directory
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# Set Python path
export PYTHONPATH="$PROJECT_ROOT"

# Use virtual environment Python if available
if [ -f "$PROJECT_ROOT/.venv/bin/python" ]; then
    PYTHON_EXEC="$PROJECT_ROOT/.venv/bin/python"
else
    PYTHON_EXEC="python3"
fi

# Start Observatory with proper environment
exec "$PYTHON_EXEC" scripts/start_observatory_production.py