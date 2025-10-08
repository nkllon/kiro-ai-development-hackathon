#!/usr/bin/env python3
"""
Network Topology Visualizer - Task 3.3 Implementation
=====================================================

Creates NetworkTopologyVisualizer class using existing network topology discovery data.
Generates network flow diagrams with decision points using Mermaid graph format.
Includes WebSocket upgrade handling and connection flows for all Observatory endpoints.

Author: Beast Mode Framework
Date: 2025-01-03
Version: 1.0
"""

import logging
import json
import yaml
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleCapability, GracefulDegradationResult
from src.system_architecture.models.network_topology import (
    NetworkTopology, ServiceEndpoint, NetworkFlow, DNSMapping, 
    RedisCoordination, WebSocketConfiguration, FailoverMechanism,
    Protocol, FlowType, FailoverType, ServiceStatus
)
from src.system_architecture.models.diagram_models import (
    DiagramMetadata, DiagramComponent, DiagramRelationship, SecurityBoundary,
    DiagramType, DiagramFormat, ValidationStatus, SecurityLevel
)


@dataclass
class NetworkVisualizationConfig:
    """Configuration for network topology visualization."""
    output_directory: Path = Path("generated_diagrams/network")
    include_decision_points: bool = True
    include_websocket_flows: bool = True
    include_dns_propagation: bool = True
    include_failover_mechanisms: bool = True
    include_security_zones: bool = True
    mermaid_theme: str = "default"
    show_port_details: bool = True
    show_latency_info: bool = True
    show_bandwidth_limits: bool = True


