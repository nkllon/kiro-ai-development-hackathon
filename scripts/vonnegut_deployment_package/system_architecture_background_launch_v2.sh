#!/bin/bash
"""
Background launch script for System Architecture Wiring Diagram implementation.
Executes parallel DAG orchestration in the background with comprehensive logging.
Generated using proven spec-creation-dag-compliance patterns v2.0.
"""

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
EXECUTION_LOG="$LOG_DIR/system_architecture_background_$TIMESTAMP.log"
PID_FILE="$LOG_DIR/system_architecture_background.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$EXECUTION_LOG"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$EXECUTION_LOG"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$EXECUTION_LOG"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$EXECUTION_LOG"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up background execution..."
    if [[ -f "$PID_FILE" ]]; then
        rm -f "$PID_FILE"
    fi
}

# Signal handlers
trap cleanup EXIT
trap 'log_error "Script interrupted"; exit 130' INT
trap 'log_error "Script terminated"; exit 143' TERM

# Main execution function
main() {
    log_info "🚀 System Architecture Wiring Diagram - Background Launch v2.0"
    log_info "=" | tr ' ' '='
    log_info "📋 Execution ID: system_architecture_$TIMESTAMP"
    log_info "📁 Project Root: $PROJECT_ROOT"
    log_info "📄 Log File: $EXECUTION_LOG"
    log_info "🔧 PID File: $PID_FILE"
    
    # Create logs directory
    mkdir -p "$LOG_DIR"
    
    # Check if already running
    if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        log_error "System Architecture background execution is already running (PID: $(cat "$PID_FILE"))"
        log_error "Stop the existing execution first or remove $PID_FILE if it's stale"
        exit 1
    fi
    
    # Store current PID
    echo $$ > "$PID_FILE"
    log_info "📊 Background process PID: $$"
    
    # Change to project root
    cd "$PROJECT_ROOT"
    
    # Validate environment before starting
    log_info "🔍 Running prelaunch validation..."
    if python3 scripts/system_architecture_prelaunch_check_v2.py >> "$EXECUTION_LOG" 2>&1; then
        log_success "Prelaunch validation passed"
    else
        log_error "Prelaunch validation failed - check log for details"
        exit 1
    fi
    
    # Check system resources
    log_info "💻 Checking system resources..."
    
    # CPU check
    CPU_CORES=$(nproc)
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
    log_info "CPU: $CPU_CORES cores, ${CPU_USAGE}% usage"
    
    # Memory check
    MEMORY_INFO=$(free -h | grep '^Mem:')
    MEMORY_TOTAL=$(echo $MEMORY_INFO | awk '{print $2}')
    MEMORY_USED=$(echo $MEMORY_INFO | awk '{print $3}')
    MEMORY_PERCENT=$(free | grep '^Mem:' | awk '{printf "%.1f", $3/$2 * 100.0}')
    log_info "Memory: $MEMORY_USED / $MEMORY_TOTAL (${MEMORY_PERCENT}%)"
    
    # Disk check
    DISK_INFO=$(df -h . | tail -1)
    DISK_USED=$(echo $DISK_INFO | awk '{print $3}')
    DISK_TOTAL=$(echo $DISK_INFO | awk '{print $2}')
    DISK_PERCENT=$(echo $DISK_INFO | awk '{print $5}')
    log_info "Disk: $DISK_USED / $DISK_TOTAL ($DISK_PERCENT)"
    
    # Resource warnings
    if (( $(echo "$MEMORY_PERCENT > 85" | bc -l) )); then
        log_warning "High memory usage detected: ${MEMORY_PERCENT}%"
    fi
    
    if [[ "${DISK_PERCENT%?}" -gt 90 ]]; then
        log_warning "High disk usage detected: $DISK_PERCENT"
    fi
    
    # Infrastructure dependency check
    log_info "🏗️  Checking infrastructure dependencies..."
    
    # Check Directus CMS
    if curl -s --connect-timeout 3 http://localhost:8055/server/ping | grep -q "pong"; then
        log_success "Directus CMS: Available (localhost:8055)"
    else
        log_warning "Directus CMS: Unavailable (localhost:8055) - will use file-based fallback"
    fi
    
    # Check Redis coordination
    if redis-cli -h 192.168.1.119 -p 6379 ping >/dev/null 2>&1; then
        log_success "Redis Primary: Available (192.168.1.119:6379)"
    elif redis-cli -h localhost -p 6380 ping >/dev/null 2>&1; then
        log_success "Redis Fallback: Available (localhost:6380)"
    else
        log_warning "Redis: Unavailable - coordination features disabled"
    fi
    
    # Check Observatory Server
    if curl -s --connect-timeout 3 http://localhost:8888/health >/dev/null 2>&1; then
        log_success "Observatory Server: Available (localhost:8888)"
    else
        log_warning "Observatory Server: Unavailable (localhost:8888) - will use static discovery"
    fi
    
    # Check Prometheus
    if curl -s --connect-timeout 3 http://localhost:9090/api/v1/status/config >/dev/null 2>&1; then
        log_success "Prometheus: Available (localhost:9090)"
    else
        log_warning "Prometheus: Unavailable (localhost:9090) - metrics validation disabled"
    fi
    
    # Check Grafana
    if curl -s --connect-timeout 3 http://localhost:3000/api/health >/dev/null 2>&1; then
        log_success "Grafana: Available (localhost:3000)"
    else
        log_warning "Grafana: Unavailable (localhost:3000) - dashboard validation disabled"
    fi
    
    # Start the main execution
    log_info "🚀 Starting System Architecture Wiring Diagram parallel execution..."
    log_info "📊 Expected duration: 67 hours (parallel) vs 104 hours (sequential)"
    log_info "⚡ Efficiency gain: 36% time reduction"
    log_info "🔄 Peak parallelism: 4 concurrent tasks"
    
    # Execute the main launch script
    if python3 scripts/system_architecture_launch_v2_tracked.py >> "$EXECUTION_LOG" 2>&1; then
        log_success "🎉 System Architecture Wiring Diagram execution completed successfully"
        
        # Generate summary
        log_info "📊 Execution Summary:"
        log_info "  • Total phases: 6 (Infrastructure, Analysis, Diagrams, Documentation, Orchestration, Testing)"
        log_info "  • Total tasks: 26 (with 4 optional testing tasks)"
        log_info "  • Critical path: 42 hours through 10 key tasks"
        log_info "  • Parallel execution: Up to 4 concurrent tasks"
        log_info "  • Infrastructure discovery: Complete with fallback mechanisms"
        log_info "  • Diagram generation: PlantUML and Mermaid integration"
        log_info "  • WebSocket integration: Observatory real-time monitoring"
        
        # Check for generated artifacts
        ARTIFACTS_FOUND=0
        
        if [[ -f "logs/system_architecture_execution_"*".json" ]]; then
            EXECUTION_REPORT=$(ls -t logs/system_architecture_execution_*.json | head -1)
            log_success "Execution report generated: $EXECUTION_REPORT"
            ARTIFACTS_FOUND=$((ARTIFACTS_FOUND + 1))
        fi
        
        if [[ -d "generated_docs/system_architecture" ]]; then
            log_success "Documentation artifacts generated: generated_docs/system_architecture/"
            ARTIFACTS_FOUND=$((ARTIFACTS_FOUND + 1))
        fi
        
        if [[ -d "generated_diagrams/system_architecture" ]]; then
            log_success "Diagram artifacts generated: generated_diagrams/system_architecture/"
            ARTIFACTS_FOUND=$((ARTIFACTS_FOUND + 1))
        fi
        
        log_info "📄 Total artifacts generated: $ARTIFACTS_FOUND"
        
        # Performance metrics
        END_TIME=$(date +%s)
        if [[ -f "$LOG_DIR/system_architecture_start_time" ]]; then
            START_TIME=$(cat "$LOG_DIR/system_architecture_start_time")
            DURATION=$((END_TIME - START_TIME))
            HOURS=$((DURATION / 3600))
            MINUTES=$(((DURATION % 3600) / 60))
            log_info "⏱️  Total execution time: ${HOURS}h ${MINUTES}m"
        fi
        
        log_success "✅ EXECUTION COMPLETE - System Architecture Wiring Diagram ready"
        
    else
        log_error "💥 System Architecture Wiring Diagram execution failed"
        log_error "📄 Check execution log for details: $EXECUTION_LOG"
        
        # Try to extract error information
        if [[ -f "$EXECUTION_LOG" ]]; then
            log_error "Last 10 lines of execution log:"
            tail -10 "$EXECUTION_LOG" | while read line; do
                log_error "  $line"
            done
        fi
        
        exit 1
    fi
}

