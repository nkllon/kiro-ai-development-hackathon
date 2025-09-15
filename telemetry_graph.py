#!/usr/bin/env python3
"""
Telemetry Graph - Graph-based persistence for expensive DevPost telemetry data
"""

import json
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Simple graph implementation without networkx dependency
class SimpleGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}
    
    def add_node(self, node_id, **data):
        self.nodes[node_id] = data
    
    def add_edge(self, source, target, **data):
        if source not in self.edges:
            self.edges[source] = {}
        self.edges[source][target] = data
    
    def has_edge(self, source, target):
        return source in self.edges and target in self.edges[source]
    
    def nodes(self, data=False):
        if data:
            return self.nodes.items()
        return self.nodes.keys()
    
    def edges(self, data=False):
        result = []
        for source, targets in self.edges.items():
            for target, edge_data in targets.items():
                if data:
                    result.append((source, target, edge_data))
                else:
                    result.append((source, target))
        return result


@dataclass
class PageNode:
    """Represents a page in the telemetry graph"""
    url: str
    title: str
    page_type: str
    timestamp: str
    hash: str
    
    # Navigation data
    navigation_elements: List[Dict[str, Any]]
    step_sequence: List[str]
    current_step: str
    
    # Form data
    form_fields: List[Dict[str, Any]]
    form_status: str
    
    # Content analysis
    total_elements: int
    interactive_elements: List[Dict[str, Any]]
    dom_structure: Dict[str, Any]
    
    # Performance metrics
    load_time: Optional[float] = None
    element_count: Optional[int] = None
    
    # Visual data
    screenshot: Optional[str] = None
    visual_hash: Optional[str] = None


@dataclass
class NavigationEdge:
    """Represents navigation between pages"""
    source_hash: str
    target_hash: str
    navigation_method: str  # 'click', 'form_submit', 'direct'
    timestamp: str
    success: bool
    error_message: Optional[str] = None


