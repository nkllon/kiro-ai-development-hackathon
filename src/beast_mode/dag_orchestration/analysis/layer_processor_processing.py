"""
Layer Processor Processing

This module was extracted from layer_processor.py
as part of RM-DDD compliance refactoring.
"""

from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict
from ..models.dag_models import SpecificationNode, TaskNode
from ..models.enums import TaskStatus
from .dependency_mapper import ConstraintGraph
from src.rm_ddd.core.health import ModuleHealth


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

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

