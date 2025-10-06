#!/bin/bash
# Monitor Fresh Kiro Instance Beast Mode DNA Consumption
# Tracks PID and monitors Beast Mode DNA spore assimilation

set -e

PID_FILE=${1:-"/tmp/kiro-beast-mode-test.pid"}
WORKTREE_PATH=${2:-"../gke-hackathon-worktree/hackathons/gke-ai-microservices"}

echo "🔍 Beast Mode DNA Spore Consumption Monitor"
echo "==========================================="
echo "PID File: $PID_FILE"
echo "Worktree: $WORKTREE_PATH"
echo ""

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "❌ PID file not found: $PID_FILE"
    echo "Launch Kiro first with:"
    echo "./scripts/launch-kiro-worktree.sh ../gke-hackathon-worktree hackathons/gke-ai-microservices true"
    exit 1
fi

# Read PID
KIRO_PID=$(cat "$PID_FILE")
echo "📍 Tracking Kiro PID: $KIRO_PID"

# Check if process is running
if ! kill -0 $KIRO_PID 2>/dev/null; then
    echo "❌ Kiro process not running (PID: $KIRO_PID)"
    echo "Cleaning up PID file..."
    rm -f "$PID_FILE"
    exit 1
fi

echo "✅ Kiro process is running"
echo ""

# Show process details
echo "🔍 Process Details:"
echo "=================="
ps -p $KIRO_PID -o pid,ppid,etime,pcpu

echo ""
echo "🧬 Beast Mode DNA Status:"
echo "========================"

# Check DNA file
DNA_FILE="$WORKTREE_PATH/.kiro/BEAST_MODE_DNA.md"
if [ -f "$DNA_FILE" ]; then
    echo "✅ Beast Mode DNA found: $DNA_FILE"
    echo "📊 DNA size: $(wc -l < "$DNA_FILE") lines"
else
    echo "❌ Beast Mode DNA not found: $DNA_FILE"
fi

# Check steering rules
STEERING_DIR="$WORKTREE_PATH/.kiro/steering"
if [ -d "$STEERING_DIR" ]; then
    echo "✅ Steering rules found: $STEERING_DIR"
    echo "📋 Steering files: $(ls "$STEERING_DIR" | wc -l)"
    ls "$STEERING_DIR"
else
    echo "❌ Steering directory not found: $STEERING_DIR"
fi

# Check deployment scripts
DEPLOY_SCRIPT="$WORKTREE_PATH/scripts/deploy-autopilot.sh"
if [ -f "$DEPLOY_SCRIPT" ]; then
    echo "✅ Deployment script found: $DEPLOY_SCRIPT"
    echo "🚀 Script is executable: $(test -x "$DEPLOY_SCRIPT" && echo 'Yes' || echo 'No')"
else
    echo "❌ Deployment script not found: $DEPLOY_SCRIPT"
fi

echo ""
echo "📊 System Resource Usage:"
echo "========================="
echo "Memory usage by Kiro processes:"
ps aux | grep -i "kiro" | grep -v grep | awk '{print $2, $3, $4, $11}' | head -10

echo ""
echo "🎯 DNA Consumption Test Commands:"
echo "================================="
echo "# Test if fresh Kiro instance can explain GKE Autopilot:"
echo "# (Run these in the Kiro instance)"
echo ""
echo "cat .kiro/BEAST_MODE_DNA.md | head -20"
echo "ls .kiro/steering/"
echo "./scripts/deploy-autopilot.sh --help"
echo ""

echo "🔄 Monitoring Commands:"
echo "======================"
echo "# Continuous monitoring:"
echo "watch -n 5 './scripts/monitor-kiro-instance.sh'"
echo ""
echo "# Stop monitoring and kill Kiro:"
echo "kill $KIRO_PID && rm $PID_FILE"
echo ""
echo "# Check process tree:"
echo "pstree -p $KIRO_PID"

echo ""
echo "🧬 Beast Mode DNA Spore Consumption Monitor Complete!"