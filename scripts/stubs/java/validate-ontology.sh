set -euo pipefail#!/bin/bash

# Beast Mode Ontology Validation Script
# Provides easy commands for SHACL validation, SPARQL queries, and Protégé setup

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
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

# Check if Maven is available
check_maven() {
    if ! command -v mvn &> /dev/null; then
        print_error "Maven is not installed or not in PATH"
        exit 1
    fi
}

# Show usage information
show_usage() {
    echo "Beast Mode Ontology Validation Tool"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  validate-all     Run all ontology validation tests"
    echo "  validate-shacl   Run SHACL validation only"
    echo "  validate-sparql  Run SPARQL query tests only"
    echo "  setup-protege    Set up Protégé environment"
    echo "  check-syntax     Check TTL syntax for all ontology files"
    echo "  build            Build the Java project"
    echo "  clean            Clean build artifacts"
    echo "  help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 validate-all              # Run complete validation suite"
    echo "  $0 setup-protege             # Prepare ontologies for Protégé"
    echo "  $0 validate-shacl            # Run SHACL validation only"
    echo ""
}

# Build the Java project
build_project() {
    print_status "Building Java project..."
    cd "$SCRIPT_DIR"
    mvn clean compile
    print_success "Build completed"
}

# Run all validation tests
validate_all() {
    print_status "Running complete ontology validation suite..."
    cd "$SCRIPT_DIR"
    
    # Compile first
    mvn compile
    
    # Run tests
    mvn test
    
    print_success "All validation tests completed"
}

# Run SHACL validation only
validate_shacl() {
    print_status "Running SHACL validation..."
    cd "$SCRIPT_DIR"
    
    # Compile and run SHACL validation
    mvn compile exec:java -Dexec.mainClass="com.beastmode.rmddd.utilities.ValidateShacl"
    
    print_success "SHACL validation completed"
}

# Run SPARQL query tests
validate_sparql() {
    print_status "Running SPARQL query tests..."
    cd "$SCRIPT_DIR"
    
    # Run only SPARQL-related tests
    mvn test -Dtest="*Query*"
    
    print_success "SPARQL validation completed"
}

# Set up Protégé environment
setup_protege() {
    print_status "Setting up Protégé environment..."
    cd "$SCRIPT_DIR"
    
    # Compile and run Protégé setup
    mvn compile
    mvn exec:java -Dexec.mainClass="com.beastmode.rmddd.utilities.ProtegeIntegration" -Dexec.args="setup $PROJECT_ROOT"
    
    print_success "Protégé environment setup completed"
    print_status "Open $PROJECT_ROOT/ontology/beastmaster-profile.ttl in Protégé to get started"
}

# Check TTL syntax for all ontology files
check_syntax() {
    print_status "Checking TTL syntax for all ontology files..."
    
    # Find all .ttl files
    ttl_files=$(find "$PROJECT_ROOT" -name "*.ttl" -type f)
    
    if [ -z "$ttl_files" ]; then
        print_warning "No TTL files found in $PROJECT_ROOT"
        return
    fi
    
    cd "$SCRIPT_DIR"
    mvn compile
    
    error_count=0
    
    for file in $ttl_files; do
        print_status "Checking syntax: $(basename "$file")"
        
        # Use Jena's riot tool for syntax checking
        if mvn exec:java -Dexec.mainClass="org.apache.jena.riot.riot" -Dexec.args="--validate $file" -q; then
            print_success "✓ $(basename "$file")"
        else
            print_error "✗ $(basename "$file") - syntax error"
            ((error_count++))
        fi
    done
    
    if [ $error_count -eq 0 ]; then
        print_success "All TTL files have valid syntax"
    else
        print_error "$error_count files have syntax errors"
        exit 1
    fi
}

# Clean build artifacts
clean_project() {
    print_status "Cleaning build artifacts..."
    cd "$SCRIPT_DIR"
    mvn clean
    print_success "Clean completed"
}

# Main script logic
main() {
    check_maven
    
    case "${1:-help}" in
        "validate-all")
            validate_all
            ;;
        "validate-shacl")
            validate_shacl
            ;;
        "validate-sparql")
            validate_sparql
            ;;
        "setup-protege")
            setup_protege
            ;;
        "check-syntax")
            check_syntax
            ;;
        "build")
            build_project
            ;;
        "clean")
            clean_project
            ;;
        "help"|*)
            show_usage
            ;;
    esac
}

# Run main function with all arguments
main "$@"