"""
Cross-Dimensional Navigator - Navigate across 20+ dimensions
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from ..indexing.multi_dimensional_indexer import MultiDimensionalIndexer, IndexResult, NavigationResult


@dataclass
class NavigationPath:
    """Path through dimensional navigation"""
    start_dimension: str
    target_dimension: str
    path: List[str]
    total_steps: int
    confidence: float
    estimated_time_ms: float


@dataclass
class NavigationMap:
    """Comprehensive navigation map"""
    dimensions: List[str]
    relationships: List[Dict[str, Any]]
    shortest_paths: Dict[str, Dict[str, List[str]]]
    navigation_graph: Dict[str, Any]
    performance_metrics: Dict[str, Any]


class CrossDimensionalNavigator:
    """Navigate across 20+ dimensions with intelligent routing"""
    
    def __init__(self, indexer: MultiDimensionalIndexer):
        self.indexer = indexer
        self.navigation_graph = {}
        self.shortest_paths = {}
        self.performance_cache = {}
    
    def navigate(self, start_point: str, target_dimension: str) -> NavigationPath:
        """Navigate from start point to target dimension"""
        start_time = datetime.now()
        
        try:
            # Build navigation graph if not exists
            if not self.navigation_graph:
                self._build_navigation_graph()
            
            # Find shortest path
            path = self._find_shortest_path(start_point, target_dimension)
            
            # Calculate path metrics
            total_steps = len(path)
            confidence = self._calculate_path_confidence(path)
            
            # Estimate navigation time
            end_time = datetime.now()
            estimated_time = (end_time - start_time).total_seconds() * 1000
            
            return NavigationPath(
                start_dimension=start_point,
                target_dimension=target_dimension,
                path=path,
                total_steps=total_steps,
                confidence=confidence,
                estimated_time_ms=estimated_time
            )
            
        except Exception as e:
            print(f"Navigation error: {e}")
            return NavigationPath(
                start_dimension=start_point,
                target_dimension=target_dimension,
                path=[],
                total_steps=0,
                confidence=0.0,
                estimated_time_ms=0.0
            )
    
    def generate_navigation_map(self) -> NavigationMap:
        """Generate comprehensive navigation map"""
        try:
            # Build complete navigation graph
            self._build_navigation_graph()
            
            # Calculate shortest paths between all dimensions
            self._calculate_all_shortest_paths()
            
            # Get performance metrics
            performance_metrics = self._calculate_navigation_performance()
            
            return NavigationMap(
                dimensions=list(self.indexer.dimensions.keys()),
                relationships=self.indexer.cross_dimensional_relationships,
                shortest_paths=self.shortest_paths,
                navigation_graph=self.navigation_graph,
                performance_metrics=performance_metrics
            )
            
        except Exception as e:
            print(f"Error generating navigation map: {e}")
            return NavigationMap(
                dimensions=[],
                relationships=[],
                shortest_paths={},
                navigation_graph={},
                performance_metrics={}
            )
    
    def _build_navigation_graph(self) -> None:
        """Build navigation graph from dimensional relationships"""
        self.navigation_graph = {}
        
        # Initialize graph with all dimensions
        for dim_name in self.indexer.dimensions.keys():
            self.navigation_graph[dim_name] = {
                "neighbors": [],
                "weights": {},
                "attributes": {}
            }
        
        # Add relationships as edges
        for relationship in self.indexer.cross_dimensional_relationships:
            source = relationship["source_dimension"]
            target = relationship["target_dimension"]
            strength = relationship["strength"]
            
            if source in self.navigation_graph and target in self.navigation_graph:
                # Add bidirectional edges
                self.navigation_graph[source]["neighbors"].append(target)
                self.navigation_graph[source]["weights"][target] = strength
                
                self.navigation_graph[target]["neighbors"].append(source)
                self.navigation_graph[target]["weights"][source] = strength
        
        # Add additional logical connections
        self._add_logical_connections()
    
    def _add_logical_connections(self) -> None:
        """Add logical connections between related dimensions"""
        logical_connections = {
            "temporal": ["quality", "performance"],
            "spatial": ["structural", "architecture"],
            "semantic": ["audience", "document_type"],
            "quality": ["performance", "governance"],
            "security": ["governance", "compliance"],
            "technology": ["dependency", "architecture"],
            "process": ["lifecycle", "maintenance"],
            "audience": ["urgency", "governance"]
        }
        
        for source, targets in logical_connections.items():
            if source in self.navigation_graph:
                for target in targets:
                    if target in self.navigation_graph:
                        if target not in self.navigation_graph[source]["neighbors"]:
                            self.navigation_graph[source]["neighbors"].append(target)
                            self.navigation_graph[source]["weights"][target] = 0.6  # Default logical weight
    
    def _find_shortest_path(self, start: str, target: str) -> List[str]:
        """Find shortest path between dimensions using Dijkstra's algorithm"""
        if start == target:
            return [start]
        
        if start not in self.navigation_graph or target not in self.navigation_graph:
            return []
        
        # Initialize distances and previous nodes
        distances = {dim: float('infinity') for dim in self.navigation_graph.keys()}
        previous = {dim: None for dim in self.navigation_graph.keys()}
        distances[start] = 0
        
        # Unvisited nodes
        unvisited = set(self.navigation_graph.keys())
        
        while unvisited:
            # Find unvisited node with minimum distance
            current = min(unvisited, key=lambda node: distances[node])
            unvisited.remove(current)
            
            # If we reached the target, reconstruct path
            if current == target:
                path = []
                while current is not None:
                    path.append(current)
                    current = previous[current]
                return path[::-1]
            
            # Update distances to neighbors
            for neighbor in self.navigation_graph[current]["neighbors"]:
                if neighbor in unvisited:
                    weight = self.navigation_graph[current]["weights"].get(neighbor, 1.0)
                    # Use inverse of weight as distance (higher weight = shorter distance)
                    distance = distances[current] + (1.0 / weight)
                    
                    if distance < distances[neighbor]:
                        distances[neighbor] = distance
                        previous[neighbor] = current
        
        return []  # No path found
    
    def _calculate_all_shortest_paths(self) -> None:
        """Calculate shortest paths between all dimension pairs"""
        self.shortest_paths = {}
        
        dimensions = list(self.indexer.dimensions.keys())
        
        for start in dimensions:
            self.shortest_paths[start] = {}
            for target in dimensions:
                if start != target:
                    path = self._find_shortest_path(start, target)
                    self.shortest_paths[start][target] = path
    
    def _calculate_path_confidence(self, path: List[str]) -> float:
        """Calculate confidence in navigation path"""
        if len(path) < 2:
            return 1.0
        
        total_confidence = 0.0
        for i in range(len(path) - 1):
            current = path[i]
            next_dim = path[i + 1]
            
            if (current in self.navigation_graph and 
                next_dim in self.navigation_graph[current]["weights"]):
                weight = self.navigation_graph[current]["weights"][next_dim]
                total_confidence += weight
            else:
                total_confidence += 0.5  # Default confidence
        
        return min(1.0, total_confidence / (len(path) - 1))
    
    def _calculate_navigation_performance(self) -> Dict[str, Any]:
        """Calculate navigation performance metrics"""
        total_paths = 0
        total_length = 0
        successful_paths = 0
        
        for start, targets in self.shortest_paths.items():
            for target, path in targets.items():
                if path:
                    successful_paths += 1
                    total_length += len(path)
                total_paths += 1
        
        avg_path_length = total_length / successful_paths if successful_paths > 0 else 0
        success_rate = successful_paths / total_paths if total_paths > 0 else 0
        
        return {
            "total_dimensions": len(self.indexer.dimensions),
            "total_paths": total_paths,
            "successful_paths": successful_paths,
            "success_rate": success_rate,
            "average_path_length": avg_path_length,
            "navigation_efficiency": success_rate * (1.0 / (avg_path_length + 1)),
            "graph_connectivity": self._calculate_graph_connectivity()
        }
    
    def _calculate_graph_connectivity(self) -> float:
        """Calculate graph connectivity score"""
        if not self.navigation_graph:
            return 0.0
        
        total_possible_edges = len(self.navigation_graph) * (len(self.navigation_graph) - 1) / 2
        actual_edges = 0
        
        for node, data in self.navigation_graph.items():
            actual_edges += len(data["neighbors"])
        
        # Divide by 2 because we count each edge twice (bidirectional)
        actual_edges = actual_edges / 2
        
        return actual_edges / total_possible_edges if total_possible_edges > 0 else 0.0
    
    def get_dimension_info(self, dimension: str) -> Dict[str, Any]:
        """Get information about a specific dimension"""
        if dimension not in self.indexer.dimensions:
            return {}
        
        dim_obj = self.indexer.dimensions[dimension]
        graph_info = self.navigation_graph.get(dimension, {})
        
        return {
            "name": dimension,
            "type": type(dim_obj).__name__,
            "neighbors": graph_info.get("neighbors", []),
            "connection_count": len(graph_info.get("neighbors", [])),
            "centrality_score": self._calculate_centrality_score(dimension),
            "usage_frequency": self._calculate_usage_frequency(dimension)
        }
    
    def _calculate_centrality_score(self, dimension: str) -> float:
        """Calculate centrality score for a dimension"""
        if dimension not in self.navigation_graph:
            return 0.0
        
        # Simple degree centrality
        neighbors = self.navigation_graph[dimension]["neighbors"]
        total_dimensions = len(self.navigation_graph)
        
        return len(neighbors) / (total_dimensions - 1) if total_dimensions > 1 else 0.0
    
    def _calculate_usage_frequency(self, dimension: str) -> float:
        """Calculate usage frequency for a dimension"""
        if dimension not in self.indexer.indexes:
            return 0.0
        
        index = self.indexer.indexes[dimension]
        total_values = index.get("total_values", 0)
        
        # Normalize by total possible values (simplified)
        return min(1.0, total_values / 100.0)
