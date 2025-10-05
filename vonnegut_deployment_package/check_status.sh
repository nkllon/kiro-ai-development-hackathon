#!/bin/bash

# Quick status check script
echo "=== WebSocket Remediation Coordination Status ==="
echo "Time: $(date)"
echo

if [[ -f logs/worker_status.txt ]]; then
    cat logs/worker_status.txt
else
    echo "Status file not yet created..."
fi

echo
echo "=== Recent Coordinator Events ==="
tail -5 logs/coordinator.log 2>/dev/null || echo "No coordinator log yet"

echo
echo "=== Background Processes ==="
ps aux | grep -E "(coordinate_workers|claude)" | grep -v grep | head -5