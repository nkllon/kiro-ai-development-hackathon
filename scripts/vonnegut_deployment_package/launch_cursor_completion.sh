#!/bin/bash

# Launch all remaining tasks with Cursor workers
REMAINING_TASKS=(
    "2.3" "3.2" "3.3" "4.2" "4.3" "5.2" "5.3" 
    "6.2" "6.3" "7.2" "7.3" "8.1" "8.2" "8.3"
    "9.1" "9.2" "9.3" "10.1" "10.2" "10.3"
    "11.1" "11.2" "11.3" "12.1" "12.2" "12.3"
)

launch_cursor_worker() {
    local task_id=$1
    local prompt_file="prompts/task-$task_id-enhanced.md"
    local log_file="logs/workers/task-$task_id-cursor.log"
    
    if [[ -f "$prompt_file" ]]; then
        echo "Launching Cursor worker for task $task_id..."
        cursor agent --print --output-format json "$(cat $prompt_file)" > "$log_file" 2>&1 &
        local pid=$!
        echo "$pid" > "logs/workers/task-$task_id-cursor.pid"
        echo "{\"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"event\": \"cursor_worker_launched\", \"task\": \"$task_id\", \"pid\": $pid}" | tee -a logs/coordinator.log
    else
        echo "Need to create prompt for task $task_id..."
        echo "{\"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"event\": \"prompt_needed\", \"task\": \"$task_id\"}" | tee -a logs/coordinator.log
    fi
}

echo "=== CURSOR COMPLETION PHASE ==="
echo "Launching Cursor workers for ${#REMAINING_TASKS[@]} remaining tasks..."

for task in "${REMAINING_TASKS[@]}"; do
    launch_cursor_worker "$task"
    sleep 2  # Stagger launches
done

echo "=== CURSOR LAUNCH COMPLETE ==="
echo "Workers launched for ${#REMAINING_TASKS[@]} tasks"
echo "Cursor workers should complete the WebSocket remediation"