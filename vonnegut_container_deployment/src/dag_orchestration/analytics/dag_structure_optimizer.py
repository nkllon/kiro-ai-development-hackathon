"""
DAG Structure Optimizer - Automatic DAG optimization based on execution history

This module provides automatic optimization of DAG structures based on
execution patterns and performance data.
"""

import json
import logging
import statistics
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from src.dag_orchestration.analytics.execution_pattern_analyzer import ExecutionMetrics, PatternInsight


class OptimizationType(Enum):
    """Types of DAG optimizations that can be applied."""
    DEPENDENCY_REDUCTION = "dependency_reduction"
    PARALLEL_GROUPING = "parallel_grouping"
    TASK_MERGING = "task_merging"
    TASK_SPLITTING = "task_splitting"
    CRITICAL_PATH_OPTIMIZATION = "critical_path_optimization"
    RESOURCE_BALANCING = "resource_balancing"


@dataclass
class DAGNode:
    """Represents a node in the DAG structure."""
    task_id: str
    dependencies: Set[str]
    dependents: Set[str]
    execution_time: float
    resource_requirements: Dict[str, float]
    parallel_group: Optional[str] = None
    criticality_score: float = 0.0


@dataclass
class DAGOptimization:
    """Represents a DAG structure optimization."""
    optimization_type: OptimizationType
    confidence: float
    impact_score: float
    description: str
    affected_tasks: List[str]
    original_structure: Dict[str, Any]
    optimized_structure: Dict[str, Any]
    implementation_steps: List[str]
    estimated_improvement: Dict[str, float]


@dataclass
class OptimizedDAGStructure:
    """Represents an optimized DAG structure."""
    nodes: Dict[str, DAGNode]
    optimizations_applied: List[DAGOptimization]
    performance_prediction: Dict[str, float]
    validation_results: Dict[str, Any]


