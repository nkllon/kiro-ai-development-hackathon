#!/usr/bin/env python3
"""
Observatory Service Configuration - WebSocket Event System Auto-Start Registration

Registers Observatory WebSocket event system in the ServiceRegistry with proper
configuration for auto-start across all platforms with health check integration.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from ..core.service_auto_starter import ServiceDefinition
from ..registry.service_registry import ServiceRegistry
from ..types.enums import Platform, RestartPolicy


class ObservatoryServiceConfig(ReflectiveModule):
    """
    Observatory service configuration and registration manager.
    
    Handles Observatory-specific configuration requirements including WebSocket
    endpoints, event routing, and health check integration.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Observatory service configuration."""
        super().__init__()
        self._config = config or {}
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Observatory configuration
        self._observatory_port = self._config.get("port", 8888)
        self._observatory_host = self._config.get("host", "localhost")
        self._working_dir = self._config.get("working_dir", "/app/observatory")
        
        # Register metrics
        self._register_metrics()
        
        self._logger.info("ObservatoryServiceConfig initialized")
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get ObservatoryServiceConfig capabilities."""
        return {
            "websocket_events": True,
            "real_time_monitoring": True,
            "event_routing": True,
            "prometheus_integration": True
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "name": "ObservatoryServiceConfig",
            "version": "1.0.0",
            "description": "Observatory WebSocket event system configuration",
            "author": "Beast Mode Framework"
        }
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation on errors."""
        self._logger.error(f"ObservatoryServiceConfig degradation: {error}")
        return {
            "status": "degraded",
            "error": str(error),
            "fallback_mode": "basic_websocket_server"
        }
    
    def _register_metrics(self):
        """Register Prometheus metrics."""
        try:
            from prometheus_client import Counter, Gauge
            
            self._observatory_registrations = Counter(
                'observatory_service_registrations_total',
                'Total Observatory service registrations',
                ['platform']
            )
            
            self._observatory_health_checks = Gauge(
                'observatory_health_check_status',
                'Observatory health check status',
                ['endpoint']
            )
            
        except ImportError:
            self._logger.warning("Prometheus client not available, metrics disabled")
    
    def create_service_definition(self, platform: Platform) -> ServiceDefinition:
        """
        Create Observatory service definition for the specified platform.
        
        Args:
            platform: Target platform for deployment
            
        Returns:
            ServiceDefinition configured for Observatory
        """
        try:
            # Base environment variables
            environment = {
                "OBSERVATORY_PORT": str(self._observatory_port),
                "OBSERVATORY_HOST": "0.0.0.0",
                "WEBSOCKET_ENABLED": "true",
                "EVENT_ROUTING_ENABLED": "true",
                "HEALTH_CHECK_ENABLED": "true",
                "LOG_LEVEL": os.getenv("OBSERVATORY_LOG_LEVEL", "INFO"),
                "PROMETHEUS_ENABLED": "true",
                "PROMETHEUS_PORT": "9090"
            }
            
            # Add Redis configuration for event persistence
            if os.getenv("REDIS_HOST"):
                environment.update({
                    "REDIS_HOST": os.getenv("REDIS_HOST", "localhost"),
                    "REDIS_PORT": os.getenv("REDIS_PORT", "6379"),
                    "REDIS_PASSWORD": os.getenv("REDIS_PASSWORD", ""),
                    "EVENT_PERSISTENCE_ENABLED": "true"
                })
            
            # Platform-specific command configuration
            if platform == Platform.DOCKER:
                command = "python -m observatory.main"
                working_directory = "/observatory"
            else:
                # Native installation
                command = self._get_native_command()
                working_directory = self._working_dir
            
            service_definition = ServiceDefinition(
                name="observatory",
                command=command,
                working_directory=working_directory,
                environment=environment,
                dependencies=[],  # Observatory can run independently
                health_check_url=f"http://{self._observatory_host}:{self._observatory_port}/health",
                restart_policy=RestartPolicy.UNLESS_STOPPED,
                user=self._config.get("user"),
                description="Observatory WebSocket Event System - Real-time event monitoring and routing"
            )
            
            self._logger.info(f"Created Observatory service definition for {platform.value}")
            return service_definition
            
        except Exception as e:
            self._logger.error(f"Failed to create Observatory service definition: {e}")
            raise
    
    def _get_native_command(self) -> str:
        """Get native command for running Observatory outside Docker."""
        # Check for different Observatory installation methods
        possible_commands = [
            "python -m observatory.main",
            "python src/observatory/main.py",
            "python observatory/main.py",
            "python main.py"
        ]
        
        # In a real implementation, we'd check which command exists
        # For now, default to module execution
        return "python -m observatory.main"
    
    def register_with_registry(self, registry: ServiceRegistry, platform: Platform) -> bool:
        """
        Register Observatory service with the ServiceRegistry.
        
        Args:
            registry: ServiceRegistry instance
            platform: Target platform
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            service_definition = self.create_service_definition(platform)
            
            # Additional metadata for Observatory
            metadata = {
                "service_type": "websocket_server",
                "category": "event_system",
                "port": self._observatory_port,
                "health_endpoint": "/health",
                "websocket_endpoint": "/ws",
                "events_endpoint": "/events",
                "metrics_endpoint": "/metrics",
                "documentation": "https://github.com/beast-mode/observatory",
                "version": self._get_observatory_version(),
                "capabilities": [
                    "websocket_events",
                    "real_time_monitoring", 
                    "event_routing",
                    "prometheus_metrics"
                ]
            }
            
            success = registry.register_service(
                service=service_definition,
                platform=platform.value,
                metadata=metadata
            )
            
            if success:
                # Update metrics
                if hasattr(self, '_observatory_registrations'):
                    self._observatory_registrations.labels(platform=platform.value).inc()
                
                self._logger.info(f"Successfully registered Observatory service for {platform.value}")
            else:
                self._logger.error(f"Failed to register Observatory service for {platform.value}")
            
            return success
            
        except Exception as e:
            self._logger.error(f"Failed to register Observatory service: {e}")
            return False
    
    def _get_observatory_version(self) -> str:
        """Get Observatory version if available."""
        try:
            # Try to import and get version
            import sys
            sys.path.append(str(Path(self._working_dir)))
            
            try:
                from observatory import __version__
                return __version__
            except ImportError:
                pass
            
            # Try to get from git if in development
            import subprocess
            result = subprocess.run(
                ["git", "describe", "--tags", "--always"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=self._working_dir
            )
            if result.returncode == 0:
                return result.stdout.strip()
                
        except Exception:
            pass
        
        return "unknown"
    
    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate Observatory configuration requirements.
        
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
            port_available = self._check_port_available(self._observatory_port)
            if not port_available:
                validation_results["warnings"].append(f"Port {self._observatory_port} may not be available")
            validation_results["checks"]["port_available"] = port_available
            
            # Check Python availability
            python_available = self._check_python_available()
            if not python_available:
                validation_results["errors"].append("Python interpreter not available")
                validation_results["valid"] = False
            validation_results["checks"]["python_available"] = python_available
            
            # Check Redis configuration if enabled
            if os.getenv("REDIS_HOST"):
                redis_vars = ["REDIS_HOST", "REDIS_PORT"]
                for var in redis_vars:
                    if not os.getenv(var):
                        validation_results["warnings"].append(f"Redis enabled but missing config: {var}")
                    validation_results["checks"][f"redis_{var}"] = bool(os.getenv(var))
            
            # Check Observatory source code
            observatory_main = working_dir / "observatory" / "main.py"
            if not observatory_main.exists():
                validation_results["warnings"].append("Observatory main.py not found in expected location")
            validation_results["checks"]["observatory_main_exists"] = observatory_main.exists()
            
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
    
    def _check_python_available(self) -> bool:
        """Check if Python interpreter is available."""
        import subprocess
        try:
            result = subprocess.run(
                ["python", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for Observatory service configuration."""
        validation = self.validate_configuration()
        
        return {
            "status": "healthy" if validation["valid"] else "degraded",
            "configuration_valid": validation["valid"],
            "port": self._observatory_port,
            "host": self._observatory_host,
            "working_dir": self._working_dir,
            "validation_errors": len(validation["errors"]),
            "validation_warnings": len(validation["warnings"]),
            "websocket_enabled": True,
            "event_routing_enabled": True
        }