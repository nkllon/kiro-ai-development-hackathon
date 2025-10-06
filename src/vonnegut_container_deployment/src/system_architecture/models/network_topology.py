#!/usr/bin/env python3
"""
Network Topology Models - Task 1.6 Implementation
================================================

Data models and structures for network topology discovery and mapping.
Provides comprehensive models for service endpoints, network flows,
DNS mappings, Redis coordination, WebSocket configurations, and
failover mechanisms.

Author: Beast Mode Framework
Date: 2024-12-19
Version: 1.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Set, Tuple
import json
import yaml
from pathlib import Path


class ServiceStatus(Enum):
    """Service operational status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"
    MAINTENANCE = "maintenance"


class Protocol(Enum):
    """Network protocols."""
    TCP = "tcp"
    UDP = "udp"
    HTTP = "http"
    HTTPS = "https"
    WEBSOCKET = "websocket"
    REDIS = "redis"


class FlowType(Enum):
    """Network flow types."""
    INGRESS = "ingress"
    EGRESS = "egress"
    INTERNAL = "internal"
    CROSS_REGION = "cross_region"


class FailoverType(Enum):
    """Failover mechanism types."""
    DNS_FAILOVER = "dns_failover"
    REDIS_FAILOVER = "redis_failover"
    WEBSOCKET_FAILOVER = "websocket_failover"
    SERVICE_FAILOVER = "service_failover"
    LOAD_BALANCER_FAILOVER = "load_balancer_failover"


@dataclass
class ServiceEndpoint:
    """
    Service endpoint information with comprehensive metadata.
    
    Represents a network service endpoint with health monitoring,
    WebSocket support, and dependency tracking.
    """
    name: str
    host: str
    port: int
    protocol: Protocol = Protocol.TCP
    status: ServiceStatus = ServiceStatus.UNKNOWN
    response_time_ms: Optional[float] = None
    health_endpoint: Optional[str] = None
    websocket_endpoints: List[str] = field(default_factory=list)
    last_checked: datetime = field(default_factory=datetime.now)
    error_count: int = 0
    dependencies: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "host": self.host,
            "port": self.port,
            "protocol": self.protocol.value,
            "status": self.status.value,
            "response_time_ms": self.response_time_ms,
            "health_endpoint": self.health_endpoint,
            "websocket_endpoints": self.websocket_endpoints,
            "last_checked": self.last_checked.isoformat(),
            "error_count": self.error_count,
            "dependencies": self.dependencies,
            "tags": list(self.tags),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ServiceEndpoint':
        """Create from dictionary representation."""
        return cls(
            name=data["name"],
            host=data["host"],
            port=data["port"],
            protocol=Protocol(data.get("protocol", "tcp")),
            status=ServiceStatus(data.get("status", "unknown")),
            response_time_ms=data.get("response_time_ms"),
            health_endpoint=data.get("health_endpoint"),
            websocket_endpoints=data.get("websocket_endpoints", []),
            last_checked=datetime.fromisoformat(data.get("last_checked", datetime.now().isoformat())),
            error_count=data.get("error_count", 0),
            dependencies=data.get("dependencies", []),
            tags=set(data.get("tags", [])),
            metadata=data.get("metadata", {})
        )


