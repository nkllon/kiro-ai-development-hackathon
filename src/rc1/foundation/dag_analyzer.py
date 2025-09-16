"""
DAG Analyzer - Analyze dependency graphs and cycles
"""

import re
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DAGNode:
    """Represents a node in the DAG"""
    name: str
    dependencies: List[str]
    targets: List[str]
    commands: List[str]


@dataclass
class DAGAnalysisResult:
    """Result of DAG analysis"""
    nodes: Dict[str, DAGNode]
    cycles: List[List[str]]
    orphaned_nodes: List[str]
    disconnected_components: List[List[str]]
    health_score: float


class DAGAnalyzer:
    """Analyzes Makefile dependencies as DAG"""
    
    def __init__(self):
        self.nodes: Dict[str, DAGNode] = {}
        
    def analyze_makefile(self, makefile_path: str) -> DAGAnalysisResult:
        """
        Analyze Makefile and build DAG representation
        
        Args:
            makefile_path: Path to the Makefile
            
        Returns:
            DAGAnalysisResult with analysis findings
        """
        self._parse_makefile(makefile_path)
        
        cycles = self._detect_cycles()
        orphaned = self._find_orphaned_nodes()
        disconnected = self._find_disconnected_components()
        health_score = self._calculate_health_score(cycles, orphaned, disconnected)
        
        return DAGAnalysisResult(
            nodes=self.nodes,
            cycles=cycles,
            orphaned_nodes=orphaned,
            disconnected_components=disconnected,
            health_score=health_score
        )
    
    def _parse_makefile(self, makefile_path: str) -> None:
        """Parse Makefile and extract targets and dependencies"""
        try:
            with open(makefile_path, 'r') as f:
                content = f.read()
                
            # Extract targets and dependencies
            target_pattern = r'^([a-zA-Z0-9_-]+)\s*:\s*(.*?)(?=\n\t|\n[a-zA-Z0-9_-]|$)'
            targets = re.findall(target_pattern, content, re.MULTILINE | re.DOTALL)
            
            for target, deps in targets:
                dependencies = [dep.strip() for dep in deps.split() if dep.strip()]
                commands = self._extract_commands(content, target)
                
                self.nodes[target] = DAGNode(
                    name=target,
                    dependencies=dependencies,
                    targets=[target],
                    commands=commands
                )
                
        except Exception as e:
            print(f"Error parsing Makefile {makefile_path}: {e}")
    
    def _extract_commands(self, content: str, target: str) -> List[str]:
        """Extract commands for a specific target"""
        commands = []
        lines = content.split('\n')
        in_target = False
        
        for line in lines:
            if line.strip().startswith(target + ':'):
                in_target = True
                continue
            elif in_target:
                if line.strip().startswith('\t'):
                    commands.append(line.strip())
                elif line.strip() and not line.startswith('\t'):
                    break
                    
        return commands
    
    def _detect_cycles(self) -> List[List[str]]:
        """Detect cycles in the DAG using DFS"""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]) -> None:
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
                
            if node in visited:
                return
                
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            if node in self.nodes:
                for dep in self.nodes[node].dependencies:
                    dfs(dep, path.copy())
                    
            rec_stack.remove(node)
        
        for node in self.nodes:
            if node not in visited:
                dfs(node, [])
                
        return cycles
    
    def _find_orphaned_nodes(self) -> List[str]:
        """Find nodes with no dependencies and no dependents"""
        orphaned = []
        
        for node_name, node in self.nodes.items():
            has_dependencies = bool(node.dependencies)
            has_dependents = any(
                node_name in other_node.dependencies 
                for other_node in self.nodes.values()
            )
            
            if not has_dependencies and not has_dependents:
                orphaned.append(node_name)
                
        return orphaned
    
    def _find_disconnected_components(self) -> List[List[str]]:
        """Find disconnected components in the DAG"""
        visited = set()
        components = []
        
        def dfs_component(node: str, component: list[str]) -> None:
            if node in visited or node not in self.nodes:
                return
                
            visited.add(node)
            component.append(node)
            
            # Visit dependencies
            for dep in self.nodes[node].dependencies:
                dfs_component(dep, component)
                
            # Visit dependents
            for other_node_name, other_node in self.nodes.items():
                if node in other_node.dependencies:
                    dfs_component(other_node_name, component)
        
        for node_name in self.nodes:
            if node_name not in visited:
                component = []
                dfs_component(node_name, component)
                if component:
                    components.append(component)
                    
        return components
    
    def _calculate_health_score(self, cycles: List[List[str]], 
                               orphaned: List[str], 
                               disconnected: List[List[str]]) -> float:
        """Calculate overall health score based on analysis results"""
        total_nodes = len(self.nodes)
        if total_nodes == 0:
            return 0.0
            
        # Penalize cycles heavily
        cycle_penalty = len(cycles) * 0.3
        
        # Penalize orphaned nodes moderately
        orphan_penalty = len(orphaned) * 0.1
        
        # Penalize disconnected components
        disconnect_penalty = max(0, len(disconnected) - 1) * 0.2
        
        # Calculate base score
        base_score = 1.0 - (cycle_penalty + orphan_penalty + disconnect_penalty)
        
        return max(0.0, min(1.0, base_score))
