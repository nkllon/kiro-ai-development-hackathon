"""Graph algorithms for DAG management."""

from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, deque
import structlog


class GraphAlgorithms:
    """Graph algorithms for DAG operations."""
    
    def __init__(self):
        """Initialize graph algorithms."""
        self.logger = structlog.get_logger(__name__)
    
    def detect_cycles(self, graph: Dict[str, List[str]]) -> List[List[str]]:
        """
        Detect cycles in a directed graph using DFS.
        
        Args:
            graph: Adjacency list representation {node: [dependencies]}
            
        Returns:
            List of cycles, where each cycle is a list of nodes
        """
        cycles = []
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node: str) -> bool:
            """DFS helper function."""
            if node in rec_stack:
                # Found a cycle, extract it from the path
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return True
            
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            # Visit all dependencies
            for neighbor in graph.get(node, []):
                if dfs(neighbor):
                    return True
            
            rec_stack.remove(node)
            path.pop()
            return False
        
        # Check all nodes
        for node in graph:
            if node not in visited:
                dfs(node)
        
        self.logger.debug(
            "cycle_detection_completed",
            total_nodes=len(graph),
            cycles_found=len(cycles)
        )
        
        return cycles
    
    def topological_sort(self, graph: Dict[str, List[str]]) -> Optional[List[str]]:
        """
        Perform topological sort using Kahn's algorithm.
        
        Args:
            graph: Adjacency list representation {node: [dependencies]}
            
        Returns:
            Topologically sorted list of nodes, or None if cycles exist
        """
        # First check for cycles
        if self.detect_cycles(graph):
            self.logger.warning("topological_sort_failed_cycles_detected")
            return None
        
        # Build reverse graph (dependents) and calculate in-degrees
        reverse_graph = defaultdict(list)
        in_degree = defaultdict(int)
        
        # Initialize all nodes with in-degree 0
        all_nodes = set(graph.keys())
        for deps in graph.values():
            all_nodes.update(deps)
        
        for node in all_nodes:
            in_degree[node] = 0
        
        # Build reverse graph and calculate in-degrees
        for node, dependencies in graph.items():
            for dep in dependencies:
                reverse_graph[dep].append(node)
                in_degree[node] += 1
        
        # Kahn's algorithm
        queue = deque([node for node in all_nodes if in_degree[node] == 0])
        result = []
        
        while queue:
            node = queue.popleft()
            result.append(node)
            
            # Remove this node and update in-degrees of dependents
            for dependent in reverse_graph[node]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        # Check if all nodes were processed
        if len(result) != len(all_nodes):
            self.logger.error(
                "topological_sort_incomplete",
                expected_nodes=len(all_nodes),
                processed_nodes=len(result)
            )
            return None
        
        self.logger.debug(
            "topological_sort_completed",
            total_nodes=len(result),
            execution_order=result[:10]  # Log first 10 for debugging
        )
        
        return result
    
    def find_ready_nodes(self, graph: Dict[str, List[str]], completed: Set[str]) -> List[str]:
        """
        Find nodes that are ready to execute (all dependencies completed).
        
        Args:
            graph: Adjacency list representation {node: [dependencies]}
            completed: Set of completed node IDs
            
        Returns:
            List of nodes ready for execution
        """
        ready = []
        
        for node, dependencies in graph.items():
            if node not in completed:
                # Check if all dependencies are completed
                if all(dep in completed for dep in dependencies):
                    ready.append(node)
        
        self.logger.debug(
            "ready_nodes_identified",
            ready_count=len(ready),
            completed_count=len(completed),
            ready_nodes=ready[:10]  # Log first 10 for debugging
        )
        
        return ready
    
    def find_orphaned_nodes(self, graph: Dict[str, List[str]]) -> List[str]:
        """
        Find nodes that are referenced as dependencies but not defined.
        
        Args:
            graph: Adjacency list representation {node: [dependencies]}
            
        Returns:
            List of orphaned node IDs
        """
        defined_nodes = set(graph.keys())
        referenced_nodes = set()
        
        for dependencies in graph.values():
            referenced_nodes.update(dependencies)
        
        orphaned = list(referenced_nodes - defined_nodes)
        
        if orphaned:
            self.logger.warning(
                "orphaned_nodes_found",
                orphaned_count=len(orphaned),
                orphaned_nodes=orphaned
            )
        
        return orphaned
    
    def calculate_node_levels(self, graph: Dict[str, List[str]]) -> Dict[str, int]:
        """
        Calculate the level of each node in the DAG (longest path from root).
        
        Args:
            graph: Adjacency list representation {node: [dependencies]}
            
        Returns:
            Dictionary mapping node to its level
        """
        levels = {}
        
        def calculate_level(node: str, visited: Set[str]) -> int:
            """Recursively calculate node level."""
            if node in visited:
                # Circular dependency detected
                return -1
            
            if node in levels:
                return levels[node]
            
            visited.add(node)
            
            dependencies = graph.get(node, [])
            if not dependencies:
                # Root node
                level = 0
            else:
                # Level is max dependency level + 1
                dep_levels = []
                for dep in dependencies:
                    dep_level = calculate_level(dep, visited.copy())
                    if dep_level == -1:
                        return -1  # Circular dependency
                    dep_levels.append(dep_level)
                level = max(dep_levels) + 1
            
            levels[node] = level
            return level
        
        # Calculate levels for all nodes
        for node in graph:
            if node not in levels:
                result = calculate_level(node, set())
                if result == -1:
                    self.logger.error("circular_dependency_in_level_calculation", node=node)
                    return {}
        
        self.logger.debug(
            "node_levels_calculated",
            total_nodes=len(levels),
            max_level=max(levels.values()) if levels else 0
        )
        
        return levels
    
    def get_execution_batches(self, graph: Dict[str, List[str]]) -> List[List[str]]:
        """
        Group nodes into execution batches based on dependency levels.
        
        Args:
            graph: Adjacency list representation {node: [dependencies]}
            
        Returns:
            List of batches, where each batch contains nodes that can execute in parallel
        """
        levels = self.calculate_node_levels(graph)
        if not levels:
            return []
        
        # Group nodes by level
        level_groups = defaultdict(list)
        for node, level in levels.items():
            level_groups[level].append(node)
        
        # Convert to ordered list of batches
        max_level = max(levels.values())
        batches = []
        
        for level in range(max_level + 1):
            if level in level_groups:
                batches.append(level_groups[level])
        
        self.logger.debug(
            "execution_batches_created",
            total_batches=len(batches),
            batch_sizes=[len(batch) for batch in batches]
        )
        
        return batches
    
    def validate_graph_structure(self, graph: Dict[str, List[str]]) -> Dict[str, any]:
        """
        Comprehensive graph structure validation.
        
        Args:
            graph: Adjacency list representation {node: [dependencies]}
            
        Returns:
            Validation results dictionary
        """
        results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {}
        }
        
        # Check for cycles
        cycles = self.detect_cycles(graph)
        if cycles:
            results['is_valid'] = False
            results['errors'].append(f"Cycles detected: {cycles}")
        
        # Check for orphaned nodes
        orphaned = self.find_orphaned_nodes(graph)
        if orphaned:
            results['is_valid'] = False
            results['errors'].append(f"Orphaned nodes: {orphaned}")
        
        # Check for self-dependencies
        self_deps = []
        for node, deps in graph.items():
            if node in deps:
                self_deps.append(node)
        
        if self_deps:
            results['is_valid'] = False
            results['errors'].append(f"Self-dependencies detected: {self_deps}")
        
        # Calculate statistics
        all_nodes = set(graph.keys())
        for deps in graph.values():
            all_nodes.update(deps)
        
        dependency_counts = {node: len(deps) for node, deps in graph.items()}
        
        results['statistics'] = {
            'total_nodes': len(all_nodes),
            'defined_nodes': len(graph),
            'total_edges': sum(len(deps) for deps in graph.values()),
            'max_dependencies': max(dependency_counts.values()) if dependency_counts else 0,
            'avg_dependencies': sum(dependency_counts.values()) / len(dependency_counts) if dependency_counts else 0,
            'root_nodes': len([node for node, deps in graph.items() if not deps]),
            'leaf_nodes': len([node for node in graph if not any(node in deps for deps in graph.values())])
        }
        
        # Performance warnings
        if results['statistics']['max_dependencies'] > 10:
            results['warnings'].append(f"High dependency count detected: {results['statistics']['max_dependencies']}")
        
        if results['statistics']['total_nodes'] > 1000:
            results['warnings'].append(f"Large graph detected: {results['statistics']['total_nodes']} nodes")
        
        self.logger.info(
            "graph_validation_completed",
            is_valid=results['is_valid'],
            error_count=len(results['errors']),
            warning_count=len(results['warnings']),
            statistics=results['statistics']
        )
        
        return results