@dataclass
class NetworkFlow:
    """
    Network flow information with decision points and routing rules.
    
    Represents network traffic flows with comprehensive routing
    configuration and failover mechanisms.
    """
    source: str
    destination: str
    protocol: Protocol
    port: int
    flow_type: FlowType
    decision_points: List[str] = field(default_factory=list)
    routing_rules: List[Dict[str, Any]] = field(default_factory=list)
    failover_config: Optional[Dict[str, Any]] = None
    bandwidth_limit: Optional[int] = None  # Mbps
    latency_ms: Optional[float] = None
    packet_loss_percent: Optional[float] = None
    security_policies: List[str] = field(default_factory=list)
    monitoring_endpoints: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "source": self.source,
            "destination": self.destination,
            "protocol": self.protocol.value,
            "port": self.port,
            "flow_type": self.flow_type.value,
            "decision_points": self.decision_points,
            "routing_rules": self.routing_rules,
            "failover_config": self.failover_config,
            "bandwidth_limit": self.bandwidth_limit,
            "latency_ms": self.latency_ms,
            "packet_loss_percent": self.packet_loss_percent,
            "security_policies": self.security_policies,
            "monitoring_endpoints": self.monitoring_endpoints
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NetworkFlow':
        """Create from dictionary representation."""
        return cls(
            source=data["source"],
            destination=data["destination"],
            protocol=Protocol(data.get("protocol", "tcp")),
            port=data["port"],
            flow_type=FlowType(data.get("flow_type", "internal")),
            decision_points=data.get("decision_points", []),
            routing_rules=data.get("routing_rules", []),
            failover_config=data.get("failover_config"),
            bandwidth_limit=data.get("bandwidth_limit"),
            latency_ms=data.get("latency_ms"),
            packet_loss_percent=data.get("packet_loss_percent"),
            security_policies=data.get("security_policies", []),
            monitoring_endpoints=data.get("monitoring_endpoints", [])
        )


@dataclass
class DNSMapping:
    """
    DNS mapping information with failover targets.
    
    Represents domain name resolution with comprehensive
    failover and load balancing configuration.
    """
    domain: str
    target_service: str
    target_port: int
    tunnel_id: Optional[str] = None
    failover_targets: List[str] = field(default_factory=list)
    ttl_seconds: int = 300
    last_resolved: Optional[datetime] = None
    resolved_ips: List[str] = field(default_factory=list)
    load_balancing: Optional[Dict[str, Any]] = None
    health_check_config: Optional[Dict[str, Any]] = None
    ssl_config: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "domain": self.domain,
            "target_service": self.target_service,
            "target_port": self.target_port,
            "tunnel_id": self.tunnel_id,
            "failover_targets": self.failover_targets,
            "ttl_seconds": self.ttl_seconds,
            "last_resolved": self.last_resolved.isoformat() if self.last_resolved else None,
            "resolved_ips": self.resolved_ips,
            "load_balancing": self.load_balancing,
            "health_check_config": self.health_check_config,
            "ssl_config": self.ssl_config
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DNSMapping':
        """Create from dictionary representation."""
        return cls(
            domain=data["domain"],
            target_service=data["target_service"],
            target_port=data["target_port"],
            tunnel_id=data.get("tunnel_id"),
            failover_targets=data.get("failover_targets", []),
            ttl_seconds=data.get("ttl_seconds", 300),
            last_resolved=datetime.fromisoformat(data["last_resolved"]) if data.get("last_resolved") else None,
            resolved_ips=data.get("resolved_ips", []),
            load_balancing=data.get("load_balancing"),
            health_check_config=data.get("health_check_config"),
            ssl_config=data.get("ssl_config")
        )


