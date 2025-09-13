"""
Layer Processor Services

This module was extracted from layer_processor.py
as part of RM-DDD compliance refactoring.
"""

from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict
from ..models.dag_models import SpecificationNode, TaskNode
from ..models.enums import TaskStatus
from .dependency_mapper import ConstraintGraph

class LayerProcessor:
    """
    Systematic layer processor for DAG orchestration.
    
    Categorizes specifications and tasks by dependency layers,
    identifies parallel execution opportunities, and provides
    systematic analysis for orchestration optimization.
    """

    def __init__(self):
        self.parallel_threshold = 2
        self.bottleneck_threshold = 0.3

    def process_layers(self, specifications: List[SpecificationNode], constraint_graph: ConstraintGraph) -> LayerProcessingResult:
        """
        Process dependency layers for specifications and tasks.
        
        Args:
            specifications: List of specification nodes
            constraint_graph: Complete constraint graph with tasks
            
        Returns:
            LayerProcessingResult: Complete layer processing analysis
        """
        spec_layers = self._process_specification_layers(specifications, constraint_graph)
        task_layers = constraint_graph.dependency_layers
        parallel_opportunities = self._identify_parallel_opportunities(task_layers, constraint_graph)
        bottleneck_layers = self._identify_bottleneck_layers(task_layers, constraint_graph)
        critical_path_layers = self._identify_critical_path_layers(task_layers, constraint_graph)
        return LayerProcessingResult(specification_layers=spec_layers, task_layers=task_layers, parallel_opportunities=parallel_opportunities, bottleneck_layers=bottleneck_layers, critical_path_layers=critical_path_layers)

    def categorize_specifications_by_layer(self, specifications: List[SpecificationNode]) -> Dict[int, List[SpecificationNode]]:
        """
        Categorize specifications by dependency layer.
        
        Args:
            specifications: List of specification nodes
            
        Returns:
            Dict[int, List[SpecificationNode]]: Layer number -> specifications
        """
        spec_graph = {}
        for spec in specifications:
            spec_graph[spec.spec_name] = spec.dependencies
        layers = defaultdict(list)
        spec_layers = {}

        def calculate_spec_layer(spec_name: str, visited: Set[str]) -> int:
            if spec_name in visited:
                return 0
            if spec_name in spec_layers:
                return spec_layers[spec_name]
            visited.add(spec_name)
            dependencies = spec_graph.get(spec_name, [])
            if not dependencies:
                layer = 0
            else:
                max_dep_layer = max((calculate_spec_layer(dep, visited.copy()) for dep in dependencies if dep in spec_graph))
                layer = max_dep_layer + 1
            spec_layers[spec_name] = layer
            return layer
        for spec in specifications:
            layer = calculate_spec_layer(spec.spec_name, set())
            layers[layer].append(spec)
        return dict(layers)

    def analyze_layer_dependencies(self, layer_number: int, specifications: List[SpecificationNode], all_specifications: List[SpecificationNode]) -> List[str]:
        """
        Analyze dependencies for a specific layer.
        
        Args:
            layer_number: Layer to analyze
            specifications: Specifications in this layer
            all_specifications: All specifications for dependency lookup
            
        Returns:
            List[str]: Blocking dependencies for this layer
        """
        blocking_dependencies = []
        spec_lookup = {spec.spec_name: spec for spec in all_specifications}
        for spec in specifications:
            for dep_name in spec.dependencies:
                dep_spec = spec_lookup.get(dep_name)
                if dep_spec and dep_spec.completion_percentage < 100.0:
                    blocking_dependencies.append(dep_name)
        return list(set(blocking_dependencies))

    def identify_parallel_execution_opportunities(self, task_layers: Dict[int, List[str]], constraint_graph: ConstraintGraph) -> List[Tuple[int, List[str]]]:
        """
        Identify opportunities for parallel execution within layers.
        
        Args:
            task_layers: Task layers from constraint graph
            constraint_graph: Complete constraint graph
            
        Returns:
            List[Tuple[int, List[str]]]: (layer, parallel_task_ids) pairs
        """
        parallel_opportunities = []
        for layer, task_ids in task_layers.items():
            if len(task_ids) >= self.parallel_threshold:
                parallel_groups = self._group_parallel_tasks(task_ids, constraint_graph)
                for group in parallel_groups:
                    if len(group) >= self.parallel_threshold:
                        parallel_opportunities.append((layer, group))
        return parallel_opportunities

    def _process_specification_layers(self, specifications: List[SpecificationNode], constraint_graph: ConstraintGraph) -> List[SpecificationLayer]:
        """Process specification layers with detailed analysis."""
        spec_layers_dict = self.categorize_specifications_by_layer(specifications)
        spec_layers = []
        for layer_num in sorted(spec_layers_dict.keys()):
            specs = spec_layers_dict[layer_num]
            total_tasks = sum((spec.task_count for spec in specs))
            completed_tasks = sum((spec.completed_tasks for spec in specs))
            completion_percentage = completed_tasks / total_tasks * 100.0 if total_tasks > 0 else 0.0
            estimated_effort = self._estimate_layer_effort(specs, constraint_graph)
            can_start_parallel = self._can_layer_start_parallel(specs, specifications)
            blocking_dependencies = self.analyze_layer_dependencies(layer_num, specs, specifications)
            spec_layers.append(SpecificationLayer(layer_number=layer_num, specifications=specs, total_tasks=total_tasks, completed_tasks=completed_tasks, completion_percentage=completion_percentage, estimated_effort=estimated_effort, can_start_parallel=can_start_parallel, blocking_dependencies=blocking_dependencies))
        return spec_layers

    def _estimate_layer_effort(self, specifications: List[SpecificationNode], constraint_graph: ConstraintGraph) -> int:
        """Estimate total effort for a specification layer."""
        total_effort = 0
        for spec in specifications:
            spec_tasks = [task for task in constraint_graph.nodes.values() if task.spec_name == spec.spec_name]
            for task in spec_tasks:
                if task.completion_status != TaskStatus.COMPLETED:
                    total_effort += task.estimated_effort
        return total_effort

    def _can_layer_start_parallel(self, specifications: List[SpecificationNode], all_specifications: List[SpecificationNode]) -> bool:
        """Check if specifications in a layer can start in parallel."""
        spec_lookup = {spec.spec_name: spec for spec in all_specifications}
        for spec in specifications:
            for dep_name in spec.dependencies:
                dep_spec = spec_lookup.get(dep_name)
                if dep_spec and dep_spec.completion_percentage < 100.0:
                    return False
        return True

    def _identify_parallel_opportunities(self, task_layers: Dict[int, List[str]], constraint_graph: ConstraintGraph) -> List[Tuple[int, List[str]]]:
        """Identify parallel execution opportunities."""
        return self.identify_parallel_execution_opportunities(task_layers, constraint_graph)

    def _identify_bottleneck_layers(self, task_layers: Dict[int, List[str]], constraint_graph: ConstraintGraph) -> List[int]:
        """Identify layers that are bottlenecks."""
        bottleneck_layers = []
        total_effort = sum((task.estimated_effort for task in constraint_graph.nodes.values()))
        for layer, task_ids in task_layers.items():
            layer_effort = sum((constraint_graph.nodes[task_id].estimated_effort for task_id in task_ids if task_id in constraint_graph.nodes))
            if total_effort > 0 and layer_effort / total_effort > self.bottleneck_threshold:
                bottleneck_layers.append(layer)
        return bottleneck_layers

    def _identify_critical_path_layers(self, task_layers: Dict[int, List[str]], constraint_graph: ConstraintGraph) -> List[int]:
        """Identify layers that are on critical paths."""
        critical_layers = []
        for layer, task_ids in task_layers.items():
            has_critical_task = False
            for task_id in task_ids:
                if task_id not in constraint_graph.nodes:
                    continue
                task = constraint_graph.nodes[task_id]
                dependents = constraint_graph.get_dependents(task_id)
                if task.estimated_effort > 12 and len(dependents) > 2:
                    has_critical_task = True
                    break
            if has_critical_task:
                critical_layers.append(layer)
        return critical_layers

    def _group_parallel_tasks(self, task_ids: List[str], constraint_graph: ConstraintGraph) -> List[List[str]]:
        """Group tasks that can run in parallel within a layer."""
        if len(task_ids) <= 1:
            return [task_ids] if task_ids else []
        groups = []
        remaining_tasks = task_ids.copy()
        while remaining_tasks:
            current_group = [remaining_tasks.pop(0)]
            current_effort = constraint_graph.nodes[current_group[0]].estimated_effort
            i = 0
            while i < len(remaining_tasks):
                task_id = remaining_tasks[i]
                task_effort = constraint_graph.nodes[task_id].estimated_effort
                if abs(task_effort - current_effort) / max(current_effort, 1) <= 0.5:
                    current_group.append(remaining_tasks.pop(i))
                else:
                    i += 1
            groups.append(current_group)
        return groups
