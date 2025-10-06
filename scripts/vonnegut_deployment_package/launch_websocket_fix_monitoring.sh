#!/bin/bash
# WebSocket Fix Monitoring Agent Launcher
# Launches the monitoring agent to oversee WebSocket fix deployment phases

set -euo pipefail

echo "🚀 WebSocket Fix Monitoring Agent Launcher"
echo "=========================================="
echo "Monitoring WebSocket fix agents (Phase 1, Phase 2, Phase 3)"
echo ""

# Configuration
CONFIG_FILE="websocket_fix_monitoring_config.yml"
LOG_DIR="logs"
PYTHON_SCRIPT="scripts/websocket_fix_monitoring_agent.py"

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Configuration file not found: $CONFIG_FILE"
    echo "   Creating default configuration..."
    cp websocket_fix_monitoring_config.yml "$CONFIG_FILE"
fi

# Create logs directory
mkdir -p "$LOG_DIR"

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ Monitoring agent script not found: $PYTHON_SCRIPT"
    exit 1
fi

# Check Python dependencies
echo "🔍 Checking Python dependencies..."
python3 -c "import psutil, yaml, requests" 2>/dev/null || {
    echo "❌ Missing required Python packages"
    echo "   Installing dependencies..."
    pip install psutil pyyaml requests
}

# Display configuration
echo "📋 Configuration:"
echo "   Config File: $CONFIG_FILE"
echo "   Log Directory: $LOG_DIR"
echo "   Python Script: $PYTHON_SCRIPT"
echo ""

# Parse command line arguments
PHASES=""
TEST_MODE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --phases)
            PHASES="--phases $2"
            shift 2
            ;;
        --test-mode)
            TEST_MODE="--test-mode"
            shift
            ;;
        --help)
            echo "Usage: $0 [--phases phase_1 phase_2 phase_3] [--test-mode]"
            echo ""
            echo "Options:"
            echo "  --phases     Specify which phases to monitor (default: all phases)"
            echo "  --test-mode  Run in test mode without starting actual agents"
            echo "  --help       Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Launch monitoring agent
echo "🚀 Launching WebSocket Fix Monitoring Agent..."
echo "   Press Ctrl+C to stop monitoring"
echo ""

# Run the monitoring agent
python3 "$PYTHON_SCRIPT" --config "$CONFIG_FILE" $PHASES $TEST_MODE

echo ""
echo "✅ WebSocket Fix Monitoring Agent completed"