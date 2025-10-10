set -euo pipefail#!/bin/bash

# Beast Mode Self-Refactoring Recording Controls

start_recording() {
    local session_name="$1"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local filename="$HOME/Desktop/beast-mode-${session_name}-${timestamp}.mov"
    
    echo "🎬 Starting recording: $session_name"
    nohup screencapture -v -T 0 "$filename" > /dev/null 2>&1 &
    local pid=$!
    echo "$pid" > "/tmp/recording_${session_name}.pid"
    echo "📹 Recording started (PID: $pid) -> $filename"
    sleep 1
    if ps -p $pid > /dev/null; then
        echo "✅ Recording confirmed active"
    else
        echo "❌ Recording failed to start"
    fi
}

stop_recording() {
    local session_name="$1"
    local pid_file="/tmp/recording_${session_name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        echo "🛑 Stopping recording: $session_name (PID: $pid)"
        kill "$pid" 2>/dev/null
        rm "$pid_file"
        echo "✅ Recording stopped"
    else
        echo "❌ No active recording found for: $session_name"
    fi
}

# Usage examples:
# start_recording "bootstrap-implementation"
# stop_recording "bootstrap-implementation"