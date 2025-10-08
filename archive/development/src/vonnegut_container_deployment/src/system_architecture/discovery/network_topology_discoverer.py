#!/usr/bin/env python3
"""
Network Topology Discoverer - Task 1.6 Implementation
======================================================

Implements comprehensive network topology discovery for the Beast Mode framework.
Maps local network topology with service endpoints, port allocations, Redis coordination,
WebSocket upgrade handling, and DNS failover mechanisms.

Author: Beast Mode Framework
Date: 2024-12-19
Version: 1.0
"""

import asyncio
import logging
import socket
import subprocess
import json
import yaml
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from pathlib import Path
import ipaddress
import psutil
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
    GracefulDegradationResult
)

from src.system_architecture.models.network_topology import (
    NetworkTopology,
    ServiceEndpoint,
    NetworkFlow,
    DNSMapping,
    RedisCoordination,
    WebSocketConfiguration,
    FailoverMechanism,
    ServiceStatus,
    Protocol,
    FlowType,
    FailoverType
)


# Data models are imported from src.system_architecture.models.network_topology


class NetworkTopologyDiscoverer(ReflectiveModule):
    """
    Network Topology Discoverer - Task 1.6 Implementation
    
    Discovers and maps comprehensive network topology including:
    - Local network topology with service endpoints and port allocations
    - Redis coordination endpoints with failover configuration
    - Service port allocations and routing configurations (8888, 9090, 3000, etc.)
    - Network flow diagrams with decision points
    - WebSocket upgrade handling and connection flows
    - DNS failover mechanisms for service continuity
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__()
        self.module_id = "NetworkTopologyDiscoverer"
        self._config = config or {}
        self._logger = logging.getLogger(f"system_architecture.{self.__class__.__name__}")
        
        # Discovery configuration
        self._scan_timeout = self._config.get('scan_timeout', 5.0)
        self._max_concurrent_scans = self._config.get('max_concurrent_scans', 10)
        self._known_ports = {
            8888: "Observatory Server",
            9090: "Prometheus", 
            3000: "Grafana",
            6379: "Redis Primary",
            6380: "Redis Fallback",
            8055: "Directus CMS",
            8000: "Prometheus Exporter"
        }
        
        # Infrastructure details from Appendix A
        self._tunnel_id = "d1e53e43-033f-4994-8f46-c83962ae3785"
        self._primary_domain = "observatory.nkllon.com"
        self._subdomains = [
            "grafana.observatory.nkllon.com",
            "prometheus.observatory.nkllon.com"
        ]
        self._websocket_endpoints = [
            "/ws/observatory",
            "/ws/emoji-rain", 
            "/ws/anomalies",
            "/ws/doctor-status"
        ]
        
        # Discovery results
        self._topology: Optional[NetworkTopology] = None
        self._discovery_errors: List[str] = []
        
        self._logger.info(f"{self.__class__.__name__} initialized")
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": self.module_id,
            "name": "NetworkTopologyDiscoverer",
            "version": "1.0.0",
            "description": "Comprehensive network topology discovery for Beast Mode framework",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "task": "1.6 - Network Topology Discovery",
            "specification": "system-architecture-wiring-diagram"
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        try:
            # Check if we can perform basic network operations
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(1)
            test_socket.close()
            
            # Check if we have recent topology data
            has_recent_data = (
                self._topology is not None and 
                (datetime.now() - self._topology.discovery_timestamp).total_seconds() < 3600
            )
            
            # Determine health status
            if len(self._discovery_errors) == 0 and has_recent_data:
                status = ModuleStatus.HEALTHY
                health_score = 1.0
                issues = []
            elif len(self._discovery_errors) <= 2:
                status = ModuleStatus.WARNING
                health_score = 0.8
                issues = self._discovery_errors[:2]
            else:
                status = ModuleStatus.ERROR
                health_score = 0.3
                issues = self._discovery_errors
            
        except Exception as e:
            status = ModuleStatus.ERROR
            health_score = 0.0
            issues = [f"NetworkTopologyDiscoverer failed: {str(e)}"]
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds(),
            error_count=len(self._discovery_errors),
            warning_count=0
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant"""
        try:
            # In degraded mode, we can still provide basic topology info
            # but with limited real-time scanning capabilities
            remaining_capabilities = [
                ModuleCapability.CORE_FUNCTIONALITY,
                ModuleCapability.DATA_PROCESSING
            ]
            
            degraded_capabilities = [
                ModuleCapability.VALIDATION,
                ModuleCapability.MONITORING
            ]
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=degraded_capabilities,
                remaining_capabilities=remaining_capabilities
            )
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[ModuleCapability.CORE_FUNCTIONALITY],
                remaining_capabilities=[],
                error_message=str(e)
            )
    
    def discover_network_topology(self) -> NetworkTopology:
        """
        Discover comprehensive network topology.
        
        Maps local network topology with service endpoints and port allocations,
        Redis coordination endpoints with failover configuration, service port
        allocations and routing configurations, network flow diagrams with
        decision points, WebSocket upgrade handling and connection flows,
        and DNS failover mechanisms for service continuity.
        """
        self._logger.info("Starting comprehensive network topology discovery...")
        self._discovery_errors.clear()
        
        try:
            # Discover local network range
            local_network = self._discover_local_network_range()
            
            # Discover service endpoints
            service_endpoints = self._discover_service_endpoints()
            
            # Discover network flows
            network_flows = self._discover_network_flows(service_endpoints)
            
            # Discover DNS mappings
            dns_mappings = self._discover_dns_mappings()
            
            # Discover Redis coordination
            redis_coordination = self._discover_redis_coordination()
            
            # Discover WebSocket configurations
            websocket_configs = self._discover_websocket_configurations()
            
            # Map port allocations
            port_allocations = self._map_port_allocations(service_endpoints)
            
            # Discover routing configurations
            routing_configs = self._discover_routing_configurations()
            
            # Discover failover mechanisms
            failover_mechanisms = self._discover_failover_mechanisms()
            
            # Create comprehensive topology
            topology = NetworkTopology(
                local_network_range=local_network,
                service_endpoints=service_endpoints,
                network_flows=network_flows,
                dns_mappings=dns_mappings,
                redis_coordination=redis_coordination,
                websocket_configs=websocket_configs,
                port_allocations=port_allocations,
                routing_configurations=routing_configs,
                failover_mechanisms=failover_mechanisms,
                discovery_timestamp=datetime.now()
            )
            
            self._topology = topology
            
            self._logger.info(f"Network topology discovery completed: {len(service_endpoints)} endpoints, {len(network_flows)} flows")
            
            return topology
                
        except Exception as e:
            error_msg = f"Network topology discovery failed: {str(e)}"
            self._discovery_errors.append(error_msg)
            self._logger.error(error_msg)
            raise
    
    def _discover_local_network_range(self) -> str:
        """Discover local network range."""
        try:
            # Get local IP address
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            # Determine network range
            if local_ip.startswith("192.168."):
                return "192.168.1.x"
            elif local_ip.startswith("10."):
                return "10.x.x.x"
            elif local_ip.startswith("172."):
                return "172.16-31.x.x"
            else:
                return f"{local_ip}/24"
                
        except Exception as e:
            self._logger.warning(f"Could not discover local network range: {e}")
            return "192.168.1.x"  # Default fallback
    
    def _discover_service_endpoints(self) -> List[ServiceEndpoint]:
        """Discover service endpoints with port scanning."""
        endpoints = []
        
        try:
            # Scan known ports concurrently
            with ThreadPoolExecutor(max_workers=self._max_concurrent_scans) as executor:
                future_to_port = {
                    executor.submit(self._scan_service_endpoint, port, service_name): (port, service_name)
                    for port, service_name in self._known_ports.items()
                }
                
                for future in as_completed(future_to_port):
                    port, service_name = future_to_port[future]
                    try:
                        endpoint = future.result()
                        if endpoint:
                            endpoints.append(endpoint)
                    except Exception as e:
                        self._logger.warning(f"Failed to scan port {port}: {e}")
            
            # Discover additional services
            additional_endpoints = self._discover_additional_services()
            endpoints.extend(additional_endpoints)
            
        except Exception as e:
            self._logger.error(f"Service endpoint discovery failed: {e}")
            self._discovery_errors.append(f"Service discovery error: {str(e)}")
        
        return endpoints
    
    def _scan_service_endpoint(self, port: int, service_name: str) -> Optional[ServiceEndpoint]:
        """Scan a specific service endpoint."""
        try:
            # Check if port is open
            if not self._is_port_open("localhost", port):
                return None
            
            # Get response time
            start_time = datetime.now()
            try:
                response = requests.get(f"http://localhost:{port}", timeout=self._scan_timeout)
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                status = "active"
            except requests.RequestException:
                response_time = None
                status = "port_open"
            
            # Determine health endpoint
            health_endpoint = self._get_health_endpoint(service_name, port)
            
            # Get WebSocket endpoints
            websocket_endpoints = self._get_websocket_endpoints(service_name, port)
            
            return ServiceEndpoint(
                name=service_name,
                host="localhost",
                port=port,
                protocol=Protocol.TCP,
                status=ServiceStatus.ACTIVE if status == "active" else ServiceStatus.UNKNOWN,
                response_time_ms=response_time,
                health_endpoint=health_endpoint,
                websocket_endpoints=websocket_endpoints,
                last_checked=datetime.now()
            )
            
        except Exception as e:
            self._logger.debug(f"Could not scan endpoint {service_name}:{port}: {e}")
            return None
    
    def _discover_additional_services(self) -> List[ServiceEndpoint]:
        """Discover additional services beyond known ports."""
        additional_endpoints = []
        
        try:
            # Scan common port ranges for additional services
            common_ports = [8080, 8081, 9000, 9001, 5000, 5001, 4000, 4001]
            
            for port in common_ports:
                if self._is_port_open("localhost", port):
                    endpoint = ServiceEndpoint(
                        name=f"Unknown Service {port}",
                        host="localhost",
                        port=port,
                        protocol=Protocol.TCP,
                        status=ServiceStatus.ACTIVE,
                        last_checked=datetime.now()
                    )
                    additional_endpoints.append(endpoint)
                    
        except Exception as e:
            self._logger.debug(f"Additional service discovery failed: {e}")
        
        return additional_endpoints
    
    def _discover_network_flows(self, endpoints: List[ServiceEndpoint]) -> List[NetworkFlow]:
        """Discover network flows with decision points."""
        flows = []
        
        try:
            # Internet to Cloudflare tunnel flow
            flows.append(NetworkFlow(
                source="Internet",
                destination="Cloudflare Edge",
                protocol=Protocol.HTTPS,
                port=443,
                flow_type=FlowType.INGRESS,
                decision_points=["DNS Resolution", "SSL/TLS Handshake", "Tunnel Routing"],
                routing_rules=[
                    {"condition": "domain == observatory.nkllon.com", "target": "localhost:8888"},
                    {"condition": "domain == grafana.observatory.nkllon.com", "target": "localhost:3000"},
                    {"condition": "domain == prometheus.observatory.nkllon.com", "target": "localhost:9090"}
                ],
                failover_config={
                    "primary": "Cloudflare Tunnel",
                    "fallback": "Direct IP Access",
                    "timeout": "30s"
                }
            ))
            
            # Internal service flows
            for endpoint in endpoints:
                if endpoint.name == "Observatory Server":
                    flows.append(NetworkFlow(
                        source="Cloudflare Tunnel",
                        destination="Observatory Server",
                        protocol=Protocol.HTTP,
                        port=8888,
                        flow_type=FlowType.INTERNAL,
                        decision_points=["WebSocket Upgrade", "Health Check"],
                        routing_rules=[
                            {"condition": "path == /ws/*", "action": "WebSocket Upgrade"},
                            {"condition": "path == /health", "action": "Health Check"}
                        ]
                    ))
                
                elif endpoint.name == "Prometheus":
                    flows.append(NetworkFlow(
                        source="Observatory Server",
                        destination="Prometheus",
                        protocol=Protocol.HTTP,
                        port=9090,
                        flow_type=FlowType.INTERNAL,
                        decision_points=["Metrics Scraping", "Target Discovery"],
                        routing_rules=[
                            {"condition": "path == /metrics", "action": "Metrics Collection"},
                            {"condition": "path == /api/v1/targets", "action": "Target Discovery"}
                        ]
                    ))
                
                elif endpoint.name == "Grafana":
                    flows.append(NetworkFlow(
                        source="Prometheus",
                        destination="Grafana",
                        protocol=Protocol.HTTP,
                        port=3000,
                        flow_type=FlowType.INTERNAL,
                        decision_points=["Dashboard Rendering", "Query Execution"],
                        routing_rules=[
                            {"condition": "path == /api/datasources", "action": "Datasource Query"},
                            {"condition": "path == /d/*", "action": "Dashboard Render"}
                        ]
                    ))
            
            # Redis coordination flows
            flows.append(NetworkFlow(
                source="Observatory Server",
                destination="Redis Primary",
                protocol=Protocol.REDIS,
                port=6379,
                flow_type=FlowType.INTERNAL,
                decision_points=["Connection Pool", "Failover Detection"],
                failover_config={
                    "primary": "192.168.1.119:6379",
                    "fallback": "localhost:6380",
                    "health_check_interval": "10s"
                }
            ))
            
        except Exception as e:
            self._logger.error(f"Network flow discovery failed: {e}")
            self._discovery_errors.append(f"Network flow discovery error: {str(e)}")
        
        return flows
    
    def _discover_dns_mappings(self) -> List[DNSMapping]:
        """Discover DNS mappings and failover mechanisms."""
        mappings = []
        
        try:
            # Primary domain mappings
            mappings.extend([
                DNSMapping(
                    domain="observatory.nkllon.com",
                    target_service="Observatory Server",
                    target_port=8888,
                    tunnel_id="d1e53e43-033f-4994-8f46-c83962ae3785",
                    failover_targets=["direct-ip-access"],
                    ttl_seconds=300
                ),
                DNSMapping(
                    domain="grafana.observatory.nkllon.com",
                    target_service="Grafana",
                    target_port=3000,
                    tunnel_id="d1e53e43-033f-4994-8f46-c83962ae3785",
                    failover_targets=["direct-ip-access"],
                    ttl_seconds=300
                ),
                DNSMapping(
                    domain="prometheus.observatory.nkllon.com",
                    target_service="Prometheus",
                    target_port=9090,
                    tunnel_id="d1e53e43-033f-4994-8f46-c83962ae3785",
                    failover_targets=["direct-ip-access"],
                    ttl_seconds=300
                )
            ])
            
            # Test DNS resolution
            for mapping in mappings:
                try:
                    resolved_ip = socket.gethostbyname(mapping.domain)
                    mapping.last_resolved = datetime.now()
                    self._logger.debug(f"DNS resolved {mapping.domain} -> {resolved_ip}")
                except socket.gaierror as e:
                    self._logger.warning(f"DNS resolution failed for {mapping.domain}: {e}")
                    mapping.failover_targets.append("dns-resolution-failed")
            
        except Exception as e:
            self._logger.error(f"DNS mapping discovery failed: {e}")
            self._discovery_errors.append(f"DNS mapping discovery error: {str(e)}")
        
        return mappings
    
    def _discover_redis_coordination(self) -> Optional[RedisCoordination]:
        """Discover Redis coordination endpoints with failover configuration."""
        try:
            # Test primary Redis endpoint
            primary_endpoint = "192.168.1.119:6379"
            primary_host, primary_port = primary_endpoint.split(":")
            
            primary_healthy = self._is_port_open(primary_host, int(primary_port))
            
            # Test fallback endpoints
            fallback_endpoints = ["localhost:6380"]
            healthy_fallbacks = []
            
            for endpoint in fallback_endpoints:
                host, port = endpoint.split(":")
                if self._is_port_open(host, int(port)):
                    healthy_fallbacks.append(endpoint)
            
            # Determine overall health
            if primary_healthy:
                health_status = "healthy"
            elif healthy_fallbacks:
                health_status = "degraded"
            else:
                health_status = "unhealthy"
            
            return RedisCoordination(
                primary_endpoint=primary_endpoint,
                fallback_endpoints=healthy_fallbacks,
                cluster_mode=False,
                failover_config={
                    "automatic_failover": True,
                    "failover_timeout": "5s",
                    "health_check_interval": "10s",
                    "max_retries": 3
                },
                health_status=health_status,
                last_health_check=datetime.now()
            )
            
        except Exception as e:
            self._logger.error(f"Redis coordination discovery failed: {e}")
            self._discovery_errors.append(f"Redis coordination discovery error: {str(e)}")
            return None
    
    def _discover_websocket_configurations(self) -> List[WebSocketConfiguration]:
        """Discover WebSocket configurations and upgrade handling."""
        configs = []
        
        try:
            # Observatory WebSocket endpoints
            observatory_ws_endpoints = [
                "/ws/observatory",
                "/ws/emoji-rain", 
                "/ws/anomalies",
                "/ws/doctor-status"
            ]
            
            for endpoint in observatory_ws_endpoints:
                config = WebSocketConfiguration(
                    endpoint=endpoint,
                    upgrade_path=f"http://localhost:8888{endpoint}",
                    supported_protocols=["websocket"],
                    connection_flow=[
                        "HTTP Request",
                        "Upgrade Header",
                        "Protocol Negotiation",
                        "WebSocket Handshake",
                        "Connection Established"
                    ],
                    authentication_required=False,
                    max_connections=1000,
                    heartbeat_interval=30
                )
                configs.append(config)
            
        except Exception as e:
            self._logger.error(f"WebSocket configuration discovery failed: {e}")
            self._discovery_errors.append(f"WebSocket configuration discovery error: {str(e)}")
        
        return configs
    
    def _map_port_allocations(self, endpoints: List[ServiceEndpoint]) -> Dict[int, str]:
        """Map service port allocations."""
        port_allocations = {}
        
        for endpoint in endpoints:
            port_allocations[endpoint.port] = endpoint.name
        
        # Add known port mappings
        port_allocations.update(self._known_ports)
        
        return port_allocations
    
    def _discover_routing_configurations(self) -> List[Dict[str, Any]]:
        """Discover routing configurations."""
        routing_configs = []
        
        try:
            # Cloudflare tunnel routing
            routing_configs.append({
                "type": "cloudflare_tunnel",
                "tunnel_id": "d1e53e43-033f-4994-8f46-c83962ae3785",
                "ingress_rules": [
                    {
                        "hostname": "observatory.nkllon.com",
                        "service": "http://localhost:8888",
                        "origin_request": {
                            "http_host_header": "observatory.nkllon.com"
                        }
                    },
                    {
                        "hostname": "grafana.observatory.nkllon.com", 
                        "service": "http://localhost:3000",
                        "origin_request": {
                            "http_host_header": "grafana.observatory.nkllon.com"
                        }
                    },
                    {
                        "hostname": "prometheus.observatory.nkllon.com",
                        "service": "http://localhost:9090",
                        "origin_request": {
                            "http_host_header": "prometheus.observatory.nkllon.com"
                        }
                    }
                ]
            })
            
            # Internal service routing
            routing_configs.append({
                "type": "internal_routing",
                "rules": [
                    {
                        "source": "Observatory",
                        "target": "Prometheus",
                        "protocol": "http",
                        "port": 9090,
                        "path_pattern": "/metrics"
                    },
                    {
                        "source": "Prometheus",
                        "target": "Grafana",
                        "protocol": "http", 
                        "port": 3000,
                        "path_pattern": "/api/datasources"
                    }
                ]
            })
            
        except Exception as e:
            self._logger.error(f"Routing configuration discovery failed: {e}")
            self._discovery_errors.append(f"Routing configuration discovery error: {str(e)}")
        
        return routing_configs
    
    def _discover_failover_mechanisms(self) -> List[FailoverMechanism]:
        """Discover failover mechanisms for service continuity."""
        failover_mechanisms = []
        
        try:
            # DNS failover
            failover_mechanisms.append(FailoverMechanism(
                mechanism_id="dns_failover_001",
                failover_type=FailoverType.DNS_FAILOVER,
                description="DNS-based failover for domain resolution",
                primary_target="Cloudflare DNS",
                fallback_targets=["Direct IP access"],
                detection_method="DNS resolution timeout",
                failover_time="30s",
                recovery_time="60s",
                health_check_interval="10s",
                max_retries=3,
                auto_recovery=True,
                notification_endpoints=["observatory.nkllon.com"]
            ))
            
            # Redis failover
            failover_mechanisms.append(FailoverMechanism(
                mechanism_id="redis_failover_001",
                failover_type=FailoverType.REDIS_FAILOVER,
                description="Redis coordination failover",
                primary_target="192.168.1.119:6379",
                fallback_targets=["localhost:6380"],
                detection_method="Connection health check",
                failover_time="5s",
                recovery_time="10s",
                health_check_interval="5s",
                max_retries=3,
                auto_recovery=True,
                notification_endpoints=["observatory.nkllon.com"]
            ))
            
            # WebSocket failover
            failover_mechanisms.append(FailoverMechanism(
                mechanism_id="websocket_failover_001",
                failover_type=FailoverType.WEBSOCKET_FAILOVER,
                description="WebSocket connection failover",
                primary_target="Observatory WebSocket",
                fallback_targets=["Polling mode"],
                detection_method="Connection heartbeat",
                failover_time="10s",
                recovery_time="20s",
                health_check_interval="5s",
                max_retries=3,
                auto_recovery=True,
                notification_endpoints=["observatory.nkllon.com"]
            ))
            
            # Service failover
            failover_mechanisms.append(FailoverMechanism(
                mechanism_id="service_failover_001",
                failover_type=FailoverType.SERVICE_FAILOVER,
                description="Service-level failover",
                primary_target="Observatory Server",
                fallback_targets=["Static error pages"],
                detection_method="Health endpoint check",
                failover_time="15s",
                recovery_time="30s",
                health_check_interval="10s",
                max_retries=3,
                auto_recovery=True,
                notification_endpoints=["observatory.nkllon.com"]
            ))
            
        except Exception as e:
            self._logger.error(f"Failover mechanism discovery failed: {e}")
            self._discovery_errors.append(f"Failover mechanism discovery error: {str(e)}")
        
        return failover_mechanisms
    
    def _is_port_open(self, host: str, port: int) -> bool:
        """Check if a port is open on the given host."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self._scan_timeout)
                result = sock.connect_ex((host, port))
                return result == 0
        except Exception:
            return False
    
    def _get_health_endpoint(self, service_name: str, port: int) -> Optional[str]:
        """Get health endpoint for a service."""
        health_endpoints = {
            "Observatory Server": "/health",
            "Prometheus": "/metrics",
            "Grafana": "/api/health",
            "Redis Primary": None,
            "Redis Fallback": None,
            "Directus CMS": "/server/ping"
        }
        return health_endpoints.get(service_name)
    
    def _get_websocket_endpoints(self, service_name: str, port: int) -> List[str]:
        """Get WebSocket endpoints for a service."""
        if service_name == "Observatory Server":
            return [
                "/ws/observatory",
                "/ws/emoji-rain",
                "/ws/anomalies", 
                "/ws/doctor-status"
            ]
        return []
    
    def generate_network_diagram(self) -> Dict[str, Any]:
        """Generate network topology diagram data."""
        if not self._topology:
            self.discover_network_topology()
        
        diagram_data = {
            "title": "Beast Mode Framework Network Topology",
            "timestamp": self._topology.discovery_timestamp.isoformat(),
            "network_range": self._topology.local_network_range,
            "services": [
                {
                    "name": ep.name,
                    "host": ep.host,
                    "port": ep.port,
                    "status": ep.status.value,
                    "health_endpoint": ep.health_endpoint,
                    "websocket_endpoints": ep.websocket_endpoints
                }
                for ep in self._topology.service_endpoints
            ],
            "flows": [
                {
                    "source": flow.source,
                    "destination": flow.destination,
                    "protocol": flow.protocol.value,
                    "port": flow.port,
                    "flow_type": flow.flow_type.value,
                    "decision_points": flow.decision_points,
                    "failover_config": flow.failover_config
                }
                for flow in self._topology.network_flows
            ],
            "dns_mappings": [
                {
                    "domain": mapping.domain,
                    "target_service": mapping.target_service,
                    "target_port": mapping.target_port,
                    "failover_targets": mapping.failover_targets
                }
                for mapping in self._topology.dns_mappings
            ],
            "redis_coordination": {
                "primary_endpoint": self._topology.redis_coordination.primary_endpoint,
                "fallback_endpoints": self._topology.redis_coordination.fallback_endpoints,
                "health_status": self._topology.redis_coordination.health_status
            } if self._topology.redis_coordination else None,
            "websocket_configs": [
                {
                    "endpoint": config.endpoint,
                    "upgrade_path": config.upgrade_path,
                    "connection_flow": config.connection_flow,
                    "max_connections": config.max_connections
                }
                for config in self._topology.websocket_configs
            ],
            "port_allocations": self._topology.port_allocations,
            "failover_mechanisms": self._topology.failover_mechanisms
        }
        
        return diagram_data
    
    def get_discovery_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of network topology discovery."""
        if not self._topology:
            return {"status": "no_discovery_performed"}
        
        return {
            "discovery_timestamp": self._topology.discovery_timestamp.isoformat(),
            "network_range": self._topology.local_network_range,
            "service_endpoints": len(self._topology.service_endpoints),
            "active_endpoints": len([ep for ep in self._topology.service_endpoints if ep.status == ServiceStatus.ACTIVE]),
            "network_flows": len(self._topology.network_flows),
            "dns_mappings": len(self._topology.dns_mappings),
            "websocket_endpoints": len(self._topology.websocket_configs),
            "redis_coordination": {
                "configured": self._topology.redis_coordination is not None,
                "health_status": self._topology.redis_coordination.health_status if self._topology.redis_coordination else "unknown"
            },
            "failover_mechanisms": len(self._topology.failover_mechanisms),
            "discovery_errors": len(self._discovery_errors),
            "status": "completed"
        }
    
    def export_topology_json(self) -> str:
        """Export topology to JSON format."""
        if not self._topology:
            self.discover_network_topology()
        
        return self._topology.to_json()
    
    def export_topology_yaml(self) -> str:
        """Export topology to YAML format."""
        if not self._topology:
            self.discover_network_topology()
        
        return self._topology.to_yaml()
    
    def export_topology_to_file(self, file_path: str) -> None:
        """Export topology to file (auto-detect format)."""
        if not self._topology:
            self.discover_network_topology()
        
        path = Path(file_path)
        if path.suffix.lower() == '.json':
            self._topology.to_json(path)
        elif path.suffix.lower() in ['.yml', '.yaml']:
            self._topology.to_yaml(path)
        else:
            # Default to JSON
            self._topology.to_json(path)
    
    def validate_topology(self) -> List[str]:
        """Validate topology configuration and return any issues."""
        if not self._topology:
            return ["No topology data available for validation"]
        
        return self._topology.validate_topology()
    
    def get_topology_summary(self) -> Dict[str, Any]:
        """Get comprehensive topology summary."""
        if not self._topology:
            return {"status": "no_topology_available"}
        
        return self._topology.get_topology_summary()