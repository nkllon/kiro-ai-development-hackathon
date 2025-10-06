#!/bin/bash
#
# Multi-Dimensional Vocabulary Projector Background Launch
# ========================================================
#
# Launches the vocabulary projector in background mode with full logging and monitoring.
#

set -euo pipefail

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$PROJECT_ROOT/logs/vocabulary_projector"
EXECUTION_ID="vocab_proj_$(date +%Y%m%d_%H%M%S)"
PID_FILE="$LOG_DIR/vocabulary_projector.pid"
LOG_FILE="$LOG_DIR/background_execution_$EXECUTION_ID.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS:${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

# Setup function
setup_environment() {
    log "🔧 Setting up background execution environment"
    
    # Create log directory
    mkdir -p "$LOG_DIR"
    
    # Initialize log file
    cat > "$LOG_FILE" << EOF
Multi-Dimensional Vocabulary Projector Background Execution
===========================================================
Execution ID: $EXECUTION_ID
Start Time: $(date)
Project Root: $PROJECT_ROOT
Log Directory: $LOG_DIR
PID File: $PID_FILE

EOF
    
    log "📁 Log directory: $LOG_DIR"
    log "📄 Log file: $LOG_FILE"
    log "🆔 Execution ID: $EXECUTION_ID"
}

# Check if already running
check_running() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            log_error "Vocabulary projector already running (PID: $pid)"
            echo "Use 'kill $pid' to stop the existing process"
            exit 1
        else
            log_warning "Stale PID file found, removing"
            rm -f "$PID_FILE"
        fi
    fi
}

# Pre-launch validation
run_pre_launch_check() {
    log "🔍 Running pre-launch validation"
    
    if python3 "$PROJECT_ROOT/scripts/vocabulary_projector_pre_launch_check.py" >> "$LOG_FILE" 2>&1; then
        log_success "Pre-launch check passed"
        return 0
    else
        log_error "Pre-launch check failed"
        echo "Check $LOG_FILE for details"
        return 1
    fi
}

# Main execution function
execute_vocabulary_projector() {
    log "🚀 Starting vocabulary projector execution"
    
    # Change to project directory
    cd "$PROJECT_ROOT"
    
    # Execute with full logging
    if python3 "$PROJECT_ROOT/scripts/vocabulary_projector_launch.py" --background >> "$LOG_FILE" 2>&1; then
        log_success "Vocabulary projector execution completed successfully"
        return 0
    else
        log_error "Vocabulary projector execution failed"
        return 1
    fi
}

# Background execution wrapper
run_in_background() {
    log "🌙 Starting background execution"
    
    # Create background execution function
    background_execution() {
        # Store PID
        echo $$ > "$PID_FILE"
        
        # Set up signal handlers
        trap 'log "📡 Received SIGTERM, shutting down gracefully"; cleanup_and_exit' TERM
        trap 'log "📡 Received SIGINT, shutting down gracefully"; cleanup_and_exit' INT
        
        # Execute the main process
        if execute_vocabulary_projector; then
            log_success "🎉 Background execution completed successfully"
            cleanup_and_exit 0
        else
            log_error "❌ Background execution failed"
            cleanup_and_exit 1
        fi
    }
    
    # Run in background
    background_execution &
    local bg_pid=$!
    
    # Wait a moment to ensure it started
    sleep 2
    
    if kill -0 "$bg_pid" 2>/dev/null; then
        log_success "Background process started successfully (PID: $bg_pid)"
        echo "🌙 Vocabulary projector running in background"
        echo "📄 Monitor progress: tail -f $LOG_FILE"
        echo "🛑 Stop process: kill $bg_pid"
        echo "📊 Check status: ps -p $bg_pid"
    else
        log_error "Failed to start background process"
        return 1
    fi
}

# Cleanup function
cleanup_and_exit() {
    local exit_code=${1:-0}
    
    log "🧹 Cleaning up background execution"
    
    # Remove PID file
    if [[ -f "$PID_FILE" ]]; then
        rm -f "$PID_FILE"
        log "🗑️  Removed PID file"
    fi
    
    # Final log entry
    cat >> "$LOG_FILE" << EOF

Background Execution Summary
============================
End Time: $(date)
Exit Code: $exit_code
Duration: $SECONDS seconds

EOF
    
    log "📄 Final log saved to: $LOG_FILE"
    exit "$exit_code"
}

# Status check function
check_status() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo "✅ Vocabulary projector running (PID: $pid)"
            echo "📄 Log file: $LOG_FILE"
            echo "⏱️  Runtime: $(ps -o etime= -p "$pid" | tr -d ' ')"
            return 0
        else
            echo "❌ Process not running (stale PID file)"
            rm -f "$PID_FILE"
            return 1
        fi
    else
        echo "❌ Vocabulary projector not running"
        return 1
    fi
}

# Stop function
stop_process() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo "🛑 Stopping vocabulary projector (PID: $pid)"
            kill -TERM "$pid"
            
            # Wait for graceful shutdown
            local count=0
            while kill -0 "$pid" 2>/dev/null && [[ $count -lt 30 ]]; do
                sleep 1
                ((count++))
            done
            
            if kill -0 "$pid" 2>/dev/null; then
                echo "⚠️  Process didn't stop gracefully, forcing termination"
                kill -KILL "$pid"
            fi
            
            rm -f "$PID_FILE"
            echo "✅ Process stopped"
        else
            echo "❌ Process not running"
            rm -f "$PID_FILE"
        fi
    else
        echo "❌ No running process found"
    fi
}

# Show logs function
show_logs() {
    if [[ -f "$LOG_FILE" ]]; then
        echo "📄 Showing recent logs from: $LOG_FILE"
        echo "=" * 60
        tail -f "$LOG_FILE"
    else
        echo "❌ No log file found"
        echo "Available log files:"
        ls -la "$LOG_DIR"/*.log 2>/dev/null || echo "No log files found"
    fi
}

# Help function
show_help() {
    cat << EOF
Multi-Dimensional Vocabulary Projector Background Launch
========================================================

Usage: $0 [COMMAND]

Commands:
    start       Start vocabulary projector in background
    stop        Stop running vocabulary projector
    status      Check if vocabulary projector is running
    logs        Show real-time logs
    restart     Stop and start vocabulary projector
    help        Show this help message

Examples:
    $0 start                    # Start in background
    $0 status                   # Check if running
    $0 logs                     # Monitor logs
    $0 stop                     # Stop process

Files:
    PID File: $PID_FILE
    Log Dir:  $LOG_DIR
    
EOF
}

# Main execution
main() {
    local command=${1:-start}
    
    case "$command" in
        "start")
            setup_environment
            check_running
            
            if run_pre_launch_check; then
                run_in_background
            else
                log_error "Cannot start due to pre-launch check failures"
                exit 1
            fi
            ;;
        
        "stop")
            stop_process
            ;;
        
        "status")
            check_status
            ;;
        
        "logs")
            show_logs
            ;;
        
        "restart")
            echo "🔄 Restarting vocabulary projector"
            stop_process
            sleep 2
            setup_environment
            if run_pre_launch_check; then
                run_in_background
            else
                log_error "Cannot restart due to pre-launch check failures"
                exit 1
            fi
            ;;
        
        "help"|"-h"|"--help")
            show_help
            ;;
        
        *)
            echo "❌ Unknown command: $command"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Execute main function
main "$@"