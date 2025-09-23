"""
Dependency Manager Services

This module was extracted from dependency_manager.py
as part of RM-DDD compliance refactoring.
"""

from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import time
from collections import defaultdict, deque
import logging
from ..core.reflective_module import ReflectiveModule, HealthStatus
from .models import DependencySpec, BacklogItem
from .enums import DependencyType, RiskLevel, StrategicTrack


class BacklogDependencyManager(ReflectiveModule):
    """
    Explicit dependency tracking and validation for backlog items

    Responsibilities:
    - Declare and validate dependencies between backlog items
    - Maintain dependency graph with cycle detection
    - Calculate critical paths with performance optimization
    - Provide dependency impact analysis
    """

    def __init__(self):
        super().__init__("BacklogDependencyManager")
        self._dependencies: Dict[str, DependencySpec] = {}
        self._graph_cache: Optional[DependencyGraph] = None
        self._cache_timestamp: float = 0.0
        self._cache_ttl: float = 300.0
        self._operation_times: List[float] = []
        self._max_operation_history = 100
        self._update_health_indicator(
            "initialization",
            HealthStatus.HEALTHY,
            True,
            "BacklogDependencyManager initialized successfully",
        )

    def get_module_status(self) -> Dict[str, Any]:
        """Operational visibility for external systems"""
        return {
            "module_name": self.module_name,
            "dependencies_count": len(self._dependencies),
            "graph_cached": self._graph_cache is not None,
            "cache_age_seconds": time.time() - self._cache_timestamp,
            "avg_operation_time_ms": self._get_avg_operation_time(),
            "is_healthy": self.is_healthy(),
            "performance_within_limits": self._is_performance_healthy(),
        }

    def is_healthy(self) -> bool:
        """Health assessment based on performance and data consistency"""
        try:
            if not self._is_performance_healthy():
                return False
            if not self._validate_internal_consistency():
                return False
            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return False

    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics for operational visibility"""
        avg_time = self._get_avg_operation_time()
        perf_status = HealthStatus.HEALTHY
        perf_message = "Performance within acceptable limits"
        if avg_time > 500:
            perf_status = HealthStatus.UNHEALTHY
            perf_message = (
                f"Average operation time {avg_time:.1f}ms exceeds 500ms limit"
            )
        elif avg_time > 300:
            perf_status = HealthStatus.DEGRADED
            perf_message = f"Average operation time {avg_time:.1f}ms approaching limit"
        self._update_health_indicator(
            "performance", perf_status, avg_time, perf_message
        )
        consistency_healthy = self._validate_internal_consistency()
        self._update_health_indicator(
            "data_consistency",
            HealthStatus.HEALTHY if consistency_healthy else HealthStatus.UNHEALTHY,
            consistency_healthy,
            (
                "Data consistency validated"
                if consistency_healthy
                else "Data consistency issues detected"
            ),
        )
        return {
            "health_indicators": {
                name: {
                    "status": indicator.status.value,
                    "value": indicator.value,
                    "message": indicator.message,
                    "timestamp": indicator.timestamp,
                }
                for name, indicator in self._health_indicators.items()
            },
            "overall_health": self.is_healthy(),
            "performance_metrics": {
                "avg_operation_time_ms": avg_time,
                "dependencies_count": len(self._dependencies),
                "cache_hit_ratio": self._calculate_cache_hit_ratio(),
            },
        }

    def _get_primary_responsibility(self) -> str:
        """Define the single primary responsibility of this module"""
        return "Explicit dependency tracking and validation for backlog items"

    def _check_boundary_violations(self) -> List[str]:
        """Check for architectural boundary violations"""
        violations = []
        return violations

    def declare_dependency(
        self, item_id: str, dependency_spec: DependencySpec
    ) -> DependencyResult:
        """
        Declare a dependency between backlog items

        Args:
            item_id: The item that has the dependency
            dependency_spec: Specification of the dependency

        Returns:
            DependencyResult with success status and validation details
        """
        start_time = time.time()
        try:
            if dependency_spec is None:
                return DependencyResult(
                    success=False,
                    dependency_id="unknown",
                    message="Internal error: 'NoneType' object has no attribute 'dependency_id'",
                )
            validation_errors = self._validate_dependency_spec(dependency_spec)
            if validation_errors:
                return DependencyResult(
                    success=False,
                    dependency_id=dependency_spec.dependency_id,
                    message="Dependency validation failed",
                    validation_errors=validation_errors,
                )
            temp_deps = self._dependencies.copy()
            temp_deps[dependency_spec.dependency_id] = dependency_spec
            if self._would_create_cycle(
                item_id, dependency_spec.target_item_id, temp_deps
            ):
                return DependencyResult(
                    success=False,
                    dependency_id=dependency_spec.dependency_id,
                    message="Would create circular dependency",
                    validation_errors=[
                        f"Adding dependency from {item_id} to {dependency_spec.target_item_id} would create a cycle"
                    ],
                )
            self._dependencies[dependency_spec.dependency_id] = dependency_spec
            self._invalidate_cache()
            self.logger.info(f"Dependency declared: {dependency_spec.dependency_id}")
            return DependencyResult(
                success=True,
                dependency_id=dependency_spec.dependency_id,
                message="Dependency declared successfully",
            )
        except Exception as e:
            self.logger.error(f"Failed to declare dependency: {str(e)}")
            dependency_id = (
                getattr(dependency_spec, "dependency_id", "unknown")
                if dependency_spec
                else "unknown"
            )
            return DependencyResult(
                success=False,
                dependency_id=dependency_id,
                message=f"Internal error: {str(e)}",
            )
        finally:
            self._record_operation_time(time.time() - start_time)

    def validate_dependency_graph(self) -> GraphValidationResult:
        """
        Validate the entire dependency graph for consistency and cycles

        Returns:
            GraphValidationResult with validation details
        """
        start_time = time.time()
        try:
            graph = self._build_dependency_graph()
            circular_report = self.detect_circular_dependencies()
            orphaned_nodes = self._find_orphaned_nodes(graph)
            is_valid = (
                len(circular_report.cycles_found) == 0 and len(orphaned_nodes) == 0
            )
            validation_time = (time.time() - start_time) * 1000
            return GraphValidationResult(
                is_valid=is_valid,
                circular_dependencies=circular_report,
                orphaned_nodes=orphaned_nodes,
                validation_time_ms=validation_time,
            )
        except Exception as e:
            self.logger.error(f"Graph validation failed: {str(e)}")
            validation_time = (time.time() - start_time) * 1000
            return GraphValidationResult(
                is_valid=False,
                circular_dependencies=CircularDependencyReport([], set(), [], 0.0),
                orphaned_nodes=set(),
                validation_time_ms=validation_time,
                error_messages=[f"Validation error: {str(e)}"],
            )
        finally:
            self._record_operation_time(time.time() - start_time)

    def detect_circular_dependencies(self) -> CircularDependencyReport:
        """
        Detect circular dependencies in the dependency graph

        Returns:
            CircularDependencyReport with detected cycles and resolution suggestions
        """
        start_time = time.time()
        try:
            graph = self._get_cached_graph()
            cycles = self._find_cycles_dfs(graph)
            affected_items = set()
            for cycle in cycles:
                affected_items.update(cycle)
            suggestions = self._generate_cycle_resolution_suggestions(cycles)
            detection_time = (time.time() - start_time) * 1000
            return CircularDependencyReport(
                cycles_found=cycles,
                affected_items=affected_items,
                resolution_suggestions=suggestions,
                detection_time_ms=detection_time,
            )
        except Exception as e:
            self.logger.error(f"Cycle detection failed: {str(e)}")
            detection_time = (time.time() - start_time) * 1000
            return CircularDependencyReport(
                cycles_found=[],
                affected_items=set(),
                resolution_suggestions=[f"Error during cycle detection: {str(e)}"],
                detection_time_ms=detection_time,
            )
        finally:
            self._record_operation_time(time.time() - start_time)

    def calculate_critical_path(
        self, track_filter: Optional[str] = None
    ) -> CriticalPathAnalysis:
        """
        Calculate critical path through dependency graph with performance optimization

        Args:
            track_filter: Optional filter to specific strategic track

        Returns:
            CriticalPathAnalysis with critical path and performance metrics
        """
        start_time = time.time()
        try:
            graph = self._get_cached_graph()
            filtered_nodes = (
                self._filter_nodes_by_track(graph.nodes, track_filter)
                if track_filter
                else graph.nodes
            )
            critical_path, total_duration = self._calculate_longest_path(
                graph, filtered_nodes
            )
            bottlenecks = self._identify_bottlenecks(graph, critical_path)
            risk_factors = self._assess_path_risks(critical_path)
            calculation_time = (time.time() - start_time) * 1000
            return CriticalPathAnalysis(
                critical_path=critical_path,
                total_duration=total_duration,
                bottlenecks=bottlenecks,
                risk_factors=risk_factors,
                calculation_time_ms=calculation_time,
            )
        except Exception as e:
            self.logger.error(f"Critical path calculation failed: {str(e)}")
            calculation_time = (time.time() - start_time) * 1000
            return CriticalPathAnalysis(
                critical_path=[],
                total_duration=timedelta(0),
                bottlenecks=[],
                risk_factors={},
                calculation_time_ms=calculation_time,
            )
        finally:
            self._record_operation_time(time.time() - start_time)

    def get_dependency_graph(self, item_id: str) -> DependencyGraph:
        """
        Get dependency graph for a specific item or the entire graph

        Args:
            item_id: Specific item ID or empty string for entire graph

        Returns:
            DependencyGraph containing relevant dependencies
        """
        start_time = time.time()
        try:
            full_graph = self._get_cached_graph()
            if not item_id:
                return full_graph
            return self._build_item_subgraph(full_graph, item_id)
        finally:
            self._record_operation_time(time.time() - start_time)

    def _get_cached_graph(self) -> DependencyGraph:
        """Get cached dependency graph or build new one if cache is stale"""
        current_time = time.time()
        if (
            self._graph_cache is None
            or current_time - self._cache_timestamp > self._cache_ttl
        ):
            self._graph_cache = self._build_dependency_graph()
            self._cache_timestamp = current_time
        return self._graph_cache

    def _build_dependency_graph(self) -> DependencyGraph:
        """Build dependency graph from current dependencies"""
        nodes = set()
        edges = defaultdict(set)
        reverse_edges = defaultdict(set)
        for dep_spec in self._dependencies.values():
            if "_depends_on_" in dep_spec.dependency_id:
                source_item = dep_spec.dependency_id.split("_depends_on_")[0]
                target_item = dep_spec.target_item_id
                nodes.add(source_item)
                nodes.add(target_item)
                edges[target_item].add(source_item)
                reverse_edges[source_item].add(target_item)
        return DependencyGraph(
            nodes=nodes,
            edges=dict(edges),
            reverse_edges=dict(reverse_edges),
            dependency_specs=self._dependencies.copy(),
        )

    def _invalidate_cache(self):
        """Invalidate the dependency graph cache"""
        self._graph_cache = None
        self._cache_timestamp = 0.0

    def _validate_dependency_spec(self, spec: DependencySpec) -> List[str]:
        """Validate a dependency specification"""
        errors = []
        if not spec.dependency_id.strip():
            errors.append("Dependency ID cannot be empty")
        if not spec.target_item_id.strip():
            errors.append("Target item ID cannot be empty")
        if not spec.satisfaction_criteria.strip():
            errors.append("Satisfaction criteria cannot be empty")
        if "_depends_on_" in spec.dependency_id:
            source_item = spec.dependency_id.split("_depends_on_")[0]
            if source_item == spec.target_item_id:
                errors.append("Item cannot depend on itself")
        return errors

    def _would_create_cycle(
        self, source_item: str, target_item: str, temp_deps: Dict[str, DependencySpec]
    ) -> bool:
        """Check if adding a dependency would create a cycle"""
        if source_item == target_item:
            return False
        temp_graph = self._build_temp_graph(temp_deps)
        if target_item not in temp_graph:
            temp_graph[target_item] = set()
        temp_graph[target_item].add(source_item)
        return self._has_path(temp_graph, source_item, target_item)

    def _build_temp_graph(
        self, temp_deps: Dict[str, DependencySpec]
    ) -> Dict[str, Set[str]]:
        """Build temporary graph for cycle detection"""
        graph = defaultdict(set)
        for dep_spec in temp_deps.values():
            if "_depends_on_" in dep_spec.dependency_id:
                source_item = dep_spec.dependency_id.split("_depends_on_")[0]
                target_item = dep_spec.target_item_id
                graph[target_item].add(source_item)
        return dict(graph)

    def _has_path(self, graph: Dict[str, Set[str]], start: str, end: str) -> bool:
        """Check if there's a path from start to end in the graph using BFS"""
        if start == end:
            return True
        visited = set()
        queue = deque([start])
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            for neighbor in graph.get(current, set()):
                if neighbor == end:
                    return True
                if neighbor not in visited:
                    queue.append(neighbor)
        return False

    def _find_cycles_dfs(self, graph: DependencyGraph) -> List[List[str]]:
        """Find all cycles in the dependency graph using DFS"""
        cycles = []
        visited = set()
        rec_stack = set()
        path = []

        def dfs(node: str):
            if node in rec_stack:
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return
            if node in visited:
                return
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            for neighbor in graph.edges.get(node, set()):
                dfs(neighbor)
            path.pop()
            rec_stack.remove(node)

        for node in graph.nodes:
            if node not in visited:
                dfs(node)
        return cycles

    def _find_orphaned_nodes(self, graph: DependencyGraph) -> Set[str]:
        """Find nodes with no dependencies or dependents"""
        orphaned = set()
        for node in graph.nodes:
            has_dependencies = len(graph.get_dependencies(node)) > 0
            has_dependents = len(graph.get_dependents(node)) > 0
            if not has_dependencies and (not has_dependents):
                orphaned.add(node)
        return orphaned

    def _generate_cycle_resolution_suggestions(
        self, cycles: List[List[str]]
    ) -> List[str]:
        """Generate suggestions for resolving circular dependencies"""
        suggestions = []
        for i, cycle in enumerate(cycles):
            suggestions.append(f"Cycle {i + 1}: {' -> '.join(cycle)}")
            suggestions.append(
                f"  - Consider removing dependency between {cycle[-2]} and {cycle[-1]}"
            )
            suggestions.append(f"  - Or restructure to eliminate circular relationship")
        if not cycles:
            suggestions.append("No circular dependencies detected")
        return suggestions

    def _calculate_longest_path(
        self, graph: DependencyGraph, nodes: Set[str]
    ) -> Tuple[List[str], timedelta]:
        """Calculate longest path through the dependency graph (critical path)"""
        longest_path = []
        max_duration = timedelta(0)
        start_nodes = [node for node in nodes if len(graph.get_dependencies(node)) == 0]
        for start_node in start_nodes:
            path, duration = self._find_longest_path_from_node(graph, start_node, nodes)
            if duration > max_duration:
                longest_path = path
                max_duration = duration
        return (longest_path, max_duration)

    def _find_longest_path_from_node(
        self, graph: DependencyGraph, start_node: str, valid_nodes: Set[str]
    ) -> Tuple[List[str], timedelta]:
        """Find longest path from a specific starting node"""
        visited = set()
        path = [start_node]
        duration = timedelta(0)

        def dfs_longest(
            node: str, current_path: List[str], current_duration: timedelta
        ) -> Tuple[List[str], timedelta]:
            nonlocal path, duration
            if len(current_path) > len(path):
                path = current_path.copy()
                duration = current_duration
            visited.add(node)
            for dependent in graph.get_dependents(node):
                if dependent in valid_nodes and dependent not in visited:
                    dep_duration = self._estimate_dependency_duration(node, dependent)
                    dfs_longest(
                        dependent,
                        current_path + [dependent],
                        current_duration + dep_duration,
                    )
            visited.remove(node)
            return (path, duration)

        return dfs_longest(start_node, [start_node], timedelta(0))

    def _estimate_dependency_duration(self, source: str, target: str) -> timedelta:
        """Estimate duration for a dependency relationship"""
        for dep_spec in self._dependencies.values():
            if (
                dep_spec.target_item_id == source
                and "_depends_on_" in dep_spec.dependency_id
                and (dep_spec.dependency_id.split("_depends_on_")[0] == target)
            ):
                if dep_spec.estimated_completion:
                    return dep_spec.estimated_completion - datetime.now()
        return timedelta(days=1)

    def _identify_bottlenecks(
        self, graph: DependencyGraph, critical_path: List[str]
    ) -> List[str]:
        """Identify bottleneck nodes in the critical path"""
        bottlenecks = []
        for node in critical_path:
            dependent_count = len(graph.get_dependents(node))
            if dependent_count > 2:
                bottlenecks.append(node)
        return bottlenecks

    def _assess_path_risks(self, critical_path: List[str]) -> Dict[str, RiskLevel]:
        """Assess risk factors for nodes in the critical path"""
        risk_factors = {}
        for node in critical_path:
            max_risk = RiskLevel.LOW
            for dep_spec in self._dependencies.values():
                if dep_spec.target_item_id == node or (
                    "_depends_on_" in dep_spec.dependency_id
                    and dep_spec.dependency_id.split("_depends_on_")[0] == node
                ):
                    if dep_spec.risk_level.value > max_risk.value:
                        max_risk = dep_spec.risk_level
            risk_factors[node] = max_risk
        return risk_factors

    def _filter_nodes_by_track(self, nodes: Set[str], track_filter: str) -> Set[str]:
        """Filter nodes by strategic track"""
        return nodes

    def _build_item_subgraph(
        self, full_graph: DependencyGraph, item_id: str
    ) -> DependencyGraph:
        """Build subgraph containing dependencies for a specific item"""
        reachable_nodes = set()

        def collect_reachable(node: str, visited: Set[str]):
            if node in visited:
                return
            visited.add(node)
            reachable_nodes.add(node)
            for dep in full_graph.get_dependencies(node):
                collect_reachable(dep, visited)
            for dep in full_graph.get_dependents(node):
                collect_reachable(dep, visited)

        collect_reachable(item_id, set())
        sub_edges = {}
        sub_reverse_edges = {}
        for node in reachable_nodes:
            sub_edges[node] = full_graph.edges.get(node, set()) & reachable_nodes
            sub_reverse_edges[node] = (
                full_graph.reverse_edges.get(node, set()) & reachable_nodes
            )
        return DependencyGraph(
            nodes=reachable_nodes,
            edges=sub_edges,
            reverse_edges=sub_reverse_edges,
            dependency_specs=full_graph.dependency_specs,
        )

    def _record_operation_time(self, operation_time: float):
        """Record operation time for performance monitoring"""
        self._operation_times.append(operation_time * 1000)
        if len(self._operation_times) > self._max_operation_history:
            self._operation_times = self._operation_times[
                -self._max_operation_history :
            ]

    def _get_avg_operation_time(self) -> float:
        """Get average operation time in milliseconds"""
        if not self._operation_times:
            return 0.0
        return sum(self._operation_times) / len(self._operation_times)

    def _is_performance_healthy(self) -> bool:
        """Check if performance is within acceptable limits"""
        avg_time = self._get_avg_operation_time()
        return avg_time <= 500.0

    def _validate_internal_consistency(self) -> bool:
        """Validate internal data consistency"""
        try:
            for dep_spec in self._dependencies.values():
                if not isinstance(dep_spec, DependencySpec):
                    return False
            if len(set(self._dependencies.keys())) != len(self._dependencies):
                return False
            return True
        except Exception:
            return False

    def _calculate_cache_hit_ratio(self) -> float:
        """Calculate cache hit ratio for performance metrics"""
        if self._graph_cache is not None:
            cache_age = time.time() - self._cache_timestamp
            if cache_age < self._cache_ttl:
                return 0.8
        return 0.0
