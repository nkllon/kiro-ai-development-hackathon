#!/bin/bash
"""
Repository Setup and Installation - Background Launch Script
==========================================================

Launches parallel DAG execution in the background with comprehensive monitoring,
logging, and progress tracking. Provides real-time status updates and handles
graceful shutdown and error recovery.
"""

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SPEC_DIR="$PROJECT_ROOT/.kiro/specs/repository-setup-and-installation"
LOG_DIR="$PROJECT_ROOT/logs/repository-setup-$(date +%Y%m%d-%H%M%S)"
PID_FILE="$LOG_DIR/orchestrator.pid"
STATUS_FILE="$LOG_DIR/status.json"
PROGRESS_FILE="$LOG_DIR/progress.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_DIR/launch.log"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_DIR/launch.log"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_DIR/launch.log"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_DIR/launch.log"
}

# Cleanup function
cleanup() {
    log_info "🧹 Cleaning up background processes..."
    
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            log_info "⏹️  Stopping orchestrator process (PID: $pid)"
            kill -TERM "$pid" 2>/dev/null || true
            
            # Wait for graceful shutdown
            local count=0
            while kill -0 "$pid" 2>/dev/null && [[ $count -lt 10 ]]; do
                sleep 1
                ((count++))
            done
            
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                log_warn "🔨 Force killing orchestrator process"
                kill -KILL "$pid" 2>/dev/null || true
            fi
        fi
        rm -f "$PID_FILE"
    fi
    
    log_info "✅ Cleanup complete"
}

# Set up signal handlers
trap cleanup EXIT INT TERM

# Create log directory
create_log_directory() {
    log_info "📁 Creating log directory: $LOG_DIR"
    mkdir -p "$LOG_DIR"
    
    # Create initial status file
    cat > "$STATUS_FILE" << EOF
{
    "status": "initializing",
    "start_time": "$(date -Iseconds)",
    "pid": null,
    "progress": {
        "completed_tasks": 0,
        "total_tasks": 0,
        "current_phase": "initialization"
    },
    "log_directory": "$LOG_DIR"
}
EOF
}

# Pre-launch validation
run_prelaunch_check() {
    log_info "🔍 Running pre-launch validation..."
    
    if ! python3 "$SCRIPT_DIR/repository_setup_prelaunch_check.py"; then
        log_error "❌ Pre-launch validation failed"
        log_error "🔧 Fix critical issues before launching"
        exit 1
    fi
    
    log_success "✅ Pre-launch validation passed"
}

# Start progress monitor
start_progress_monitor() {
    log_info "📊 Starting progress monitor..."
    
    # Background progress monitoring
    (
        while [[ -f "$PID_FILE" ]]; do
            if [[ -f "$SPEC_DIR/LAUNCH_SUMMARY.md" ]]; then
                # Extract progress from summary file
                local completed=$(grep -o "Completed Tasks.*" "$SPEC_DIR/LAUNCH_SUMMARY.md" | head -1 || echo "0/0")
                local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
                echo "[$timestamp] Progress: $completed" >> "$PROGRESS_FILE"
            fi
            sleep 10
        done
    ) &
    
    local monitor_pid=$!
    echo "$monitor_pid" > "$LOG_DIR/monitor.pid"
}

# Launch orchestrator
launch_orchestrator() {
    local max_workers=${1:-4}
    
    log_info "🚀 Launching DAG orchestrator with $max_workers workers..."
    
    # Update status
    jq --arg status "launching" --arg pid "$$" \
       '.status = $status | .launcher_pid = ($pid | tonumber)' \
       "$STATUS_FILE" > "$STATUS_FILE.tmp" && mv "$STATUS_FILE.tmp" "$STATUS_FILE"
    
    # Launch orchestrator in background
    python3 "$SCRIPT_DIR/repository_setup_launch.py" "$max_workers" \
        > "$LOG_DIR/orchestrator.log" 2>&1 &
    
    local orchestrator_pid=$!
    echo "$orchestrator_pid" > "$PID_FILE"
    
    # Update status with PID
    jq --arg pid "$orchestrator_pid" \
       '.status = "running" | .pid = ($pid | tonumber)' \
       "$STATUS_FILE" > "$STATUS_FILE.tmp" && mv "$STATUS_FILE.tmp" "$STATUS_FILE"
    
    log_success "🎯 Orchestrator launched (PID: $orchestrator_pid)"
    log_info "📄 Logs: $LOG_DIR/orchestrator.log"
    log_info "📊 Status: $STATUS_FILE"
    
    return $orchestrator_pid
}

# Monitor execution
monitor_execution() {
    local orchestrator_pid=$1
    
    log_info "👀 Monitoring execution (PID: $orchestrator_pid)..."
    
    # Start progress monitor
    start_progress_monitor
    
    # Wait for completion or failure
    local exit_code=0
    
    while kill -0 "$orchestrator_pid" 2>/dev/null; do
        # Show live progress
        if [[ -f "$PROGRESS_FILE" ]]; then
            local last_progress=$(tail -1 "$PROGRESS_FILE" 2>/dev/null || echo "No progress yet")
            echo -ne "\r${CYAN}📈 $last_progress${NC}"
        fi
        
        sleep 2
    done
    
    # Get final exit code
    wait "$orchestrator_pid" || exit_code=$?
    
    echo # New line after progress display
    
    # Update final status
    local final_status="completed"
    if [[ $exit_code -ne 0 ]]; then
        final_status="failed"
    fi
    
    jq --arg status "$final_status" --arg end_time "$(date -Iseconds)" --arg exit_code "$exit_code" \
       '.status = $status | .end_time = $end_time | .exit_code = ($exit_code | tonumber)' \
       "$STATUS_FILE" > "$STATUS_FILE.tmp" && mv "$STATUS_FILE.tmp" "$STATUS_FILE"
    
    return $exit_code
}

