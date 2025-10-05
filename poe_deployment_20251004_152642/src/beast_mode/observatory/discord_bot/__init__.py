"""
Discord Bot Integration for Beast Mode Observatory

This module provides Discord bot functionality integrated with the Observatory system.
Built with extraction-ready architecture for standalone Discord Bot Framework OSS.

Key Features:
- Secure token management and automatic Discord app setup
- Service abstraction layer for Observatory integration
- Graceful degradation when Observatory services unavailable
- Plugin-ready architecture for community extensions
- MSP-grade reliability and monitoring

Architecture:
- BotManager: Orchestrates all bot operations
- SecurityManager: Handles tokens, permissions, and audit logging
- ServiceRegistry: Abstracts Observatory service dependencies
- CommandSystem: Unified command handling with fallbacks
- EventProcessor: Discord event handling and routing
"""

from .models import (
    BotConfig, BotStatus, NotificationLevel, DiscordChannel,
    CommandContext, CommandResult, ServiceHealth
)
from .exceptions import (
    DiscordBotError, ConfigurationError, ServiceUnavailableError,
    PermissionError, RateLimitError
)
from .interfaces import (
    ServiceInterface, HealthServiceInterface, StatusServiceInterface,
    AIResponseServiceInterface, ObservatoryServiceRegistry
)
from .bot_manager import BotManager, get_bot_manager
from .security_manager import SecurityManager, TokenManager
from .service_registry import ServiceRegistry, ServiceDiscovery
from .discord_client import DiscordClient, DiscordEventHandler
from .command_system import CommandHandler, Command, CommandRouter
from .notification_service import (
    DiscordNotificationService, send_discord_notification
)
from .observatory_integration import (
    ObservatoryServiceRegistryImpl, get_observatory_service_registry,
    cleanup_observatory_service_registry
)

__version__ = "0.1.0"
__all__ = [
    # Models
    "BotConfig", "BotStatus", "NotificationLevel", "DiscordChannel",
    "CommandContext", "CommandResult", "ServiceHealth",
    
    # Exceptions
    "DiscordBotError", "ConfigurationError", "ServiceUnavailableError",
    "PermissionError", "RateLimitError",
    
    # Interfaces
    "ServiceInterface", "HealthServiceInterface", "StatusServiceInterface",
    "AIResponseServiceInterface", "ObservatoryServiceRegistry",
    
    # Core Components
    "BotManager", "get_bot_manager",
    "SecurityManager", "TokenManager",
    "ServiceRegistry", "ServiceDiscovery",
    "DiscordClient", "DiscordEventHandler",
    "CommandHandler", "Command", "CommandRouter",
    
    # Notification System
    "DiscordNotificationService", "send_discord_notification",
    
    # Observatory Integration
    "ObservatoryServiceRegistryImpl", "get_observatory_service_registry",
    "cleanup_observatory_service_registry",
]