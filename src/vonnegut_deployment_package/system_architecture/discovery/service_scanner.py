#!/usr/bin/env python3
"""
Service Scanner - Comprehensive Service Discovery
===============================================

Unified scanner for all Beast Mode framework services.
"""

import asyncio
import logging
import requests
import aiohttp
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from .infrastructure_discoverer import InfrastructureDiscoverer, ServiceInfo, NetworkTopology
from .observatory_websocket_client import ObservatoryWebSocketClient


@dataclass
class ScanResult:
    """Result of service discovery scan."""
    services: List[ServiceInfo]
    network_topology: NetworkTopology
    websocket_endpoints: List[Dict[str, Any]]
    prometheus_metrics: Dict[str, Any]
    health_checks: Dict[str, Any]
    scan_time: datetime
    scan_duration_seconds: float
    scan_status: str = "completed"
    errors: List[str] = field(default_factory=list)


@dataclass
class PrometheusMetric:
    """Prometheus metric information."""
    name: str
    type: str
    help: str
    value: Optional[float] = None
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class ServiceScanner(ReflectiveModule):
    """
    Unified scanner for Observatory, Prometheus, Grafana and all
    Beast Mode framework services.
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "ServiceScanner"
        self._logger = logging.getLogger(f"system_architecture.{self.__class__.__name__}")
        self._session_timeout = 5.0
        
    async def scan_all_services(self) -> ScanResult:
        """Perform comprehensive scan of all services."""
        start_time = datetime.now()
        self._logger.info("Starting comprehensive service scan...")
        
        errors = []
        
        try:
            # Initialize discovery components
            discoverer = InfrastructureDiscoverer()
            websocket_client = ObservatoryWebSocketClient()
            
            # Discover services
            services = discoverer.discover_services()
            self._logger.info(f"Discovered {len(services)} services")
            
            # Discover network topology
            network_topology = discoverer.discover_network_config()
            self._logger.info("Network topology discovered")
            
            # Discover WebSocket endpoints
            websocket_endpoints = websocket_client.discover_websocket_endpoints()
            self._logger.info(f"Discovered {len(websocket_endpoints)} WebSocket endpoints")
            
            # Scan Prometheus metrics
            prometheus_metrics = await self._scan_prometheus_metrics()
            
            # Perform health checks
            health_checks = await self._perform_health_checks(services)
            
            # Create scan result
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = ScanResult(
                services=services,
                network_topology=network_topology,
                websocket_endpoints=[
                    {
                        "path": ep.path,
                        "purpose": ep.purpose,
                        "message_types": ep.message_types,
                        "connection_limits": ep.connection_limits,
                        "auth_required": ep.authentication_required
                    }
                    for ep in websocket_endpoints
                ],
                prometheus_metrics=prometheus_metrics,
                health_checks=health_checks,
                scan_time=start_time,
                scan_duration_seconds=duration,
                errors=errors
            )
            
            self._logger.info(f"Service scan completed in {duration:.2f}s")
            return result
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            error_msg = f"Service scan failed: {str(e)}"
            errors.append(error_msg)
            self._logger.error(error_msg)
            
            # Return partial result
            return ScanResult(
                services=[],
                network_topology=NetworkTopology(),
                websocket_endpoints=[],
                prometheus_metrics={},
                health_checks={},
                scan_time=start_time,
                scan_duration_seconds=duration,
                scan_status="failed",
                errors=errors
            )
    
    async def _scan_prometheus_metrics(self) -> Dict[str, Any]:
        """Scan Prometheus metrics API for live service status."""
        self._logger.info("Scanning Prometheus metrics...")
        
        prometheus_data = {
            "available": False,
            "metrics_count": 0,
            "targets": [],
            "alerts": [],
            "scrape_status": {}
        }
        
        try:
            # Check if Prometheus is available
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self._session_timeout)) as session:
                
                # Get metrics
                async with session.get("http://localhost:9090/api/v1/label/__name__/values") as response:
                    if response.status == 200:
                        data = await response.json()
                        prometheus_data["available"] = True
                        prometheus_data["metrics_count"] = len(data.get("data", []))
                        self._logger.info(f"Prometheus available with {prometheus_data['metrics_count']} metrics")
                
                # Get targets
                async with session.get("http://localhost:9090/api/v1/targets") as response:
                    if response.status == 200:
                        data = await response.json()
                        targets = data.get("data", {}).get("activeTargets", [])
                        prometheus_data["targets"] = [
                            {
                                "job": target.get("labels", {}).get("job", "unknown"),
                                "instance": target.get("labels", {}).get("instance", "unknown"),
                                "health": target.get("health", "unknown"),
                                "last_scrape": target.get("lastScrape"),
                                "scrape_duration": target.get("lastScrapeDuration")
                            }
                            for target in targets
                        ]
                        self._logger.info(f"Found {len(prometheus_data['targets'])} Prometheus targets")
                
                # Get alerts
                async with session.get("http://localhost:9090/api/v1/alerts") as response:
                    if response.status == 200:
                        data = await response.json()
                        alerts = data.get("data", {}).get("alerts", [])
                        prometheus_data["alerts"] = [
                            {
                                "name": alert.get("labels", {}).get("alertname", "unknown"),
                                "state": alert.get("state", "unknown"),
                                "value": alert.get("value"),
                                "labels": alert.get("labels", {})
                            }
                            for alert in alerts
                        ]
                        self._logger.info(f"Found {len(prometheus_data['alerts'])} Prometheus alerts")
                        
        except Exception as e:
            self._logger.warning(f"Could not scan Prometheus metrics: {e}")
            prometheus_data["error"] = str(e)
        
        return prometheus_data
    
    async def _perform_health_checks(self, services: List[ServiceInfo]) -> Dict[str, Any]:
        """Perform health checks on discovered services."""
        self._logger.info("Performing health checks...")
        
        health_results = {
            "total_services": len(services),
            "healthy_services": 0,
            "unhealthy_services": 0,
            "unknown_services": 0,
            "service_details": {}
        }
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self._session_timeout)) as session:
            
            for service in services:
                service_name = service.name.lower()
                health_info = {
                    "status": "unknown",
                    "response_time_ms": None,
                    "error": None,
                    "endpoints_checked": []
                }
                
                # Define health check endpoints for each service
                health_endpoints = self._get_health_endpoints(service)
                
                for endpoint in health_endpoints:
                    try:
                        start_time = datetime.now()
                        
                        async with session.get(endpoint) as response:
                            end_time = datetime.now()
                            response_time = (end_time - start_time).total_seconds() * 1000
                            
                            health_info["endpoints_checked"].append({
                                "url": endpoint,
                                "status_code": response.status,
                                "response_time_ms": response_time
                            })
                            
                            if response.status == 200:
                                health_info["status"] = "healthy"
                                health_info["response_time_ms"] = response_time
                                health_results["healthy_services"] += 1
                                self._logger.info(f"{service.name} health check passed ({response_time:.1f}ms)")
                                break
                            else:
                                health_info["status"] = "unhealthy"
                                health_info["error"] = f"HTTP {response.status}"
                                
                    except Exception as e:
                        health_info["endpoints_checked"].append({
                            "url": endpoint,
                            "error": str(e)
                        })
                        health_info["error"] = str(e)
                
                # Update counters
                if health_info["status"] == "healthy":
                    pass  # Already counted
                elif health_info["status"] == "unhealthy":
                    health_results["unhealthy_services"] += 1
                else:
                    health_results["unknown_services"] += 1
                
                health_results["service_details"][service_name] = health_info
        
        self._logger.info(f"Health checks completed: {health_results['healthy_services']} healthy, {health_results['unhealthy_services']} unhealthy, {health_results['unknown_services']} unknown")
        return health_results
    
    def _get_health_endpoints(self, service: ServiceInfo) -> List[str]:
        """Get health check endpoints for a service."""
        base_url = f"http://localhost:{service.port}" if service.port else None
        
        if not base_url:
            return []
        
        # Standard health endpoints
        endpoints = []
        
        if service.health_endpoint:
            endpoints.append(f"{base_url}{service.health_endpoint}")
        
        # Common health check patterns
        common_endpoints = ["/health", "/ready", "/metrics", "/api/health", "/status"]
        
        for endpoint in common_endpoints:
            full_url = f"{base_url}{endpoint}"
            if full_url not in endpoints:
                endpoints.append(full_url)
        
        return endpoints
    
    async def scan_configuration_files(self) -> Dict[str, Any]:
        """Scan and parse configuration files."""
        self._logger.info("Scanning configuration files...")
        
        config_scan = {
            "yaml_configs": {},
            "json_configs": {},
            "makefile_targets": [],
            "docker_configs": [],
            "environment_files": []
        }
        
        try:
            # Scan for YAML files
            yaml_files = list(Path(".").glob("**/*.yml")) + list(Path(".").glob("**/*.yaml"))
            for yaml_file in yaml_files[:20]:  # Limit for performance
                try:
                    with open(yaml_file, 'r') as f:
                        content = f.read()
                        config_scan["yaml_configs"][str(yaml_file)] = {
                            "size_bytes": len(content),
                            "lines": len(content.splitlines()),
                            "modified": datetime.fromtimestamp(yaml_file.stat().st_mtime).isoformat()
                        }
                except Exception as e:
                    self._logger.warning(f"Could not read YAML file {yaml_file}: {e}")
            
            # Scan for JSON files
            json_files = list(Path(".").glob("**/*.json"))
            for json_file in json_files[:20]:  # Limit for performance
                try:
                    with open(json_file, 'r') as f:
                        content = f.read()
                        config_scan["json_configs"][str(json_file)] = {
                            "size_bytes": len(content),
                            "lines": len(content.splitlines()),
                            "modified": datetime.fromtimestamp(json_file.stat().st_mtime).isoformat()
                        }
                except Exception as e:
                    self._logger.warning(f"Could not read JSON file {json_file}: {e}")
            
            # Scan Makefile
            makefile_path = Path("Makefile")
            if makefile_path.exists():
                config_scan["makefile_targets"] = self._parse_makefile_targets(makefile_path)
            
            # Scan for Docker files
            docker_files = list(Path(".").glob("**/Dockerfile*")) + list(Path(".").glob("**/docker-compose*.yml"))
            config_scan["docker_configs"] = [str(f) for f in docker_files]
            
            # Scan for environment files
            env_files = list(Path(".").glob("**/.env*"))
            config_scan["environment_files"] = [str(f) for f in env_files]
            
        except Exception as e:
            self._logger.error(f"Error scanning configuration files: {e}")
        
        self._logger.info(f"Configuration scan completed: {len(config_scan['yaml_configs'])} YAML, {len(config_scan['json_configs'])} JSON, {len(config_scan['makefile_targets'])} Makefile targets")
        return config_scan
    
    def _parse_makefile_targets(self, makefile_path: Path) -> List[Dict[str, Any]]:
        """Parse Makefile targets with dependencies."""
        targets = []
        
        try:
            with open(makefile_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and ':' in line and not line.startswith('#') and not line.startswith('\t'):
                        parts = line.split(':', 1)
                        target_name = parts[0].strip()
                        dependencies = [dep.strip() for dep in parts[1].split() if dep.strip()]
                        
                        if target_name and not target_name.startswith('.'):
                            targets.append({
                                "name": target_name,
                                "dependencies": dependencies,
                                "line_number": line_num
                            })
        except Exception as e:
            self._logger.warning(f"Could not parse Makefile: {e}")
        
        return targets
    
    def get_scan_summary(self, scan_result: ScanResult) -> Dict[str, Any]:
        """Get summary of scan results."""
        return {
            "scan_timestamp": scan_result.scan_time.isoformat(),
            "scan_duration_seconds": scan_result.scan_duration_seconds,
            "scan_status": scan_result.scan_status,
            "services": {
                "total_discovered": len(scan_result.services),
                "service_names": [s.name for s in scan_result.services],
                "ports_in_use": [s.port for s in scan_result.services if s.port]
            },
            "network": {
                "websocket_endpoints": len(scan_result.websocket_endpoints),
                "dns_mappings": len(scan_result.network_topology.dns_mappings),
                "network_range": scan_result.network_topology.local_network_range,
                "redis_endpoints": len(scan_result.network_topology.redis_endpoints)
            },
            "monitoring": {
                "prometheus_available": scan_result.prometheus_metrics.get("available", False),
                "metrics_count": scan_result.prometheus_metrics.get("metrics_count", 0),
                "prometheus_targets": len(scan_result.prometheus_metrics.get("targets", [])),
                "active_alerts": len(scan_result.prometheus_metrics.get("alerts", []))
            },
            "health": {
                "total_services": scan_result.health_checks.get("total_services", 0),
                "healthy_services": scan_result.health_checks.get("healthy_services", 0),
                "unhealthy_services": scan_result.health_checks.get("unhealthy_services", 0),
                "unknown_services": scan_result.health_checks.get("unknown_services", 0)
            },
            "errors": scan_result.errors,
            "overall_status": "healthy" if not scan_result.errors and scan_result.scan_status == "completed" else "issues_detected"
        }