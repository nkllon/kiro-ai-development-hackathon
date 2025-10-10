"""
Observatory Integration for Discord Bot

Connects Discord bot to Observatory services using the service abstraction layer.
This module handles the Observatory-specific integration while keeping the Discord
bot core framework-agnostic for easy extraction.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .interfaces import (
    ObservatoryServiceRegistry, HealthServiceInterface, StatusServiceInterface,
    AIResponseServiceInterface, ContextServiceInterface, NotificationServiceInterface
)
from .models import ServiceHealth, CommandContext, BotHealthStatus, NotificationMessage
from .exceptions import ServiceUnavailableError

logger = logging.getLogger(__name__)


class ObservatoryHealthService(HealthServiceInterface):
    """Health service that integrates with Observatory health monitoring"""
    
    def __init__(self):
        self._observatory_health = None
        self._last_check = None
        self._cache_ttl_seconds = 30
    
    async def get_health(self) -> ServiceHealth:
        """Get health of this service"""
        try:
            # Try to get Observatory health status
            if await self._check_observatory_connection():
                return ServiceHealth.HEALTHY
            else:
                return ServiceHealth.DEGRADED
        except Exception:
            return ServiceHealth.UNHEALTHY
    
    async def initialize(self) -> bool:
        """Initialize Observatory health integration"""
        try:
            # Try to import and connect to Observatory health system
            from ..ai_consultation.health_checker import HealthChecker
            self._observatory_health = HealthChecker()
            logger.info("Observatory health service integration initialized")
            return True
        except ImportError:
            logger.warning("Observatory health checker not available")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Observatory health integration: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up Observatory health integration"""
        self._observatory_health = None
    
    async def get_system_health(self) -> BotHealthStatus:
        """Get overall system health including Observatory services"""
        # This would integrate with Observatory's health monitoring
        # For now, return basic health status
        return BotHealthStatus(
            status="online",
            uptime_seconds=0.0,  # Would get from Observatory
            total_commands=0,
            successful_commands=0,
            failed_commands=0
        )
    
    async def get_service_health(self, service_name: str) -> ServiceHealth:
        """Get health of specific Observatory service"""
        if not self._observatory_health:
            return ServiceHealth.UNKNOWN
        
        try:
            # This would check specific Observatory service health
            return ServiceHealth.HEALTHY  # Simplified for now
        except Exception:
            return ServiceHealth.UNHEALTHY
    
    async def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary for display"""
        return {
            "observatory_connected": self._observatory_health is not None,
            "last_check": self._last_check.isoformat() if self._last_check else None,
            "services": ["discord_bot", "observatory_integration"]
        }
    
    async def _check_observatory_connection(self) -> bool:
        """Check if Observatory services are available"""
        now = datetime.utcnow()
        
        # Use cached result if recent
        if (self._last_check and 
            (now - self._last_check).total_seconds() < self._cache_ttl_seconds):
            return self._observatory_health is not None
        
        try:
            # Try to access Observatory health system
            if self._observatory_health:
                # This would do an actual health check
                self._last_check = now
                return True
        except Exception:
            pass
        
        self._last_check = now
        return False


class ObservatoryStatusService(StatusServiceInterface):
    """Status service that integrates with Observatory monitoring"""
    
    def __init__(self):
        self._start_time = datetime.utcnow()
        self._observatory_context = None
    
    async def get_health(self) -> ServiceHealth:
        return ServiceHealth.HEALTHY
    
    async def initialize(self) -> bool:
        """Initialize Observatory status integration"""
        try:
            # Try to connect to Observatory context provider
            from ..ai_consultation.observatory_context_provider import observatory_context_provider
            self._observatory_context = observatory_context_provider
            logger.info("Observatory status service integration initialized")
            return True
        except ImportError:
            logger.warning("Observatory context provider not available")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Observatory status integration: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up Observatory status integration"""
        self._observatory_context = None
    
    async def get_bot_status(self) -> str:
        """Get current bot status"""
        return "online"
    
    async def get_uptime(self) -> float:
        """Get bot uptime in seconds"""
        return (datetime.utcnow() - self._start_time).total_seconds()
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics from Observatory"""
        if not self._observatory_context:
            return {"source": "standalone", "metrics": {}}
        
        try:
            # This would get actual Observatory metrics
            return {
                "source": "observatory",
                "metrics": {
                    "response_time_ms": 0.0,
                    "memory_usage_mb": 0.0,
                    "cpu_usage_percent": 0.0
                }
            }
        except Exception as e:
            logger.error(f"Failed to get Observatory performance metrics: {e}")
            return {"source": "error", "error": str(e)}
    
    async def get_usage_statistics(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            "commands_executed": 0,
            "messages_processed": 0,
            "uptime_seconds": await self.get_uptime()
        }


class ObservatoryAIService(AIResponseServiceInterface):
    """AI service that integrates with Observatory AI consultation system"""
    
    def __init__(self):
        self._ai_service = None
        self._consultation_router = None
    
    async def get_health(self) -> ServiceHealth:
        """Get AI service health"""
        if not self._ai_service:
            return ServiceHealth.UNHEALTHY
        
        try:
            # Check if AI consultation system is available
            if await self.is_available():
                return ServiceHealth.HEALTHY
            else:
                return ServiceHealth.DEGRADED
        except Exception:
            return ServiceHealth.UNHEALTHY
    
    async def initialize(self) -> bool:
        """Initialize Observatory AI integration"""
        try:
            # Try to connect to Observatory AI consultation system
            from ..ai_consultation.consultation_router import get_consultation_router
            from ..ai_consultation.llm_service import get_llm_service
            
            self._consultation_router = get_consultation_router()
            self._ai_service = get_llm_service()
            
            logger.info("Observatory AI service integration initialized")
            return True
        except ImportError:
            logger.warning("Observatory AI consultation system not available")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Observatory AI integration: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up Observatory AI integration"""
        self._ai_service = None
        self._consultation_router = None
    
    async def generate_response(
        self, 
        query: str, 
        context: CommandContext,
        max_tokens: int = 150
    ) -> str:
        """Generate AI response using Observatory AI consultation system"""
        if not self._consultation_router or not self._ai_service:
            return "AI services are currently unavailable. Please try again later."
        
        try:
            # This would use the actual Observatory AI consultation system
            # For now, return a placeholder response
            return f"Observatory AI response to: {query[:50]}..."
            
        except Exception as e:
            logger.error(f"Failed to generate AI response: {e}")
            return "Sorry, I encountered an error generating a response. Please try again later."
    
    async def is_available(self) -> bool:
        """Check if AI service is available"""
        return self._ai_service is not None and self._consultation_router is not None
    
    async def get_cost_estimate(self, query: str) -> float:
        """Get cost estimate for query"""
        if not self._ai_service:
            return 0.0
        
        try:
            # This would calculate actual cost using Observatory cost tracking
            return 0.001  # Placeholder cost
        except Exception:
            return 0.0


