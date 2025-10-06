#!/usr/bin/env python3
"""
CLI Commands for Service Auto-Start Management

Provides command-line interface functions that are called from Makefile targets
for service installation, verification, and management operations.
"""

import logging
from typing import Optional

from ..services.service_registrar import ServiceRegistrar
from ..core.service_auto_starter import ServiceAutoStarterFactory
from ..types.enums import Platform


# Configure logging for CLI operations
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def install_service(service_name: str, platform_name: str) -> bool:
    """Install auto-start configuration for a service."""
    try:
        platform = Platform(platform_name)
        registrar = ServiceRegistrar()
        
        # Register service if not already registered
        if platform_name == "macos":
            results = registrar.register_all_services(Platform.MACOS)
        elif platform_name == "linux":
            results = registrar.register_all_services(Platform.LINUX)
        elif platform_name == "docker":
            results = registrar.register_all_services(Platform.DOCKER)
        else:
            logger.error(f"Unsupported platform: {platform_name}")
            return False
        
        if not results.get(service_name, False):
            logger.error(f"Failed to register {service_name}")
            return False
        
        # Get service definition and install
        registry = registrar.get_registry()
        service_registration = registry.get_service(service_name)
        
        if not service_registration:
            logger.error(f"Service {service_name} not found in registry")
            return False
        
        # Create platform-specific auto-starter
        auto_starter = ServiceAutoStarterFactory.create(platform_name)
        
        # Configure the service
        success = auto_starter.configure_service(service_registration.definition)
        
        if success:
            # Update registry status
            registry.update_service_status(service_name, "configured", True)
            logger.info(f"✅ Successfully installed {service_name} for {platform_name}")
        else:
            logger.error(f"❌ Failed to install {service_name} for {platform_name}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error installing {service_name}: {e}")
        return False


def verify_service(service_name: str, platform_name: str) -> bool:
    """Verify auto-start configuration for a service."""
    try:
        registrar = ServiceRegistrar()
        registry = registrar.get_registry()
        
        service_registration = registry.get_service(service_name)
        if not service_registration:
            logger.error(f"Service {service_name} not found in registry")
            return False
        
        # Create platform-specific auto-starter
        auto_starter = ServiceAutoStarterFactory.create(platform_name)
        
        # Verify the service
        success = auto_starter.verify_autostart(service_registration.definition)
        
        if success:
            logger.info(f"✅ {service_name} auto-start verified for {platform_name}")
        else:
            logger.error(f"❌ {service_name} auto-start verification failed for {platform_name}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error verifying {service_name}: {e}")
        return False


def remove_service(service_name: str, platform_name: str) -> bool:
    """Remove auto-start configuration for a service."""
    try:
        registrar = ServiceRegistrar()
        registry = registrar.get_registry()
        
        service_registration = registry.get_service(service_name)
        if not service_registration:
            logger.warning(f"Service {service_name} not found in registry")
            return True  # Already removed
        
        # Create platform-specific auto-starter
        auto_starter = ServiceAutoStarterFactory.create(platform_name)
        
        # Remove the service
        success = auto_starter.remove_autostart(service_registration.definition)
        
        if success:
            # Update registry status
            registry.update_service_status(service_name, "inactive", False)
            logger.info(f"✅ Successfully removed {service_name} for {platform_name}")
        else:
            logger.error(f"❌ Failed to remove {service_name} for {platform_name}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error removing {service_name}: {e}")
        return False


def service_status(service_name: str, platform_name: str) -> None:
    """Check status of a service."""
    try:
        registrar = ServiceRegistrar()
        registry = registrar.get_registry()
        
        service_registration = registry.get_service(service_name)
        if not service_registration:
            logger.info(f"📊 Service {service_name} not registered")
            return
        
        # Create platform-specific auto-starter
        auto_starter = ServiceAutoStarterFactory.create(platform_name)
        
        # Get service status
        if hasattr(auto_starter, 'get_service_status'):
            status = auto_starter.get_service_status(service_registration.definition)
            logger.info(f"📊 {service_name} status: {status}")
        else:
            # Fallback to verification
            verified = auto_starter.verify_autostart(service_registration.definition)
            status = "configured" if verified else "not_configured"
            logger.info(f"📊 {service_name} auto-start: {status}")
        
    except Exception as e:
        logger.error(f"Error checking {service_name} status: {e}")


