"""
Dependency Mapper Core Core Core

This module was extracted from dependency_mapper_core_core.py
as part of RM-DDD compliance refactoring.
"""

"""
Dependency_Mapper - Consolidated Interface Definition

This file was consolidated from the core_core_core refactoring mess.
All duplicate definitions have been removed and this is now the single
authoritative source for dependency_mapper.

Consolidated from: /Users/lou/kiro-2/kiro-ai-development-hackathon/src/beast_mode/dag_orchestration/analysis/dependency_mapper_core_core_core.py
Consolidation date: 2025-09-13T10:15:07.491796
"""



from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict, deque
from ..models.dag_models import TaskNode, DependencyEdge, SpecificationNode
from ..models.enums import TaskStatus

@dataclass
class DependencyConflict:
    """Represents a dependency conflict."""
    conflict_type: str
    affected_tasks: List[str]
    description: str
    severity: str

@dataclass
class ConstraintGraph:
    """Systematic dependency representation."""
    nodes: Dict[str, TaskNode]
    edges: List[DependencyEdge]
    adjacency_list: Dict[str, List[str]]
    reverse_adjacency: Dict[str, List[str]]
    topological_order: List[str]
    dependency_layers: Dict[int, List[str]]
    conflicts: List[DependencyConflict]

    def get_dependencies(self, task_id: str) -> List[str]:
        """Get direct dependencies of a task."""
        return self.adjacency_list.get(task_id, [])

    def get_dependents(self, task_id: str) -> List[str]:
        """Get direct dependents of a task."""
        return self.reverse_adjacency.get(task_id, [])

    def get_all_dependencies(self, task_id: str) -> Set[str]:
        """Get all transitive dependencies of a task."""
        visited = set()
        stack = [task_id]
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            for dep in self.get_dependencies(current):
                if dep not in visited:
                    stack.append(dep)
        visited.discard(task_id)
        return visited

    def get_all_dependents(self, task_id: str) -> Set[str]:
        """Get all transitive dependents of a task."""
        visited = set()
        stack = [task_id]
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            for dependent in self.get_dependents(current):
                if dependent not in visited:
                    stack.append(dependent)
        visited.discard(task_id)
        return visited