@dataclass
class RedisCoordination:
    """
    Redis coordination configuration with failover support.
    
    Represents Redis cluster configuration with comprehensive
    failover mechanisms and health monitoring.
    """
    primary_endpoint: str
    fallback_endpoints: List[str] = field(default_factory=list)
    cluster_mode: bool = False
    failover_config: Dict[str, Any] = field(default_factory=dict)
    health_status: str = "unknown"
    last_health_check: Optional[datetime] = None
    connection_pool_size: int = 10
    timeout_seconds: int = 5
    retry_attempts: int = 3
    password: Optional[str] = None
    ssl_enabled: bool = False
    monitoring_config: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "primary_endpoint": self.primary_endpoint,
            "fallback_endpoints": self.fallback_endpoints,
            "cluster_mode": self.cluster_mode,
            "failover_config": self.failover_config,
            "health_status": self.health_status,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "connection_pool_size": self.connection_pool_size,
            "timeout_seconds": self.timeout_seconds,
            "retry_attempts": self.retry_attempts,
            "password": "***" if self.password else None,  # Mask password
            "ssl_enabled": self.ssl_enabled,
            "monitoring_config": self.monitoring_config
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RedisCoordination':
        """Create from dictionary representation."""
        return cls(
            primary_endpoint=data["primary_endpoint"],
            fallback_endpoints=data.get("fallback_endpoints", []),
            cluster_mode=data.get("cluster_mode", False),
            failover_config=data.get("failover_config", {}),
            health_status=data.get("health_status", "unknown"),
            last_health_check=datetime.fromisoformat(data["last_health_check"]) if data.get("last_health_check") else None,
            connection_pool_size=data.get("connection_pool_size", 10),
            timeout_seconds=data.get("timeout_seconds", 5),
            retry_attempts=data.get("retry_attempts", 3),
            password=data.get("password"),
            ssl_enabled=data.get("ssl_enabled", False),
            monitoring_config=data.get("monitoring_config")
        )


@dataclass
class WebSocketConfiguration:
    """
    WebSocket configuration and upgrade handling.
    
    Represents WebSocket endpoint configuration with comprehensive
    connection management and authentication.
    """
    endpoint: str
    upgrade_path: str
    supported_protocols: List[str] = field(default_factory=list)
    connection_flow: List[str] = field(default_factory=list)
    authentication_required: bool = False
    max_connections: int = 1000
    heartbeat_interval: int = 30
    compression_enabled: bool = True
    subprotocols: List[str] = field(default_factory=list)
    origin_validation: Optional[Dict[str, Any]] = None
    rate_limiting: Optional[Dict[str, Any]] = None
    message_size_limit: int = 1024 * 1024  # 1MB
    connection_timeout: int = 300  # 5 minutes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "endpoint": self.endpoint,
            "upgrade_path": self.upgrade_path,
            "supported_protocols": self.supported_protocols,
            "connection_flow": self.connection_flow,
            "authentication_required": self.authentication_required,
            "max_connections": self.max_connections,
            "heartbeat_interval": self.heartbeat_interval,
            "compression_enabled": self.compression_enabled,
            "subprotocols": self.subprotocols,
            "origin_validation": self.origin_validation,
            "rate_limiting": self.rate_limiting,
            "message_size_limit": self.message_size_limit,
            "connection_timeout": self.connection_timeout
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WebSocketConfiguration':
        """Create from dictionary representation."""
        return cls(
            endpoint=data["endpoint"],
            upgrade_path=data["upgrade_path"],
            supported_protocols=data.get("supported_protocols", []),
            connection_flow=data.get("connection_flow", []),
            authentication_required=data.get("authentication_required", False),
            max_connections=data.get("max_connections", 1000),
            heartbeat_interval=data.get("heartbeat_interval", 30),
            compression_enabled=data.get("compression_enabled", True),
            subprotocols=data.get("subprotocols", []),
            origin_validation=data.get("origin_validation"),
            rate_limiting=data.get("rate_limiting"),
            message_size_limit=data.get("message_size_limit", 1024 * 1024),
            connection_timeout=data.get("connection_timeout", 300)
        )


