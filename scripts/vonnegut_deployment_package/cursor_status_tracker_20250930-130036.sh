#!/bin/bash
# Execution Status Tracker for System Architecture Wiring Diagram
# Generated: 2025-09-30T13:00:36.995750

LOG_DIR="logs/cursor-parallel-execution/20250930-130036"

echo "📊 System Architecture Wiring Diagram - Execution Status"
echo "Execution ID: 20250930-130036"
echo "Log Directory: $LOG_DIR"
echo ""

# Function to check task status
check_task_status() {
    local task_id="$1"
    local task_name="$2"
    local log_pattern="$3"
    
    if ls ${log_pattern} 1> /dev/null 2>&1; then
        if grep -q "COMPLETED\|✅" ${log_pattern} 2>/dev/null; then
            echo "✅ [${task_id}] ${task_name} - COMPLETED"
        elif grep -q "FAILED\|❌\|ERROR" ${log_pattern} 2>/dev/null; then
            echo "❌ [${task_id}] ${task_name} - FAILED"
        else
            echo "🔄 [${task_id}] ${task_name} - RUNNING"
        fi
    else
        echo "⏳ [${task_id}] ${task_name} - PENDING"
    fi
}

echo "Task Status:"
check_task_status "1.4" "Cloudflare Tunnel Discovery" "logs/cursor-parallel-execution/20250930-130036/task-1.4-cloudflare-tunnel-discovery.log"
check_task_status "1.6" "Network Topology Discovery" "logs/cursor-parallel-execution/20250930-130036/task-1.6-network-topology-discovery.log"
check_task_status "2.1" "DAG-Compliant Dependency Analysis" "logs/cursor-parallel-execution/20250930-130036/task-2.1-dag-dependency-analysis.log"
check_task_status "2.2" "Comprehensive Data Flow Mapping" "logs/cursor-parallel-execution/20250930-130036/task-2.2-data-flow-mapping.log"
check_task_status "2.3" "Automation Chain Analysis" "logs/cursor-parallel-execution/20250930-130036/task-2.3-automation-chain-analysis.log"
check_task_status "2.4" "Error Propagation Analysis" "logs/cursor-parallel-execution/20250930-130036/task-2.4-error-propagation-analysis.log"
check_task_status "3.1" "Comprehensive Diagram Generation System" "logs/cursor-parallel-execution/20250930-130036/task-3.1-diagram-generation-system.log"
check_task_status "3.2" "Observatory-Specific Sequence Diagrams" "logs/cursor-parallel-execution/20250930-130036/task-3.2-observatory-sequence-diagrams.log"
check_task_status "3.3" "Network Topology Visualization" "logs/cursor-parallel-execution/20250930-130036/task-3.3-network-topology-visualization.log"
check_task_status "3.4" "Real-Time Diagram Updates" "logs/cursor-parallel-execution/20250930-130036/task-3.4-real-time-diagram-updates.log"

echo ""
echo "📁 Log Files:"
ls -la logs/cursor-parallel-execution/20250930-130036/ 2>/dev/null || echo "No log files yet"

echo ""
echo "🔍 Recent Activity:"
tail -n 5 logs/cursor-parallel-execution/20250930-130036/*.log 2>/dev/null | head -20 || echo "No recent activity"