class DependencyMapper:
    """
    Systematic dependency mapper for DAG orchestration.
    
    Creates comprehensive task-level dependency graphs with validation,
    conflict detection, and systematic dependency representation.
    """

    def __init__(self):
        self.conflict_detectors = [self._detect_circular_dependencies, self._detect_missing_dependencies, self._detect_conflicting_statuses, self._detect_resource_conflicts, self._detect_timeline_conflicts]

    def create_dependency_graph(self, tasks: List[TaskNode], dependencies: List[DependencyEdge], specifications: List[SpecificationNode]=None) -> ConstraintGraph:
        """
        Create comprehensive dependency graph with systematic validation.
        
        Args:
            tasks: List of task nodes
            dependencies: List of dependency edges
            specifications: Optional specification nodes for spec-level dependencies
            
        Returns:
            ConstraintGraph: Complete systematic dependency representation
        """
        nodes = {task.task_id: task for task in tasks}
        adjacency_list = defaultdict(list)
        reverse_adjacency = defaultdict(list)
        for edge in dependencies:
            if edge.source_id in nodes and edge.target_id in nodes:
                adjacency_list[edge.target_id].append(edge.source_id)
                reverse_adjacency[edge.source_id].append(edge.target_id)
        if specifications:
            spec_dependencies = self._resolve_spec_dependencies(specifications, tasks)
            dependencies.extend(spec_dependencies)
            for edge in spec_dependencies:
                if edge.source_id in nodes and edge.target_id in nodes:
                    adjacency_list[edge.target_id].append(edge.source_id)
                    reverse_adjacency[edge.source_id].append(edge.target_id)
        topological_order = self._calculate_topological_order(nodes, adjacency_list)
        dependency_layers = self._calculate_dependency_layers(nodes, adjacency_list)
        conflicts = self._detect_all_conflicts(nodes, dependencies, adjacency_list)
        return ConstraintGraph(nodes=nodes, edges=dependencies, adjacency_list=dict(adjacency_list), reverse_adjacency=dict(reverse_adjacency), topological_order=topological_order, dependency_layers=dependency_layers, conflicts=conflicts)

    def validate_dependencies(self, constraint_graph: ConstraintGraph) -> List[DependencyConflict]:
        """
        Validate dependency graph and return conflicts.
        
        Args:
            constraint_graph: Constraint graph to validate
            
        Returns:
            List[DependencyConflict]: All detected conflicts
        """
        return constraint_graph.conflicts

    def resolve_dependency_conflicts(self, constraint_graph: ConstraintGraph, auto_resolve: bool=False) -> ConstraintGraph:
        """
        Resolve dependency conflicts systematically.
        
        Args:
            constraint_graph: Graph with conflicts to resolve
            auto_resolve: Whether to automatically resolve conflicts
            
        Returns:
            ConstraintGraph: Updated graph with resolved conflicts
        """
        if not auto_resolve:
            return self._add_resolution_recommendations(constraint_graph)
        resolved_graph = constraint_graph
        for conflict in constraint_graph.conflicts:
            if conflict.severity in ['low', 'medium']:
                resolved_graph = self._auto_resolve_conflict(resolved_graph, conflict)
        return resolved_graph

    def _resolve_spec_dependencies(self, specifications: List[SpecificationNode], tasks: List[TaskNode]) -> List[DependencyEdge]:
        """Resolve specification-level dependencies to task-level dependencies."""
        spec_dependencies = []
        spec_tasks = defaultdict(list)
        for task in tasks:
            spec_tasks[task.spec_name].append(task)
        for spec in specifications:
            for dep_spec_name in spec.dependencies:
                dep_spec = next((s for s in specifications if s.spec_name == dep_spec_name), None)
                if not dep_spec:
                    continue
                dep_tasks = spec_tasks.get(dep_spec_name, [])
                current_tasks = spec_tasks.get(spec.spec_name, [])
                if dep_tasks and current_tasks:
                    last_dep_task = max(dep_tasks, key=lambda t: t.task_id)
                    first_current_task = min(current_tasks, key=lambda t: t.task_id)
                    spec_dependencies.append(DependencyEdge(source_id=last_dep_task.task_id, target_id=first_current_task.task_id, dependency_type='spec_dependency'))
        return spec_dependencies

    def _calculate_topological_order(self, nodes: Dict[str, TaskNode], adjacency_list: Dict[str, List[str]]) -> List[str]:
        """Calculate topological order using Kahn's algorithm."""
        in_degree = {node_id: 0 for node_id in nodes}
        for node_id in nodes:
            for dep in adjacency_list.get(node_id, []):
                in_degree[node_id] += 1
        queue = deque([node_id for node_id, degree in in_degree.items() if degree == 0])
        topological_order = []
        while queue:
            current = queue.popleft()
            topological_order.append(current)
            for dependent in adjacency_list:
                if current in adjacency_list[dependent]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)
        return topological_order

    def _calculate_dependency_layers(self, nodes: Dict[str, TaskNode], adjacency_list: Dict[str, List[str]]) -> Dict[int, List[str]]:
        """Calculate dependency layers for parallel execution planning."""
        layers = defaultdict(list)
        node_layers = {}

        def calculate_layer(node_id: str, visited: Set[str]) -> int:
            if node_id in visited:
                return 0
            if node_id in node_layers:
                return node_layers[node_id]
            visited.add(node_id)
            dependencies = adjacency_list.get(node_id, [])
            if not dependencies:
                layer = 0
            else:
                max_dep_layer = max((calculate_layer(dep, visited.copy()) for dep in dependencies))
                layer = max_dep_layer + 1
            node_layers[node_id] = layer
            return layer
        for node_id in nodes:
            layer = calculate_layer(node_id, set())
            layers[layer].append(node_id)
        return dict(layers)

    def _detect_all_conflicts(self, nodes: Dict[str, TaskNode], dependencies: List[DependencyEdge], adjacency_list: Dict[str, List[str]]) -> List[DependencyConflict]:
        """Detect all types of dependency conflicts."""
        all_conflicts = []
        for detector in self.conflict_detectors:
            conflicts = detector(nodes, dependencies, adjacency_list)
            all_conflicts.extend(conflicts)
        return all_conflicts

    def _detect_circular_dependencies(self, nodes: Dict[str, TaskNode], dependencies: List[DependencyEdge], adjacency_list: Dict[str, List[str]]) -> List[DependencyConflict]:
        """Detect circular dependencies."""
        conflicts = []
        visited = set()
        rec_stack = set()

        def dfs(node_id: str, path: List[str]) -> None:
            if node_id in rec_stack:
                cycle_start = path.index(node_id)
                cycle = path[cycle_start:] + [node_id]
                conflicts.append(DependencyConflict(conflict_type='circular_dependency', affected_tasks=cycle, description=f"Circular dependency detected: {' -> '.join(cycle)}", severity='critical'))
                return
            if node_id in visited:
                return
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)
            for dep in adjacency_list.get(node_id, []):
                dfs(dep, path.copy())
            rec_stack.remove(node_id)
        for node_id in nodes:
            if node_id not in visited:
                dfs(node_id, [])
        return conflicts

    def _detect_missing_dependencies(self, nodes: Dict[str, TaskNode], dependencies: List[DependencyEdge], adjacency_list: Dict[str, List[str]]) -> List[DependencyConflict]:
        """Detect missing or broken dependencies."""
        conflicts = []
        for edge in dependencies:
            if edge.source_id not in nodes:
                conflicts.append(DependencyConflict(conflict_type='missing_dependency', affected_tasks=[edge.target_id], description=f'Task {edge.target_id} depends on non-existent task {edge.source_id}', severity='high'))
            if edge.target_id not in nodes:
                conflicts.append(DependencyConflict(conflict_type='missing_dependency', affected_tasks=[edge.source_id], description=f'Dependency edge references non-existent target task {edge.target_id}', severity='high'))
        return conflicts

    def _detect_conflicting_statuses(self, nodes: Dict[str, TaskNode], dependencies: List[DependencyEdge], adjacency_list: Dict[str, List[str]]) -> List[DependencyConflict]:
        """Detect conflicting task statuses."""
        conflicts = []
        for node_id, task in nodes.items():
            dependencies_list = adjacency_list.get(node_id, [])
            if task.completion_status == TaskStatus.COMPLETED:
                for dep_id in dependencies_list:
                    dep_task = nodes.get(dep_id)
                    if dep_task and dep_task.completion_status not in [TaskStatus.COMPLETED]:
                        conflicts.append(DependencyConflict(conflict_type='status_conflict', affected_tasks=[node_id, dep_id], description=f'Task {node_id} is completed but dependency {dep_id} is not completed', severity='medium'))
            if task.completion_status == TaskStatus.NOT_STARTED:
                all_deps_completed = True
                for dep_id in dependencies_list:
                    dep_task = nodes.get(dep_id)
                    if dep_task and dep_task.completion_status != TaskStatus.COMPLETED:
                        all_deps_completed = False
                        break
                if dependencies_list and all_deps_completed:
                    conflicts.append(DependencyConflict(conflict_type='status_conflict', affected_tasks=[node_id], description=f'Task {node_id} can be started (all dependencies completed)', severity='low'))
        return conflicts

    def _detect_resource_conflicts(self, nodes: Dict[str, TaskNode], dependencies: List[DependencyEdge], adjacency_list: Dict[str, List[str]]) -> List[DependencyConflict]:
        """Detect potential resource conflicts."""
        conflicts = []
        layers = self._calculate_dependency_layers(nodes, adjacency_list)
        for layer, task_ids in layers.items():
            if len(task_ids) > 1:
                high_effort_tasks = [task_id for task_id in task_ids if nodes[task_id].estimated_effort > 20]
                if len(high_effort_tasks) > 3:
                    conflicts.append(DependencyConflict(conflict_type='resource_conflict', affected_tasks=high_effort_tasks, description=f'Layer {layer} has {len(high_effort_tasks)} high-effort tasks that may cause resource conflicts', severity='medium'))
        return conflicts

    def _detect_timeline_conflicts(self, nodes: Dict[str, TaskNode], dependencies: List[DependencyEdge], adjacency_list: Dict[str, List[str]]) -> List[DependencyConflict]:
        """Detect timeline conflicts and bottlenecks."""
        conflicts = []

        def calculate_critical_path_length(task_id: str, memo: Dict[str, int]) -> int:
            if task_id in memo:
                return memo[task_id]
            task = nodes[task_id]
            dependencies_list = adjacency_list.get(task_id, [])
            if not dependencies_list:
                length = task.estimated_effort
            else:
                max_dep_length = max((calculate_critical_path_length(dep_id, memo) for dep_id in dependencies_list))
                length = max_dep_length + task.estimated_effort
            memo[task_id] = length
            return length
        memo = {}
        critical_path_lengths = {task_id: calculate_critical_path_length(task_id, memo) for task_id in nodes}
        max_length = max(critical_path_lengths.values()) if critical_path_lengths else 0
        long_path_threshold = max_length * 0.8
        long_path_tasks = [task_id for task_id, length in critical_path_lengths.items() if length > long_path_threshold and length > 100]
        if long_path_tasks:
            conflicts.append(DependencyConflict(conflict_type='timeline_conflict', affected_tasks=long_path_tasks, description=f'Tasks with very long critical paths may cause timeline bottlenecks', severity='high'))
        return conflicts

    def _add_resolution_recommendations(self, constraint_graph: ConstraintGraph) -> ConstraintGraph:
        """Add resolution recommendations to conflicts."""
        for conflict in constraint_graph.conflicts:
            if conflict.conflict_type == 'circular_dependency':
                conflict.description += '\nRecommendation: Remove one dependency to break the cycle'
            elif conflict.conflict_type == 'missing_dependency':
                conflict.description += '\nRecommendation: Remove invalid dependency or create missing task'
            elif conflict.conflict_type == 'status_conflict':
                conflict.description += '\nRecommendation: Update task status or verify dependency completion'
            elif conflict.conflict_type == 'resource_conflict':
                conflict.description += '\nRecommendation: Stagger task execution or increase team size'
            elif conflict.conflict_type == 'timeline_conflict':
                conflict.description += '\nRecommendation: Parallelize tasks or reduce scope'
        return constraint_graph

    def _auto_resolve_conflict(self, constraint_graph: ConstraintGraph, conflict: DependencyConflict) -> ConstraintGraph:
        """Automatically resolve a conflict where possible."""
        if conflict.conflict_type == 'status_conflict' and conflict.severity == 'low':
            for task_id in conflict.affected_tasks:
                task = constraint_graph.nodes.get(task_id)
                if task and task.completion_status == TaskStatus.NOT_STARTED:
                    deps = constraint_graph.get_dependencies(task_id)
                    all_completed = all((constraint_graph.nodes[dep_id].completion_status == TaskStatus.COMPLETED for dep_id in deps if dep_id in constraint_graph.nodes))
                    if all_completed:
                        task.completion_status = TaskStatus.NOT_STARTED
        return constraint_graph

def get_dependencies(self, task_id: str) -> List[str]:
    """Get direct dependencies of a task."""
    return self.adjacency_list.get(task_id, [])

def get_dependents(self, task_id: str) -> List[str]:
    """Get direct dependents of a task."""
    return self.reverse_adjacency.get(task_id, [])

def get_all_dependencies(self, task_id: str) -> Set[str]:
    """Get all transitive dependencies of a task."""
    visited = set()
    stack = [task_id]
    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)
        for dep in self.get_dependencies(current):
            if dep not in visited:
                stack.append(dep)
    visited.discard(task_id)
    return visited

def get_all_dependents(self, task_id: str) -> Set[str]:
    """Get all transitive dependents of a task."""
    visited = set()
    stack = [task_id]
    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)
        for dependent in self.get_dependents(current):
            if dependent not in visited:
                stack.append(dependent)
    visited.discard(task_id)
    return visited

def __init__(self):
    self.conflict_detectors = [self._detect_circular_dependencies, self._detect_missing_dependencies, self._detect_conflicting_statuses, self._detect_resource_conflicts, self._detect_timeline_conflicts]

