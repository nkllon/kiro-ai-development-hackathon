#!/bin/bash
# Prerequisite Check for DAG Orchestrated Parallel Execution
# Generated using prepare-spec-for-execution tool
# 
# This script validates all prerequisites before executing the DAG orchestration tasks

set -euo pipefail

# Configuration
SPEC_NAME="dag-orchestrated-parallel-execution"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Main prerequisite check function
main() {
    echo "🔍 DAG Orchestrated Parallel Execution - Prerequisite Check"
    echo "=========================================================="
    echo
    
    local exit_code=0
    
    # Run the Python prerequisite validator
    log_info "Running comprehensive prerequisite validation..."
    
    if python3 "$SCRIPT_DIR/check_dag_orchestrated_parallel_execution_prereqs.py"; then
        log_success "All prerequisites validated successfully"
        echo
        log_info "✨ System is ready for DAG orchestrated parallel execution"
        log_info "Next step: Run the execution script"
        log_info "Command: python3 $SCRIPT_DIR/execute_dag_orchestrated_parallel_execution_working.py"
    else
        exit_code=$?
        log_error "Prerequisite validation failed"
        echo
        log_info "Please resolve the issues above before proceeding"
        log_info "Re-run this script after fixing the prerequisites"
    fi
    
    return $exit_code
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message and exit"
        echo ""
        echo "This script validates all prerequisites for DAG orchestrated"
        echo "parallel execution including infrastructure, dependencies,"
        echo "and system readiness."
        exit 0
        ;;
esac

# Execute main function
main "$@"