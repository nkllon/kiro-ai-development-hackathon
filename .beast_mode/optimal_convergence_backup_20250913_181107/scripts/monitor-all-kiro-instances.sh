#!/bin/bash
# Monitor All Kiro Instances - Beast Mode DNA Ecosystem
# Comprehensive monitoring of all Kiro processes and their Beast Mode DNA status

set -e

echo "🔍 Beast Mode DNA Ecosystem Monitor"
echo "==================================="
echo "Timestamp: $(date)"
echo ""

# Get all Kiro processes
echo "📊 All Kiro Instances:"
echo "====================="
KIRO_PIDS=$(ps aux | grep -i "kiro" | grep -v grep | grep "Electron\|Renderer" | awk '{print $2}' | head -10)

if [ -z "$KIRO_PIDS" ]; then
    echo "❌ No Kiro instances found"
    exit 0
fi

echo "Found $(echo "$KIRO_PIDS" | wc -l) Kiro instances"
echo ""

# Create a table header
printf "%-8s %-8s %-10s %-8s %-12s %-20s %-15s\n" "PID" "PPID" "ELAPSED" "%CPU" "STATUS" "WINDOW-CONFIG" "DNA-STATUS"
printf "%-8s %-8s %-10s %-8s %-12s %-20s %-15s\n" "----" "----" "-------" "----" "------" "-------------" "----------"

