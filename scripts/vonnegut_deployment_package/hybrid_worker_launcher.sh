#!/bin/bash

# Hybrid worker launcher - Claude (cloud) first, Cursor (local/time-based) fallback
COORD_LOG="logs/coordinator.log"

log_event() {
    echo "{\"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"event\": \"$1\", \"details\": \"$2\"}" | tee -a "$COORD_LOG"
}

launch_claude_worker() {
    local task_id=$1
    local prompt_file="prompts/task-$task_id-enhanced.md"
    local log_file="logs/workers/task-$task_id-claude.log"
    
    if [[ -f "$prompt_file" ]]; then
        log_event "launching_claude_worker" "task_$task_id"
        cat "$prompt_file" | claude --print --output-format json --permission-mode bypassPermissions > "$log_file" 2>&1 &
        local pid=$!
        echo "$pid" > "logs/workers/task-$task_id-claude.pid"
        echo "$task_id:claude:$pid"
    fi
}

launch_cursor_worker() {
    local task_id=$1
    local prompt_file="prompts/task-$task_id-enhanced.md"
    local log_file="logs/workers/task-$task_id-cursor.log"
    
    if [[ -f "$prompt_file" ]]; then
        log_event "launching_cursor_worker" "task_$task_id"
        cursor agent --print --output-format json "$(cat $prompt_file)" > "$log_file" 2>&1 &
        local pid=$!
        echo "$pid" > "logs/workers/task-$task_id-cursor.pid"
        echo "$task_id:cursor:$pid"
    fi
}

check_claude_failure() {
    local log_file=$1
    if [[ -f "$log_file" ]]; then
        # Check for Claude cloud token limits or API errors
        if grep -q -E "(token limit|rate limit|quota exceeded|usage limit|API error)" "$log_file" 2>/dev/null; then
            return 0  # Claude cloud failed
        fi
    fi
    return 1  # Claude cloud OK
}

launch_with_fallback() {
    local task_id=$1
    
    # Try Claude first
    local claude_result=$(launch_claude_worker "$task_id")
    if [[ -n "$claude_result" ]]; then
        local claude_pid=$(echo "$claude_result" | cut -d: -f3)
        
        # Monitor for 30 seconds
        sleep 30
        
        # Check if Claude failed
        if check_claude_failure "logs/workers/task-$task_id-claude.log"; then
            log_event "claude_failed_switching_cursor" "task_$task_id"
            kill "$claude_pid" 2>/dev/null
            launch_cursor_worker "$task_id"
        else
            log_event "claude_worker_healthy" "task_$task_id"
        fi
    else
        # Claude launch failed, use Cursor
        log_event "claude_launch_failed_using_cursor" "task_$task_id"
        launch_cursor_worker "$task_id"
    fi
}

# Export function for parallel execution
export -f launch_with_fallback
export -f launch_claude_worker
export -f launch_cursor_worker
export -f check_claude_failure
export -f log_event

# Launch workers with fallback
REMAINING_TASKS=(
    "2.3" "3.2" "3.3" "4.2" "4.3" "5.2" "5.3" 
    "6.2" "6.3" "7.2" "7.3" "8.1" "8.2" "8.3"
)

echo "=== HYBRID WORKER LAUNCH ==="
log_event "hybrid_launch_start" "claude_primary_cursor_fallback"

for task in "${REMAINING_TASKS[@]}"; do
    launch_with_fallback "$task" &
    sleep 2  # Stagger launches
done

wait
log_event "hybrid_launch_complete" "all_workers_launched"