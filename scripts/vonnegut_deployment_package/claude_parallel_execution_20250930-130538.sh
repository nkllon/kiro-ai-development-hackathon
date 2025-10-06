#!/bin/bash
# System Architecture Wiring Diagram - Parallel Execution with Cursor CLI
# Generated: 2025-09-30T13:05:38.173374
# Execution ID: 20250930-130538

set -e  # Exit on any error

echo "🐺 Starting DAG-Orchestrated Parallel Execution with Cursor CLI 🐺"
echo "Execution ID: 20250930-130538"
echo "Log Directory: logs/claude-parallel-execution/20250930-130538"
echo ""

# Create log directory
mkdir -p logs/claude-parallel-execution/20250930-130538

# Function to run Claude task with proper logging
run_claude_task() {
    local task_id="$1"
    local task_name="$2" 
    local prompt_file="$3"
    local context_files="$4"
    local log_file="$5"
    
    echo "[${task_id}] Starting: ${task_name}"
    echo "[${task_id}] Prompt: ${prompt_file}"
    echo "[${task_id}] Context: ${context_files}"
    echo "[${task_id}] Log: ${log_file}"
    
    # Execute Cursor CLI with proper pipes and tees
    cat ${prompt_file} | cursor agent - ${context_files} 2>&1 | tee ${log_file} || {
        echo "[${task_id}] FAILED"
        return 1
    }
    
    echo "[${task_id}] COMPLETED"
    return 0
}

# Function to wait for parallel tasks
wait_for_tasks() {
    local pids=("$@")
    local failed=0
    
    for pid in "${pids[@]}"; do
        if ! wait "$pid"; then
            failed=1
        fi
    done
    
    return $failed
}


echo ""
echo "🚀 Phase 1: Executing 2 tasks in parallel with Cursor CLI"
echo "Tasks: 1.4, 1.6"
echo ""

# Start parallel Claude tasks for Phase 1
pids_1=()

# Task 1.4: Cloudflare Tunnel Discovery Implementation
run_claude_task "1.4" "Cloudflare Tunnel Discovery Implementation" "prompts/claude_execution_20250930-130538/task_1_4_prompt.txt" ".kiro/specs/system-architecture-wiring-diagram/tasks.md .kiro/specs/system-architecture-wiring-diagram/requirements.md cloudflare-tunnel-config-websocket.yml" "logs/claude-parallel-execution/20250930-130538/task-1.4-cloudflare-tunnel.log" &
pids_1+=($!)

# Task 1.6: Network Topology Discovery Implementation
run_claude_task "1.6" "Network Topology Discovery Implementation" "prompts/claude_execution_20250930-130538/task_1_6_prompt.txt" ".kiro/specs/system-architecture-wiring-diagram/tasks.md .kiro/specs/system-architecture-wiring-diagram/requirements.md Makefile" "logs/claude-parallel-execution/20250930-130538/task-1.6-network-topology.log" &
pids_1+=($!)

# Wait for Phase 1 completion
echo "Waiting for Phase 1 tasks to complete..."
if ! wait_for_tasks "${pids_1[@]}"; then
    echo "❌ Phase 1 had failures - check logs in logs/claude-parallel-execution/20250930-130538"
    exit 1
fi

echo "✅ Phase 1 completed successfully"

echo ""
echo "🚀 Phase 2: Executing 3 tasks in parallel with Claude CLI"
echo "Tasks: 2.1, 2.2, 2.3"
echo ""

# Start parallel Claude tasks for Phase 2
pids_2=()

# Task 2.1: DAG-Compliant Dependency Analysis Implementation
run_claude_task "2.1" "DAG-Compliant Dependency Analysis Implementation" "prompts/claude_execution_20250930-130538/task_2_1_prompt.txt" ".kiro/specs/system-architecture-wiring-diagram/tasks.md .kiro/specs/system-architecture-wiring-diagram/requirements.md src/rm_ddd/core/dag_registry.py" "logs/claude-parallel-execution/20250930-130538/task-2.1-dag-analysis.log" &
pids_2+=($!)

# Task 2.2: Comprehensive Data Flow Mapping Implementation
run_claude_task "2.2" "Comprehensive Data Flow Mapping Implementation" "prompts/claude_execution_20250930-130538/task_2_2_prompt.txt" ".kiro/specs/system-architecture-wiring-diagram/tasks.md .kiro/specs/system-architecture-wiring-diagram/requirements.md src/beast_mode/observatory/" "logs/claude-parallel-execution/20250930-130538/task-2.2-data-flow.log" &
pids_2+=($!)