# Monitor each Kiro instance
for PID in $KIRO_PIDS; do
    if kill -0 $PID 2>/dev/null; then
        # Get process details
        PROCESS_INFO=$(ps -p $PID -o ppid,etime,pcpu --no-headers 2>/dev/null || echo "? ? ?")
        PARENT_PID=$(echo $PROCESS_INFO | awk '{print $1}')
        ELAPSED=$(echo $PROCESS_INFO | awk '{print $2}')
        CPU=$(echo $PROCESS_INFO | awk '{print $3}')
        
        # Get window config if available
        WINDOW_CONFIG=$(ps -p $PID -o command --no-headers 2>/dev/null | grep -o "vscode:[a-f0-9-]*" | head -1 || echo "unknown")
        WINDOW_CONFIG=${WINDOW_CONFIG#vscode:}
        WINDOW_CONFIG=${WINDOW_CONFIG:0:8}...
        
        # Determine status
        if [ "$PID" = "88032" ]; then
            STATUS="FRESH-DNA"
            DNA_STATUS="🧬 ACTIVE"
        elif [ "$PID" = "50776" ] || [ "$PID" = "37779" ] || [ "$PID" = "82297" ]; then
            STATUS="MAIN"
            DNA_STATUS="📋 PARENT"
        else
            STATUS="HELPER"
            DNA_STATUS="🔧 SUPPORT"
        fi
        
        printf "%-8s %-8s %-10s %-8s %-12s %-20s %-15s\n" "$PID" "$PARENT_PID" "$ELAPSED" "$CPU%" "$STATUS" "$WINDOW_CONFIG" "$DNA_STATUS"
    fi
done

echo ""
echo "🧬 Beast Mode DNA Status Analysis:"
echo "=================================="

# Check the fresh DNA instance specifically
FRESH_DNA_PID="88032"
if kill -0 $FRESH_DNA_PID 2>/dev/null; then
    echo "✅ Fresh DNA Instance (PID: $FRESH_DNA_PID) - ACTIVE"
    
    # Check DNA files
    DNA_PATH="../gke-hackathon-worktree/hackathons/gke-ai-microservices/.kiro/BEAST_MODE_DNA.md"
    if [ -f "$DNA_PATH" ]; then
        DNA_SIZE=$(wc -l < "$DNA_PATH")
        echo "   🧬 DNA Spore: $DNA_SIZE lines"
    else
        echo "   ❌ DNA Spore: NOT FOUND"
    fi
    
    # Check steering rules
    STEERING_PATH="../gke-hackathon-worktree/hackathons/gke-ai-microservices/.kiro/steering"
    if [ -d "$STEERING_PATH" ]; then
        STEERING_COUNT=$(ls "$STEERING_PATH" | wc -l)
        echo "   📋 Steering Rules: $STEERING_COUNT files"
    else
        echo "   ❌ Steering Rules: NOT FOUND"
    fi
    
    # Check deployment scripts
    DEPLOY_PATH="../gke-hackathon-worktree/hackathons/gke-ai-microservices/scripts/deploy-autopilot.sh"
    if [ -f "$DEPLOY_PATH" ] && [ -x "$DEPLOY_PATH" ]; then
        echo "   🚀 Deployment Script: READY"
    else
        echo "   ❌ Deployment Script: NOT READY"
    fi
    
else
    echo "❌ Fresh DNA Instance (PID: $FRESH_DNA_PID) - NOT RUNNING"
fi

echo ""
echo "📈 Resource Usage Summary:"
echo "========================="

# Memory usage by all Kiro processes
TOTAL_MEMORY=$(ps aux | grep -i "kiro" | grep -v grep | awk '{sum += $4} END {printf "%.1f", sum}')
echo "Total Memory Usage: ${TOTAL_MEMORY}%"

# CPU usage by all Kiro processes  
TOTAL_CPU=$(ps aux | grep -i "kiro" | grep -v grep | awk '{sum += $3} END {printf "%.1f", sum}')
echo "Total CPU Usage: ${TOTAL_CPU}%"

# Count by type
MAIN_COUNT=$(ps aux | grep -i "kiro" | grep -v grep | grep "Electron" | wc -l)
RENDERER_COUNT=$(ps aux | grep -i "kiro" | grep -v grep | grep "Renderer" | wc -l)
HELPER_COUNT=$(ps aux | grep -i "kiro" | grep -v grep | grep "Helper" | wc -l)

echo "Process Breakdown:"
echo "  Main Processes: $MAIN_COUNT"
echo "  Renderer Processes: $RENDERER_COUNT"  
echo "  Helper Processes: $HELPER_COUNT"

echo ""
echo "🎯 Beast Mode DNA Test Status:"
echo "=============================="

# Check PID file
PID_FILE="/tmp/kiro-beast-mode-test.pid"
if [ -f "$PID_FILE" ]; then
    TRACKED_PID=$(cat "$PID_FILE")
    if kill -0 $TRACKED_PID 2>/dev/null; then
        echo "✅ Tracked Test Instance: PID $TRACKED_PID (RUNNING)"
    else
        echo "⚠️  Tracked Test Instance: PID $TRACKED_PID (STOPPED)"
    fi
else
    echo "ℹ️  No tracked test instance (no PID file)"
fi

# Check worktree status
WORKTREE_PATH="../gke-hackathon-worktree"
if [ -d "$WORKTREE_PATH" ]; then
    echo "✅ Beast Mode Worktree: AVAILABLE"
    
    # Check git status
    if git -C "$WORKTREE_PATH" status >/dev/null 2>&1; then
        BRANCH=$(git -C "$WORKTREE_PATH" branch --show-current)
        echo "   📂 Branch: $BRANCH"
        
        # Check submodule status
        SUBMODULE_STATUS=$(git -C "$WORKTREE_PATH" submodule status 2>/dev/null | head -1)
        if [ -n "$SUBMODULE_STATUS" ]; then
            echo "   🔗 Submodule: INITIALIZED"
        else
            echo "   ⚠️  Submodule: NOT INITIALIZED"
        fi
    else
        echo "   ❌ Git Status: ERROR"
    fi
else
    echo "❌ Beast Mode Worktree: NOT FOUND"
fi

echo ""
echo "🔄 Monitoring Commands:"
echo "======================"
echo "# Continuous monitoring (refresh every 5 seconds):"
echo "watch -n 5 './scripts/monitor-all-kiro-instances.sh'"
echo ""
echo "# Monitor specific fresh DNA instance:"
echo "./scripts/monitor-kiro-instance.sh"
echo ""
echo "# Kill all Kiro instances (DANGER!):"
echo "ps aux | grep -i 'kiro' | grep -v grep | awk '{print \$2}' | xargs kill"
echo ""
echo "# Kill only the fresh DNA test instance:"
echo "./scripts/kill-kiro-instance.sh"

echo ""
echo "🧬 Beast Mode DNA Ecosystem Monitor Complete!"
echo "============================================="
echo ""

# Show recent activity
echo "📋 Recent Kiro Activity (last 5 processes by start time):"
ps aux | grep -i "kiro" | grep -v grep | sort -k9 | tail -5 | awk '{printf "%-8s %-10s %-8s %s\n", $2, $9, $3"%", $11}'

echo ""
echo "🎉 All Kiro instances monitored successfully!"