# Help function
show_help() {
    cat << EOF
System Architecture Wiring Diagram - Background Launch v2.0

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -h, --help          Show this help message
    -v, --verbose       Enable verbose logging
    -d, --dry-run       Validate environment without executing
    --stop              Stop running background execution
    --status            Show status of background execution
    --logs              Show recent log entries

EXAMPLES:
    $0                  # Start background execution
    $0 --dry-run        # Validate environment only
    $0 --status         # Check execution status
    $0 --stop           # Stop background execution

FILES:
    $LOG_DIR/system_architecture_background_*.log    # Execution logs
    $PID_FILE                                        # Process ID file
    
INFRASTRUCTURE DEPENDENCIES:
    • Directus CMS (localhost:8055) - Optional, file-based fallback
    • Redis Coordination (192.168.1.119:6379 + localhost:6380) - Optional
    • Observatory Server (localhost:8888) - Optional, static discovery fallback
    • Prometheus (localhost:9090) - Optional, metrics validation disabled
    • Grafana (localhost:3000) - Optional, dashboard validation disabled

EXECUTION DETAILS:
    • Total tasks: 26 (22 core + 4 optional testing)
    • Estimated time: 67 hours (parallel) vs 104 hours (sequential)
    • Efficiency gain: 36% time reduction
    • Peak parallelism: 4 concurrent tasks
    • Critical path: 42 hours through 10 key tasks

EOF
}

