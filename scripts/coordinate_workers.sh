#!/bin/bash

# Background coordination script
COORD_LOG="logs/coordinator.log"
WORKER_DIR="logs/workers"
PROMPT_DIR="prompts"

log_event() {
    echo "{\"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"event\": \"$1\", \"details\": \"$2\"}" | tee -a "$COORD_LOG"
}

launch_worker() {
    local task_id=$1
    local prompt_file="$PROMPT_DIR/task-$task_id-enhanced.md"
    local log_file="$WORKER_DIR/task-$task_id-claude.log"
    
    if [[ -f "$prompt_file" ]]; then
        log_event "launching_worker" "task_$task_id"
        cat "$prompt_file" | claude --print --output-format json --permission-mode bypassPermissions > "$log_file" 2>&1 &
        local pid=$!
        echo "$pid" > "$WORKER_DIR/task-$task_id.pid"
        log_event "worker_launched" "task_$task_id pid_$pid"
    fi
}

monitor_worker() {
    local task_id=$1
    local log_file="$WORKER_DIR/task-$task_id-claude.log"
    local pid_file="$WORKER_DIR/task-$task_id.pid"
    local last_size=0
    local stuck_count=0
    
    while [[ -f "$pid_file" ]]; do
        local pid=$(cat "$pid_file" 2>/dev/null)
        
        # Check if process is still running
        if ! kill -0 "$pid" 2>/dev/null; then
            log_event "worker_completed" "task_$task_id"
            rm -f "$pid_file"
            break
        fi
        
        # Check for progress
        if [[ -f "$log_file" ]]; then
            local current_size=$(wc -c < "$log_file" 2>/dev/null || echo 0)
            if [[ $current_size -gt $last_size ]]; then
                stuck_count=0
                log_event "worker_progress" "task_$task_id size_$current_size"
                last_size=$current_size
            else
                stuck_count=$((stuck_count + 1))
                if [[ $stuck_count -ge 10 ]]; then  # 5 minutes stuck
                    log_event "worker_stuck" "task_$task_id duration_${stuck_count}0s"
                    # Launch diagnostic
                    echo "Task $task_id appears stuck, launching diagnostic..." | claude --print --output-format json > "$WORKER_DIR/diagnostic-$task_id.log" 2>&1 &
                    stuck_count=0
                fi
            fi
        fi
        sleep 30
    done
}

# Main coordination loop
log_event "coordinator_start" "background_mode"

# Launch initial workers
launch_worker "1"
launch_worker "2.1"

# Monitor workers in background
monitor_worker "1" &
monitor_worker "2.1" &

# Create status file for main session to check
while true; do
    {
        echo "=== Worker Status $(date) ==="
        echo "Active PIDs:"
        ls -1 "$WORKER_DIR"/*.pid 2>/dev/null | while read pidfile; do
            task=$(basename "$pidfile" .pid)
            pid=$(cat "$pidfile" 2>/dev/null)
            if kill -0 "$pid" 2>/dev/null; then
                echo "  $task: RUNNING (PID $pid)"
            else
                echo "  $task: COMPLETED"
                rm -f "$pidfile"
            fi
        done
        echo
        echo "Log sizes:"
        ls -la "$WORKER_DIR"/*.log 2>/dev/null | awk '{print "  " $9 ": " $5 " bytes"}'
        echo
    } > logs/worker_status.txt
    
    sleep 60
done