def create_dependency_graph(self, tasks: List[TaskNode], dependencies: List[DependencyEdge], specifications: List[SpecificationNode]=None) -> ConstraintGraph:
    """
        Create comprehensive dependency graph with systematic validation.
        
        Args:
            tasks: List of task nodes
            dependencies: List of dependency edges
            specifications: Optional specification nodes for spec-level dependencies
            
        Returns:
            ConstraintGraph: Complete systematic dependency representation
        """
    nodes = {task.task_id: task for task in tasks}
    adjacency_list = defaultdict(list)
    reverse_adjacency = defaultdict(list)
    for edge in dependencies:
        if edge.source_id in nodes and edge.target_id in nodes:
            adjacency_list[edge.target_id].append(edge.source_id)
            reverse_adjacency[edge.source_id].append(edge.target_id)
    if specifications:
        spec_dependencies = self._resolve_spec_dependencies(specifications, tasks)
        dependencies.extend(spec_dependencies)
        for edge in spec_dependencies:
            if edge.source_id in nodes and edge.target_id in nodes:
                adjacency_list[edge.target_id].append(edge.source_id)
                reverse_adjacency[edge.source_id].append(edge.target_id)
    topological_order = self._calculate_topological_order(nodes, adjacency_list)
    dependency_layers = self._calculate_dependency_layers(nodes, adjacency_list)
    conflicts = self._detect_all_conflicts(nodes, dependencies, adjacency_list)
    return ConstraintGraph(nodes=nodes, edges=dependencies, adjacency_list=dict(adjacency_list), reverse_adjacency=dict(reverse_adjacency), topological_order=topological_order, dependency_layers=dependency_layers, conflicts=conflicts)

def resolve_dependency_conflicts(self, constraint_graph: ConstraintGraph, auto_resolve: bool=False) -> ConstraintGraph:
    """
        Resolve dependency conflicts systematically.
        
        Args:
            constraint_graph: Graph with conflicts to resolve
            auto_resolve: Whether to automatically resolve conflicts
            
        Returns:
            ConstraintGraph: Updated graph with resolved conflicts
        """
    if not auto_resolve:
        return self._add_resolution_recommendations(constraint_graph)
    resolved_graph = constraint_graph
    for conflict in constraint_graph.conflicts:
        if conflict.severity in ['low', 'medium']:
            resolved_graph = self._auto_resolve_conflict(resolved_graph, conflict)
    return resolved_graph

def _resolve_spec_dependencies(self, specifications: List[SpecificationNode], tasks: List[TaskNode]) -> List[DependencyEdge]:
    """Resolve specification-level dependencies to task-level dependencies."""
    spec_dependencies = []
    spec_tasks = defaultdict(list)
    for task in tasks:
        spec_tasks[task.spec_name].append(task)
    for spec in specifications:
        for dep_spec_name in spec.dependencies:
            dep_spec = next((s for s in specifications if s.spec_name == dep_spec_name), None)
            if not dep_spec:
                continue
            dep_tasks = spec_tasks.get(dep_spec_name, [])
            current_tasks = spec_tasks.get(spec.spec_name, [])
            if dep_tasks and current_tasks:
                last_dep_task = max(dep_tasks, key=lambda t: t.task_id)
                first_current_task = min(current_tasks, key=lambda t: t.task_id)
                spec_dependencies.append(DependencyEdge(source_id=last_dep_task.task_id, target_id=first_current_task.task_id, dependency_type='spec_dependency'))
    return spec_dependencies

def _calculate_topological_order(self, nodes: Dict[str, TaskNode], adjacency_list: Dict[str, List[str]]) -> List[str]:
    """Calculate topological order using Kahn's algorithm."""
    in_degree = {node_id: 0 for node_id in nodes}
    for node_id in nodes:
        for dep in adjacency_list.get(node_id, []):
            in_degree[node_id] += 1
    queue = deque([node_id for node_id, degree in in_degree.items() if degree == 0])
    topological_order = []
    while queue:
        current = queue.popleft()
        topological_order.append(current)
        for dependent in adjacency_list:
            if current in adjacency_list[dependent]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
    return topological_order

def _calculate_dependency_layers(self, nodes: Dict[str, TaskNode], adjacency_list: Dict[str, List[str]]) -> Dict[int, List[str]]:
    """Calculate dependency layers for parallel execution planning."""
    layers = defaultdict(list)
    node_layers = {}

    def calculate_layer(node_id: str, visited: Set[str]) -> int:
        if node_id in visited:
            return 0
        if node_id in node_layers:
            return node_layers[node_id]
        visited.add(node_id)
        dependencies = adjacency_list.get(node_id, [])
        if not dependencies:
            layer = 0
        else:
            max_dep_layer = max((calculate_layer(dep, visited.copy()) for dep in dependencies))
            layer = max_dep_layer + 1
        node_layers[node_id] = layer
        return layer
    for node_id in nodes:
        layer = calculate_layer(node_id, set())
        layers[layer].append(node_id)
    return dict(layers)

def _detect_all_conflicts(self, nodes: Dict[str, TaskNode], dependencies: List[DependencyEdge], adjacency_list: Dict[str, List[str]]) -> List[DependencyConflict]:
    """Detect all types of dependency conflicts."""
    all_conflicts = []
    for detector in self.conflict_detectors:
        conflicts = detector(nodes, dependencies, adjacency_list)
        all_conflicts.extend(conflicts)
    return all_conflicts

def _detect_circular_dependencies(self, nodes: Dict[str, TaskNode], dependencies: List[DependencyEdge], adjacency_list: Dict[str, List[str]]) -> List[DependencyConflict]:
    """Detect circular dependencies."""
    conflicts = []
    visited = set()
    rec_stack = set()

    def dfs(node_id: str, path: List[str]) -> None:
        if node_id in rec_stack:
            cycle_start = path.index(node_id)
            cycle = path[cycle_start:] + [node_id]
            conflicts.append(DependencyConflict(conflict_type='circular_dependency', affected_tasks=cycle, description=f"Circular dependency detected: {' -> '.join(cycle)}", severity='critical'))
            return
        if node_id in visited:
            return
        visited.add(node_id)
        rec_stack.add(node_id)
        path.append(node_id)
        for dep in adjacency_list.get(node_id, []):
            dfs(dep, path.copy())
        rec_stack.remove(node_id)
    for node_id in nodes:
        if node_id not in visited:
            dfs(node_id, [])
    return conflicts

def _detect_missing_dependencies(self, nodes: Dict[str, TaskNode], dependencies: List[DependencyEdge], adjacency_list: Dict[str, List[str]]) -> List[DependencyConflict]:
    """Detect missing or broken dependencies."""
    conflicts = []
    for edge in dependencies:
        if edge.source_id not in nodes:
            conflicts.append(DependencyConflict(conflict_type='missing_dependency', affected_tasks=[edge.target_id], description=f'Task {edge.target_id} depends on non-existent task {edge.source_id}', severity='high'))
        if edge.target_id not in nodes:
            conflicts.append(DependencyConflict(conflict_type='missing_dependency', affected_tasks=[edge.source_id], description=f'Dependency edge references non-existent target task {edge.target_id}', severity='high'))
    return conflicts

def _detect_conflicting_statuses(self, nodes: Dict[str, TaskNode], dependencies: List[DependencyEdge], adjacency_list: Dict[str, List[str]]) -> List[DependencyConflict]:
    """Detect conflicting task statuses."""
    conflicts = []
    for node_id, task in nodes.items():
        dependencies_list = adjacency_list.get(node_id, [])
        if task.completion_status == TaskStatus.COMPLETED:
            for dep_id in dependencies_list:
                dep_task = nodes.get(dep_id)
                if dep_task and dep_task.completion_status not in [TaskStatus.COMPLETED]:
                    conflicts.append(DependencyConflict(conflict_type='status_conflict', affected_tasks=[node_id, dep_id], description=f'Task {node_id} is completed but dependency {dep_id} is not completed', severity='medium'))
        if task.completion_status == TaskStatus.NOT_STARTED:
            all_deps_completed = True
            for dep_id in dependencies_list:
                dep_task = nodes.get(dep_id)
                if dep_task and dep_task.completion_status != TaskStatus.COMPLETED:
                    all_deps_completed = False
                    break
            if dependencies_list and all_deps_completed:
                conflicts.append(DependencyConflict(conflict_type='status_conflict', affected_tasks=[node_id], description=f'Task {node_id} can be started (all dependencies completed)', severity='low'))
    return conflicts

