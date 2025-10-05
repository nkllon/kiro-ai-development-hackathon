"""
Network Topology Discovery System for System Architecture Wiring Diagram.

This module implements comprehensive network topology discovery to map
local network topology, Redis coordination endpoints, service port allocations,
and create network flow diagrams.
"""

import asyncio
import json
import logging
import psutil
import socket
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum

from ..core import ReflectiveModule

logger = logging.getLogger(__name__)


class NetworkProtocol(Enum):
    """Network protocols."""
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    HTTP = "http"
    HTTPS = "https"
    WEBSOCKET = "websocket"
    REDIS = "redis"


class ServiceStatus(Enum):
    """Service status."""
    RUNNING = "running"
    STOPPED = "stopped"
    STARTING = "starting"
    STOPPING = "stopping"
    ERROR = "error"
    UNKNOWN = "unknown"


class ConnectionState(Enum):
    """Network connection states."""
    LISTEN = "listen"
    ESTABLISHED = "established"
    TIME_WAIT = "time_wait"
    CLOSE_WAIT = "close_wait"
    FIN_WAIT = "fin_wait"
    SYN_SENT = "syn_sent"
    SYN_RECV = "syn_recv"


@dataclass
class NetworkInterface:
    """Network interface information."""
    name: str
    ip_address: str
    netmask: str
    broadcast: Optional[str] = None
    mac_address: Optional[str] = None
    is_up: bool = True
    interface_type: str = "ethernet"  # ethernet, wifi, loopback, etc.
    
    # Performance metrics
    bytes_sent: int = 0
    bytes_received: int = 0
    packets_sent: int = 0
    packets_received: int = 0


@dataclass
class ServiceEndpoint:
    """Service endpoint information."""
    service_name: str
    host: str
    port: int
    protocol: NetworkProtocol
    status: ServiceStatus = ServiceStatus.UNKNOWN
    process_id: Optional[int] = None
    process_name: Optional[str] = None
    
    # Service-specific information
    health_endpoint: Optional[str] = None
    websocket_endpoints: List[str] = field(default_factory=list)
    api_endpoints: List[str] = field(default_factory=list)
    
    # Performance metrics
    connection_count: int = 0
    response_time_ms: Optional[float] = None
    last_health_check: Optional[datetime] = None
    
    # Validation fields
    is_valid: bool = True
    validation_errors: List[str] = field(default_factory=list)
    last_validated: Optional[datetime] = None


@dataclass
class NetworkConnection:
    """Network connection information."""
    source_ip: str
    source_port: int
    dest_ip: str
    dest_port: int
    protocol: NetworkProtocol
    state: ConnectionState
    process_id: Optional[int] = None
    process_name: Optional[str] = None
    
    # Connection metadata
    established_time: Optional[datetime] = None
    bytes_sent: int = 0
    bytes_received: int = 0
    
    # Validation fields
    is_valid: bool = True
    validation_errors: List[str] = field(default_factory=list)
    last_validated: Optional[datetime] = None


@dataclass
class RedisEndpoint:
    """Redis coordination endpoint information."""
    host: str
    port: int
    role: str  # primary, secondary, replica, etc.
    status: ServiceStatus = ServiceStatus.UNKNOWN
    is_primary: bool = False
    is_failover_target: bool = False
    
    # Redis-specific information
    redis_version: Optional[str] = None
    memory_usage: Optional[int] = None
    connected_clients: int = 0
    keys_count: int = 0
    
    # Failover configuration
    failover_timeout: Optional[int] = None
    failover_priority: int = 0
    
    # Validation fields
    is_valid: bool = True
    validation_errors: List[str] = field(default_factory=list)
    last_validated: Optional[datetime] = None


@dataclass
class NetworkFlow:
    """Network flow information."""
    flow_id: str
    source_endpoint: ServiceEndpoint
    dest_endpoint: ServiceEndpoint
    protocol: NetworkProtocol
    data_flow_direction: str  # inbound, outbound, bidirectional
    
    # Flow characteristics
    bytes_transferred: int = 0
    packets_transferred: int = 0
    flow_duration: Optional[float] = None  # seconds
    
    # Decision points
    routing_decisions: List[str] = field(default_factory=list)
    load_balancing: Optional[str] = None
    failover_mechanisms: List[str] = field(default_factory=list)


