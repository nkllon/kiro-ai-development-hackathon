#!/bin/bash

# Task completion validation script
validate_task() {
    local task_id=$1
    local log_file="logs/workers/task-$task_id-cursor.log"
    
    echo "=== Validating Task $task_id ==="
    
    # Check if log file exists and has content
    if [[ ! -f "$log_file" || ! -s "$log_file" ]]; then
        echo "❌ No output log found for task $task_id"
        return 1
    fi
    
    # Check for completion status in JSON log
    if grep -q '"status": "completed"' "$log_file"; then
        echo "✅ Task $task_id claims completion"
    else
        echo "⚠️  Task $task_id did not report completion"
    fi
    
    # Check if actual files were created (based on task requirements)
    case "$task_id" in
        "1")
            # Task 1: Tunnel configuration files
            expected_files=(
                "src/beast_mode/observatory/tunnel/__init__.py"
                "src/beast_mode/observatory/tunnel/config_manager.py"
                "src/beast_mode/observatory/tunnel/validator.py"
                "tests/unit/tunnel/test_config_manager.py"
            )
            ;;
        "2.1")
            # Task 2.1: WebSocket manager files
            expected_files=(
                "src/beast_mode/observatory/websocket/__init__.py"
                "src/beast_mode/observatory/websocket/manager.py"
                "src/beast_mode/observatory/websocket/connection.py"
                "tests/unit/websocket/test_manager.py"
            )
            ;;
        "2.3")
            # Task 2.3: Health validation files
            expected_files=(
                "src/beast_mode/observatory/websocket/health_validator.py"
                "src/beast_mode/observatory/websocket/endpoint_monitor.py"
                "tests/unit/websocket/test_health_validator.py"
            )
            ;;
        *)
            echo "No validation rules defined for task $task_id yet"
            return 0
            ;;
    esac
    
    # Check if expected files exist
    local files_created=0
    local files_expected=${#expected_files[@]}
    
    for file in "${expected_files[@]}"; do
        if [[ -f "$file" ]]; then
            echo "✅ Created: $file"
            files_created=$((files_created + 1))
        else
            echo "❌ Missing: $file"
        fi
    done
    
    # Validate file contents aren't just stubs
    for file in "${expected_files[@]}"; do
        if [[ -f "$file" ]]; then
            local line_count=$(wc -l < "$file")
            if [[ $line_count -lt 10 ]]; then
                echo "⚠️  $file seems too short ($line_count lines) - might be stub"
            else
                echo "✅ $file has substantial content ($line_count lines)"
            fi
        fi
    done
    
    # Overall assessment
    if [[ $files_created -eq $files_expected ]]; then
        echo "✅ Task $task_id: All expected files created"
        return 0
    else
        echo "❌ Task $task_id: Only $files_created/$files_expected files created"
        return 1
    fi
}

# Validate specific task or all tasks
if [[ $# -eq 1 ]]; then
    validate_task "$1"
else
    echo "Usage: $0 <task_id>"
    echo "Example: $0 2.1"
fi