# Generate final report
generate_final_report() {
    local exit_code=$1
    
    log_info "📋 Generating final execution report..."
    
    local report_file="$LOG_DIR/FINAL_REPORT.md"
    
    cat > "$report_file" << EOF
# Repository Setup and Installation - Final Execution Report

## Execution Summary

- **Start Time**: $(jq -r '.start_time' "$STATUS_FILE")
- **End Time**: $(jq -r '.end_time // "N/A"' "$STATUS_FILE")
- **Final Status**: $(jq -r '.status' "$STATUS_FILE")
- **Exit Code**: $exit_code
- **Log Directory**: $LOG_DIR

## Files Generated

- **Orchestrator Log**: \`$LOG_DIR/orchestrator.log\`
- **Launch Log**: \`$LOG_DIR/launch.log\`
- **Progress Log**: \`$LOG_DIR/progress.log\`
- **Status File**: \`$STATUS_FILE\`
- **Detailed Summary**: \`$SPEC_DIR/LAUNCH_SUMMARY.md\`

## Quick Status Check

\`\`\`bash
# Check current status
cat $STATUS_FILE | jq '.'

# View orchestrator logs
tail -f $LOG_DIR/orchestrator.log

# View progress
tail -f $LOG_DIR/progress.log
\`\`\`

## Next Steps

EOF

    if [[ $exit_code -eq 0 ]]; then
        cat >> "$report_file" << EOF
### ✅ Execution Successful

1. **Test Installation System**:
   \`\`\`bash
   make install
   \`\`\`

2. **Test Validation System**:
   \`\`\`bash
   make validate
   \`\`\`

3. **Test Cleanup System**:
   \`\`\`bash
   make cleanup
   \`\`\`

4. **Review Implementation**:
   - Check generated files in \`src/repository_setup/\`
   - Review updated Makefile targets
   - Test CLI tools and reporting

EOF
    else
        cat >> "$report_file" << EOF
### ❌ Execution Failed

1. **Review Logs**:
   \`\`\`bash
   cat $LOG_DIR/orchestrator.log
   \`\`\`

2. **Check Detailed Summary**:
   \`\`\`bash
   cat $SPEC_DIR/LAUNCH_SUMMARY.md
   \`\`\`

3. **Fix Issues and Retry**:
   - Address failed tasks
   - Re-run pre-launch check
   - Launch again with fixes

EOF
    fi
    
    log_info "📄 Final report saved: $report_file"
}

# Display usage
usage() {
    cat << EOF
Repository Setup and Installation - Background Launch

Usage: $0 [OPTIONS]

Options:
    -w, --workers NUM     Number of parallel workers (default: 4)
    -h, --help           Show this help message
    
Examples:
    $0                   # Launch with 4 workers
    $0 -w 6              # Launch with 6 workers
    
The script will:
1. Run pre-launch validation
2. Launch DAG orchestrator in background
3. Monitor progress and provide real-time updates
4. Generate comprehensive execution report
5. Clean up processes on completion or interruption

Logs and status files are saved to: logs/repository-setup-YYYYMMDD-HHMMSS/
EOF
}

# Main execution
main() {
    local max_workers=4
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -w|--workers)
                max_workers="$2"
                shift 2
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
    
    # Validate workers parameter
    if ! [[ "$max_workers" =~ ^[0-9]+$ ]] || [[ "$max_workers" -lt 1 ]] || [[ "$max_workers" -gt 16 ]]; then
        log_error "Invalid worker count: $max_workers (must be 1-16)"
        exit 1
    fi
    
    echo -e "${PURPLE}🚀 Repository Setup and Installation - Background Launch${NC}"
    echo -e "${PURPLE}================================================================${NC}"
    echo
    
    log_info "🎯 Configuration:"
    log_info "   📁 Project Root: $PROJECT_ROOT"
    log_info "   📊 Max Workers: $max_workers"
    log_info "   📂 Log Directory: $LOG_DIR"
    echo
    
    # Create log directory
    create_log_directory
    
    # Run pre-launch validation
    run_prelaunch_check
    echo
    
    # Launch orchestrator
    local orchestrator_pid
    orchestrator_pid=$(launch_orchestrator "$max_workers")
    echo
    
    # Monitor execution
    local exit_code=0
    monitor_execution "$orchestrator_pid" || exit_code=$?
    echo
    
    # Generate final report
    generate_final_report "$exit_code"
    echo
    
    # Final status
    if [[ $exit_code -eq 0 ]]; then
        log_success "🎉 Repository Setup DAG execution completed successfully!"
        log_info "📋 Review the summary: $SPEC_DIR/LAUNCH_SUMMARY.md"
        log_info "🧪 Test the new installation system: make install"
    else
        log_error "💥 Repository Setup DAG execution failed (exit code: $exit_code)"
        log_info "📋 Review the logs: $LOG_DIR/orchestrator.log"
        log_info "🔧 Fix issues and retry the launch"
    fi
    
    return $exit_code
}

# Run main function
main "$@"