@dataclass
class NetworkFlowDiagram:
    """Network flow diagram with decision points and routing logic."""
    flow_id: str
    title: str
    description: str
    source_nodes: List[str]
    target_nodes: List[str]
    decision_points: List[Dict[str, Any]]
    routing_rules: List[Dict[str, Any]]
    mermaid_content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WebSocketFlowDiagram:
    """WebSocket connection flow diagram with upgrade handling."""
    endpoint_path: str
    title: str
    description: str
    connection_flow: List[str]
    upgrade_sequence: List[Dict[str, Any]]
    message_types: List[str]
    mermaid_content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DNSPropagationDiagram:
    """DNS propagation timing and failover mechanism diagram."""
    domain: str
    title: str
    description: str
    propagation_steps: List[Dict[str, Any]]
    failover_targets: List[str]
    timing_estimates: Dict[str, str]
    mermaid_content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityZoneDiagram:
    """Security zones and access pattern documentation diagram."""
    zone_id: str
    title: str
    description: str
    security_zones: List[Dict[str, Any]]
    access_patterns: List[Dict[str, Any]]
    authentication_flows: List[Dict[str, Any]]
    mermaid_content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class NetworkTopologyVisualizer(ReflectiveModule):
    """
    Creates network topology visualizations using existing network topology discovery data.
    
    Implements Task 3.3 from the system architecture wiring diagram specification.
    Generates interactive network flow diagrams with decision points, WebSocket connection
    flows, DNS propagation documentation, and security zone visualizations.
    """
    
    def __init__(self, config: Optional[NetworkVisualizationConfig] = None):
        super().__init__()
        self.module_id = "NetworkTopologyVisualizer"
        self._logger = logging.getLogger(f"system_architecture.{self.__class__.__name__}")
        
        # Configuration
        self._config = config or NetworkVisualizationConfig()
        
        # Ensure output directory exists
        self._config.output_directory.mkdir(parents=True, exist_ok=True)
        
        # Generated diagrams cache
        self._network_flow_diagrams: Dict[str, NetworkFlowDiagram] = {}
        self._websocket_flow_diagrams: Dict[str, WebSocketFlowDiagram] = {}
        self._dns_propagation_diagrams: Dict[str, DNSPropagationDiagram] = {}
        self._security_zone_diagrams: Dict[str, SecurityZoneDiagram] = {}
        
        # Known infrastructure constants from specification
        self._cloudflare_tunnel_id = "d1e53e43-033f-4994-8f46-c83962ae3785"
        self._known_domains = [
            "observatory.nkllon.com",
            "grafana.observatory.nkllon.com", 
            "prometheus.observatory.nkllon.com"
        ]
        self._service_ports = {
            "Observatory": 8888,
            "Prometheus": 9090,
            "Grafana": 3000,
            "Directus": 8055
        }
        self._websocket_endpoints = [
            "/ws/observatory",
            "/ws/emoji-rain", 
            "/ws/anomalies",
            "/ws/doctor-status"
        ]
        
        self._logger.info("NetworkTopologyVisualizer initialized")
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION
        ]
    
    def generate_network_flow_diagrams(self, topology: NetworkTopology) -> List[NetworkFlowDiagram]:
        """
        Generate network flow diagrams with decision points using Mermaid graph format.
        
        Args:
            topology: Network topology data
            
        Returns:
            List of network flow diagrams with decision points and routing logic
        """
        self._logger.info("Generating network flow diagrams with decision points...")
        
        diagrams = []
        
        # Generate main network flow diagram
        main_flow = self._generate_main_network_flow(topology)
        diagrams.append(main_flow)
        
        # Generate service-specific flow diagrams
        for service in topology.service_endpoints:
            service_flow = self._generate_service_flow_diagram(service, topology)
            diagrams.append(service_flow)
        
        # Generate Cloudflare tunnel routing diagram
        tunnel_flow = self._generate_tunnel_routing_diagram(topology)
        diagrams.append(tunnel_flow)
        
        # Generate Redis coordination flow diagram
        if topology.redis_coordination:
            redis_flow = self._generate_redis_coordination_diagram(topology.redis_coordination)
            diagrams.append(redis_flow)
        
        # Cache generated diagrams
        for diagram in diagrams:
            self._network_flow_diagrams[diagram.flow_id] = diagram
        
        self._logger.info(f"Generated {len(diagrams)} network flow diagrams")
        return diagrams
    
    def _generate_main_network_flow(self, topology: NetworkTopology) -> NetworkFlowDiagram:
        """Generate main network flow diagram showing overall topology."""
        
        # Create Mermaid flowchart
        mermaid_content = f"""
graph TD
    %% Main Network Flow - {topology.local_network_range}
    %% Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    Internet[Internet Users]
    CloudflareEdge[Cloudflare Edge Network]
    Tunnel[Cloudflare Tunnel<br/>{self._cloudflare_tunnel_id[:8]}...]
    LocalNetwork[Local Network<br/>{topology.local_network_range}]
    
    %% External to Internal Flow
    Internet -->|HTTPS/WSS| CloudflareEdge
    CloudflareEdge -->|Encrypted Tunnel| Tunnel
    Tunnel -->|Local Routing| LocalNetwork
    
    %% Service Endpoints
"""
        
        # Add service endpoints
        for service in topology.service_endpoints:
            service_id = service.name.replace(" ", "").replace("-", "")
            status_icon = self._get_service_status_icon(service.status)
            
            mermaid_content += f"    {service_id}[{status_icon} {service.name}<br/>{service.host}:{service.port}]\n"
            mermaid_content += f"    LocalNetwork -->|{service.protocol.value.upper()}| {service_id}\n"
        
        # Add decision points
        mermaid_content += """
    
    %% Decision Points
    CloudflareEdge -->|DNS Resolution| DNSDecision{Domain?}
    DNSDecision -->|observatory.nkllon.com| Observatory
    DNSDecision -->|grafana.observatory.nkllon.com| Grafana  
    DNSDecision -->|prometheus.observatory.nkllon.com| Prometheus
    
    %% WebSocket Upgrade Decision
    Observatory -->|HTTP Request| WSDecision{WebSocket Upgrade?}
    WSDecision -->|Yes| WSEndpoints[WebSocket Endpoints]
    WSDecision -->|No| HTTPEndpoints[HTTP Endpoints]
    
    %% Styling
    classDef serviceNode fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef decisionNode fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef tunnelNode fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    
    class Observatory,Prometheus,Grafana,Directus serviceNode
    class DNSDecision,WSDecision decisionNode
    class Tunnel,CloudflareEdge tunnelNode
"""
        
        # Create decision points from topology
        decision_points = [
            {
                "point_id": "dns_resolution",
                "description": "DNS domain routing decision",
                "conditions": [f"Domain matches {domain}" for domain in self._known_domains],
                "outcomes": ["Route to Observatory", "Route to Grafana", "Route to Prometheus"]
            },
            {
                "point_id": "websocket_upgrade", 
                "description": "WebSocket protocol upgrade decision",
                "conditions": ["Upgrade header present", "WebSocket protocol requested"],
                "outcomes": ["Upgrade to WebSocket", "Continue with HTTP"]
            },
            {
                "point_id": "service_routing",
                "description": "Internal service routing decision", 
                "conditions": [f"Port {port}" for port in self._service_ports.values()],
                "outcomes": [f"Route to {service}" for service in self._service_ports.keys()]
            }
        ]
        
        # Create routing rules
        routing_rules = []
        for dns_mapping in topology.dns_mappings:
            routing_rules.append({
                "rule_id": f"dns_route_{dns_mapping.domain.replace('.', '_')}",
                "condition": f"Host header == {dns_mapping.domain}",
                "action": f"Route to {dns_mapping.target_service}:{dns_mapping.target_port}",
                "priority": 1,
                "failover": dns_mapping.failover_targets
            })
        
        return NetworkFlowDiagram(
            flow_id="main_network_flow",
            title="Main Network Flow Topology",
            description=f"Complete network flow from Internet through Cloudflare tunnel to local services ({topology.local_network_range})",
            source_nodes=["Internet", "CloudflareEdge"],
            target_nodes=[service.name for service in topology.service_endpoints],
            decision_points=decision_points,
            routing_rules=routing_rules,
            mermaid_content=mermaid_content,
            metadata={
                "tunnel_id": self._cloudflare_tunnel_id,
                "network_range": topology.local_network_range,
                "service_count": len(topology.service_endpoints),
                "dns_mappings": len(topology.dns_mappings)
            }
        )
    
    def _generate_service_flow_diagram(self, service: ServiceEndpoint, topology: NetworkTopology) -> NetworkFlowDiagram:
        """Generate flow diagram for a specific service."""
        
        service_id = service.name.replace(" ", "").replace("-", "")
        status_icon = self._get_service_status_icon(service.status)
        
        mermaid_content = f"""
graph LR
    %% {service.name} Service Flow
    %% Host: {service.host}:{service.port}
    %% Protocol: {service.protocol.value.upper()}
    %% Status: {service.status.value}
    
    Client[Client Request]
    LoadBalancer[Load Balancer]
    {service_id}[{status_icon} {service.name}<br/>{service.host}:{service.port}]
    
    Client -->|{service.protocol.value.upper()}| LoadBalancer
    LoadBalancer -->|Route| {service_id}
"""
        
        # Add WebSocket endpoints if available
        if service.websocket_endpoints:
            mermaid_content += f"""
    
    %% WebSocket Endpoints
    {service_id} -->|WebSocket Upgrade| WSHandler[WebSocket Handler]
"""
            for i, ws_endpoint in enumerate(service.websocket_endpoints):
                endpoint_id = f"WS{i+1}"
                mermaid_content += f"    WSHandler -->|{ws_endpoint}| {endpoint_id}[{ws_endpoint}]\n"
        
        # Add health endpoint if available
        if service.health_endpoint:
            mermaid_content += f"""
    
    %% Health Monitoring
    HealthChecker[Health Checker] -->|GET {service.health_endpoint}| {service_id}
    {service_id} -->|Status Response| HealthChecker
"""
        
        # Add dependencies
        if service.dependencies:
            mermaid_content += "\n    %% Service Dependencies\n"
            for dep in service.dependencies:
                dep_id = dep.replace(" ", "").replace("-", "")
                mermaid_content += f"    {service_id} -.->|depends on| {dep_id}[{dep}]\n"
        
        # Add styling
        mermaid_content += f"""
    
    %% Styling
    classDef serviceNode fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef wsNode fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef healthNode fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    
    class {service_id} serviceNode
    class WSHandler,WS1,WS2,WS3,WS4 wsNode
    class HealthChecker healthNode
"""
        
        # Create decision points for this service
        decision_points = []
        if service.websocket_endpoints:
            decision_points.append({
                "point_id": f"{service_id.lower()}_protocol_decision",
                "description": f"Protocol decision for {service.name}",
                "conditions": ["WebSocket upgrade requested", "HTTP request"],
                "outcomes": ["Handle WebSocket connection", "Handle HTTP request"]
            })
        
        if service.health_endpoint:
            decision_points.append({
                "point_id": f"{service_id.lower()}_health_decision", 
                "description": f"Health check routing for {service.name}",
                "conditions": [f"Path == {service.health_endpoint}"],
                "outcomes": ["Return health status", "Route to main handler"]
            })
        
        return NetworkFlowDiagram(
            flow_id=f"service_flow_{service_id.lower()}",
            title=f"{service.name} Service Flow",
            description=f"Network flow diagram for {service.name} service on {service.host}:{service.port}",
            source_nodes=["Client", "LoadBalancer"],
            target_nodes=[service.name],
            decision_points=decision_points,
            routing_rules=[],
            mermaid_content=mermaid_content,
            metadata={
                "service_name": service.name,
                "host": service.host,
                "port": service.port,
                "protocol": service.protocol.value,
                "status": service.status.value,
                "websocket_endpoints": service.websocket_endpoints,
                "health_endpoint": service.health_endpoint,
                "dependencies": service.dependencies
            }
        )
    
    def _generate_tunnel_routing_diagram(self, topology: NetworkTopology) -> NetworkFlowDiagram:
        """Generate Cloudflare tunnel routing diagram with WebSocket proxy configuration."""
        
        mermaid_content = f"""
graph TD
    %% Cloudflare Tunnel Routing Configuration
    %% Tunnel ID: {self._cloudflare_tunnel_id}
    %% WebSocket Support: Enabled
    
    Internet[Internet Traffic]
    CloudflareEdge[Cloudflare Edge<br/>Global Network]
    TunnelAuth[Tunnel Authentication<br/>Credentials Validation]
    TunnelProxy[Tunnel Proxy<br/>{self._cloudflare_tunnel_id[:8]}...]
    
    Internet -->|HTTPS/WSS| CloudflareEdge
    CloudflareEdge -->|Authenticate| TunnelAuth
    TunnelAuth -->|Authorized| TunnelProxy
    
    %% Ingress Rules
    TunnelProxy -->|Host: observatory.nkllon.com| ObservatoryRoute[Observatory Server<br/>localhost:8888]
    TunnelProxy -->|Host: grafana.observatory.nkllon.com| GrafanaRoute[Grafana Dashboard<br/>localhost:3000]  
    TunnelProxy -->|Host: prometheus.observatory.nkllon.com| PrometheusRoute[Prometheus Server<br/>localhost:9090]
    
    %% WebSocket Proxy Configuration
    ObservatoryRoute -->|WebSocket Upgrade| WSProxy[WebSocket Proxy<br/>Connection Pooling]
    WSProxy -->|/ws/observatory| WSObservatory[Observatory Events]
    WSProxy -->|/ws/emoji-rain| WSEmojiRain[Emoji Rain Stream]
    WSProxy -->|/ws/anomalies| WSAnomalies[Anomaly Alerts]
    WSProxy -->|/ws/doctor-status| WSDoctor[Health Status]
    
    %% Failover Mechanisms
    TunnelProxy -.->|Failover| BackupTunnel[Backup Tunnel<br/>Auto-failover]
    ObservatoryRoute -.->|Health Check Failed| HealthFailover[Health Check Failover<br/>503 Service Unavailable]
    
    %% Styling
    classDef tunnelNode fill:#e8eaf6,stroke:#3f51b5,stroke-width:2px
    classDef serviceNode fill:#e8f5e8,stroke:#4caf50,stroke-width:2px
    classDef wsNode fill:#e1f5fe,stroke:#03a9f4,stroke-width:2px
    classDef failoverNode fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    
    class CloudflareEdge,TunnelAuth,TunnelProxy tunnelNode
    class ObservatoryRoute,GrafanaRoute,PrometheusRoute serviceNode
    class WSProxy,WSObservatory,WSEmojiRain,WSAnomalies,WSDoctor wsNode
    class BackupTunnel,HealthFailover failoverNode
"""
        
        # Create decision points for tunnel routing
        decision_points = [
            {
                "point_id": "tunnel_authentication",
                "description": "Tunnel authentication and authorization",
                "conditions": ["Valid tunnel credentials", "Authorized origin"],
                "outcomes": ["Allow tunnel connection", "Reject connection"]
            },
            {
                "point_id": "host_based_routing",
                "description": "Host header based routing decision",
                "conditions": [f"Host == {domain}" for domain in self._known_domains],
                "outcomes": ["Route to Observatory", "Route to Grafana", "Route to Prometheus", "Return 404"]
            },
            {
                "point_id": "websocket_proxy_decision",
                "description": "WebSocket proxy routing decision",
                "conditions": ["WebSocket upgrade request", "Valid WebSocket endpoint"],
                "outcomes": ["Proxy WebSocket connection", "Handle HTTP request", "Return 404"]
            }
        ]
        
        # Create routing rules from DNS mappings
        routing_rules = []
        for dns_mapping in topology.dns_mappings:
            routing_rules.append({
                "rule_id": f"tunnel_route_{dns_mapping.domain.replace('.', '_')}",
                "condition": f"Host == {dns_mapping.domain}",
                "action": f"Proxy to {dns_mapping.target_service}:{dns_mapping.target_port}",
                "priority": 1,
                "websocket_support": True,
                "ssl_termination": True,
                "failover_targets": dns_mapping.failover_targets
            })
        
        return NetworkFlowDiagram(
            flow_id="cloudflare_tunnel_routing",
            title="Cloudflare Tunnel Routing Configuration",
            description=f"Cloudflare tunnel ({self._cloudflare_tunnel_id}) routing with WebSocket proxy configuration",
            source_nodes=["Internet", "CloudflareEdge"],
            target_nodes=["Observatory", "Grafana", "Prometheus"],
            decision_points=decision_points,
            routing_rules=routing_rules,
            mermaid_content=mermaid_content,
            metadata={
                "tunnel_id": self._cloudflare_tunnel_id,
                "domains": self._known_domains,
                "websocket_support": True,
                "ssl_termination": True,
                "ingress_rules": len(topology.dns_mappings)
            }
        )
    
    def _generate_redis_coordination_diagram(self, redis_config: RedisCoordination) -> NetworkFlowDiagram:
        """Generate Redis coordination flow diagram with failover logic."""
        
        mermaid_content = f"""
graph TD
    %% Redis Coordination Flow
    %% Primary: {redis_config.primary_endpoint}
    %% Failover: {', '.join(redis_config.fallback_endpoints)}
    %% Cluster Mode: {redis_config.cluster_mode}
    
    Client[Application Client]
    ConnectionPool[Connection Pool<br/>Size: {redis_config.connection_pool_size}]
    HealthChecker[Health Monitor<br/>Interval: {redis_config.timeout_seconds}s]
    
    Client -->|Redis Commands| ConnectionPool
    HealthChecker -->|Health Check| ConnectionPool
    
    %% Primary Redis
    ConnectionPool -->|Primary Connection| RedisPrimary[Redis Primary<br/>{redis_config.primary_endpoint}]
    
    %% Failover Logic
    ConnectionPool -->|Health Check Failed| FailoverDecision{{Failover Required?}}
    FailoverDecision -->|Yes| RedisFailover[Redis Failover<br/>{redis_config.fallback_endpoints[0] if redis_config.fallback_endpoints else 'localhost:6380'}]
    FailoverDecision -->|No| RedisPrimary
    
    %% Cluster Mode (if enabled)
"""
        
        if redis_config.cluster_mode:
            mermaid_content += """
    RedisPrimary -->|Cluster Discovery| ClusterNodes[Redis Cluster Nodes]
    RedisFailover -->|Cluster Discovery| ClusterNodes
    ClusterNodes -->|Shard Routing| Shard1[Shard 1]
    ClusterNodes -->|Shard Routing| Shard2[Shard 2]
    ClusterNodes -->|Shard Routing| Shard3[Shard 3]
"""
        
        mermaid_content += f"""
    
    %% Monitoring and Alerts
    HealthChecker -->|Status Update| MonitoringSystem[Monitoring System]
    MonitoringSystem -->|Alert| AlertManager[Alert Manager]
    
    %% Recovery Process
    RedisFailover -.->|Auto Recovery| RecoveryProcess[Recovery Process<br/>Max Retries: {redis_config.retry_attempts}]
    RecoveryProcess -.->|Primary Restored| RedisPrimary
    
    %% Styling
    classDef redisNode fill:#dc382d,color:#ffffff,stroke:#a91e2c,stroke-width:2px
    classDef failoverNode fill:#ff9800,color:#ffffff,stroke:#f57c00,stroke-width:2px
    classDef monitoringNode fill:#4caf50,color:#ffffff,stroke:#388e3c,stroke-width:2px
    classDef decisionNode fill:#2196f3,color:#ffffff,stroke:#1976d2,stroke-width:2px
    
    class RedisPrimary,RedisFailover,Shard1,Shard2,Shard3 redisNode
    class RecoveryProcess,AlertManager failoverNode
    class HealthChecker,MonitoringSystem monitoringNode
    class FailoverDecision decisionNode
"""
        
        # Create decision points for Redis coordination
        decision_points = [
            {
                "point_id": "redis_health_check",
                "description": "Redis primary health check decision",
                "conditions": ["Primary responds within timeout", "Primary connection failed"],
                "outcomes": ["Continue with primary", "Initiate failover"]
            },
            {
                "point_id": "failover_target_selection",
                "description": "Failover target selection decision",
                "conditions": [f"Fallback {i+1} available" for i in range(len(redis_config.fallback_endpoints))],
                "outcomes": ["Use fallback", "Connection failed"]
            }
        ]
        
        if redis_config.cluster_mode:
            decision_points.append({
                "point_id": "cluster_shard_routing",
                "description": "Redis cluster shard routing decision", 
                "conditions": ["Key hash calculation", "Shard availability check"],
                "outcomes": ["Route to appropriate shard", "Cluster error"]
            })
        
        return NetworkFlowDiagram(
            flow_id="redis_coordination_flow",
            title="Redis Coordination Flow with Failover",
            description=f"Redis coordination flow with primary ({redis_config.primary_endpoint}) and failover mechanisms",
            source_nodes=["Client", "ConnectionPool"],
            target_nodes=["RedisPrimary", "RedisFailover"],
            decision_points=decision_points,
            routing_rules=[],
            mermaid_content=mermaid_content,
            metadata={
                "primary_endpoint": redis_config.primary_endpoint,
                "fallback_endpoints": redis_config.fallback_endpoints,
                "cluster_mode": redis_config.cluster_mode,
                "connection_pool_size": redis_config.connection_pool_size,
                "timeout_seconds": redis_config.timeout_seconds,
                "retry_attempts": redis_config.retry_attempts,
                "health_status": redis_config.health_status
            }
        )
    
    def generate_websocket_connection_flows(self, topology: NetworkTopology) -> List[WebSocketFlowDiagram]:
        """
        Generate WebSocket connection flow visualization with upgrade handling.
        
        Args:
            topology: Network topology data
            
        Returns:
            List of WebSocket flow diagrams with connection establishment flows
        """
        self._logger.info("Generating WebSocket connection flow diagrams...")
        
        diagrams = []
        
        # Generate flow for each WebSocket endpoint
        for endpoint in self._websocket_endpoints:
            ws_flow = self._generate_websocket_flow_diagram(endpoint, topology)
            diagrams.append(ws_flow)
        
        # Generate general WebSocket upgrade flow
        upgrade_flow = self._generate_websocket_upgrade_flow()
        diagrams.append(upgrade_flow)
        
        # Cache generated diagrams
        for diagram in diagrams:
            self._websocket_flow_diagrams[diagram.endpoint_path] = diagram
        
        self._logger.info(f"Generated {len(diagrams)} WebSocket flow diagrams")
        return diagrams
    
    def _generate_websocket_flow_diagram(self, endpoint: str, topology: NetworkTopology) -> WebSocketFlowDiagram:
        """Generate WebSocket flow diagram for specific endpoint."""
        
        endpoint_id = endpoint.replace("/", "").replace("-", "")
        
        mermaid_content = f"""
sequenceDiagram
    participant Client
    participant CloudflareTunnel as Cloudflare Tunnel
    participant Observatory as Observatory Server
    participant WSHandler as WebSocket Handler
    participant {endpoint_id} as {endpoint}
    
    Note over Client,{endpoint_id}: WebSocket Connection Flow for {endpoint}
    
    %% Initial HTTP Request
    Client->>CloudflareTunnel: HTTP GET {endpoint}
    Note right of Client: Upgrade: websocket<br/>Connection: Upgrade<br/>Sec-WebSocket-Key: [key]
    
    %% Tunnel Proxy
    CloudflareTunnel->>Observatory: Proxy HTTP Request
    Note right of CloudflareTunnel: WebSocket headers preserved<br/>Origin validation
    
    %% WebSocket Upgrade
    Observatory->>WSHandler: Route to WebSocket Handler
    WSHandler->>WSHandler: Validate WebSocket Request
    
    alt Valid WebSocket Request
        WSHandler->>Observatory: Accept WebSocket Upgrade
        Observatory->>CloudflareTunnel: 101 Switching Protocols
        CloudflareTunnel->>Client: 101 Switching Protocols
        Note right of Observatory: Sec-WebSocket-Accept: [hash]<br/>Connection established
        
        %% WebSocket Communication
        Client->>CloudflareTunnel: WebSocket Message
        CloudflareTunnel->>Observatory: Proxy WebSocket Message
        Observatory->>WSHandler: Route Message
        WSHandler->>{endpoint_id}: Handle Message
        
        %% Response Flow
        {endpoint_id}->>WSHandler: Response Message
        WSHandler->>Observatory: Send Response
        Observatory->>CloudflareTunnel: WebSocket Response
        CloudflareTunnel->>Client: WebSocket Response
        
    else Invalid Request
        WSHandler->>Observatory: Reject Request
        Observatory->>CloudflareTunnel: 400 Bad Request
        CloudflareTunnel->>Client: 400 Bad Request
    end
    
    %% Connection Maintenance
    loop Heartbeat (every 30s)
        Client->>CloudflareTunnel: Ping Frame
        CloudflareTunnel->>Observatory: Proxy Ping
        Observatory->>CloudflareTunnel: Pong Frame
        CloudflareTunnel->>Client: Pong Frame
    end
    
    %% Connection Termination
    Client->>CloudflareTunnel: Close Frame
    CloudflareTunnel->>Observatory: Proxy Close
    Observatory->>WSHandler: Handle Close
    WSHandler->>Observatory: Acknowledge Close
    Observatory->>CloudflareTunnel: Close Frame
    CloudflareTunnel->>Client: Close Frame
"""
        
        # Define connection flow steps
        connection_flow = [
            "Client initiates HTTP request with WebSocket upgrade headers",
            "Cloudflare tunnel proxies request with header preservation",
            "Observatory server routes to WebSocket handler",
            "WebSocket handler validates upgrade request",
            "Server responds with 101 Switching Protocols",
            "WebSocket connection established",
            "Bidirectional message exchange begins",
            "Heartbeat mechanism maintains connection",
            "Connection closed gracefully with close frames"
        ]
        
        # Define upgrade sequence
        upgrade_sequence = [
            {
                "step": 1,
                "action": "Client sends HTTP GET with upgrade headers",
                "headers": ["Upgrade: websocket", "Connection: Upgrade", "Sec-WebSocket-Key: [random]"],
                "timing": "0ms"
            },
            {
                "step": 2, 
                "action": "Server validates WebSocket request",
                "validation": ["Check Upgrade header", "Validate WebSocket key", "Check origin"],
                "timing": "5-10ms"
            },
            {
                "step": 3,
                "action": "Server responds with 101 Switching Protocols", 
                "headers": ["HTTP/1.1 101 Switching Protocols", "Upgrade: websocket", "Connection: Upgrade", "Sec-WebSocket-Accept: [hash]"],
                "timing": "10-20ms"
            },
            {
                "step": 4,
                "action": "WebSocket connection established",
                "result": "Bidirectional communication channel active",
                "timing": "20-30ms"
            }
        ]
        
        # Define message types for this endpoint
        message_types = self._get_endpoint_message_types(endpoint)
        
        return WebSocketFlowDiagram(
            endpoint_path=endpoint,
            title=f"WebSocket Connection Flow - {endpoint}",
            description=f"Complete WebSocket connection establishment and communication flow for {endpoint}",
            connection_flow=connection_flow,
            upgrade_sequence=upgrade_sequence,
            message_types=message_types,
            mermaid_content=mermaid_content,
            metadata={
                "endpoint": endpoint,
                "server": "Observatory Server",
                "port": 8888,
                "tunnel_support": True,
                "heartbeat_interval": 30,
                "max_message_size": "1MB",
                "compression": "deflate-frame"
            }
        )
    
    def _generate_websocket_upgrade_flow(self) -> WebSocketFlowDiagram:
        """Generate general WebSocket upgrade flow diagram."""
        
        mermaid_content = """
graph TD
    %% WebSocket Upgrade Process
    %% RFC 6455 Compliant Implementation
    
    HTTPRequest[HTTP GET Request<br/>with Upgrade Headers]
    ValidateHeaders{Validate<br/>WebSocket Headers?}
    CheckOrigin{Check<br/>Origin Policy?}
    GenerateAccept[Generate<br/>Sec-WebSocket-Accept]
    SendUpgrade[Send 101<br/>Switching Protocols]
    WSConnection[WebSocket<br/>Connection Active]
    
    HTTPRequest --> ValidateHeaders
    ValidateHeaders -->|Valid| CheckOrigin
    ValidateHeaders -->|Invalid| RejectBadRequest[400 Bad Request]
    
    CheckOrigin -->|Allowed| GenerateAccept
    CheckOrigin -->|Forbidden| RejectForbidden[403 Forbidden]
    
    GenerateAccept --> SendUpgrade
    SendUpgrade --> WSConnection
    
    %% WebSocket Frame Handling
    WSConnection --> FrameHandler[WebSocket Frame Handler]
    FrameHandler --> TextFrame[Text Frame]
    FrameHandler --> BinaryFrame[Binary Frame]
    FrameHandler --> PingFrame[Ping Frame]
    FrameHandler --> PongFrame[Pong Frame]
    FrameHandler --> CloseFrame[Close Frame]
    
    %% Frame Processing
    TextFrame --> MessageProcessor[Message Processor]
    BinaryFrame --> MessageProcessor
    PingFrame --> AutoPong[Auto Pong Response]
    PongFrame --> HeartbeatTracker[Heartbeat Tracker]
    CloseFrame --> ConnectionClose[Connection Close]
    
    %% Styling
    classDef httpNode fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef wsNode fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef errorNode fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    classDef frameNode fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    
    class HTTPRequest,ValidateHeaders,CheckOrigin,GenerateAccept,SendUpgrade httpNode
    class WSConnection,FrameHandler,MessageProcessor,HeartbeatTracker wsNode
    class RejectBadRequest,RejectForbidden,ConnectionClose errorNode
    class TextFrame,BinaryFrame,PingFrame,PongFrame,CloseFrame frameNode
"""
        
        connection_flow = [
            "HTTP GET request received with WebSocket upgrade headers",
            "Server validates required WebSocket headers (Upgrade, Connection, Sec-WebSocket-Key)",
            "Server checks origin policy and security constraints",
            "Server generates Sec-WebSocket-Accept hash using magic string",
            "Server responds with 101 Switching Protocols status",
            "WebSocket connection established, HTTP connection upgraded",
            "Frame-based communication begins using WebSocket protocol",
            "Ping/Pong frames maintain connection liveness",
            "Close frame initiates graceful connection termination"
        ]
        
        upgrade_sequence = [
            {
                "step": 1,
                "action": "Validate WebSocket headers",
                "required_headers": ["Upgrade: websocket", "Connection: Upgrade", "Sec-WebSocket-Key"],
                "timing": "1-2ms"
            },
            {
                "step": 2,
                "action": "Check security policies",
                "checks": ["Origin validation", "Rate limiting", "Authentication"],
                "timing": "2-5ms"
            },
            {
                "step": 3,
                "action": "Generate accept key",
                "algorithm": "SHA-1 hash of (Sec-WebSocket-Key + magic string)",
                "timing": "1ms"
            },
            {
                "step": 4,
                "action": "Send upgrade response",
                "response": "101 Switching Protocols with Sec-WebSocket-Accept",
                "timing": "1-2ms"
            }
        ]
        
        return WebSocketFlowDiagram(
            endpoint_path="/ws/upgrade",
            title="WebSocket Upgrade Process",
            description="General WebSocket protocol upgrade process (RFC 6455 compliant)",
            connection_flow=connection_flow,
            upgrade_sequence=upgrade_sequence,
            message_types=["text", "binary", "ping", "pong", "close"],
            mermaid_content=mermaid_content,
            metadata={
                "rfc": "RFC 6455",
                "protocol_version": "13",
                "magic_string": "258EAFA5-E914-47DA-95CA-C5AB0DC85B11",
                "frame_types": ["text", "binary", "close", "ping", "pong"],
                "max_frame_size": "2^63 bytes"
            }
        )
    
    def _get_endpoint_message_types(self, endpoint: str) -> List[str]:
        """Get message types for specific WebSocket endpoint."""
        message_types_map = {
            "/ws/observatory": ["system_events", "service_status", "metrics_updates", "health_reports"],
            "/ws/emoji-rain": ["coordination_events", "achievement_notifications", "celebration_triggers", "progress_updates"],
            "/ws/anomalies": ["anomaly_alerts", "performance_warnings", "threshold_breaches", "error_notifications"],
            "/ws/doctor-status": ["health_updates", "diagnostic_results", "system_status", "component_health"]
        }
        return message_types_map.get(endpoint, ["generic_message"])
    
    def generate_dns_propagation_documentation(self, topology: NetworkTopology) -> List[DNSPropagationDiagram]:
        """
        Generate DNS propagation timing and failover mechanism documentation.
        
        Args:
            topology: Network topology data
            
        Returns:
            List of DNS propagation diagrams with timing estimates and failover mechanisms
        """
        self._logger.info("Generating DNS propagation documentation...")
        
        diagrams = []
        
        # Generate propagation diagram for each DNS mapping
        for dns_mapping in topology.dns_mappings:
            propagation_diagram = self._generate_dns_propagation_diagram(dns_mapping)
            diagrams.append(propagation_diagram)
        
        # Generate general DNS failover mechanism diagram
        failover_diagram = self._generate_dns_failover_diagram(topology)
        diagrams.append(failover_diagram)
        
        # Cache generated diagrams
        for diagram in diagrams:
            self._dns_propagation_diagrams[diagram.domain] = diagram
        
        self._logger.info(f"Generated {len(diagrams)} DNS propagation diagrams")
        return diagrams
    
    def _generate_dns_propagation_diagram(self, dns_mapping: DNSMapping) -> DNSPropagationDiagram:
        """Generate DNS propagation diagram for specific domain."""
        
        domain_id = dns_mapping.domain.replace(".", "")
        
        mermaid_content = f"""
graph TD
    %% DNS Propagation Flow for {dns_mapping.domain}
    %% Target: {dns_mapping.target_service}:{dns_mapping.target_port}
    %% TTL: {dns_mapping.ttl_seconds} seconds
    
    DNSUpdate[DNS Record Update<br/>{dns_mapping.domain}]
    CloudflareAPI[Cloudflare API<br/>DNS Management]
    CloudflareEdge[Cloudflare Edge Servers<br/>Global Network]
    
    DNSUpdate -->|API Call| CloudflareAPI
    CloudflareAPI -->|Propagate| CloudflareEdge
    
    %% Propagation Stages
    CloudflareEdge -->|0-15s| Tier1[Tier 1 Edge Servers<br/>Major Cities]
    Tier1 -->|15-30s| Tier2[Tier 2 Edge Servers<br/>Regional]
    Tier2 -->|30-60s| Tier3[Tier 3 Edge Servers<br/>Local]
    
    %% Client Resolution
    Client[Client DNS Query]
    LocalResolver[Local DNS Resolver]
    ISPResolver[ISP DNS Resolver]
    
    Client -->|Query {dns_mapping.domain}| LocalResolver
    LocalResolver -->|Cache Miss| ISPResolver
    ISPResolver -->|Query| CloudflareEdge
    CloudflareEdge -->|Response| ISPResolver
    ISPResolver -->|Cached Response| LocalResolver
    LocalResolver -->|Response| Client
    
    %% Target Resolution
    Client -->|Connect| TunnelEndpoint[Tunnel Endpoint<br/>{dns_mapping.domain}]
    TunnelEndpoint -->|Route| TargetService[{dns_mapping.target_service}<br/>Port {dns_mapping.target_port}]
    
    %% Timing Annotations
    CloudflareAPI -.->|Immediate| PropagationStart[Propagation Start<br/>0 seconds]
    Tier1 -.->|15s| PropagationMid[50% Propagated<br/>15 seconds]
    Tier3 -.->|60s| PropagationComplete[100% Propagated<br/>60 seconds]
    
    %% Styling
    classDef dnsNode fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef edgeNode fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef clientNode fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef timingNode fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    
    class DNSUpdate,CloudflareAPI,LocalResolver,ISPResolver dnsNode
    class CloudflareEdge,Tier1,Tier2,Tier3 edgeNode
    class Client,TunnelEndpoint,TargetService clientNode
    class PropagationStart,PropagationMid,PropagationComplete timingNode
"""
        
        # Define propagation steps with timing
        propagation_steps = [
            {
                "step": 1,
                "action": "DNS record update via Cloudflare API",
                "timing": "0 seconds",
                "description": "Initial DNS record modification"
            },
            {
                "step": 2,
                "action": "Propagation to Tier 1 edge servers",
                "timing": "0-15 seconds",
                "description": "Major city edge servers receive update"
            },
            {
                "step": 3,
                "action": "Propagation to Tier 2 edge servers", 
                "timing": "15-30 seconds",
                "description": "Regional edge servers receive update"
            },
            {
                "step": 4,
                "action": "Propagation to Tier 3 edge servers",
                "timing": "30-60 seconds", 
                "description": "Local edge servers receive update"
            },
            {
                "step": 5,
                "action": "Client DNS cache expiration",
                "timing": f"{dns_mapping.ttl_seconds} seconds",
                "description": "Client requests fresh DNS resolution"
            }
        ]
        
        # Define timing estimates
        timing_estimates = {
            "initial_propagation": "0-15 seconds",
            "regional_propagation": "15-30 seconds", 
            "global_propagation": "30-60 seconds",
            "client_cache_refresh": f"{dns_mapping.ttl_seconds} seconds",
            "full_propagation": "60 seconds maximum"
        }
        
        return DNSPropagationDiagram(
            domain=dns_mapping.domain,
            title=f"DNS Propagation - {dns_mapping.domain}",
            description=f"DNS propagation timing and process for {dns_mapping.domain} -> {dns_mapping.target_service}:{dns_mapping.target_port}",
            propagation_steps=propagation_steps,
            failover_targets=dns_mapping.failover_targets,
            timing_estimates=timing_estimates,
            mermaid_content=mermaid_content,
            metadata={
                "domain": dns_mapping.domain,
                "target_service": dns_mapping.target_service,
                "target_port": dns_mapping.target_port,
                "ttl_seconds": dns_mapping.ttl_seconds,
                "tunnel_id": dns_mapping.tunnel_id,
                "failover_targets": dns_mapping.failover_targets
            }
        )
    
    def _generate_dns_failover_diagram(self, topology: NetworkTopology) -> DNSPropagationDiagram:
        """Generate DNS failover mechanism diagram."""
        
        mermaid_content = """
graph TD
    %% DNS Failover Mechanisms
    %% Automatic failover for service continuity
    
    Client[Client Request]
    DNSResolver[DNS Resolver]
    HealthChecker[Health Checker<br/>Continuous Monitoring]
    
    Client -->|DNS Query| DNSResolver
    HealthChecker -->|Monitor| PrimaryService[Primary Service<br/>observatory.nkllon.com]
    
    %% Health Check Decision
    HealthChecker -->|Health Status| FailoverDecision{Service Healthy?}
    
    %% Primary Path (Healthy)
    FailoverDecision -->|Healthy| DNSResolver
    DNSResolver -->|Primary Record| PrimaryService
    PrimaryService -->|Response| Client
    
    %% Failover Path (Unhealthy)
    FailoverDecision -->|Unhealthy| DNSFailover[DNS Failover<br/>Update Records]
    DNSFailover -->|Switch to Backup| BackupService[Backup Service<br/>backup.observatory.nkllon.com]
    DNSResolver -->|Backup Record| BackupService
    BackupService -->|Response| Client
    
    %% Recovery Process
    HealthChecker -->|Primary Restored| RecoveryProcess[Recovery Process<br/>Restore Primary]
    RecoveryProcess -->|Update DNS| DNSResolver
    
    %% Notification System
    DNSFailover -->|Alert| NotificationSystem[Notification System<br/>Alert Administrators]
    RecoveryProcess -->|Notify| NotificationSystem
    
    %% Styling
    classDef primaryNode fill:#4caf50,color:#ffffff,stroke:#388e3c,stroke-width:2px
    classDef failoverNode fill:#ff9800,color:#ffffff,stroke:#f57c00,stroke-width:2px
    classDef monitoringNode fill:#2196f3,color:#ffffff,stroke:#1976d2,stroke-width:2px
    classDef decisionNode fill:#9c27b0,color:#ffffff,stroke:#7b1fa2,stroke-width:2px
    
    class PrimaryService,RecoveryProcess primaryNode
    class BackupService,DNSFailover,NotificationSystem failoverNode
    class HealthChecker,DNSResolver monitoringNode
    class FailoverDecision decisionNode
"""
        
        # Collect all failover targets from topology
        all_failover_targets = []
        for dns_mapping in topology.dns_mappings:
            all_failover_targets.extend(dns_mapping.failover_targets)
        
        propagation_steps = [
            {
                "step": 1,
                "action": "Continuous health monitoring of primary services",
                "timing": "Every 30 seconds",
                "description": "Automated health checks detect service failures"
            },
            {
                "step": 2,
                "action": "Failover decision based on health status",
                "timing": "Within 30 seconds of failure",
                "description": "Health checker determines need for failover"
            },
            {
                "step": 3,
                "action": "DNS record update to backup service",
                "timing": "30-60 seconds",
                "description": "DNS records updated to point to backup"
            },
            {
                "step": 4,
                "action": "Client traffic routed to backup service",
                "timing": "60-120 seconds",
                "description": "New DNS records propagated to clients"
            },
            {
                "step": 5,
                "action": "Primary service recovery and DNS restoration",
                "timing": "When primary restored",
                "description": "Automatic recovery to primary service"
            }
        ]
        
        timing_estimates = {
            "failure_detection": "30 seconds",
            "failover_decision": "30 seconds", 
            "dns_update": "30-60 seconds",
            "client_propagation": "60-120 seconds",
            "total_failover_time": "2-4 minutes",
            "recovery_time": "1-2 minutes"
        }
        
        return DNSPropagationDiagram(
            domain="failover_mechanisms",
            title="DNS Failover Mechanisms",
            description="Automatic DNS failover mechanisms for service continuity",
            propagation_steps=propagation_steps,
            failover_targets=list(set(all_failover_targets)),
            timing_estimates=timing_estimates,
            mermaid_content=mermaid_content,
            metadata={
                "failover_type": "automatic",
                "health_check_interval": "30 seconds",
                "failover_threshold": "3 consecutive failures",
                "recovery_threshold": "3 consecutive successes",
                "notification_channels": ["email", "slack", "webhook"]
            }
        )
    
    def _get_service_status_icon(self, status) -> str:
        """Get service status icon for Mermaid diagrams."""
        if hasattr(status, 'value'):
            status_value = status.value
        else:
            status_value = str(status).lower()
        
        icons = {
            "active": "✅",
            "inactive": "❌", 
            "degraded": "⚠️",
            "maintenance": "🔧",
            "unknown": "❓"
        }
        return icons.get(status_value, "❓")
    
    def save_all_diagrams(self) -> Dict[str, List[str]]:
        """Save all generated diagrams to files."""
        self._logger.info("Saving all generated diagrams...")
        
        saved_files = {
            "network_flows": [],
            "websocket_flows": [],
            "dns_propagation": [],
            "security_zones": []
        }
        
        # Save network flow diagrams
        for diagram in self._network_flow_diagrams.values():
            files = self._save_network_flow_diagram(diagram)
            saved_files["network_flows"].extend(files)
        
        # Save WebSocket flow diagrams
        for diagram in self._websocket_flow_diagrams.values():
            files = self._save_websocket_flow_diagram(diagram)
            saved_files["websocket_flows"].extend(files)
        
        # Save DNS propagation diagrams
        for diagram in self._dns_propagation_diagrams.values():
            files = self._save_dns_propagation_diagram(diagram)
            saved_files["dns_propagation"].extend(files)
        
        total_files = sum(len(files) for files in saved_files.values())
        self._logger.info(f"Saved {total_files} diagram files")
        
        return saved_files
    
    def _save_network_flow_diagram(self, diagram: NetworkFlowDiagram) -> List[str]:
        """Save network flow diagram to files."""
        files = []
        
        # Save Mermaid source
        mermaid_file = self._config.output_directory / f"{diagram.flow_id}.mmd"
        with open(mermaid_file, 'w', encoding='utf-8') as f:
            f.write(diagram.mermaid_content)
        files.append(str(mermaid_file))
        
        # Save metadata
        metadata_file = self._config.output_directory / f"{diagram.flow_id}_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump({
                "flow_id": diagram.flow_id,
                "title": diagram.title,
                "description": diagram.description,
                "source_nodes": diagram.source_nodes,
                "target_nodes": diagram.target_nodes,
                "decision_points": diagram.decision_points,
                "routing_rules": diagram.routing_rules,
                "metadata": diagram.metadata,
                "generated_at": datetime.now().isoformat()
            }, f, indent=2)
        files.append(str(metadata_file))
        
        return files
    
    def _save_websocket_flow_diagram(self, diagram: WebSocketFlowDiagram) -> List[str]:
        """Save WebSocket flow diagram to files."""
        files = []
        
        # Save Mermaid source
        mermaid_file = self._config.output_directory / f"websocket_{diagram.endpoint_path.replace('/', '_')}.mmd"
        with open(mermaid_file, 'w', encoding='utf-8') as f:
            f.write(diagram.mermaid_content)
        files.append(str(mermaid_file))
        
        # Save metadata
        metadata_file = self._config.output_directory / f"websocket_{diagram.endpoint_path.replace('/', '_')}_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump({
                "endpoint_path": diagram.endpoint_path,
                "title": diagram.title,
                "description": diagram.description,
                "connection_flow": diagram.connection_flow,
                "upgrade_sequence": diagram.upgrade_sequence,
                "message_types": diagram.message_types,
                "metadata": diagram.metadata,
                "generated_at": datetime.now().isoformat()
            }, f, indent=2)
        files.append(str(metadata_file))
        
        return files
    
    def _save_dns_propagation_diagram(self, diagram: DNSPropagationDiagram) -> List[str]:
        """Save DNS propagation diagram to files."""
        files = []
        
        # Save Mermaid source
        domain_safe = diagram.domain.replace(".", "_")
        mermaid_file = self._config.output_directory / f"dns_{domain_safe}.mmd"
        with open(mermaid_file, 'w', encoding='utf-8') as f:
            f.write(diagram.mermaid_content)
        files.append(str(mermaid_file))
        
        # Save metadata
        metadata_file = self._config.output_directory / f"dns_{domain_safe}_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump({
                "domain": diagram.domain,
                "title": diagram.title,
                "description": diagram.description,
                "propagation_steps": diagram.propagation_steps,
                "failover_targets": diagram.failover_targets,
                "timing_estimates": diagram.timing_estimates,
                "metadata": diagram.metadata,
                "generated_at": datetime.now().isoformat()
            }, f, indent=2)
        files.append(str(metadata_file))
        
        return files
    
    def get_all_diagrams(self) -> Dict[str, Any]:
        """Get all generated diagrams."""
        return {
            "network_flows": list(self._network_flow_diagrams.values()),
            "websocket_flows": list(self._websocket_flow_diagrams.values()),
            "dns_propagation": list(self._dns_propagation_diagrams.values()),
            "security_zones": list(self._security_zone_diagrams.values())
        }
    
    def graceful_degradation(self, error: Exception) -> GracefulDegradationResult:
        """Handle graceful degradation on errors."""
        self._logger.warning(f"Graceful degradation triggered: {error}")
        
        return GracefulDegradationResult(
            success=True,
            message=f"NetworkTopologyVisualizer degraded due to: {str(error)}",
            fallback_data={
                "network_flow_diagrams": len(self._network_flow_diagrams),
                "websocket_flow_diagrams": len(self._websocket_flow_diagrams),
                "dns_propagation_diagrams": len(self._dns_propagation_diagrams),
                "security_zone_diagrams": len(self._security_zone_diagrams)
            }
        )