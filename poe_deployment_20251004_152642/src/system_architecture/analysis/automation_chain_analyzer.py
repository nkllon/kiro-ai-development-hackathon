#!/usr/bin/env python3
"""
Automation Chain Analyzer - Task 2.3 Implementation
==================================================

Analyzes automation chain dependencies, parameter passing, and integration workflows
for the Beast Mode framework system architecture documentation.

This implements Task 2.3 from the system architecture wiring diagram specification.
"""

import logging
import json
import networkx as nx
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleCapability, GracefulDegradationResult
from src.system_architecture.discovery.makefile_analyzer import MakefileAnalyzer, MakefileTarget


@dataclass
class ParameterMapping:
    """Parameter passing between scripts and components."""
    source: str
    target: str
    parameter_name: str
    parameter_type: str
    required: bool = True
    default_value: Optional[str] = None
    environment_variable: Optional[str] = None


@dataclass
class EnvironmentRequirement:
    """Environment requirements for script execution."""
    script_name: str
    variable_name: str
    required: bool = True
    default_value: Optional[str] = None
    description: Optional[str] = None
    validation_pattern: Optional[str] = None


@dataclass
class WebSocketEndpointDependency:
    """WebSocket endpoint registration dependencies."""
    endpoint_path: str
    service_name: str
    dependencies: List[str] = field(default_factory=list)
    initialization_order: int = 0
    health_check_endpoint: Optional[str] = None
    message_types: List[str] = field(default_factory=list)


@dataclass
class MetricsPipelineDependency:
    """Metrics collection pipeline dependency mapping."""
    source_component: str
    target_component: str
    metric_types: List[str] = field(default_factory=list)
    collection_interval: Optional[int] = None
    aggregation_rules: List[str] = field(default_factory=list)
    alert_thresholds: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntegrationCoordination:
    """Integration point coordination workflow."""
    integration_name: str
    source_system: str
    target_system: str
    coordination_method: str  # "direct", "queue", "webhook", "websocket"
    data_flow_direction: str  # "bidirectional", "source_to_target", "target_to_source"
    dependencies: List[str] = field(default_factory=list)
    validation_endpoints: List[str] = field(default_factory=list)


@dataclass
class AutomationDependencyGraph:
    """Complete automation dependency graph with execution order."""
    nodes: List[Dict[str, Any]] = field(default_factory=list)
    edges: List[Dict[str, Any]] = field(default_factory=list)
    execution_order: List[str] = field(default_factory=list)
    critical_path: List[str] = field(default_factory=list)
    parallel_groups: List[List[str]] = field(default_factory=list)


