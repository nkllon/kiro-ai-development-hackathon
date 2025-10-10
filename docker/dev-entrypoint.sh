#!/bin/bash
# Development entrypoint script for Beast Mode AI Development Framework

set -e

echo "🚀 Starting Beast Mode AI Development Framework (Development Mode)"

# Start Redis in background if not already running
if ! pgrep -x "redis-server" > /dev/null; then
    echo "📦 Starting Redis server..."
    redis-server --daemonize yes --port 6379
    sleep 2
fi

# Validate installation
echo "🔍 Validating development environment..."
python3 scripts/installation_validator.py --quick

# Load environment variables
if [ -f "/app/.env" ]; then
    echo "📋 Loading environment variables from .env"
    export $(grep -v '^#' /app/.env | xargs)
fi

# Run any initialization scripts
if [ -f "/app/scripts/dev_init.py" ]; then
    echo "🔧 Running development initialization..."
    python3 scripts/dev_init.py
fi

# Start the application with the provided command
echo "🎯 Starting application: $@"
exec "$@"