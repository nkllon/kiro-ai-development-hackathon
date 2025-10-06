#!/bin/bash

# Repository Setup and Installation - Background Launch Script
# Updated with proven workflow control patterns

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"
EXECUTION_ID="repository_setup_$(date +%Y%m%d_%H%M%S)"
PID_FILE="$LOG_DIR/${EXECUTION_ID}.pid"
LOG_FILE="$LOG_DIR/${EXECUTION_ID}.log"
PROGRESS_FILE="$LOG_DIR/${EXECUTION_ID}_progress.json"
LOCK_FILE="$LOG_DIR/repository_setup.lock"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Execution locking functions (proven pattern from spec-creation-dag-compliance)
acquire_lock() {
    log_info "Checking for concurrent executions..."
    
    if [[ -f "$LOCK_FILE" ]]; then
        local lock_pid=$(cat "$LOCK_FILE" 2>/dev/null || echo "")
        if [[ -n "$lock_pid" ]] && kill -0 "$lock_pid" 2>/dev/null; then
            log_error "Another execution is already running (PID: $lock_pid)"
            log_error "Wait for completion or stop with: $0 stop"
            exit 1
        else
            log_warning "Stale lock file found, removing..."
            rm -f "$LOCK_FILE"
        fi
    fi
    
    echo $$ > "$LOCK_FILE"
    log_info "Execution lock acquired (PID: $$)"
}

release_lock() {
    if [[ -f "$LOCK_FILE" ]]; then
        rm -f "$LOCK_FILE"
        log_info "Execution lock released"
    fi
}

# Progress tracking functions
update_progress() {
    local phase="$1"
    local status="$2"
    local details="$3"
    
    cat > "$PROGRESS_FILE" << EOF
{
    "execution_id": "$EXECUTION_ID",
    "timestamp": "$(date -Iseconds)",
    "current_phase": "$phase",
    "status": "$status",
    "details": "$details",
    "log_file": "$LOG_FILE",
    "pid_file": "$PID_FILE",
    "lock_file": "$LOCK_FILE"
}
EOF
}

# Cleanup function
cleanup() {
    local exit_code=$?
    log_info "Cleaning up background launch process..."
    
    # Release execution lock
    release_lock
    
    if [[ -f "$PID_FILE" ]]; then
        rm -f "$PID_FILE"
        log_info "Removed PID file: $PID_FILE"
    fi
    
    if [[ $exit_code -eq 0 ]]; then
        update_progress "cleanup" "completed" "Background launch completed successfully"
        log_success "Background launch completed successfully"
    else
        update_progress "cleanup" "failed" "Background launch failed with exit code $exit_code"
        log_error "Background launch failed with exit code $exit_code"
    fi
    
    exit $exit_code
}

# Set up cleanup trap
trap cleanup EXIT INT TERM

# Main execution function
main() {
    log_info "🚀 Starting Repository Setup and Installation Background Launch"
    log_info "Execution ID: $EXECUTION_ID"
    log_info "Log File: $LOG_FILE"
    log_info "Progress File: $PROGRESS_FILE"
    
    # Create logs directory
    mkdir -p "$LOG_DIR"
    
    # Acquire execution lock to prevent concurrent runs
    acquire_lock
    
    # Store PID for monitoring
    echo $$ > "$PID_FILE"
    log_info "Background process PID: $$"
    
    # Phase 1: Pre-launch validation
    update_progress "prelaunch_validation" "running" "Running infrastructure readiness checks"
    log_info "Phase 1: Running prelaunch validation..."
    
    if python3 "$SCRIPT_DIR/repository_setup_prelaunch_check.py" >> "$LOG_FILE" 2>&1; then
        log_success "Prelaunch validation completed successfully"
        update_progress "prelaunch_validation" "completed" "Infrastructure validation passed"
    else
        log_error "Prelaunch validation failed"
        update_progress "prelaunch_validation" "failed" "Infrastructure validation failed - check logs"
        return 1
    fi
    
    # Phase 2: Launch parallel execution
    update_progress "parallel_execution" "running" "Launching parallel execution with updated workflow control"
    log_info "Phase 2: Launching parallel execution..."
    
    if python3 "$SCRIPT_DIR/repository_setup_launch.py" >> "$LOG_FILE" 2>&1; then
        log_success "Parallel execution completed successfully"
        update_progress "parallel_execution" "completed" "All phases executed successfully"
    else
        log_error "Parallel execution failed"
        update_progress "parallel_execution" "failed" "Parallel execution failed - check logs"
        return 1
    fi
    
    # Phase 3: Post-execution validation
    update_progress "post_validation" "running" "Running post-execution validation"
    log_info "Phase 3: Running post-execution validation..."
    
    # Validate execution results
    if validate_execution_results; then
        log_success "Post-execution validation completed"
        update_progress "post_validation" "completed" "Execution results validated successfully"
    else
        log_warning "Post-execution validation found issues"
        update_progress "post_validation" "completed_with_warnings" "Validation completed with warnings"
    fi
    
    # Phase 4: Generate final report
    update_progress "reporting" "running" "Generating final execution report"
    log_info "Phase 4: Generating final report..."
    
    generate_final_report
    log_success "Final report generated"
    update_progress "reporting" "completed" "Final report generated successfully"
    
    log_success "🎉 Repository Setup and Installation implementation completed successfully!"
    log_info "Check logs and reports in: $LOG_DIR"
}

