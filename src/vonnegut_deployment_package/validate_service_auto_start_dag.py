#!/usr/bin/env python3
"""
Service Auto-Start Governance DAG Validator
Validates the task structure for DAG compliance and parallelization
"""

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

def parse_tasks_file(file_path: Path) -> Dict[str, Dict]:
    """Parse tasks.md file and extract task information."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    tasks = {}
    
    # Find all task sections
    task_pattern = r'#### Task (\d+\.\d+): ([^\n]+)\n\n\*\*Dependencies:\*\* ([^\n]+)'
    matches = re.findall(task_pattern, content)
    
    for task_id, task_name, dependencies in matches:
        deps = []
        if dependencies.strip() != "None":
            # Parse dependencies like "Task 1.1, Task 1.4"
            dep_matches = re.findall(r'Task (\d+\.\d+)', dependencies)
            deps = dep_matches
        
        tasks[task_id] = {
            'name': task_name,
            'dependencies': deps,
            'phase': int(task_id.split('.')[0])
        }
    
    return tasks

def validate_dag_structure(tasks: Dict[str, Dict]) -> Tuple[bool, List[str]]:
    """Validate that tasks form a valid DAG."""
    issues = []
    
    # Check for circular dependencies using DFS
    def has_cycle(task_id: str, visited: Set[str], rec_stack: Set[str]) -> bool:
        visited.add(task_id)
        rec_stack.add(task_id)
        
        for dep in tasks[task_id]['dependencies']:
            if dep not in visited:
                if has_cycle(dep, visited, rec_stack):
                    return True
            elif dep in rec_stack:
                issues.append(f"Circular dependency detected: {task_id} -> {dep}")
                return True
        
        rec_stack.remove(task_id)
        return False
    
    visited = set()
    for task_id in tasks:
        if task_id not in visited:
            if has_cycle(task_id, visited, set()):
                return False, issues
    
    # Validate dependencies exist
    for task_id, task_info in tasks.items():
        for dep in task_info['dependencies']:
            if dep not in tasks:
                issues.append(f"Task {task_id} depends on non-existent task {dep}")
    
    return len(issues) == 0, issues

def calculate_parallelization(tasks: Dict[str, Dict]) -> Tuple[int, int, float]:
    """Calculate parallelization potential."""
    total_tasks = len(tasks)
    
    # Group tasks by phase
    phases = {}
    for task_id, task_info in tasks.items():
        phase = task_info['phase']
        if phase not in phases:
            phases[phase] = []
        phases[phase].append(task_id)
    
    # Count parallel tasks (tasks within same phase)
    parallel_tasks = 0
    for phase, phase_tasks in phases.items():
        if len(phase_tasks) > 1:
            parallel_tasks += len(phase_tasks)
    
    parallelization = (parallel_tasks / total_tasks) * 100
    return parallel_tasks, total_tasks, parallelization

def main():
    """Main validation function."""
    tasks_file = Path(".kiro/specs/service-auto-start-governance/tasks.md")
    
    if not tasks_file.exists():
        print("❌ Tasks file not found")
        return False
    
    print("🔍 Validating Service Auto-Start Governance DAG Structure")
    print("=" * 60)
    
    # Parse tasks
    tasks = parse_tasks_file(tasks_file)
    print(f"📊 Found {len(tasks)} tasks")
    
    # Validate DAG structure
    is_valid_dag, issues = validate_dag_structure(tasks)
    
    if is_valid_dag:
        print("✅ Valid DAG: No circular dependencies")
    else:
        print("❌ Invalid DAG structure:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    
    # Calculate parallelization
    parallel_tasks, total_tasks, parallelization = calculate_parallelization(tasks)
    print(f"✅ Parallelization: {parallelization:.1f}% ({parallel_tasks}/{total_tasks} tasks can run in parallel)")
    
    # Check all tasks have dependencies specified
    all_have_deps = all('dependencies' in task for task in tasks.values())
    if all_have_deps:
        print("✅ All tasks have dependencies specified")
    else:
        print("❌ Some tasks missing dependency specification")
    
    # Check verification sections exist
    with open(tasks_file, 'r') as f:
        content = f.read()
    
    verification_count = content.count('**Verification:**')
    rollback_count = content.count('**Rollback:**')
    
    if verification_count >= len(tasks):
        print("✅ All tasks have verification")
    else:
        print(f"❌ Missing verification sections: {verification_count}/{len(tasks)}")
    
    if rollback_count >= len(tasks):
        print("✅ All tasks have rollback procedures")
    else:
        print(f"❌ Missing rollback sections: {rollback_count}/{len(tasks)}")
    
    # Summary
    if is_valid_dag and parallelization >= 70:
        print("\n🎉 Ready for orchestration")
        return True
    else:
        print("\n⚠️ Issues found - fix before orchestration")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)