def _detect_resource_conflicts(self, nodes: Dict[str, TaskNode], dependencies: List[DependencyEdge], adjacency_list: Dict[str, List[str]]) -> List[DependencyConflict]:
    """Detect potential resource conflicts."""
    conflicts = []
    layers = self._calculate_dependency_layers(nodes, adjacency_list)
    for layer, task_ids in layers.items():
        if len(task_ids) > 1:
            high_effort_tasks = [task_id for task_id in task_ids if nodes[task_id].estimated_effort > 20]
            if len(high_effort_tasks) > 3:
                conflicts.append(DependencyConflict(conflict_type='resource_conflict', affected_tasks=high_effort_tasks, description=f'Layer {layer} has {len(high_effort_tasks)} high-effort tasks that may cause resource conflicts', severity='medium'))
    return conflicts

def _detect_timeline_conflicts(self, nodes: Dict[str, TaskNode], dependencies: List[DependencyEdge], adjacency_list: Dict[str, List[str]]) -> List[DependencyConflict]:
    """Detect timeline conflicts and bottlenecks."""
    conflicts = []

    def calculate_critical_path_length(task_id: str, memo: Dict[str, int]) -> int:
        if task_id in memo:
            return memo[task_id]
        task = nodes[task_id]
        dependencies_list = adjacency_list.get(task_id, [])
        if not dependencies_list:
            length = task.estimated_effort
        else:
            max_dep_length = max((calculate_critical_path_length(dep_id, memo) for dep_id in dependencies_list))
            length = max_dep_length + task.estimated_effort
        memo[task_id] = length
        return length
    memo = {}
    critical_path_lengths = {task_id: calculate_critical_path_length(task_id, memo) for task_id in nodes}
    max_length = max(critical_path_lengths.values()) if critical_path_lengths else 0
    long_path_threshold = max_length * 0.8
    long_path_tasks = [task_id for task_id, length in critical_path_lengths.items() if length > long_path_threshold and length > 100]
    if long_path_tasks:
        conflicts.append(DependencyConflict(conflict_type='timeline_conflict', affected_tasks=long_path_tasks, description=f'Tasks with very long critical paths may cause timeline bottlenecks', severity='high'))
    return conflicts

def _add_resolution_recommendations(self, constraint_graph: ConstraintGraph) -> ConstraintGraph:
    """Add resolution recommendations to conflicts."""
    for conflict in constraint_graph.conflicts:
        if conflict.conflict_type == 'circular_dependency':
            conflict.description += '\nRecommendation: Remove one dependency to break the cycle'
        elif conflict.conflict_type == 'missing_dependency':
            conflict.description += '\nRecommendation: Remove invalid dependency or create missing task'
        elif conflict.conflict_type == 'status_conflict':
            conflict.description += '\nRecommendation: Update task status or verify dependency completion'
        elif conflict.conflict_type == 'resource_conflict':
            conflict.description += '\nRecommendation: Stagger task execution or increase team size'
        elif conflict.conflict_type == 'timeline_conflict':
            conflict.description += '\nRecommendation: Parallelize tasks or reduce scope'
    return constraint_graph

def _auto_resolve_conflict(self, constraint_graph: ConstraintGraph, conflict: DependencyConflict) -> ConstraintGraph:
    """Automatically resolve a conflict where possible."""
    if conflict.conflict_type == 'status_conflict' and conflict.severity == 'low':
        for task_id in conflict.affected_tasks:
            task = constraint_graph.nodes.get(task_id)
            if task and task.completion_status == TaskStatus.NOT_STARTED:
                deps = constraint_graph.get_dependencies(task_id)
                all_completed = all((constraint_graph.nodes[dep_id].completion_status == TaskStatus.COMPLETED for dep_id in deps if dep_id in constraint_graph.nodes))
                if all_completed:
                    task.completion_status = TaskStatus.NOT_STARTED
    return constraint_graph

def calculate_layer(node_id: str, visited: Set[str]) -> int:
    if node_id in visited:
        return 0
    if node_id in node_layers:
        return node_layers[node_id]
    visited.add(node_id)
    dependencies = adjacency_list.get(node_id, [])
    if not dependencies:
        layer = 0
    else:
        max_dep_layer = max((calculate_layer(dep, visited.copy()) for dep in dependencies))
        layer = max_dep_layer + 1
    node_layers[node_id] = layer
    return layer

def dfs(node_id: str, path: List[str]) -> None:
    if node_id in rec_stack:
        cycle_start = path.index(node_id)
        cycle = path[cycle_start:] + [node_id]
        conflicts.append(DependencyConflict(conflict_type='circular_dependency', affected_tasks=cycle, description=f"Circular dependency detected: {' -> '.join(cycle)}", severity='critical'))
        return
    if node_id in visited:
        return
    visited.add(node_id)
    rec_stack.add(node_id)
    path.append(node_id)
    for dep in adjacency_list.get(node_id, []):
        dfs(dep, path.copy())
    rec_stack.remove(node_id)

def calculate_critical_path_length(task_id: str, memo: Dict[str, int]) -> int:
    if task_id in memo:
        return memo[task_id]
    task = nodes[task_id]
    dependencies_list = adjacency_list.get(task_id, [])
    if not dependencies_list:
        length = task.estimated_effort
    else:
        max_dep_length = max((calculate_critical_path_length(dep_id, memo) for dep_id in dependencies_list))
        length = max_dep_length + task.estimated_effort
    memo[task_id] = length
    return length

def get_dependencies(self, task_id: str) -> List[str]:
    """Get direct dependencies of a task."""
    return self.adjacency_list.get(task_id, [])

def get_dependents(self, task_id: str) -> List[str]:
    """Get direct dependents of a task."""
    return self.reverse_adjacency.get(task_id, [])

def get_all_dependencies(self, task_id: str) -> Set[str]:
    """Get all transitive dependencies of a task."""
    visited = set()
    stack = [task_id]
    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)
        for dep in self.get_dependencies(current):
            if dep not in visited:
                stack.append(dep)
    visited.discard(task_id)
    return visited

def get_all_dependents(self, task_id: str) -> Set[str]:
    """Get all transitive dependents of a task."""
    visited = set()
    stack = [task_id]
    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)
        for dependent in self.get_dependents(current):
            if dependent not in visited:
                stack.append(dependent)
    visited.discard(task_id)
    return visited

def __init__(self):
    self.conflict_detectors = [self._detect_circular_dependencies, self._detect_missing_dependencies, self._detect_conflicting_statuses, self._detect_resource_conflicts, self._detect_timeline_conflicts]

def create_dependency_graph(self, tasks: List[TaskNode], dependencies: List[DependencyEdge], specifications: List[SpecificationNode]=None) -> ConstraintGraph:
    """
        Create comprehensive dependency graph with systematic validation.
        
        Args:
            tasks: List of task nodes
            dependencies: List of dependency edges
            specifications: Optional specification nodes for spec-level dependencies
            
        Returns:
            ConstraintGraph: Complete systematic dependency representation
        """
    nodes = {task.task_id: task for task in tasks}
    adjacency_list = defaultdict(list)
    reverse_adjacency = defaultdict(list)
    for edge in dependencies:
        if edge.source_id in nodes and edge.target_id in nodes:
            adjacency_list[edge.target_id].append(edge.source_id)
            reverse_adjacency[edge.source_id].append(edge.target_id)
    if specifications:
        spec_dependencies = self._resolve_spec_dependencies(specifications, tasks)
        dependencies.extend(spec_dependencies)
        for edge in spec_dependencies:
            if edge.source_id in nodes and edge.target_id in nodes:
                adjacency_list[edge.target_id].append(edge.source_id)
                reverse_adjacency[edge.source_id].append(edge.target_id)
    topological_order = self._calculate_topological_order(nodes, adjacency_list)
    dependency_layers = self._calculate_dependency_layers(nodes, adjacency_list)
    conflicts = self._detect_all_conflicts(nodes, dependencies, adjacency_list)
    return ConstraintGraph(nodes=nodes, edges=dependencies, adjacency_list=dict(adjacency_list), reverse_adjacency=dict(reverse_adjacency), topological_order=topological_order, dependency_layers=dependency_layers, conflicts=conflicts)

