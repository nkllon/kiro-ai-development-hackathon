#!/usr/bin/env python3
"""
Infrastructure Discoverer - System Architecture Discovery Engine
==============================================================

Discovers and catalogs all infrastructure components in the Beast Mode ecosystem.
"""

import asyncio
import logging
import psutil
import socket
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json
import yaml

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


@dataclass
class ServiceInfo:
    """Information about a discovered service."""
    name: str
    process_id: Optional[int] = None
    port: Optional[int] = None
    config_files: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    health_endpoint: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    last_validated: Optional[datetime] = None
    validation_status: str = "unknown"
    validation_errors: List[str] = field(default_factory=list)


@dataclass
class NetworkTopology:
    """Network topology information."""
    services: List[ServiceInfo] = field(default_factory=list)
    local_network_range: str = "192.168.1.x"
    dns_mappings: List[Dict[str, str]] = field(default_factory=list)
    redis_endpoints: List[str] = field(default_factory=list)
    tunnel_configuration: Optional[Dict[str, Any]] = None


@dataclass
class ConfigurationMap:
    """Configuration mapping for discovered services."""
    yaml_configs: Dict[str, Any] = field(default_factory=dict)
    json_configs: Dict[str, Any] = field(default_factory=dict)
    env_configs: Dict[str, str] = field(default_factory=dict)
    makefile_targets: List[str] = field(default_factory=list)