@dataclass
class FailoverMechanism:
    """
    Failover mechanism configuration.
    
    Represents comprehensive failover configuration for
    service continuity and disaster recovery.
    """
    mechanism_id: str
    failover_type: FailoverType
    description: str
    primary_target: str
    fallback_targets: List[str] = field(default_factory=list)
    detection_method: str = "health_check"
    failover_time: str = "30s"
    recovery_time: str = "60s"
    health_check_interval: str = "10s"
    max_retries: int = 3
    auto_recovery: bool = True
    notification_endpoints: List[str] = field(default_factory=list)
    monitoring_config: Optional[Dict[str, Any]] = None
    rollback_config: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "mechanism_id": self.mechanism_id,
            "failover_type": self.failover_type.value,
            "description": self.description,
            "primary_target": self.primary_target,
            "fallback_targets": self.fallback_targets,
            "detection_method": self.detection_method,
            "failover_time": self.failover_time,
            "recovery_time": self.recovery_time,
            "health_check_interval": self.health_check_interval,
            "max_retries": self.max_retries,
            "auto_recovery": self.auto_recovery,
            "notification_endpoints": self.notification_endpoints,
            "monitoring_config": self.monitoring_config,
            "rollback_config": self.rollback_config
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FailoverMechanism':
        """Create from dictionary representation."""
        return cls(
            mechanism_id=data["mechanism_id"],
            failover_type=FailoverType(data.get("failover_type", "service_failover")),
            description=data["description"],
            primary_target=data["primary_target"],
            fallback_targets=data.get("fallback_targets", []),
            detection_method=data.get("detection_method", "health_check"),
            failover_time=data.get("failover_time", "30s"),
            recovery_time=data.get("recovery_time", "60s"),
            health_check_interval=data.get("health_check_interval", "10s"),
            max_retries=data.get("max_retries", 3),
            auto_recovery=data.get("auto_recovery", True),
            notification_endpoints=data.get("notification_endpoints", []),
            monitoring_config=data.get("monitoring_config"),
            rollback_config=data.get("rollback_config")
        )


