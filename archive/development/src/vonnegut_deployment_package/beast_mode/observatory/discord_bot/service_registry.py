"""
Service Registry for Discord Bot Integration

Provides service discovery and management for Observatory integration.
Built with extraction-ready architecture for standalone framework.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .models import ServiceHealth
from .interfaces import (
    ServiceInterface, ObservatoryServiceRegistry, FrameworkServiceRegistry
)
from .exceptions import ServiceUnavailableError

logger = logging.getLogger(__name__)


class ServiceRegistry(FrameworkServiceRegistry):
    """Generic service registry for standalone framework"""
    
    def __init__(self):
        self._services: Dict[str, ServiceInterface] = {}
        self._health_cache: Dict[str, tuple[ServiceHealth, datetime]] = {}
        self._cache_ttl_seconds = 30
    
    async def register(self, name: str, service: ServiceInterface) -> None:
        """Register a service"""
        try:
            # Initialize the service
            if await service.initialize():
                self._services[name] = service
                logger.info(f"Registered service: {name}")
            else:
                logger.error(f"Failed to initialize service: {name}")
        except Exception as e:
            logger.error(f"Error registering service {name}: {e}")
    
    async def get(self, name: str) -> Optional[ServiceInterface]:
        """Get service by name"""
        return self._services.get(name)
    
    async def remove(self, name: str) -> bool:
        """Remove service"""
        if name in self._services:
            try:
                await self._services[name].cleanup()
                del self._services[name]
                if name in self._health_cache:
                    del self._health_cache[name]
                logger.info(f"Removed service: {name}")
                return True
            except Exception as e:
                logger.error(f"Error removing service {name}: {e}")
        return False
    
    async def list_services(self) -> List[str]:
        """List all registered services"""
        return list(self._services.keys())
    
    async def health_check_all(self) -> Dict[str, ServiceHealth]:
        """Health check all services with caching"""
        results = {}
        now = datetime.utcnow()
        
        for name, service in self._services.items():
            # Check cache first
            if name in self._health_cache:
                health, timestamp = self._health_cache[name]
                if (now - timestamp).total_seconds() < self._cache_ttl_seconds:
                    results[name] = health
                    continue
            
            # Perform health check
            try:
                health = await service.get_health()
                self._health_cache[name] = (health, now)
                results[name] = health
            except Exception as e:
                logger.error(f"Health check failed for service {name}: {e}")
                results[name] = ServiceHealth.UNHEALTHY
                self._health_cache[name] = (ServiceHealth.UNHEALTHY, now)
        
        return results
    
    async def is_service_available(self, name: str) -> bool:
        """Check if service is available and healthy"""
        if name not in self._services:
            return False
        
        try:
            health = await self._services[name].get_health()
            return health in [ServiceHealth.HEALTHY, ServiceHealth.DEGRADED]
        except Exception:
            return False


class ObservatoryServiceRegistryImpl(ObservatoryServiceRegistry):
    """Observatory-specific service registry implementation"""
    
    def __init__(self):
        self._base_registry = ServiceRegistry()
        self._observatory_services = {}
    
    async def get_service(self, service_name: str) -> Optional[ServiceInterface]:
        """Get service by name"""
        return await self._base_registry.get(service_name)
    
    async def register_service(self, name: str, service: ServiceInterface) -> None:
        """Register a service"""
        await self._base_registry.register(name, service)
        self._observatory_services[name] = service
    
    async def is_service_available(self, service_name: str) -> bool:
        """Check if service is available"""
        return await self._base_registry.is_service_available(service_name)
    
    async def get_available_services(self) -> List[str]:
        """Get list of available services"""
        return await self._base_registry.list_services()
    
    async def health_check_all(self) -> Dict[str, ServiceHealth]:
        """Health check all registered services"""
        return await self._base_registry.health_check_all()


class ServiceDiscovery:
    """Service discovery helper for Observatory integration"""
    
    def __init__(self, registry: ObservatoryServiceRegistry):
        self.registry = registry
    
    async def discover_observatory_services(self) -> Dict[str, bool]:
        """Discover available Observatory services"""
        services_to_check = [
            'ai_consultation',
            'health_monitor',
            'status_service',
            'context_provider',
            'notification_service',
            'audit_service',
            'security_service'
        ]
        
        results = {}
        for service_name in services_to_check:
            try:
                available = await self.registry.is_service_available(service_name)
                results[service_name] = available
                if available:
                    logger.info(f"Discovered Observatory service: {service_name}")
            except Exception as e:
                logger.warning(f"Error checking service {service_name}: {e}")
                results[service_name] = False
        
        return results
    
    async def get_service_capabilities(self, service_name: str) -> Dict[str, Any]:
        """Get capabilities of a specific service"""
        service = await self.registry.get_service(service_name)
        if not service:
            return {}
        
        capabilities = {
            'available': True,
            'health': await service.get_health(),
            'type': type(service).__name__
        }
        
        # Add service-specific capabilities
        if hasattr(service, 'get_capabilities'):
            try:
                service_caps = await service.get_capabilities()
                capabilities.update(service_caps)
            except Exception as e:
                logger.warning(f"Could not get capabilities for {service_name}: {e}")
        
        return capabilities


# Default service implementations for fallback behavior

class DefaultHealthService(ServiceInterface):
    """Default health service when Observatory unavailable"""
    
    async def get_health(self) -> ServiceHealth:
        return ServiceHealth.HEALTHY
    
    async def initialize(self) -> bool:
        return True
    
    async def cleanup(self) -> None:
        pass
    
    async def get_system_health(self) -> Dict[str, Any]:
        return {
            'status': 'healthy',
            'message': 'Discord bot running in standalone mode',
            'services': ['discord_notifications']
        }


class DefaultStatusService(ServiceInterface):
    """Default status service when Observatory unavailable"""
    
    def __init__(self):
        self._start_time = datetime.utcnow()
    
    async def get_health(self) -> ServiceHealth:
        return ServiceHealth.HEALTHY
    
    async def initialize(self) -> bool:
        return True
    
    async def cleanup(self) -> None:
        pass
    
    async def get_bot_status(self) -> str:
        return "online"
    
    async def get_uptime(self) -> float:
        return (datetime.utcnow() - self._start_time).total_seconds()


class DefaultAIService(ServiceInterface):
    """Default AI service when Observatory unavailable"""
    
    async def get_health(self) -> ServiceHealth:
        return ServiceHealth.DEGRADED
    
    async def initialize(self) -> bool:
        return True
    
    async def cleanup(self) -> None:
        pass
    
    async def generate_response(self, query: str, context: Any) -> str:
        return "AI services are currently unavailable. Please try again later."
    
    async def is_available(self) -> bool:
        return False


# Factory functions for creating service registries

def create_observatory_service_registry() -> ObservatoryServiceRegistry:
    """Create Observatory service registry"""
    return ObservatoryServiceRegistryImpl()


def create_standalone_service_registry() -> ServiceRegistry:
    """Create standalone service registry with default services"""
    registry = ServiceRegistry()
    
    # Register default services for standalone operation
    asyncio.create_task(registry.register('health', DefaultHealthService()))
    asyncio.create_task(registry.register('status', DefaultStatusService()))
    asyncio.create_task(registry.register('ai', DefaultAIService()))
    
    return registry