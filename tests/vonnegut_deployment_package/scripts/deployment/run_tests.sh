#!/bin/bash
#
# Comprehensive Test Execution Script
#
# This script provides a convenient way to run the comprehensive test suite
# with various configurations and options.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
TIMEOUT=30
COVERAGE_THRESHOLD=90
PARALLEL=true
CLEANUP=true
LOG_LEVEL="INFO"
OUTPUT_FILE="test_results.json"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] [CATEGORY]"
    echo ""
    echo "OPTIONS:"
    echo "  -h, --help              Show this help message"
    echo "  -t, --timeout SECONDS   Set test timeout (default: $TIMEOUT)"
    echo "  -c, --coverage PERCENT  Set coverage threshold (default: $COVERAGE_THRESHOLD)"
    echo "  -p, --parallel          Enable parallel execution (default: $PARALLEL)"
    echo "  -s, --sequential        Disable parallel execution"
    echo "  -n, --no-cleanup        Don't cleanup temporary files"
    echo "  -l, --log-level LEVEL   Set log level (default: $LOG_LEVEL)"
    echo "  -o, --output FILE       Set output file (default: $OUTPUT_FILE)"
    echo "  -v, --verbose           Enable verbose output"
    echo "  -q, --quiet             Enable quiet output"
    echo ""
    echo "CATEGORIES:"
    echo "  all                     Run all tests (default)"
    echo "  unit                    Run unit tests only"
    echo "  integration             Run integration tests only"
    echo "  performance             Run performance tests only"
    echo "  coverage                Run coverage analysis only"
    echo "  linting                 Run code linting only"
    echo "  security                Run security scan only"
    echo "  cli                     Run CLI tests only"
    echo ""
    echo "EXAMPLES:"
    echo "  $0                      # Run all tests with default settings"
    echo "  $0 unit                 # Run unit tests only"
    echo "  $0 -t 60 -c 95         # Run with 60s timeout and 95% coverage"
    echo "  $0 -p -v performance   # Run performance tests in parallel with verbose output"
    echo "  $0 -s -q integration   # Run integration tests sequentially and quietly"
}

# Function to check dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check pytest
    if ! python3 -c "import pytest" &> /dev/null; then
        print_error "pytest is required but not installed"
        print_status "Install with: pip install pytest"
        exit 1
    fi
    
    # Check other dependencies
    local missing_deps=()
    
    if ! python3 -c "import pytest_cov" &> /dev/null; then
        missing_deps+=("pytest-cov")
    fi
    
    if ! python3 -c "import pytest_asyncio" &> /dev/null; then
        missing_deps+=("pytest-asyncio")
    fi
    
    if ! python3 -c "import pytest_timeout" &> /dev/null; then
        missing_deps+=("pytest-timeout")
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        print_warning "Missing optional dependencies: ${missing_deps[*]}"
        print_status "Install with: pip install ${missing_deps[*]}"
    fi
    
    print_success "Dependencies check completed"
}

# Function to setup environment
setup_environment() {
    print_status "Setting up test environment..."
    
    # Set environment variables
    export BEAST_MODE_TEST_MODE=true
    export BEAST_MODE_LOG_LEVEL="$LOG_LEVEL"
    export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
    
    # Create reports directory
    mkdir -p reports
    
    # Create coverage directory
    mkdir -p htmlcov
    
    print_success "Environment setup completed"
}

# Function to run tests
run_tests() {
    local category="$1"
    local verbose_flag=""
    local quiet_flag=""
    
    if [ "$VERBOSE" = true ]; then
        verbose_flag="-v"
    fi
    
    if [ "$QUIET" = true ]; then
        quiet_flag="-q"
    fi
    
    print_status "Running $category tests..."
    
    # Build command
    local cmd="python3 tests/run_comprehensive_tests.py"
    cmd="$cmd --timeout $TIMEOUT"
    cmd="$cmd --coverage-threshold $COVERAGE_THRESHOLD"
    cmd="$cmd --log-level $LOG_LEVEL"
    cmd="$cmd --output $OUTPUT_FILE"
    
    if [ "$PARALLEL" = true ]; then
        cmd="$cmd --parallel"
    fi
    
    if [ "$CLEANUP" = false ]; then
        cmd="$cmd --no-cleanup"
    fi
    
    cmd="$cmd --category $category"
    
    # Run command
    if [ "$VERBOSE" = true ]; then
        print_status "Executing: $cmd"
    fi
    
    if eval "$cmd"; then
        print_success "$category tests completed successfully"
        return 0
    else
        print_error "$category tests failed"
        return 1
    fi
}

# Function to generate reports
generate_reports() {
    print_status "Generating test reports..."
    
    # Generate coverage report
    if [ -f "coverage.json" ]; then
        print_status "Generating HTML coverage report..."
        python3 -m coverage html -d htmlcov
        print_success "Coverage report generated: htmlcov/index.html"
    fi
    
    # Generate test summary
    if [ -f "$OUTPUT_FILE" ]; then
        print_status "Test results saved to: $OUTPUT_FILE"
        
        # Extract summary from JSON
        if command -v jq &> /dev/null; then
            print_status "Test Summary:"
            python3 -c "
import json
with open('$OUTPUT_FILE') as f:
    data = json.load(f)
    results = data.get('results', {})
    overall = results.get('overall_success', False)
    print(f'Overall Success: {overall}')
    for category, result in results.items():
        if category != 'overall_success':
            success = result.get('success', False)
            duration = result.get('duration', 0)
            status = '✓ PASS' if success else '✗ FAIL'
            print(f'  {category:20} {status:8} ({duration:.2f}s)')
"
        fi
    fi
    
    print_success "Reports generated successfully"
}

# Function to cleanup
cleanup() {
    if [ "$CLEANUP" = true ]; then
        print_status "Cleaning up temporary files..."
        
        # Remove temporary test directories
        find . -name "beast_mode_test_*" -type d -exec rm -rf {} + 2>/dev/null || true
        
        # Remove temporary files
        find . -name "*.tmp" -delete 2>/dev/null || true
        
        print_success "Cleanup completed"
    fi
}

# Parse command line arguments
CATEGORY="all"
VERBOSE=false
QUIET=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -c|--coverage)
            COVERAGE_THRESHOLD="$2"
            shift 2
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        -s|--sequential)
            PARALLEL=false
            shift
            ;;
        -n|--no-cleanup)
            CLEANUP=false
            shift
            ;;
        -l|--log-level)
            LOG_LEVEL="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -q|--quiet)
            QUIET=true
            shift
            ;;
        unit|integration|performance|coverage|linting|security|cli|all)
            CATEGORY="$1"
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    print_status "Starting comprehensive test suite..."
    print_status "Category: $CATEGORY"
    print_status "Timeout: $TIMEOUT seconds"
    print_status "Coverage threshold: $COVERAGE_THRESHOLD%"
    print_status "Parallel execution: $PARALLEL"
    print_status "Cleanup: $CLEANUP"
    print_status "Log level: $LOG_LEVEL"
    print_status "Output file: $OUTPUT_FILE"
    echo ""
    
    # Check dependencies
    check_dependencies
    
    # Setup environment
    setup_environment
    
    # Run tests
    if run_tests "$CATEGORY"; then
        print_success "All tests completed successfully!"
        
        # Generate reports
        generate_reports
        
        # Cleanup
        cleanup
        
        exit 0
    else
        print_error "Tests failed!"
        
        # Still generate reports for failed tests
        generate_reports
        
        # Cleanup
        cleanup
        
        exit 1
    fi
}

# Run main function
main "$@"
