#!/bin/bash
# Kill Fresh Kiro Instance and Clean Up
# Safely terminates the Beast Mode DNA test instance

set -e

PID_FILE=${1:-"/tmp/kiro-beast-mode-test.pid"}

echo "🛑 Killing Fresh Kiro Instance"
echo "=============================="
echo "PID File: $PID_FILE"
echo ""

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "❌ PID file not found: $PID_FILE"
    echo "No Kiro instance to kill"
    exit 0
fi

# Read PID
KIRO_PID=$(cat "$PID_FILE")
echo "📍 Target Kiro PID: $KIRO_PID"

# Check if process is running
if ! kill -0 $KIRO_PID 2>/dev/null; then
    echo "⚠️  Kiro process not running (PID: $KIRO_PID)"
    echo "Cleaning up stale PID file..."
    rm -f "$PID_FILE"
    exit 0
fi

echo "🔍 Process details before termination:"
ps -p $KIRO_PID -o pid,ppid,etime,cpu,mem,cmd

echo ""
echo "🛑 Terminating Kiro process..."

# Try graceful termination first
kill $KIRO_PID

# Wait a moment
sleep 2

# Check if it's still running
if kill -0 $KIRO_PID 2>/dev/null; then
    echo "⚠️  Process still running, forcing termination..."
    kill -9 $KIRO_PID
    sleep 1
fi

# Final check
if kill -0 $KIRO_PID 2>/dev/null; then
    echo "❌ Failed to terminate process (PID: $KIRO_PID)"
    exit 1
else
    echo "✅ Kiro process terminated successfully"
fi

# Clean up PID file
rm -f "$PID_FILE"
echo "🧹 PID file cleaned up: $PID_FILE"

echo ""
echo "📊 Remaining Kiro processes:"
echo "============================"
REMAINING_KIRO=$(ps aux | grep -i "kiro" | grep -v grep | wc -l)
echo "Count: $REMAINING_KIRO"

if [ $REMAINING_KIRO -gt 0 ]; then
    echo ""
    echo "Active Kiro processes:"
    ps aux | grep -i "kiro" | grep -v grep | head -5
fi

echo ""
echo "🎉 Fresh Kiro Instance Cleanup Complete!"
echo "========================================"
echo ""
echo "Beast Mode DNA spore consumption test session ended."
echo "Ready for next test cycle!"