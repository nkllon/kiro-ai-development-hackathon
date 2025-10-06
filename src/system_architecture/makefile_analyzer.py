#!/usr/bin/env python3
"""
Makefile Analysis System
Task 1.5 - System Architecture Wiring Diagram Implementation
"""

import os
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class MakefileAnalysisSystem(ReflectiveModule):
    """
    Analyzes Makefile structure and dependencies for system architecture mapping.
    
    Provides comprehensive analysis of build targets, dependencies,
    and automation workflows defined in Makefiles.
    """
    
    def __init__(self):
        """Initialize the Makefile analysis system."""
        super().__init__()
        self.discovered_makefiles = []
        self.target_analysis = {}
        self.dependency_graph = {}
        
        self._logger.info("MakefileAnalysisSystem initialized", extra={
            "component": "makefile_analysis_system"
        })
    
    def discover_makefiles(self) -> List[str]:
        """
        Discover all Makefile-related files in the project.
        
        Returns:
            List of discovered Makefile paths
        """
        try:
            makefile_patterns = [
                "Makefile*",
                "makefile*",
                "*.mk"
            ]
            
            discovered = []
            for pattern in makefile_patterns:
                for makefile in Path(".").glob(pattern):
                    if makefile.is_file():
                        discovered.append(str(makefile))
            
            # Also search in subdirectories
            for makefile in Path(".").rglob("Makefile*"):
                if makefile.is_file() and str(makefile) not in discovered:
                    discovered.append(str(makefile))
            
            self.discovered_makefiles = discovered
            
            self._logger.info("Makefiles discovered", extra={
                "makefile_count": len(discovered),
                "component": "makefile_analysis_system"
            })
            
            return discovered
            
        except Exception as e:
            self._logger.error("Makefile discovery failed", extra={
                "error": str(e),
                "component": "makefile_analysis_system"
            })
            return []
    
    def analyze_targets(self, makefile_path: str) -> Dict[str, Any]:
        """
        Analyze targets and dependencies in a Makefile.
        
        Args:
            makefile_path: Path to Makefile to analyze
            
        Returns:
            Dict containing target analysis
        """
        try:
            with open(makefile_path, 'r') as f:
                content = f.read()
            
            # Extract targets using regex
            target_pattern = r'^([a-zA-Z0-9_-]+)\s*:([^=].*)?$'
            targets = {}
            
            for line_num, line in enumerate(content.split('\n'), 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    match = re.match(target_pattern, line)
                    if match:
                        target_name = match.group(1)
                        dependencies = match.group(2)
                        
                        deps = []
                        if dependencies:
                            deps = [dep.strip() for dep in dependencies.split() if dep.strip()]
                        
                        targets[target_name] = {
                            "line_number": line_num,
                            "dependencies": deps,
                            "raw_line": line
                        }
            
            analysis = {
                "makefile": makefile_path,
                "target_count": len(targets),
                "targets": targets
            }
            
            self.target_analysis[makefile_path] = analysis
            
            self._logger.info("Target analysis completed", extra={
                "makefile": makefile_path,
                "target_count": len(targets),
                "component": "makefile_analysis_system"
            })
            
            return analysis
            
        except Exception as e:
            self._logger.error("Target analysis failed", extra={
                "makefile": makefile_path,
                "error": str(e),
                "component": "makefile_analysis_system"
            })
            return {"error": str(e)}
    
    def build_dependency_graph(self) -> Dict[str, Any]:
        """
        Build dependency graph from all analyzed Makefiles.
        
        Returns:
            Dict containing dependency graph
        """
        try:
            graph = {
                "nodes": [],
                "edges": [],
                "makefiles": list(self.target_analysis.keys())
            }
            
            all_targets = set()
            
            # Collect all targets
            for makefile, analysis in self.target_analysis.items():
                for target_name in analysis["targets"].keys():
                    all_targets.add(target_name)
                    graph["nodes"].append({
                        "id": target_name,
                        "makefile": makefile,
                        "type": "target"
                    })
            
            # Build edges (dependencies)
            for makefile, analysis in self.target_analysis.items():
                for target_name, target_info in analysis["targets"].items():
                    for dep in target_info["dependencies"]:
                        if dep in all_targets:
                            graph["edges"].append({
                                "source": dep,
                                "target": target_name,
                                "makefile": makefile
                            })
            
            self.dependency_graph = graph
            
            self._logger.info("Dependency graph built", extra={
                "node_count": len(graph["nodes"]),
                "edge_count": len(graph["edges"]),
                "component": "makefile_analysis_system"
            })
            
            return graph
            
        except Exception as e:
            self._logger.error("Dependency graph building failed", extra={
                "error": str(e),
                "component": "makefile_analysis_system"
            })
            return {"error": str(e)}
    
    def get_comprehensive_analysis(self) -> Dict[str, Any]:
        """
        Generate comprehensive Makefile analysis report.
        
        Returns:
            Dict containing complete analysis
        """
        # Discover makefiles
        makefiles = self.discover_makefiles()
        
        # Analyze each makefile
        for makefile in makefiles:
            self.analyze_targets(makefile)
        
        # Build dependency graph
        dependency_graph = self.build_dependency_graph()
        
        return {
            "analysis_timestamp": self._get_current_timestamp(),
            "discovered_makefiles": makefiles,
            "target_analysis": self.target_analysis,
            "dependency_graph": dependency_graph,
            "summary": {
                "total_makefiles": len(makefiles),
                "total_targets": sum(len(analysis["targets"]) for analysis in self.target_analysis.values()),
                "total_dependencies": len(dependency_graph.get("edges", []))
            }
        }
    
    def get_capabilities(self) -> List[str]:
        """Get module capabilities."""
        return ["makefile_analysis", "dependency_mapping", "target_discovery"]
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_name": "makefile_analysis_system",
            "version": "1.0.0",
            "description": "Makefile structure and dependency analysis"
        }
    
    def graceful_degradation(self) -> Dict[str, Any]:
        """Handle graceful degradation."""
        return {"success": True, "degraded_capabilities": []}
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status."""
        return {"status": "healthy", "uptime": 0}
