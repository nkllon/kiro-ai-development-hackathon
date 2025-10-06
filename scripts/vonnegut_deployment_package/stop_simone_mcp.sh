#!/bin/bash
# Stop Simone MCP Server Daemon

set -e

# Configuration
PROJECT_PATH="/Users/lou/kiro-2/kiro-ai-development-hackathon"
PID_FILE="$PROJECT_PATH/.simone/simone_mcp.pid"
LOG_FILE="$PROJECT_PATH/.simone/simone_mcp.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🛑 Stopping Simone MCP Server Daemon${NC}"

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo -e "${YELLOW}⚠️  No PID file found. Server may not be running.${NC}"
    exit 0
fi

# Read PID
PID=$(cat "$PID_FILE")

# Check if process is running
if ! ps -p "$PID" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Process not running (PID: $PID). Removing stale PID file.${NC}"
    rm -f "$PID_FILE"
    exit 0
fi

echo -e "${GREEN}🔄 Stopping Simone MCP Server (PID: $PID)...${NC}"

# Try graceful shutdown first
kill -TERM "$PID" 2>/dev/null || true

# Wait for graceful shutdown
for i in {1..10}; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Simone MCP Server stopped gracefully${NC}"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# Force kill if still running
echo -e "${YELLOW}⚠️  Graceful shutdown failed, forcing stop...${NC}"
kill -KILL "$PID" 2>/dev/null || true

# Wait a moment and verify
sleep 1
if ps -p "$PID" > /dev/null 2>&1; then
    echo -e "${RED}❌ Failed to stop Simone MCP Server${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Simone MCP Server stopped forcefully${NC}"
    rm -f "$PID_FILE"
fi