# Command line argument handling
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    -d|--dry-run)
        log_info "🔍 Dry run mode - validating environment only"
        mkdir -p "$LOG_DIR"
        cd "$PROJECT_ROOT"
        python3 scripts/system_architecture_prelaunch_check_v2.py
        log_success "Dry run completed - environment validation finished"
        exit 0
        ;;
    --stop)
        if [[ -f "$PID_FILE" ]]; then
            PID=$(cat "$PID_FILE")
            if kill -0 "$PID" 2>/dev/null; then
                log_info "Stopping background execution (PID: $PID)..."
                kill "$PID"
                rm -f "$PID_FILE"
                log_success "Background execution stopped"
            else
                log_warning "No running background execution found (stale PID file removed)"
                rm -f "$PID_FILE"
            fi
        else
            log_info "No background execution running"
        fi
        exit 0
        ;;
    --status)
        if [[ -f "$PID_FILE" ]]; then
            PID=$(cat "$PID_FILE")
            if kill -0 "$PID" 2>/dev/null; then
                log_success "Background execution running (PID: $PID)"
                
                # Show recent log entries
                if [[ -f "$EXECUTION_LOG" ]]; then
                    log_info "Recent log entries:"
                    tail -5 "$EXECUTION_LOG" | while read line; do
                        echo "  $line"
                    done
                fi
            else
                log_warning "Background execution not running (stale PID file found)"
                rm -f "$PID_FILE"
            fi
        else
            log_info "No background execution running"
        fi
        exit 0
        ;;
    --logs)
        if [[ -f "$EXECUTION_LOG" ]]; then
            log_info "Showing recent log entries from: $EXECUTION_LOG"
            tail -20 "$EXECUTION_LOG"
        else
            LATEST_LOG=$(ls -t "$LOG_DIR"/system_architecture_background_*.log 2>/dev/null | head -1)
            if [[ -n "$LATEST_LOG" ]]; then
                log_info "Showing recent log entries from: $LATEST_LOG"
                tail -20 "$LATEST_LOG"
            else
                log_info "No log files found"
            fi
        fi
        exit 0
        ;;
    -v|--verbose)
        set -x
        ;;
    "")
        # No arguments - proceed with main execution
        ;;
    *)
        log_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac

# Store start time for duration calculation
date +%s > "$LOG_DIR/system_architecture_start_time"

# Execute main function
main "$@"