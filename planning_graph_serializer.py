#!/usr/bin/env python3
"""
Planning Graph Serializer
========================

Serializes planning material into a graph structure that can be loaded at runtime
for dynamic analysis, cross-referencing, and intelligent decision-making.
"""

import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import os
from pathlib import Path


class SimpleGraph:
    """Simple graph implementation without external dependencies"""
    
    def __init__(self):
        self.nodes = {}
        self.edges = []
    
    def add_node(self, node_id: str, **attributes):
        """Add a node to the graph"""
        self.nodes[node_id] = attributes
    
    def add_edge(self, source: str, target: str, **attributes):
        """Add an edge to the graph"""
        self.edges.append({
            'source': source,
            'target': target,
            **attributes
        })
    
    def has_edge(self, source: str, target: str) -> bool:
        """Check if an edge exists"""
        return any(edge['source'] == source and edge['target'] == target for edge in self.edges)
    
    def neighbors(self, node_id: str) -> List[str]:
        """Get neighbors of a node"""
        neighbors = []
        for edge in self.edges:
            if edge['source'] == node_id:
                neighbors.append(edge['target'])
            elif edge['target'] == node_id:
                neighbors.append(edge['source'])
        return neighbors


@dataclass
class PlanningNode:
    """Represents a node in the planning graph"""
    id: str
    node_type: str  # dimension, insight, scenario, constraint, mitigation, risk
    title: str
    description: str
    risk_level: Optional[str] = None
    confidence: Optional[float] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.last_updated:
            data['last_updated'] = self.last_updated.isoformat()
        return data


@dataclass
class PlanningEdge:
    """Represents an edge in the planning graph"""
    source_id: str
    target_id: str
    relationship_type: str  # depends_on, mitigates, constrains, influences, conflicts_with
    strength: float = 1.0
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)


