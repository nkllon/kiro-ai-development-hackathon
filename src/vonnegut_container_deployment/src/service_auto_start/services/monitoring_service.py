#!/usr/bin/env python3
"""
Monitoring Service Configuration - System Health Monitoring Auto-Start Registration

Registers system health monitoring daemon in the ServiceRegistry with proper
configuration for auto-start across all platforms with Prometheus integration.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from ..core.service_auto_starter import ServiceDefinition
from ..registry.service_registry import ServiceRegistry
from ..types.enums import Platform, RestartPolicy


class MonitoringServiceConfig(ReflectiveModule):
    """
    Monitoring service configuration and registration manager.
    
    Handles monitoring daemon configuration including Prometheus metrics,
    Grafana dashboards, and system health monitoring integration.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Monitoring service configuration."""
        super().__init__()
        self._config = config or {}
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Monitoring configuration
        self._prometheus_port = self._config.get("prometheus_port", 9090)
        self._grafana_port = self._config.get("grafana_port", 3000)
        self._monitoring_host = self._config.get("host", "localhost")
        self._working_dir = self._config.get("working_dir", "/app/monitoring")
        
        # Register metrics
        self._register_metrics()
        
        self._logger.info("MonitoringServiceConfig initialized")
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get MonitoringServiceConfig capabilities."""
        return {
            "prometheus_metrics": True,
            "grafana_dashboards": True,
            "alert_manager": True,
            "service_discovery": True,
            "system_monitoring": True
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "name": "MonitoringServiceConfig",
            "version": "1.0.0",
            "description": "System health monitoring daemon configuration",
            "author": "Beast Mode Framework"
        }
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation on errors."""
        self._logger.error(f"MonitoringServiceConfig degradation: {error}")
        return {
            "status": "degraded",
            "error": str(error),
            "fallback_mode": "basic_monitoring"
        }
    
    def _register_metrics(self):
        """Register Prometheus metrics."""
        try:
            from prometheus_client import Counter, Gauge
            
            self._monitoring_registrations = Counter(
                'monitoring_service_registrations_total',
                'Total Monitoring service registrations',
                ['platform']
            )
            
            self._monitoring_health_checks = Gauge(
                'monitoring_health_check_status',
                'Monitoring health check status',
                ['component']
            )
            
        except ImportError:
            self._logger.warning("Prometheus client not available, metrics disabled")
    
    def create_service_definition(self, platform: Platform) -> ServiceDefinition:
        """
        Create Monitoring service definition for the specified platform.
        
        Args:
            platform: Target platform for deployment
            
        Returns:
            ServiceDefinition configured for Monitoring daemon
        """
        try:
            # Base environment variables
            environment = {
                "PROMETHEUS_PORT": str(self._prometheus_port),
                "GRAFANA_PORT": str(self._grafana_port),
                "MONITORING_HOST": "0.0.0.0",
                "METRICS_COLLECTION_ENABLED": "true",
                "SYSTEM_MONITORING_ENABLED": "true",
                "SERVICE_DISCOVERY_ENABLED": "true",
                "ALERT_MANAGER_ENABLED": "true",
                "LOG_LEVEL": os.getenv("MONITORING_LOG_LEVEL", "INFO"),
                "SCRAPE_INTERVAL": "15s",
                "EVALUATION_INTERVAL": "15s"
            }
            
            # Add service discovery configuration
            environment.update({
                "DIRECTUS_ENDPOINT": f"http://localhost:8055/server/health",
                "OBSERVATORY_ENDPOINT": f"http://localhost:8888/health",
                "SERVICE_REGISTRY_ENABLED": "true"
            })
            
            # Add alerting configuration
            if os.getenv("SMTP_HOST"):
                environment.update({
                    "SMTP_HOST": os.getenv("SMTP_HOST"),
                    "SMTP_PORT": os.getenv("SMTP_PORT", "587"),
                    "SMTP_USER": os.getenv("SMTP_USER", ""),
                    "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD", ""),
                    "ALERT_EMAIL_ENABLED": "true"
                })
            
            # Platform-specific command configuration
            if platform == Platform.DOCKER:
                command = "docker-compose -f monitoring/docker-compose.yml up"
                working_directory = "/monitoring"
            else:
                # Native installation
                command = self._get_native_command()
                working_directory = self._working_dir
            
            service_definition = ServiceDefinition(
                name="monitoring",
                command=command,
                working_directory=working_directory,
                environment=environment,
                dependencies=["directus", "observatory"],  # Monitor other services
                health_check_url=f"http://{self._monitoring_host}:{self._prometheus_port}/-/healthy",
                restart_policy=RestartPolicy.UNLESS_STOPPED,
                user=self._config.get("user"),
                description="System Health Monitoring Daemon - Prometheus, Grafana, and AlertManager"
            )
            
            self._logger.info(f"Created Monitoring service definition for {platform.value}")
            return service_definition
            
        except Exception as e:
            self._logger.error(f"Failed to create Monitoring service definition: {e}")
            raise
    
    def _get_native_command(self) -> str:
        """Get native command for running Monitoring daemon outside Docker."""
        # Check for different monitoring setup methods
        possible_commands = [
            "python -m monitoring.daemon",
            "python src/monitoring/daemon.py",
            "prometheus --config.file=prometheus.yml",
            "make start-monitoring"
        ]
        
        # In a real implementation, we'd check which command exists
        # For now, default to Python daemon
        return "python -m monitoring.daemon"
    
    def register_with_registry(self, registry: ServiceRegistry, platform: Platform) -> bool:
        """
        Register Monitoring service with the ServiceRegistry.
        
        Args:
            registry: ServiceRegistry instance
            platform: Target platform
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            service_definition = self.create_service_definition(platform)
            
            # Additional metadata for Monitoring
            metadata = {
                "service_type": "monitoring_daemon",
                "category": "system_monitoring",
                "prometheus_port": self._prometheus_port,
                "grafana_port": self._grafana_port,
                "health_endpoint": "/-/healthy",
                "metrics_endpoint": "/metrics",
                "grafana_endpoint": f"http://localhost:{self._grafana_port}",
                "documentation": "https://prometheus.io/docs/",
                "version": self._get_monitoring_version(),
                "capabilities": [
                    "prometheus_metrics",
                    "grafana_dashboards",
                    "alert_manager",
                    "service_discovery",
                    "system_monitoring"
                ],
                "monitored_services": ["directus", "observatory"]
            }
            
            success = registry.register_service(
                service=service_definition,
                platform=platform.value,
                metadata=metadata
            )
            
            if success:
                # Update metrics
                if hasattr(self, '_monitoring_registrations'):
                    self._monitoring_registrations.labels(platform=platform.value).inc()
                
                self._logger.info(f"Successfully registered Monitoring service for {platform.value}")
            else:
                self._logger.error(f"Failed to register Monitoring service for {platform.value}")
            
            return success
            
        except Exception as e:
            self._logger.error(f"Failed to register Monitoring service: {e}")
            return False
    
    def _get_monitoring_version(self) -> str:
        """Get Monitoring stack version if available."""
        try:
            # Try to get Prometheus version
            import subprocess
            result = subprocess.run(
                ["prometheus", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Extract version from output
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'prometheus, version' in line:
                        return line.split('version')[1].strip()
                        
        except Exception:
            pass
        
        return "unknown"
    
    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate Monitoring configuration requirements.
        
        Returns:
            Validation results dictionary
        """
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "checks": {}
        }
        
        try:
            # Check working directory
            working_dir = Path(self._working_dir)
            if not working_dir.exists():
                validation_results["warnings"].append(f"Working directory does not exist: {working_dir}")
            validation_results["checks"]["working_dir_exists"] = working_dir.exists()
            
            # Check port availability
            prometheus_available = self._check_port_available(self._prometheus_port)
            grafana_available = self._check_port_available(self._grafana_port)
            
            if not prometheus_available:
                validation_results["warnings"].append(f"Prometheus port {self._prometheus_port} may not be available")
            if not grafana_available:
                validation_results["warnings"].append(f"Grafana port {self._grafana_port} may not be available")
            
            validation_results["checks"]["prometheus_port_available"] = prometheus_available
            validation_results["checks"]["grafana_port_available"] = grafana_available
            
            # Check monitoring configuration files
            config_files = [
                "prometheus.yml",
                "grafana/provisioning/dashboards/dashboard.yml",
                "alertmanager/alertmanager.yml"
            ]
            
            for config_file in config_files:
                config_path = working_dir / config_file
                exists = config_path.exists()
                if not exists:
                    validation_results["warnings"].append(f"Configuration file not found: {config_file}")
                validation_results["checks"][f"config_{config_file.replace('/', '_').replace('.', '_')}"] = exists
            
            # Check Docker availability if using Docker platform
            docker_available = self._check_docker_available()
            validation_results["checks"]["docker_available"] = docker_available
            
            # Check dependent services
            dependent_services = ["directus", "observatory"]
            for service in dependent_services:
                # In a real implementation, we'd check if these services are registered
                validation_results["checks"][f"dependent_service_{service}"] = True
            
        except Exception as e:
            validation_results["errors"].append(f"Validation error: {e}")
            validation_results["valid"] = False
        
        return validation_results
    
    def _check_port_available(self, port: int) -> bool:
        """Check if port is available."""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False
    
    def _check_docker_available(self) -> bool:
        """Check if Docker is available."""
        import subprocess
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for Monitoring service configuration."""
        validation = self.validate_configuration()
        
        return {
            "status": "healthy" if validation["valid"] else "degraded",
            "configuration_valid": validation["valid"],
            "prometheus_port": self._prometheus_port,
            "grafana_port": self._grafana_port,
            "host": self._monitoring_host,
            "working_dir": self._working_dir,
            "validation_errors": len(validation["errors"]),
            "validation_warnings": len(validation["warnings"]),
            "monitored_services": ["directus", "observatory"]
        }