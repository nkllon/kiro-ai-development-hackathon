#!/bin/bash

# Worker monitoring script for coordinator
LOG_DIR="logs/workers"
COORDINATOR_LOG="logs/coordinator.log"

monitor_worker() {
    local task_id=$1
    local log_file="$LOG_DIR/task-$task_id-claude.log"
    local last_size=0
    local stuck_count=0
    
    while true; do
        if [[ -f "$log_file" ]]; then
            current_size=$(wc -c < "$log_file" 2>/dev/null || echo 0)
            
            if [[ $current_size -gt $last_size ]]; then
                # Progress detected
                stuck_count=0
                echo "{\"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"event\": \"worker_progress\", \"task\": \"$task_id\", \"log_size\": $current_size}" | tee -a "$COORDINATOR_LOG"
                last_size=$current_size
            else
                # No progress
                stuck_count=$((stuck_count + 1))
                if [[ $stuck_count -ge 10 ]]; then  # 5 minutes of no progress
                    echo "{\"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"event\": \"worker_stuck\", \"task\": \"$task_id\", \"stuck_duration\": \"${stuck_count}0s\"}" | tee -a "$COORDINATOR_LOG"
                    return 1
                fi
            fi
        fi
        sleep 30
    done
}

# Monitor both workers in parallel
monitor_worker "1" &
monitor_worker "2.1" &

wait