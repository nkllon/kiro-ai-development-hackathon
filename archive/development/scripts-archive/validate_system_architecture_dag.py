#!/usr/bin/env python3
"""
System Architecture DAG Validator
=================================

Validates the DAG structure for the system architecture wiring diagram spec
to ensure proper dependency management and parallel execution readiness.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Any
from dataclasses import dataclass
from collections import defaultdict, deque


@dataclass
class ValidationResult:
    """Result of DAG validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    cycle_detected: bool
    cycles: List[List[str]]
    execution_order: List[str]
    parallel_groups: Dict[str, List[str]]
    critical_path: List[str]
    estimated_parallel_time: float
    estimated_sequential_time: float


class SystemArchitectureDAGValidator:
    """Validates DAG structure and dependencies for system architecture tasks."""
    
    def __init__(self, config_file: str = "system_architecture_dag_tasks.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
        self.tasks = self._extract_tasks()
        self.dependency_graph = self._build_dependency_graph()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load task configuration from JSON file."""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Configuration file {self.config_file} not found")
        
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def _extract_tasks(self) -> Dict[str, Dict[str, Any]]:
        """Extract all tasks from task groups."""
        tasks = {}
        
        for group_name, group_data in self.config.get("task_groups", {}).items():
            for task in group_data.get("tasks", []):
                task_id = task["task_id"]
                tasks[task_id] = {
                    **task,
                    "group": group_name,
                    "parallel_execution": group_data.get("parallel_execution", False)
                }
        
        return tasks
    
    def _build_dependency_graph(self) -> Dict[str, List[str]]:
        """Build dependency graph from tasks."""
        graph = {}
        
        for task_id, task_data in self.tasks.items():
            dependencies = task_data.get("dependencies", [])
            graph[task_id] = dependencies
        
        return graph
    
    def validate_dag(self) -> ValidationResult:
        """Perform comprehensive DAG validation."""
        
        errors = []
        warnings = []
        
        # 1. Check for missing dependencies
        missing_deps = self._check_missing_dependencies()
        if missing_deps:
            errors.extend([f"Missing dependency: {dep}" for dep in missing_deps])
        
        # 2. Detect cycles
        cycles = self._detect_cycles()
        cycle_detected = len(cycles) > 0
        if cycle_detected:
            errors.extend([f"Cycle detected: {' -> '.join(cycle)}" for cycle in cycles])
        
        # 3. Validate task group dependencies
        group_errors = self._validate_group_dependencies()
        errors.extend(group_errors)
        
        # 4. Calculate execution order (topological sort)
        execution_order = []
        if not cycle_detected:
            execution_order = self._topological_sort()
        
        # 5. Identify parallel execution groups
        parallel_groups = self._identify_parallel_groups()
        
        # 6. Calculate critical path
        critical_path = self._calculate_critical_path()
        
        # 7. Estimate execution times
        sequential_time = self._estimate_sequential_time()
        parallel_time = self._estimate_parallel_time(parallel_groups)
        
        # 8. Additional validations
        additional_warnings = self._additional_validations()
        warnings.extend(additional_warnings)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            cycle_detected=cycle_detected,
            cycles=cycles,
            execution_order=execution_order,
            parallel_groups=parallel_groups,
            critical_path=critical_path,
            estimated_parallel_time=parallel_time,
            estimated_sequential_time=sequential_time
        )
    
    def _check_missing_dependencies(self) -> List[str]:
        """Check for dependencies that reference non-existent tasks."""
        missing = []
        all_task_ids = set(self.tasks.keys())
        
        for task_id, dependencies in self.dependency_graph.items():
            for dep in dependencies:
                if dep not in all_task_ids:
                    missing.append(f"{task_id} -> {dep}")
        
        return missing
    
    def _detect_cycles(self) -> List[List[str]]:
        """Detect cycles in the dependency graph using DFS."""
        
        WHITE, GRAY, BLACK = 0, 1, 2
        colors = {task_id: WHITE for task_id in self.tasks.keys()}
        cycles = []
        
        def dfs(node: str, path: List[str]) -> None:
            if colors[node] == GRAY:
                # Found a cycle
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            
            if colors[node] == BLACK:
                return
            
            colors[node] = GRAY
            path.append(node)
            
            for neighbor in self.dependency_graph.get(node, []):
                if neighbor in self.tasks:  # Only follow valid dependencies
                    dfs(neighbor, path.copy())
            
            colors[node] = BLACK
        
        for task_id in self.tasks.keys():
            if colors[task_id] == WHITE:
                dfs(task_id, [])
        
        return cycles
    
    def _validate_group_dependencies(self) -> List[str]:
        """Validate that task group dependencies are properly configured."""
        errors = []
        
        # Check that group dependencies in config match actual task dependencies
        for group_name, group_data in self.config.get("task_groups", {}).items():
            group_deps = group_data.get("dependencies", [])
            
            # Get all tasks in this group
            group_tasks = [task["task_id"] for task in group_data.get("tasks", [])]
            
            # Check if any task in this group depends on tasks from dependency groups
            for task_id in group_tasks:
                task_deps = self.dependency_graph.get(task_id, [])
                
                for dep in task_deps:
                    dep_group = self.tasks.get(dep, {}).get("group")
                    if dep_group and dep_group not in group_deps and dep_group != group_name:
                        errors.append(
                            f"Task {task_id} in group '{group_name}' depends on {dep} "
                            f"from group '{dep_group}', but '{dep_group}' is not in group dependencies"
                        )
        
        return errors
    
    def _topological_sort(self) -> List[str]:
        """Perform topological sort to get valid execution order."""
        
        # Calculate in-degrees
        in_degree = {task_id: 0 for task_id in self.tasks.keys()}
        
        for task_id, dependencies in self.dependency_graph.items():
            for dep in dependencies:
                if dep in in_degree:
                    in_degree[task_id] += 1
        
        # Use Kahn's algorithm
        queue = deque([task_id for task_id, degree in in_degree.items() if degree == 0])
        result = []
        
        while queue:
            current = queue.popleft()
            result.append(current)
            
            # Find tasks that depend on current task
            for task_id, dependencies in self.dependency_graph.items():
                if current in dependencies:
                    in_degree[task_id] -= 1
                    if in_degree[task_id] == 0:
                        queue.append(task_id)
        
        return result
    
    def _identify_parallel_groups(self) -> Dict[str, List[str]]:
        """Identify tasks that can be executed in parallel."""
        
        execution_order = self._topological_sort()
        parallel_groups = {}
        
        # Group tasks by their "level" in the DAG
        levels = {}
        task_levels = {task_id: 0 for task_id in self.tasks.keys()}
        
        # Calculate levels (longest path from root)
        for task_id in execution_order:
            dependencies = self.dependency_graph.get(task_id, [])
            if dependencies:
                max_dep_level = max(task_levels.get(dep, 0) for dep in dependencies if dep in task_levels)
                task_levels[task_id] = max_dep_level + 1
            else:
                task_levels[task_id] = 0
        
        # Group by level
        for task_id, level in task_levels.items():
            if level not in levels:
                levels[level] = []
            levels[level].append(task_id)
        
        # Create parallel groups
        for level, tasks in levels.items():
            if len(tasks) > 1:
                parallel_groups[f"level_{level}"] = tasks
        
        return parallel_groups
    
    def _calculate_critical_path(self) -> List[str]:
        """Calculate the critical path through the DAG."""
        
        # Use the execution matrix critical path if available
        execution_matrix = self.config.get("execution_matrix", {})
        if "critical_path" in execution_matrix:
            return execution_matrix["critical_path"]
        
        # Otherwise, calculate longest path
        execution_order = self._topological_sort()
        
        # Calculate longest path to each node
        distances = {task_id: 0 for task_id in self.tasks.keys()}
        predecessors = {task_id: None for task_id in self.tasks.keys()}
        
        for task_id in execution_order:
            task_duration = self.tasks[task_id].get("estimated_duration_minutes", 30)
            dependencies = self.dependency_graph.get(task_id, [])
            
            for dep in dependencies:
                if dep in distances:
                    new_distance = distances[dep] + task_duration
                    if new_distance > distances[task_id]:
                        distances[task_id] = new_distance
                        predecessors[task_id] = dep
        
        # Find the task with maximum distance
        max_task = max(distances.keys(), key=lambda x: distances[x])
        
        # Reconstruct path
        path = []
        current = max_task
        while current is not None:
            path.append(current)
            current = predecessors[current]
        
        return list(reversed(path))
    
    def _estimate_sequential_time(self) -> float:
        """Estimate total execution time if run sequentially."""
        total_time = 0
        for task_data in self.tasks.values():
            total_time += task_data.get("estimated_duration_minutes", 30)
        return total_time / 60.0  # Convert to hours
    
    def _estimate_parallel_time(self, parallel_groups: Dict[str, List[str]]) -> float:
        """Estimate total execution time with parallel execution."""
        
        execution_order = self._topological_sort()
        task_levels = {}
        
        # Calculate task levels
        for task_id in execution_order:
            dependencies = self.dependency_graph.get(task_id, [])
            if dependencies:
                max_dep_level = max(task_levels.get(dep, 0) for dep in dependencies if dep in task_levels)
                task_levels[task_id] = max_dep_level + 1
            else:
                task_levels[task_id] = 0
        
        # Calculate time per level (max time of tasks in that level)
        level_times = {}
        for task_id, level in task_levels.items():
            duration = self.tasks[task_id].get("estimated_duration_minutes", 30)
            if level not in level_times:
                level_times[level] = 0
            level_times[level] = max(level_times[level], duration)
        
        total_time = sum(level_times.values())
        return total_time / 60.0  # Convert to hours
    
    def _additional_validations(self) -> List[str]:
        """Perform additional validations and return warnings."""
        warnings = []
        
        # Check for tasks with no dependencies (potential roots)
        roots = [task_id for task_id, deps in self.dependency_graph.items() if not deps]
        if len(roots) > 5:
            warnings.append(f"Many root tasks detected ({len(roots)}). Consider consolidating.")
        
        # Check for tasks with many dependencies
        for task_id, deps in self.dependency_graph.items():
            if len(deps) > 5:
                warnings.append(f"Task {task_id} has many dependencies ({len(deps)}). Consider simplifying.")
        
        # Check for very long estimated times
        for task_id, task_data in self.tasks.items():
            duration = task_data.get("estimated_duration_minutes", 30)
            if duration > 90:
                warnings.append(f"Task {task_id} has long estimated duration ({duration} min). Consider breaking down.")
        
        return warnings
    
    def print_validation_report(self, result: ValidationResult) -> None:
        """Print a comprehensive validation report."""
        
        print("🔍 SYSTEM ARCHITECTURE DAG VALIDATION REPORT")
        print("=" * 50)
        
        # Overall status
        if result.is_valid:
            print("✅ DAG is VALID and ready for execution")
        else:
            print("❌ DAG has ERRORS that must be fixed")
        
        print(f"📊 Total tasks: {len(self.tasks)}")
        print(f"🔗 Total dependencies: {sum(len(deps) for deps in self.dependency_graph.values())}")
        
        # Errors
        if result.errors:
            print(f"\n❌ ERRORS ({len(result.errors)}):")
            for error in result.errors:
                print(f"   • {error}")
        
        # Warnings
        if result.warnings:
            print(f"\n⚠️  WARNINGS ({len(result.warnings)}):")
            for warning in result.warnings:
                print(f"   • {warning}")
        
        # Cycle detection
        if result.cycle_detected:
            print(f"\n🔄 CYCLES DETECTED ({len(result.cycles)}):")
            for cycle in result.cycles:
                print(f"   • {' -> '.join(cycle)}")
        
        # Execution order
        if result.execution_order:
            print(f"\n📋 EXECUTION ORDER:")
            for i, task_id in enumerate(result.execution_order, 1):
                task_name = self.tasks[task_id]["name"]
                print(f"   {i:2d}. {task_id}: {task_name}")
        
        # Parallel groups
        if result.parallel_groups:
            print(f"\n⚡ PARALLEL EXECUTION GROUPS:")
            for group_name, tasks in result.parallel_groups.items():
                print(f"   {group_name}: {', '.join(tasks)}")
        
        # Critical path
        if result.critical_path:
            print(f"\n🎯 CRITICAL PATH:")
            print(f"   {' -> '.join(result.critical_path)}")
        
        # Time estimates
        print(f"\n⏱️  TIME ESTIMATES:")
        print(f"   Sequential execution: {result.estimated_sequential_time:.1f} hours")
        print(f"   Parallel execution:   {result.estimated_parallel_time:.1f} hours")
        if result.estimated_sequential_time > 0:
            savings = (1 - result.estimated_parallel_time / result.estimated_sequential_time) * 100
            print(f"   Time savings:         {savings:.1f}%")
        
        print("\n" + "=" * 50)


def main():
    """Main validation function."""
    
    validator = SystemArchitectureDAGValidator()
    result = validator.validate_dag()
    validator.print_validation_report(result)
    
    # Exit with error code if validation failed
    if not result.is_valid:
        sys.exit(1)
    
    return result


if __name__ == "__main__":
    main()