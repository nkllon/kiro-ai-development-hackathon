#!/bin/bash

# Real-time worker monitoring script
echo "=== CURSOR FLEET MONITORING ==="
echo "Time: $(date)"
echo

WORKERS=(
    "2.2:Intelligent HTTP Polling"
    "3.2:Tunnel Diagnostics" 
    "4.1:Automated Recovery"
    "5.1:Bot Protection Integration"
    "6.2:HTTP Polling Tests"
    "7.2:Deployment Automation"
    "8.1:Connection Optimization"
    "test-probe:Comprehensive Validation"
)

echo "Active Workers:"
for worker in "${WORKERS[@]}"; do
    task_id=$(echo "$worker" | cut -d: -f1)
    description=$(echo "$worker" | cut -d: -f2)
    log_file="logs/workers/task-$task_id-cursor.log"
    
    if [[ "$task_id" == "test-probe" ]]; then
        log_file="logs/workers/test-probe-cursor.log"
    fi
    
    if [[ -f "$log_file" ]]; then
        size=$(wc -c < "$log_file" 2>/dev/null || echo 0)
        if [[ $size -gt 0 ]]; then
            echo "  ✅ $task_id: $description ($size bytes)"
        else
            echo "  🔄 $task_id: $description (starting...)"
        fi
    else
        echo "  ❌ $task_id: $description (not found)"
    fi
done

echo
echo "System Resources:"
echo "  CPU: $(top -l 1 -n 0 | grep "CPU usage" | awk '{print $3}' | sed 's/%//')"
echo "  Memory: $(top -l 1 -n 0 | grep "PhysMem" | awk '{print $2}')"
echo "  Active Processes: $(ps aux | grep cursor | grep -v grep | wc -l | tr -d ' ')"

echo
echo "Recent Activity:"
tail -3 logs/coordinator.log 2>/dev/null | while read line; do
    echo "  $line"
done