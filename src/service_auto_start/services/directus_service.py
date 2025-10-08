#!/usr/bin/env python3
"""
Directus Service Configuration - CMS Auto-Start Registration

Registers Directus CMS service in the ServiceRegistry with proper configuration
for auto-start across all platforms with health check integration.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from ..core.service_auto_starter import ServiceDefinition
from ..registry.service_registry import ServiceRegistry
from ..types.enums import Platform, RestartPolicy


class DirectusServiceConfig(ReflectiveModule):
    """
    Directus service configuration and registration manager.
    
    Handles Directus-specific configuration requirements including database
    connections, environment variables, and health check endpoints.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Directus service configuration."""
        super().__init__()
        self._config = config or {}
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Directus configuration
        self._directus_port = self._config.get("port", 8055)
        self._directus_host = self._config.get("host", "localhost")
        self._working_dir = self._config.get("working_dir", "/app/directus")
        
        # Register metrics
        self._register_metrics()
        
        self._logger.info("DirectusServiceConfig initialized")
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get DirectusServiceConfig capabilities."""
        return {
            "cms_management": True,
            "multi_platform_support": True,
            "health_check_integration": True,
            "database_support": ["sqlite3", "postgresql"]
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "name": "DirectusServiceConfig",
            "version": "1.0.0",
            "description": "Directus CMS service configuration and registration",
            "author": "Beast Mode Framework"
        }
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation on errors."""
        self._logger.error(f"DirectusServiceConfig degradation: {error}")
        return {
            "status": "degraded",
            "error": str(error),
            "fallback_mode": "manual_directus_setup"
        }
    
    def _register_metrics(self):
        """Register Prometheus metrics."""
        try:
            from prometheus_client import Counter, Gauge
            
            self._directus_registrations = Counter(
                'directus_service_registrations_total',
                'Total Directus service registrations',
                ['platform']
            )
            
            self._directus_health_checks = Gauge(
                'directus_health_check_status',
                'Directus health check status',
                ['endpoint']
            )
            
        except ImportError:
            self._logger.warning("Prometheus client not available, metrics disabled")
    
    def create_service_definition(self, platform: Platform) -> ServiceDefinition:
        """
        Create Directus service definition for the specified platform.
        
        Args:
            platform: Target platform for deployment
            
        Returns:
            ServiceDefinition configured for Directus
        """
        try:
            # Base environment variables
            environment = {
                "KEY": os.getenv("DIRECTUS_KEY", ""),
                "SECRET": os.getenv("DIRECTUS_SECRET", ""),
                "DB_CLIENT": os.getenv("DIRECTUS_DB_CLIENT", "sqlite3"),
                "DB_FILENAME": os.getenv("DIRECTUS_DB_FILENAME", "./data/database.db"),
                "CACHE_ENABLED": "false",
                "RATE_LIMITER_ENABLED": "false",
                "HOST": "0.0.0.0",
                "PORT": str(self._directus_port),
                "PUBLIC_URL": f"http://{self._directus_host}:{self._directus_port}"
            }
            
            # Add database configuration if using PostgreSQL
            if os.getenv("DIRECTUS_DB_CLIENT") == "pg":
                environment.update({
                    "DB_HOST": os.getenv("DIRECTUS_DB_HOST", "localhost"),
                    "DB_PORT": os.getenv("DIRECTUS_DB_PORT", "5432"),
                    "DB_DATABASE": os.getenv("DIRECTUS_DB_DATABASE", "directus"),
                    "DB_USER": os.getenv("DIRECTUS_DB_USER", "directus"),
                    "DB_PASSWORD": os.getenv("DIRECTUS_DB_PASSWORD", "")
                })
            
            # Platform-specific command configuration
            if platform == Platform.DOCKER:
                command = "npx directus start"
                working_directory = "/directus"
            else:
                # Native installation
                command = self._get_native_command()
                working_directory = self._working_dir
            
            service_definition = ServiceDefinition(
                name="directus",
                command=command,
                working_directory=working_directory,
                environment=environment,
                dependencies=[],  # Directus has no service dependencies in our setup
                health_check_url=f"http://{self._directus_host}:{self._directus_port}/server/health",
                restart_policy=RestartPolicy.UNLESS_STOPPED,
                user=self._config.get("user"),
                description="Directus Headless CMS - Content Management System"
            )
            
            self._logger.info(f"Created Directus service definition for {platform.value}")
            return service_definition
            
        except Exception as e:
            self._logger.error(f"Failed to create Directus service definition: {e}")
            raise
    
    def _get_native_command(self) -> str:
        """Get native command for running Directus outside Docker."""
        # Check for different Directus installation methods
        possible_commands = [
            "npx directus start",
            "node_modules/.bin/directus start",
            "directus start",
            "npm run start"
        ]
        
        for cmd in possible_commands:
            # In a real implementation, we'd check if the command exists
            # For now, default to npx
            return "npx directus start"
        
        return "npx directus start"
    
    def register_with_registry(self, registry: ServiceRegistry, platform: Platform) -> bool:
        """
        Register Directus service with the ServiceRegistry.
        
        Args:
            registry: ServiceRegistry instance
            platform: Target platform
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            service_definition = self.create_service_definition(platform)
            
            # Additional metadata for Directus
            metadata = {
                "service_type": "cms",
                "category": "content_management",
                "port": self._directus_port,
                "health_endpoint": "/server/health",
                "admin_endpoint": "/admin",
                "api_endpoint": "/items",
                "documentation": "https://docs.directus.io/",
                "version": self._get_directus_version()
            }
            
            success = registry.register_service(
                service=service_definition,
                platform=platform.value,
                metadata=metadata
            )
            
            if success:
                # Update metrics
                if hasattr(self, '_directus_registrations'):
                    self._directus_registrations.labels(platform=platform.value).inc()
                
                self._logger.info(f"Successfully registered Directus service for {platform.value}")
            else:
                self._logger.error(f"Failed to register Directus service for {platform.value}")
            
            return success
            
        except Exception as e:
            self._logger.error(f"Failed to register Directus service: {e}")
            return False
    
    def _get_directus_version(self) -> str:
        """Get Directus version if available."""
        try:
            import subprocess
            result = subprocess.run(
                ["npx", "directus", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        
        return "unknown"
    
    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate Directus configuration requirements.
        
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
            # Check required environment variables
            required_env_vars = ["DIRECTUS_KEY", "DIRECTUS_SECRET"]
            for var in required_env_vars:
                if not os.getenv(var):
                    validation_results["errors"].append(f"Missing required environment variable: {var}")
                    validation_results["valid"] = False
                validation_results["checks"][f"env_{var}"] = bool(os.getenv(var))
            
            # Check working directory
            working_dir = Path(self._working_dir)
            if not working_dir.exists():
                validation_results["warnings"].append(f"Working directory does not exist: {working_dir}")
            validation_results["checks"]["working_dir_exists"] = working_dir.exists()
            
            # Check port availability
            port_available = self._check_port_available(self._directus_port)
            if not port_available:
                validation_results["warnings"].append(f"Port {self._directus_port} may not be available")
            validation_results["checks"]["port_available"] = port_available
            
            # Check database configuration
            db_client = os.getenv("DIRECTUS_DB_CLIENT", "sqlite3")
            if db_client == "pg":
                # PostgreSQL specific checks
                pg_vars = ["DIRECTUS_DB_HOST", "DIRECTUS_DB_DATABASE", "DIRECTUS_DB_USER"]
                for var in pg_vars:
                    if not os.getenv(var):
                        validation_results["errors"].append(f"Missing PostgreSQL config: {var}")
                        validation_results["valid"] = False
                    validation_results["checks"][f"pg_{var}"] = bool(os.getenv(var))
            
            validation_results["checks"]["db_client"] = db_client
            
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
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for Directus service configuration."""
        validation = self.validate_configuration()
        
        return {
            "status": "healthy" if validation["valid"] else "degraded",
            "configuration_valid": validation["valid"],
            "port": self._directus_port,
            "host": self._directus_host,
            "working_dir": self._working_dir,
            "validation_errors": len(validation["errors"]),
            "validation_warnings": len(validation["warnings"])
        }