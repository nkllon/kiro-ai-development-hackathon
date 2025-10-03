#!/usr/bin/env python3
"""
Makefile Analysis System - Automation Script Discovery
=====================================================

Analyzes Makefile targets and maps them to infrastructure components
for the Beast Mode framework system architecture documentation.
"""

import logging
import re
import subprocess
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleCapability, GracefulDegradationResult


@dataclass
class MakefileTarget:
    """Makefile target information."""
    name: str
    dependencies: List[str] = field(default_factory=list)
    commands: List[str] = field(default_factory=list)
    affected_components: List[str] = field(default_factory=list)
    expected_outcomes: List[str] = field(default_factory=list)
    description: Optional[str] = None
    category: Optional[str] = None
    execution_time_estimate: Optional[int] = None  # seconds


@dataclass
class AutomationChain:
    """Automation chain mapping."""
    trigger_target: str
    sequence: List[str]
    validation_points: List[str]
    rollback_procedure: List[str]
    affected_services: List[str]


@dataclass
class ScriptToComponentMapping:
    """Mapping between scripts and infrastructure components."""
    script_path: str
    script_type: str  # python, shell, makefile_target
    target_components: List[str]
    purpose: str
    parameters: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    integration_points: List[str] = field(default_factory=list)


class MakefileAnalyzer(ReflectiveModule):
    """
    Analyzes Makefile targets and maps automation workflows
    to infrastructure components.
    """
    
    def __init__(self, makefile_path: str = "Makefile"):
        super().__init__()
        self.module_id = "MakefileAnalyzer"
        self._logger = logging.getLogger(f"system_architecture.{self.__class__.__name__}")
        self._makefile_path = Path(makefile_path)
        self._targets: Dict[str, MakefileTarget] = {}
        self._automation_chains: List[AutomationChain] = []
        self._script_mappings: List[ScriptToComponentMapping] = []
        
        # Infrastructure component categories
        self._component_categories = {
            "tunnel": ["Cloudflare", "DNS", "Ingress"],
            "dashboard": ["Observatory", "WebSocket", "Metrics"],
            "prometheus": ["Metrics", "Scraping", "Alerts"],
            "grafana": ["Visualization", "Dashboards", "Datasources"],
            "task": ["Beast Mode Components", "Execution"],
            "phase": ["Multi-component Operations", "Coordination"]
        }
        
    def parse_makefile(self) -> Dict[str, MakefileTarget]:
        """Parse Makefile and extract all targets with their dependencies and commands."""
        self._logger.info(f"Parsing Makefile: {self._makefile_path}")
        
        if not self._makefile_path.exists():
            self._logger.error(f"Makefile not found: {self._makefile_path}")
            return {}
        
        targets = {}
        current_target = None
        
        try:
            with open(self._makefile_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.rstrip('\n')
                
                # Skip empty lines and comments
                if not line.strip() or line.strip().startswith('#'):
                    continue
                
                # Target definition (starts at column 0, contains colon)
                if ':' in line and not line.startswith('\t') and not line.startswith(' '):
                    target_match = re.match(r'^([^:]+):\s*(.*)', line)
                    if target_match:
                        target_name = target_match.group(1).strip()
                        dependencies_str = target_match.group(2).strip()
                        
                        # Parse dependencies
                        dependencies = []
                        if dependencies_str:
                            dependencies = [dep.strip() for dep in dependencies_str.split() if dep.strip()]
                        
                        # Create target
                        current_target = MakefileTarget(
                            name=target_name,
                            dependencies=dependencies
                        )
                        
                        # Categorize target
                        current_target.category = self._categorize_target(target_name)
                        current_target.affected_components = self._identify_affected_components(target_name)
                        
                        targets[target_name] = current_target
                
                # Command line (starts with tab)
                elif line.startswith('\t') and current_target:
                    command = line[1:].strip()  # Remove leading tab
                    if command and not command.startswith('#'):
                        current_target.commands.append(command)
                        
                        # Extract expected outcomes from commands
                        outcomes = self._extract_expected_outcomes(command)
                        current_target.expected_outcomes.extend(outcomes)
        
        except Exception as e:
            self._logger.error(f"Error parsing Makefile: {e}")
            return {}
        
        self._targets = targets
        self._logger.info(f"Parsed {len(targets)} Makefile targets")
        return targets
    
    def _categorize_target(self, target_name: str) -> str:
        """Categorize target based on naming patterns."""
        target_lower = target_name.lower()
        
        for category, keywords in self._component_categories.items():
            if category in target_lower:
                return category
        
        # Additional categorization logic
        if any(keyword in target_lower for keyword in ['start', 'stop', 'restart']):
            return "lifecycle"
        elif any(keyword in target_lower for keyword in ['status', 'health', 'check']):
            return "monitoring"
        elif any(keyword in target_lower for keyword in ['deploy', 'install', 'setup']):
            return "deployment"
        elif any(keyword in target_lower for keyword in ['test', 'validate']):
            return "testing"
        elif any(keyword in target_lower for keyword in ['clean', 'reset']):
            return "maintenance"
        else:
            return "general"
    
    def _identify_affected_components(self, target_name: str) -> List[str]:
        """Identify which infrastructure components are affected by this target."""
        target_lower = target_name.lower()
        affected = []
        
        # Map target patterns to components
        component_mappings = {
            "tunnel": ["Cloudflare Tunnel (d1e53e43-033f-4994-8f46-c83962ae3785)", "DNS Routing"],
            "dashboard": ["Observatory Server (localhost:8888)", "WebSocket Endpoints"],
            "prometheus": ["Prometheus Server (localhost:9090)", "Metrics Collection"],
            "grafana": ["Grafana Dashboard (localhost:3000)", "Visualization"],
            "redis": ["Redis Coordination (192.168.1.119:6379)", "Redis Fallback (localhost:6380)"],
            "observatory": ["Observatory Server", "WebSocket Endpoints", "ReflectiveModule Integration"]
        }
        
        for pattern, components in component_mappings.items():
            if pattern in target_lower:
                affected.extend(components)
        
        # Task and phase targets affect Beast Mode components
        if target_lower.startswith('task-') or target_lower.startswith('phase-'):
            affected.append("Beast Mode Framework Components")
        
        return list(set(affected))  # Remove duplicates
    
    def _extract_expected_outcomes(self, command: str) -> List[str]:
        """Extract expected outcomes from command analysis."""
        outcomes = []
        command_lower = command.lower()
        
        # Common outcome patterns
        if 'start' in command_lower:
            outcomes.append("Service startup")
        if 'stop' in command_lower:
            outcomes.append("Service shutdown")
        if 'restart' in command_lower:
            outcomes.append("Service restart")
        if 'status' in command_lower:
            outcomes.append("Status report")
        if 'health' in command_lower:
            outcomes.append("Health check")
        if 'deploy' in command_lower:
            outcomes.append("Deployment completion")
        if 'test' in command_lower:
            outcomes.append("Test execution")
        if 'validate' in command_lower:
            outcomes.append("Validation results")
        
        return outcomes
    
    def analyze_target_dependencies(self) -> Dict[str, Any]:
        """Analyze target dependency chains and execution order."""
        self._logger.info("Analyzing target dependencies...")
        
        if not self._targets:
            self.parse_makefile()
        
        dependency_analysis = {
            "dependency_graph": {},
            "execution_chains": [],
            "circular_dependencies": [],
            "orphaned_targets": [],
            "critical_path_targets": []
        }
        
        # Build dependency graph
        for target_name, target in self._targets.items():
            dependency_analysis["dependency_graph"][target_name] = {
                "dependencies": target.dependencies,
                "dependents": [],
                "category": target.category,
                "affected_components": target.affected_components
            }
        
        # Find dependents (reverse dependencies)
        for target_name, target in self._targets.items():
            for dep in target.dependencies:
                if dep in dependency_analysis["dependency_graph"]:
                    dependency_analysis["dependency_graph"][dep]["dependents"].append(target_name)
        
        # Identify execution chains for key workflows
        key_workflows = [
            "tunnel-start", "tunnel-stop",
            "dashboard-up", "dashboard-stop", "dashboard-restart",
            "dashboard-status", "dashboard-logs"
        ]
        
        for workflow in key_workflows:
            if workflow in self._targets:
                chain = self._build_execution_chain(workflow)
                dependency_analysis["execution_chains"].append({
                    "workflow": workflow,
                    "chain": chain,
                    "estimated_duration": self._estimate_chain_duration(chain)
                })
        
        # Detect circular dependencies
        circular_deps = self._detect_circular_dependencies()
        dependency_analysis["circular_dependencies"] = circular_deps
        
        # Find orphaned targets (no dependencies, no dependents)
        orphaned = []
        for target_name, info in dependency_analysis["dependency_graph"].items():
            if not info["dependencies"] and not info["dependents"]:
                orphaned.append(target_name)
        dependency_analysis["orphaned_targets"] = orphaned
        
        # Identify critical path targets
        critical_targets = self._identify_critical_path_targets()
        dependency_analysis["critical_path_targets"] = critical_targets
        
        self._logger.info(f"Dependency analysis completed: {len(dependency_analysis['execution_chains'])} chains identified")
        return dependency_analysis
    
    def _build_execution_chain(self, target_name: str, visited: Optional[Set[str]] = None) -> List[str]:
        """Build execution chain for a target including all dependencies."""
        if visited is None:
            visited = set()
        
        if target_name in visited:
            return []  # Circular dependency
        
        visited.add(target_name)
        chain = []
        
        if target_name in self._targets:
            target = self._targets[target_name]
            
            # Add dependencies first
            for dep in target.dependencies:
                dep_chain = self._build_execution_chain(dep, visited.copy())
                chain.extend(dep_chain)
            
            # Add current target
            chain.append(target_name)
        
        return chain
    
    def _estimate_chain_duration(self, chain: List[str]) -> int:
        """Estimate execution duration for a chain of targets."""
        # Default time estimates based on target categories
        category_times = {
            "tunnel": 30,      # Tunnel operations take time
            "dashboard": 15,   # Dashboard operations
            "prometheus": 10,  # Prometheus operations
            "grafana": 10,     # Grafana operations
            "lifecycle": 5,    # Start/stop operations
            "monitoring": 2,   # Status checks
            "testing": 20,     # Test execution
            "deployment": 60,  # Deployment operations
            "general": 5       # Default
        }
        
        total_time = 0
        for target_name in chain:
            if target_name in self._targets:
                target = self._targets[target_name]
                category_time = category_times.get(target.category, 5)
                total_time += category_time
        
        return total_time
    
    def _detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies in the target graph."""
        circular_deps = []
        visited = set()
        rec_stack = set()
        
        def dfs(target_name: str, path: List[str]) -> bool:
            if target_name in rec_stack:
                # Found circular dependency
                cycle_start = path.index(target_name)
                cycle = path[cycle_start:] + [target_name]
                circular_deps.append(cycle)
                return True
            
            if target_name in visited:
                return False
            
            visited.add(target_name)
            rec_stack.add(target_name)
            
            if target_name in self._targets:
                for dep in self._targets[target_name].dependencies:
                    if dfs(dep, path + [target_name]):
                        return True
            
            rec_stack.remove(target_name)
            return False
        
        for target_name in self._targets:
            if target_name not in visited:
                dfs(target_name, [])
        
        return circular_deps
    
    def _identify_critical_path_targets(self) -> List[str]:
        """Identify targets that are on the critical path for key operations."""
        critical_targets = set()
        
        # Key operational targets
        key_targets = [
            "tunnel-start", "dashboard-up", "prometheus-start", "grafana-start"
        ]
        
        for target in key_targets:
            if target in self._targets:
                chain = self._build_execution_chain(target)
                critical_targets.update(chain)
        
        return list(critical_targets)
    
    def map_scripts_to_components(self) -> List[ScriptToComponentMapping]:
        """Map Python scripts and automation to infrastructure components."""
        self._logger.info("Mapping scripts to infrastructure components...")
        
        script_mappings = []
        
        # Known script mappings from the spec
        known_mappings = [
            {
                "script": "observatory-daemon.py",
                "type": "python",
                "components": ["Observatory Server", "WebSocket Endpoints", "ReflectiveModule Integration"],
                "purpose": "Observatory server lifecycle management",
                "integration_points": ["ACE Reporter", "AI Memory Palace", "DAG Registry"]
            },
            {
                "script": "tunnel management scripts",
                "type": "python",
                "components": ["Cloudflare Tunnel", "DNS Routing"],
                "purpose": "Cloudflare tunnel operations",
                "integration_points": ["DNS Management", "SSL/TLS Configuration"]
            },
            {
                "script": "prometheus integration scripts",
                "type": "python", 
                "components": ["Prometheus Server", "Metrics Collection"],
                "purpose": "Metrics collection and validation",
                "integration_points": ["ReflectiveModule Metrics", "Observatory Integration"]
            },
            {
                "script": "grafana configuration scripts",
                "type": "python",
                "components": ["Grafana Dashboard", "Datasource Management"],
                "purpose": "Dashboard and datasource management",
                "integration_points": ["Prometheus Datasource", "Dashboard Deployment"]
            }
        ]
        
        # Create mappings for known scripts
        for mapping_info in known_mappings:
            mapping = ScriptToComponentMapping(
                script_path=mapping_info["script"],
                script_type=mapping_info["type"],
                target_components=mapping_info["components"],
                purpose=mapping_info["purpose"],
                integration_points=mapping_info.get("integration_points", [])
            )
            script_mappings.append(mapping)
        
        # Map Makefile targets to components
        for target_name, target in self._targets.items():
            if target.affected_components:
                mapping = ScriptToComponentMapping(
                    script_path=f"Makefile:{target_name}",
                    script_type="makefile_target",
                    target_components=target.affected_components,
                    purpose=f"Makefile target: {target_name}",
                    dependencies=target.dependencies,
                    parameters=target.commands
                )
                script_mappings.append(mapping)
        
        self._script_mappings = script_mappings
        self._logger.info(f"Created {len(script_mappings)} script-to-component mappings")
        return script_mappings
    
    def generate_automation_workflow_diagrams(self) -> Dict[str, Any]:
        """Generate automation workflow diagrams showing target execution chains."""
        self._logger.info("Generating automation workflow diagrams...")
        
        if not self._targets:
            self.parse_makefile()
        
        dependency_analysis = self.analyze_target_dependencies()
        
        # Create workflow diagrams for key operations
        workflow_diagrams = {
            "tunnel_operations": self._create_tunnel_workflow_diagram(),
            "dashboard_operations": self._create_dashboard_workflow_diagram(),
            "monitoring_operations": self._create_monitoring_workflow_diagram(),
            "maintenance_operations": self._create_maintenance_workflow_diagram()
        }
        
        # Add dependency graph visualization
        workflow_diagrams["dependency_graph"] = {
            "nodes": [
                {
                    "id": target_name,
                    "label": target_name,
                    "category": target.category,
                    "affected_components": target.affected_components
                }
                for target_name, target in self._targets.items()
            ],
            "edges": [
                {
                    "from": target_name,
                    "to": dep,
                    "type": "dependency"
                }
                for target_name, target in self._targets.items()
                for dep in target.dependencies
            ]
        }
        
        return workflow_diagrams
    
    def _create_tunnel_workflow_diagram(self) -> Dict[str, Any]:
        """Create workflow diagram for tunnel operations."""
        tunnel_targets = [name for name in self._targets.keys() if 'tunnel' in name.lower()]
        
        return {
            "title": "Tunnel Operations Workflow",
            "targets": tunnel_targets,
            "workflows": [
                {
                    "name": "tunnel-start",
                    "sequence": self._build_execution_chain("tunnel-start") if "tunnel-start" in self._targets else [],
                    "validation_points": ["DNS propagation", "Service health", "WebSocket connectivity"]
                },
                {
                    "name": "tunnel-stop", 
                    "sequence": self._build_execution_chain("tunnel-stop") if "tunnel-stop" in self._targets else [],
                    "validation_points": ["Graceful shutdown", "Resource cleanup"]
                }
            ]
        }
    
    def _create_dashboard_workflow_diagram(self) -> Dict[str, Any]:
        """Create workflow diagram for dashboard operations."""
        dashboard_targets = [name for name in self._targets.keys() if 'dashboard' in name.lower()]
        
        return {
            "title": "Dashboard Operations Workflow",
            "targets": dashboard_targets,
            "workflows": [
                {
                    "name": "dashboard-up",
                    "sequence": self._build_execution_chain("dashboard-up") if "dashboard-up" in self._targets else [],
                    "validation_points": ["Observatory startup", "WebSocket registration", "Metrics exposure"]
                },
                {
                    "name": "dashboard-status",
                    "sequence": self._build_execution_chain("dashboard-status") if "dashboard-status" in self._targets else [],
                    "validation_points": ["Health endpoints", "WebSocket connectivity", "Metrics collection"]
                }
            ]
        }
    
    def _create_monitoring_workflow_diagram(self) -> Dict[str, Any]:
        """Create workflow diagram for monitoring operations."""
        monitoring_targets = [name for name in self._targets.keys() 
                            if any(keyword in name.lower() for keyword in ['prometheus', 'grafana', 'status', 'health'])]
        
        return {
            "title": "Monitoring Operations Workflow",
            "targets": monitoring_targets,
            "workflows": [
                {
                    "name": "monitoring-setup",
                    "sequence": [t for t in monitoring_targets if 'start' in t or 'up' in t],
                    "validation_points": ["Prometheus scraping", "Grafana datasource", "Dashboard availability"]
                }
            ]
        }
    
    def _create_maintenance_workflow_diagram(self) -> Dict[str, Any]:
        """Create workflow diagram for maintenance operations."""
        maintenance_targets = [name for name in self._targets.keys() 
                             if any(keyword in name.lower() for keyword in ['clean', 'reset', 'restart', 'stop'])]
        
        return {
            "title": "Maintenance Operations Workflow",
            "targets": maintenance_targets,
            "workflows": [
                {
                    "name": "system-restart",
                    "sequence": [t for t in maintenance_targets if 'restart' in t],
                    "validation_points": ["Service shutdown", "Service startup", "Health verification"]
                }
            ]
        }
    
    def get_comprehensive_analysis(self) -> Dict[str, Any]:
        """Get comprehensive Makefile analysis report."""
        self._logger.info("Generating comprehensive Makefile analysis...")
        
        # Parse Makefile if not already done
        if not self._targets:
            self.parse_makefile()
        
        # Perform all analyses
        dependency_analysis = self.analyze_target_dependencies()
        script_mappings = self.map_scripts_to_components()
        workflow_diagrams = self.generate_automation_workflow_diagrams()
        
        # Create comprehensive report
        analysis_report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "makefile_path": str(self._makefile_path),
            "summary": {
                "total_targets": len(self._targets),
                "target_categories": self._get_category_summary(),
                "dependency_chains": len(dependency_analysis["execution_chains"]),
                "script_mappings": len(script_mappings),
                "circular_dependencies": len(dependency_analysis["circular_dependencies"])
            },
            "targets": {
                name: {
                    "dependencies": target.dependencies,
                    "commands": target.commands,
                    "category": target.category,
                    "affected_components": target.affected_components,
                    "expected_outcomes": target.expected_outcomes
                }
                for name, target in self._targets.items()
            },
            "dependency_analysis": dependency_analysis,
            "script_mappings": [
                {
                    "script_path": mapping.script_path,
                    "script_type": mapping.script_type,
                    "target_components": mapping.target_components,
                    "purpose": mapping.purpose,
                    "dependencies": mapping.dependencies,
                    "integration_points": mapping.integration_points
                }
                for mapping in script_mappings
            ],
            "workflow_diagrams": workflow_diagrams,
            "recommendations": self._generate_recommendations()
        }
        
        self._logger.info("Comprehensive Makefile analysis completed")
        return analysis_report
    
    def _get_category_summary(self) -> Dict[str, int]:
        """Get summary of targets by category."""
        category_counts = {}
        for target in self._targets.values():
            category = target.category or "unknown"
            category_counts[category] = category_counts.get(category, 0) + 1
        return category_counts
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # Check for missing key targets
        expected_targets = [
            "tunnel-start", "tunnel-stop",
            "dashboard-up", "dashboard-stop", "dashboard-restart",
            "dashboard-status", "dashboard-logs"
        ]
        
        missing_targets = [target for target in expected_targets if target not in self._targets]
        if missing_targets:
            recommendations.append(f"Consider adding missing key targets: {', '.join(missing_targets)}")
        
        # Check for circular dependencies
        dependency_analysis = self.analyze_target_dependencies()
        if dependency_analysis["circular_dependencies"]:
            recommendations.append("Resolve circular dependencies to ensure proper execution order")
        
        # Check for orphaned targets
        if dependency_analysis["orphaned_targets"]:
            recommendations.append("Review orphaned targets - they may need integration into workflows")
        
        # Check for undocumented targets
        undocumented = [name for name, target in self._targets.items() if not target.expected_outcomes]
        if len(undocumented) > len(self._targets) * 0.3:  # More than 30% undocumented
            recommendations.append("Add documentation/comments for target expected outcomes")
        
        return recommendations
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - required by ReflectiveModule."""
        return {
            "module_id": self.module_id,
            "name": "Makefile Analyzer",
            "version": "1.0.0",
            "description": "Analyzes Makefile targets and maps automation workflows to infrastructure components",
            "author": "System Architecture Discovery",
            "capabilities": [
                "makefile_parsing",
                "dependency_analysis",
                "workflow_mapping",
                "script_component_mapping"
            ]
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - required by ReflectiveModule."""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.VALIDATION,
            ModuleCapability.ANALYSIS
        ]
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - required by ReflectiveModule."""
        return GracefulDegradationResult(
            success=True,
            message="Makefile analyzer supports graceful degradation",
            fallback_capabilities=[ModuleCapability.CORE_FUNCTIONALITY],
            recovery_suggestions=[
                "Retry with simpler Makefile parsing",
                "Skip complex dependency analysis if needed",
                "Use basic target extraction without workflow mapping"
            ]
        )
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status - required by ReflectiveModule."""
        return {
            "module": "MakefileAnalyzer",
            "status": "healthy",
            "makefile_path": str(self._makefile_path),
            "makefile_exists": self._makefile_path.exists(),
            "targets_parsed": len(self._targets),
            "script_mappings": len(self._script_mappings),
            "automation_chains": len(self._automation_chains)
        }