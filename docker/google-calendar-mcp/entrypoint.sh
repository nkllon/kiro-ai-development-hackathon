#!/bin/bash
set -e

echo "🚀 Starting Google Calendar MCP Server..."
echo "Port: ${GOOGLE_CALENDAR_PORT:-3000}"
echo "Log Level: ${GOOGLE_CALENDAR_LOG_LEVEL:-info}"

# Validate environment
if [ ! -d "/app/src" ]; then
    echo "❌ Application source code not found"
    exit 1
fi

# Create credentials directory if it doesn't exist
mkdir -p /app/credentials

# Check for credentials file
if [ ! -f "/app/credentials/gcp-oauth.keys.json" ]; then
    echo "⚠️  No Google OAuth credentials found at /app/credentials/gcp-oauth.keys.json"
    echo "   Server will start in stub mode for testing"
fi

# Set Python path
export PYTHONPATH=/app

# Start the MCP server
echo "🔄 Launching MCP server..."
exec python3 -m src.beast_mode.mcp_integrations.google_calendar.main \
    --port "${GOOGLE_CALENDAR_PORT:-3000}" \
    --log-level "${GOOGLE_CALENDAR_LOG_LEVEL:-info}" \
    --credentials-file "/app/credentials/gcp-oauth.keys.json"