@dataclass
class NetworkTopology:
    """
    Complete network topology information.
    
    Comprehensive network topology representation including
    all service endpoints, flows, DNS mappings, Redis coordination,
    WebSocket configurations, and failover mechanisms.
    """
    local_network_range: str
    service_endpoints: List[ServiceEndpoint] = field(default_factory=list)
    network_flows: List[NetworkFlow] = field(default_factory=list)
    dns_mappings: List[DNSMapping] = field(default_factory=list)
    redis_coordination: Optional[RedisCoordination] = None
    websocket_configs: List[WebSocketConfiguration] = field(default_factory=list)
    port_allocations: Dict[int, str] = field(default_factory=dict)
    routing_configurations: List[Dict[str, Any]] = field(default_factory=list)
    failover_mechanisms: List[FailoverMechanism] = field(default_factory=list)
    discovery_timestamp: datetime = field(default_factory=datetime.now)
    topology_version: str = "1.0"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "local_network_range": self.local_network_range,
            "service_endpoints": [ep.to_dict() for ep in self.service_endpoints],
            "network_flows": [flow.to_dict() for flow in self.network_flows],
            "dns_mappings": [mapping.to_dict() for mapping in self.dns_mappings],
            "redis_coordination": self.redis_coordination.to_dict() if self.redis_coordination else None,
            "websocket_configs": [config.to_dict() for config in self.websocket_configs],
            "port_allocations": self.port_allocations,
            "routing_configurations": self.routing_configurations,
            "failover_mechanisms": [mechanism.to_dict() for mechanism in self.failover_mechanisms],
            "discovery_timestamp": self.discovery_timestamp.isoformat(),
            "topology_version": self.topology_version,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NetworkTopology':
        """Create from dictionary representation."""
        return cls(
            local_network_range=data["local_network_range"],
            service_endpoints=[ServiceEndpoint.from_dict(ep) for ep in data.get("service_endpoints", [])],
            network_flows=[NetworkFlow.from_dict(flow) for flow in data.get("network_flows", [])],
            dns_mappings=[DNSMapping.from_dict(mapping) for mapping in data.get("dns_mappings", [])],
            redis_coordination=RedisCoordination.from_dict(data["redis_coordination"]) if data.get("redis_coordination") else None,
            websocket_configs=[WebSocketConfiguration.from_dict(config) for config in data.get("websocket_configs", [])],
            port_allocations=data.get("port_allocations", {}),
            routing_configurations=data.get("routing_configurations", []),
            failover_mechanisms=[FailoverMechanism.from_dict(mechanism) for mechanism in data.get("failover_mechanisms", [])],
            discovery_timestamp=datetime.fromisoformat(data.get("discovery_timestamp", datetime.now().isoformat())),
            topology_version=data.get("topology_version", "1.0"),
            metadata=data.get("metadata", {})
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
    def from_json(cls, json_data: str) -> 'NetworkTopology':
        """Import from JSON format."""
        data = json.loads(json_data)
        return cls.from_dict(data)
    
    @classmethod
    def from_yaml(cls, yaml_data: str) -> 'NetworkTopology':
        """Import from YAML format."""
        data = yaml.safe_load(yaml_data)
        return cls.from_dict(data)
    
    @classmethod
    def from_file(cls, file_path: Path) -> 'NetworkTopology':
        """Import from file (auto-detect format)."""
        with open(file_path, 'r') as f:
            content = f.read()
        
        if file_path.suffix.lower() == '.json':
            return cls.from_json(content)
        elif file_path.suffix.lower() in ['.yml', '.yaml']:
            return cls.from_yaml(content)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    def get_service_by_name(self, name: str) -> Optional[ServiceEndpoint]:
        """Get service endpoint by name."""
        for service in self.service_endpoints:
            if service.name == name:
                return service
        return None
    
    def get_services_by_port(self, port: int) -> List[ServiceEndpoint]:
        """Get service endpoints by port."""
        return [service for service in self.service_endpoints if service.port == port]
    
    def get_active_services(self) -> List[ServiceEndpoint]:
        """Get all active service endpoints."""
        return [service for service in self.service_endpoints if service.status == ServiceStatus.ACTIVE]
    
    def get_websocket_endpoints(self) -> List[str]:
        """Get all WebSocket endpoints."""
        endpoints = []
        for service in self.service_endpoints:
            endpoints.extend(service.websocket_endpoints)
        return endpoints
    
    def get_failover_mechanisms_by_type(self, failover_type: FailoverType) -> List[FailoverMechanism]:
        """Get failover mechanisms by type."""
        return [mechanism for mechanism in self.failover_mechanisms if mechanism.failover_type == failover_type]
    
    def validate_topology(self) -> List[str]:
        """Validate topology configuration and return any issues."""
        issues = []
        
        # Check for duplicate ports
        port_counts = {}
        for service in self.service_endpoints:
            port_counts[service.port] = port_counts.get(service.port, 0) + 1
        
        for port, count in port_counts.items():
            if count > 1:
                issues.append(f"Port {port} is used by {count} services")
        
        # Check for missing dependencies
        service_names = {service.name for service in self.service_endpoints}
        for service in self.service_endpoints:
            for dependency in service.dependencies:
                if dependency not in service_names:
                    issues.append(f"Service {service.name} depends on unknown service {dependency}")
        
        # Check DNS mappings
        for mapping in self.dns_mappings:
            if mapping.target_service not in service_names:
                issues.append(f"DNS mapping {mapping.domain} points to unknown service {mapping.target_service}")
        
        return issues
    
    def get_topology_summary(self) -> Dict[str, Any]:
        """Get comprehensive topology summary."""
        active_services = self.get_active_services()
        websocket_endpoints = self.get_websocket_endpoints()
        
        return {
            "discovery_timestamp": self.discovery_timestamp.isoformat(),
            "topology_version": self.topology_version,
            "network_range": self.local_network_range,
            "total_services": len(self.service_endpoints),
            "active_services": len(active_services),
            "total_flows": len(self.network_flows),
            "dns_mappings": len(self.dns_mappings),
            "websocket_endpoints": len(websocket_endpoints),
            "redis_configured": self.redis_coordination is not None,
            "redis_health": self.redis_coordination.health_status if self.redis_coordination else "unknown",
            "failover_mechanisms": len(self.failover_mechanisms),
            "port_allocations": len(self.port_allocations),
            "validation_issues": len(self.validate_topology())
        }