class AutomationChainAnalyzer(ReflectiveModule):
    """
    Analyzes automation chain dependencies and creates comprehensive
    dependency graphs with execution order using NetworkX.
    
    Implements Task 2.3 from the system architecture wiring diagram specification.
    """
    
    def __init__(self, makefile_path: str = "Makefile"):
        super().__init__()
        self.module_id = "AutomationChainAnalyzer"
        self._logger = logging.getLogger(f"system_architecture.{self.__class__.__name__}")
        
        # Initialize makefile analyzer
        self._makefile_analyzer = MakefileAnalyzer(makefile_path)
        
        # Analysis results
        self._parameter_mappings: List[ParameterMapping] = []
        self._environment_requirements: List[EnvironmentRequirement] = []
        self._websocket_dependencies: List[WebSocketEndpointDependency] = []
        self._metrics_dependencies: List[MetricsPipelineDependency] = []
        self._integration_coordination: List[IntegrationCoordination] = []
        self._dependency_graph: Optional[AutomationDependencyGraph] = None
        
        # NetworkX graph for dependency analysis
        self._nx_graph = nx.DiGraph()
        
        self._logger.info("AutomationChainAnalyzer initialized")
    
    def analyze_makefile_target_dependencies(self) -> Dict[str, Any]:
        """
        Analyze Makefile target dependencies using existing makefile_analyzer.py.
        
        Returns comprehensive analysis of target dependencies and execution chains.
        """
        self._logger.info("Analyzing Makefile target dependencies...")
        
        # Use existing makefile analyzer
        makefile_analysis = self._makefile_analyzer.get_comprehensive_analysis()
        
        # Extract dependency information
        target_dependencies = {}
        for target_name, target_info in makefile_analysis["targets"].items():
            target_dependencies[target_name] = {
                "dependencies": target_info["dependencies"],
                "affected_components": target_info["affected_components"],
                "category": target_info["category"],
                "commands": target_info["commands"],
                "expected_outcomes": target_info["expected_outcomes"]
            }
        
        # Analyze specific dependency patterns mentioned in Task 2.3
        dependency_patterns = self._analyze_dependency_patterns(makefile_analysis)
        
        # Create enhanced dependency analysis
        enhanced_analysis = {
            "target_dependencies": target_dependencies,
            "dependency_patterns": dependency_patterns,
            "execution_chains": makefile_analysis["dependency_analysis"]["execution_chains"],
            "circular_dependencies": makefile_analysis["dependency_analysis"]["circular_dependencies"],
            "critical_path": makefile_analysis["dependency_analysis"]["critical_path_targets"],
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        self._logger.info(f"Analyzed {len(target_dependencies)} Makefile targets")
        return enhanced_analysis
    
    def _analyze_dependency_patterns(self, makefile_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze specific dependency patterns like task-3.4 depends on task-3.3."""
        patterns = {
            "task_dependencies": {},
            "phase_dependencies": {},
            "service_dependencies": {},
            "sequential_patterns": [],
            "parallel_opportunities": []
        }
        
        # Analyze task dependencies (task-X.Y patterns)
        for target_name, target_info in makefile_analysis["targets"].items():
            if target_name.startswith("task-"):
                patterns["task_dependencies"][target_name] = {
                    "dependencies": target_info["dependencies"],
                    "task_number": self._extract_task_number(target_name),
                    "can_run_parallel": len(target_info["dependencies"]) == 0
                }
        
        # Analyze phase dependencies (phase-X patterns)
        for target_name, target_info in makefile_analysis["targets"].items():
            if target_name.startswith("phase-"):
                patterns["phase_dependencies"][target_name] = {
                    "dependencies": target_info["dependencies"],
                    "phase_number": self._extract_phase_number(target_name),
                    "coordination_required": True
                }
        
        # Identify sequential vs parallel execution patterns
        for chain_info in makefile_analysis["dependency_analysis"]["execution_chains"]:
            chain = chain_info["chain"]
            if len(chain) > 1:
                patterns["sequential_patterns"].append({
                    "workflow": chain_info["workflow"],
                    "sequence": chain,
                    "estimated_duration": chain_info["estimated_duration"]
                })
        
        return patterns
    
    def _extract_task_number(self, task_name: str) -> Optional[Tuple[int, int]]:
        """Extract task number from task-X.Y format."""
        import re
        match = re.match(r'task-(\d+)\.(\d+)', task_name)
        if match:
            return (int(match.group(1)), int(match.group(2)))
        return None
    
    def _extract_phase_number(self, phase_name: str) -> Optional[int]:
        """Extract phase number from phase-X format."""
        import re
        match = re.match(r'phase-(\d+)', phase_name)
        if match:
            return int(match.group(1))
        return None
    
    def map_python_script_parameter_passing(self) -> List[ParameterMapping]:
        """
        Map Python script parameter passing and environment requirements.
        
        Returns comprehensive mapping of parameter flows between scripts.
        """
        self._logger.info("Mapping Python script parameter passing...")
        
        parameter_mappings = []
        
        # Known script parameter mappings from the specification
        known_parameter_flows = [
            {
                "source": "observatory-daemon.py",
                "target": "WebSocket Endpoints",
                "parameters": [
                    {"name": "port", "type": "int", "env_var": "OBSERVATORY_PORT", "default": "8888"},
                    {"name": "host", "type": "str", "env_var": "OBSERVATORY_HOST", "default": "localhost"},
                    {"name": "websocket_endpoints", "type": "list", "required": True},
                    {"name": "redis_url", "type": "str", "env_var": "REDIS_URL", "required": True}
                ]
            },
            {
                "source": "tunnel management scripts",
                "target": "Cloudflare Tunnel",
                "parameters": [
                    {"name": "tunnel_id", "type": "str", "env_var": "CLOUDFLARE_TUNNEL_ID", "required": True},
                    {"name": "credentials_file", "type": "str", "env_var": "TUNNEL_CREDENTIALS", "required": True},
                    {"name": "config_file", "type": "str", "default": "cloudflared-config.yml"},
                    {"name": "ingress_rules", "type": "dict", "required": True}
                ]
            },
            {
                "source": "prometheus integration scripts",
                "target": "Prometheus Server",
                "parameters": [
                    {"name": "prometheus_url", "type": "str", "env_var": "PROMETHEUS_URL", "default": "http://localhost:9090"},
                    {"name": "scrape_configs", "type": "list", "required": True},
                    {"name": "alert_rules", "type": "list", "required": False},
                    {"name": "retention_period", "type": "str", "env_var": "PROMETHEUS_RETENTION", "default": "15d"}
                ]
            },
            {
                "source": "grafana configuration scripts",
                "target": "Grafana Dashboard",
                "parameters": [
                    {"name": "grafana_url", "type": "str", "env_var": "GRAFANA_URL", "default": "http://localhost:3000"},
                    {"name": "admin_password", "type": "str", "env_var": "GRAFANA_ADMIN_PASSWORD", "required": True},
                    {"name": "datasource_config", "type": "dict", "required": True},
                    {"name": "dashboard_configs", "type": "list", "required": False}
                ]
            }
        ]
        
        # Create parameter mappings
        for flow in known_parameter_flows:
            for param in flow["parameters"]:
                mapping = ParameterMapping(
                    source=flow["source"],
                    target=flow["target"],
                    parameter_name=param["name"],
                    parameter_type=param["type"],
                    required=param.get("required", True),
                    default_value=param.get("default"),
                    environment_variable=param.get("env_var")
                )
                parameter_mappings.append(mapping)
        
        # Add Makefile target parameter passing
        makefile_analysis = self._makefile_analyzer.get_comprehensive_analysis()
        for target_name, target_info in makefile_analysis["targets"].items():
            for command in target_info["commands"]:
                # Extract parameter patterns from commands
                param_mappings = self._extract_command_parameters(target_name, command)
                parameter_mappings.extend(param_mappings)
        
        self._parameter_mappings = parameter_mappings
        self._logger.info(f"Mapped {len(parameter_mappings)} parameter flows")
        return parameter_mappings
    
    def _extract_command_parameters(self, target_name: str, command: str) -> List[ParameterMapping]:
        """Extract parameter patterns from Makefile commands."""
        mappings = []
        
        # Look for environment variable usage patterns
        import re
        env_vars = re.findall(r'\$\{?([A-Z_]+)\}?', command)
        
        for env_var in env_vars:
            mapping = ParameterMapping(
                source=f"Makefile:{target_name}",
                target="Environment",
                parameter_name=env_var.lower(),
                parameter_type="str",
                required=True,
                environment_variable=env_var
            )
            mappings.append(mapping)
        
        # Look for script invocation patterns
        if "python" in command:
            script_match = re.search(r'python\s+([^\s]+)', command)
            if script_match:
                script_name = script_match.group(1)
                mapping = ParameterMapping(
                    source=f"Makefile:{target_name}",
                    target=script_name,
                    parameter_name="script_execution",
                    parameter_type="command",
                    required=True
                )
                mappings.append(mapping)
        
        return mappings
    
    def document_websocket_endpoint_registration_dependencies(self) -> List[WebSocketEndpointDependency]:
        """
        Document WebSocket endpoint registration dependencies.
        
        Returns comprehensive mapping of WebSocket endpoint dependencies and initialization order.
        """
        self._logger.info("Documenting WebSocket endpoint registration dependencies...")
        
        # Known WebSocket endpoints from the specification
        websocket_endpoints = [
            {
                "path": "/ws/observatory",
                "service": "Observatory Server",
                "dependencies": ["Observatory Server startup", "ReflectiveModule initialization"],
                "order": 1,
                "health_check": "/health",
                "message_types": ["system_events", "service_status", "metrics_updates"]
            },
            {
                "path": "/ws/emoji-rain",
                "service": "Observatory Server",
                "dependencies": ["Observatory Server startup", "/ws/observatory registration"],
                "order": 2,
                "health_check": "/health",
                "message_types": ["coordination_events", "achievement_notifications", "celebration_triggers"]
            },
            {
                "path": "/ws/anomalies",
                "service": "Observatory Server",
                "dependencies": ["Observatory Server startup", "Prometheus integration"],
                "order": 3,
                "health_check": "/health",
                "message_types": ["anomaly_alerts", "performance_warnings", "threshold_breaches"]
            },
            {
                "path": "/ws/doctor-status",
                "service": "Observatory Server",
                "dependencies": ["Observatory Server startup", "Health monitoring system"],
                "order": 4,
                "health_check": "/health",
                "message_types": ["health_updates", "diagnostic_results", "system_status"]
            }
        ]
        
        websocket_dependencies = []
        for endpoint in websocket_endpoints:
            dependency = WebSocketEndpointDependency(
                endpoint_path=endpoint["path"],
                service_name=endpoint["service"],
                dependencies=endpoint["dependencies"],
                initialization_order=endpoint["order"],
                health_check_endpoint=endpoint["health_check"],
                message_types=endpoint["message_types"]
            )
            websocket_dependencies.append(dependency)
        
        self._websocket_dependencies = websocket_dependencies
        self._logger.info(f"Documented {len(websocket_dependencies)} WebSocket endpoint dependencies")
        return websocket_dependencies
    
    def create_metrics_collection_pipeline_dependency_mapping(self) -> List[MetricsPipelineDependency]:
        """
        Create metrics collection pipeline dependency mapping.
        
        Returns comprehensive mapping of metrics flow through the observability stack.
        """
        self._logger.info("Creating metrics collection pipeline dependency mapping...")
        
        # Known metrics pipeline flows from the specification
        metrics_pipelines = [
            {
                "source": "ReflectiveModule Components",
                "target": "Observatory Server",
                "metrics": ["health_status", "performance_counters", "error_rates", "request_latency"],
                "interval": 30,  # seconds
                "aggregation": ["avg", "max", "count"],
                "alerts": {"error_rate_threshold": 0.05, "latency_threshold": 1000}
            },
            {
                "source": "Observatory Server",
                "target": "Prometheus Server",
                "metrics": ["observatory_requests", "websocket_connections", "system_metrics"],
                "interval": 15,  # seconds
                "aggregation": ["rate", "histogram"],
                "alerts": {"connection_threshold": 1000, "request_rate_threshold": 100}
            },
            {
                "source": "Prometheus Server",
                "target": "Grafana Dashboard",
                "metrics": ["all_collected_metrics"],
                "interval": 5,  # seconds (query interval)
                "aggregation": ["visualization", "alerting"],
                "alerts": {"dashboard_availability": True}
            },
            {
                "source": "WebSocket Endpoints",
                "target": "Observatory Server",
                "metrics": ["message_rates", "connection_counts", "error_counts"],
                "interval": 10,  # seconds
                "aggregation": ["sum", "rate"],
                "alerts": {"message_rate_threshold": 1000, "error_threshold": 10}
            },
            {
                "source": "ACE Reporter",
                "target": "AI Memory Palace",
                "metrics": ["progress_updates", "completion_status", "coordination_events"],
                "interval": 60,  # seconds
                "aggregation": ["latest", "count"],
                "alerts": {"coordination_failure": True}
            },
            {
                "source": "AI Memory Palace",
                "target": "DAG Registry",
                "metrics": ["context_storage", "retrieval_performance", "validation_results"],
                "interval": 120,  # seconds
                "aggregation": ["avg", "success_rate"],
                "alerts": {"validation_failure_threshold": 0.1}
            }
        ]
        
        metrics_dependencies = []
        for pipeline in metrics_pipelines:
            dependency = MetricsPipelineDependency(
                source_component=pipeline["source"],
                target_component=pipeline["target"],
                metric_types=pipeline["metrics"],
                collection_interval=pipeline["interval"],
                aggregation_rules=pipeline["aggregation"],
                alert_thresholds=pipeline["alerts"]
            )
            metrics_dependencies.append(dependency)
        
        self._metrics_dependencies = metrics_dependencies
        self._logger.info(f"Created {len(metrics_dependencies)} metrics pipeline dependencies")
        return metrics_dependencies
    
    def map_integration_point_coordination_workflows(self) -> List[IntegrationCoordination]:
        """
        Map integration point coordination workflows (ACE Reporter → AI Memory Palace → DAG Registry).
        
        Returns comprehensive mapping of integration coordination flows.
        """
        self._logger.info("Mapping integration point coordination workflows...")
        
        # Known integration coordination flows from the specification
        integration_flows = [
            {
                "name": "ACE Reporter to AI Memory Palace",
                "source": "ACE Reporter",
                "target": "AI Memory Palace",
                "method": "websocket",
                "direction": "source_to_target",
                "dependencies": ["Observatory WebSocket", "ACE Reporter initialization"],
                "validation": ["/ws/observatory", "/health"]
            },
            {
                "name": "AI Memory Palace to DAG Registry",
                "source": "AI Memory Palace",
                "target": "DAG Registry",
                "method": "direct",
                "direction": "bidirectional",
                "dependencies": ["AI Memory Palace startup", "DAG Registry availability"],
                "validation": ["/health", "/ready"]
            },
            {
                "name": "DAG Registry to Execution Engine",
                "source": "DAG Registry",
                "target": "Execution Engine",
                "method": "queue",
                "direction": "source_to_target",
                "dependencies": ["Redis coordination", "DAG validation"],
                "validation": ["Redis connectivity", "DAG structure validation"]
            },
            {
                "name": "Observatory to Prometheus",
                "source": "Observatory Server",
                "target": "Prometheus Server",
                "method": "direct",
                "direction": "source_to_target",
                "dependencies": ["Observatory metrics endpoint", "Prometheus scrape config"],
                "validation": ["/metrics", "Prometheus targets"]
            },
            {
                "name": "Prometheus to Grafana",
                "source": "Prometheus Server",
                "target": "Grafana Dashboard",
                "method": "direct",
                "direction": "source_to_target",
                "dependencies": ["Prometheus availability", "Grafana datasource config"],
                "validation": ["Prometheus API", "Grafana datasource test"]
            }
        ]
        
        integration_coordination = []
        for flow in integration_flows:
            coordination = IntegrationCoordination(
                integration_name=flow["name"],
                source_system=flow["source"],
                target_system=flow["target"],
                coordination_method=flow["method"],
                data_flow_direction=flow["direction"],
                dependencies=flow["dependencies"],
                validation_endpoints=flow["validation"]
            )
            integration_coordination.append(coordination)
        
        self._integration_coordination = integration_coordination
        self._logger.info(f"Mapped {len(integration_coordination)} integration coordination workflows")
        return integration_coordination
    
    def generate_automation_dependency_graphs_with_execution_order(self) -> AutomationDependencyGraph:
        """
        Generate automation dependency graphs with execution order using NetworkX.
        
        Returns comprehensive dependency graph with topological ordering for execution.
        """
        self._logger.info("Generating automation dependency graphs with execution order...")
        
        # Clear existing graph
        self._nx_graph.clear()
        
        # Add nodes from all analysis components
        nodes = []
        edges = []
        
        # Add Makefile targets as nodes
        makefile_analysis = self._makefile_analyzer.get_comprehensive_analysis()
        for target_name, target_info in makefile_analysis["targets"].items():
            node = {
                "id": target_name,
                "type": "makefile_target",
                "category": target_info["category"],
                "affected_components": target_info["affected_components"],
                "commands": target_info["commands"]
            }
            nodes.append(node)
            self._nx_graph.add_node(target_name, **node)
            
            # Add dependency edges
            for dep in target_info["dependencies"]:
                edge = {
                    "source": dep,
                    "target": target_name,
                    "type": "makefile_dependency",
                    "weight": 1
                }
                edges.append(edge)
                self._nx_graph.add_edge(dep, target_name, **edge)
        
        # Add WebSocket endpoints as nodes
        for ws_dep in self._websocket_dependencies:
            node = {
                "id": ws_dep.endpoint_path,
                "type": "websocket_endpoint",
                "service": ws_dep.service_name,
                "initialization_order": ws_dep.initialization_order,
                "message_types": ws_dep.message_types
            }
            nodes.append(node)
            self._nx_graph.add_node(ws_dep.endpoint_path, **node)
            
            # Add dependency edges
            for dep in ws_dep.dependencies:
                edge = {
                    "source": dep,
                    "target": ws_dep.endpoint_path,
                    "type": "websocket_dependency",
                    "weight": ws_dep.initialization_order
                }
                edges.append(edge)
                if dep in self._nx_graph:
                    self._nx_graph.add_edge(dep, ws_dep.endpoint_path, **edge)
        
        # Add metrics pipeline as nodes and edges
        for metrics_dep in self._metrics_dependencies:
            # Add edge for metrics flow
            edge = {
                "source": metrics_dep.source_component,
                "target": metrics_dep.target_component,
                "type": "metrics_pipeline",
                "metrics": metrics_dep.metric_types,
                "interval": metrics_dep.collection_interval,
                "weight": 1
            }
            edges.append(edge)
            
            # Ensure nodes exist
            for component in [metrics_dep.source_component, metrics_dep.target_component]:
                if component not in self._nx_graph:
                    node = {
                        "id": component,
                        "type": "metrics_component",
                        "category": "observability"
                    }
                    nodes.append(node)
                    self._nx_graph.add_node(component, **node)
            
            self._nx_graph.add_edge(metrics_dep.source_component, metrics_dep.target_component, **edge)
        
        # Add integration coordination as nodes and edges
        for integration in self._integration_coordination:
            edge = {
                "source": integration.source_system,
                "target": integration.target_system,
                "type": "integration_coordination",
                "method": integration.coordination_method,
                "direction": integration.data_flow_direction,
                "weight": 1
            }
            edges.append(edge)
            
            # Ensure nodes exist
            for system in [integration.source_system, integration.target_system]:
                if system not in self._nx_graph:
                    node = {
                        "id": system,
                        "type": "integration_system",
                        "category": "integration"
                    }
                    nodes.append(node)
                    self._nx_graph.add_node(system, **node)
            
            self._nx_graph.add_edge(integration.source_system, integration.target_system, **edge)
        
        # Calculate execution order using topological sort
        try:
            execution_order = list(nx.topological_sort(self._nx_graph))
        except nx.NetworkXError as e:
            self._logger.warning(f"Graph contains cycles, using partial ordering: {e}")
            # Use DFS to get partial ordering
            execution_order = list(nx.dfs_preorder_nodes(self._nx_graph))
        
        # Calculate critical path
        critical_path = self._calculate_critical_path()
        
        # Identify parallel execution groups
        parallel_groups = self._identify_parallel_groups()
        
        # Create dependency graph result
        dependency_graph = AutomationDependencyGraph(
            nodes=nodes,
            edges=edges,
            execution_order=execution_order,
            critical_path=critical_path,
            parallel_groups=parallel_groups
        )
        
        self._dependency_graph = dependency_graph
        self._logger.info(f"Generated dependency graph with {len(nodes)} nodes, {len(edges)} edges")
        return dependency_graph
    
    def _calculate_critical_path(self) -> List[str]:
        """Calculate critical path through the dependency graph."""
        try:
            # Find longest path (critical path) using DAG longest path algorithm
            if nx.is_directed_acyclic_graph(self._nx_graph):
                # Get topological ordering
                topo_order = list(nx.topological_sort(self._nx_graph))
                
                # Calculate longest paths
                distances = {node: 0 for node in self._nx_graph.nodes()}
                predecessors = {node: None for node in self._nx_graph.nodes()}
                
                for node in topo_order:
                    for successor in self._nx_graph.successors(node):
                        edge_weight = self._nx_graph[node][successor].get('weight', 1)
                        if distances[node] + edge_weight > distances[successor]:
                            distances[successor] = distances[node] + edge_weight
                            predecessors[successor] = node
                
                # Find the node with maximum distance (end of critical path)
                max_distance = max(distances.values())
                end_nodes = [node for node, dist in distances.items() if dist == max_distance]
                
                if end_nodes:
                    # Reconstruct critical path
                    critical_path = []
                    current = end_nodes[0]  # Take first end node
                    while current is not None:
                        critical_path.append(current)
                        current = predecessors[current]
                    
                    return list(reversed(critical_path))
            
        except Exception as e:
            self._logger.warning(f"Error calculating critical path: {e}")
        
        return []
    
    def _identify_parallel_groups(self) -> List[List[str]]:
        """Identify groups of nodes that can be executed in parallel."""
        parallel_groups = []
        
        try:
            if nx.is_directed_acyclic_graph(self._nx_graph):
                # Group nodes by their level in the DAG
                levels = {}
                for node in nx.topological_sort(self._nx_graph):
                    # Calculate level as maximum distance from any source
                    level = 0
                    for pred in self._nx_graph.predecessors(node):
                        level = max(level, levels.get(pred, 0) + 1)
                    levels[node] = level
                
                # Group nodes by level
                level_groups = {}
                for node, level in levels.items():
                    if level not in level_groups:
                        level_groups[level] = []
                    level_groups[level].append(node)
                
                # Convert to list of parallel groups
                for level in sorted(level_groups.keys()):
                    group = level_groups[level]
                    if len(group) > 1:  # Only include groups with multiple nodes
                        parallel_groups.append(group)
        
        except Exception as e:
            self._logger.warning(f"Error identifying parallel groups: {e}")
        
        return parallel_groups
    
    def get_comprehensive_automation_analysis(self) -> Dict[str, Any]:
        """
        Get comprehensive automation chain analysis report.
        
        Returns complete analysis including all components and dependency graphs.
        """
        self._logger.info("Generating comprehensive automation chain analysis...")
        
        # Perform all analyses
        makefile_dependencies = self.analyze_makefile_target_dependencies()
        parameter_mappings = self.map_python_script_parameter_passing()
        websocket_dependencies = self.document_websocket_endpoint_registration_dependencies()
        metrics_dependencies = self.create_metrics_collection_pipeline_dependency_mapping()
        integration_coordination = self.map_integration_point_coordination_workflows()
        dependency_graph = self.generate_automation_dependency_graphs_with_execution_order()
        
        # Create comprehensive report
        analysis_report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "module_id": self.module_id,
            "task_id": "2.3",
            "task_description": "Automation Chain Analysis",
            "summary": {
                "makefile_targets_analyzed": len(makefile_dependencies["target_dependencies"]),
                "parameter_mappings": len(parameter_mappings),
                "websocket_endpoints": len(websocket_dependencies),
                "metrics_pipelines": len(metrics_dependencies),
                "integration_flows": len(integration_coordination),
                "dependency_graph_nodes": len(dependency_graph.nodes),
                "dependency_graph_edges": len(dependency_graph.edges),
                "execution_order_length": len(dependency_graph.execution_order),
                "critical_path_length": len(dependency_graph.critical_path),
                "parallel_groups": len(dependency_graph.parallel_groups)
            },
            "makefile_dependencies": makefile_dependencies,
            "parameter_mappings": [
                {
                    "source": mapping.source,
                    "target": mapping.target,
                    "parameter_name": mapping.parameter_name,
                    "parameter_type": mapping.parameter_type,
                    "required": mapping.required,
                    "default_value": mapping.default_value,
                    "environment_variable": mapping.environment_variable
                }
                for mapping in parameter_mappings
            ],
            "websocket_dependencies": [
                {
                    "endpoint_path": dep.endpoint_path,
                    "service_name": dep.service_name,
                    "dependencies": dep.dependencies,
                    "initialization_order": dep.initialization_order,
                    "health_check_endpoint": dep.health_check_endpoint,
                    "message_types": dep.message_types
                }
                for dep in websocket_dependencies
            ],
            "metrics_dependencies": [
                {
                    "source_component": dep.source_component,
                    "target_component": dep.target_component,
                    "metric_types": dep.metric_types,
                    "collection_interval": dep.collection_interval,
                    "aggregation_rules": dep.aggregation_rules,
                    "alert_thresholds": dep.alert_thresholds
                }
                for dep in metrics_dependencies
            ],
            "integration_coordination": [
                {
                    "integration_name": coord.integration_name,
                    "source_system": coord.source_system,
                    "target_system": coord.target_system,
                    "coordination_method": coord.coordination_method,
                    "data_flow_direction": coord.data_flow_direction,
                    "dependencies": coord.dependencies,
                    "validation_endpoints": coord.validation_endpoints
                }
                for coord in integration_coordination
            ],
            "dependency_graph": {
                "nodes": dependency_graph.nodes,
                "edges": dependency_graph.edges,
                "execution_order": dependency_graph.execution_order,
                "critical_path": dependency_graph.critical_path,
                "parallel_groups": dependency_graph.parallel_groups
            },
            "networkx_graph_info": {
                "number_of_nodes": self._nx_graph.number_of_nodes(),
                "number_of_edges": self._nx_graph.number_of_edges(),
                "is_directed_acyclic_graph": nx.is_directed_acyclic_graph(self._nx_graph),
                "number_of_weakly_connected_components": nx.number_weakly_connected_components(self._nx_graph)
            },
            "recommendations": self._generate_automation_recommendations()
        }
        
        self._logger.info("Comprehensive automation chain analysis completed")
        return analysis_report
    
    def _generate_automation_recommendations(self) -> List[str]:
        """Generate recommendations based on automation analysis."""
        recommendations = []
        
        # Check for missing WebSocket endpoint dependencies
        if len(self._websocket_dependencies) < 4:
            recommendations.append("Ensure all WebSocket endpoints (/ws/observatory, /ws/emoji-rain, /ws/anomalies, /ws/doctor-status) are documented")
        
        # Check for metrics pipeline completeness
        if len(self._metrics_dependencies) < 5:
            recommendations.append("Complete metrics pipeline mapping for all observability components")
        
        # Check for integration coordination completeness
        if len(self._integration_coordination) < 3:
            recommendations.append("Document all integration coordination workflows (ACE Reporter → AI Memory Palace → DAG Registry)")
        
        # Check for circular dependencies in NetworkX graph
        if not nx.is_directed_acyclic_graph(self._nx_graph):
            recommendations.append("Resolve circular dependencies in automation dependency graph")
        
        # Check for isolated components
        isolated_nodes = list(nx.isolates(self._nx_graph))
        if isolated_nodes:
            recommendations.append(f"Review isolated components that may need integration: {', '.join(isolated_nodes[:5])}")
        
        # Check for parameter mapping completeness
        env_var_mappings = [m for m in self._parameter_mappings if m.environment_variable]
        if len(env_var_mappings) < 10:
            recommendations.append("Complete environment variable mapping for all script parameters")
        
        return recommendations
    
    def export_dependency_graph_to_networkx(self, output_path: str) -> bool:
        """Export NetworkX graph to file for external analysis."""
        try:
            import pickle
            with open(output_path, 'wb') as f:
                pickle.dump(self._nx_graph, f)
            self._logger.info(f"NetworkX graph exported to {output_path}")
            return True
        except Exception as e:
            self._logger.error(f"Error exporting NetworkX graph: {e}")
            return False
    
    def export_dependency_graph_to_graphml(self, output_path: str) -> bool:
        """Export dependency graph to GraphML format for visualization tools."""
        try:
            nx.write_graphml(self._nx_graph, output_path)
            self._logger.info(f"Dependency graph exported to GraphML: {output_path}")
            return True
        except Exception as e:
            self._logger.error(f"Error exporting to GraphML: {e}")
            return False
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - required by ReflectiveModule."""
        return {
            "module_id": self.module_id,
            "name": "Automation Chain Analyzer",
            "version": "1.0.0",
            "description": "Analyzes automation chain dependencies and creates comprehensive dependency graphs",
            "author": "System Architecture DAG",
            "task_id": "2.3",
            "capabilities": [
                "makefile_dependency_analysis",
                "parameter_mapping",
                "websocket_dependency_documentation",
                "metrics_pipeline_mapping",
                "integration_coordination_mapping",
                "networkx_graph_generation"
            ]
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - required by ReflectiveModule."""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING,
            ModuleCapability.ANALYSIS
        ]
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - required by ReflectiveModule."""
        return GracefulDegradationResult(
            success=True,
            message="Automation chain analyzer supports graceful degradation",
            fallback_capabilities=[
                ModuleCapability.CORE_FUNCTIONALITY,
                ModuleCapability.ANALYSIS
            ],
            recovery_suggestions=[
                "Retry with simpler dependency analysis",
                "Use basic makefile parsing without NetworkX",
                "Skip complex graph analysis if NetworkX unavailable"
            ]
        )
    
    def get_health_status(self) -> Dict[str, Any]:
        """Override ReflectiveModule health check."""
        return {
            "module": "AutomationChainAnalyzer",
            "status": "healthy",
            "task_id": "2.3",
            "analyses_completed": {
                "makefile_dependencies": len(self._makefile_analyzer._targets) > 0,
                "parameter_mappings": len(self._parameter_mappings) > 0,
                "websocket_dependencies": len(self._websocket_dependencies) > 0,
                "metrics_dependencies": len(self._metrics_dependencies) > 0,
                "integration_coordination": len(self._integration_coordination) > 0,
                "dependency_graph": self._dependency_graph is not None
            },
            "networkx_graph_stats": {
                "nodes": self._nx_graph.number_of_nodes(),
                "edges": self._nx_graph.number_of_edges(),
                "is_dag": nx.is_directed_acyclic_graph(self._nx_graph)
            }
        }


# Example usage and testing
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = AutomationChainAnalyzer()
    
    # Run comprehensive analysis
    analysis_report = analyzer.get_comprehensive_automation_analysis()
    
    # Print summary
    print("🔍 AUTOMATION CHAIN ANALYSIS COMPLETE")
    print("=" * 50)
    print(f"Task ID: {analysis_report['task_id']}")
    print(f"Analysis Timestamp: {analysis_report['analysis_timestamp']}")
    print("\n📊 SUMMARY:")
    for key, value in analysis_report['summary'].items():
        print(f"  {key}: {value}")
    
    print("\n🎯 RECOMMENDATIONS:")
    for i, rec in enumerate(analysis_report['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    # Export results
    output_file = f"automation_chain_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(analysis_report, f, indent=2)
    print(f"\n💾 Analysis exported to: {output_file}")
    
    # Export NetworkX graph
    analyzer.export_dependency_graph_to_graphml("automation_dependency_graph.graphml")
    print("📈 NetworkX graph exported to: automation_dependency_graph.graphml")