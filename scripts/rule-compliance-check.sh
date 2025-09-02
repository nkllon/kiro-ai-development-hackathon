#!/bin/bash
# Rule Compliance Checker
# Validates that files follow deterministic editing rules and other coding standards

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname ""SCRIPT_DI"R")"
RULES_DIR=""PROJECT_ROOT"/.cursor/rules"
VIOLATIONS=0
TOTAL_CHECKS=0

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    ((VIOLATIONS++))
}

# Check if file uses deterministic editing
check_deterministic_editing() {
    local file="$1"
    local file_type="${file##*.}"
    
    case ""file_typ"e" in
        yaml|yml|json|toml|ini|cfg|mdc|py|xml|properties|env)
            log_info "Checking deterministic editing for "fil"e"
            
            # Check for common non-deterministic patterns
            if grep -q "edit_file" ""fil"e" 2>/dev/null; then
                log_error "File "fil"e may use non-deterministic edit_file tool"
                return 1
            fi
            
            # Check for proper YAML frontmatter in .mdc files
            if [[ ""file_typ"e" == "mdc" ]]; then
                if ! grep -q "^---$" ""fil"e" 2>/dev/null; then
                    log_error "File "fil"e missing YAML frontmatter"
                    return 1
                fi
                
                if ! grep -q "description:" ""fil"e" 2>/dev/null; then
                    log_error "File "fil"e missing description in frontmatter"
                    return 1
                fi
                
                if ! grep -q "globs:" ""fil"e" 2>/dev/null; then
                    log_error "File "fil"e missing globs in frontmatter"
                    return 1
                fi
            fi
            
            log_success "File "fil"e passes deterministic editing checks"
            ;;
    esac
    return 0
}

# Check security compliance
check_security_compliance() {
    local file="$1"
    
    log_info "Checking security compliance for "fil"e"
    
    # Check for hardcoded credentials
    if grep -q -E "(password|secret|key|token).*=.*['\"][^'\"]*['\"]" ""fil"e" 2>/dev/null
then
        log_error "File "fil"e contains potential hardcoded credentials"
        return 1
    fi
    
    # Check for AWS keys
    if grep -q "AKIA[0-9A-Z]\{16\}" ""fil"e" 2>/dev/null; then
        log_error "File "fil"e contains potential AWS access keys"
        return 1
    fi
    
    # Check for UUID patterns
    if grep -q "[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}" ""fil"e" 2>/dev/null
then
        log_warning "File "fil"e contains UUID patterns (may be legitimate)"
    fi
    
    log_success "File "fil"e passes security compliance checks"
    return 0
}

# Check .mdc file structure
check_mdc_structure() {
    local file="$1"
    
    if [[ "${file##*.}" != "mdc" ]]; then
        return 0
    fi
    
    log_info "Checking .mdc file structure for "fil"e"
    
    # Check for proper YAML frontmatter
    if ! awk '/^---$/{count++} END{exit count!=2}' ""fil"e" 2>/dev/null; then
        log_error "File "fil"e has incorrect YAML frontmatter structure"
        return 1
    fi
    
    # Check for required frontmatter fields
    local has_description=false
    local has_globs=false
    local has_always_apply=false
    
    while IFS= read -r line; do
        if [[ ""lin"e" =~ ^description: ]]; then
            has_description=true
        elif [[ ""lin"e" =~ ^globs: ]]; then
            has_globs=true
        elif [[ ""lin"e" =~ ^alwaysApply: ]]; then
            has_always_apply=true
        fi
    done < ""fil"e"
    
    if [[ ""has_descriptio"n" == "false" ]]; then
        log_error "File "fil"e missing description field"
        return 1
    fi
    
    if [[ ""has_glob"s" == "false" ]]; then
        log_error "File "fil"e missing globs field"
        return 1
    fi
    
    if [[ ""has_always_appl"y" == "false" ]]; then
        log_error "File "fil"e missing alwaysApply field"
        return 1
    fi
    
    log_success "File "fil"e has correct .mdc structure"
    return 0
}