def resolve_dependency_conflicts(self, constraint_graph: ConstraintGraph, auto_resolve: bool=False) -> ConstraintGraph:
    """
        Resolve dependency conflicts systematically.
        
        Args:
            constraint_graph: Graph with conflicts to resolve
            auto_resolve: Whether to automatically resolve conflicts
            
        Returns:
            ConstraintGraph: Updated graph with resolved conflicts
        """
    if not auto_resolve:
        return self._add_resolution_recommendations(constraint_graph)
    resolved_graph = constraint_graph
    for conflict in constraint_graph.conflicts:
        if conflict.severity in ['low', 'medium']:
            resolved_graph = self._auto_resolve_conflict(resolved_graph, conflict)
    return resolved_graph

def _resolve_spec_dependencies(self, specifications: List[SpecificationNode], tasks: List[TaskNode]) -> List[DependencyEdge]:
    """Resolve specification-level dependencies to task-level dependencies."""
    spec_dependencies = []
    spec_tasks = defaultdict(list)
    for task in tasks:
        spec_tasks[task.spec_name].append(task)
    for spec in specifications:
        for dep_spec_name in spec.dependencies:
            dep_spec = next((s for s in specifications if s.spec_name == dep_spec_name), None)
            if not dep_spec:
                continue
            dep_tasks = spec_tasks.get(dep_spec_name, [])
            current_tasks = spec_tasks.get(spec.spec_name, [])
            if dep_tasks and current_tasks:
                last_dep_task = max(dep_tasks, key=lambda t: t.task_id)
                first_current_task = min(current_tasks, key=lambda t: t.task_id)
                spec_dependencies.append(DependencyEdge(source_id=last_dep_task.task_id, target_id=first_current_task.task_id, dependency_type='spec_dependency'))
    return spec_dependencies

def _calculate_topological_order(self, nodes: Dict[str, TaskNode], adjacency_list: Dict[str, List[str]]) -> List[str]:
    """Calculate topological order using Kahn's algorithm."""
    in_degree = {node_id: 0 for node_id in nodes}
    for node_id in nodes:
        for dep in adjacency_list.get(node_id, []):
            in_degree[node_id] += 1
    queue = deque([node_id for node_id, degree in in_degree.items() if degree == 0])
    topological_order = []
    while queue:
        current = queue.popleft()
        topological_order.append(current)
        for dependent in adjacency_list:
            if current in adjacency_list[dependent]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
    return topological_order

def _calculate_dependency_layers(self, nodes: Dict[str, TaskNode], adjacency_list: Dict[str, List[str]]) -> Dict[int, List[str]]:
    """Calculate dependency layers for parallel execution planning."""
    layers = defaultdict(list)
    node_layers = {}

    def calculate_layer(node_id: str, visited: Set[str]) -> int:
        if node_id in visited:
            return 0
        if node_id in node_layers:
            return node_layers[node_id]
        visited.add(node_id)
        dependencies = adjacency_list.get(node_id, [])
        if not dependencies:
            layer = 0
        else:
            max_dep_layer = max((calculate_layer(dep, visited.copy()) for dep in dependencies))
            layer = max_dep_layer + 1
        node_layers[node_id] = layer
        return layer
    for node_id in nodes:
        layer = calculate_layer(node_id, set())
        layers[layer].append(node_id)
    return dict(layers)

def _detect_all_conflicts(self, nodes: Dict[str, TaskNode], dependencies: List[DependencyEdge], adjacency_list: Dict[str, List[str]]) -> List[DependencyConflict]:
    """Detect all types of dependency conflicts."""
    all_conflicts = []
    for detector in self.conflict_detectors:
        conflicts = detector(nodes, dependencies, adjacency_list)
        all_conflicts.extend(conflicts)
    return all_conflicts

def _detect_circular_dependencies(self, nodes: Dict[str, TaskNode], dependencies: List[DependencyEdge], adjacency_list: Dict[str, List[str]]) -> List[DependencyConflict]:
    """Detect circular dependencies."""
    conflicts = []
    visited = set()
    rec_stack = set()

    def dfs(node_id: str, path: List[str]) -> None:
        if node_id in rec_stack:
            cycle_start = path.index(node_id)
            cycle = path[cycle_start:] + [node_id]
            conflicts.append(DependencyConflict(conflict_type='circular_dependency', affected_tasks=cycle, description=f"Circular dependency detected: {' -> '.join(cycle)}", severity='critical'))
            return
        if node_id in visited:
            return
        visited.add(node_id)
        rec_stack.add(node_id)
        path.append(node_id)
        for dep in adjacency_list.get(node_id, []):
            dfs(dep, path.copy())
        rec_stack.remove(node_id)
    for node_id in nodes:
        if node_id not in visited:
            dfs(node_id, [])
    return conflicts

def _detect_missing_dependencies(self, nodes: Dict[str, TaskNode], dependencies: List[DependencyEdge], adjacency_list: Dict[str, List[str]]) -> List[DependencyConflict]:
    """Detect missing or broken dependencies."""
    conflicts = []
    for edge in dependencies:
        if edge.source_id not in nodes:
            conflicts.append(DependencyConflict(conflict_type='missing_dependency', affected_tasks=[edge.target_id], description=f'Task {edge.target_id} depends on non-existent task {edge.source_id}', severity='high'))
        if edge.target_id not in nodes:
            conflicts.append(DependencyConflict(conflict_type='missing_dependency', affected_tasks=[edge.source_id], description=f'Dependency edge references non-existent target task {edge.target_id}', severity='high'))
    return conflicts

def _detect_conflicting_statuses(self, nodes: Dict[str, TaskNode], dependencies: List[DependencyEdge], adjacency_list: Dict[str, List[str]]) -> List[DependencyConflict]:
    """Detect conflicting task statuses."""
    conflicts = []
    for node_id, task in nodes.items():
        dependencies_list = adjacency_list.get(node_id, [])
        if task.completion_status == TaskStatus.COMPLETED:
            for dep_id in dependencies_list:
                dep_task = nodes.get(dep_id)
                if dep_task and dep_task.completion_status not in [TaskStatus.COMPLETED]:
                    conflicts.append(DependencyConflict(conflict_type='status_conflict', affected_tasks=[node_id, dep_id], description=f'Task {node_id} is completed but dependency {dep_id} is not completed', severity='medium'))
        if task.completion_status == TaskStatus.NOT_STARTED:
            all_deps_completed = True
            for dep_id in dependencies_list:
                dep_task = nodes.get(dep_id)
                if dep_task and dep_task.completion_status != TaskStatus.COMPLETED:
                    all_deps_completed = False
                    break
            if dependencies_list and all_deps_completed:
                conflicts.append(DependencyConflict(conflict_type='status_conflict', affected_tasks=[node_id], description=f'Task {node_id} can be started (all dependencies completed)', severity='low'))
    return conflicts

def _detect_resource_conflicts(self, nodes: Dict[str, TaskNode], dependencies: List[DependencyEdge], adjacency_list: Dict[str, List[str]]) -> List[DependencyConflict]:
    """Detect potential resource conflicts."""
    conflicts = []
    layers = self._calculate_dependency_layers(nodes, adjacency_list)
    for layer, task_ids in layers.items():
        if len(task_ids) > 1:
            high_effort_tasks = [task_id for task_id in task_ids if nodes[task_id].estimated_effort > 20]
            if len(high_effort_tasks) > 3:
                conflicts.append(DependencyConflict(conflict_type='resource_conflict', affected_tasks=high_effort_tasks, description=f'Layer {layer} has {len(high_effort_tasks)} high-effort tasks that may cause resource conflicts', severity='medium'))
    return conflicts

