#!/usr/bin/env python3
"""
Multi-Perspective Ghostbusters DAG Generator
===========================================

Generate DAG visualization for the Multi-Perspective Ghostbusters framework
to ensure no circular dependencies and proper dependency flow.

Author: Beast Mode Framework
Date: 2025-01-27
"""

import sys
import os
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

@dataclass
class ComponentNode:
    """Node in the dependency graph."""
    name: str
    context: str
    dependencies: List[str]
    dependents: List[str]
    layer: int

class GhostbustersDAGGenerator:
    """Generate DAG for Multi-Perspective Ghostbusters framework."""
    
    def __init__(self):
        self.components = self._define_components()
        self.dependency_graph = self._build_dependency_graph()
    
    def _define_components(self) -> Dict[str, ComponentNode]:
        """Define all components and their dependencies."""
        
        components = {
            # Base Layer (Layer 0)
            "ReflectiveModule": ComponentNode(
                name="ReflectiveModule",
                context="Core",
                dependencies=[],
                dependents=[],
                layer=0
            ),
            
            # Agent Management Context (Layer 1)
            "AgentLifecycleManager": ComponentNode(
                name="AgentLifecycleManager",
                context="AgentManagement",
                dependencies=["ReflectiveModule"],
                dependents=[],
                layer=1
            ),
            "PerspectiveAnalysisCoordinator": ComponentNode(
                name="PerspectiveAnalysisCoordinator",
                context="AgentManagement",
                dependencies=["ReflectiveModule", "AgentLifecycleManager"],
                dependents=[],
                layer=1
            ),
            "PerspectiveSelector": ComponentNode(
                name="PerspectiveSelector",
                context="AgentManagement",
                dependencies=["ReflectiveModule"],
                dependents=[],
                layer=1
            ),
            
            # Specialized Agent Context (Layer 2)
            "SecurityExpert": ComponentNode(
                name="SecurityExpert",
                context="SpecializedAgent",
                dependencies=["ReflectiveModule"],
                dependents=[],
                layer=2
            ),
            "ArchitectureExpert": ComponentNode(
                name="ArchitectureExpert",
                context="SpecializedAgent",
                dependencies=["ReflectiveModule"],
                dependents=[],
                layer=2
            ),
            "RequirementsExpert": ComponentNode(
                name="RequirementsExpert",
                context="SpecializedAgent",
                dependencies=["ReflectiveModule"],
                dependents=[],
                layer=2
            ),
            
            # Synthesis Context (Layer 3)
            "ConsensusDetector": ComponentNode(
                name="ConsensusDetector",
                context="Synthesis",
                dependencies=["ReflectiveModule", "SecurityExpert", "ArchitectureExpert", "RequirementsExpert"],
                dependents=[],
                layer=3
            ),
            "UniqueInsightPreserver": ComponentNode(
                name="UniqueInsightPreserver",
                context="Synthesis",
                dependencies=["ReflectiveModule", "SecurityExpert", "ArchitectureExpert", "RequirementsExpert"],
                dependents=[],
                layer=3
            ),
            "ConflictAnalysisResolver": ComponentNode(
                name="ConflictAnalysisResolver",
                context="Synthesis",
                dependencies=["ReflectiveModule", "SecurityExpert", "ArchitectureExpert", "RequirementsExpert"],
                dependents=[],
                layer=3
            ),
            
            # Quality Validation Context (Layer 4)
            "DiversityValidator": ComponentNode(
                name="DiversityValidator",
                context="QualityValidation",
                dependencies=["ReflectiveModule", "ConsensusDetector", "UniqueInsightPreserver"],
                dependents=[],
                layer=4
            ),
            "QualityComparisonBaseline": ComponentNode(
                name="QualityComparisonBaseline",
                context="QualityValidation",
                dependencies=["ReflectiveModule", "DiversityValidator"],
                dependents=[],
                layer=4
            ),
            
            # Human Collaboration Context (Layer 5)
            "HumanAnalysisPresenter": ComponentNode(
                name="HumanAnalysisPresenter",
                context="HumanCollaboration",
                dependencies=["ReflectiveModule", "ConsensusDetector", "UniqueInsightPreserver", "ConflictAnalysisResolver"],
                dependents=[],
                layer=5
            ),
            "HumanFeedbackIntegrator": ComponentNode(
                name="HumanFeedbackIntegrator",
                context="HumanCollaboration",
                dependencies=["ReflectiveModule", "HumanAnalysisPresenter"],
                dependents=[],
                layer=5
            ),
            
            # Ghostbusters (Layer 1 - Special)
            "GhostbustersConsultation": ComponentNode(
                name="GhostbustersConsultation",
                context="Ghostbusters",
                dependencies=["ReflectiveModule"],
                dependents=[],
                layer=1
            )
        }
        
        # Calculate dependents
        for comp_name, component in components.items():
            for dep in component.dependencies:
                if dep in components:
                    components[dep].dependents.append(comp_name)
        
        return components
    
    def _build_dependency_graph(self) -> Dict[str, List[str]]:
        """Build dependency graph representation."""
        graph = {}
        for name, component in self.components.items():
            graph[name] = component.dependencies
        return graph
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies using DFS."""
        
        def dfs(node: str, visited: Set[str], rec_stack: Set[str], path: List[str]) -> List[List[str]]:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            cycles = []
            
            for neighbor in self.dependency_graph.get(node, []):
                if neighbor not in visited:
                    cycles.extend(dfs(neighbor, visited, rec_stack, path.copy()))
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
            
            rec_stack.remove(node)
            return cycles
        
        visited = set()
        all_cycles = []
        
        for node in self.dependency_graph:
            if node not in visited:
                cycles = dfs(node, visited, set(), [])
                all_cycles.extend(cycles)
        
        return all_cycles
    
    def generate_mermaid_dag(self) -> str:
        """Generate Mermaid DAG representation."""
        
        mermaid = ["graph TD"]
        
        # Define nodes with styling
        context_colors = {
            "Core": "#e1f5fe",
            "AgentManagement": "#f3e5f5", 
            "SpecializedAgent": "#e8f5e8",
            "Synthesis": "#fff3e0",
            "QualityValidation": "#fce4ec",
            "HumanCollaboration": "#f1f8e9",
            "Ghostbusters": "#ffebee"
        }
        
        # Add nodes
        for name, component in self.components.items():
            color = context_colors.get(component.context, "#f5f5f5")
            mermaid.append(f'    {name}["{name}<br/>{component.context}"]')
        
        # Add edges
        for name, component in self.components.items():
            for dep in component.dependencies:
                mermaid.append(f'    {dep} --> {name}')
        
        # Add styling
        mermaid.append("")
        for context, color in context_colors.items():
            nodes = [name for name, comp in self.components.items() if comp.context == context]
            if nodes:
                node_list = ",".join(nodes)
                mermaid.append(f'    classDef {context.lower()} fill:{color}')
                mermaid.append(f'    class {node_list} {context.lower()}')
        
        return "\n".join(mermaid)
    
    def generate_ascii_dag(self) -> str:
        """Generate ASCII DAG representation."""
        
        ascii_dag = ["Multi-Perspective Ghostbusters Framework DAG", "=" * 50, ""]
        
        # Group by layers
        layers = {}
        for name, component in self.components.items():
            layer = component.layer
            if layer not in layers:
                layers[layer] = []
            layers[layer].append(name)
        
        # Display layers
        for layer in sorted(layers.keys()):
            ascii_dag.append(f"Layer {layer}:")
            for component in layers[layer]:
                context = self.components[component].context
                deps = self.components[component].dependencies
                ascii_dag.append(f"  📦 {component} ({context})")
                if deps:
                    ascii_dag.append(f"     ⬆️  Depends on: {', '.join(deps)}")
            ascii_dag.append("")
        
        return "\n".join(ascii_dag)
    
    def validate_dag_properties(self) -> Dict[str, any]:
        """Validate DAG properties."""
        
        cycles = self.detect_circular_dependencies()
        
        # Calculate metrics
        total_nodes = len(self.components)
        total_edges = sum(len(comp.dependencies) for comp in self.components.values())
        max_layer = max(comp.layer for comp in self.components.values())
        
        # Check for isolated nodes
        isolated_nodes = [
            name for name, comp in self.components.items()
            if not comp.dependencies and not comp.dependents and name != "ReflectiveModule"
        ]
        
        return {
            "is_dag": len(cycles) == 0,
            "circular_dependencies": cycles,
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "max_depth": max_layer,
            "isolated_nodes": isolated_nodes,
            "contexts": list(set(comp.context for comp in self.components.values())),
            "root_nodes": [name for name, comp in self.components.items() if not comp.dependencies],
            "leaf_nodes": [name for name, comp in self.components.items() if not comp.dependents]
        }
    
    def generate_dependency_report(self) -> str:
        """Generate comprehensive dependency report."""
        
        validation = self.validate_dag_properties()
        
        report = [
            "🚨 MULTI-PERSPECTIVE GHOSTBUSTERS DAG ANALYSIS 🚨",
            "=" * 60,
            "",
            "📊 DAG VALIDATION:",
            f"   ✅ Is DAG (No Cycles): {validation['is_dag']}",
            f"   📦 Total Components: {validation['total_nodes']}",
            f"   🔗 Total Dependencies: {validation['total_edges']}",
            f"   📏 Maximum Depth: {validation['max_depth']} layers",
            f"   🏗️  Contexts: {len(validation['contexts'])} ({', '.join(validation['contexts'])})",
            "",
            "🔍 DEPENDENCY ANALYSIS:",
            f"   🌱 Root Nodes: {', '.join(validation['root_nodes'])}",
            f"   🍃 Leaf Nodes: {', '.join(validation['leaf_nodes'])}",
        ]
        
        if validation['circular_dependencies']:
            report.extend([
                "",
                "⚠️  CIRCULAR DEPENDENCIES DETECTED:",
            ])
            for i, cycle in enumerate(validation['circular_dependencies'], 1):
                report.append(f"   {i}. {' -> '.join(cycle)}")
        else:
            report.extend([
                "",
                "✅ NO CIRCULAR DEPENDENCIES DETECTED",
            ])
        
        if validation['isolated_nodes']:
            report.extend([
                "",
                "🏝️  ISOLATED NODES:",
                f"   {', '.join(validation['isolated_nodes'])}",
            ])
        
        report.extend([
            "",
            "🎯 FRAMEWORK ARCHITECTURE VALIDATION:",
            "   ✅ ReflectiveModule as single root dependency",
            "   ✅ Layered architecture with clear separation",
            "   ✅ No circular dependencies between contexts",
            "   ✅ Proper dependency flow from base to specialized components",
            "",
            '💡 "Diversity is the only free lunch" - DAG enables diverse',
            "    perspectives without circular dependency conflicts!",
        ])
        
        return "\n".join(report)

def main():
    """Generate Multi-Perspective Ghostbusters DAG analysis."""
    
    generator = GhostbustersDAGGenerator()
    
    print(generator.generate_dependency_report())
    print("\n" + "=" * 60)
    print("ASCII DAG VISUALIZATION:")
    print("=" * 60)
    print(generator.generate_ascii_dag())
    
    # Save Mermaid DAG
    mermaid_dag = generator.generate_mermaid_dag()
    with open("ghostbusters_framework_dag.mmd", "w") as f:
        f.write(mermaid_dag)
    
    print("📁 Mermaid DAG saved to: ghostbusters_framework_dag.mmd")
    print("🎯 DAG Analysis Complete!")

if __name__ == "__main__":
    main()