# Check file organization compliance
check_file_organization() {
    local file="$1"
    
    log_info "Checking file organization compliance for "fil"e"
    
    # Check if file is in appropriate directory based on type
    local file_type="${file##*.}"
    local dir_name="$(dirname ""fil"e")"
    
    case ""file_typ"e" in
        py)
            if [[ ""dir_nam"e" == "src/"* ]] || [[ ""dir_nam"e" == "tests/" ]] || [[ ""dir_nam"e" == "scripts/" ]]
then
                log_success "Python file "fil"e is in appropriate directory"
            else
                log_warning "Python file "fil"e may be in wrong directory"
            fi
            ;;
        md)
            if [[ ""dir_nam"e" == "docs/" ]] || [[ ""dir_nam"e" == "." ]] || [[ ""dir_nam"e" == "healthcare-cdc/" ]]
then
                log_success "Markdown file "fil"e is in appropriate directory"
            else
                log_warning "Markdown file "fil"e may be in wrong directory"
            fi
            ;;
        yaml|yml)
            if [[ ""dir_nam"e" == "config/" ]] || [[ ""dir_nam"e" == "." ]]; then
                log_success "YAML file "fil"e is in appropriate directory"
            else
                log_warning "YAML file "fil"e may be in wrong directory"
            fi
            ;;
        json)
            if [[ ""dir_nam"e" == "data/" ]] || [[ ""dir_nam"e" == "config/" ]] || [[ ""dir_nam"e" == "." ]]
then
                log_success "JSON file "fil"e is in appropriate directory"
            else
                log_warning "JSON file "fil"e may be in wrong directory"
            fi
            ;;
    esac
}

# Main validation function
validate_file() {
    local file="$1"
    ((TOTAL_CHECKS++))
    
    log_info "Validating file: "fil"e"
    
    local has_violations=false
    
    # Run all checks
    if ! check_deterministic_editing ""fil"e"; then
        has_violations=true
    fi
    
    if ! check_security_compliance ""fil"e"; then
        has_violations=true
    fi
    
    if ! check_mdc_structure ""fil"e"; then
        has_violations=true
    fi
    
    check_file_organization ""fil"e"
    
    if [[ ""has_violation"s" == "true" ]]; then
        return 1
    fi
    
    return 0
}

# Process all files
main() {
    log_info "Starting rule compliance check"
    
    # Get list of files to check (excluding git, node_modules, etc.)
    local files_to_check
    files_to_check=$(find . -type f \ \
( -name "*.py" -o -name "*.md" -o -name "*.yaml" -o -name "*.yml" -o -name "*.json" -o
-name "*.mdc" -o -name "*.sh" \) \
        -not -path "./.git/*" \
        -not -path "./node_modules/*" \
        -not -path "./__pycache__/*" \
        -not -path "./.pytest_cache/*" \
        -not -path "./.mypy_cache/*" \
        -not -path "./venv/*" \
        -not -path "./.venv/*" \
        -not -path "./env/*" \
        -not -path "./.env/*")
    
    local failed_files=0
    
    while IFS= read -r file; do
        if [[ -n ""fil"e" ]]; then
            if ! validate_file ""fil"e"; then
                ((failed_files++))
            fi
        fi
    done <<< ""files_to_chec"k"
    
    # Summary
    echo
    log_info "Rule compliance check completed"
    log_info "Total files checked: "TOTAL_CHECK"S"
    log_info "Violations found: "VIOLATION"S"
    log_info "Files with issues: "failed_file"s"
    
    if [[ "VIOLATION"S -eq 0 ]]; then
        log_success "All files pass rule compliance checks!"
        exit 0
    else
        log_error "Found "VIOLATION"S violations. Please fix before committing."
        exit 1
    fi
}

# Run main function
main "$@" 