def _detect_timeline_conflicts(self, nodes: Dict[str, TaskNode], dependencies: List[DependencyEdge], adjacency_list: Dict[str, List[str]]) -> List[DependencyConflict]:
    """Detect timeline conflicts and bottlenecks."""
    conflicts = []

    def calculate_critical_path_length(task_id: str, memo: Dict[str, int]) -> int:
        if task_id in memo:
            return memo[task_id]
        task = nodes[task_id]
        dependencies_list = adjacency_list.get(task_id, [])
        if not dependencies_list:
            length = task.estimated_effort
        else:
            max_dep_length = max((calculate_critical_path_length(dep_id, memo) for dep_id in dependencies_list))
            length = max_dep_length + task.estimated_effort
        memo[task_id] = length
        return length
    memo = {}
    critical_path_lengths = {task_id: calculate_critical_path_length(task_id, memo) for task_id in nodes}
    max_length = max(critical_path_lengths.values()) if critical_path_lengths else 0
    long_path_threshold = max_length * 0.8
    long_path_tasks = [task_id for task_id, length in critical_path_lengths.items() if length > long_path_threshold and length > 100]
    if long_path_tasks:
        conflicts.append(DependencyConflict(conflict_type='timeline_conflict', affected_tasks=long_path_tasks, description=f'Tasks with very long critical paths may cause timeline bottlenecks', severity='high'))
    return conflicts

def _add_resolution_recommendations(self, constraint_graph: ConstraintGraph) -> ConstraintGraph:
    """Add resolution recommendations to conflicts."""
    for conflict in constraint_graph.conflicts:
        if conflict.conflict_type == 'circular_dependency':
            conflict.description += '\nRecommendation: Remove one dependency to break the cycle'
        elif conflict.conflict_type == 'missing_dependency':
            conflict.description += '\nRecommendation: Remove invalid dependency or create missing task'
        elif conflict.conflict_type == 'status_conflict':
            conflict.description += '\nRecommendation: Update task status or verify dependency completion'
        elif conflict.conflict_type == 'resource_conflict':
            conflict.description += '\nRecommendation: Stagger task execution or increase team size'
        elif conflict.conflict_type == 'timeline_conflict':
            conflict.description += '\nRecommendation: Parallelize tasks or reduce scope'
    return constraint_graph

def _auto_resolve_conflict(self, constraint_graph: ConstraintGraph, conflict: DependencyConflict) -> ConstraintGraph:
    """Automatically resolve a conflict where possible."""
    if conflict.conflict_type == 'status_conflict' and conflict.severity == 'low':
        for task_id in conflict.affected_tasks:
            task = constraint_graph.nodes.get(task_id)
            if task and task.completion_status == TaskStatus.NOT_STARTED:
                deps = constraint_graph.get_dependencies(task_id)
                all_completed = all((constraint_graph.nodes[dep_id].completion_status == TaskStatus.COMPLETED for dep_id in deps if dep_id in constraint_graph.nodes))
                if all_completed:
                    task.completion_status = TaskStatus.NOT_STARTED
    return constraint_graph

def calculate_layer(node_id: str, visited: Set[str]) -> int:
    if node_id in visited:
        return 0
    if node_id in node_layers:
        return node_layers[node_id]
    visited.add(node_id)
    dependencies = adjacency_list.get(node_id, [])
    if not dependencies:
        layer = 0
    else:
        max_dep_layer = max((calculate_layer(dep, visited.copy()) for dep in dependencies))
        layer = max_dep_layer + 1
    node_layers[node_id] = layer
    return layer

def dfs(node_id: str, path: List[str]) -> None:
    if node_id in rec_stack:
        cycle_start = path.index(node_id)
        cycle = path[cycle_start:] + [node_id]
        conflicts.append(DependencyConflict(conflict_type='circular_dependency', affected_tasks=cycle, description=f"Circular dependency detected: {' -> '.join(cycle)}", severity='critical'))
        return
    if node_id in visited:
        return
    visited.add(node_id)
    rec_stack.add(node_id)
    path.append(node_id)
    for dep in adjacency_list.get(node_id, []):
        dfs(dep, path.copy())
    rec_stack.remove(node_id)

def calculate_critical_path_length(task_id: str, memo: Dict[str, int]) -> int:
    if task_id in memo:
        return memo[task_id]
    task = nodes[task_id]
    dependencies_list = adjacency_list.get(task_id, [])
    if not dependencies_list:
        length = task.estimated_effort
    else:
        max_dep_length = max((calculate_critical_path_length(dep_id, memo) for dep_id in dependencies_list))
        length = max_dep_length + task.estimated_effort
    memo[task_id] = length
    return length

def calculate_layer(node_id: str, visited: Set[str]) -> int:
    if node_id in visited:
        return 0
    if node_id in node_layers:
        return node_layers[node_id]
    visited.add(node_id)
    dependencies = adjacency_list.get(node_id, [])
    if not dependencies:
        layer = 0
    else:
        max_dep_layer = max((calculate_layer(dep, visited.copy()) for dep in dependencies))
        layer = max_dep_layer + 1
    node_layers[node_id] = layer
    return layer

def dfs(node_id: str, path: List[str]) -> None:
    if node_id in rec_stack:
        cycle_start = path.index(node_id)
        cycle = path[cycle_start:] + [node_id]
        conflicts.append(DependencyConflict(conflict_type='circular_dependency', affected_tasks=cycle, description=f"Circular dependency detected: {' -> '.join(cycle)}", severity='critical'))
        return
    if node_id in visited:
        return
    visited.add(node_id)
    rec_stack.add(node_id)
    path.append(node_id)
    for dep in adjacency_list.get(node_id, []):
        dfs(dep, path.copy())
    rec_stack.remove(node_id)

def calculate_critical_path_length(task_id: str, memo: Dict[str, int]) -> int:
    if task_id in memo:
        return memo[task_id]
    task = nodes[task_id]
    dependencies_list = adjacency_list.get(task_id, [])
    if not dependencies_list:
        length = task.estimated_effort
    else:
        max_dep_length = max((calculate_critical_path_length(dep_id, memo) for dep_id in dependencies_list))
        length = max_dep_length + task.estimated_effort
    memo[task_id] = length
    return length

def get_dependencies(self, task_id: str) -> List[str]:
    """Get direct dependencies of a task."""
    return self.adjacency_list.get(task_id, [])

def get_dependents(self, task_id: str) -> List[str]:
    """Get direct dependents of a task."""
    return self.reverse_adjacency.get(task_id, [])

def get_all_dependencies(self, task_id: str) -> Set[str]:
    """Get all transitive dependencies of a task."""
    visited = set()
    stack = [task_id]
    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)
        for dep in self.get_dependencies(current):
            if dep not in visited:
                stack.append(dep)
    visited.discard(task_id)
    return visited

def get_all_dependents(self, task_id: str) -> Set[str]:
    """Get all transitive dependents of a task."""
    visited = set()
    stack = [task_id]
    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)
        for dependent in self.get_dependents(current):
            if dependent not in visited:
                stack.append(dependent)
    visited.discard(task_id)
    return visited

def __init__(self):
    self.conflict_detectors = [self._detect_circular_dependencies, self._detect_missing_dependencies, self._detect_conflicting_statuses, self._detect_resource_conflicts, self._detect_timeline_conflicts]

