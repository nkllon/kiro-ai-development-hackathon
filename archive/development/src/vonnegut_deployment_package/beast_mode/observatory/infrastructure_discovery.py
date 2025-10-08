"""
Infrastructure Discovery Engine for System Architecture Wiring Diagram.

This module implements the Infrastructure Discovery Engine that automatically discovers
and catalogs all infrastructure components in the Beast Mode framework ecosystem.
"""

import asyncio
import json
import logging
import psutil
import subprocess
import yaml
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from enum import Enum

from ..core import ReflectiveModule
from .websocket.manager import WebSocketManager, WebSocketManagerConfig
from .websocket.connection import WebSocketConnection, ConnectionStatus
from .models import ObservatoryConfig

logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """Validation status for discovered components."""
    VALID = "valid"
    INVALID = "invalid"
    PENDING = "pending"
    ERROR = "error"


@dataclass
class ServiceInfo:
    """Information about a discovered service."""
    name: str
    process_id: Optional[int] = None
    port: Optional[int] = None
    config_files: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    health_endpoint: Optional[str] = None
    websocket_endpoints: List[str] = field(default_factory=list)
    
    # Versioning and validation fields
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    last_validated: Optional[datetime] = None
    validation_status: ValidationStatus = ValidationStatus.PENDING
    validation_errors: List[str] = field(default_factory=list)
    changed_by: str = "system"
    change_reason: Optional[str] = None


@dataclass
class NetworkConnection:
    """Network connection information."""
    source_ip: str
    source_port: int
    dest_ip: str
    dest_port: int
    protocol: str
    status: str
    process_id: Optional[int] = None


@dataclass
class DNSRecord:
    """DNS record information."""
    domain: str
    record_type: str
    value: str
    ttl: Optional[int] = None


@dataclass
class RoutingRule:
    """Routing rule information."""
    pattern: str
    target: str
    method: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class NetworkTopology:
    """Network topology information."""
    services: List[ServiceInfo] = field(default_factory=list)
    connections: List[NetworkConnection] = field(default_factory=list)
    dns_records: List[DNSRecord] = field(default_factory=list)
    routing_rules: List[RoutingRule] = field(default_factory=list)
    
    # Versioning and validation fields
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    last_validated: Optional[datetime] = None
    validation_status: ValidationStatus = ValidationStatus.PENDING
    accuracy_score: float = 0.0  # 0.0-1.0 confidence in accuracy


@dataclass
class ConfigurationMap:
    """Configuration file mapping."""
    config_files: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    tunnel_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    service_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class ScriptRegistry:
    """Registry of automation scripts and their targets."""
    makefile_targets: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    python_scripts: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    automation_chains: List[Dict[str, Any]] = field(default_factory=list)