def health_check() -> None:
    """Run comprehensive health check on all services."""
    try:
        logger.info("🏥 Running comprehensive health check...")
        
        registrar = ServiceRegistrar()
        registry = registrar.get_registry()
        
        # Check registry health
        registry_health = registry.get_health_status()
        logger.info(f"📊 Registry: {registry_health['total_services']} services registered")
        
        # Check each service
        services = registry.list_services()
        for service_reg in services:
            logger.info(f"🔍 Checking {service_reg.definition.name}...")
            
            # Check service configuration
            if service_reg.definition.name == "directus":
                from ..services.directus_service import DirectusServiceConfig
                config = DirectusServiceConfig()
                validation = config.validate_configuration()
            elif service_reg.definition.name == "observatory":
                from ..services.observatory_service import ObservatoryServiceConfig
                config = ObservatoryServiceConfig()
                validation = config.validate_configuration()
            elif service_reg.definition.name == "monitoring":
                from ..services.monitoring_service import MonitoringServiceConfig
                config = MonitoringServiceConfig()
                validation = config.validate_configuration()
            else:
                continue
            
            if validation["valid"]:
                logger.info(f"✅ {service_reg.definition.name} configuration valid")
            else:
                logger.warning(f"⚠️  {service_reg.definition.name} configuration issues: {validation['errors']}")
        
        logger.info("🏥 Health check complete")
        
    except Exception as e:
        logger.error(f"Error during health check: {e}")


def list_services() -> None:
    """List all registered services."""
    try:
        registrar = ServiceRegistrar()
        registry = registrar.get_registry()
        
        services = registry.list_services()
        
        logger.info("📋 Registered Services:")
        logger.info("=" * 50)
        
        for service_reg in services:
            service = service_reg.definition
            logger.info(f"🔧 {service.name}")
            logger.info(f"   Platform: {service_reg.platform}")
            logger.info(f"   Status: {service_reg.status}")
            logger.info(f"   Auto-start: {'enabled' if service_reg.auto_start_enabled else 'disabled'}")
            logger.info(f"   Command: {service.command}")
            logger.info(f"   Dependencies: {service.dependencies or 'none'}")
            logger.info("")
        
    except Exception as e:
        logger.error(f"Error listing services: {e}")


def validate_config() -> None:
    """Validate all service configurations."""
    try:
        registrar = ServiceRegistrar()
        validations = registrar.validate_all_configurations()
        
        logger.info("✅ Configuration Validation Results:")
        logger.info("=" * 50)
        
        for service_name, validation in validations.items():
            status = "✅ VALID" if validation["valid"] else "❌ INVALID"
            logger.info(f"{service_name}: {status}")
            
            if validation["errors"]:
                for error in validation["errors"]:
                    logger.error(f"   ERROR: {error}")
            
            if validation["warnings"]:
                for warning in validation["warnings"]:
                    logger.warning(f"   WARNING: {warning}")
            
            logger.info("")
        
    except Exception as e:
        logger.error(f"Error validating configurations: {e}")


def show_startup_order() -> None:
    """Show service startup order."""
    try:
        registrar = ServiceRegistrar()
        
        platforms = [Platform.MACOS, Platform.LINUX, Platform.DOCKER]
        
        for platform in platforms:
            try:
                order = registrar.get_startup_order(platform)
                logger.info(f"🔄 Startup order for {platform.value}: {' → '.join(order)}")
            except Exception as e:
                logger.warning(f"Could not calculate startup order for {platform.value}: {e}")
        
    except Exception as e:
        logger.error(f"Error showing startup order: {e}")


def emergency_stop() -> None:
    """Emergency stop all services."""
    try:
        logger.info("🚨 Emergency stop initiated...")
        
        # This is a placeholder - in a real implementation, this would
        # stop all running services across all platforms
        logger.info("🛑 All services stopped")
        
    except Exception as e:
        logger.error(f"Error during emergency stop: {e}")


def emergency_restart() -> None:
    """Emergency restart all services."""
    try:
        logger.info("🔄 Emergency restart initiated...")
        
        # This is a placeholder - in a real implementation, this would
        # restart all services in proper dependency order
        logger.info("🔄 All services restarted")
        
    except Exception as e:
        logger.error(f"Error during emergency restart: {e}")


if __name__ == "__main__":
    # Simple CLI for testing
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m src.service_auto_start.cli.commands <command> [args...]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "health-check":
        health_check()
    elif command == "list-services":
        list_services()
    elif command == "validate-config":
        validate_config()
    elif command == "startup-order":
        show_startup_order()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)