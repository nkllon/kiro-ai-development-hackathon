#!/usr/bin/env python3
"""
Network Visualization Models - Task 3.3 Implementation
=====================================================

Data models and structures for network topology visualization.
Provides comprehensive models for network flow diagrams, WebSocket
upgrade handling, DNS propagation timing, Cloudflare tunnel routing,
security zones, and Redis coordination visualization.

Author: Beast Mode Framework
Date: 2024-12-19
Version: 1.0
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Set, Tuple, Union
import json
import yaml
from pathlib import Path
import uuid


class VisualizationType(Enum):
    """Types of network visualizations."""
    NETWORK_FLOW_DIAGRAM = "network_flow_diagram"
    WEBSOCKET_CONNECTION_FLOW = "websocket_connection_flow"
    DNS_PROPAGATION_TIMELINE = "dns_propagation_timeline"
    CLOUDFLARE_TUNNEL_ROUTING = "cloudflare_tunnel_routing"
    SECURITY_ZONE_MAP = "security_zone_map"
    REDIS_COORDINATION_FLOW = "redis_coordination_flow"
    FAILOVER_MECHANISM_DIAGRAM = "failover_mechanism_diagram"


class FlowDirection(Enum):
    """Flow direction types."""
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BIDIRECTIONAL = "bidirectional"
    INTERNAL = "internal"


class SecurityLevel(Enum):
    """Security zone levels."""
    PUBLIC = "public"
    DMZ = "dmz"
    PRIVATE = "private"
    SECURE = "secure"
    RESTRICTED = "restricted"


class ConnectionState(Enum):
    """WebSocket connection states."""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    UPGRADING = "upgrading"
    UPGRADED = "upgraded"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"
    FAILED = "failed"


@dataclass
class NetworkNode:
    """
    Network node representation for visualization.
    
    Represents a network component (service, router, load balancer, etc.)
    with comprehensive metadata for visualization.
    """
    node_id: str
    name: str
    node_type: str  # service, router, load_balancer, firewall, etc.
    position: Tuple[float, float]  # x, y coordinates for visualization
    size: Tuple[float, float] = (100.0, 60.0)  # width, height
    color: str = "#3498db"
    status: str = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)
    security_level: SecurityLevel = SecurityLevel.PRIVATE
    tags: Set[str] = field(default_factory=set)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "node_id": self.node_id,
            "name": self.name,
            "node_type": self.node_type,
            "position": self.position,
            "size": self.size,
            "color": self.color,
            "status": self.status,
            "metadata": self.metadata,
            "security_level": self.security_level.value,
            "tags": list(self.tags)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NetworkNode':
        """Create from dictionary representation."""
        return cls(
            node_id=data["node_id"],
            name=data["name"],
            node_type=data["node_type"],
            position=tuple(data["position"]),
            size=tuple(data.get("size", [100.0, 60.0])),
            color=data.get("color", "#3498db"),
            status=data.get("status", "active"),
            metadata=data.get("metadata", {}),
            security_level=SecurityLevel(data.get("security_level", "private")),
            tags=set(data.get("tags", []))
        )


@dataclass
class NetworkEdge:
    """
    Network edge representation for visualization.
    
    Represents a connection between network nodes with comprehensive
    flow information and routing details.
    """
    edge_id: str
    source_node: str
    target_node: str
    edge_type: str  # connection, flow, failover, etc.
    direction: FlowDirection = FlowDirection.BIDIRECTIONAL
    protocol: str = "tcp"
    port: Optional[int] = None
    bandwidth_limit: Optional[int] = None  # Mbps
    latency_ms: Optional[float] = None
    packet_loss_percent: Optional[float] = None
    color: str = "#95a5a6"
    thickness: float = 2.0
    style: str = "solid"  # solid, dashed, dotted
    label: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    decision_points: List[str] = field(default_factory=list)
    failover_targets: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "edge_id": self.edge_id,
            "source_node": self.source_node,
            "target_node": self.target_node,
            "edge_type": self.edge_type,
            "direction": self.direction.value,
            "protocol": self.protocol,
            "port": self.port,
            "bandwidth_limit": self.bandwidth_limit,
            "latency_ms": self.latency_ms,
            "packet_loss_percent": self.packet_loss_percent,
            "color": self.color,
            "thickness": self.thickness,
            "style": self.style,
            "label": self.label,
            "metadata": self.metadata,
            "decision_points": self.decision_points,
            "failover_targets": self.failover_targets
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NetworkEdge':
        """Create from dictionary representation."""
        return cls(
            edge_id=data["edge_id"],
            source_node=data["source_node"],
            target_node=data["target_node"],
            edge_type=data["edge_type"],
            direction=FlowDirection(data.get("direction", "bidirectional")),
            protocol=data.get("protocol", "tcp"),
            port=data.get("port"),
            bandwidth_limit=data.get("bandwidth_limit"),
            latency_ms=data.get("latency_ms"),
            packet_loss_percent=data.get("packet_loss_percent"),
            color=data.get("color", "#95a5a6"),
            thickness=data.get("thickness", 2.0),
            style=data.get("style", "solid"),
            label=data.get("label"),
            metadata=data.get("metadata", {}),
            decision_points=data.get("decision_points", []),
            failover_targets=data.get("failover_targets", [])
        )


@dataclass
class WebSocketUpgradeFlow:
    """
    WebSocket upgrade flow representation.
    
    Represents the complete WebSocket upgrade process with
    timing information and decision points.
    """
    flow_id: str
    endpoint: str
    upgrade_path: str
    connection_states: List[ConnectionState] = field(default_factory=list)
    timing_milestones: Dict[str, datetime] = field(default_factory=dict)
    decision_points: List[str] = field(default_factory=list)
    authentication_steps: List[str] = field(default_factory=list)
    error_scenarios: List[str] = field(default_factory=list)
    recovery_procedures: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "flow_id": self.flow_id,
            "endpoint": self.endpoint,
            "upgrade_path": self.upgrade_path,
            "connection_states": [state.value for state in self.connection_states],
            "timing_milestones": {k: v.isoformat() for k, v in self.timing_milestones.items()},
            "decision_points": self.decision_points,
            "authentication_steps": self.authentication_steps,
            "error_scenarios": self.error_scenarios,
            "recovery_procedures": self.recovery_procedures,
            "performance_metrics": self.performance_metrics
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WebSocketUpgradeFlow':
        """Create from dictionary representation."""
        return cls(
            flow_id=data["flow_id"],
            endpoint=data["endpoint"],
            upgrade_path=data["upgrade_path"],
            connection_states=[ConnectionState(state) for state in data.get("connection_states", [])],
            timing_milestones={k: datetime.fromisoformat(v) for k, v in data.get("timing_milestones", {}).items()},
            decision_points=data.get("decision_points", []),
            authentication_steps=data.get("authentication_steps", []),
            error_scenarios=data.get("error_scenarios", []),
            recovery_procedures=data.get("recovery_procedures", []),
            performance_metrics=data.get("performance_metrics", {})
        )


@dataclass
class DNSPropagationTimeline:
    """
    DNS propagation timeline representation.
    
    Represents DNS propagation timing and failover mechanisms
    with comprehensive timing information.
    """
    domain: str
    tunnel_id: str
    propagation_events: List[Dict[str, Any]] = field(default_factory=list)
    failover_mechanisms: List[str] = field(default_factory=list)
    health_check_intervals: Dict[str, int] = field(default_factory=dict)
    ttl_values: Dict[str, int] = field(default_factory=dict)
    cache_layers: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "domain": self.domain,
            "tunnel_id": self.tunnel_id,
            "propagation_events": self.propagation_events,
            "failover_mechanisms": self.failover_mechanisms,
            "health_check_intervals": self.health_check_intervals,
            "ttl_values": self.ttl_values,
            "cache_layers": self.cache_layers,
            "performance_metrics": self.performance_metrics
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DNSPropagationTimeline':
        """Create from dictionary representation."""
        return cls(
            domain=data["domain"],
            tunnel_id=data["tunnel_id"],
            propagation_events=data.get("propagation_events", []),
            failover_mechanisms=data.get("failover_mechanisms", []),
            health_check_intervals=data.get("health_check_intervals", {}),
            ttl_values=data.get("ttl_values", {}),
            cache_layers=data.get("cache_layers", []),
            performance_metrics=data.get("performance_metrics", {})
        )


@dataclass
class CloudflareTunnelRouting:
    """
    Cloudflare tunnel routing configuration.
    
    Represents Cloudflare tunnel routing with WebSocket proxy
    configuration and ingress rules.
    """
    tunnel_id: str
    domain: str
    ingress_rules: List[Dict[str, Any]] = field(default_factory=list)
    websocket_proxy_config: Dict[str, Any] = field(default_factory=dict)
    routing_decisions: List[str] = field(default_factory=list)
    security_policies: List[str] = field(default_factory=list)
    performance_optimizations: List[str] = field(default_factory=list)
    monitoring_endpoints: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "tunnel_id": self.tunnel_id,
            "domain": self.domain,
            "ingress_rules": self.ingress_rules,
            "websocket_proxy_config": self.websocket_proxy_config,
            "routing_decisions": self.routing_decisions,
            "security_policies": self.security_policies,
            "performance_optimizations": self.performance_optimizations,
            "monitoring_endpoints": self.monitoring_endpoints
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CloudflareTunnelRouting':
        """Create from dictionary representation."""
        return cls(
            tunnel_id=data["tunnel_id"],
            domain=data["domain"],
            ingress_rules=data.get("ingress_rules", []),
            websocket_proxy_config=data.get("websocket_proxy_config", {}),
            routing_decisions=data.get("routing_decisions", []),
            security_policies=data.get("security_policies", []),
            performance_optimizations=data.get("performance_optimizations", []),
            monitoring_endpoints=data.get("monitoring_endpoints", [])
        )


@dataclass
class SecurityZone:
    """
    Security zone representation.
    
    Represents a security zone with access patterns and
    security policies.
    """
    zone_id: str
    name: str
    security_level: SecurityLevel
    access_patterns: List[str] = field(default_factory=list)
    security_policies: List[str] = field(default_factory=list)
    allowed_protocols: List[str] = field(default_factory=list)
    allowed_ports: List[int] = field(default_factory=list)
    authentication_required: bool = False
    encryption_required: bool = False
    monitoring_endpoints: List[str] = field(default_factory=list)
    incident_response_procedures: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "zone_id": self.zone_id,
            "name": self.name,
            "security_level": self.security_level.value,
            "access_patterns": self.access_patterns,
            "security_policies": self.security_policies,
            "allowed_protocols": self.allowed_protocols,
            "allowed_ports": self.allowed_ports,
            "authentication_required": self.authentication_required,
            "encryption_required": self.encryption_required,
            "monitoring_endpoints": self.monitoring_endpoints,
            "incident_response_procedures": self.incident_response_procedures
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SecurityZone':
        """Create from dictionary representation."""
        return cls(
            zone_id=data["zone_id"],
            name=data["name"],
            security_level=SecurityLevel(data["security_level"]),
            access_patterns=data.get("access_patterns", []),
            security_policies=data.get("security_policies", []),
            allowed_protocols=data.get("allowed_protocols", []),
            allowed_ports=data.get("allowed_ports", []),
            authentication_required=data.get("authentication_required", False),
            encryption_required=data.get("encryption_required", False),
            monitoring_endpoints=data.get("monitoring_endpoints", []),
            incident_response_procedures=data.get("incident_response_procedures", [])
        )


@dataclass
class RedisCoordinationFlow:
    """
    Redis coordination flow representation.
    
    Represents Redis coordination connectivity with automatic
    failover logic and health monitoring.
    """
    cluster_id: str
    primary_endpoint: str
    fallback_endpoints: List[str] = field(default_factory=list)
    failover_logic: List[str] = field(default_factory=list)
    health_check_procedures: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    monitoring_endpoints: List[str] = field(default_factory=list)
    recovery_procedures: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "cluster_id": self.cluster_id,
            "primary_endpoint": self.primary_endpoint,
            "fallback_endpoints": self.fallback_endpoints,
            "failover_logic": self.failover_logic,
            "health_check_procedures": self.health_check_procedures,
            "performance_metrics": self.performance_metrics,
            "monitoring_endpoints": self.monitoring_endpoints,
            "recovery_procedures": self.recovery_procedures
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RedisCoordinationFlow':
        """Create from dictionary representation."""
        return cls(
            cluster_id=data["cluster_id"],
            primary_endpoint=data["primary_endpoint"],
            fallback_endpoints=data.get("fallback_endpoints", []),
            failover_logic=data.get("failover_logic", []),
            health_check_procedures=data.get("health_check_procedures", []),
            performance_metrics=data.get("performance_metrics", {}),
            monitoring_endpoints=data.get("monitoring_endpoints", []),
            recovery_procedures=data.get("recovery_procedures", [])
        )


@dataclass
class NetworkVisualization:
    """
    Complete network visualization representation.
    
    Comprehensive network visualization including all components,
    flows, security zones, and coordination mechanisms.
    """
    visualization_id: str
    visualization_type: VisualizationType
    title: str
    description: str
    nodes: List[NetworkNode] = field(default_factory=list)
    edges: List[NetworkEdge] = field(default_factory=list)
    websocket_flows: List[WebSocketUpgradeFlow] = field(default_factory=list)
    dns_timelines: List[DNSPropagationTimeline] = field(default_factory=list)
    tunnel_routing: List[CloudflareTunnelRouting] = field(default_factory=list)
    security_zones: List[SecurityZone] = field(default_factory=list)
    redis_coordination: List[RedisCoordinationFlow] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "visualization_id": self.visualization_id,
            "visualization_type": self.visualization_type.value,
            "title": self.title,
            "description": self.description,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "websocket_flows": [flow.to_dict() for flow in self.websocket_flows],
            "dns_timelines": [timeline.to_dict() for timeline in self.dns_timelines],
            "tunnel_routing": [routing.to_dict() for routing in self.tunnel_routing],
            "security_zones": [zone.to_dict() for zone in self.security_zones],
            "redis_coordination": [coord.to_dict() for coord in self.redis_coordination],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NetworkVisualization':
        """Create from dictionary representation."""
        return cls(
            visualization_id=data["visualization_id"],
            visualization_type=VisualizationType(data["visualization_type"]),
            title=data["title"],
            description=data["description"],
            nodes=[NetworkNode.from_dict(node) for node in data.get("nodes", [])],
            edges=[NetworkEdge.from_dict(edge) for edge in data.get("edges", [])],
            websocket_flows=[WebSocketUpgradeFlow.from_dict(flow) for flow in data.get("websocket_flows", [])],
            dns_timelines=[DNSPropagationTimeline.from_dict(timeline) for timeline in data.get("dns_timelines", [])],
            tunnel_routing=[CloudflareTunnelRouting.from_dict(routing) for routing in data.get("tunnel_routing", [])],
            security_zones=[SecurityZone.from_dict(zone) for zone in data.get("security_zones", [])],
            redis_coordination=[RedisCoordinationFlow.from_dict(coord) for coord in data.get("redis_coordination", [])],
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat())),
            version=data.get("version", "1.0")
        )
    
    def to_json(self, file_path: Optional[Path] = None) -> str:
        """Export to JSON format."""
        json_data = json.dumps(self.to_dict(), indent=2, default=str)
        
        if file_path:
            with open(file_path, 'w') as f:
                f.write(json_data)
        
        return json_data
    
    def to_yaml(self, file_path: Optional[Path] = None) -> str:
        """Export to YAML format."""
        yaml_data = yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False)
        
        if file_path:
            with open(file_path, 'w') as f:
                f.write(yaml_data)
        
        return yaml_data
    
    @classmethod
    def from_json(cls, json_data: str) -> 'NetworkVisualization':
        """Import from JSON format."""
        data = json.loads(json_data)
        return cls.from_dict(data)
    
    @classmethod
    def from_yaml(cls, yaml_data: str) -> 'NetworkVisualization':
        """Import from YAML format."""
        data = yaml.safe_load(yaml_data)
        return cls.from_dict(data)
    
    @classmethod
    def from_file(cls, file_path: Path) -> 'NetworkVisualization':
        """Import from file (auto-detect format)."""
        with open(file_path, 'r') as f:
            content = f.read()
        
        if file_path.suffix.lower() == '.json':
            return cls.from_json(content)
        elif file_path.suffix.lower() in ['.yml', '.yaml']:
            return cls.from_yaml(content)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    def get_node_by_id(self, node_id: str) -> Optional[NetworkNode]:
        """Get network node by ID."""
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None
    
    def get_nodes_by_type(self, node_type: str) -> List[NetworkNode]:
        """Get network nodes by type."""
        return [node for node in self.nodes if node.node_type == node_type]
    
    def get_edges_by_node(self, node_id: str) -> List[NetworkEdge]:
        """Get edges connected to a specific node."""
        edges = []
        for edge in self.edges:
            if edge.source_node == node_id or edge.target_node == node_id:
                edges.append(edge)
        return edges
    
    def get_security_zones_by_level(self, security_level: SecurityLevel) -> List[SecurityZone]:
        """Get security zones by security level."""
        return [zone for zone in self.security_zones if zone.security_level == security_level]
    
    def validate_visualization(self) -> List[str]:
        """Validate visualization configuration and return any issues."""
        issues = []
        
        # Check for orphaned nodes
        node_ids = {node.node_id for node in self.nodes}
        for edge in self.edges:
            if edge.source_node not in node_ids:
                issues.append(f"Edge {edge.edge_id} references unknown source node {edge.source_node}")
            if edge.target_node not in node_ids:
                issues.append(f"Edge {edge.edge_id} references unknown target node {edge.target_node}")
        
        # Check for duplicate node IDs
        node_id_counts = {}
        for node in self.nodes:
            node_id_counts[node.node_id] = node_id_counts.get(node.node_id, 0) + 1
        
        for node_id, count in node_id_counts.items():
            if count > 1:
                issues.append(f"Node ID {node_id} is used by {count} nodes")
        
        # Check for duplicate edge IDs
        edge_id_counts = {}
        for edge in self.edges:
            edge_id_counts[edge.edge_id] = edge_id_counts.get(edge.edge_id, 0) + 1
        
        for edge_id, count in edge_id_counts.items():
            if count > 1:
                issues.append(f"Edge ID {edge_id} is used by {count} edges")
        
        return issues
    
    def get_visualization_summary(self) -> Dict[str, Any]:
        """Get comprehensive visualization summary."""
        return {
            "visualization_id": self.visualization_id,
            "visualization_type": self.visualization_type.value,
            "title": self.title,
            "description": self.description,
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "websocket_flows": len(self.websocket_flows),
            "dns_timelines": len(self.dns_timelines),
            "tunnel_routing": len(self.tunnel_routing),
            "security_zones": len(self.security_zones),
            "redis_coordination": len(self.redis_coordination),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "validation_issues": len(self.validate_visualization())
        }