class ObservatoryWebSocketClient:
    """WebSocket client for real-time Observatory service discovery."""
    
    def __init__(self, base_url: str = "ws://localhost:8888"):
        self.base_url = base_url
        self.connections: Dict[str, WebSocketConnection] = {}
        self.discovered_services: Dict[str, ServiceInfo] = {}
        self.real_time_metrics: Dict[str, Any] = {}
        
        # WebSocket endpoints to monitor
        self.endpoints = [
            "/ws/observatory",
            "/ws/anomalies", 
            "/ws/emoji-rain",
            "/ws/doctor-status"
        ]
        
        logger.info(f"Observatory WebSocket client initialized for {base_url}")
    
    async def connect_to_endpoints(self) -> bool:
        """Connect to all Observatory WebSocket endpoints."""
        success_count = 0
        
        for endpoint in self.endpoints:
            try:
                connection = WebSocketConnection(endpoint)
                await connection.connect()
                self.connections[endpoint] = connection
                success_count += 1
                logger.info(f"Connected to Observatory WebSocket endpoint: {endpoint}")
            except Exception as e:
                logger.error(f"Failed to connect to {endpoint}: {e}")
        
        return success_count > 0
    
    async def discover_services_from_websockets(self) -> Dict[str, ServiceInfo]:
        """Discover services by monitoring Observatory WebSocket feeds."""
        discovered = {}
        
        for endpoint, connection in self.connections.items():
            if connection.state.status == ConnectionStatus.CONNECTED:
                try:
                    # Send discovery request
                    discovery_request = {
                        "type": "service_discovery",
                        "timestamp": datetime.now().isoformat(),
                        "request_id": f"discovery_{endpoint.replace('/', '_')}"
                    }
                    
                    await connection.send_message(json.dumps(discovery_request))
                    
                    # Wait for response (with timeout)
                    try:
                        response = await asyncio.wait_for(
                            connection.receive_message(), 
                            timeout=5.0
                        )
                        
                        if response:
                            data = json.loads(response)
                            if data.get("type") == "service_discovery_response":
                                service_info = self._parse_service_response(data, endpoint)
                                if service_info:
                                    discovered[endpoint] = service_info
                    
                    except asyncio.TimeoutError:
                        logger.warning(f"Timeout waiting for discovery response from {endpoint}")
                    
                except Exception as e:
                    logger.error(f"Error discovering services from {endpoint}: {e}")
        
        return discovered
    
    def _parse_service_response(self, data: Dict[str, Any], endpoint: str) -> Optional[ServiceInfo]:
        """Parse service discovery response into ServiceInfo."""
        try:
            service_data = data.get("data", {})
            
            return ServiceInfo(
                name=service_data.get("name", f"service_{endpoint}"),
                port=service_data.get("port"),
                health_endpoint=service_data.get("health_endpoint"),
                websocket_endpoints=[endpoint],
                validation_status=ValidationStatus.VALID,
                last_validated=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error parsing service response: {e}")
            return None
    
    async def monitor_real_time_metrics(self) -> Dict[str, Any]:
        """Monitor real-time metrics from Observatory WebSocket feeds."""
        metrics = {}
        
        for endpoint, connection in self.connections.items():
            if connection.state.status == ConnectionStatus.CONNECTED:
                try:
                    # Request current metrics
                    metrics_request = {
                        "type": "metrics_request",
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    await connection.send_message(json.dumps(metrics_request))
                    
                    # Collect metrics for a short period
                    start_time = datetime.now()
                    endpoint_metrics = []
                    
                    while (datetime.now() - start_time).total_seconds() < 2.0:
                        try:
                            message = await asyncio.wait_for(
                                connection.receive_message(),
                                timeout=0.5
                            )
                            
                            if message:
                                data = json.loads(message)
                                if data.get("type") in ["metrics", "observatory_status", "anomaly"]:
                                    endpoint_metrics.append(data)
                        
                        except asyncio.TimeoutError:
                            break
                        except Exception as e:
                            logger.debug(f"Error receiving metrics from {endpoint}: {e}")
                            break
                    
                    metrics[endpoint] = endpoint_metrics
                    
                except Exception as e:
                    logger.error(f"Error monitoring metrics from {endpoint}: {e}")
        
        return metrics
    
    async def disconnect(self) -> None:
        """Disconnect from all WebSocket endpoints."""
        for connection in self.connections.values():
            try:
                await connection.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")
        
        self.connections.clear()
        logger.info("Disconnected from all Observatory WebSocket endpoints")


class InfrastructureDiscoverer(ReflectiveModule):
    """Infrastructure Discovery Engine for System Architecture Wiring Diagram."""
    
    def __init__(self, config: ObservatoryConfig):
        super().__init__()
        self.module_id = "infrastructure_discoverer"
        self._config = config
        self._websocket_client = ObservatoryWebSocketClient()
        self._discovered_services: Dict[str, ServiceInfo] = {}
        self._network_topology: Optional[NetworkTopology] = None
        self._configuration_map: Optional[ConfigurationMap] = None
        self._script_registry: Optional[ScriptRegistry] = None
        
        logger.info("Infrastructure Discovery Engine initialized")
    
    async def start_discovery(self) -> bool:
        """Start the infrastructure discovery process."""
        try:
            logger.info("Starting infrastructure discovery...")
            
            # Connect to Observatory WebSocket endpoints
            websocket_connected = await self._websocket_client.connect_to_endpoints()
            if websocket_connected:
                logger.info("Connected to Observatory WebSocket endpoints")
            
            # Discover services from WebSocket feeds
            websocket_services = await self._websocket_client.discover_services_from_websockets()
            self._discovered_services.update(websocket_services)
            
            # Discover running services
            running_services = await self._discover_running_services()
            self._discovered_services.update(running_services)
            
            # Discover network topology
            self._network_topology = await self._discover_network_topology()
            
            # Discover configuration files
            self._configuration_map = await self._discover_configurations()
            
            # Discover automation scripts
            self._script_registry = await self._discover_automation_scripts()
            
            logger.info(f"Infrastructure discovery completed. Found {len(self._discovered_services)} services")
            return True
            
        except Exception as e:
            logger.error(f"Infrastructure discovery failed: {e}")
            return False
    
    async def _discover_running_services(self) -> Dict[str, ServiceInfo]:
        """Discover running services on the system."""
        services = {}
        
        try:
            # Get all running processes
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'connections']):
                try:
                    proc_info = proc.info
                    cmdline = proc_info.get('cmdline', [])
                    
                    # Look for Observatory-related processes
                    if any('observatory' in str(cmd).lower() for cmd in cmdline):
                        service_name = f"observatory_{proc_info['pid']}"
                        
                        # Extract port information from connections
                        port = None
                        connections = proc_info.get('connections', [])
                        for conn in connections:
                            if conn.status == 'LISTEN':
                                port = conn.laddr.port
                                break
                        
                        services[service_name] = ServiceInfo(
                            name=service_name,
                            process_id=proc_info['pid'],
                            port=port,
                            validation_status=ValidationStatus.VALID,
                            last_validated=datetime.now()
                        )
                
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        
        except Exception as e:
            logger.error(f"Error discovering running services: {e}")
        
        return services
    
    async def _discover_network_topology(self) -> NetworkTopology:
        """Discover network topology and connections."""
        topology = NetworkTopology()
        
        try:
            # Get network connections
            connections = psutil.net_connections(kind='inet')
            
            for conn in connections:
                if conn.status == 'LISTEN':
                    # This is a listening service
                    service_name = f"service_{conn.laddr.port}"
                    
                    # Check if we already have this service
                    if service_name not in self._discovered_services:
                        self._discovered_services[service_name] = ServiceInfo(
                            name=service_name,
                            port=conn.laddr.port,
                            validation_status=ValidationStatus.VALID,
                            last_validated=datetime.now()
                        )
                    
                    topology.services.append(self._discovered_services[service_name])
                
                # Add to network connections
                topology.connections.append(NetworkConnection(
                    source_ip=conn.laddr.ip if conn.laddr else "unknown",
                    source_port=conn.laddr.port if conn.laddr else 0,
                    dest_ip=conn.raddr.ip if conn.raddr else "unknown", 
                    dest_port=conn.raddr.port if conn.raddr else 0,
                    protocol="tcp",  # Default to TCP
                    status=conn.status,
                    process_id=getattr(conn, 'pid', None)
                ))
        
        except Exception as e:
            logger.error(f"Error discovering network topology: {e}")
        
        topology.updated_at = datetime.now()
        topology.validation_status = ValidationStatus.VALID
        topology.last_validated = datetime.now()
        
        return topology
    
    async def _discover_configurations(self) -> ConfigurationMap:
        """Discover configuration files."""
        config_map = ConfigurationMap()
        
        try:
            # Look for common configuration files
            config_patterns = [
                "**/*.yaml",
                "**/*.yml", 
                "**/*.json",
                "**/*.env",
                "**/*.conf",
                "**/*.cfg"
            ]
            
            project_root = Path.cwd()
            
            for pattern in config_patterns:
                for config_file in project_root.glob(pattern):
                    try:
                        if config_file.is_file():
                            # Read configuration file
                            if config_file.suffix in ['.yaml', '.yml']:
                                with open(config_file, 'r') as f:
                                    config_data = yaml.safe_load(f)
                            elif config_file.suffix == '.json':
                                with open(config_file, 'r') as f:
                                    config_data = json.load(f)
                            else:
                                # For other formats, just store the path
                                config_data = {"file_path": str(config_file)}
                            
                            config_map.config_files[str(config_file)] = config_data
                            
                            # Check for tunnel configurations
                            if 'tunnel' in str(config_file).lower() or 'cloudflare' in str(config_file).lower():
                                config_map.tunnel_configs[str(config_file)] = config_data
                            
                            # Check for service configurations
                            if any(service in str(config_file).lower() for service in ['observatory', 'prometheus', 'grafana']):
                                config_map.service_configs[str(config_file)] = config_data
                    
                    except Exception as e:
                        logger.debug(f"Error reading config file {config_file}: {e}")
        
        except Exception as e:
            logger.error(f"Error discovering configurations: {e}")
        
        return config_map
    
    async def _discover_automation_scripts(self) -> ScriptRegistry:
        """Discover automation scripts and Makefile targets."""
        registry = ScriptRegistry()
        
        try:
            # Parse Makefile
            makefile_path = Path("Makefile")
            if makefile_path.exists():
                makefile_targets = await self._parse_makefile(makefile_path)
                registry.makefile_targets = makefile_targets
            
            # Discover Python scripts
            python_scripts = await self._discover_python_scripts()
            registry.python_scripts = python_scripts
        
        except Exception as e:
            logger.error(f"Error discovering automation scripts: {e}")
        
        return registry
    
    async def _parse_makefile(self, makefile_path: Path) -> Dict[str, Dict[str, Any]]:
        """Parse Makefile to extract targets and dependencies."""
        targets = {}
        
        try:
            with open(makefile_path, 'r') as f:
                content = f.read()
            
            # Simple Makefile parsing (this could be enhanced)
            lines = content.split('\n')
            current_target = None
            
            for line in lines:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Check if this is a target line (ends with :)
                if ':' in line and not line.startswith('\t'):
                    target_name = line.split(':')[0].strip()
                    dependencies = [dep.strip() for dep in line.split(':')[1].split() if dep.strip()]
                    
                    targets[target_name] = {
                        "dependencies": dependencies,
                        "commands": [],
                        "affected_components": self._identify_affected_components(target_name)
                    }
                    current_target = target_name
                
                # Check if this is a command line (starts with tab)
                elif line.startswith('\t') and current_target:
                    command = line[1:].strip()  # Remove leading tab
                    targets[current_target]["commands"].append(command)
        
        except Exception as e:
            logger.error(f"Error parsing Makefile: {e}")
        
        return targets
    
    def _identify_affected_components(self, target_name: str) -> List[str]:
        """Identify which infrastructure components are affected by a Makefile target."""
        components = []
        
        # Map target names to components based on naming patterns
        if 'tunnel' in target_name.lower():
            components.extend(['cloudflare_tunnel', 'dns_routing'])
        
        if 'dashboard' in target_name.lower():
            components.extend(['observatory_server', 'websocket_endpoints'])
        
        if 'prometheus' in target_name.lower():
            components.append('prometheus_server')
        
        if 'grafana' in target_name.lower():
            components.append('grafana_server')
        
        if 'task' in target_name.lower():
            components.append('beast_mode_components')
        
        if 'phase' in target_name.lower():
            components.extend(['beast_mode_components', 'dag_registry'])
        
        return components
    
    async def _discover_python_scripts(self) -> Dict[str, Dict[str, Any]]:
        """Discover Python automation scripts."""
        scripts = {}
        
        try:
            # Look for Python scripts in common locations
            script_patterns = [
                "**/*observatory*.py",
                "**/*tunnel*.py", 
                "**/*prometheus*.py",
                "**/*grafana*.py",
                "**/*deploy*.py",
                "**/*automation*.py"
            ]
            
            project_root = Path.cwd()
            
            for pattern in script_patterns:
                for script_file in project_root.glob(pattern):
                    if script_file.is_file():
                        script_info = {
                            "path": str(script_file),
                            "purpose": self._infer_script_purpose(script_file),
                            "target_components": self._identify_target_components(script_file),
                            "dependencies": await self._extract_script_dependencies(script_file)
                        }
                        scripts[str(script_file)] = script_info
        
        except Exception as e:
            logger.error(f"Error discovering Python scripts: {e}")
        
        return scripts
    
    def _infer_script_purpose(self, script_path: Path) -> str:
        """Infer the purpose of a Python script from its name and path."""
        script_name = script_path.name.lower()
        
        if 'observatory' in script_name:
            return "Observatory server lifecycle management"
        elif 'tunnel' in script_name:
            return "Cloudflare tunnel operations"
        elif 'prometheus' in script_name:
            return "Prometheus metrics collection and validation"
        elif 'grafana' in script_name:
            return "Grafana dashboard and datasource management"
        elif 'deploy' in script_name:
            return "Deployment automation"
        else:
            return "Automation script"
    
    def _identify_target_components(self, script_path: Path) -> List[str]:
        """Identify target components for a Python script."""
        components = []
        script_name = script_path.name.lower()
        
        if 'observatory' in script_name:
            components.extend(['observatory_server', 'websocket_endpoints'])
        elif 'tunnel' in script_name:
            components.extend(['cloudflare_tunnel', 'dns_routing'])
        elif 'prometheus' in script_name:
            components.append('prometheus_server')
        elif 'grafana' in script_name:
            components.append('grafana_server')
        
        return components
    
    async def _extract_script_dependencies(self, script_path: Path) -> List[str]:
        """Extract dependencies from a Python script."""
        dependencies = []
        
        try:
            with open(script_path, 'r') as f:
                content = f.read()
            
            # Look for import statements
            import_lines = [line.strip() for line in content.split('\n') if line.strip().startswith(('import ', 'from '))]
            
            for line in import_lines:
                if 'import ' in line:
                    module = line.split('import ')[1].split()[0]
                    dependencies.append(module)
                elif 'from ' in line:
                    module = line.split('from ')[1].split()[0]
                    dependencies.append(module)
        
        except Exception as e:
            logger.debug(f"Error extracting dependencies from {script_path}: {e}")
        
        return dependencies
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time metrics from Observatory WebSocket feeds."""
        return await self._websocket_client.monitor_real_time_metrics()
    
    def get_discovered_services(self) -> Dict[str, ServiceInfo]:
        """Get all discovered services."""
        return self._discovered_services.copy()
    
    def get_network_topology(self) -> Optional[NetworkTopology]:
        """Get discovered network topology."""
        return self._network_topology
    
    def get_configuration_map(self) -> Optional[ConfigurationMap]:
        """Get discovered configuration map."""
        return self._configuration_map
    
    def get_script_registry(self) -> Optional[ScriptRegistry]:
        """Get discovered script registry."""
        return self._script_registry
    
    async def stop_discovery(self) -> None:
        """Stop the discovery process."""
        await self._websocket_client.disconnect()
        logger.info("Infrastructure discovery stopped")
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> List['ModuleCapability']:
        """Get Infrastructure Discoverer capabilities."""
        from src.rm_ddd.core.unified_reflective_module import ModuleCapability
        return [
            ModuleCapability.MONITORING,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.API_INTEGRATION,
        ]
    
    def get_health_status(self) -> 'ModuleHealth':
        """Get health status of the Infrastructure Discoverer."""
        from src.rm_ddd.core.unified_reflective_module import ModuleHealth, ModuleStatus
        
        # Determine status based on discovery state
        if self._discovered_services:
            status = ModuleStatus.HEALTHY
            health_score = min(1.0, len(self._discovered_services) / 10.0)  # Scale based on discoveries
            issues = []
        else:
            status = ModuleStatus.WARNING
            health_score = 0.5
            issues = ["No services discovered yet"]
        
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
        """Get Infrastructure Discoverer performance metrics."""
        return {
            "discovered_services_count": len(self._discovered_services),
            "websocket_connections": len(self._websocket_client.connections),
            "network_connections": len(self._network_topology.connections) if self._network_topology else 0,
            "configuration_files": len(self._configuration_map.config_files) if self._configuration_map else 0,
            "makefile_targets": len(self._script_registry.makefile_targets) if self._script_registry else 0,
            "python_scripts": len(self._script_registry.python_scripts) if self._script_registry else 0,
        }