class TelemetryGraph:
    """Graph-based persistence for DevPost telemetry data"""
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or f"telemetry_session_{int(time.time())}"
        self.graph = SimpleGraph()
        self.current_page_hash = None
        self.session_start = datetime.now().isoformat()
        
        # Persistence files
        self.graph_file = f"telemetry_graph_{self.session_id}.json"
        self.raw_data_file = f"telemetry_raw_{self.session_id}.jsonl"
        
        # Load existing data if available
        self.load_graph()
    
    def _generate_page_hash(self, url: str, timestamp: str) -> str:
        """Generate unique hash for page state"""
        content = f"{url}:{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def add_page_telemetry(self, page_data: Dict[str, Any]) -> str:
        """Add comprehensive page telemetry to the graph"""
        timestamp = datetime.now().isoformat()
        page_hash = self._generate_page_hash(page_data['url'], timestamp)
        
        # Create page node
        page_node = PageNode(
            url=page_data['url'],
            title=page_data['title'],
            page_type=page_data.get('page_type', 'unknown'),
            timestamp=timestamp,
            hash=page_hash,
            navigation_elements=page_data.get('navigationElements', []),
            step_sequence=page_data.get('step_sequence', []),
            current_step=page_data.get('current_step', 'unknown'),
            form_fields=page_data.get('formElements', []),
            form_status=page_data.get('form_status', 'unknown'),
            total_elements=page_data.get('totalElements', 0),
            interactive_elements=page_data.get('interactiveElements', []),
            dom_structure=page_data.get('dom_structure', {}),
            load_time=page_data.get('load_time'),
            element_count=page_data.get('totalElements'),
            screenshot=page_data.get('screenshot'),
            visual_hash=page_data.get('visual_hash')
        )
        
        # Add node to graph
        self.graph.add_node(page_hash, **asdict(page_node))
        
        # Add navigation edge if we have a previous page
        if self.current_page_hash:
            self.add_navigation_edge(
                self.current_page_hash,
                page_hash,
                "page_navigation",
                True
            )
        
        self.current_page_hash = page_hash
        
        # Save raw data to JSONL for detailed analysis
        self._save_raw_telemetry(page_data, page_hash)
        
        # Auto-save graph
        self.save_graph()
        
        return page_hash
    
    def add_navigation_edge(self, source_hash: str, target_hash: str, 
                           method: str, success: bool, error: str = None):
        """Add navigation edge to graph"""
        edge = NavigationEdge(
            source_hash=source_hash,
            target_hash=target_hash,
            navigation_method=method,
            timestamp=datetime.now().isoformat(),
            success=success,
            error_message=error
        )
        
        self.graph.add_edge(source_hash, target_hash, **asdict(edge))
    
    def _save_raw_telemetry(self, page_data: Dict[str, Any], page_hash: str):
        """Save raw telemetry data to JSONL for detailed analysis"""
        raw_entry = {
            "session_id": self.session_id,
            "page_hash": page_hash,
            "timestamp": datetime.now().isoformat(),
            "data": page_data
        }
        
        with open(self.raw_data_file, 'a') as f:
            f.write(json.dumps(raw_entry) + '\n')
    
    def save_graph(self):
        """Save graph to file"""
        graph_data = {
            "session_id": self.session_id,
            "session_start": self.session_start,
            "current_page_hash": self.current_page_hash,
            "nodes": dict(self.graph.nodes(data=True)),
            "edges": [(u, v, d) for u, v, d in self.graph.edges(data=True)],
            "statistics": {
                "total_pages": len(self.graph.nodes),
                "total_navigations": len(self.graph.edges),
                "session_duration": self._get_session_duration()
            }
        }
        
        with open(self.graph_file, 'w') as f:
            json.dump(graph_data, f, indent=2)
        
        print(f"💾 Telemetry graph saved: {len(self.graph.nodes)} pages, {len(self.graph.edges)} navigations")
    
    def load_graph(self):
        """Load graph from file"""
        try:
            with open(self.graph_file, 'r') as f:
                graph_data = json.load(f)
            
            # Reconstruct graph
            for node_id, node_data in graph_data.get('nodes', {}).items():
                self.graph.add_node(node_id, **node_data)
            
            for source, target, edge_data in graph_data.get('edges', []):
                self.graph.add_edge(source, target, **edge_data)
            
            self.current_page_hash = graph_data.get('current_page_hash')
            
            print(f"📊 Loaded telemetry graph: {len(self.graph.nodes)} pages, {len(self.graph.edges)} navigations")
            
        except FileNotFoundError:
            print("🆕 Starting new telemetry graph")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get comprehensive session summary"""
        if not self.graph.nodes:
            return {"error": "No telemetry data collected"}
        
        # Calculate statistics
        successful_navigations = sum(1 for _, _, data in self.graph.edges(data=True) 
                                   if data.get('success', False))
        failed_navigations = len(self.graph.edges) - successful_navigations
        
        # Get page types visited
        page_types = {}
        for _, data in self.graph.nodes(data=True):
            page_type = data.get('page_type', 'unknown')
            page_types[page_type] = page_types.get(page_type, 0) + 1
        
        # Get navigation paths
        navigation_paths = []
        if len(self.graph.nodes) > 1:
            try:
                # Find all simple paths
                nodes = list(self.graph.nodes())
                for source in nodes:
                    for target in nodes:
                        if source != target and self.graph.has_edge(source, target):
                            path_data = {
                                "source": source,
                                "target": target,
                                "method": self.graph.edges[source, target].get('navigation_method', 'unknown')
                            }
                            navigation_paths.append(path_data)
            except:
                pass
        
        return {
            "session_id": self.session_id,
            "session_duration": self._get_session_duration(),
            "total_pages_visited": len(self.graph.nodes),
            "total_navigations": len(self.graph.edges),
            "successful_navigations": successful_navigations,
            "failed_navigations": failed_navigations,
            "success_rate": (successful_navigations / max(len(self.graph.edges), 1)) * 100,
            "page_types_visited": page_types,
            "navigation_paths": navigation_paths,
            "current_page": self.current_page_hash,
            "raw_data_file": self.raw_data_file,
            "graph_file": self.graph_file
        }
    
    def _get_session_duration(self) -> str:
        """Calculate session duration"""
        try:
            start_time = datetime.fromisoformat(self.session_start)
            duration = datetime.now() - start_time
            return str(duration).split('.')[0]  # Remove microseconds
        except:
            return "unknown"
    
    def has_changes(self) -> bool:
        """Check if session has any changes worth saving"""
        return len(self.graph.nodes) > 0 or len(self.graph.edges) > 0
    
    def export_for_analysis(self) -> str:
        """Export comprehensive data for analysis"""
        export_file = f"telemetry_export_{self.session_id}_{int(time.time())}.json"
        
        export_data = {
            "session_summary": self.get_session_summary(),
            "graph_structure": {
                "nodes": list(self.graph.nodes(data=True)),
                "edges": [(u, v, d) for u, v, d in self.graph.edges(data=True)]
            },
            "export_timestamp": datetime.now().isoformat(),
            "files": {
                "graph_file": self.graph_file,
                "raw_data_file": self.raw_data_file
            }
        }
        
        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"📤 Telemetry exported for analysis: {export_file}")
        return export_file


def create_telemetry_graph(session_id: str = None) -> TelemetryGraph:
    """Create a new telemetry graph instance"""
    return TelemetryGraph(session_id)


if __name__ == "__main__":
    # Test the telemetry graph
    graph = create_telemetry_graph()
    print("✅ Telemetry Graph created successfully")
    print(f"📁 Graph file: {graph.graph_file}")
    print(f"📁 Raw data file: {graph.raw_data_file}")
    print(graph.get_session_summary())
