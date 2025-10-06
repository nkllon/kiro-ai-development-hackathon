#!/bin/bash

# Prometheus Management Script for Kiro AI Development Hackathon
# This script provides comprehensive management of Prometheus in Docker

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
COMPOSE_FILE="${SCRIPT_DIR}/docker-compose.yml"
PROMETHEUS_CONFIG="${SCRIPT_DIR}/prometheus.yml"
ALERT_RULES="${SCRIPT_DIR}/alert_rules.yml"
LOG_DIR="${PROJECT_ROOT}/logs"
PROMETHEUS_LOG="${LOG_DIR}/prometheus.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "${PROMETHEUS_LOG}"
}

log_info() {
    log "INFO" "${BLUE}$*${NC}"
}

log_warn() {
    log "WARN" "${YELLOW}$*${NC}"
}

log_error() {
    log "ERROR" "${RED}$*${NC}"
}

log_success() {
    log "SUCCESS" "${GREEN}$*${NC}"
}

# Ensure log directory exists
ensure_log_directory() {
    if [[ ! -d "${LOG_DIR}" ]]; then
        mkdir -p "${LOG_DIR}"
        log_info "Created log directory: ${LOG_DIR}"
    fi
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not available. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if configuration files exist
    if [[ ! -f "${PROMETHEUS_CONFIG}" ]]; then
        log_error "Prometheus configuration file not found: ${PROMETHEUS_CONFIG}"
        exit 1
    fi
    
    if [[ ! -f "${ALERT_RULES}" ]]; then
        log_error "Alert rules file not found: ${ALERT_RULES}"
        exit 1
    fi
    
    log_success "All prerequisites met"
}

# Validate configuration
validate_config() {
    log_info "Validating Prometheus configuration..."
    
    # Check if prometheus.yml is valid YAML
    if ! python3 -c "import yaml; yaml.safe_load(open('${PROMETHEUS_CONFIG}'))" 2>/dev/null; then
        log_error "Invalid YAML in prometheus.yml"
        exit 1
    fi
    
    # Check if alert_rules.yml is valid YAML
    if ! python3 -c "import yaml; yaml.safe_load(open('${ALERT_RULES}'))" 2>/dev/null; then
        log_error "Invalid YAML in alert_rules.yml"
        exit 1
    fi
    
    log_success "Configuration validation passed"
}

# Start Prometheus
start_prometheus() {
    log_info "Starting Prometheus..."
    
    ensure_log_directory
    check_prerequisites
    validate_config
    
    # Start Prometheus with monitoring profile
    if command -v docker-compose &> /dev/null; then
        docker-compose -f "${COMPOSE_FILE}" --profile monitoring up -d prometheus
    else
        docker compose -f "${COMPOSE_FILE}" --profile monitoring up -d prometheus
    fi
    
    # Wait for Prometheus to be ready
    log_info "Waiting for Prometheus to be ready..."
    local max_attempts=30
    local attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        if curl -s http://localhost:9090/-/ready &> /dev/null; then
            log_success "Prometheus is ready and running"
            log_info "Prometheus UI available at: http://localhost:9090"
            return 0
        fi
        
        ((attempt++))
        sleep 2
    done
    
    log_error "Prometheus failed to start within expected time"
    return 1
}

# Stop Prometheus
stop_prometheus() {
    log_info "Stopping Prometheus..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose -f "${COMPOSE_FILE}" stop prometheus
    else
        docker compose -f "${COMPOSE_FILE}" stop prometheus
    fi
    
    log_success "Prometheus stopped"
}

# Restart Prometheus
restart_prometheus() {
    log_info "Restarting Prometheus..."
    stop_prometheus
    sleep 2
    start_prometheus
}