@dataclass
class NetworkTopology:
    """Complete network topology information."""
    interfaces: List[NetworkInterface] = field(default_factory=list)
    service_endpoints: List[ServiceEndpoint] = field(default_factory=list)
    network_connections: List[NetworkConnection] = field(default_factory=list)
    redis_endpoints: List[RedisEndpoint] = field(default_factory=list)
    network_flows: List[NetworkFlow] = field(default_factory=list)
    
    # Topology metadata
    discovery_timestamp: datetime = field(default_factory=datetime.now)
    local_network_range: str = "192.168.1.x"
    total_services: int = 0
    active_connections: int = 0
    redis_coordination_active: bool = False
    
    # Validation results
    validation_success_rate: float = 0.0
    connectivity_test_results: Dict[str, bool] = field(default_factory=dict)


class NetworkTopologyDiscoverer(ReflectiveModule):
    """Comprehensive network topology discovery system."""
    
    def __init__(self):
        super().__init__()
        self.module_id = "network_topology_discoverer"
        self._topology: Optional[NetworkTopology] = None
        
        # Known service endpoints from requirements
        self._known_endpoints = [
            ("observatory", "localhost", 8888, NetworkProtocol.HTTP),
            ("prometheus", "localhost", 9090, NetworkProtocol.HTTP),
            ("grafana", "localhost", 3000, NetworkProtocol.HTTP),
        ]
        
        # Known Redis endpoints from requirements
        self._known_redis_endpoints = [
            ("192.168.1.119", 6379, "primary"),
            ("localhost", 6380, "fallback"),
        ]
        
        # WebSocket endpoints to discover
        self._websocket_endpoints = [
            "/ws/observatory",
            "/ws/anomalies",
            "/ws/emoji-rain",
            "/ws/doctor-status"
        ]
        
        logger.info("Network Topology Discoverer initialized")
    
    async def discover_topology(self) -> NetworkTopology:
        """Discover complete network topology."""
        try:
            logger.info("Starting network topology discovery...")
            
            self._topology = NetworkTopology()
            
            # Discover network interfaces
            await self._discover_network_interfaces()
            
            # Discover service endpoints
            await self._discover_service_endpoints()
            
            # Discover network connections
            await self._discover_network_connections()
            
            # Discover Redis coordination endpoints
            await self._discover_redis_endpoints()
            
            # Analyze network flows
            await self._analyze_network_flows()
            
            # Validate connectivity
            await self._validate_connectivity()
            
            # Update topology metadata
            self._update_topology_metadata()
            
            logger.info(f"Network topology discovery completed: {self._topology.total_services} services, "
                       f"{self._topology.active_connections} connections")
            
            return self._topology
            
        except Exception as e:
            logger.error(f"Network topology discovery failed: {e}")
            raise
    
    async def _discover_network_interfaces(self) -> None:
        """Discover network interfaces."""
        try:
            # Get network interface information
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            for interface_name, addresses in interfaces.items():
                interface_stats = stats.get(interface_name)
                
                # Find IPv4 address
                ip_address = None
                netmask = None
                broadcast = None
                mac_address = None
                
                for addr in addresses:
                    if addr.family == socket.AF_INET:  # IPv4
                        ip_address = addr.address
                        netmask = addr.netmask
                        broadcast = addr.broadcast
                    elif addr.family == psutil.AF_LINK:  # MAC address
                        mac_address = addr.address
                
                if ip_address:
                    interface = NetworkInterface(
                        name=interface_name,
                        ip_address=ip_address,
                        netmask=netmask or "255.255.255.0",
                        broadcast=broadcast,
                        mac_address=mac_address,
                        is_up=interface_stats.isup if interface_stats else True,
                        interface_type=self._determine_interface_type(interface_name)
                    )
                    
                    # Get interface statistics
                    if interface_stats:
                        interface.bytes_sent = interface_stats.bytes_sent
                        interface.bytes_received = interface_stats.bytes_recv
                        interface.packets_sent = interface_stats.packets_sent
                        interface.packets_received = interface_stats.packets_recv
                    
                    self._topology.interfaces.append(interface)
        
        except Exception as e:
            logger.error(f"Error discovering network interfaces: {e}")
    
    def _determine_interface_type(self, interface_name: str) -> str:
        """Determine interface type from name."""
        name_lower = interface_name.lower()
        
        if "lo" in name_lower:
            return "loopback"
        elif "eth" in name_lower:
            return "ethernet"
        elif "wlan" in name_lower or "wifi" in name_lower:
            return "wifi"
        elif "docker" in name_lower:
            return "docker"
        else:
            return "unknown"
    
    async def _discover_service_endpoints(self) -> None:
        """Discover service endpoints."""
        try:
            # Discover known endpoints
            for service_name, host, port, protocol in self._known_endpoints:
                endpoint = ServiceEndpoint(
                    service_name=service_name,
                    host=host,
                    port=port,
                    protocol=protocol,
                    status=ServiceStatus.UNKNOWN
                )
                
                # Test endpoint connectivity
                endpoint.status = await self._test_endpoint_status(endpoint)
                
                # Discover service-specific endpoints
                if service_name == "observatory":
                    endpoint.websocket_endpoints = self._websocket_endpoints
                    endpoint.health_endpoint = "/health"
                    endpoint.api_endpoints = ["/metrics", "/ready"]
                elif service_name == "prometheus":
                    endpoint.health_endpoint = "/-/healthy"
                    endpoint.api_endpoints = ["/api/v1/targets", "/metrics"]
                elif service_name == "grafana":
                    endpoint.health_endpoint = "/api/health"
                    endpoint.api_endpoints = ["/api/datasources", "/api/dashboards"]
                
                self._topology.service_endpoints.append(endpoint)
            
            # Discover additional services from network connections
            await self._discover_additional_services()
        
        except Exception as e:
            logger.error(f"Error discovering service endpoints: {e}")
    
    async def _test_endpoint_status(self, endpoint: ServiceEndpoint) -> ServiceStatus:
        """Test endpoint status."""
        try:
            # Try to connect to the endpoint
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2.0)
            
            result = sock.connect_ex((endpoint.host, endpoint.port))
            sock.close()
            
            if result == 0:
                return ServiceStatus.RUNNING
            else:
                return ServiceStatus.STOPPED
        
        except Exception as e:
            logger.debug(f"Error testing endpoint {endpoint.host}:{endpoint.port}: {e}")
            return ServiceStatus.ERROR
    
    async def _discover_additional_services(self) -> None:
        """Discover additional services from network connections."""
        try:
            # Get all network connections
            connections = psutil.net_connections(kind='inet')
            
            # Find listening services
            listening_services = {}
            
            for conn in connections:
                if conn.status == 'LISTEN' and conn.laddr:
                    host, port = conn.laddr
                    service_key = f"{host}:{port}"
                    
                    if service_key not in listening_services:
                        # Determine service name
                        service_name = self._identify_service_by_port(port)
                        
                        endpoint = ServiceEndpoint(
                            service_name=service_name,
                            host=host,
                            port=port,
                            protocol=NetworkProtocol.TCP,
                            status=ServiceStatus.RUNNING,
                            process_id=getattr(conn, 'pid', None)
                        )
                        
                        listening_services[service_key] = endpoint
            
            # Add discovered services to topology
            for endpoint in listening_services.values():
                # Check if we already have this endpoint
                if not any(ep.host == endpoint.host and ep.port == endpoint.port 
                          for ep in self._topology.service_endpoints):
                    self._topology.service_endpoints.append(endpoint)
        
        except Exception as e:
            logger.error(f"Error discovering additional services: {e}")
    
    def _identify_service_by_port(self, port: int) -> str:
        """Identify service by port number."""
        port_services = {
            22: "ssh",
            80: "http",
            443: "https",
            3000: "grafana",
            6379: "redis",
            8080: "http-alt",
            8888: "observatory",
            9090: "prometheus",
            9200: "elasticsearch",
            27017: "mongodb",
            3306: "mysql",
            5432: "postgresql",
        }
        
        return port_services.get(port, f"service-{port}")
    
    async def _discover_network_connections(self) -> None:
        """Discover network connections."""
        try:
            connections = psutil.net_connections(kind='inet')
            
            for conn in connections:
                if conn.laddr and conn.raddr:
                    # Determine protocol
                    protocol = NetworkProtocol.TCP
                    if hasattr(conn, 'type') and conn.type == socket.SOCK_DGRAM:
                        protocol = NetworkProtocol.UDP
                    
                    # Determine connection state
                    state = ConnectionState.ESTABLISHED
                    if conn.status == 'LISTEN':
                        state = ConnectionState.LISTEN
                    elif conn.status == 'TIME_WAIT':
                        state = ConnectionState.TIME_WAIT
                    elif conn.status == 'CLOSE_WAIT':
                        state = ConnectionState.CLOSE_WAIT
                    elif conn.status == 'FIN_WAIT':
                        state = ConnectionState.FIN_WAIT
                    elif conn.status == 'SYN_SENT':
                        state = ConnectionState.SYN_SENT
                    elif conn.status == 'SYN_RECV':
                        state = ConnectionState.SYN_RECV
                    
                    connection = NetworkConnection(
                        source_ip=conn.laddr.ip,
                        source_port=conn.laddr.port,
                        dest_ip=conn.raddr.ip,
                        dest_port=conn.raddr.port,
                        protocol=protocol,
                        state=state,
                        process_id=getattr(conn, 'pid', None)
                    )
                    
                    self._topology.network_connections.append(connection)
        
        except Exception as e:
            logger.error(f"Error discovering network connections: {e}")
    
    async def _discover_redis_endpoints(self) -> None:
        """Discover Redis coordination endpoints."""
        try:
            for host, port, role in self._known_redis_endpoints:
                redis_endpoint = RedisEndpoint(
                    host=host,
                    port=port,
                    role=role,
                    is_primary=(role == "primary"),
                    is_failover_target=(role == "fallback"),
                    failover_priority=0 if role == "primary" else 1
                )
                
                # Test Redis connectivity
                redis_endpoint.status = await self._test_redis_connectivity(redis_endpoint)
                
                # Get Redis information if connected
                if redis_endpoint.status == ServiceStatus.RUNNING:
                    await self._get_redis_info(redis_endpoint)
                
                self._topology.redis_endpoints.append(redis_endpoint)
        
        except Exception as e:
            logger.error(f"Error discovering Redis endpoints: {e}")
    
    async def _test_redis_connectivity(self, redis_endpoint: RedisEndpoint) -> ServiceStatus:
        """Test Redis connectivity."""
        try:
            # Try to connect to Redis
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2.0)
            
            result = sock.connect_ex((redis_endpoint.host, redis_endpoint.port))
            sock.close()
            
            if result == 0:
                return ServiceStatus.RUNNING
            else:
                return ServiceStatus.STOPPED
        
        except Exception as e:
            logger.debug(f"Error testing Redis connectivity {redis_endpoint.host}:{redis_endpoint.port}: {e}")
            return ServiceStatus.ERROR
    
    async def _get_redis_info(self, redis_endpoint: RedisEndpoint) -> None:
        """Get Redis information."""
        try:
            # Use redis-cli to get information
            result = await asyncio.create_subprocess_exec(
                "redis-cli", "-h", redis_endpoint.host, "-p", str(redis_endpoint.port),
                "INFO", "server",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                # Parse Redis INFO output
                info_text = stdout.decode('utf-8')
                for line in info_text.split('\n'):
                    if line.startswith('redis_version:'):
                        redis_endpoint.redis_version = line.split(':', 1)[1]
                    elif line.startswith('connected_clients:'):
                        redis_endpoint.connected_clients = int(line.split(':', 1)[1])
                    elif line.startswith('used_memory:'):
                        redis_endpoint.memory_usage = int(line.split(':', 1)[1])
                    elif line.startswith('db0:keys='):
                        redis_endpoint.keys_count = int(line.split('=', 1)[1].split(',')[0])
        
        except Exception as e:
            logger.debug(f"Error getting Redis info: {e}")
    
    async def _analyze_network_flows(self) -> None:
        """Analyze network flows and decision points."""
        try:
            # Create flows between service endpoints
            for source_endpoint in self._topology.service_endpoints:
                for dest_endpoint in self._topology.service_endpoints:
                    if source_endpoint != dest_endpoint:
                        # Check if there are connections between these endpoints
                        connections = [
                            conn for conn in self._topology.network_connections
                            if ((conn.source_ip == source_endpoint.host and conn.source_port == source_endpoint.port) or
                                (conn.dest_ip == source_endpoint.host and conn.dest_port == source_endpoint.port)) and
                               ((conn.source_ip == dest_endpoint.host and conn.source_port == dest_endpoint.port) or
                                (conn.dest_ip == dest_endpoint.host and conn.dest_port == dest_endpoint.port))
                        ]
                        
                        if connections:
                            flow = NetworkFlow(
                                flow_id=f"{source_endpoint.service_name}_to_{dest_endpoint.service_name}",
                                source_endpoint=source_endpoint,
                                dest_endpoint=dest_endpoint,
                                protocol=connections[0].protocol,
                                data_flow_direction="bidirectional"
                            )
                            
                            # Add routing decisions based on service types
                            if dest_endpoint.service_name == "prometheus":
                                flow.routing_decisions.append("metrics_collection")
                            elif dest_endpoint.service_name == "grafana":
                                flow.routing_decisions.append("dashboard_visualization")
                            elif dest_endpoint.service_name == "observatory":
                                flow.routing_decisions.append("coordination_monitoring")
                            
                            # Add failover mechanisms for Redis
                            if dest_endpoint.service_name == "redis":
                                flow.failover_mechanisms.append("automatic_failover")
                                flow.failover_mechanisms.append("connection_retry")
                            
                            self._topology.network_flows.append(flow)
        
        except Exception as e:
            logger.error(f"Error analyzing network flows: {e}")
    
    async def _validate_connectivity(self) -> None:
        """Validate connectivity between components."""
        try:
            # Test connectivity between service endpoints
            for endpoint in self._topology.service_endpoints:
                connectivity_result = await self._test_endpoint_status(endpoint)
                self._topology.connectivity_test_results[f"{endpoint.host}:{endpoint.port}"] = (
                    connectivity_result == ServiceStatus.RUNNING
                )
            
            # Test Redis connectivity
            for redis_endpoint in self._topology.redis_endpoints:
                connectivity_result = await self._test_redis_connectivity(redis_endpoint)
                self._topology.connectivity_test_results[f"redis_{redis_endpoint.host}:{redis_endpoint.port}"] = (
                    connectivity_result == ServiceStatus.RUNNING
                )
        
        except Exception as e:
            logger.error(f"Error validating connectivity: {e}")
    
    def _update_topology_metadata(self) -> None:
        """Update topology metadata."""
        if not self._topology:
            return
        
        self._topology.total_services = len(self._topology.service_endpoints)
        self._topology.active_connections = len([
            conn for conn in self._topology.network_connections
            if conn.state == ConnectionState.ESTABLISHED
        ])
        self._topology.redis_coordination_active = any(
            redis.status == ServiceStatus.RUNNING for redis in self._topology.redis_endpoints
        )
        
        # Calculate validation success rate
        total_tests = len(self._topology.connectivity_test_results)
        successful_tests = sum(1 for result in self._topology.connectivity_test_results.values() if result)
        self._topology.validation_success_rate = (
            successful_tests / total_tests if total_tests > 0 else 0.0
        )
    
    def get_topology(self) -> Optional[NetworkTopology]:
        """Get the current network topology."""
        return self._topology
    
    def get_service_endpoints(self) -> List[ServiceEndpoint]:
        """Get all service endpoints."""
        if not self._topology:
            return []
        return self._topology.service_endpoints.copy()
    
    def get_redis_endpoints(self) -> List[RedisEndpoint]:
        """Get all Redis endpoints."""
        if not self._topology:
            return []
        return self._topology.redis_endpoints.copy()
    
    def get_network_flows(self) -> List[NetworkFlow]:
        """Get all network flows."""
        if not self._topology:
            return []
        return self._topology.network_flows.copy()
    
    def get_connectivity_status(self) -> Dict[str, bool]:
        """Get connectivity test results."""
        if not self._topology:
            return {}
        return self._topology.connectivity_test_results.copy()
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> List['ModuleCapability']:
        """Get Network Topology Discoverer capabilities."""
        from src.rm_ddd.core.unified_reflective_module import ModuleCapability
        return [
            ModuleCapability.MONITORING,
            ModuleCapability.NETWORK_ANALYSIS,
            ModuleCapability.DATA_PROCESSING,
        ]
    
    def get_health_status(self) -> 'ModuleHealth':
        """Get health status of the Network Topology Discoverer."""
        from src.rm_ddd.core.unified_reflective_module import ModuleHealth, ModuleStatus
        
        if self._topology and self._topology.total_services > 0:
            status = ModuleStatus.HEALTHY
            health_score = min(1.0, self._topology.validation_success_rate)
            issues = []
        else:
            status = ModuleStatus.WARNING
            health_score = 0.5
            issues = ["No network topology available"]
        
        uptime = (datetime.now() - self._start_time).total_seconds()
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=uptime,
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    async def get_metrics(self) -> Dict[str, any]:
        """Get Network Topology Discoverer performance metrics."""
        if not self._topology:
            return {
                "total_services": 0,
                "active_connections": 0,
                "redis_endpoints": 0,
                "network_flows": 0,
                "validation_success_rate": 0.0,
            }
        
        return {
            "total_services": self._topology.total_services,
            "active_connections": self._topology.active_connections,
            "redis_endpoints": len(self._topology.redis_endpoints),
            "network_flows": len(self._topology.network_flows),
            "validation_success_rate": self._topology.validation_success_rate,
            "network_interfaces": len(self._topology.interfaces),
            "connectivity_tests": len(self._topology.connectivity_test_results),
            "successful_connectivity_tests": sum(1 for r in self._topology.connectivity_test_results.values() if r),
        }