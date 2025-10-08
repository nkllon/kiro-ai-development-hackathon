#!/usr/bin/env python3
"""
RC1 DAG Builder
===============

Implements the DAG Organization Engine for building hierarchical document
organization and resolving dependencies.

Part of the Beast Mode parallel execution orchestration.
"""

import json
import networkx as nx
from pathlib import Path
from typing import List, Dict, Any, Set, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class DocumentNode:
    """Node in the document DAG"""
    path: str
    filename: str
    category: str
    dependencies: List[str]
    dependents: List[str]
    level: int
    position: int
    metadata: Dict[str, Any]


@dataclass
class DocumentDAG:
    """Document DAG structure"""
    nodes: Dict[str, DocumentNode]
    edges: List[Tuple[str, str]]
    levels: Dict[int, List[str]]
    root_nodes: List[str]
    leaf_nodes: List[str]
    cycles: List[List[str]]
    metadata: Dict[str, Any]


@dataclass
class HierarchyLevel:
    """Level in the document hierarchy"""
    level: int
    name: str
    documents: List[str]
    parent_level: Optional[int]
    child_levels: List[int]


class DAGBuilder:
    """
    DAG Organization Engine
    
    Builds hierarchical document organization using DAG principles.
    Part of the Beast Mode parallel execution system.
    """
    
    def __init__(self, analysis_results_path: str = "rc1_content_analysis.json"):
        self.analysis_results_path = Path(analysis_results_path)
        self.content_analyses = []
        self.dependency_graph = {}
        self.document_dag = None
        
    def load_analysis_results(self) -> bool:
        """Load content analysis results"""
        if not self.analysis_results_path.exists():
            print(f"❌ Analysis results not found: {self.analysis_results_path}")
            return False
            
        try:
            with open(self.analysis_results_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.content_analyses = data.get('content_analyses', [])
                self.dependency_graph = data.get('dependency_graph', {})
                print(f"📄 Loaded {len(self.content_analyses)} content analyses")
                print(f"🔗 Loaded dependency graph with {len(self.dependency_graph)} documents")
                return True
        except Exception as e:
            print(f"❌ Error loading analysis results: {e}")
            return False
    
    def build_document_hierarchy(self) -> DocumentDAG:
        """Build hierarchical document DAG"""
        if not self.content_analyses:
            print("⚠️ No content analyses available. Run load_analysis_results() first.")
            return None
        
        print("🏗️ Building document hierarchy...")
        
        # Create NetworkX graph for DAG operations
        G = nx.DiGraph()
        
        # Add nodes
        for analysis in self.content_analyses:
            G.add_node(analysis['document_path'])
        
        # Add edges based on dependencies
        for doc_path, dependencies in self.dependency_graph.items():
            for dep in dependencies:
                if dep in G.nodes and dep != doc_path:
                    G.add_edge(dep, doc_path)  # dependency -> document
        
        # Detect cycles
        cycles = list(nx.simple_cycles(G))
        if cycles:
            print(f"⚠️ Detected {len(cycles)} cycles in dependency graph")
            # Remove edges to break cycles (simplified approach)
            G = self._break_cycles(G, cycles)
        
        # Build hierarchy levels using topological sort
        try:
            topo_order = list(nx.topological_sort(G))
            levels = self._assign_levels(G, topo_order)
        except nx.NetworkXError:
            print("⚠️ Graph still has cycles, using fallback level assignment")
            levels = self._fallback_level_assignment(G)
        
        # Create document nodes
        nodes = {}
        for doc_path in G.nodes():
            analysis = self._find_analysis_by_path(doc_path)
            if analysis:
                node = DocumentNode(
                    path=doc_path,
                    filename=Path(doc_path).name,
                    category=self._categorize_document(doc_path),
                    dependencies=list(G.predecessors(doc_path)),
                    dependents=list(G.successors(doc_path)),
                    level=levels.get(doc_path, 0),
                    position=topo_order.index(doc_path) if doc_path in topo_order else 0,
                    metadata=analysis
                )
                nodes[doc_path] = node
        
        # Create DAG structure
        self.document_dag = DocumentDAG(
            nodes=nodes,
            edges=list(G.edges()),
            levels=self._group_by_levels(levels),
            root_nodes=[node for node in G.nodes() if G.in_degree(node) == 0],
            leaf_nodes=[node for node in G.nodes() if G.out_degree(node) == 0],
            cycles=cycles,
            metadata={
                "total_documents": len(nodes),
                "total_dependencies": len(G.edges()),
                "max_level": max(levels.values()) if levels else 0,
                "build_timestamp": datetime.now().isoformat()
            }
        )
        
        print(f"✅ Document hierarchy built:")
        print(f"   Documents: {len(nodes)}")
        print(f"   Dependencies: {len(G.edges())}")
        print(f"   Levels: {len(self.document_dag.levels)}")
        print(f"   Root nodes: {len(self.document_dag.root_nodes)}")
        print(f"   Leaf nodes: {len(self.document_dag.leaf_nodes)}")
        
        return self.document_dag
    
    def _find_analysis_by_path(self, doc_path: str) -> Optional[Dict[str, Any]]:
        """Find content analysis by document path"""
        for analysis in self.content_analyses:
            if analysis['document_path'] == doc_path:
                return analysis
        return None
    
    def _categorize_document(self, doc_path: str) -> str:
        """Categorize document by path and filename"""
        filename = Path(doc_path).name.lower()
        
        if filename.startswith('rc1_'):
            return 'rc1_planning'
        elif 'readme' in filename:
            return 'readme'
        elif 'task' in filename:
            return 'task'
        elif 'summary' in filename:
            return 'summary'
        elif 'test' in filename:
            return 'test'
        elif 'spec' in filename:
            return 'specification'
        elif 'requirements' in filename:
            return 'requirements'
        elif 'implementation' in filename:
            return 'implementation'
        elif 'docs/' in doc_path:
            return 'documentation'
        elif 'src/' in doc_path:
            return 'source_code'
        else:
            return 'other'
    
    def _break_cycles(self, G: nx.DiGraph, cycles: List[List[str]]) -> nx.DiGraph:
        """Break cycles in the dependency graph"""
        edges_to_remove = set()
        
        for cycle in cycles:
            # Remove the edge with lowest priority (simplified)
            if len(cycle) > 1:
                # Remove edge from last to first node in cycle
                edges_to_remove.add((cycle[-1], cycle[0]))
        
        G.remove_edges_from(edges_to_remove)
        print(f"🔧 Removed {len(edges_to_remove)} edges to break cycles")
        return G
    
    def _assign_levels(self, G: nx.DiGraph, topo_order: List[str]) -> Dict[str, int]:
        """Assign hierarchy levels using topological order"""
        levels = {}
        
        for node in topo_order:
            predecessors = list(G.predecessors(node))
            if not predecessors:
                levels[node] = 0
            else:
                max_pred_level = max(levels.get(pred, 0) for pred in predecessors)
                levels[node] = max_pred_level + 1
        
        return levels
    
    def _fallback_level_assignment(self, G: nx.DiGraph) -> Dict[str, int]:
        """Fallback level assignment when topological sort fails"""
        levels = {}
        
        # Start with nodes that have no predecessors
        current_level = 0
        remaining = set(G.nodes())
        
        while remaining:
            level_nodes = [node for node in remaining if not any(pred in remaining for pred in G.predecessors(node))]
            
            if not level_nodes:
                # If no nodes can be assigned, assign remaining nodes to current level
                level_nodes = list(remaining)
            
            for node in level_nodes:
                levels[node] = current_level
            
            remaining -= set(level_nodes)
            current_level += 1
        
        return levels
    
    def _group_by_levels(self, levels: Dict[str, int]) -> Dict[int, List[str]]:
        """Group documents by hierarchy level"""
        level_groups = {}
        for doc_path, level in levels.items():
            if level not in level_groups:
                level_groups[level] = []
            level_groups[level].append(doc_path)
        
        return level_groups
    
    def generate_navigation_structure(self) -> Dict[str, Any]:
        """Generate navigation structure from DAG"""
        if not self.document_dag:
            print("⚠️ No document DAG available. Run build_document_hierarchy() first.")
            return {}
        
        print("🧭 Generating navigation structure...")
        
        navigation = {
            "hierarchy_levels": [],
            "category_groups": {},
            "dependency_chains": [],
            "navigation_paths": [],
            "metadata": {
                "generation_timestamp": datetime.now().isoformat(),
                "total_levels": len(self.document_dag.levels),
                "total_documents": len(self.document_dag.nodes)
            }
        }
        
        # Generate hierarchy levels
        for level_num in sorted(self.document_dag.levels.keys()):
            level_docs = self.document_dag.levels[level_num]
            level_info = {
                "level": level_num,
                "name": f"Level {level_num}",
                "document_count": len(level_docs),
                "documents": level_docs
            }
            navigation["hierarchy_levels"].append(level_info)
        
        # Generate category groups
        categories = {}
        for doc_path, node in self.document_dag.nodes.items():
            category = node.category
            if category not in categories:
                categories[category] = []
            categories[category].append(doc_path)
        
        navigation["category_groups"] = categories
        
        # Generate dependency chains (simplified)
        for root in self.document_dag.root_nodes:
            chain = self._build_dependency_chain(root)
            if chain:
                navigation["dependency_chains"].append(chain)
        
        # Generate navigation paths
        navigation["navigation_paths"] = self._generate_navigation_paths()
        
        print(f"✅ Navigation structure generated:")
        print(f"   Hierarchy levels: {len(navigation['hierarchy_levels'])}")
        print(f"   Category groups: {len(navigation['category_groups'])}")
        print(f"   Dependency chains: {len(navigation['dependency_chains'])}")
        print(f"   Navigation paths: {len(navigation['navigation_paths'])}")
        
        return navigation
    
    def _build_dependency_chain(self, root_path: str, max_depth: int = 5) -> List[str]:
        """Build dependency chain starting from root"""
        if not self.document_dag:
            return []
        
        chain = [root_path]
        current = root_path
        depth = 0
        
        while depth < max_depth:
            node = self.document_dag.nodes.get(current)
            if not node or not node.dependents:
                break
            
            # Take first dependent (simplified)
            next_doc = node.dependents[0]
            if next_doc in chain:  # Avoid cycles
                break
            
            chain.append(next_doc)
            current = next_doc
            depth += 1
        
        return chain
    
    def _generate_navigation_paths(self) -> List[Dict[str, Any]]:
        """Generate navigation paths through the document hierarchy"""
        if not self.document_dag:
            return []
        
        paths = []
        
        # Create paths from root to leaf nodes
        for root in self.document_dag.root_nodes:
            for leaf in self.document_dag.leaf_nodes:
                path = self._find_path(root, leaf)
                if path:
                    paths.append({
                        "path_id": f"path_{root}_{leaf}",
                        "start": root,
                        "end": leaf,
                        "documents": path,
                        "length": len(path)
                    })
        
        # Create category-based paths
        for category, docs in self._group_by_category().items():
            if len(docs) > 1:
                paths.append({
                    "path_id": f"category_{category}",
                    "type": "category",
                    "category": category,
                    "documents": docs,
                    "length": len(docs)
                })
        
        return paths
    
    def _find_path(self, start: str, end: str) -> Optional[List[str]]:
        """Find path between two documents"""
        if not self.document_dag:
            return None
        
        # Simple BFS path finding
        queue = [(start, [start])]
        visited = {start}
        
        while queue:
            current, path = queue.pop(0)
            
            if current == end:
                return path
            
            node = self.document_dag.nodes.get(current)
            if node:
                for dependent in node.dependents:
                    if dependent not in visited:
                        visited.add(dependent)
                        queue.append((dependent, path + [dependent]))
        
        return None
    
    def _group_by_category(self) -> Dict[str, List[str]]:
        """Group documents by category"""
        categories = {}
        for doc_path, node in self.document_dag.nodes.items():
            category = node.category
            if category not in categories:
                categories[category] = []
            categories[category].append(doc_path)
        return categories
    
    def optimize_dag_structure(self) -> DocumentDAG:
        """Optimize DAG structure for better organization"""
        if not self.document_dag:
            print("⚠️ No document DAG available. Run build_document_hierarchy() first.")
            return None
        
        print("⚡ Optimizing DAG structure...")
        
        # Create optimized copy
        optimized_dag = self.document_dag
        
        # Optimize level assignment
        optimized_dag = self._optimize_levels(optimized_dag)
        
        # Optimize category grouping
        optimized_dag = self._optimize_categories(optimized_dag)
        
        # Update metadata
        optimized_dag.metadata.update({
            "optimization_timestamp": datetime.now().isoformat(),
            "optimized": True
        })
        
        print("✅ DAG structure optimized")
        return optimized_dag
    
    def _optimize_levels(self, dag: DocumentDAG) -> DocumentDAG:
        """Optimize hierarchy level assignment"""
        # Simple optimization: balance level sizes
        level_sizes = {level: len(docs) for level, docs in dag.levels.items()}
        
        # If any level is too large (>50 docs), split it
        for level, docs in list(dag.levels.items()):
            if len(docs) > 50:
                # Split large level
                mid_point = len(docs) // 2
                docs1 = docs[:mid_point]
                docs2 = docs[mid_point:]
                
                # Update level assignments
                new_level = max(dag.levels.keys()) + 1
                dag.levels[level] = docs1
                dag.levels[new_level] = docs2
                
                # Update node levels
                for doc in docs2:
                    if doc in dag.nodes:
                        dag.nodes[doc].level = new_level
        
        return dag
    
    def _optimize_categories(self, dag: DocumentDAG) -> DocumentDAG:
        """Optimize document categorization"""
        # Simple optimization: merge small categories
        category_counts = {}
        for node in dag.nodes.values():
            category_counts[node.category] = category_counts.get(node.category, 0) + 1
        
        # Merge categories with <3 documents into 'other'
        for node in dag.nodes.values():
            if category_counts[node.category] < 3:
                node.category = 'other'
        
        return dag
    
    def save_dag_results(self, output_path: str = "rc1_dag_structure.json") -> None:
        """Save DAG results to JSON file"""
        if not self.document_dag:
            print("⚠️ No DAG results to save. Run build_document_hierarchy() first.")
            return
        
        # Convert to serializable format
        dag_data = {
            "nodes": {path: asdict(node) for path, node in self.document_dag.nodes.items()},
            "edges": self.document_dag.edges,
            "levels": self.document_dag.levels,
            "root_nodes": self.document_dag.root_nodes,
            "leaf_nodes": self.document_dag.leaf_nodes,
            "cycles": self.document_dag.cycles,
            "metadata": self.document_dag.metadata
        }
        
        results_data = {
            "dag_structure": dag_data,
            "navigation_structure": self.generate_navigation_structure(),
            "export_timestamp": datetime.now().isoformat()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 DAG results saved to: {output_path}")


def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="RC1 DAG Builder")
    parser.add_argument("--input", default="rc1_content_analysis.json", help="Input analysis results file")
    parser.add_argument("--output", default="rc1_dag_structure.json", help="Output DAG structure file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Initialize DAG builder
    builder = DAGBuilder(args.input)
    
    # Load analysis results
    if not builder.load_analysis_results():
        return
    
    # Build document hierarchy
    dag = builder.build_document_hierarchy()
    
    if dag:
        # Optimize structure
        optimized_dag = builder.optimize_dag_structure()
        
        # Save results
        builder.save_dag_results(args.output)
        
        # Print summary
        if args.verbose:
            print(f"\n📊 DAG Structure Summary:")
            print(f"   Total Documents: {len(dag.nodes)}")
            print(f"   Total Dependencies: {len(dag.edges)}")
            print(f"   Hierarchy Levels: {len(dag.levels)}")
            print(f"   Root Documents: {len(dag.root_nodes)}")
            print(f"   Leaf Documents: {len(dag.leaf_nodes)}")


if __name__ == "__main__":
    main()
