"""
Dependency Manager Services

This module was extracted from dependency_manager.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
import logging
from typing import Dict, List, Any, Set, Tuple
from dataclasses import dataclass
from pathlib import Path
import json
from ..core.reflective_module import ReflectiveModule

class DependencyFirstManager(ReflectiveModule):
    """
    Manages dependency-first implementation strategy to avoid circular dependency hell.
    
    The key insight: implement foundation dependencies first, then build everything else
    on that solid foundation. This prevents the "chicken and egg" problem of needing
    Beast Mode to refactor Beast Mode.
    """

    def __init__(self):
        super().__init__('DependencyFirstManager')
        self.logger = logging.getLogger(__name__)
        self.dependency_graph: Dict[str, DependencyNode] = {}
        self.implementation_phases: List[ImplementationPhase] = []
        self.spec_dependencies = {'ghostbusters-framework': [], 'systematic-pdca-orchestrator': ['ghostbusters-framework'], 'tool-health-manager': ['ghostbusters-framework'], 'systematic-metrics-engine': ['ghostbusters-framework'], 'parallel-dag-orchestrator': ['ghostbusters-framework'], 'beast-mode-core': ['systematic-pdca-orchestrator', 'tool-health-manager', 'systematic-metrics-engine', 'parallel-dag-orchestrator'], 'integrated-beast-mode-system': ['beast-mode-core']}
        self.logger.info('🔍 Dependency-First Manager initialized')

    async def analyze_dependency_graph(self, specs: List[str]) -> Dict[str, Any]:
        """Analyze all specs to create dependency-ordered implementation plan"""
        self.logger.info(f'📊 Analyzing dependency graph for {len(specs)} specs...')
        self.dependency_graph = self._build_dependency_graph(specs)
        circular_deps = self._detect_circular_dependencies()
        if circular_deps:
            raise Exception(f'Circular dependencies detected: {circular_deps}')
        self._calculate_dependency_layers()
        parallel_groups = self._identify_parallel_opportunities()
        graph_analysis = {'dependency_graph': self.dependency_graph, 'circular_dependencies': circular_deps, 'dependency_layers': self._get_dependency_layers(), 'parallel_opportunities': parallel_groups, 'foundation_components': self._get_foundation_components(), 'total_specs': len(specs)}
        self.logger.info(f'✅ Dependency analysis complete: {len(self._get_dependency_layers())} layers identified')
        return graph_analysis

    def _build_dependency_graph(self, specs: List[str]) -> Dict[str, DependencyNode]:
        """Build the dependency graph from spec dependencies"""
        graph = {}
        for spec in specs:
            dependencies = self.spec_dependencies.get(spec, [])
            node = DependencyNode(spec_name=spec, dependencies=dependencies, dependents=[])
            graph[spec] = node
        for spec, node in graph.items():
            for dep in node.dependencies:
                if dep in graph:
                    graph[dep].dependents.append(spec)
        return graph

    def _detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies using DFS"""
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(node: str, path: List[str]) -> bool:
            if node in rec_stack:
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return True
            if node in visited:
                return False
            visited.add(node)
            rec_stack.add(node)
            for dep in self.dependency_graph[node].dependencies:
                if dep in self.dependency_graph:
                    if dfs(dep, path + [node]):
                        return True
            rec_stack.remove(node)
            return False
        for spec in self.dependency_graph:
            if spec not in visited:
                dfs(spec, [])
        return cycles

    def _calculate_dependency_layers(self):
        """Calculate dependency layers for topological ordering"""
        current_layer = 0
        remaining_specs = set(self.dependency_graph.keys())
        while remaining_specs:
            current_layer_specs = []
            for spec in list(remaining_specs):
                node = self.dependency_graph[spec]
                deps_satisfied = all((dep not in remaining_specs or dep not in self.dependency_graph for dep in node.dependencies))
                if deps_satisfied:
                    current_layer_specs.append(spec)
            if not current_layer_specs:
                raise Exception(f'Cannot resolve dependencies for remaining specs: {remaining_specs}')
            for spec in current_layer_specs:
                self.dependency_graph[spec].layer = current_layer
                remaining_specs.remove(spec)
            current_layer += 1

    def _identify_parallel_opportunities(self) -> Dict[str, List[str]]:
        """Identify specs that can be implemented in parallel"""
        parallel_groups = {}
        for spec, node in self.dependency_graph.items():
            layer_key = f'layer_{node.layer}'
            if layer_key not in parallel_groups:
                parallel_groups[layer_key] = []
            parallel_groups[layer_key].append(spec)
        for spec, node in self.dependency_graph.items():
            if node.layer == 0:
                node.parallel_group = 'foundation'
            elif spec in ['systematic-pdca-orchestrator', 'tool-health-manager', 'systematic-metrics-engine', 'parallel-dag-orchestrator']:
                node.parallel_group = 'specialized'
            elif spec in ['beast-mode-core', 'integrated-beast-mode-system']:
                node.parallel_group = 'integration'
            else:
                node.parallel_group = f'layer_{node.layer}'
        return parallel_groups

    async def create_implementation_phases(self, dependency_graph: Dict[str, Any]) -> List[ImplementationPhase]:
        """Create phased implementation plan with maximum parallelization"""
        self.logger.info('📋 Creating implementation phases with maximum parallelization...')
        phases = []
        foundation_specs = [spec for spec, node in self.dependency_graph.items() if node.layer == 0]
        phases.append(ImplementationPhase(phase_number=1, phase_name='Foundation Layer', specs=foundation_specs, can_parallelize=True, estimated_duration_days=1, dependencies_satisfied=[]))
        specialized_specs = [spec for spec, node in self.dependency_graph.items() if node.parallel_group == 'specialized']
        phases.append(ImplementationPhase(phase_number=2, phase_name='Specialized Components', specs=specialized_specs, can_parallelize=True, estimated_duration_days=1, dependencies_satisfied=foundation_specs))
        integration_specs = [spec for spec, node in self.dependency_graph.items() if node.parallel_group == 'integration']
        phases.append(ImplementationPhase(phase_number=3, phase_name='Integration Layer', specs=integration_specs, can_parallelize=False, estimated_duration_days=1, dependencies_satisfied=specialized_specs))
        self.implementation_phases = phases
        sequential_duration = sum((len(phase.specs) for phase in phases))
        parallel_duration = len(phases)
        timeline_reduction = (sequential_duration - parallel_duration) / sequential_duration * 100
        self.logger.info(f'✅ Implementation plan created: {len(phases)} phases, {timeline_reduction:.1f}% timeline reduction')
        return phases

    def _get_dependency_layers(self) -> Dict[int, List[str]]:
        """Get specs organized by dependency layer"""
        layers = {}
        for spec, node in self.dependency_graph.items():
            if node.layer not in layers:
                layers[node.layer] = []
            layers[node.layer].append(spec)
        return layers

    def _get_foundation_components(self) -> List[str]:
        """Get foundation components (no dependencies)"""
        return [spec for spec, node in self.dependency_graph.items() if node.layer == 0]

    async def validate_dependency_order(self, implementation_order: List[str]) -> Dict[str, Any]:
        """Validate that implementation order respects dependencies"""
        implemented = set()
        violations = []
        for spec in implementation_order:
            if spec not in self.dependency_graph:
                violations.append(f'Unknown spec: {spec}')
                continue
            node = self.dependency_graph[spec]
            for dep in node.dependencies:
                if dep not in implemented and dep in self.dependency_graph:
                    violations.append(f'{spec} depends on {dep} but {dep} not implemented yet')
            implemented.add(spec)
        return {'valid': len(violations) == 0, 'violations': violations, 'implementation_order': implementation_order}

    def get_module_status(self) -> Dict[str, Any]:
        """Get current status of dependency manager"""
        return {'module_name': 'DependencyFirstManager', 'specs_analyzed': len(self.dependency_graph), 'dependency_layers': len(self._get_dependency_layers()) if self.dependency_graph else 0, 'implementation_phases': len(self.implementation_phases), 'foundation_components': len(self._get_foundation_components()), 'parallel_opportunities': len([p for p in self.implementation_phases if p.can_parallelize])}

    def is_healthy(self) -> bool:
        """Check if dependency manager is healthy"""
        try:
            if not self.dependency_graph:
                return False
            circular_deps = self._detect_circular_dependencies()
            if circular_deps:
                return False
            for node in self.dependency_graph.values():
                if node.layer < 0:
                    return False
            return True
        except Exception as e:
            self.logger.error(f'Dependency manager health check failed: {e}')
            return False

    def get_health_indicators(self) -> List[Dict[str, Any]]:
        """Get detailed health indicators"""
        indicators = []
        indicators.append({'name': 'dependency_graph_health', 'status': 'healthy' if self.dependency_graph else 'unhealthy', 'specs_count': len(self.dependency_graph), 'layers_count': len(self._get_dependency_layers()) if self.dependency_graph else 0})
        try:
            circular_deps = self._detect_circular_dependencies()
            indicators.append({'name': 'circular_dependency_check', 'status': 'healthy' if not circular_deps else 'unhealthy', 'circular_dependencies': circular_deps})
        except Exception as e:
            indicators.append({'name': 'circular_dependency_check', 'status': 'error', 'error': str(e)})
        indicators.append({'name': 'implementation_phases', 'status': 'healthy' if self.implementation_phases else 'not_ready', 'phases_count': len(self.implementation_phases), 'parallel_phases': len([p for p in self.implementation_phases if p.can_parallelize])})
        return indicators

    def _get_primary_responsibility(self) -> str:
        """Get the primary responsibility of this module"""
        return 'Manage dependency-first implementation strategy to avoid circular dependency hell'
