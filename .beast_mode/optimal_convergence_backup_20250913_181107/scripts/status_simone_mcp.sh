#!/bin/bash
# Check Simone MCP Server Daemon Status

set -e

# Configuration
PROJECT_PATH="/Users/lou/kiro-2/kiro-ai-development-hackathon"
PID_FILE="$PROJECT_PATH/.simone/simone_mcp.pid"
LOG_FILE="$PROJECT_PATH/.simone/simone_mcp.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📊 Simone MCP Server Status${NC}"
echo "=================================="

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo -e "${RED}❌ Status: Not Running${NC}"
    echo -e "${RED}📝 Reason: No PID file found${NC}"
    exit 1
fi

# Read PID
PID=$(cat "$PID_FILE")

# Check if process is running
if ps -p "$PID" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Status: Running${NC}"
    echo -e "${GREEN}🆔 PID: $PID${NC}"
    
    # Get process info
    PROCESS_INFO=$(ps -p "$PID" -o pid,ppid,etime,pcpu,pmem,comm --no-headers 2>/dev/null || echo "N/A")
    if [ "$PROCESS_INFO" != "N/A" ]; then
        echo -e "${GREEN}📊 Process Info: $PROCESS_INFO${NC}"
    fi
    
    # Check log file
    if [ -f "$LOG_FILE" ]; then
        LOG_SIZE=$(ls -lh "$LOG_FILE" | awk '{print $5}')
        echo -e "${GREEN}📝 Log File: $LOG_FILE (Size: $LOG_SIZE)${NC}"
        
        # Show last few lines of log
        echo -e "${BLUE}📋 Recent Log Entries:${NC}"
        tail -5 "$LOG_FILE" | sed 's/^/  /'
    fi
    
    # Check if MCP server is responding (basic check)
    echo -e "${BLUE}🔍 Testing MCP Server Response...${NC}"
    if timeout 3 bash -c 'echo "{\"jsonrpc\": \"2.0\", \"id\": 1, \"method\": \"tools/list\", \"params\": {}}" | PROJECT_PATH="/Users/lou/kiro-2/kiro-ai-development-hackathon" node kiro_simone_adapter/mcp-server/dist/index.js' >/dev/null 2>&1; then
        echo -e "${GREEN}✅ MCP Server responding to commands${NC}"
    else
        echo -e "${YELLOW}⚠️  MCP Server not responding to commands${NC}"
    fi
    
else
    echo -e "${RED}❌ Status: Not Running${NC}"
    echo -e "${RED}📝 Reason: Process not found (PID: $PID)${NC}"
    echo -e "${YELLOW}🧹 Removing stale PID file${NC}"
    rm -f "$PID_FILE"
    exit 1
fi





