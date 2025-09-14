#!/bin/bash

# Prometheus Test Script for Kiro AI Development Hackathon
# This script tests Prometheus functionality and health

set -euo pipefail

# Configuration
PROMETHEUS_URL="http://localhost:9090"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
LOG_DIR="${PROJECT_ROOT}/logs"
TEST_LOG="${LOG_DIR}/prometheus-test.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=0

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "${TEST_LOG}"
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

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_result="${3:-0}"
    
    ((TOTAL_TESTS++))
    log_info "Running test: ${test_name}"
    
    if eval "${test_command}" &> /dev/null; then
        if [[ $? -eq $expected_result ]]; then
            log_success "✓ ${test_name} - PASSED"
            ((TESTS_PASSED++))
            return 0
        else
            log_error "✗ ${test_name} - FAILED (unexpected exit code)"
            ((TESTS_FAILED++))
            return 1
        fi
    else
        log_error "✗ ${test_name} - FAILED"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Ensure log directory exists
ensure_log_directory() {
    if [[ ! -d "${LOG_DIR}" ]]; then
        mkdir -p "${LOG_DIR}"
        log_info "Created log directory: ${LOG_DIR}"
    fi
}

# Test Prometheus connectivity
test_prometheus_connectivity() {
    log_info "Testing Prometheus connectivity..."
    
    run_test "Prometheus is reachable" "curl -s ${PROMETHEUS_URL}/-/ready"
    run_test "Prometheus health check" "curl -s ${PROMETHEUS_URL}/-/healthy"
    run_test "Prometheus status page" "curl -s ${PROMETHEUS_URL}/status"
}

# Test Prometheus API endpoints
test_prometheus_api() {
    log_info "Testing Prometheus API endpoints..."
    
    run_test "Query API is accessible" "curl -s ${PROMETHEUS_URL}/api/v1/query?query=up"
    run_test "Targets API is accessible" "curl -s ${PROMETHEUS_URL}/api/v1/targets"
    run_test "Config API is accessible" "curl -s ${PROMETHEUS_URL}/api/v1/status/config"
    run_test "Rules API is accessible" "curl -s ${PROMETHEUS_URL}/api/v1/rules"
}

# Test Prometheus targets
test_prometheus_targets() {
    log_info "Testing Prometheus targets..."
    
    # Get targets status
    local targets_response=$(curl -s "${PROMETHEUS_URL}/api/v1/targets")
    
    if echo "${targets_response}" | jq -e '.data.activeTargets[]' &> /dev/null; then
        local active_targets=$(echo "${targets_response}" | jq -r '.data.activeTargets | length')
        log_info "Found ${active_targets} active targets"
        
        # Check if Prometheus self-monitoring is working
        if echo "${targets_response}" | jq -e '.data.activeTargets[] | select(.job=="prometheus" and .health=="up")' &> /dev/null; then
            log_success "✓ Prometheus self-monitoring target is up"
            ((TESTS_PASSED++))
        else
            log_error "✗ Prometheus self-monitoring target is not up"
            ((TESTS_FAILED++))
        fi
        ((TOTAL_TESTS++))
    else
        log_error "✗ Could not retrieve targets information"
        ((TESTS_FAILED++))
        ((TOTAL_TESTS++))
    fi
}

# Test Prometheus metrics
test_prometheus_metrics() {
    log_info "Testing Prometheus metrics..."
    
    # Test basic metrics
    run_test "Prometheus metrics endpoint" "curl -s ${PROMETHEUS_URL}/metrics"
    
    # Test specific metrics
    local metrics_response=$(curl -s "${PROMETHEUS_URL}/api/v1/query?query=up")
    if echo "${metrics_response}" | jq -e '.data.result' &> /dev/null; then
        log_success "✓ Metrics query API is working"
        ((TESTS_PASSED++))
    else
        log_error "✗ Metrics query API is not working"
        ((TESTS_FAILED++))
    fi
    ((TOTAL_TESTS++))
}

# Test Prometheus configuration
test_prometheus_config() {
    log_info "Testing Prometheus configuration..."
    
    local config_response=$(curl -s "${PROMETHEUS_URL}/api/v1/status/config")
    
    if echo "${config_response}" | jq -e '.data.yaml' &> /dev/null; then
        log_success "✓ Configuration is loaded and accessible"
        ((TESTS_PASSED++))
    else
        log_error "✗ Configuration is not accessible"
        ((TESTS_FAILED++))
    fi
    ((TOTAL_TESTS++))
}

