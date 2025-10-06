#!/bin/bash
# Quick status check for constellation execution
# Usage: ./scripts/constellation_status.sh

STATUS_FILE="${1:-.kiro/execution-status.json}"

if [ ! -f "$STATUS_FILE" ]; then
    echo "❌ No execution in progress"
    echo ""
    echo "🚀 Start execution with:"
    echo "   python3 scripts/constellation_orchestrator.py 10"
    exit 1
fi

echo "=== Constellation Execution Status ==="
echo ""

# Check if jq is available
if command -v jq &> /dev/null; then
    # Use jq for pretty formatting
    jq -r '
      "🆔 Execution ID: \(.execution_id)",
      "🕐 Started: \(.started_at)",
      "📊 Status: \(.status | ascii_upcase)",
      "👥 Max Agents: \(.max_agents)",
      "",
      "Progress:",
      "  📦 Total: \(.prompts | length)",
      "  ⏳ Pending: \([.prompts[] | select(.status == "pending")] | length)",
      "  🔄 Running: \([.prompts[] | select(.status == "running")] | length)",
      "  ✅ Completed: \([.prompts[] | select(.status == "completed")] | length)",
      "  ❌ Failed: \([.prompts[] | select(.status == "failed")] | length)",
      "",
      if ([.prompts[] | select(.status == "completed")] | length) > 0 then
        "⏱️  Average Duration: \(
          ([.prompts[] | select(.duration_min != null) | .duration_min] | add / length)
        ) min"
      else
        ""
      end
    ' "$STATUS_FILE"

    # Show currently running prompts
    RUNNING=$(jq -r '.prompts | to_entries[] | select(.value.status == "running") | "  🔄 [\(.value.agent_id)] \(.key)"' "$STATUS_FILE")
    if [ -n "$RUNNING" ]; then
        echo ""
        echo "Currently Running:"
        echo "$RUNNING"
    fi

    # Show recently completed (last 3)
    COMPLETED=$(jq -r '
      [.prompts | to_entries[] | select(.value.status == "completed")] |
      sort_by(.value.completed_at) | reverse | .[0:3][] |
      "  ✅ [\(.value.agent_id)] \(.key) (\(.value.duration_min) min)"
    ' "$STATUS_FILE")
    if [ -n "$COMPLETED" ]; then
        echo ""
        echo "Recently Completed:"
        echo "$COMPLETED"
    fi

    # Show failed prompts
    FAILED=$(jq -r '.prompts | to_entries[] | select(.value.status == "failed") | "  ❌ \(.key)"' "$STATUS_FILE")
    if [ -n "$FAILED" ]; then
        echo ""
        echo "Failed Prompts:"
        echo "$FAILED"
    fi
else
    # Fallback to basic grep if jq not available
    echo "🆔 Execution ID: $(grep -o '"execution_id": "[^"]*"' "$STATUS_FILE" | cut -d'"' -f4)"
    echo "📊 Status: $(grep -o '"status": "[^"]*"' "$STATUS_FILE" | head -1 | cut -d'"' -f4 | tr '[:lower:]' '[:upper:]')"
    echo ""
    echo "⚠️  Install 'jq' for detailed status: brew install jq"
fi

echo ""
echo "📊 Full dashboard: python3 scripts/constellation_monitor.py"
