#!/usr/bin/env python3
"""
ServiceAutoStarter Base Class - Foundation for Platform-Specific Auto-Start

Provides the core interface and shared functionality for service auto-start 
management across all platforms (macOS, Linux, Docker, Kubernetes).
"""

import os
import platform
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


@dataclass
class ServiceDefinition:
    """Service definition for auto-start configuration."""
    name: str
    command: str
    working_directory: str
    environment: Dict[str, str] = None
    dependencies: List[str] = None
    health_check_url: Optional[str] = None
    restart_policy: str = "always"
    user: Optional[str] = None
    description: Optional[str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.environment is None:
            self.environment = {}
        if self.dependencies is None:
            self.dependencies = []


class PlatformDetector:
    """Detects current platform and capabilities."""
    
    @staticmethod
    def get_platform() -> str:
        """Detect current platform."""
        system = platform.system().lower()
        if system == "darwin":
            return "macos"
        elif system == "linux":
            # Check if we're in a container
            if os.path.exists("/.dockerenv") or os.path.exists("/proc/1/cgroup"):
                return "docker"
            # Check for systemd
            elif os.path.exists("/bin/systemctl") or os.path.exists("/usr/bin/systemctl"):
                return "linux"
            else:
                return "linux-legacy"
        elif system == "windows":
            return "windows"
        else:
            return "unknown"
    
    @staticmethod
    def has_docker() -> bool:
        """Check if Docker is available."""
        return os.system("docker --version >/dev/null 2>&1") == 0
    
    @staticmethod
    def has_systemd() -> bool:
        """Check if systemd is available."""
        return os.path.exists("/bin/systemctl") or os.path.exists("/usr/bin/systemctl")


class ServiceAutoStarter(ReflectiveModule, ABC):
    """
    Base class for service auto-start management.
    
    Provides platform detection, configuration generation, and service lifecycle
    management with systematic observability and error handling.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize ServiceAutoStarter with configuration."""
        super().__init__()
        self._config = config or {}
        self._platform = PlatformDetector.get_platform()
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Register metrics
        self._register_metrics()
        
        self._logger.info(f"ServiceAutoStarter initialized for platform: {self._platform}")
    
    def _register_metrics(self):
        """Register Prometheus metrics for observability."""
        try:
            from prometheus_client import Counter, Histogram, Gauge
            
            self._services_configured = Counter(
                'service_autostart_configured_total',
                'Total services configured for auto-start',
                ['platform', 'service_name']
            )
            
            self._config_generation_time = Histogram(
                'service_autostart_config_generation_seconds',
                'Time spent generating auto-start configuration',
                ['platform']
            )
            
            self._services_active = Gauge(
                'service_autostart_active_count',
                'Number of services with active auto-start configuration',
                ['platform']
            )
            
        except ImportError:
            self._logger.warning("Prometheus client not available, metrics disabled")
    
    @property
    def platform(self) -> str:
        """Get detected platform."""
        return self._platform
    
    @abstractmethod
    def generate_config(self, service: ServiceDefinition) -> Dict[str, Any]:
        """
        Generate platform-appropriate auto-start configuration.
        
        Args:
            service: Service definition to configure
            
        Returns:
            Platform-specific configuration dictionary
        """
        pass
    
    @abstractmethod
    def install_config(self, service: ServiceDefinition, config: Dict[str, Any]) -> bool:
        """
        Install and activate the auto-start configuration.
        
        Args:
            service: Service definition
            config: Generated configuration
            
        Returns:
            True if installation successful, False otherwise
        """
        pass
    
    @abstractmethod
    def verify_autostart(self, service: ServiceDefinition) -> bool:
        """
        Verify that the service will start automatically on boot.
        
        Args:
            service: Service definition to verify
            
        Returns:
            True if auto-start is properly configured, False otherwise
        """
        pass
    
    @abstractmethod
    def remove_autostart(self, service: ServiceDefinition) -> bool:
        """
        Remove auto-start configuration for a service.
        
        Args:
            service: Service definition to remove
            
        Returns:
            True if removal successful, False otherwise
        """
        pass
    
    def configure_service(self, service: ServiceDefinition) -> bool:
        """
        Complete service auto-start configuration workflow.
        
        Args:
            service: Service definition to configure
            
        Returns:
            True if configuration successful, False otherwise
        """
        try:
            start_time = self._get_current_time()
            
            self._logger.info(f"Configuring auto-start for service: {service.name}")
            
            # Generate platform-specific configuration
            config = self.generate_config(service)
            if not config:
                self._logger.error(f"Failed to generate config for {service.name}")
                return False
            
            # Install configuration
            if not self.install_config(service, config):
                self._logger.error(f"Failed to install config for {service.name}")
                return False
            
            # Verify installation
            if not self.verify_autostart(service):
                self._logger.error(f"Failed to verify auto-start for {service.name}")
                return False
            
            # Update metrics
            if hasattr(self, '_services_configured'):
                self._services_configured.labels(
                    platform=self._platform,
                    service_name=service.name
                ).inc()
            
            if hasattr(self, '_config_generation_time'):
                duration = self._get_current_time() - start_time
                self._config_generation_time.labels(platform=self._platform).observe(duration)
            
            self._logger.info(f"Successfully configured auto-start for {service.name}")
            return True
            
        except Exception as e:
            self._logger.error(f"Error configuring service {service.name}: {e}")
            return False
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for observability."""
        return {
            "status": "healthy",
            "platform": self._platform,
            "capabilities": {
                "docker": PlatformDetector.has_docker(),
                "systemd": PlatformDetector.has_systemd()
            }
        }
    
    def _get_current_time(self) -> float:
        """Get current time for metrics."""
        import time
        return time.time()


class ServiceAutoStarterFactory:
    """Factory for creating platform-specific ServiceAutoStarter instances."""
    
    @staticmethod
    def create(platform: Optional[str] = None) -> ServiceAutoStarter:
        """
        Create appropriate ServiceAutoStarter for the platform.
        
        Args:
            platform: Override platform detection
            
        Returns:
            Platform-specific ServiceAutoStarter instance
        """
        target_platform = platform or PlatformDetector.get_platform()
        
        if target_platform == "macos":
            from ..platforms.macos_adapter import MacOSLaunchAgentAdapter
            return MacOSLaunchAgentAdapter()
        elif target_platform == "linux":
            from ..platforms.linux_adapter import LinuxSystemdAdapter
            return LinuxSystemdAdapter()
        elif target_platform == "docker":
            from ..platforms.docker_adapter import DockerComposeAdapter
            return DockerComposeAdapter()
        else:
            raise ValueError(f"Unsupported platform: {target_platform}")