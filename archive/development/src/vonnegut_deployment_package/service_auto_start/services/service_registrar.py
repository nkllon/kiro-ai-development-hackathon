#!/usr/bin/env python3
"""
ServiceRegistrar - Centralized Service Registration and Makefile Generation

Coordinates registration of all services and generates Makefile targets for
service management operations across all platforms.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from ..registry.service_registry import ServiceRegistry
from ..types.enums import Platform
from .directus_service import DirectusServiceConfig
from .observatory_service import ObservatoryServiceConfig
from .monitoring_service import MonitoringServiceConfig


class ServiceRegistrar(ReflectiveModule):
    """
    Centralized service registration and Makefile generation.
    
    Coordinates registration of all services (Directus, Observatory, Monitoring)
    and generates comprehensive Makefile targets for service management.
    """
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get ServiceRegistrar capabilities."""
        return {
            "service_registration": True,
            "makefile_generation": True,
            "multi_platform_support": True,
            "dependency_resolution": True
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "name": "ServiceRegistrar",
            "version": "1.0.0",
            "description": "Centralized service registration and Makefile generation",
            "author": "Beast Mode Framework"
        }
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation on errors."""
        self._logger.error(f"ServiceRegistrar degradation: {error}")
        return {
            "status": "degraded",
            "error": str(error),
            "fallback_mode": "manual_configuration"
        }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize ServiceRegistrar."""
        super().__init__()
        self._config = config or {}
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize service registry
        self._registry = ServiceRegistry()
        
        # Initialize service configurations
        self._directus_config = DirectusServiceConfig(self._config.get("directus", {}))
        self._observatory_config = ObservatoryServiceConfig(self._config.get("observatory", {}))
        self._monitoring_config = MonitoringServiceConfig(self._config.get("monitoring", {}))
        
        # Makefile configuration
        self._makefile_path = Path(self._config.get("makefile_path", "Makefile.services"))
        
        # Register metrics
        self._register_metrics()
        
        self._logger.info("ServiceRegistrar initialized")
    
    def _register_metrics(self):
        """Register Prometheus metrics."""
        try:
            from prometheus_client import Counter, Gauge, Histogram
            
            self._services_registered_total = Counter(
                'service_registrar_registered_total',
                'Total services registered',
                ['service_name', 'platform']
            )
            
            self._makefile_generations = Counter(
                'service_registrar_makefile_generations_total',
                'Total Makefile generations'
            )
            
            self._registration_time = Histogram(
                'service_registrar_registration_seconds',
                'Time spent registering services'
            )
            
        except ImportError:
            self._logger.warning("Prometheus client not available, metrics disabled")
    
    def register_all_services(self, platform: Platform) -> Dict[str, bool]:
        """
        Register all services for the specified platform.
        
        Args:
            platform: Target platform for registration
            
        Returns:
            Dictionary of service registration results
        """
        start_time = self._get_current_time()
        results = {}
        
        try:
            self._logger.info(f"Registering all services for platform: {platform.value}")
            
            # Register Directus
            results["directus"] = self._directus_config.register_with_registry(
                self._registry, platform
            )
            
            # Register Observatory
            results["observatory"] = self._observatory_config.register_with_registry(
                self._registry, platform
            )
            
            # Register Monitoring (depends on other services)
            results["monitoring"] = self._monitoring_config.register_with_registry(
                self._registry, platform
            )
            
            # Update metrics
            for service_name, success in results.items():
                if success and hasattr(self, '_services_registered_total'):
                    self._services_registered_total.labels(
                        service_name=service_name,
                        platform=platform.value
                    ).inc()
            
            if hasattr(self, '_registration_time'):
                duration = self._get_current_time() - start_time
                self._registration_time.observe(duration)
            
            successful_registrations = sum(1 for success in results.values() if success)
            self._logger.info(f"Registered {successful_registrations}/{len(results)} services successfully")
            
            return results
            
        except Exception as e:
            self._logger.error(f"Failed to register services: {e}")
            return {service: False for service in ["directus", "observatory", "monitoring"]}
    
    def generate_makefile_targets(self, platforms: Optional[List[Platform]] = None) -> bool:
        """
        Generate Makefile targets for all registered services.
        
        Args:
            platforms: List of platforms to generate targets for (None for all)
            
        Returns:
            True if generation successful, False otherwise
        """
        try:
            if platforms is None:
                platforms = [Platform.MACOS, Platform.LINUX, Platform.DOCKER]
            
            self._logger.info(f"Generating Makefile targets for platforms: {[p.value for p in platforms]}")
            
            makefile_content = self._generate_makefile_header()
            
            # Generate platform-specific targets
            for platform in platforms:
                makefile_content += self._generate_platform_targets(platform)
            
            # Generate service-specific targets
            makefile_content += self._generate_service_targets()
            
            # Generate utility targets
            makefile_content += self._generate_utility_targets()
            
            # Write Makefile
            with open(self._makefile_path, 'w') as f:
                f.write(makefile_content)
            
            # Update metrics
            if hasattr(self, '_makefile_generations'):
                self._makefile_generations.inc()
            
            self._logger.info(f"Generated Makefile targets: {self._makefile_path}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to generate Makefile targets: {e}")
            return False
    
    def _generate_makefile_header(self) -> str:
        """Generate Makefile header with metadata."""
        return f"""# Service Auto-Start Governance Makefile
# Generated by ServiceRegistrar on {datetime.now().isoformat()}
# 
# This Makefile provides targets for managing service auto-start configuration
# across multiple platforms (macOS, Linux, Docker).

.PHONY: help install-all verify-all remove-all status-all
.DEFAULT_GOAL := help

# Platform detection
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
    PLATFORM := macos
endif
ifeq ($(UNAME_S),Linux)
    PLATFORM := linux
endif

# Service configuration
DIRECTUS_PORT := 8055
OBSERVATORY_PORT := 8888
PROMETHEUS_PORT := 9090
GRAFANA_PORT := 3000

"""
    
    def _generate_platform_targets(self, platform: Platform) -> str:
        """Generate platform-specific targets."""
        platform_name = platform.value
        
        return f"""
# {platform_name.upper()} Platform Targets
install-{platform_name}: install-directus-{platform_name} install-observatory-{platform_name} install-monitoring-{platform_name}
\t@echo "✅ All services installed for {platform_name}"

verify-{platform_name}: verify-directus-{platform_name} verify-observatory-{platform_name} verify-monitoring-{platform_name}
\t@echo "✅ All services verified for {platform_name}"

remove-{platform_name}: remove-directus-{platform_name} remove-observatory-{platform_name} remove-monitoring-{platform_name}
\t@echo "✅ All services removed for {platform_name}"

status-{platform_name}: status-directus-{platform_name} status-observatory-{platform_name} status-monitoring-{platform_name}
\t@echo "📊 Status check complete for {platform_name}"

"""
    
    def _generate_service_targets(self) -> str:
        """Generate service-specific targets."""
        services = ["directus", "observatory", "monitoring"]
        platforms = ["macos", "linux", "docker"]
        
        content = ""
        
        for service in services:
            content += f"\n# {service.upper()} Service Targets\n"
            
            for platform in platforms:
                content += f"""
install-{service}-{platform}:
\t@echo "🚀 Installing {service} for {platform}..."
\t@python -c "from src.service_auto_start.cli import install_service; install_service('{service}', '{platform}')"

verify-{service}-{platform}:
\t@echo "🔍 Verifying {service} for {platform}..."
\t@python -c "from src.service_auto_start.cli import verify_service; verify_service('{service}', '{platform}')"

remove-{service}-{platform}:
\t@echo "🗑️  Removing {service} for {platform}..."
\t@python -c "from src.service_auto_start.cli import remove_service; remove_service('{service}', '{platform}')"

status-{service}-{platform}:
\t@echo "📊 Checking {service} status for {platform}..."
\t@python -c "from src.service_auto_start.cli import service_status; service_status('{service}', '{platform}')"
"""
            
            # Generic service targets (platform-agnostic)
            content += f"""
install-{service}: install-{service}-$(PLATFORM)
verify-{service}: verify-{service}-$(PLATFORM)
remove-{service}: remove-{service}-$(PLATFORM)
status-{service}: status-{service}-$(PLATFORM)

"""
        
        return content
    
    def _generate_utility_targets(self) -> str:
        """Generate utility and management targets."""
        return """
# Utility Targets
help:
\t@echo "Service Auto-Start Governance Makefile"
\t@echo ""
\t@echo "Platform-specific targets:"
\t@echo "  install-macos     Install all services for macOS"
\t@echo "  install-linux     Install all services for Linux"
\t@echo "  install-docker    Install all services for Docker"
\t@echo ""
\t@echo "Service-specific targets:"
\t@echo "  install-directus     Install Directus CMS"
\t@echo "  install-observatory  Install Observatory WebSocket system"
\t@echo "  install-monitoring   Install monitoring stack"
\t@echo ""
\t@echo "Management targets:"
\t@echo "  verify-all        Verify all services"
\t@echo "  status-all        Check status of all services"
\t@echo "  remove-all        Remove all service configurations"
\t@echo "  health-check      Run comprehensive health check"
\t@echo ""
\t@echo "Current platform: $(PLATFORM)"

install-all: install-$(PLATFORM)
verify-all: verify-$(PLATFORM)
remove-all: remove-$(PLATFORM)
status-all: status-$(PLATFORM)

health-check:
\t@echo "🏥 Running comprehensive health check..."
\t@python -c "from src.service_auto_start.cli import health_check; health_check()"

list-services:
\t@echo "📋 Listing registered services..."
\t@python -c "from src.service_auto_start.cli import list_services; list_services()"

validate-config:
\t@echo "✅ Validating service configurations..."
\t@python -c "from src.service_auto_start.cli import validate_config; validate_config()"

startup-order:
\t@echo "🔄 Calculating service startup order..."
\t@python -c "from src.service_auto_start.cli import show_startup_order; show_startup_order()"

# Development targets
test-services:
\t@echo "🧪 Running service tests..."
\t@pytest tests/unit/service_auto_start/ -v

lint-services:
\t@echo "🔍 Linting service code..."
\t@flake8 src/service_auto_start/

# Emergency targets
emergency-stop:
\t@echo "🚨 Emergency stop all services..."
\t@python -c "from src.service_auto_start.cli import emergency_stop; emergency_stop()"

emergency-restart:
\t@echo "🔄 Emergency restart all services..."
\t@python -c "from src.service_auto_start.cli import emergency_restart; emergency_restart()"

# Monitoring targets
dashboard:
\t@echo "📊 Opening monitoring dashboard..."
\t@open http://localhost:$(GRAFANA_PORT) || xdg-open http://localhost:$(GRAFANA_PORT)

prometheus:
\t@echo "📈 Opening Prometheus..."
\t@open http://localhost:$(PROMETHEUS_PORT) || xdg-open http://localhost:$(PROMETHEUS_PORT)

directus-admin:
\t@echo "🎛️  Opening Directus admin..."
\t@open http://localhost:$(DIRECTUS_PORT)/admin || xdg-open http://localhost:$(DIRECTUS_PORT)/admin

observatory-ws:
\t@echo "🔭 Opening Observatory WebSocket..."
\t@open http://localhost:$(OBSERVATORY_PORT) || xdg-open http://localhost:$(OBSERVATORY_PORT)

"""
    
    def get_registry(self) -> ServiceRegistry:
        """Get the service registry instance."""
        return self._registry
    
    def get_startup_order(self, platform: Platform) -> List[str]:
        """Get service startup order for platform."""
        return self._registry.get_startup_order(platform.value)
    
    def validate_all_configurations(self) -> Dict[str, Dict[str, Any]]:
        """Validate all service configurations."""
        return {
            "directus": self._directus_config.validate_configuration(),
            "observatory": self._observatory_config.validate_configuration(),
            "monitoring": self._monitoring_config.validate_configuration()
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for ServiceRegistrar."""
        registry_status = self._registry.get_health_status()
        
        return {
            "status": "healthy",
            "registry": registry_status,
            "makefile_path": str(self._makefile_path),
            "makefile_exists": self._makefile_path.exists(),
            "services_configured": ["directus", "observatory", "monitoring"]
        }
    
    def _get_current_time(self) -> float:
        """Get current time for metrics."""
        import time
        return time.time()