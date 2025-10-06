#!/bin/bash
# Start Simone MCP Server Daemon

set -e

# Configuration
PROJECT_PATH="/Users/lou/kiro-2/kiro-ai-development-hackathon"
MCP_SERVER_PATH="$PROJECT_PATH/kiro_simone_adapter/mcp-server/dist/index.js"
PID_FILE="$PROJECT_PATH/.simone/simone_mcp.pid"
LOG_FILE="$PROJECT_PATH/.simone/simone_mcp.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Starting Simone MCP Server Daemon${NC}"

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Simone MCP Server is already running (PID: $PID)${NC}"
        exit 0
    else
        echo -e "${YELLOW}🧹 Removing stale PID file${NC}"
        rm -f "$PID_FILE"
    fi
fi

# Ensure directories exist
mkdir -p "$(dirname "$PID_FILE")"
mkdir -p "$(dirname "$LOG_FILE")"

# Check if MCP server binary exists
if [ ! -f "$MCP_SERVER_PATH" ]; then
    echo -e "${RED}❌ MCP server binary not found at: $MCP_SERVER_PATH${NC}"
    exit 1
fi

# Check if Node.js is available
if ! command -v node >/dev/null 2>&1; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Starting Simone MCP Server...${NC}"

# Start the server in background
export PROJECT_PATH="$PROJECT_PATH"
nohup node "$MCP_SERVER_PATH" > "$LOG_FILE" 2>&1 &
SERVER_PID=$!

# Save PID
echo "$SERVER_PID" > "$PID_FILE"

# Wait a moment to check if it started successfully
sleep 2

if ps -p "$SERVER_PID" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Simone MCP Server started successfully (PID: $SERVER_PID)${NC}"
    echo -e "${GREEN}📝 Logs: $LOG_FILE${NC}"
    echo -e "${GREEN}🆔 PID: $PID_FILE${NC}"
else
    echo -e "${RED}❌ Failed to start Simone MCP Server${NC}"
    echo -e "${RED}📝 Check logs: $LOG_FILE${NC}"
    rm -f "$PID_FILE"
    exit 1
fi





