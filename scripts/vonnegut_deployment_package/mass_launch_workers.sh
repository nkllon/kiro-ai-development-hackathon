#!/bin/bash

# Mass launch all remaining critical tasks
TASKS=(
    "2.3" "3.2" "3.3" "4.2" "4.3" "5.2" "5.3" 
    "6.2" "6.3" "7.2" "7.3" "8.1" "8.2" "8.3"
    "9.1" "9.2" "9.3" "10.1" "10.2" "10.3"
    "11.1" "11.2" "11.3" "12.1" "12.2" "12.3"
)

launch_worker() {
    local task_id=$1
    local prompt_file="prompts/task-$task_id-enhanced.md"
    local log_file="logs/workers/task-$task_id-claude.log"
    
    if [[ -f "$prompt_file" ]]; then
        echo "Launching worker for task $task_id..."
        cat "$prompt_file" | claude --print --output-format json --permission-mode bypassPermissions > "$log_file" 2>&1 &
        local pid=$!
        echo "$pid" > "logs/workers/task-$task_id.pid"
        echo "{\"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"event\": \"worker_launched\", \"task\": \"$task_id\", \"pid\": $pid}" | tee -a logs/coordinator.log
    else
        echo "Prompt file missing for task $task_id, skipping..."
    fi
}

echo "=== MASS WORKER LAUNCH ==="
echo "Launching workers for ${#TASKS[@]} tasks..."

for task in "${TASKS[@]}"; do
    launch_worker "$task"
    sleep 1  # Small delay to prevent overwhelming
done

echo "=== LAUNCH COMPLETE ==="
echo "Total workers launched: ${#TASKS[@]}"
echo "Check logs/workers/ for individual worker logs"