class ObservatoryContextService(ContextServiceInterface):
    """Context service that provides Observatory system context"""
    
    def __init__(self):
        self._context_provider = None
    
    async def get_health(self) -> ServiceHealth:
        return ServiceHealth.HEALTHY if self._context_provider else ServiceHealth.UNHEALTHY
    
    async def initialize(self) -> bool:
        """Initialize Observatory context integration"""
        try:
            from ..ai_consultation.observatory_context_provider import observatory_context_provider
            self._context_provider = observatory_context_provider
            logger.info("Observatory context service integration initialized")
            return True
        except ImportError:
            logger.warning("Observatory context provider not available")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Observatory context integration: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up Observatory context integration"""
        self._context_provider = None
    
    async def get_system_context(self) -> Dict[str, Any]:
        """Get system context for AI responses"""
        if not self._context_provider:
            return {"source": "standalone", "context": {}}
        
        try:
            # This would get actual Observatory context
            return {
                "source": "observatory",
                "context": {
                    "system_status": "operational",
                    "active_services": [],
                    "recent_metrics": {}
                }
            }
        except Exception as e:
            logger.error(f"Failed to get Observatory context: {e}")
            return {"source": "error", "error": str(e)}
    
    async def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        if not self._context_provider:
            return {}
        
        try:
            # This would get actual Observatory metrics
            return {
                "total_metrics": 0,
                "active_alerts": 0,
                "system_health": "healthy"
            }
        except Exception:
            return {}
    
    async def get_recent_alerts(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent system alerts"""
        if not self._context_provider:
            return []
        
        try:
            # This would get actual Observatory alerts
            return []
        except Exception:
            return []


