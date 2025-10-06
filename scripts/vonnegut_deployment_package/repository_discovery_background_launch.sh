#!/bin/bash
"""
Repository Content Discovery and Indexing - Background Launch Script
==================================================================

Launches the repository discovery implementation in background mode with
comprehensive monitoring, logging, and status reporting.

Author: Repository Discovery System
Date: 2025-10-01
Version: 1.0
"""

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$PROJECT_ROOT/.kiro/specs/repository-content-discovery-indexing/logs"
PID_FILE="$LOG_DIR/launch.pid"
STATUS_FILE="$PROJECT_ROOT/.kiro/specs/repository-content-discovery-indexing/execution_status.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if already running
check_running() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            return 0  # Running
        else
            rm -f "$PID_FILE"
            return 1  # Not running
        fi
    fi
    return 1  # Not running
}

# Start background execution
start_background() {
    log "🚀 Starting Repository Discovery Implementation in background..."
    
    # Create log directory
    mkdir -p "$LOG_DIR"
    
    # Check if already running
    if check_running; then
        warning "Implementation already running (PID: $(cat "$PID_FILE"))"
        return 1
    fi
    
    # Change to project root
    cd "$PROJECT_ROOT"
    
    # Start background process
    nohup python3 "$SCRIPT_DIR/repository_discovery_launch.py" --background \
        > "$LOG_DIR/background_execution.log" 2>&1 &
    
    local pid=$!
    echo "$pid" > "$PID_FILE"
    
    success "Background execution started (PID: $pid)"
    log "📄 Logs: $LOG_DIR/background_execution.log"
    log "📊 Status: Use 'scripts/repository_discovery_background_launch.sh status' to monitor"
    
    return 0
}

# Stop background execution
stop_background() {
    log "🛑 Stopping Repository Discovery Implementation..."
    
    if check_running; then
        local pid=$(cat "$PID_FILE")
        log "Terminating process $pid..."
        
        # Try graceful shutdown first
        kill -TERM "$pid" 2>/dev/null || true
        
        # Wait up to 30 seconds for graceful shutdown
        local count=0
        while kill -0 "$pid" 2>/dev/null && [[ $count -lt 30 ]]; do
            sleep 1
            ((count++))
        done
        
        # Force kill if still running
        if kill -0 "$pid" 2>/dev/null; then
            warning "Graceful shutdown failed, forcing termination..."
            kill -KILL "$pid" 2>/dev/null || true
        fi
        
        rm -f "$PID_FILE"
        success "Background execution stopped"
    else
        warning "No background execution running"
    fi
}

# Show status
show_status() {
    log "📊 Repository Discovery Implementation Status"
    echo "=================================================="
    
    # Check if running
    if check_running; then
        local pid=$(cat "$PID_FILE")
        success "Status: RUNNING (PID: $pid)"
        
        # Show execution status if available
        if [[ -f "$STATUS_FILE" ]]; then
            echo ""
            log "📈 Execution Progress:"
            python3 -c "
import json
import sys
try:
    with open('$STATUS_FILE', 'r') as f:
        data = json.load(f)
    
    status = data['execution_status']
    print(f\"  Phase: {status['current_phase']}\")
    print(f\"  Progress: {status['completed_tasks']}/{status['total_tasks']} tasks\")
    print(f\"  Running: {', '.join(status['running_tasks']) if status['running_tasks'] else 'None'}\")
    
    if status['failed_tasks']:
        print(f\"  Failed: {', '.join(status['failed_tasks'])}\")
    
    if status['estimated_completion']:
        print(f\"  ETA: {status['estimated_completion']}\")
        
except Exception as e:
    print(f\"  Error reading status: {e}\")
"
        else
            warning "No detailed status available yet"
        fi
        
        # Show recent log entries
        echo ""
        log "📄 Recent Log Entries:"
        if [[ -f "$LOG_DIR/background_execution.log" ]]; then
            tail -n 10 "$LOG_DIR/background_execution.log" | sed 's/^/  /'
        else
            warning "No log file found"
        fi
        
    else
        warning "Status: NOT RUNNING"
    fi
    
    echo ""
    log "💡 Commands:"
    echo "  Start:   $0 start"
    echo "  Stop:    $0 stop"
    echo "  Status:  $0 status"
    echo "  Logs:    $0 logs"
    echo "  Restart: $0 restart"
}

# Show logs
show_logs() {
    log "📄 Repository Discovery Implementation Logs"
    echo "============================================="
    
    if [[ -f "$LOG_DIR/background_execution.log" ]]; then
        echo ""
        log "Following logs (Ctrl+C to exit):"
        tail -f "$LOG_DIR/background_execution.log"
    else
        error "No log file found at $LOG_DIR/background_execution.log"
        return 1
    fi
}

# Restart background execution
restart_background() {
    log "🔄 Restarting Repository Discovery Implementation..."
    
    stop_background
    sleep 2
    start_background
}

# Run pre-launch check
run_prelaunch_check() {
    log "🔍 Running pre-launch validation..."
    
    cd "$PROJECT_ROOT"
    
    if python3 "$SCRIPT_DIR/repository_discovery_prelaunch_check.py"; then
        success "Pre-launch check passed"
        return 0
    else
        error "Pre-launch check failed"
        return 1
    fi
}

# Show help
show_help() {
    echo "Repository Discovery Implementation - Background Launcher"
    echo "========================================================"
    echo ""
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  start     Start background implementation"
    echo "  stop      Stop background implementation"
    echo "  restart   Restart background implementation"
    echo "  status    Show current status and progress"
    echo "  logs      Follow execution logs"
    echo "  check     Run pre-launch validation"
    echo "  help      Show this help message"
    echo ""
    echo "Files:"
    echo "  Logs:     $LOG_DIR/"
    echo "  Status:   $STATUS_FILE"
    echo "  PID:      $PID_FILE"
}

# Main execution
main() {
    local command="${1:-help}"
    
    case "$command" in
        "start")
            if run_prelaunch_check; then
                start_background
            else
                error "Pre-launch check failed. Fix issues before starting."
                exit 1
            fi
            ;;
        "stop")
            stop_background
            ;;
        "restart")
            restart_background
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs
            ;;
        "check")
            run_prelaunch_check
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            error "Unknown command: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Execute main function
main "$@"