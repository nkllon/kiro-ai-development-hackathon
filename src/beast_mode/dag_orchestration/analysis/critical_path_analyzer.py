"""
Critical path analyzer for DAG orchestration system.

Identifies longest dependency chains, bottlenecks, and calculates
completion percentages with systematic analysis capabilities.
"""

from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict, deque

from ..models.dag_models import TaskNode, CriticalPath, SpecificationNode
from ..models.enums import TaskStatus, RiskImpact
from .dependency_mapper import ConstraintGraph


@dataclass
class LayerAnalysis:
    """Analysis of a dependency layer."""
    layer_number: int
    tasks: List[str]
    total_effort: int  # hours
    max_parallel_tasks: int
    bottleneck_tasks: List[str]
    completion_percentage: float
    estimated_duration: int  # days assuming parallel execution


@dataclass
class CriticalPathAnalysis:
    """Complete critical path analysis results."""
    longest_path: CriticalPath
    all_critical_paths: List[CriticalPath]
    bottleneck_tasks: List[str]
    layer_analysis: List[LayerAnalysis]
    total_project_duration: int  # days
    completion_percentage: float
    remaining_effort: int  # hours


class CriticalPathAnalyzer:
    """
    Systematic critical path analyzer for DAG orchestration.
    
    Identifies longest dependency chains, bottlenecks, and provides
    systematic analysis of completion percentages and work estimates.
    """
    
    def __init__(self):
        self.working_hours_per_day = 8
        self.parallel_efficiency = 0.85  # 85% efficiency for parallel work
    
    def analyze_critical_paths(self, constraint_graph: ConstraintGraph) -> CriticalPathAnalysis:
        """
        Analyze critical paths in the constraint graph.
        
        Args:
            constraint_graph: Complete constraint graph with dependencies
            
        Returns:
            CriticalPathAnalysis: Complete critical path analysis
        """
        # Calculate all critical paths
        all_critical_paths = self._calculate_all_critical_paths(constraint_graph)
        
        # Find longest path
        longest_path = max(all_critical_paths, key=lambda p: p.total_duration) if all_critical_paths else None
        
        # Identify bottleneck tasks
        bottleneck_tasks = self._identify_bottleneck_tasks(constraint_graph, all_critical_paths)
        
        # Analyze dependency layers
        layer_analysis = self._analyze_dependency_layers(constraint_graph)
        
        # Calculate project metrics
        total_duration = self._calculate_total_project_duration(layer_analysis)
        completion_percentage = self._calculate_overall_completion(constraint_graph)
        remaining_effort = self._calculate_remaining_effort(constraint_graph)
        
        return CriticalPathAnalysis(
            longest_path=longest_path,
            all_critical_paths=all_critical_paths,
            bottleneck_tasks=bottleneck_tasks,
            layer_analysis=layer_analysis,
            total_project_duration=total_duration,
            completion_percentage=completion_percentage,
            remaining_effort=remaining_effort
        )
    
    def identify_bottlenecks(self, constraint_graph: ConstraintGraph) -> List[str]:
        """
        Identify bottleneck tasks that could delay the project.
        
        Args:
            constraint_graph: Constraint graph to analyze
            
        Returns:
            List[str]: Task IDs of bottleneck tasks
        """
        bottlenecks = []
        
        # Tasks with high effort and many dependents
        for task_id, task in constraint_graph.nodes.items():
            dependents = constraint_graph.get_dependents(task_id)
            
            # High effort task with many dependents
            if task.estimated_effort > 16 and len(dependents) > 3:  # More than 2 days, 3+ dependents
                bottlenecks.append(task_id)
            
            # Tasks on critical path with incomplete status
            if (task.completion_status != TaskStatus.COMPLETED and 
                self._is_on_critical_path(task_id, constraint_graph)):
                bottlenecks.append(task_id)
        
        return list(set(bottlenecks))  # Remove duplicates
    
    def calculate_completion_percentage(self, 
                                     constraint_graph: ConstraintGraph,
                                     by_effort: bool = True) -> float:
        """
        Calculate overall completion percentage.
        
        Args:
            constraint_graph: Constraint graph to analyze
            by_effort: If True, weight by effort; if False, count tasks equally
            
        Returns:
            float: Completion percentage (0.0 to 100.0)
        """
        if not constraint_graph.nodes:
            return 0.0
        
        if by_effort:
            total_effort = sum(task.estimated_effort for task in constraint_graph.nodes.values())
            completed_effort = sum(
                task.estimated_effort for task in constraint_graph.nodes.values()
                if task.completion_status == TaskStatus.COMPLETED
            )
            return (completed_effort / total_effort * 100.0) if total_effort > 0 else 0.0
        else:
            total_tasks = len(constraint_graph.nodes)
            completed_tasks = sum(
                1 for task in constraint_graph.nodes.values()
                if task.completion_status == TaskStatus.COMPLETED
            )
            return (completed_tasks / total_tasks * 100.0) if total_tasks > 0 else 0.0
    
    def estimate_remaining_work(self, constraint_graph: ConstraintGraph) -> Dict[str, int]:
        """
        Estimate remaining work by category.
        
        Args:
            constraint_graph: Constraint graph to analyze
            
        Returns:
            Dict[str, int]: Remaining effort by status category (hours)
        """
        remaining_work = {
            'not_started': 0,
            'in_progress': 0,
            'blocked': 0,
            'total': 0
        }
        
        for task in constraint_graph.nodes.values():
            if task.completion_status != TaskStatus.COMPLETED:
                remaining_work['total'] += task.estimated_effort
                
                if task.completion_status == TaskStatus.NOT_STARTED:
                    remaining_work['not_started'] += task.estimated_effort
                elif task.completion_status == TaskStatus.IN_PROGRESS:
                    remaining_work['in_progress'] += task.estimated_effort // 2  # Assume 50% complete
                elif task.completion_status == TaskStatus.BLOCKED:
                    remaining_work['blocked'] += task.estimated_effort
        
        return remaining_work
    
    def _calculate_all_critical_paths(self, constraint_graph: ConstraintGraph) -> List[CriticalPath]:
        """Calculate all critical paths in the graph."""
        critical_paths = []
        
        # Find all paths from nodes with no dependencies to nodes with no dependents
        start_nodes = [
            task_id for task_id in constraint_graph.nodes
            if not constraint_graph.get_dependencies(task_id)
        ]
        
        end_nodes = [
            task_id for task_id in constraint_graph.nodes
            if not constraint_graph.get_dependents(task_id)
        ]
        
        # Calculate paths from each start to each end
        for start_node in start_nodes:
            for end_node in end_nodes:
                path = self._find_longest_path(start_node, end_node, constraint_graph)
                if path:
                    critical_paths.append(path)
        
        # Sort by duration and return top paths
        critical_paths.sort(key=lambda p: p.total_duration, reverse=True)
        return critical_paths[:10]  # Return top 10 critical paths
    
    def _find_longest_path(self, 
                          start_node: str, 
                          end_node: str, 
                          constraint_graph: ConstraintGraph) -> Optional[CriticalPath]:
        """Find longest path between two nodes."""
        # Use dynamic programming to find longest path
        memo = {}
        
        def longest_path_from(node_id: str, target: str, visited: Set[str]) -> Tuple[int, List[str]]:
            if node_id == target:
                task = constraint_graph.nodes[node_id]
                return task.estimated_effort, [node_id]
            
            if node_id in visited:
                return 0, []  # Cycle detected
            
            if (node_id, target) in memo:
                return memo[(node_id, target)]
            
            visited.add(node_id)
            
            max_duration = 0
            best_path = []
            
            # Try all dependents
            for dependent in constraint_graph.get_dependents(node_id):
                if dependent not in visited:
                    duration, path = longest_path_from(dependent, target, visited.copy())
                    if duration > 0:  # Valid path found
                        task = constraint_graph.nodes[node_id]
                        total_duration = task.estimated_effort + duration
                        if total_duration > max_duration:
                            max_duration = total_duration
                            best_path = [node_id] + path
            
            visited.remove(node_id)
            memo[(node_id, target)] = (max_duration, best_path)
            return max_duration, best_path
        
        duration, path = longest_path_from(start_node, end_node, set())
        
        if duration > 0 and path:
            # Identify bottleneck tasks in this path
            bottleneck_tasks = []
            for task_id in path:
                task = constraint_graph.nodes[task_id]
                if task.estimated_effort > 12:  # More than 1.5 days
                    bottleneck_tasks.append(task_id)
            
            # Determine risk level based on path length and bottlenecks
            if duration > 200:  # More than 25 days
                risk_level = RiskImpact.CRITICAL
            elif duration > 120:  # More than 15 days
                risk_level = RiskImpact.HIGH
            elif duration > 80:  # More than 10 days
                risk_level = RiskImpact.MEDIUM
            else:
                risk_level = RiskImpact.LOW
            
            return CriticalPath(
                path_id=f"{start_node}_to_{end_node}",
                task_sequence=path,
                total_duration=duration,
                bottleneck_tasks=bottleneck_tasks,
                risk_level=risk_level
            )
        
        return None
    
    def _identify_bottleneck_tasks(self, 
                                 constraint_graph: ConstraintGraph,
                                 critical_paths: List[CriticalPath]) -> List[str]:
        """Identify tasks that are bottlenecks across multiple critical paths."""
        task_frequency = defaultdict(int)
        
        # Count how often each task appears in critical paths
        for path in critical_paths:
            for task_id in path.task_sequence:
                task_frequency[task_id] += 1
        
        # Tasks that appear in multiple critical paths are bottlenecks
        bottlenecks = [
            task_id for task_id, frequency in task_frequency.items()
            if frequency > 1 or constraint_graph.nodes[task_id].estimated_effort > 16
        ]
        
        return bottlenecks
    
    def _analyze_dependency_layers(self, constraint_graph: ConstraintGraph) -> List[LayerAnalysis]:
        """Analyze each dependency layer for parallel execution planning."""
        layer_analyses = []
        
        for layer_num, task_ids in constraint_graph.dependency_layers.items():
            if not task_ids:
                continue
            
            # Calculate layer metrics
            tasks = [constraint_graph.nodes[task_id] for task_id in task_ids]
            total_effort = sum(task.estimated_effort for task in tasks)
            max_parallel_tasks = len(task_ids)
            
            # Identify bottleneck tasks in this layer
            bottleneck_tasks = [
                task.task_id for task in tasks
                if task.estimated_effort > 12  # More than 1.5 days
            ]
            
            # Calculate completion percentage for this layer
            completed_tasks = sum(
                1 for task in tasks
                if task.completion_status == TaskStatus.COMPLETED
            )
            completion_percentage = (completed_tasks / len(tasks) * 100.0) if tasks else 0.0
            
            # Estimate duration assuming parallel execution
            if max_parallel_tasks > 0:
                # Assume we can parallelize effectively
                max_task_effort = max(task.estimated_effort for task in tasks)
                estimated_duration = int(
                    max_task_effort / self.working_hours_per_day * 
                    (1 / self.parallel_efficiency)
                )
            else:
                estimated_duration = 0
            
            layer_analyses.append(LayerAnalysis(
                layer_number=layer_num,
                tasks=task_ids,
                total_effort=total_effort,
                max_parallel_tasks=max_parallel_tasks,
                bottleneck_tasks=bottleneck_tasks,
                completion_percentage=completion_percentage,
                estimated_duration=estimated_duration
            ))
        
        return sorted(layer_analyses, key=lambda x: x.layer_number)
    
    def _calculate_total_project_duration(self, layer_analyses: List[LayerAnalysis]) -> int:
        """Calculate total project duration based on layer analysis."""
        return sum(analysis.estimated_duration for analysis in layer_analyses)
    
    def _calculate_overall_completion(self, constraint_graph: ConstraintGraph) -> float:
        """Calculate overall project completion percentage."""
        return self.calculate_completion_percentage(constraint_graph, by_effort=True)
    
    def _calculate_remaining_effort(self, constraint_graph: ConstraintGraph) -> int:
        """Calculate total remaining effort in hours."""
        remaining_work = self.estimate_remaining_work(constraint_graph)
        return remaining_work['total']
    
    def _is_on_critical_path(self, task_id: str, constraint_graph: ConstraintGraph) -> bool:
        """Check if a task is on any critical path."""
        # Simplified check - in practice would need to calculate actual critical paths
        # For now, check if task has high effort and many dependents
        task = constraint_graph.nodes[task_id]
        dependents = constraint_graph.get_dependents(task_id)
        
        return task.estimated_effort > 8 and len(dependents) > 1