class ObservatoryNotificationService(NotificationServiceInterface):
    """Notification service that integrates with Observatory notification system"""
    
    def __init__(self):
        self._notification_integration = None
    
    async def get_health(self) -> ServiceHealth:
        return ServiceHealth.HEALTHY if self._notification_integration else ServiceHealth.DEGRADED
    
    async def initialize(self) -> bool:
        """Initialize Observatory notification integration"""
        try:
            from ..ai_consultation.notification_integration import NotificationIntegration
            self._notification_integration = NotificationIntegration()
            logger.info("Observatory notification service integration initialized")
            return True
        except ImportError:
            logger.warning("Observatory notification integration not available")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Observatory notification integration: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up Observatory notification integration"""
        self._notification_integration = None
    
    async def send_notification(self, notification: NotificationMessage) -> bool:
        """Send notification through Observatory system"""
        if not self._notification_integration:
            logger.warning("Observatory notification system not available")
            return False
        
        try:
            # This would use the actual Observatory notification system
            logger.info(f"Observatory notification: {notification.title} - {notification.message}")
            return True
        except Exception as e:
            logger.error(f"Failed to send Observatory notification: {e}")
            return False
    
    async def send_alert(self, title: str, message: str, level: str) -> bool:
        """Send alert notification"""
        notification = NotificationMessage(
            title=title,
            message=message,
            level=level,
            timestamp=datetime.utcnow()
        )
        return await self.send_notification(notification)


class ObservatoryServiceRegistryImpl(ObservatoryServiceRegistry):
    """Observatory service registry implementation with automatic service discovery"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize Observatory service registry with automatic service discovery"""
        if self._initialized:
            return True
        
        logger.info("Initializing Observatory service registry...")
        
        # Try to initialize each Observatory service
        services_to_initialize = [
            ("health", ObservatoryHealthService()),
            ("status", ObservatoryStatusService()),
            ("ai_response", ObservatoryAIService()),
            ("context", ObservatoryContextService()),
            ("notification", ObservatoryNotificationService())
        ]
        
        initialized_count = 0
        for service_name, service in services_to_initialize:
            try:
                if await service.initialize():
                    await self.register_service(service_name, service)
                    initialized_count += 1
                    logger.info(f"Observatory service '{service_name}' initialized successfully")
                else:
                    logger.warning(f"Observatory service '{service_name}' failed to initialize")
            except Exception as e:
                logger.error(f"Error initializing Observatory service '{service_name}': {e}")
        
        self._initialized = True
        logger.info(f"Observatory service registry initialized with {initialized_count}/{len(services_to_initialize)} services")
        
        return initialized_count > 0  # Success if at least one service initialized
    
    async def get_service(self, service_name: str) -> Optional[Any]:
        """Get service by name"""
        return self._services.get(service_name)
    
    async def register_service(self, name: str, service: Any) -> None:
        """Register a service"""
        self._services[name] = service
    
    async def is_service_available(self, service_name: str) -> bool:
        """Check if service is available"""
        service = self._services.get(service_name)
        if not service:
            return False
        
        try:
            health = await service.get_health()
            return health in [ServiceHealth.HEALTHY, ServiceHealth.DEGRADED]
        except Exception:
            return False
    
    async def get_available_services(self) -> List[str]:
        """Get list of available services"""
        available = []
        for name, service in self._services.items():
            try:
                if await self.is_service_available(name):
                    available.append(name)
            except Exception:
                continue
        return available
    
    async def health_check_all(self) -> Dict[str, ServiceHealth]:
        """Health check all registered services"""
        results = {}
        for name, service in self._services.items():
            try:
                health = await service.get_health()
                results[name] = health
            except Exception as e:
                logger.error(f"Health check failed for Observatory service {name}: {e}")
                results[name] = ServiceHealth.UNHEALTHY
        return results
    
    async def cleanup(self) -> None:
        """Clean up all Observatory services"""
        for name, service in self._services.items():
            try:
                await service.cleanup()
                logger.info(f"Observatory service '{name}' cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up Observatory service '{name}': {e}")
        
        self._services.clear()
        self._initialized = False


# Factory function for creating Observatory service registry
async def create_observatory_service_registry() -> ObservatoryServiceRegistry:
    """Create and initialize Observatory service registry"""
    registry = ObservatoryServiceRegistryImpl()
    await registry.initialize()
    return registry


# Global Observatory service registry instance
_observatory_registry: Optional[ObservatoryServiceRegistry] = None


async def get_observatory_service_registry() -> Optional[ObservatoryServiceRegistry]:
    """Get the global Observatory service registry"""
    global _observatory_registry
    if _observatory_registry is None:
        try:
            _observatory_registry = await create_observatory_service_registry()
        except Exception as e:
            logger.error(f"Failed to create Observatory service registry: {e}")
            return None
    return _observatory_registry


async def cleanup_observatory_service_registry() -> None:
    """Clean up the global Observatory service registry"""
    global _observatory_registry
    if _observatory_registry:
        await _observatory_registry.cleanup()
        _observatory_registry = None