class PlanningGraphSerializer:
    """Serializes planning material into a graph structure"""
    
    def __init__(self):
        self.graph = SimpleGraph()
        self.nodes: Dict[str, PlanningNode] = {}
        self.edges: List[PlanningEdge] = []
    
    def add_node(self, node: PlanningNode):
        """Add a node to the graph"""
        self.nodes[node.id] = node
        self.graph.add_node(
            node.id,
            **node.to_dict()
        )
    
    def add_edge(self, edge: PlanningEdge):
        """Add an edge to the graph"""
        self.edges.append(edge)
        self.graph.add_edge(
            edge.source_id,
            edge.target_id,
            **edge.to_dict()
        )
    
    def serialize_planning_memory(self, planning_memory_file: str):
        """Serialize planning memory data into graph structure"""
        with open(planning_memory_file, 'r') as f:
            data = json.load(f)
        
        context = data['current_context']
        session_id = context['session_id']
        
        # Create session node
        session_node = PlanningNode(
            id=f"session_{session_id}",
            node_type="session",
            title=f"Planning Session: {context['project_name']}",
            description=f"Planning session for {context['project_name']}",
            metadata={
                "total_dimensions": context['total_dimensions'],
                "planning_depth": context['planning_depth'],
                "planning_exhaustion_level": context['planning_exhaustion_level'],
                "total_risks": context['total_risks'],
                "total_unknowns": context['total_unknowns'],
                "total_constraints": context['total_constraints'],
                "total_mitigations": context['total_mitigations']
            },
            created_at=datetime.fromisoformat(context['created_at']),
            last_updated=datetime.fromisoformat(context['last_updated'])
        )
        self.add_node(session_node)
        
        # Process planning dimensions
        for i, dimension in enumerate(context['planning_dimensions']):
            dim_id = f"dimension_{i}_{dimension['name'].lower().replace(' ', '_')}"
            
            # Create dimension node
            dim_node = PlanningNode(
                id=dim_id,
                node_type="dimension",
                title=dimension['name'],
                description=f"Planning dimension: {dimension['name']}",
                risk_level=dimension['risk_level'],
                confidence=dimension['confidence'],
                status=dimension['status'],
                created_at=datetime.fromisoformat(dimension['last_updated']),
                last_updated=datetime.fromisoformat(dimension['last_updated']),
                metadata={
                    "unknown_factors": dimension['unknown_factors'],
                    "constraints": dimension['constraints'],
                    "mitigation_strategies": dimension['mitigation_strategies']
                }
            )
            self.add_node(dim_node)
            
            # Connect dimension to session
            self.add_edge(PlanningEdge(
                source_id=f"session_{session_id}",
                target_id=dim_id,
                relationship_type="contains",
                description="Session contains this planning dimension"
            ))
            
            # Create nodes for unknown factors
            for j, factor in enumerate(dimension['unknown_factors']):
                factor_id = f"{dim_id}_unknown_{j}"
                factor_node = PlanningNode(
                    id=factor_id,
                    node_type="unknown_factor",
                    title=f"Unknown: {factor}",
                    description=factor,
                    priority="medium",
                    metadata={"parent_dimension": dim_id}
                )
                self.add_node(factor_node)
                
                # Connect unknown factor to dimension
                self.add_edge(PlanningEdge(
                    source_id=dim_id,
                    target_id=factor_id,
                    relationship_type="has_unknown",
                    description="Dimension has this unknown factor"
                ))
            
            # Create nodes for constraints
            for j, constraint in enumerate(dimension['constraints']):
                constraint_id = f"{dim_id}_constraint_{j}"
                constraint_node = PlanningNode(
                    id=constraint_id,
                    node_type="constraint",
                    title=f"Constraint: {constraint}",
                    description=constraint,
                    priority="high",
                    metadata={"parent_dimension": dim_id}
                )
                self.add_node(constraint_node)
                
                # Connect constraint to dimension
                self.add_edge(PlanningEdge(
                    source_id=dim_id,
                    target_id=constraint_id,
                    relationship_type="has_constraint",
                    description="Dimension has this constraint"
                ))
            
            # Create nodes for mitigation strategies
            for j, strategy in enumerate(dimension['mitigation_strategies']):
                strategy_id = f"{dim_id}_mitigation_{j}"
                strategy_node = PlanningNode(
                    id=strategy_id,
                    node_type="mitigation",
                    title=f"Mitigation: {strategy}",
                    description=strategy,
                    priority="high",
                    metadata={"parent_dimension": dim_id}
                )
                self.add_node(strategy_node)
                
                # Connect mitigation to dimension
                self.add_edge(PlanningEdge(
                    source_id=dim_id,
                    target_id=strategy_id,
                    relationship_type="has_mitigation",
                    description="Dimension has this mitigation strategy"
                ))
    
    def serialize_planning_documents(self, document_dir: str = "."):
        """Serialize planning documents into graph structure"""
        planning_files = [
            "FINE_TOOTH_COMB_PLANNING_ANALYSIS.md",
            "EXHAUSTIVE_MULTI_DIMENSIONAL_PLAN.md",
            "CONTINUED_EXHAUSTIVE_PLANNING.md",
            "PLANNING_EXHAUSTION_ANALYSIS.md",
            "MULTI_DIMENSIONAL_CONTEXT_ANALYSIS.md"
        ]
        
        for filename in planning_files:
            filepath = os.path.join(document_dir, filename)
            if os.path.exists(filepath):
                self._serialize_document(filepath)
    
    def _serialize_document(self, filepath: str):
        """Serialize a single planning document"""
        with open(filepath, 'r') as f:
            content = f.read()
        
        filename = os.path.basename(filepath)
        doc_id = f"doc_{filename.lower().replace('.md', '').replace('_', '_')}"
        
        # Create document node
        doc_node = PlanningNode(
            id=doc_id,
            node_type="document",
            title=filename,
            description=f"Planning document: {filename}",
            metadata={
                "filepath": filepath,
                "content_length": len(content),
                "sections": content.count('##'),
                "subsections": content.count('###'),
                "details": content.count('####')
            },
            created_at=datetime.fromtimestamp(os.path.getctime(filepath)),
            last_updated=datetime.fromtimestamp(os.path.getmtime(filepath))
        )
        self.add_node(doc_node)
        
        # Parse sections and create nodes
        lines = content.split('\n')
        current_section = None
        current_subsection = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('## '):
                # Main section
                section_title = line[3:].strip()
                section_id = f"{doc_id}_section_{section_title.lower().replace(' ', '_').replace('*', '').replace('**', '')}"
                
                section_node = PlanningNode(
                    id=section_id,
                    node_type="section",
                    title=section_title,
                    description=f"Section: {section_title}",
                    metadata={"parent_document": doc_id}
                )
                self.add_node(section_node)
                
                # Connect section to document
                self.add_edge(PlanningEdge(
                    source_id=doc_id,
                    target_id=section_id,
                    relationship_type="contains",
                    description="Document contains this section"
                ))
                
                current_section = section_id
                current_subsection = None
                
            elif line.startswith('### ') and current_section:
                # Subsection
                subsection_title = line[4:].strip()
                subsection_id = f"{current_section}_subsection_{subsection_title.lower().replace(' ', '_').replace('*', '').replace('**', '')}"
                
                subsection_node = PlanningNode(
                    id=subsection_id,
                    node_type="subsection",
                    title=subsection_title,
                    description=f"Subsection: {subsection_title}",
                    metadata={"parent_section": current_section, "parent_document": doc_id}
                )
                self.add_node(subsection_node)
                
                # Connect subsection to section
                self.add_edge(PlanningEdge(
                    source_id=current_section,
                    target_id=subsection_id,
                    relationship_type="contains",
                    description="Section contains this subsection"
                ))
                
                current_subsection = subsection_id
    
    def create_cross_references(self):
        """Create cross-references between related nodes"""
        # Find nodes with similar titles or content
        for node_id1, node1 in self.nodes.items():
            for node_id2, node2 in self.nodes.items():
                if node_id1 >= node_id2:  # Avoid duplicate pairs
                    continue
                
                # Check for similarity
                similarity = self._calculate_similarity(node1, node2)
                if similarity > 0.7:  # High similarity threshold
                    self.add_edge(PlanningEdge(
                        source_id=node_id1,
                        target_id=node_id2,
                        relationship_type="similar_to",
                        strength=similarity,
                        description=f"Similar content (similarity: {similarity:.2f})"
                    ))
    
    def _calculate_similarity(self, node1: PlanningNode, node2: PlanningNode) -> float:
        """Calculate similarity between two nodes"""
        # Simple similarity based on title and description
        title1 = node1.title.lower()
        title2 = node2.title.lower()
        
        # Check for common words
        words1 = set(title1.split())
        words2 = set(title2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def export_graph(self, output_file: str):
        """Export the graph to a file"""
        # Convert to serializable format
        graph_data = {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges],
            "graph_metadata": {
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "node_types": list(set(node.node_type for node in self.nodes.values())),
                "relationship_types": list(set(edge.relationship_type for edge in self.edges)),
                "created_at": datetime.now().isoformat()
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(graph_data, f, indent=2)
        
        print(f"✅ Graph exported to {output_file}")
        print(f"   Nodes: {len(self.nodes)}")
        print(f"   Edges: {len(self.edges)}")
        print(f"   Node types: {graph_data['graph_metadata']['node_types']}")
        print(f"   Relationship types: {graph_data['graph_metadata']['relationship_types']}")
    
    def export_simple_graph(self, output_file: str):
        """Export as simple graph for runtime loading"""
        # Add metadata to nodes
        for node_id, node in self.nodes.items():
            self.graph.nodes[node_id].update(node.to_dict())
        
        # Add metadata to edges
        for edge in self.edges:
            if self.graph.has_edge(edge.source_id, edge.target_id):
                # Find the edge and update it
                for graph_edge in self.graph.edges:
                    if graph_edge['source'] == edge.source_id and graph_edge['target'] == edge.target_id:
                        graph_edge.update(edge.to_dict())
                        break
        
        # Export as JSON
        graph_data = {
            "nodes": self.graph.nodes,
            "edges": self.graph.edges,
            "metadata": {
                "total_nodes": len(self.graph.nodes),
                "total_edges": len(self.graph.edges),
                "exported_at": datetime.now().isoformat()
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(graph_data, f, indent=2)
        
        print(f"✅ Simple graph exported to {output_file}")


class PlanningGraphLoader:
    """Loads planning graph at runtime for analysis"""
    
    def __init__(self, graph_file: str):
        self.graph_file = graph_file
        self.graph = None
        self.nodes = {}
        self.edges = []
        self.load_graph()
    
    def load_graph(self):
        """Load the graph from file"""
        if self.graph_file.endswith('.json'):
            # Check if it's our simple graph format or the full format
            with open(self.graph_file, 'r') as f:
                data = json.load(f)
            
            if 'nodes' in data and isinstance(data['nodes'], dict):
                self._load_simple_graph()
            else:
                self._load_json_graph()
        else:
            raise ValueError("Unsupported graph format")
    
    def _load_json_graph(self):
        """Load JSON graph format"""
        with open(self.graph_file, 'r') as f:
            data = json.load(f)
        
        self.graph = SimpleGraph()
        
        # Load nodes
        for node_data in data['nodes']:
            node_id = node_data['id']
            self.nodes[node_id] = node_data
            self.graph.add_node(node_id, **node_data)
        
        # Load edges
        for edge_data in data['edges']:
            self.edges.append(edge_data)
            self.graph.add_edge(
                edge_data['source_id'],
                edge_data['target_id'],
                **edge_data
            )
    
    def _load_simple_graph(self):
        """Load simple graph JSON format"""
        with open(self.graph_file, 'r') as f:
            data = json.load(f)
        
        self.graph = SimpleGraph()
        
        # Load nodes
        for node_id, node_data in data['nodes'].items():
            self.nodes[node_id] = node_data
            self.graph.add_node(node_id, **node_data)
        
        # Load edges
        for edge_data in data['edges']:
            self.edges.append(edge_data)
            self.graph.add_edge(
                edge_data['source'],
                edge_data['target'],
                **edge_data
            )
    
    def get_related_nodes(self, node_id: str, relationship_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get nodes related to a given node"""
        related = []
        
        if relationship_type:
            # Filter by relationship type
            for edge in self.edges:
                if (edge['source_id'] == node_id or edge['target_id'] == node_id) and \
                   edge['relationship_type'] == relationship_type:
                    related_node_id = edge['target_id'] if edge['source_id'] == node_id else edge['source_id']
                    if related_node_id in self.nodes:
                        related.append({
                            'node': self.nodes[related_node_id],
                            'relationship': edge['relationship_type'],
                            'strength': edge.get('strength', 1.0)
                        })
        else:
            # Get all related nodes
            for edge in self.edges:
                if edge['source_id'] == node_id:
                    related.append({
                        'node': self.nodes[edge['target_id']],
                        'relationship': edge['relationship_type'],
                        'strength': edge.get('strength', 1.0)
                    })
                elif edge['target_id'] == node_id:
                    related.append({
                        'node': self.nodes[edge['source_id']],
                        'relationship': edge['relationship_type'],
                        'strength': edge.get('strength', 1.0)
                    })
        
        return related
    
    def find_nodes_by_type(self, node_type: str) -> List[Dict[str, Any]]:
        """Find all nodes of a specific type"""
        return [node for node in self.nodes.values() if node.get('node_type') == node_type]
    
    def find_nodes_by_risk_level(self, risk_level: str) -> List[Dict[str, Any]]:
        """Find all nodes with a specific risk level"""
        return [node for node in self.nodes.values() if node.get('risk_level') == risk_level]
    
    def get_planning_summary(self) -> Dict[str, Any]:
        """Get a summary of the planning graph"""
        node_types = {}
        risk_levels = {}
        relationship_types = {}
        
        for node in self.nodes.values():
            node_type = node.get('node_type', 'unknown')
            node_types[node_type] = node_types.get(node_type, 0) + 1
            
            risk_level = node.get('risk_level')
            if risk_level:
                risk_levels[risk_level] = risk_levels.get(risk_level, 0) + 1
        
        for edge in self.edges:
            rel_type = edge['relationship_type']
            relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1
        
        return {
            'total_nodes': len(self.nodes),
            'total_edges': len(self.edges),
            'node_types': node_types,
            'risk_levels': risk_levels,
            'relationship_types': relationship_types
        }


def main():
    """Main function to demonstrate graph serialization"""
    print("🧠 PLANNING GRAPH SERIALIZER")
    print("=" * 50)
    
    # Initialize serializer
    serializer = PlanningGraphSerializer()
    
    # Serialize planning memory
    planning_memory_file = ".planning_memory/planning_memory_planning_20250914_200132.json"
    if os.path.exists(planning_memory_file):
        print("📊 Serializing planning memory...")
        serializer.serialize_planning_memory(planning_memory_file)
    
    # Serialize planning documents
    print("📄 Serializing planning documents...")
    serializer.serialize_planning_documents()
    
    # Create cross-references
    print("🔗 Creating cross-references...")
    serializer.create_cross_references()
    
    # Export graphs
    print("💾 Exporting graphs...")
    serializer.export_graph("planning_graph.json")
    serializer.export_simple_graph("planning_simple_graph.json")
    
    # Demonstrate loading
    print("\n🔄 Demonstrating graph loading...")
    loader = PlanningGraphLoader("planning_graph.json")
    summary = loader.get_planning_summary()
    
    print(f"📊 Graph Summary:")
    print(f"   Total Nodes: {summary['total_nodes']}")
    print(f"   Total Edges: {summary['total_edges']}")
    print(f"   Node Types: {summary['node_types']}")
    print(f"   Risk Levels: {summary['risk_levels']}")
    print(f"   Relationship Types: {summary['relationship_types']}")
    
    # Example queries
    print(f"\n🔍 Example Queries:")
    
    # Find all dimensions
    dimensions = loader.find_nodes_by_type("dimension")
    print(f"   Planning Dimensions: {len(dimensions)}")
    for dim in dimensions[:3]:  # Show first 3
        print(f"     • {dim['title']} (Risk: {dim.get('risk_level', 'N/A')})")
    
    # Find critical risks
    critical_risks = loader.find_nodes_by_risk_level("critical")
    print(f"   Critical Risks: {len(critical_risks)}")
    for risk in critical_risks[:3]:  # Show first 3
        print(f"     • {risk['title']}")
    
    print("\n✅ Planning graph serialization complete!")


if __name__ == "__main__":
    main()