def create_dependency_graph(self, tasks: List[TaskNode], dependencies: List[DependencyEdge], specifications: List[SpecificationNode]=None) -> ConstraintGraph:
    """
        Create comprehensive dependency graph with systematic validation.
        
        Args:
            tasks: List of task nodes
            dependencies: List of dependency edges
            specifications: Optional specification nodes for spec-level dependencies
            
        Returns:
            ConstraintGraph: Complete systematic dependency representation
        """
    nodes = {task.task_id: task for task in tasks}
    adjacency_list = defaultdict(list)
    reverse_adjacency = defaultdict(list)
    for edge in dependencies:
        if edge.source_id in nodes and edge.target_id in nodes:
            adjacency_list[edge.target_id].append(edge.source_id)
            reverse_adjacency[edge.source_id].append(edge.target_id)
    if specifications:
        spec_dependencies = self._resolve_spec_dependencies(specifications, tasks)
        dependencies.extend(spec_dependencies)
        for edge in spec_dependencies:
            if edge.source_id in nodes and edge.target_id in nodes:
                adjacency_list[edge.target_id].append(edge.source_id)
                reverse_adjacency[edge.source_id].append(edge.target_id)
    topological_order = self._calculate_topological_order(nodes, adjacency_list)
    dependency_layers = self._calculate_dependency_layers(nodes, adjacency_list)
    conflicts = self._detect_all_conflicts(nodes, dependencies, adjacency_list)
    return ConstraintGraph(nodes=nodes, edges=dependencies, adjacency_list=dict(adjacency_list), reverse_adjacency=dict(reverse_adjacency), topological_order=topological_order, dependency_layers=dependency_layers, conflicts=conflicts)

def resolve_dependency_conflicts(self, constraint_graph: ConstraintGraph, auto_resolve: bool=False) -> ConstraintGraph:
    """
        Resolve dependency conflicts systematically.
        
        Args:
            constraint_graph: Graph with conflicts to resolve
            auto_resolve: Whether to automatically resolve conflicts
            
        Returns:
            ConstraintGraph: Updated graph with resolved conflicts
        """
    if not auto_resolve:
        return self._add_resolution_recommendations(constraint_graph)
    resolved_graph = constraint_graph
    for conflict in constraint_graph.conflicts:
        if conflict.severity in ['low', 'medium']:
            resolved_graph = self._auto_resolve_conflict(resolved_graph, conflict)
    return resolved_graph

def _resolve_spec_dependencies(self, specifications: List[SpecificationNode], tasks: List[TaskNode]) -> List[DependencyEdge]:
    """Resolve specification-level dependencies to task-level dependencies."""
    spec_dependencies = []
    spec_tasks = defaultdict(list)
    for task in tasks:
        spec_tasks[task.spec_name].append(task)
    for spec in specifications:
        for dep_spec_name in spec.dependencies:
            dep_spec = next((s for s in specifications if s.spec_name == dep_spec_name), None)
            if not dep_spec:
                continue
            dep_tasks = spec_tasks.get(dep_spec_name, [])
            current_tasks = spec_tasks.get(spec.spec_name, [])
            if dep_tasks and current_tasks:
                last_dep_task = max(dep_tasks, key=lambda t: t.task_id)
                first_current_task = min(current_tasks, key=lambda t: t.task_id)
                spec_dependencies.append(DependencyEdge(source_id=last_dep_task.task_id, target_id=first_current_task.task_id, dependency_type='spec_dependency'))
    return spec_dependencies

def _calculate_topological_order(self, nodes: Dict[str, TaskNode], adjacency_list: Dict[str, List[str]]) -> List[str]:
    """Calculate topological order using Kahn's algorithm."""
    in_degree = {node_id: 0 for node_id in nodes}
    for node_id in nodes:
        for dep in adjacency_list.get(node_id, []):
            in_degree[node_id] += 1
    queue = deque([node_id for node_id, degree in in_degree.items() if degree == 0])
    topological_order = []
    while queue:
        current = queue.popleft()
        topological_order.append(current)
        for dependent in adjacency_list:
            if current in adjacency_list[dependent]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
    return topological_order

def _calculate_dependency_layers(self, nodes: Dict[str, TaskNode], adjacency_list: Dict[str, List[str]]) -> Dict[int, List[str]]:
    """Calculate dependency layers for parallel execution planning."""
    layers = defaultdict(list)
    node_layers = {}

    def calculate_layer(node_id: str, visited: Set[str]) -> int:
        if node_id in visited:
            return 0
        if node_id in node_layers:
            return node_layers[node_id]
        visited.add(node_id)
        dependencies = adjacency_list.get(node_id, [])
        if not dependencies:
            layer = 0
        else:
            max_dep_layer = max((calculate_layer(dep, visited.copy()) for dep in dependencies))
            layer = max_dep_layer + 1
        node_layers[node_id] = layer
        return layer
    for node_id in nodes:
        layer = calculate_layer(node_id, set())
        layers[layer].append(node_id)
    return dict(layers)

def _detect_all_conflicts(self, nodes: Dict[str, TaskNode], dependencies: List[DependencyEdge], adjacency_list: Dict[str, List[str]]) -> List[DependencyConflict]:
    """Detect all types of dependency conflicts."""
    all_conflicts = []
    for detector in self.conflict_detectors:
        conflicts = detector(nodes, dependencies, adjacency_list)
        all_conflicts.extend(conflicts)
    return all_conflicts

def _detect_circular_dependencies(self, nodes: Dict[str, TaskNode], dependencies: List[DependencyEdge], adjacency_list: Dict[str, List[str]]) -> List[DependencyConflict]:
    """Detect circular dependencies."""
    conflicts = []
    visited = set()
    rec_stack = set()

    def dfs(node_id: str, path: List[str]) -> None:
        if node_id in rec_stack:
            cycle_start = path.index(node_id)
            cycle = path[cycle_start:] + [node_id]
            conflicts.append(DependencyConflict(conflict_type='circular_dependency', affected_tasks=cycle, description=f"Circular dependency detected: {' -> '.join(cycle)}", severity='critical'))
            return
        if node_id in visited:
            return
        visited.add(node_id)
        rec_stack.add(node_id)
        path.append(node_id)
        for dep in adjacency_list.get(node_id, []):
            dfs(dep, path.copy())
        rec_stack.remove(node_id)
    for node_id in nodes:
        if node_id not in visited:
            dfs(node_id, [])
    return conflicts

def _detect_missing_dependencies(self, nodes: Dict[str, TaskNode], dependencies: List[DependencyEdge], adjacency_list: Dict[str, List[str]]) -> List[DependencyConflict]:
    """Detect missing or broken dependencies."""
    conflicts = []
    for edge in dependencies:
        if edge.source_id not in nodes:
            conflicts.append(DependencyConflict(conflict_type='missing_dependency', affected_tasks=[edge.target_id], description=f'Task {edge.target_id} depends on non-existent task {edge.source_id}', severity='high'))
        if edge.target_id not in nodes:
            conflicts.append(DependencyConflict(conflict_type='missing_dependency', affected_tasks=[edge.source_id], description=f'Dependency edge references non-existent target task {edge.target_id}', severity='high'))
    return conflicts

def _detect_conflicting_statuses(self, nodes: Dict[str, TaskNode], dependencies: List[DependencyEdge], adjacency_list: Dict[str, List[str]]) -> List[DependencyConflict]:
    """Detect conflicting task statuses."""
    conflicts = []
    for node_id, task in nodes.items():
        dependencies_list = adjacency_list.get(node_id, [])
        if task.completion_status == TaskStatus.COMPLETED:
            for dep_id in dependencies_list:
                dep_task = nodes.get(dep_id)
                if dep_task and dep_task.completion_status not in [TaskStatus.COMPLETED]:
                    conflicts.append(DependencyConflict(conflict_type='status_conflict', affected_tasks=[node_id, dep_id], description=f'Task {node_id} is completed but dependency {dep_id} is not completed', severity='medium'))
        if task.completion_status == TaskStatus.NOT_STARTED:
            all_deps_completed = True
            for dep_id in dependencies_list:
                dep_task = nodes.get(dep_id)
                if dep_task and dep_task.completion_status != TaskStatus.COMPLETED:
                    all_deps_completed = False
                    break
            if dependencies_list and all_deps_completed:
                conflicts.append(DependencyConflict(conflict_type='status_conflict', affected_tasks=[node_id], description=f'Task {node_id} can be started (all dependencies completed)', severity='low'))
    return conflicts

def _detect_resource_conflicts(self, nodes: Dict[str, TaskNode], dependencies: List[DependencyEdge], adjacency_list: Dict[str, List[str]]) -> List[DependencyConflict]:
    """Detect potential resource conflicts."""
    conflicts = []
    layers = self._calculate_dependency_layers(nodes, adjacency_list)
    for layer, task_ids in layers.items():
        if len(task_ids) > 1:
            high_effort_tasks = [task_id for task_id in task_ids if nodes[task_id].estimated_effort > 20]
            if len(high_effort_tasks) > 3:
                conflicts.append(DependencyConflict(conflict_type='resource_conflict', affected_tasks=high_effort_tasks, description=f'Layer {layer} has {len(high_effort_tasks)} high-effort tasks that may cause resource conflicts', severity='medium'))
    return conflicts

