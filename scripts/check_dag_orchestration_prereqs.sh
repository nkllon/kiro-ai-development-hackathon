#!/bin/bash
# DAG Orchestration Prerequisites Check
# ====================================
# 
# Shell script to check all prerequisites before DAG orchestrated execution
# Observer pattern - checks and reports, doesn't execute

set -e

echo "🔍 DAG ORCHESTRATION PREREQUISITES CHECK"
echo "========================================"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SPEC_NAME="dag-orchestrated-parallel-execution"
SPEC_PATH=".kiro/specs/${SPEC_NAME}"

# Check functions
check_spec_files() {
    echo "📋 Checking spec files..."
    
    local missing_files=()
    local required_files=("requirements.md" "design.md" "tasks.md")
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "${SPEC_PATH}/${file}" ]]; then
            missing_files+=("$file")
        fi
    done
    
    if [[ ${#missing_files[@]} -eq 0 ]]; then
        echo -e "   ${GREEN}✅ All spec files present${NC}"
        return 0
    else
        echo -e "   ${RED}❌ Missing files: ${missing_files[*]}${NC}"
        return 1
    fi
}

check_python_environment() {
    echo "🐍 Checking Python environment..."
    
    if command -v python3 &> /dev/null; then
        local python_version=$(python3 --version | cut -d' ' -f2)
        echo -e "   ${GREEN}✅ Python 3 available: ${python_version}${NC}"
        return 0
    else
        echo -e "   ${RED}❌ Python 3 not found${NC}"
        return 1
    fi
}

check_dag_orchestration_components() {
    echo "🏗️  Checking DAG orchestration components..."
    
    local components=(
        "src/dag_orchestration/core/dag_orchestrator.py"
        "src/dag_orchestration/execution/parallel_execution_engine.py"
        "src/dag_orchestration/execution/dependency_aware_scheduler.py"
        "src/rm_ddd/core/dag_registry.py"
    )
    
    local missing_components=()
    
    for component in "${components[@]}"; do
        if [[ ! -f "$component" ]]; then
            missing_components+=("$component")
        fi
    done
    
    if [[ ${#missing_components[@]} -eq 0 ]]; then
        echo -e "   ${GREEN}✅ All DAG orchestration components present${NC}"
        return 0
    else
        echo -e "   ${RED}❌ Missing components: ${missing_components[*]}${NC}"
        return 1
    fi
}

check_dag_orchestrator_functionality() {
    echo "🧪 Testing DAG orchestrator functionality..."
    
    if python3 -c "
from src.dag_orchestration.core.dag_orchestrator import create_dag_orchestrator
orchestrator = create_dag_orchestrator(max_workers=2)
print(f'   ✅ DAG Orchestrator: {orchestrator.module_id}')
" 2>/dev/null; then
        return 0
    else
        echo -e "   ${RED}❌ DAG orchestrator test failed${NC}"
        return 1
    fi
}

check_prepare_spec_system() {
    echo "📦 Checking prepare-spec-for-execution system..."
    
    if [[ -d ".kiro/specs/prepare-spec-for-execution" ]]; then
        echo -e "   ${GREEN}✅ prepare-spec-for-execution system available${NC}"
        return 0
    else
        echo -e "   ${RED}❌ prepare-spec-for-execution system not found${NC}"
        return 1
    fi
}

analyze_task_status() {
    echo "📊 Analyzing task status..."
    
    if [[ -f "${SPEC_PATH}/tasks.md" ]]; then
        local completed=$(grep -c "^- \[x\]" "${SPEC_PATH}/tasks.md" || echo "0")
        local remaining=$(grep -c "^- \[ \]" "${SPEC_PATH}/tasks.md" || echo "0")
        local total=$((completed + remaining))
        
        if [[ $total -gt 0 ]]; then
            local completion_rate=$((completed * 100 / total))
            echo "   Total Tasks: $total"
            echo "   Completed: $completed"
            echo "   Remaining: $remaining"
            echo "   Completion: ${completion_rate}%"
            
            if [[ $remaining -gt 0 ]]; then
                echo -e "   ${BLUE}🎯 Ready for DAG orchestrated execution${NC}"
                return 0
            else
                echo -e "   ${GREEN}✅ All tasks completed${NC}"
                return 0
            fi
        else
            echo -e "   ${YELLOW}⚠️  No tasks found${NC}"
            return 1
        fi
    else
        echo -e "   ${RED}❌ tasks.md not found${NC}"
        return 1
    fi
}

# Main execution
main() {
    local checks_passed=0
    local total_checks=6
    
    # Run all checks
    check_spec_files && ((checks_passed++))
    echo
    
    check_python_environment && ((checks_passed++))
    echo
    
    check_dag_orchestration_components && ((checks_passed++))
    echo
    
    check_dag_orchestrator_functionality && ((checks_passed++))
    echo
    
    check_prepare_spec_system && ((checks_passed++))
    echo
    
    analyze_task_status && ((checks_passed++))
    echo
    
    # Summary
    echo "📋 PREREQUISITE CHECK SUMMARY"
    echo "============================"
    echo "Checks Passed: ${checks_passed}/${total_checks}"
    
    if [[ $checks_passed -eq $total_checks ]]; then
        echo -e "${GREEN}🚀 READY FOR DAG ORCHESTRATED EXECUTION!${NC}"
        echo
        echo "Next steps:"
        echo "1. Use prepare-spec-for-execution system:"
        echo "   cd .kiro/specs/prepare-spec-for-execution"
        echo "   python scripts/prepare_spec.py ${SPEC_NAME}"
        echo
        echo "2. Or execute tasks directly:"
        echo "   ./scripts/execute_dag_orchestration_tasks.sh"
        return 0
    else
        echo -e "${RED}🛑 NOT READY FOR EXECUTION${NC}"
        echo "Please resolve failed checks before proceeding."
        return 1
    fi
}

# Execute main function
main "$@"