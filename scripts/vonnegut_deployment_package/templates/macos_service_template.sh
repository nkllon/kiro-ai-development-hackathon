#!/bin/bash
# macOS LaunchAgent Service Template
# Copy this template for any macOS service deployment

# =============================================================================
# ENVIRONMENT SETUP - Critical for macOS LaunchAgent compatibility
# =============================================================================

# Set explicit PATH (LaunchAgents don't inherit shell PATH)
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/sbin"

# Set required environment variables
export HOME="${HOME:-/Users/$(whoami)}"
export USER="${USER:-$(whoami)}"
export SHELL="${SHELL:-/bin/bash}"

# Change to project directory (use absolute path from script location)
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

# Set Python path for imports
export PYTHONPATH="$PROJECT_ROOT"

# =============================================================================
# SERVICE CONFIGURATION - Customize this section
# =============================================================================

SERVICE_NAME="your-service-name"
PYTHON_SCRIPT="scripts/your_service.py"
LOG_DIR="$PROJECT_ROOT/logs"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# =============================================================================
# LOGGING SETUP - Always log everything for debugging
# =============================================================================

exec > >(tee -a "$LOG_DIR/${SERVICE_NAME}.out.log") 2>&1

echo "$(date): Starting $SERVICE_NAME"
echo "PROJECT_ROOT: $PROJECT_ROOT"
echo "PATH: $PATH"
echo "PYTHONPATH: $PYTHONPATH"
echo "Python version: $(python3 --version)"

# =============================================================================
# SERVICE EXECUTION - Use absolute paths
# =============================================================================

# Find Python executable (prefer virtual environment if available)
if [ -f "$PROJECT_ROOT/.venv/bin/python" ]; then
    PYTHON_EXEC="$PROJECT_ROOT/.venv/bin/python"
elif [ -f "/opt/homebrew/bin/python3" ]; then
    PYTHON_EXEC="/opt/homebrew/bin/python3"
else
    PYTHON_EXEC="/usr/bin/python3"
fi

echo "Using Python: $PYTHON_EXEC"

# Execute the service
exec "$PYTHON_EXEC" "$PYTHON_SCRIPT"