# Check Prometheus status
status_prometheus() {
    log_info "Checking Prometheus status..."
    
    # Check if container is running
    if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "prometheus"; then
        log_success "Prometheus container is running"
        
        # Check if Prometheus is responding
        if curl -s http://localhost:9090/-/ready &> /dev/null; then
            log_success "Prometheus is healthy and responding"
            
            # Show basic metrics
            log_info "Prometheus metrics:"
            curl -s http://localhost:9090/api/v1/query?query=up | jq -r '.data.result[] | "\(.metric.job): \(.value[1])"' 2>/dev/null || log_warn "Could not fetch metrics (jq not available)"
        else
            log_warn "Prometheus container is running but not responding"
        fi
    else
        log_warn "Prometheus container is not running"
    fi
}

# Show Prometheus logs
logs_prometheus() {
    log_info "Showing Prometheus logs..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose -f "${COMPOSE_FILE}" logs -f prometheus
    else
        docker compose -f "${COMPOSE_FILE}" logs -f prometheus
    fi
}

# Reload Prometheus configuration
reload_config() {
    log_info "Reloading Prometheus configuration..."
    
    # Send reload signal to Prometheus
    if curl -s -X POST http://localhost:9090/-/reload; then
        log_success "Configuration reloaded successfully"
    else
        log_error "Failed to reload configuration"
        return 1
    fi
}

# Backup Prometheus data
backup_data() {
    local backup_dir="${PROJECT_ROOT}/backups/prometheus-$(date +%Y%m%d-%H%M%S)"
    
    log_info "Creating backup of Prometheus data..."
    
    mkdir -p "${backup_dir}"
    
    # Copy configuration files
    cp "${PROMETHEUS_CONFIG}" "${backup_dir}/"
    cp "${ALERT_RULES}" "${backup_dir}/"
    
    # Copy Prometheus data volume (if accessible)
    if docker volume ls | grep -q "systematic-pdca-local_prometheus_data"; then
        docker run --rm -v "systematic-pdca-local_prometheus_data:/data" -v "${backup_dir}:/backup" alpine tar czf /backup/prometheus-data.tar.gz -C /data .
        log_success "Prometheus data backed up to: ${backup_dir}"
    else
        log_warn "Prometheus data volume not found, only configuration files backed up"
    fi
}

# Clean up old data
cleanup_data() {
    log_info "Cleaning up old Prometheus data..."
    
    # Remove old log files (keep last 7 days)
    find "${LOG_DIR}" -name "prometheus*.log" -mtime +7 -delete 2>/dev/null || true
    
    # Clean up old Docker images
    docker image prune -f
    
    log_success "Cleanup completed"
}

# Show help
show_help() {
    cat << EOF
Prometheus Management Script for Kiro AI Development Hackathon

Usage: $0 <command> [options]

Commands:
    start       Start Prometheus with monitoring profile
    stop        Stop Prometheus
    restart     Restart Prometheus
    status      Show Prometheus status and health
    logs        Show Prometheus logs (follow mode)
    reload      Reload Prometheus configuration
    backup      Backup Prometheus data and configuration
    cleanup     Clean up old logs and Docker images
    validate    Validate configuration files
    help        Show this help message

Examples:
    $0 start                    # Start Prometheus
    $0 status                   # Check if Prometheus is running
    $0 logs                     # Follow Prometheus logs
    $0 backup                   # Create backup of data
    $0 reload                   # Reload configuration

Configuration:
    Compose file: ${COMPOSE_FILE}
    Prometheus config: ${PROMETHEUS_CONFIG}
    Alert rules: ${ALERT_RULES}
    Logs: ${PROMETHEUS_LOG}

EOF
}

# Main script logic
main() {
    ensure_log_directory
    
    case "${1:-help}" in
        start)
            start_prometheus
            ;;
        stop)
            stop_prometheus
            ;;
        restart)
            restart_prometheus
            ;;
        status)
            status_prometheus
            ;;
        logs)
            logs_prometheus
            ;;
        reload)
            reload_config
            ;;
        backup)
            backup_data
            ;;
        cleanup)
            cleanup_data
            ;;
        validate)
            validate_config
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