def _detect_timeline_conflicts(self, nodes: Dict[str, TaskNode], dependencies: List[DependencyEdge], adjacency_list: Dict[str, List[str]]) -> List[DependencyConflict]:
    """Detect timeline conflicts and bottlenecks."""
    conflicts = []

    def calculate_critical_path_length(task_id: str, memo: Dict[str, int]) -> int:
        if task_id in memo:
            return memo[task_id]
        task = nodes[task_id]
        dependencies_list = adjacency_list.get(task_id, [])
        if not dependencies_list:
            length = task.estimated_effort
        else:
            max_dep_length = max((calculate_critical_path_length(dep_id, memo) for dep_id in dependencies_list))
            length = max_dep_length + task.estimated_effort
        memo[task_id] = length
        return length
    memo = {}
    critical_path_lengths = {task_id: calculate_critical_path_length(task_id, memo) for task_id in nodes}
    max_length = max(critical_path_lengths.values()) if critical_path_lengths else 0
    long_path_threshold = max_length * 0.8
    long_path_tasks = [task_id for task_id, length in critical_path_lengths.items() if length > long_path_threshold and length > 100]
    if long_path_tasks:
        conflicts.append(DependencyConflict(conflict_type='timeline_conflict', affected_tasks=long_path_tasks, description=f'Tasks with very long critical paths may cause timeline bottlenecks', severity='high'))
    return conflicts

def _add_resolution_recommendations(self, constraint_graph: ConstraintGraph) -> ConstraintGraph:
    """Add resolution recommendations to conflicts."""
    for conflict in constraint_graph.conflicts:
        if conflict.conflict_type == 'circular_dependency':
            conflict.description += '\nRecommendation: Remove one dependency to break the cycle'
        elif conflict.conflict_type == 'missing_dependency':
            conflict.description += '\nRecommendation: Remove invalid dependency or create missing task'
        elif conflict.conflict_type == 'status_conflict':
            conflict.description += '\nRecommendation: Update task status or verify dependency completion'
        elif conflict.conflict_type == 'resource_conflict':
            conflict.description += '\nRecommendation: Stagger task execution or increase team size'
        elif conflict.conflict_type == 'timeline_conflict':
            conflict.description += '\nRecommendation: Parallelize tasks or reduce scope'
    return constraint_graph

def _auto_resolve_conflict(self, constraint_graph: ConstraintGraph, conflict: DependencyConflict) -> ConstraintGraph:
    """Automatically resolve a conflict where possible."""
    if conflict.conflict_type == 'status_conflict' and conflict.severity == 'low':
        for task_id in conflict.affected_tasks:
            task = constraint_graph.nodes.get(task_id)
            if task and task.completion_status == TaskStatus.NOT_STARTED:
                deps = constraint_graph.get_dependencies(task_id)
                all_completed = all((constraint_graph.nodes[dep_id].completion_status == TaskStatus.COMPLETED for dep_id in deps if dep_id in constraint_graph.nodes))
                if all_completed:
                    task.completion_status = TaskStatus.NOT_STARTED
    return constraint_graph

def calculate_layer(node_id: str, visited: Set[str]) -> int:
    if node_id in visited:
        return 0
    if node_id in node_layers:
        return node_layers[node_id]
    visited.add(node_id)
    dependencies = adjacency_list.get(node_id, [])
    if not dependencies:
        layer = 0
    else:
        max_dep_layer = max((calculate_layer(dep, visited.copy()) for dep in dependencies))
        layer = max_dep_layer + 1
    node_layers[node_id] = layer
    return layer

def dfs(node_id: str, path: List[str]) -> None:
    if node_id in rec_stack:
        cycle_start = path.index(node_id)
        cycle = path[cycle_start:] + [node_id]
        conflicts.append(DependencyConflict(conflict_type='circular_dependency', affected_tasks=cycle, description=f"Circular dependency detected: {' -> '.join(cycle)}", severity='critical'))
        return
    if node_id in visited:
        return
    visited.add(node_id)
    rec_stack.add(node_id)
    path.append(node_id)
    for dep in adjacency_list.get(node_id, []):
        dfs(dep, path.copy())
    rec_stack.remove(node_id)

def calculate_critical_path_length(task_id: str, memo: Dict[str, int]) -> int:
    if task_id in memo:
        return memo[task_id]
    task = nodes[task_id]
    dependencies_list = adjacency_list.get(task_id, [])
    if not dependencies_list:
        length = task.estimated_effort
    else:
        max_dep_length = max((calculate_critical_path_length(dep_id, memo) for dep_id in dependencies_list))
        length = max_dep_length + task.estimated_effort
    memo[task_id] = length
    return length

def calculate_layer(node_id: str, visited: Set[str]) -> int:
    if node_id in visited:
        return 0
    if node_id in node_layers:
        return node_layers[node_id]
    visited.add(node_id)
    dependencies = adjacency_list.get(node_id, [])
    if not dependencies:
        layer = 0
    else:
        max_dep_layer = max((calculate_layer(dep, visited.copy()) for dep in dependencies))
        layer = max_dep_layer + 1
    node_layers[node_id] = layer
    return layer

def dfs(node_id: str, path: List[str]) -> None:
    if node_id in rec_stack:
        cycle_start = path.index(node_id)
        cycle = path[cycle_start:] + [node_id]
        conflicts.append(DependencyConflict(conflict_type='circular_dependency', affected_tasks=cycle, description=f"Circular dependency detected: {' -> '.join(cycle)}", severity='critical'))
        return
    if node_id in visited:
        return
    visited.add(node_id)
    rec_stack.add(node_id)
    path.append(node_id)
    for dep in adjacency_list.get(node_id, []):
        dfs(dep, path.copy())
    rec_stack.remove(node_id)

def calculate_critical_path_length(task_id: str, memo: Dict[str, int]) -> int:
    if task_id in memo:
        return memo[task_id]
    task = nodes[task_id]
    dependencies_list = adjacency_list.get(task_id, [])
    if not dependencies_list:
        length = task.estimated_effort
    else:
        max_dep_length = max((calculate_critical_path_length(dep_id, memo) for dep_id in dependencies_list))
        length = max_dep_length + task.estimated_effort
    memo[task_id] = length
    return length

def calculate_layer(node_id: str, visited: Set[str]) -> int:
    if node_id in visited:
        return 0
    if node_id in node_layers:
        return node_layers[node_id]
    visited.add(node_id)
    dependencies = adjacency_list.get(node_id, [])
    if not dependencies:
        layer = 0
    else:
        max_dep_layer = max((calculate_layer(dep, visited.copy()) for dep in dependencies))
        layer = max_dep_layer + 1
    node_layers[node_id] = layer
    return layer

def dfs(node_id: str, path: List[str]) -> None:
    if node_id in rec_stack:
        cycle_start = path.index(node_id)
        cycle = path[cycle_start:] + [node_id]
        conflicts.append(DependencyConflict(conflict_type='circular_dependency', affected_tasks=cycle, description=f"Circular dependency detected: {' -> '.join(cycle)}", severity='critical'))
        return
    if node_id in visited:
        return
    visited.add(node_id)
    rec_stack.add(node_id)
    path.append(node_id)
    for dep in adjacency_list.get(node_id, []):
        dfs(dep, path.copy())
    rec_stack.remove(node_id)

def calculate_critical_path_length(task_id: str, memo: Dict[str, int]) -> int:
    if task_id in memo:
        return memo[task_id]
    task = nodes[task_id]
    dependencies_list = adjacency_list.get(task_id, [])
    if not dependencies_list:
        length = task.estimated_effort
    else:
        max_dep_length = max((calculate_critical_path_length(dep_id, memo) for dep_id in dependencies_list))
        length = max_dep_length + task.estimated_effort
    memo[task_id] = length
    return length