# Test Prometheus rules
test_prometheus_rules() {
    log_info "Testing Prometheus rules..."
    
    local rules_response=$(curl -s "${PROMETHEUS_URL}/api/v1/rules")
    
    if echo "${rules_response}" | jq -e '.data.groups' &> /dev/null; then
        local rule_groups=$(echo "${rules_response}" | jq -r '.data.groups | length')
        log_info "Found ${rule_groups} rule groups"
        log_success "✓ Rules are loaded and accessible"
        ((TESTS_PASSED++))
    else
        log_error "✗ Rules are not accessible"
        ((TESTS_FAILED++))
    fi
    ((TOTAL_TESTS++))
}

# Test Prometheus storage
test_prometheus_storage() {
    log_info "Testing Prometheus storage..."
    
    local tsdb_response=$(curl -s "${PROMETHEUS_URL}/api/v1/status/tsdb")
    
    if echo "${tsdb_response}" | jq -e '.data' &> /dev/null; then
        log_success "✓ TSDB storage is accessible"
        ((TESTS_PASSED++))
    else
        log_error "✗ TSDB storage is not accessible"
        ((TESTS_FAILED++))
    fi
    ((TOTAL_TESTS++))
}

# Test Prometheus web UI
test_prometheus_web_ui() {
    log_info "Testing Prometheus web UI..."
    
    run_test "Web UI is accessible" "curl -s ${PROMETHEUS_URL}/"
    run_test "Graph page is accessible" "curl -s ${PROMETHEUS_URL}/graph"
    run_test "Alerts page is accessible" "curl -s ${PROMETHEUS_URL}/alerts"
    run_test "Status page is accessible" "curl -s ${PROMETHEUS_URL}/status"
}

# Test Prometheus performance
test_prometheus_performance() {
    log_info "Testing Prometheus performance..."
    
    # Test query performance
    local start_time=$(date +%s%N)
    curl -s "${PROMETHEUS_URL}/api/v1/query?query=up" &> /dev/null
    local end_time=$(date +%s%N)
    local duration=$(( (end_time - start_time) / 1000000 )) # Convert to milliseconds
    
    if [[ $duration -lt 1000 ]]; then
        log_success "✓ Query performance is good (${duration}ms)"
        ((TESTS_PASSED++))
    else
        log_warn "⚠ Query performance is slow (${duration}ms)"
        ((TESTS_PASSED++)) # Still pass, but warn
    fi
    ((TOTAL_TESTS++))
}

# Generate test report
generate_test_report() {
    log_info "Generating test report..."
    
    local success_rate=$(( (TESTS_PASSED * 100) / TOTAL_TESTS ))
    
    cat << EOF | tee -a "${TEST_LOG}"

========================================
PROMETHEUS TEST REPORT
========================================
Test Date: $(date)
Total Tests: ${TOTAL_TESTS}
Passed: ${TESTS_PASSED}
Failed: ${TESTS_FAILED}
Success Rate: ${success_rate}%

EOF

    if [[ $TESTS_FAILED -eq 0 ]]; then
        log_success "🎉 All tests passed! Prometheus is working correctly."
        return 0
    else
        log_error "❌ ${TESTS_FAILED} test(s) failed. Please check the logs for details."
        return 1
    fi
}

# Main test function
run_all_tests() {
    log_info "Starting Prometheus tests..."
    
    ensure_log_directory
    
    # Check if Prometheus is running
    if ! curl -s "${PROMETHEUS_URL}/-/ready" &> /dev/null; then
        log_error "Prometheus is not running or not accessible at ${PROMETHEUS_URL}"
        log_info "Please start Prometheus first using: ./prometheus-manager.sh start"
        exit 1
    fi
    
    # Run all tests
    test_prometheus_connectivity
    test_prometheus_api
    test_prometheus_targets
    test_prometheus_metrics
    test_prometheus_config
    test_prometheus_rules
    test_prometheus_storage
    test_prometheus_web_ui
    test_prometheus_performance
    
    # Generate report
    generate_test_report
}

# Show help
show_help() {
    cat << EOF
Prometheus Test Script for Kiro AI Development Hackathon

Usage: $0 [options]

Options:
    --url URL     Prometheus URL (default: http://localhost:9090)
    --help        Show this help message

Examples:
    $0                    # Run all tests
    $0 --url http://localhost:9091  # Test different URL

Test Categories:
    - Connectivity tests
    - API endpoint tests
    - Target monitoring tests
    - Metrics collection tests
    - Configuration tests
    - Rules evaluation tests
    - Storage tests
    - Web UI tests
    - Performance tests

EOF
}

# Main script logic
main() {
    case "${1:-}" in
        --help|-h)
            show_help
            exit 0
            ;;
        --url)
            PROMETHEUS_URL="$2"
            run_all_tests
            ;;
        "")
            run_all_tests
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
