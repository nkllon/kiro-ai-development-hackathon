"""
Service interfaces for Discord Bot Integration

These interfaces enable clean separation between Discord bot logic and 
Observatory services, making extraction to standalone framework straightforward.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime

from .models import (
    ServiceHealth, CommandContext, CommandResult, 
    BotHealthStatus, NotificationMessage
)


class ServiceInterface(ABC):
    """Base interface for all integrated services"""
    
    @abstractmethod
    async def get_health(self) -> ServiceHealth:
        """Get service health status"""
        pass
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the service"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up service resources"""
        pass


class HealthServiceInterface(ServiceInterface):
    """Interface for health monitoring services"""
    
    @abstractmethod
    async def get_system_health(self) -> BotHealthStatus:
        """Get overall system health"""
        pass
    
    @abstractmethod
    async def get_service_health(self, service_name: str) -> ServiceHealth:
        """Get health of specific service"""
        pass
    
    @abstractmethod
    async def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary for display"""
        pass


class StatusServiceInterface(ServiceInterface):
    """Interface for status reporting services"""
    
    @abstractmethod
    async def get_bot_status(self) -> str:
        """Get current bot status"""
        pass
    
    @abstractmethod
    async def get_uptime(self) -> float:
        """Get bot uptime in seconds"""
        pass
    
    @abstractmethod
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        pass
    
    @abstractmethod
    async def get_usage_statistics(self) -> Dict[str, Any]:
        """Get usage statistics"""
        pass


class AIResponseServiceInterface(ServiceInterface):
    """Interface for AI response services"""
    
    @abstractmethod
    async def generate_response(
        self, 
        query: str, 
        context: CommandContext,
        max_tokens: int = 150
    ) -> str:
        """Generate AI response to user query"""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if AI service is available"""
        pass
    
    @abstractmethod
    async def get_cost_estimate(self, query: str) -> float:
        """Get cost estimate for query"""
        pass


class NotificationServiceInterface(ServiceInterface):
    """Interface for notification services"""
    
    @abstractmethod
    async def send_notification(self, notification: NotificationMessage) -> bool:
        """Send notification"""
        pass
    
    @abstractmethod
    async def send_alert(self, title: str, message: str, level: str) -> bool:
        """Send alert notification"""
        pass


class ContextServiceInterface(ServiceInterface):
    """Interface for context providers (Observatory-specific)"""
    
    @abstractmethod
    async def get_system_context(self) -> Dict[str, Any]:
        """Get system context for AI responses"""
        pass
    
    @abstractmethod
    async def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        pass
    
    @abstractmethod
    async def get_recent_alerts(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent system alerts"""
        pass


class ObservatoryServiceRegistry(ABC):
    """Registry for Observatory-specific services"""
    
    @abstractmethod
    async def get_service(self, service_name: str) -> Optional[ServiceInterface]:
        """Get service by name"""
        pass
    
    @abstractmethod
    async def register_service(self, name: str, service: ServiceInterface) -> None:
        """Register a service"""
        pass
    
    @abstractmethod
    async def is_service_available(self, service_name: str) -> bool:
        """Check if service is available"""
        pass
    
    @abstractmethod
    async def get_available_services(self) -> List[str]:
        """Get list of available services"""
        pass
    
    @abstractmethod
    async def health_check_all(self) -> Dict[str, ServiceHealth]:
        """Health check all registered services"""
        pass


class CommandServiceInterface(ServiceInterface):
    """Interface for command execution services"""
    
    @abstractmethod
    async def execute_command(
        self, 
        command: str, 
        context: CommandContext
    ) -> CommandResult:
        """Execute a command"""
        pass
    
    @abstractmethod
    async def get_available_commands(self) -> List[str]:
        """Get list of available commands"""
        pass
    
    @abstractmethod
    async def get_command_help(self, command: str) -> Optional[str]:
        """Get help text for command"""
        pass


class AuditServiceInterface(ServiceInterface):
    """Interface for audit logging services"""
    
    @abstractmethod
    async def log_action(
        self,
        user_id: str,
        action: str,
        resource: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log an action"""
        pass
    
    @abstractmethod
    async def get_audit_log(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get audit log entries"""
        pass


class SecurityServiceInterface(ServiceInterface):
    """Interface for security services"""
    
    @abstractmethod
    async def validate_permissions(
        self, 
        user_id: str, 
        action: str, 
        resource: str
    ) -> bool:
        """Validate user permissions"""
        pass
    
    @abstractmethod
    async def get_user_permissions(self, user_id: str) -> List[str]:
        """Get user permissions"""
        pass
    
    @abstractmethod
    async def is_rate_limited(self, user_id: str, action: str) -> bool:
        """Check if user is rate limited"""
        pass


# Framework Extraction Ready Interfaces

class FrameworkServiceRegistry(ABC):
    """Generic service registry for standalone framework"""
    
    @abstractmethod
    async def register(self, name: str, service: ServiceInterface) -> None:
        """Register a service"""
        pass
    
    @abstractmethod
    async def get(self, name: str) -> Optional[ServiceInterface]:
        """Get service by name"""
        pass
    
    @abstractmethod
    async def remove(self, name: str) -> bool:
        """Remove service"""
        pass
    
    @abstractmethod
    async def list_services(self) -> List[str]:
        """List all registered services"""
        pass


class PluginInterface(ABC):
    """Interface for bot plugins (framework extraction ready)"""
    
    @abstractmethod
    async def initialize(self, bot_context: Dict[str, Any]) -> bool:
        """Initialize plugin"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up plugin resources"""
        pass
    
    @abstractmethod
    async def handle_command(self, context: CommandContext) -> Optional[CommandResult]:
        """Handle command if plugin supports it"""
        pass
    
    @abstractmethod
    async def handle_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Handle Discord event"""
        pass
    
    @abstractmethod
    def get_commands(self) -> List[str]:
        """Get list of commands this plugin handles"""
        pass
    
    @abstractmethod
    def get_permissions(self) -> List[str]:
        """Get required permissions"""
        pass