class InfrastructureDiscoverer(ReflectiveModule):
    """
    Infrastructure discovery engine that scans and catalogs all
    Beast Mode framework components.
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "InfrastructureDiscoverer"
        self._logger = logging.getLogger(f"system_architecture.{self.__class__.__name__}")
        self._discovered_services: List[ServiceInfo] = []
        self._network_topology: Optional[NetworkTopology] = None
        self._configuration_map: Optional[ConfigurationMap] = None
        
    def discover_services(self) -> List[ServiceInfo]:
        """Discover running services and their configurations."""
        self._logger.info("Starting service discovery...")
        
        discovered_services = []
        
        # Discover Observatory service
        observatory_service = self._discover_observatory_service()
        if observatory_service:
            discovered_services.append(observatory_service)
            
        # Discover Prometheus service  
        prometheus_service = self._discover_prometheus_service()
        if prometheus_service:
            discovered_services.append(prometheus_service)
            
        # Discover Grafana service
        grafana_service = self._discover_grafana_service()
        if grafana_service:
            discovered_services.append(grafana_service)
            
        # Discover Redis coordination
        redis_service = self._discover_redis_service()
        if redis_service:
            discovered_services.append(redis_service)
        
        self._discovered_services = discovered_services
        self._logger.info(f"Discovered {len(self._discovered_services)} services")
        return self._discovered_services
    
    def _discover_observatory_service(self) -> Optional[ServiceInfo]:
        """Discover Observatory server configuration."""
        try:
            # Check if Observatory is running on port 8888
            if self._is_port_open("localhost", 8888):
                return ServiceInfo(
                    name="Observatory",
                    port=8888,
                    config_files=["observatory-daemon.py"],
                    health_endpoint="/health",
                    dependencies=["Redis", "WebSocket"],
                    validation_status="active"
                )
        except Exception as e:
            self._logger.warning(f"Could not discover Observatory service: {e}")
        return None
    
    def _discover_prometheus_service(self) -> Optional[ServiceInfo]:
        """Discover Prometheus server configuration."""
        try:
            # Check if Prometheus is running on port 9090
            if self._is_port_open("localhost", 9090):
                return ServiceInfo(
                    name="Prometheus",
                    port=9090,
                    config_files=["prometheus.yml"],
                    health_endpoint="/metrics",
                    dependencies=["Observatory"],
                    validation_status="active"
                )
        except Exception as e:
            self._logger.warning(f"Could not discover Prometheus service: {e}")
        return None
    
    def _discover_grafana_service(self) -> Optional[ServiceInfo]:
        """Discover Grafana server configuration."""
        try:
            # Check if Grafana is running on port 3000
            if self._is_port_open("localhost", 3000):
                return ServiceInfo(
                    name="Grafana", 
                    port=3000,
                    config_files=["grafana.ini"],
                    health_endpoint="/api/health",
                    dependencies=["Prometheus"],
                    validation_status="active"
                )
        except Exception as e:
            self._logger.warning(f"Could not discover Grafana service: {e}")
        return None
    
    def _discover_redis_service(self) -> Optional[ServiceInfo]:
        """Discover Redis coordination service."""
        try:
            # Check Redis endpoints
            redis_endpoints = ["192.168.1.119:6379", "localhost:6380"]
            active_endpoints = []
            
            for endpoint in redis_endpoints:
                host, port = endpoint.split(":")
                if self._is_port_open(host, int(port)):
                    active_endpoints.append(endpoint)
            
            if active_endpoints:
                return ServiceInfo(
                    name="Redis",
                    config_files=["redis.conf"],
                    dependencies=[],
                    validation_status="active",
                    validation_errors=[] if len(active_endpoints) > 1 else ["Single point of failure"]
                )
        except Exception as e:
            self._logger.warning(f"Could not discover Redis service: {e}")
        return None
    
    def _is_port_open(self, host: str, port: int) -> bool:
        """Check if a port is open on the given host."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                return result == 0
        except Exception:
            return False
    
    def discover_network_config(self) -> NetworkTopology:
        """Discover network topology and configuration."""
        self._logger.info("Discovering network topology...")
        
        # Create network topology
        topology = NetworkTopology(
            services=self._discovered_services,
            local_network_range="192.168.1.x",
            dns_mappings=[
                {"domain": "observatory.nkllon.com", "service": "Observatory", "port": "8888"},
                {"domain": "grafana.observatory.nkllon.com", "service": "Grafana", "port": "3000"},
                {"domain": "prometheus.observatory.nkllon.com", "service": "Prometheus", "port": "9090"}
            ],
            redis_endpoints=["192.168.1.119:6379", "localhost:6380"],
            tunnel_configuration={
                "tunnel_id": "d1e53e43-033f-4994-8f46-c83962ae3785",
                "ingress_rules": [
                    {"hostname": "observatory.nkllon.com", "service": "http://localhost:8888"},
                    {"hostname": "grafana.observatory.nkllon.com", "service": "http://localhost:3000"},
                    {"hostname": "prometheus.observatory.nkllon.com", "service": "http://localhost:9090"}
                ]
            }
        )
        
        self._network_topology = topology
        self._logger.info("Network topology discovery completed")
        return topology
    
    def discover_configurations(self) -> ConfigurationMap:
        """Discover configuration files and automation scripts."""
        self._logger.info("Discovering configuration files...")
        
        config_map = ConfigurationMap()
        
        # Discover YAML configurations
        yaml_files = list(Path(".").glob("**/*.yml")) + list(Path(".").glob("**/*.yaml"))
        for yaml_file in yaml_files[:10]:  # Limit to first 10 for performance
            try:
                with open(yaml_file, 'r') as f:
                    config_map.yaml_configs[str(yaml_file)] = yaml.safe_load(f)
            except Exception as e:
                self._logger.warning(f"Could not parse YAML file {yaml_file}: {e}")
        
        # Discover JSON configurations
        json_files = list(Path(".").glob("**/*.json"))
        for json_file in json_files[:10]:  # Limit to first 10 for performance
            try:
                with open(json_file, 'r') as f:
                    config_map.json_configs[str(json_file)] = json.load(f)
            except Exception as e:
                self._logger.warning(f"Could not parse JSON file {json_file}: {e}")
        
        # Discover Makefile targets
        makefile_path = Path("Makefile")
        if makefile_path.exists():
            config_map.makefile_targets = self._parse_makefile_targets(makefile_path)
        
        self._configuration_map = config_map
        self._logger.info(f"Configuration discovery completed: {len(config_map.yaml_configs)} YAML, {len(config_map.json_configs)} JSON, {len(config_map.makefile_targets)} Makefile targets")
        return config_map
    
    def _parse_makefile_targets(self, makefile_path: Path) -> List[str]:
        """Parse Makefile to extract targets."""
        targets = []
        try:
            with open(makefile_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and ':' in line and not line.startswith('#') and not line.startswith('\t'):
                        target = line.split(':')[0].strip()
                        if target and not target.startswith('.'):
                            targets.append(target)
        except Exception as e:
            self._logger.warning(f"Could not parse Makefile: {e}")
        
        return targets
    
    def discover_automation_scripts(self) -> Dict[str, List[str]]:
        """Discover Python automation scripts and their purposes."""
        self._logger.info("Discovering automation scripts...")
        
        scripts = {
            "python_scripts": [],
            "shell_scripts": [],
            "automation_targets": []
        }
        
        # Find Python scripts
        python_files = list(Path(".").glob("**/*.py"))
        for py_file in python_files:
            if any(keyword in str(py_file).lower() for keyword in ['daemon', 'server', 'deploy', 'tunnel', 'observatory']):
                scripts["python_scripts"].append(str(py_file))
        
        # Find shell scripts
        shell_files = list(Path(".").glob("**/*.sh"))
        scripts["shell_scripts"] = [str(f) for f in shell_files]
        
        # Extract automation-related Makefile targets
        if self._configuration_map and self._configuration_map.makefile_targets:
            automation_keywords = ['tunnel', 'dashboard', 'prometheus', 'grafana', 'deploy', 'start', 'stop', 'restart']
            for target in self._configuration_map.makefile_targets:
                if any(keyword in target.lower() for keyword in automation_keywords):
                    scripts["automation_targets"].append(target)
        
        self._logger.info(f"Discovered {len(scripts['python_scripts'])} Python scripts, {len(scripts['shell_scripts'])} shell scripts, {len(scripts['automation_targets'])} automation targets")
        return scripts
    
    def get_discovery_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of discovery results."""
        return {
            "services_discovered": len(self._discovered_services),
            "services": [
                {
                    "name": s.name,
                    "port": s.port,
                    "status": s.validation_status,
                    "dependencies": s.dependencies
                }
                for s in self._discovered_services
            ],
            "network_topology": {
                "dns_mappings": len(self._network_topology.dns_mappings) if self._network_topology else 0,
                "redis_endpoints": len(self._network_topology.redis_endpoints) if self._network_topology else 0,
                "tunnel_configured": bool(self._network_topology and self._network_topology.tunnel_configuration)
            },
            "configurations": {
                "yaml_files": len(self._configuration_map.yaml_configs) if self._configuration_map else 0,
                "json_files": len(self._configuration_map.json_configs) if self._configuration_map else 0,
                "makefile_targets": len(self._configuration_map.makefile_targets) if self._configuration_map else 0
            },
            "discovery_time": datetime.now().isoformat(),
            "status": "completed"
        }
    
    async def perform_comprehensive_discovery(self) -> Dict[str, Any]:
        """Perform complete infrastructure discovery."""
        self._logger.info("Starting comprehensive infrastructure discovery...")
        
        # Discover all components
        services = self.discover_services()
        network_config = self.discover_network_config()
        configurations = self.discover_configurations()
        automation_scripts = self.discover_automation_scripts()
        
        # Create comprehensive report
        discovery_report = {
            "discovery_timestamp": datetime.now().isoformat(),
            "services": [
                {
                    "name": s.name,
                    "port": s.port,
                    "status": s.validation_status,
                    "health_endpoint": s.health_endpoint,
                    "dependencies": s.dependencies,
                    "config_files": s.config_files
                }
                for s in services
            ],
            "network_topology": {
                "local_network": network_config.local_network_range,
                "dns_mappings": network_config.dns_mappings,
                "redis_endpoints": network_config.redis_endpoints,
                "tunnel_id": network_config.tunnel_configuration.get("tunnel_id") if network_config.tunnel_configuration else None
            },
            "configurations": {
                "yaml_configs": list(configurations.yaml_configs.keys()),
                "json_configs": list(configurations.json_configs.keys()),
                "makefile_targets": configurations.makefile_targets
            },
            "automation_scripts": automation_scripts,
            "summary": self.get_discovery_summary()
        }
        
        self._logger.info("Comprehensive infrastructure discovery completed")
        return discovery_report