# Validation function
validate_execution_results() {
    log_info "Validating execution results..."
    
    local validation_passed=true
    
    # Check if specification files exist
    local spec_dir="$PROJECT_ROOT/.kiro/specs/repository-setup-and-installation"
    if [[ ! -d "$spec_dir" ]]; then
        log_error "Specification directory not found: $spec_dir"
        validation_passed=false
    fi
    
    # Check for execution logs
    local execution_logs=$(find "$LOG_DIR" -name "repository_setup_execution_*.json" -mmin -60 | wc -l)
    if [[ $execution_logs -eq 0 ]]; then
        log_warning "No recent execution logs found"
        validation_passed=false
    else
        log_info "Found $execution_logs recent execution log(s)"
    fi
    
    # Check for any critical errors in logs
    if grep -q "CRITICAL\|FATAL" "$LOG_FILE" 2>/dev/null; then
        log_warning "Critical errors found in execution logs"
        validation_passed=false
    fi
    
    if [[ "$validation_passed" == "true" ]]; then
        log_success "Execution results validation passed"
        return 0
    else
        log_warning "Execution results validation found issues"
        return 1
    fi
}

# Report generation function
generate_final_report() {
    local report_file="$LOG_DIR/${EXECUTION_ID}_final_report.md"
    
    log_info "Generating final report: $report_file"
    
    cat > "$report_file" << EOF
# Repository Setup and Installation - Execution Report

## Execution Summary
- **Execution ID**: $EXECUTION_ID
- **Start Time**: $(head -1 "$LOG_FILE" | grep -o '[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\} [0-9]\{2\}:[0-9]\{2\}:[0-9]\{2\}' || echo "Unknown")
- **End Time**: $(date '+%Y-%m-%d %H:%M:%S')
- **Log File**: $LOG_FILE
- **Progress File**: $PROGRESS_FILE

## Phase Results
$(grep -E "\[SUCCESS\].*Phase [0-9]:" "$LOG_FILE" | sed 's/.*\[SUCCESS\]/✅/' || echo "No phase completions found")

## Warnings and Errors
$(grep -E "\[WARNING\]|\[ERROR\]" "$LOG_FILE" | tail -10 || echo "No warnings or errors found")

## Next Steps
1. Review execution logs for any warnings or issues
2. Test the new repository setup system with \`make install\`
3. Validate repository health with \`make validate\`
4. Use \`make cleanup\` to test automated cleanup features
5. Review generated documentation and examples

## Files Generated
- Log File: $LOG_FILE
- Progress File: $PROGRESS_FILE
- Final Report: $report_file
- Execution Reports: $LOG_DIR/repository_setup_execution_*.json

---
Generated by Repository Setup and Installation Background Launch
Execution ID: $EXECUTION_ID
EOF

    log_success "Final report generated: $report_file"
}

# Process monitoring functions
show_status() {
    if [[ -f "$PROGRESS_FILE" ]]; then
        echo "📊 Current Status:"
        cat "$PROGRESS_FILE" | python3 -m json.tool 2>/dev/null || cat "$PROGRESS_FILE"
    else
        echo "❌ No progress file found"
    fi
}

show_logs() {
    if [[ -f "$LOG_FILE" ]]; then
        echo "📋 Recent Logs:"
        tail -20 "$LOG_FILE"
    else
        echo "❌ No log file found"
    fi
}

# Handle command line arguments
case "${1:-run}" in
    "run")
        main
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs
        ;;
    "stop")
        if [[ -f "$LOCK_FILE" ]]; then
            local lock_pid=$(cat "$LOCK_FILE" 2>/dev/null || echo "")
            if [[ -n "$lock_pid" ]] && kill -0 "$lock_pid" 2>/dev/null; then
                log_info "Stopping background process (PID: $lock_pid)"
                kill "$lock_pid"
                # Wait a moment for cleanup
                sleep 2
                # Force remove lock if still exists
                if [[ -f "$LOCK_FILE" ]]; then
                    rm -f "$LOCK_FILE"
                    log_info "Removed stale lock file"
                fi
                log_success "Background process stopped"
            else
                log_warning "Background process not running"
                # Clean up stale lock
                rm -f "$LOCK_FILE"
            fi
        else
            log_warning "No active execution found"
        fi
        ;;
    *)
        echo "Usage: $0 [run|status|logs|stop]"
        echo "  run    - Start background execution (default)"
        echo "  status - Show current execution status"
        echo "  logs   - Show recent execution logs"
        echo "  stop   - Stop background execution"
        exit 1
        ;;
esac