# Task 2.3: Automation Chain Analysis Implementation
run_claude_task "2.3" "Automation Chain Analysis Implementation" "prompts/claude_execution_20250930-130538/task_2_3_prompt.txt" ".kiro/specs/system-architecture-wiring-diagram/tasks.md .kiro/specs/system-architecture-wiring-diagram/requirements.md Makefile" "logs/claude-parallel-execution/20250930-130538/task-2.3-automation-chain.log" &
pids_2+=($!)

# Wait for Phase 2 completion
echo "Waiting for Phase 2 tasks to complete..."
if ! wait_for_tasks "${pids_2[@]}"; then
    echo "❌ Phase 2 had failures - check logs in logs/claude-parallel-execution/20250930-130538"
    exit 1
fi

echo "✅ Phase 2 completed successfully"

echo ""
echo "🚀 Phase 3: Executing 4 tasks in parallel with Claude CLI"
echo "Tasks: 2.4, 3.1, 3.2, 3.3"
echo ""

# Start parallel Claude tasks for Phase 3
pids_3=()

# Task 2.4: Error Propagation Analysis Implementation
run_claude_task "2.4" "Error Propagation Analysis Implementation" "prompts/claude_execution_20250930-130538/task_2_4_prompt.txt" ".kiro/specs/system-architecture-wiring-diagram/tasks.md .kiro/specs/system-architecture-wiring-diagram/requirements.md" "logs/claude-parallel-execution/20250930-130538/task-2.4-error-propagation.log" &
pids_3+=($!)

# Task 3.1: Comprehensive Diagram Generation System Implementation
run_claude_task "3.1" "Comprehensive Diagram Generation System Implementation" "prompts/claude_execution_20250930-130538/task_3_1_prompt.txt" ".kiro/specs/system-architecture-wiring-diagram/tasks.md .kiro/specs/system-architecture-wiring-diagram/requirements.md" "logs/claude-parallel-execution/20250930-130538/task-3.1-diagram-generation.log" &
pids_3+=($!)

# Task 3.2: Observatory-Specific Sequence Diagrams Implementation
run_claude_task "3.2" "Observatory-Specific Sequence Diagrams Implementation" "prompts/claude_execution_20250930-130538/task_3_2_prompt.txt" ".kiro/specs/system-architecture-wiring-diagram/tasks.md .kiro/specs/system-architecture-wiring-diagram/requirements.md src/beast_mode/observatory/" "logs/claude-parallel-execution/20250930-130538/task-3.2-observatory-sequences.log" &
pids_3+=($!)

# Task 3.3: Network Topology Visualization Implementation
run_claude_task "3.3" "Network Topology Visualization Implementation" "prompts/claude_execution_20250930-130538/task_3_3_prompt.txt" ".kiro/specs/system-architecture-wiring-diagram/tasks.md .kiro/specs/system-architecture-wiring-diagram/requirements.md" "logs/claude-parallel-execution/20250930-130538/task-3.3-network-visualization.log" &
pids_3+=($!)

# Wait for Phase 3 completion
echo "Waiting for Phase 3 tasks to complete..."
if ! wait_for_tasks "${pids_3[@]}"; then
    echo "❌ Phase 3 had failures - check logs in logs/claude-parallel-execution/20250930-130538"
    exit 1
fi

echo "✅ Phase 3 completed successfully"

echo ""
echo "🚀 Phase 4: Executing 1 tasks in parallel with Claude CLI"
echo "Tasks: 3.4"
echo ""

# Start parallel Claude tasks for Phase 4
pids_4=()

# Task 3.4: Real-Time Diagram Updates Implementation
run_claude_task "3.4" "Real-Time Diagram Updates Implementation" "prompts/claude_execution_20250930-130538/task_3_4_prompt.txt" ".kiro/specs/system-architecture-wiring-diagram/tasks.md .kiro/specs/system-architecture-wiring-diagram/requirements.md" "logs/claude-parallel-execution/20250930-130538/task-3.4-real-time-updates.log" &
pids_4+=($!)

# Wait for Phase 4 completion
echo "Waiting for Phase 4 tasks to complete..."
if ! wait_for_tasks "${pids_4[@]}"; then
    echo "❌ Phase 4 had failures - check logs in logs/claude-parallel-execution/20250930-130538"
    exit 1
fi

echo "✅ Phase 4 completed successfully"

echo ""
echo "🎉 All phases completed successfully!"
echo "📊 Execution Summary:"
echo "  - Total Tasks: 10"
echo "  - Execution Phases: 4"
echo "  - Log Directory: logs/claude-parallel-execution/20250930-130538"
echo ""
echo "📋 Next Steps:"
echo "  1. Review logs in logs/claude-parallel-execution/20250930-130538/"
echo "  2. Validate task outputs and deliverables"
echo "  3. Run integration tests"
echo "  4. Generate final system architecture documentation"
echo ""
