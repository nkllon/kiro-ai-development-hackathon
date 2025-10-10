#!/usr/bin/env python3
"""
DAG Validator - Mathematical DAG validation and cycle detection.

Provides proper mathematical validation of Directed Acyclic Graphs with
cycle detection, topological sorting, and dependency validation.
"""

import logging
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict, deque

from src.beast_mode.core.beastly_module import BeastlyModule


class ValidationResult(Enum):
    """DAG validation results"""
    VALID = "valid"
    CYCLIC = "cyclic"
    MISSING_DEPENDENCIES = "missing_dependencies"
    INVALID_STRUCTURE = "invalid_structure"


@dataclass
class DAGValidationReport:
    """Comprehensive DAG validation report"""
    result: ValidationResult
    is_valid: bool
    cycles: List[List[str]]
    missing_dependencies: List[Tuple[str, str]]
    topological_order: List[List[str]]
    execution_waves: List[List[str]]
    critical_path: List[str]
    max_parallelism: int
    total_tasks: int
    validation_errors: List[str]


@dataclass
class TaskNode:
    """Task node for DAG representation"""
    task_id: str
    dependencies: List[str]
    dependents: List[str]
    metadata: Dict[str, Any]


class DAGValidator(BeastlyModule):
    """
    Mathematical DAG validator with proper cycle detection and topological sorting.
    
    Implements Kahn's algorithm for topological sorting and DFS-based cycle detection
    to ensure mathematical correctness of task dependency graphs.
    """
    
    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(f"beast_mode.orchestration.{self.__class__.__name__}")
        
        # Validation metrics
        self._validations_performed = 0
        self._cycles_detected = 0
        self._valid_dags = 0
        
        self._logger.info("DAGValidator initialized with mathematical validation")
    
    def get_capabilities(self) -> List[Any]:
        """Get module capabilities"""
        return ["DAG_VALIDATION", "CYCLE_DETECTION", "TOPOLOGICAL_SORTING"]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get module health status"""
        return {
            "status": "healthy",
            "validations_performed": self._validations_performed,
            "cycles_detected": self._cycles_detected,
            "valid_dags": self._valid_dags
        }
    
    def graceful_degradation(self) -> Dict[str, Any]:
        """Perform graceful degradation"""
        return {
            "success": True,
            "degraded_capabilities": [],
            "remaining_capabilities": ["DAG_VALIDATION", "CYCLE_DETECTION"]
        }
    
    def validate_dag(self, tasks: Dict[str, TaskNode]) -> DAGValidationReport:
        """
        Perform comprehensive DAG validation with mathematical guarantees.
        
        Args:
            tasks: Dictionary of task_id -> TaskNode
            
        Returns:
            DAGValidationReport with complete validation results
        """
        with self.trace_operation("validate_dag") as trace:
            self._validations_performed += 1
            
            # Initialize validation report
            report = DAGValidationReport(
                result=ValidationResult.VALID,
                is_valid=True,
                cycles=[],
                missing_dependencies=[],
                topological_order=[],
                execution_waves=[],
                critical_path=[],
                max_parallelism=0,
                total_tasks=len(tasks),
                validation_errors=[]
            )
            
            try:
                # Step 1: Validate task structure
                structure_errors = self._validate_task_structure(tasks)
                if structure_errors:
                    report.validation_errors.extend(structure_errors)
                    report.result = ValidationResult.INVALID_STRUCTURE
                    report.is_valid = False
                    return report
                
                # Step 2: Check for missing dependencies
                missing_deps = self._find_missing_dependencies(tasks)
                if missing_deps:
                    report.missing_dependencies = missing_deps
                    report.validation_errors.append(f"Missing dependencies: {missing_deps}")
                    report.result = ValidationResult.MISSING_DEPENDENCIES
                    report.is_valid = False
                    return report
                
                # Step 3: Detect cycles using DFS
                cycles = self._detect_cycles_dfs(tasks)
                if cycles:
                    self._cycles_detected += 1
                    report.cycles = cycles
                    report.validation_errors.append(f"Circular dependencies detected: {cycles}")
                    report.result = ValidationResult.CYCLIC
                    report.is_valid = False
                    return report
                
                # Step 4: Generate topological ordering using Kahn's algorithm
                topological_order = self._topological_sort_kahns(tasks)
                report.topological_order = topological_order
                
                # Step 5: Create execution waves for parallel execution
                execution_waves = self._create_execution_waves(tasks)
                report.execution_waves = execution_waves
                report.max_parallelism = max(len(wave) for wave in execution_waves) if execution_waves else 0
                
                # Step 6: Calculate critical path
                critical_path = self._calculate_critical_path(tasks)
                report.critical_path = critical_path
                
                # Success metrics
                self._valid_dags += 1
                trace.output_result = {
                    'valid': True,
                    'total_tasks': len(tasks),
                    'execution_waves': len(execution_waves),
                    'max_parallelism': report.max_parallelism,
                    'critical_path_length': len(critical_path)
                }
                
                self._logger.info(f"DAG validation successful: {len(tasks)} tasks, {len(execution_waves)} waves")
                return report
                
            except Exception as e:
                self._logger.error(f"DAG validation failed: {e}")
                report.validation_errors.append(f"Validation exception: {str(e)}")
                report.result = ValidationResult.INVALID_STRUCTURE
                report.is_valid = False
                trace.output_result = {'valid': False, 'error': str(e)}
                return report
    
    def _validate_task_structure(self, tasks: Dict[str, TaskNode]) -> List[str]:
        """Validate basic task structure and data integrity"""
        errors = []
        
        for task_id, task in tasks.items():
            if not task.task_id:
                errors.append(f"Task {task_id} has empty task_id")
            
            if task.task_id != task_id:
                errors.append(f"Task ID mismatch: key={task_id}, task.task_id={task.task_id}")
            
            if not isinstance(task.dependencies, list):
                errors.append(f"Task {task_id} dependencies must be a list")
            
            if not isinstance(task.dependents, list):
                errors.append(f"Task {task_id} dependents must be a list")
        
        return errors
    
    def _find_missing_dependencies(self, tasks: Dict[str, TaskNode]) -> List[Tuple[str, str]]:
        """Find dependencies that reference non-existent tasks"""
        missing = []
        task_ids = set(tasks.keys())
        
        for task_id, task in tasks.items():
            for dep in task.dependencies:
                if dep not in task_ids:
                    missing.append((task_id, dep))
        
        return missing
    
    def _detect_cycles_dfs(self, tasks: Dict[str, TaskNode]) -> List[List[str]]:
        """
        Detect cycles using Depth-First Search with proper mathematical validation.
        
        Uses three-color DFS algorithm:
        - White (0): Unvisited
        - Gray (1): Currently being processed (in recursion stack)
        - Black (2): Completely processed
        """
        WHITE, GRAY, BLACK = 0, 1, 2
        colors = {task_id: WHITE for task_id in tasks}
        cycles = []
        current_path = []
        
        def dfs_visit(task_id: str) -> bool:
            """DFS visit with cycle detection"""
            if colors[task_id] == GRAY:
                # Found back edge - cycle detected
                cycle_start = current_path.index(task_id)
                cycle = current_path[cycle_start:] + [task_id]
                cycles.append(cycle)
                return True
            
            if colors[task_id] == BLACK:
                return False
            
            # Mark as currently being processed
            colors[task_id] = GRAY
            current_path.append(task_id)
            
            # Visit all dependencies
            for dep in tasks[task_id].dependencies:
                if dep in tasks and dfs_visit(dep):
                    return True
            
            # Mark as completely processed
            colors[task_id] = BLACK
            current_path.pop()
            return False
        
        # Check all nodes for cycles
        for task_id in tasks:
            if colors[task_id] == WHITE:
                dfs_visit(task_id)
        
        return cycles
    
    def _topological_sort_kahns(self, tasks: Dict[str, TaskNode]) -> List[List[str]]:
        """
        Topological sort using Kahn's algorithm for parallel execution waves.
        
        Returns list of lists where each inner list contains tasks that can
        be executed in parallel (have no dependencies on each other).
        """
        # Calculate in-degrees
        in_degree = {task_id: 0 for task_id in tasks}
        for task in tasks.values():
            for dep in task.dependencies:
                if dep in in_degree:
                    in_degree[dep] += 1
        
        # Initialize queue with tasks having no dependencies
        queue = deque([task_id for task_id, degree in in_degree.items() if degree == 0])
        result = []
        
        while queue:
            # Process all tasks at current level (parallel execution wave)
            current_wave = []
            wave_size = len(queue)
            
            for _ in range(wave_size):
                task_id = queue.popleft()
                current_wave.append(task_id)
                
                # Reduce in-degree for dependent tasks
                for dependent in tasks[task_id].dependents:
                    if dependent in in_degree:
                        in_degree[dependent] -= 1
                        if in_degree[dependent] == 0:
                            queue.append(dependent)
            
            if current_wave:
                result.append(current_wave)
        
        return result
    
    def _create_execution_waves(self, tasks: Dict[str, TaskNode]) -> List[List[str]]:
        """Create execution waves optimized for parallel execution"""
        # Build reverse dependency graph (dependents)
        for task_id, task in tasks.items():
            for dep in task.dependencies:
                if dep in tasks:
                    tasks[dep].dependents.append(task_id)
        
        return self._topological_sort_kahns(tasks)
    
    def _calculate_critical_path(self, tasks: Dict[str, TaskNode]) -> List[str]:
        """
        Calculate critical path (longest path) through the DAG.
        
        Uses dynamic programming to find the longest path from any source
        to any sink in the DAG.
        """
        # Calculate longest path to each node
        longest_path = {}
        path_predecessor = {}
        
        def calculate_longest_path(task_id: str) -> int:
            if task_id in longest_path:
                return longest_path[task_id]
            
            if not tasks[task_id].dependencies:
                longest_path[task_id] = 1
                return 1
            
            max_path = 0
            best_predecessor = None
            
            for dep in tasks[task_id].dependencies:
                if dep in tasks:
                    dep_path = calculate_longest_path(dep)
                    if dep_path > max_path:
                        max_path = dep_path
                        best_predecessor = dep
            
            longest_path[task_id] = max_path + 1
            path_predecessor[task_id] = best_predecessor
            return longest_path[task_id]
        
        # Calculate longest paths for all tasks
        for task_id in tasks:
            calculate_longest_path(task_id)
        
        # Find the task with the longest path (end of critical path)
        if not longest_path:
            return []
        
        end_task = max(longest_path.keys(), key=lambda x: longest_path[x])
        
        # Reconstruct critical path
        critical_path = []
        current = end_task
        
        while current is not None:
            critical_path.append(current)
            current = path_predecessor.get(current)
        
        critical_path.reverse()
        return critical_path
    
    def get_validation_metrics(self) -> Dict[str, Any]:
        """Get DAG validation metrics"""
        return {
            "validations_performed": self._validations_performed,
            "cycles_detected": self._cycles_detected,
            "valid_dags": self._valid_dags,
            "success_rate": self._valid_dags / max(self._validations_performed, 1) * 100
        }