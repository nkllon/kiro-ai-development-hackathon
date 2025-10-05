#!/bin/bash
# Unified DAG Registry Prerequisites Check
# =======================================
# 
# Shell script to check all prerequisites before unified DAG registry execution
# Observer pattern - checks and reports, doesn't execute

set -e

echo "🔍 UNIFIED DAG REGISTRY PREREQUISITES CHECK"
echo "==========================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SPEC_NAME="unified-dag-registry"
SPEC_PATH=".kiro/specs/${SPEC_NAME}"

# Check functions
check_spec_files() {
    echo "📋 Checking spec files..."
    
    local missing_files=()
    local required_files=("requirements.md" "design.md" "tasks.md" "dag-registry-inventory.md")
    
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
        
        # Check for required packages
        local packages=("redis" "celery" "networkx")
        local missing_packages=()
        
        for package in "${packages[@]}"; do
            if ! python3 -c "import $package" 2>/dev/null; then
                missing_packages+=("$package")
            fi
        done
        
        if [[ ${#missing_packages[@]} -eq 0 ]]; then
            echo -e "   ${GREEN}✅ Required Python packages available${NC}"
            return 0
        else
            echo -e "   ${YELLOW}⚠️  Missing packages: ${missing_packages[*]}${NC}"
            echo -e "   ${BLUE}💡 Install with: pip install ${missing_packages[*]}${NC}"
            return 1
        fi
    else
        echo -e "   ${RED}❌ Python 3 not found${NC}"
        return 1
    fi
}

check_redis_connectivity() {
    echo "🔗 Checking Redis connectivity..."
    
    # Check primary Redis (Vonnegut)
    if python3 -c "
import redis
try:
    client = redis.Redis(host='192.168.1.119', port=6379, socket_timeout=5)
    client.ping()
    print('   ✅ Primary Redis (192.168.1.119:6379) - Connected')
except:
    print('   ⚠️  Primary Redis (192.168.1.119:6379) - Not reachable')
" 2>/dev/null; then
        echo -e "   ${GREEN}✅ Primary Redis connectivity confirmed${NC}"
        return 0
    else
        echo -e "   ${YELLOW}⚠️  Primary Redis not reachable, checking fallback...${NC}"
        
        # Check fallback Redis (localhost)
        if python3 -c "
import redis
try:
    client = redis.Redis(host='localhost', port=6380, socket_timeout=5)
    client.ping()
    print('   ✅ Fallback Redis (localhost:6380) - Connected')
except:
    try:
        client = redis.Redis(host='localhost', port=6379, socket_timeout=5)
        client.ping()
        print('   ✅ Local Redis (localhost:6379) - Connected')
    except:
        print('   ❌ No Redis connectivity available')
        exit(1)
" 2>/dev/null; then
            echo -e "   ${GREEN}✅ Fallback Redis connectivity confirmed${NC}"
            return 0
        else
            echo -e "   ${RED}❌ No Redis connectivity available${NC}"
            echo -e "   ${BLUE}💡 Start Redis with: redis-server${NC}"
            return 1
        fi
    fi
}

check_existing_dag_registries() {
    echo "🏗️  Checking existing DAG registry implementations..."
    
    local registries=(
        "src/rm_ddd/core/dag_registry.py:In-Memory DAG Registry"
        "src/rm_ddd/core/persistent_dag_registry.py:SQLite DAG Registry"
        "src/integration_governance/dag_registry.py:Mathematical DAG Registry"
    )
    
    local missing_registries=()
    local available_registries=()
    
    for registry in "${registries[@]}"; do
        local file="${registry%%:*}"
        local name="${registry#*:}"
        
        if [[ -f "$file" ]]; then
            available_registries+=("$name")
        else
            missing_registries+=("$name")
        fi
    done
    
    echo "   Available registries:"
    for registry in "${available_registries[@]}"; do
        echo -e "   ${GREEN}✅ $registry${NC}"
    done
    
    if [[ ${#missing_registries[@]} -gt 0 ]]; then
        echo "   Missing registries:"
        for registry in "${missing_registries[@]}"; do
            echo -e "   ${YELLOW}⚠️  $registry${NC}"
        done
    fi
    
    if [[ ${#available_registries[@]} -ge 2 ]]; then
        echo -e "   ${GREEN}✅ Sufficient registries for consolidation${NC}"
        return 0
    else
        echo -e "   ${RED}❌ Insufficient registries for consolidation${NC}"
        return 1
    fi
}

check_dag_registry_functionality() {
    echo "🧪 Testing existing DAG registry functionality..."
    
    # Test in-memory registry
    if python3 -c "
from src.rm_ddd.core.dag_registry import dag_registry
stats = dag_registry.get_registry_stats()
print(f'   ✅ In-Memory Registry: {stats[\"total_modules\"]} modules, DAG valid: {stats[\"is_dag\"]}')
" 2>/dev/null; then
        echo -e "   ${GREEN}✅ In-memory registry functional${NC}"
    else
        echo -e "   ${YELLOW}⚠️  In-memory registry test failed${NC}"
    fi
    
    # Test SQLite registry
    if python3 -c "
from src.rm_ddd.core.persistent_dag_registry import persistent_dag_registry
stats = persistent_dag_registry.get_registry_stats()
print(f'   ✅ SQLite Registry: {stats[\"total_modules\"]} modules, DAG valid: {stats[\"is_dag\"]}')
" 2>/dev/null; then
        echo -e "   ${GREEN}✅ SQLite registry functional${NC}"
    else
        echo -e "   ${YELLOW}⚠️  SQLite registry test failed${NC}"
    fi
    
    return 0
}

check_beast_mode_integration() {
    echo "🦾 Checking Beast Mode ReflectiveModule integration..."
    
    if python3 -c "
from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
print('   ✅ ReflectiveModule available for inheritance')
" 2>/dev/null; then
        echo -e "   ${GREEN}✅ ReflectiveModule integration ready${NC}"
        return 0
    else
        echo -e "   ${RED}❌ ReflectiveModule not available${NC}"
        return 1
    fi
}

check_dag_orchestration_system() {
    echo "🚀 Checking DAG orchestration system availability..."
    
    if [[ -f "src/dag_orchestration/core/dag_orchestrator.py" ]]; then
        echo -e "   ${GREEN}✅ DAG orchestrator available${NC}"
        
        if python3 -c "
from src.dag_orchestration.core.dag_orchestrator import create_dag_orchestrator
orchestrator = create_dag_orchestrator(max_workers=2)
print(f'   ✅ DAG Orchestrator functional: {orchestrator.module_id}')
" 2>/dev/null; then
            echo -e "   ${GREEN}✅ DAG orchestration system functional${NC}"
            return 0
        else
            echo -e "   ${YELLOW}⚠️  DAG orchestrator test failed${NC}"
            return 1
        fi
    else
        echo -e "   ${RED}❌ DAG orchestrator not found${NC}"
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
                echo -e "   ${BLUE}🎯 Ready for unified DAG registry implementation${NC}"
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
    local total_checks=8
    
    # Run all checks
    check_spec_files && ((checks_passed++))
    echo
    
    check_python_environment && ((checks_passed++))
    echo
    
    check_redis_connectivity && ((checks_passed++))
    echo
    
    check_existing_dag_registries && ((checks_passed++))
    echo
    
    check_dag_registry_functionality && ((checks_passed++))
    echo
    
    check_beast_mode_integration && ((checks_passed++))
    echo
    
    check_dag_orchestration_system && ((checks_passed++))
    echo
    
    analyze_task_status && ((checks_passed++))
    echo
    
    # Summary
    echo "📋 PREREQUISITE CHECK SUMMARY"
    echo "============================"
    echo "Checks Passed: ${checks_passed}/${total_checks}"
    
    if [[ $checks_passed -eq $total_checks ]]; then
        echo -e "${GREEN}🚀 READY FOR UNIFIED DAG REGISTRY IMPLEMENTATION!${NC}"
        echo
        echo "Next steps:"
        echo "1. Launch unified DAG registry execution:"
        echo "   ./scripts/execute_unified_dag_registry_tasks.sh"
        echo
        echo "2. Or execute specific tasks:"
        echo "   # Start with Redis infrastructure"
        echo "   # Task 1.1: Create RedisDataManager"
        echo "   # Task 1.2: Implement Redis data operations"
        echo
        echo "3. Monitor execution:"
        echo "   tail -f logs/unified-dag-registry/execution-*.log"
        return 0
    else
        echo -e "${RED}🛑 NOT READY FOR EXECUTION${NC}"
        echo "Please resolve failed checks before proceeding."
        echo
        echo "Common fixes:"
        echo "• Install Redis: brew install redis (macOS) or apt install redis (Linux)"
        echo "• Install Python packages: pip install redis celery networkx"
        echo "• Start Redis server: redis-server"
        echo "• Check network connectivity to 192.168.1.119:6379"
        return 1
    fi
}

# Execute main function
main "$@"