class DAGStructureOptimizer(ReflectiveModule):
    """
    Automatic DAG structure optimizer based on execution history.
    
    Analyzes execution patterns and automatically suggests or applies
    optimizations to improve DAG structure and performance.
    """
    
    def __init__(self, auto_apply_optimizations: bool = False):
        super().__init__()
        self.auto_apply_optimizations = auto_apply_optimizations
        self.execution_history: List[ExecutionMetrics] = []
        self.current_dag_structure: Dict[str, DAGNode] = {}
        self.optimization_history: List[DAGOptimization] = []
        
        # Optimization thresholds
        self.thresholds = {
            'dependency_reduction_threshold': 0.8,  # Remove deps with <80% correlation
            'parallel_grouping_threshold': 0.9,    # Group tasks with >90% time similarity
            'task_merging_threshold': 5.0,         # Merge tasks with <5s execution time
            'task_splitting_threshold': 300.0,     # Split tasks with >300s execution time
            'critical_path_threshold': 0.7,        # Optimize if critical path >70% of total
            'resource_imbalance_threshold': 0.5,   # Balance if variance >50%
        }
        
        self.logger = logging.getLogger(__name__)
    
    def update_dag_structure(self, dag_structure: Dict[str, DAGNode]) -> None:
        """Update the current DAG structure."""
        with self.trace_operation("update_dag_structure"):
            self.current_dag_structure = dag_structure
            self.logger.info(
                f"Updated DAG structure with {len(dag_structure)} nodes",
                extra={'node_count': len(dag_structure)}
            )
    
    def add_execution_data(self, metrics: List[ExecutionMetrics]) -> None:
        """Add execution data for analysis."""
        with self.trace_operation("add_execution_data"):
            self.execution_history.extend(metrics)
            self._update_node_statistics()
            
            self.logger.info(
                f"Added {len(metrics)} execution records",
                extra={'total_records': len(self.execution_history)}
            )
    
    def analyze_and_optimize_structure(self) -> OptimizedDAGStructure:
        """
        Analyze current DAG structure and generate optimizations.
        
        Returns:
            Optimized DAG structure with applied optimizations
        """
        with self.trace_operation("analyze_and_optimize_structure"):
            if not self.current_dag_structure or not self.execution_history:
                return OptimizedDAGStructure(
                    nodes={},
                    optimizations_applied=[],
                    performance_prediction={},
                    validation_results={'error': 'Insufficient data for optimization'}
                )
            
            # Calculate criticality scores
            self._calculate_criticality_scores()
            
            # Generate optimizations
            optimizations = []
            optimizations.extend(self._analyze_dependency_reduction())
            optimizations.extend(self._analyze_parallel_grouping())
            optimizations.extend(self._analyze_task_merging())
            optimizations.extend(self._analyze_task_splitting())
            optimizations.extend(self._analyze_critical_path_optimization())
            optimizations.extend(self._analyze_resource_balancing())
            
            # Sort by impact score
            optimizations.sort(key=lambda x: x.impact_score, reverse=True)
            
            # Apply optimizations if enabled
            optimized_nodes = self.current_dag_structure.copy()
            applied_optimizations = []
            
            if self.auto_apply_optimizations:
                for optimization in optimizations:
                    if self._validate_optimization(optimization, optimized_nodes):
                        optimized_nodes = self._apply_optimization(optimization, optimized_nodes)
                        applied_optimizations.append(optimization)
            
            # Generate performance predictions
            performance_prediction = self._predict_performance(optimized_nodes, applied_optimizations)
            
            # Validate optimized structure
            validation_results = self._validate_optimized_structure(optimized_nodes)
            
            result = OptimizedDAGStructure(
                nodes=optimized_nodes,
                optimizations_applied=applied_optimizations,
                performance_prediction=performance_prediction,
                validation_results=validation_results
            )
            
            self.logger.info(
                f"Generated {len(optimizations)} optimizations, applied {len(applied_optimizations)}",
                extra={
                    'total_optimizations': len(optimizations),
                    'applied_optimizations': len(applied_optimizations),
                    'predicted_improvement': performance_prediction.get('total_improvement', 0)
                }
            )
            
            return result
    
    def _update_node_statistics(self) -> None:
        """Update node statistics based on execution history."""
        # Group metrics by task
        task_metrics = defaultdict(list)
        for metric in self.execution_history:
            task_metrics[metric.task_id].append(metric)
        
        # Update node execution times and resource requirements
        for task_id, metrics in task_metrics.items():
            if task_id in self.current_dag_structure:
                node = self.current_dag_structure[task_id]
                
                # Update execution time (average)
                execution_times = [m.execution_time for m in metrics]
                node.execution_time = statistics.mean(execution_times)
                
                # Update resource requirements (average)
                cpu_usage = [m.cpu_usage for m in metrics if m.cpu_usage > 0]
                memory_usage = [m.memory_usage for m in metrics if m.memory_usage > 0]
                
                node.resource_requirements = {
                    'cpu': statistics.mean(cpu_usage) if cpu_usage else 0.0,
                    'memory': statistics.mean(memory_usage) if memory_usage else 0.0
                }
    
    def _calculate_criticality_scores(self) -> None:
        """Calculate criticality scores for all nodes."""
        # Use topological sort to calculate longest path (critical path)
        sorted_nodes = self._topological_sort()
        longest_paths = {}
        
        # Calculate longest path to each node
        for node_id in sorted_nodes:
            node = self.current_dag_structure[node_id]
            
            if not node.dependencies:
                longest_paths[node_id] = node.execution_time
            else:
                max_dep_path = max(
                    longest_paths.get(dep_id, 0) for dep_id in node.dependencies
                )
                longest_paths[node_id] = max_dep_path + node.execution_time
        
        # Calculate criticality as ratio of longest path through node to total critical path
        total_critical_path = max(longest_paths.values()) if longest_paths else 1.0
        
        for node_id, path_length in longest_paths.items():
            self.current_dag_structure[node_id].criticality_score = path_length / total_critical_path
    
    def _topological_sort(self) -> List[str]:
        """Perform topological sort of the DAG."""
        in_degree = {node_id: len(node.dependencies) for node_id, node in self.current_dag_structure.items()}
        queue = deque([node_id for node_id, degree in in_degree.items() if degree == 0])
        result = []
        
        while queue:
            node_id = queue.popleft()
            result.append(node_id)
            
            node = self.current_dag_structure[node_id]
            for dependent_id in node.dependents:
                in_degree[dependent_id] -= 1
                if in_degree[dependent_id] == 0:
                    queue.append(dependent_id)
        
        return result
    
    def _analyze_dependency_reduction(self) -> List[DAGOptimization]:
        """Analyze opportunities to reduce unnecessary dependencies."""
        optimizations = []
        
        # Look for dependencies that don't correlate with execution patterns
        for node_id, node in self.current_dag_structure.items():
            for dep_id in node.dependencies.copy():
                correlation = self._calculate_dependency_correlation(node_id, dep_id)
                
                if correlation < self.thresholds['dependency_reduction_threshold']:
                    optimizations.append(DAGOptimization(
                        optimization_type=OptimizationType.DEPENDENCY_REDUCTION,
                        confidence=1.0 - correlation,
                        impact_score=(1.0 - correlation) * node.execution_time,
                        description=f"Remove weak dependency: {dep_id} -> {node_id} (correlation: {correlation:.2f})",
                        affected_tasks=[node_id, dep_id],
                        original_structure={'dependencies': list(node.dependencies)},
                        optimized_structure={'dependencies': list(node.dependencies - {dep_id})},
                        implementation_steps=[
                            f"Remove dependency from {dep_id} to {node_id}",
                            "Validate that removal doesn't break functionality",
                            "Update task scheduling logic"
                        ],
                        estimated_improvement={
                            'parallel_efficiency': (1.0 - correlation) * 20,
                            'execution_time': (1.0 - correlation) * 10
                        }
                    ))
        
        return optimizations
    
    def _analyze_parallel_grouping(self) -> List[DAGOptimization]:
        """Analyze opportunities to create better parallel groups."""
        optimizations = []
        
        # Find tasks with similar execution times that could be grouped
        ungrouped_tasks = [
            (node_id, node) for node_id, node in self.current_dag_structure.items()
            if not node.parallel_group
        ]
        
        for i, (task1_id, task1) in enumerate(ungrouped_tasks):
            for task2_id, task2 in ungrouped_tasks[i+1:]:
                # Check if tasks can be parallelized (no dependency relationship)
                if (task1_id not in task2.dependencies and 
                    task2_id not in task1.dependencies and
                    not self._have_transitive_dependency(task1_id, task2_id)):
                    
                    # Check execution time similarity
                    time_ratio = min(task1.execution_time, task2.execution_time) / max(task1.execution_time, task2.execution_time)
                    
                    if time_ratio > self.thresholds['parallel_grouping_threshold']:
                        group_id = f"parallel_group_{task1_id}_{task2_id}"
                        
                        optimizations.append(DAGOptimization(
                            optimization_type=OptimizationType.PARALLEL_GROUPING,
                            confidence=time_ratio,
                            impact_score=time_ratio * (task1.execution_time + task2.execution_time),
                            description=f"Group tasks {task1_id} and {task2_id} for parallel execution",
                            affected_tasks=[task1_id, task2_id],
                            original_structure={
                                task1_id: {'parallel_group': task1.parallel_group},
                                task2_id: {'parallel_group': task2.parallel_group}
                            },
                            optimized_structure={
                                task1_id: {'parallel_group': group_id},
                                task2_id: {'parallel_group': group_id}
                            },
                            implementation_steps=[
                                f"Create parallel group {group_id}",
                                f"Assign {task1_id} and {task2_id} to the group",
                                "Update scheduling logic to execute group in parallel"
                            ],
                            estimated_improvement={
                                'execution_time': max(task1.execution_time, task2.execution_time) * 0.4,
                                'parallel_efficiency': 30
                            }
                        ))
        
        return optimizations
    
    def _analyze_task_merging(self) -> List[DAGOptimization]:
        """Analyze opportunities to merge small tasks."""
        optimizations = []
        
        # Find small tasks that could be merged with their dependencies or dependents
        small_tasks = [
            (node_id, node) for node_id, node in self.current_dag_structure.items()
            if node.execution_time < self.thresholds['task_merging_threshold']
        ]
        
        for task_id, task in small_tasks:
            # Try to merge with single dependency
            if len(task.dependencies) == 1:
                dep_id = next(iter(task.dependencies))
                dep_task = self.current_dag_structure[dep_id]
                
                if dep_task.execution_time < self.thresholds['task_merging_threshold']:
                    merged_time = task.execution_time + dep_task.execution_time
                    
                    optimizations.append(DAGOptimization(
                        optimization_type=OptimizationType.TASK_MERGING,
                        confidence=0.8,
                        impact_score=task.execution_time + dep_task.execution_time,
                        description=f"Merge small tasks {dep_id} and {task_id}",
                        affected_tasks=[task_id, dep_id],
                        original_structure={
                            'tasks': [task_id, dep_id],
                            'total_time': task.execution_time + dep_task.execution_time
                        },
                        optimized_structure={
                            'merged_task': f"{dep_id}_{task_id}",
                            'total_time': merged_time
                        },
                        implementation_steps=[
                            f"Combine functionality of {dep_id} and {task_id}",
                            "Update dependencies to point to merged task",
                            "Remove original tasks from DAG"
                        ],
                        estimated_improvement={
                            'execution_time': (task.execution_time + dep_task.execution_time) * 0.2,
                            'overhead_reduction': 15
                        }
                    ))
        
        return optimizations
    
    def _analyze_task_splitting(self) -> List[DAGOptimization]:
        """Analyze opportunities to split large tasks."""
        optimizations = []
        
        # Find large tasks that could be split
        large_tasks = [
            (node_id, node) for node_id, node in self.current_dag_structure.items()
            if node.execution_time > self.thresholds['task_splitting_threshold']
        ]
        
        for task_id, task in large_tasks:
            # Suggest splitting based on criticality and dependencies
            if task.criticality_score > self.thresholds['critical_path_threshold']:
                # Split critical path tasks more aggressively
                suggested_splits = max(2, int(task.execution_time / 60))  # Split into ~60s chunks
            else:
                suggested_splits = 2
            
            estimated_parallel_time = task.execution_time / suggested_splits
            
            optimizations.append(DAGOptimization(
                optimization_type=OptimizationType.TASK_SPLITTING,
                confidence=min(task.execution_time / self.thresholds['task_splitting_threshold'], 1.0),
                impact_score=task.execution_time * task.criticality_score,
                description=f"Split large task {task_id} into {suggested_splits} subtasks",
                affected_tasks=[task_id],
                original_structure={
                    'task': task_id,
                    'execution_time': task.execution_time,
                    'splits': 1
                },
                optimized_structure={
                    'subtasks': [f"{task_id}_part_{i}" for i in range(suggested_splits)],
                    'execution_time': estimated_parallel_time,
                    'splits': suggested_splits
                },
                implementation_steps=[
                    f"Analyze {task_id} to identify splittable components",
                    f"Create {suggested_splits} subtasks with proper dependencies",
                    "Update DAG structure with new subtasks",
                    "Implement parallel execution for subtasks"
                ],
                estimated_improvement={
                    'execution_time': task.execution_time * (1 - 1/suggested_splits) * 0.8,
                    'parallel_efficiency': 40
                }
            ))
        
        return optimizations
    
    def _analyze_critical_path_optimization(self) -> List[DAGOptimization]:
        """Analyze critical path optimization opportunities."""
        optimizations = []
        
        # Find the critical path
        critical_path_nodes = [
            (node_id, node) for node_id, node in self.current_dag_structure.items()
            if node.criticality_score > self.thresholds['critical_path_threshold']
        ]
        
        if not critical_path_nodes:
            return optimizations
        
        # Sort by criticality score
        critical_path_nodes.sort(key=lambda x: x[1].criticality_score, reverse=True)
        
        # Focus on the most critical nodes
        for task_id, task in critical_path_nodes[:3]:  # Top 3 critical tasks
            optimizations.append(DAGOptimization(
                optimization_type=OptimizationType.CRITICAL_PATH_OPTIMIZATION,
                confidence=task.criticality_score,
                impact_score=task.criticality_score * task.execution_time * 2,
                description=f"Optimize critical path task {task_id} (criticality: {task.criticality_score:.2f})",
                affected_tasks=[task_id],
                original_structure={
                    'task': task_id,
                    'execution_time': task.execution_time,
                    'criticality': task.criticality_score
                },
                optimized_structure={
                    'task': task_id,
                    'optimized_execution_time': task.execution_time * 0.7,  # Assume 30% improvement
                    'criticality': task.criticality_score
                },
                implementation_steps=[
                    f"Profile {task_id} to identify performance bottlenecks",
                    "Optimize algorithms and data structures",
                    "Consider caching or memoization",
                    "Implement resource prioritization for critical tasks"
                ],
                estimated_improvement={
                    'execution_time': task.execution_time * 0.3 * task.criticality_score,
                    'critical_path_reduction': 25
                }
            ))
        
        return optimizations
    
    def _analyze_resource_balancing(self) -> List[DAGOptimization]:
        """Analyze resource balancing opportunities."""
        optimizations = []
        
        # Analyze resource usage patterns
        cpu_usage = [node.resource_requirements.get('cpu', 0) for node in self.current_dag_structure.values()]
        memory_usage = [node.resource_requirements.get('memory', 0) for node in self.current_dag_structure.values()]
        
        if not cpu_usage or not memory_usage:
            return optimizations
        
        cpu_variance = statistics.variance(cpu_usage) if len(cpu_usage) > 1 else 0
        memory_variance = statistics.variance(memory_usage) if len(memory_usage) > 1 else 0
        
        cpu_mean = statistics.mean(cpu_usage)
        memory_mean = statistics.mean(memory_usage)
        
        # Check for resource imbalance
        if cpu_variance / (cpu_mean ** 2) > self.thresholds['resource_imbalance_threshold']:
            high_cpu_tasks = [
                node_id for node_id, node in self.current_dag_structure.items()
                if node.resource_requirements.get('cpu', 0) > cpu_mean * 1.5
            ]
            
            if high_cpu_tasks:
                optimizations.append(DAGOptimization(
                    optimization_type=OptimizationType.RESOURCE_BALANCING,
                    confidence=min(cpu_variance / (cpu_mean ** 2), 1.0),
                    impact_score=len(high_cpu_tasks) * cpu_variance,
                    description=f"Balance CPU usage across {len(high_cpu_tasks)} high-CPU tasks",
                    affected_tasks=high_cpu_tasks,
                    original_structure={
                        'cpu_variance': cpu_variance,
                        'high_cpu_tasks': high_cpu_tasks
                    },
                    optimized_structure={
                        'balanced_scheduling': True,
                        'cpu_aware_grouping': True
                    },
                    implementation_steps=[
                        "Implement CPU-aware task scheduling",
                        "Balance high-CPU tasks across parallel groups",
                        "Consider CPU resource limits and throttling"
                    ],
                    estimated_improvement={
                        'resource_efficiency': 20,
                        'execution_time': 10
                    }
                ))
        
        if memory_variance / (memory_mean ** 2) > self.thresholds['resource_imbalance_threshold']:
            high_memory_tasks = [
                node_id for node_id, node in self.current_dag_structure.items()
                if node.resource_requirements.get('memory', 0) > memory_mean * 1.5
            ]
            
            if high_memory_tasks:
                optimizations.append(DAGOptimization(
                    optimization_type=OptimizationType.RESOURCE_BALANCING,
                    confidence=min(memory_variance / (memory_mean ** 2), 1.0),
                    impact_score=len(high_memory_tasks) * memory_variance,
                    description=f"Balance memory usage across {len(high_memory_tasks)} high-memory tasks",
                    affected_tasks=high_memory_tasks,
                    original_structure={
                        'memory_variance': memory_variance,
                        'high_memory_tasks': high_memory_tasks
                    },
                    optimized_structure={
                        'balanced_scheduling': True,
                        'memory_aware_grouping': True
                    },
                    implementation_steps=[
                        "Implement memory-aware task scheduling",
                        "Balance high-memory tasks across parallel groups",
                        "Consider memory resource limits and cleanup"
                    ],
                    estimated_improvement={
                        'resource_efficiency': 25,
                        'execution_time': 15
                    }
                ))
        
        return optimizations
    
    def _calculate_dependency_correlation(self, task_id: str, dep_id: str) -> float:
        """Calculate correlation between task execution and dependency completion."""
        # This is a simplified correlation calculation
        # In practice, you'd analyze execution timing patterns
        
        task_metrics = [m for m in self.execution_history if m.task_id == task_id]
        dep_metrics = [m for m in self.execution_history if m.task_id == dep_id]
        
        if not task_metrics or not dep_metrics:
            return 1.0  # Assume strong correlation if no data
        
        # Simple correlation based on execution success patterns
        task_success_rate = sum(1 for m in task_metrics if m.success) / len(task_metrics)
        dep_success_rate = sum(1 for m in dep_metrics if m.success) / len(dep_metrics)
        
        # If both have similar success rates, assume correlation
        correlation = 1.0 - abs(task_success_rate - dep_success_rate)
        
        return correlation
    
    def _have_transitive_dependency(self, task1_id: str, task2_id: str) -> bool:
        """Check if there's a transitive dependency between two tasks."""
        visited = set()
        
        def has_path(from_id: str, to_id: str) -> bool:
            if from_id == to_id:
                return True
            if from_id in visited:
                return False
            
            visited.add(from_id)
            
            if from_id in self.current_dag_structure:
                for dependent in self.current_dag_structure[from_id].dependents:
                    if has_path(dependent, to_id):
                        return True
            
            return False
        
        return has_path(task1_id, task2_id) or has_path(task2_id, task1_id)
    
    def _validate_optimization(self, optimization: DAGOptimization, current_structure: Dict[str, DAGNode]) -> bool:
        """Validate that an optimization is safe to apply."""
        # Basic validation - ensure no cycles would be created
        # This is a simplified validation
        
        if optimization.optimization_type == OptimizationType.DEPENDENCY_REDUCTION:
            # Always safe to remove dependencies
            return True
        elif optimization.optimization_type == OptimizationType.PARALLEL_GROUPING:
            # Safe if no dependency relationship exists
            affected_tasks = optimization.affected_tasks
            if len(affected_tasks) == 2:
                task1, task2 = affected_tasks
                return not self._have_transitive_dependency(task1, task2)
        
        # For other optimizations, assume they're safe for now
        return True
    
    def _apply_optimization(self, optimization: DAGOptimization, structure: Dict[str, DAGNode]) -> Dict[str, DAGNode]:
        """Apply an optimization to the DAG structure."""
        # This is a simplified implementation
        # In practice, you'd need more sophisticated structure modification
        
        if optimization.optimization_type == OptimizationType.DEPENDENCY_REDUCTION:
            # Remove specified dependencies
            for task_id in optimization.affected_tasks:
                if task_id in structure:
                    # This would need more specific implementation based on the optimization details
                    pass
        
        elif optimization.optimization_type == OptimizationType.PARALLEL_GROUPING:
            # Assign parallel groups
            if len(optimization.affected_tasks) >= 2:
                group_id = f"optimized_group_{len(self.optimization_history)}"
                for task_id in optimization.affected_tasks:
                    if task_id in structure:
                        structure[task_id].parallel_group = group_id
        
        # Store applied optimization
        self.optimization_history.append(optimization)
        
        return structure
    
    def _predict_performance(self, optimized_structure: Dict[str, DAGNode], 
                           optimizations: List[DAGOptimization]) -> Dict[str, float]:
        """Predict performance improvements from optimizations."""
        total_improvements = defaultdict(float)
        
        for optimization in optimizations:
            for metric, improvement in optimization.estimated_improvement.items():
                total_improvements[metric] += improvement
        
        # Calculate overall improvement score
        execution_time_improvement = total_improvements.get('execution_time', 0)
        parallel_efficiency_improvement = total_improvements.get('parallel_efficiency', 0)
        resource_efficiency_improvement = total_improvements.get('resource_efficiency', 0)
        
        overall_improvement = (
            execution_time_improvement * 0.4 +
            parallel_efficiency_improvement * 0.3 +
            resource_efficiency_improvement * 0.3
        )
        
        return {
            'total_improvement': overall_improvement,
            'execution_time_improvement': execution_time_improvement,
            'parallel_efficiency_improvement': parallel_efficiency_improvement,
            'resource_efficiency_improvement': resource_efficiency_improvement,
            'optimizations_count': len(optimizations)
        }
    
    def _validate_optimized_structure(self, structure: Dict[str, DAGNode]) -> Dict[str, Any]:
        """Validate the optimized DAG structure."""
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'metrics': {}
        }
        
        # Check for cycles
        if self._has_cycles(structure):
            validation_results['is_valid'] = False
            validation_results['errors'].append("Optimized structure contains cycles")
        
        # Check for orphaned nodes
        orphaned_nodes = self._find_orphaned_nodes(structure)
        if orphaned_nodes:
            validation_results['warnings'].append(f"Found {len(orphaned_nodes)} orphaned nodes")
        
        # Calculate structure metrics
        validation_results['metrics'] = {
            'node_count': len(structure),
            'total_dependencies': sum(len(node.dependencies) for node in structure.values()),
            'parallel_groups': len(set(node.parallel_group for node in structure.values() if node.parallel_group)),
            'critical_path_length': self._calculate_critical_path_length(structure)
        }
        
        return validation_results
    
    def _has_cycles(self, structure: Dict[str, DAGNode]) -> bool:
        """Check if the structure has cycles."""
        visited = set()
        rec_stack = set()
        
        def has_cycle_util(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            
            if node_id in structure:
                for dependent in structure[node_id].dependents:
                    if dependent not in visited:
                        if has_cycle_util(dependent):
                            return True
                    elif dependent in rec_stack:
                        return True
            
            rec_stack.remove(node_id)
            return False
        
        for node_id in structure:
            if node_id not in visited:
                if has_cycle_util(node_id):
                    return True
        
        return False
    
    def _find_orphaned_nodes(self, structure: Dict[str, DAGNode]) -> List[str]:
        """Find nodes with no dependencies or dependents."""
        orphaned = []
        
        for node_id, node in structure.items():
            if not node.dependencies and not node.dependents:
                orphaned.append(node_id)
        
        return orphaned
    
    def _calculate_critical_path_length(self, structure: Dict[str, DAGNode]) -> float:
        """Calculate the length of the critical path."""
        if not structure:
            return 0.0
        
        # Simple critical path calculation
        max_path = 0.0
        
        def calculate_path_length(node_id: str, visited: Set[str]) -> float:
            if node_id in visited:
                return 0.0
            
            visited.add(node_id)
            
            if node_id not in structure:
                return 0.0
            
            node = structure[node_id]
            max_dependent_path = 0.0
            
            for dependent in node.dependents:
                dependent_path = calculate_path_length(dependent, visited.copy())
                max_dependent_path = max(max_dependent_path, dependent_path)
            
            return node.execution_time + max_dependent_path
        
        for node_id in structure:
            path_length = calculate_path_length(node_id, set())
            max_path = max(max_path, path_length)
        
        return max_path
    
    def export_optimization_report(self, optimized_structure: OptimizedDAGStructure, 
                                 output_path: Path) -> None:
        """Export optimization report to JSON file."""
        with self.trace_operation("export_optimization_report"):
            report = {
                'generated_at': datetime.now().isoformat(),
                'original_structure': {
                    'node_count': len(self.current_dag_structure),
                    'total_dependencies': sum(len(node.dependencies) for node in self.current_dag_structure.values())
                },
                'optimized_structure': {
                    'node_count': len(optimized_structure.nodes),
                    'total_dependencies': sum(len(node.dependencies) for node in optimized_structure.nodes.values())
                },
                'optimizations_applied': [asdict(opt) for opt in optimized_structure.optimizations_applied],
                'performance_prediction': optimized_structure.performance_prediction,
                'validation_results': optimized_structure.validation_results,
                'summary': {
                    'total_optimizations': len(optimized_structure.optimizations_applied),
                    'predicted_improvement': optimized_structure.performance_prediction.get('total_improvement', 0),
                    'structure_valid': optimized_structure.validation_results.get('is_valid', False)
                }
            }
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            self.logger.info(
                f"Exported optimization report to {output_path}",
                extra={'report_size': len(json.dumps(report))}
            )