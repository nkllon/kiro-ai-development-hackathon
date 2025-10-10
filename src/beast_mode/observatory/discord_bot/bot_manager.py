"""
Discord Bot Manager

Central orchestrator for Discord bot operations with Observatory integration.
Built with extraction-ready architecture for standalone framework.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from .models import BotConfig, BotStatus, BotHealthStatus, ServiceHealth
from .exceptions import DiscordBotError, ConfigurationError, ServiceUnavailableError
from .interfaces import ObservatoryServiceRegistry
from .notification_service import DiscordNotificationService, DiscordNotificationConfig

logger = logging.getLogger(__name__)


class BotManager:
    """Central manager for Discord bot operations"""
    
    def __init__(self, config: BotConfig, service_registry: Optional[ObservatoryServiceRegistry] = None):
        self.config = config
        self.service_registry = service_registry
        self._status = BotStatus.OFFLINE
        self._start_time = None
        self._discord_client = None
        self._notification_service = None
        self._command_handlers = {}
        self._event_handlers = {}
        
    async def initialize(self) -> bool:
        """Initialize the bot manager and all services"""
        try:
            logger.info("Initializing Discord Bot Manager...")
            self._status = BotStatus.STARTING
            self._start_time = datetime.utcnow()
            
            # Initialize notification service
            if self.config.token:
                await self._initialize_notification_service()
            
            # Initialize Observatory service integration
            if self.config.observatory_integration and self.service_registry:
                await self._initialize_observatory_integration()
            
            # Initialize Discord client (placeholder for now)
            await self._initialize_discord_client()
            
            self._status = BotStatus.ONLINE
            logger.info("Discord Bot Manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Discord Bot Manager: {e}")
            self._status = BotStatus.ERROR
            return False
    
    async def cleanup(self) -> None:
        """Clean up all bot resources"""
        logger.info("Cleaning up Discord Bot Manager...")
        
        if self._notification_service:
            await self._notification_service.cleanup()
        
        if self._discord_client:
            # Clean up Discord client when implemented
            pass
        
        self._status = BotStatus.OFFLINE
        logger.info("Discord Bot Manager cleanup complete")
    
    async def get_health_status(self) -> BotHealthStatus:
        """Get comprehensive bot health status"""
        uptime = 0.0
        if self._start_time:
            uptime = (datetime.utcnow() - self._start_time).total_seconds()
        
        # Get service health statuses
        services = []
        if self._notification_service:
            health = await self._notification_service.get_health()
            services.append({
                'name': 'discord_notifications',
                'health': health,
                'response_time_ms': 0.0,  # TODO: Implement actual timing
                'last_check': datetime.utcnow()
            })
        
        # Get Observatory service health if available
        if self.service_registry:
            try:
                observatory_health = await self.service_registry.health_check_all()
                for service_name, health in observatory_health.items():
                    services.append({
                        'name': f'observatory_{service_name}',
                        'health': health,
                        'response_time_ms': 0.0,
                        'last_check': datetime.utcnow()
                    })
            except Exception as e:
                logger.warning(f"Could not get Observatory service health: {e}")
        
        return BotHealthStatus(
            status=self._status,
            uptime_seconds=uptime,
            total_commands=0,  # TODO: Implement command tracking
            successful_commands=0,
            failed_commands=0,
            services=services,
            avg_response_time_ms=0.0,
            memory_usage_mb=0.0,  # TODO: Implement memory tracking
            last_updated=datetime.utcnow()
        )
    
    async def send_notification(self, title: str, message: str, level: str) -> bool:
        """Send notification through Discord"""
        if not self._notification_service:
            logger.warning("Notification service not available")
            return False
        
        return await self._notification_service.send_alert(title, message, level)
    
    async def _initialize_notification_service(self) -> None:
        """Initialize Discord notification service"""
        config = DiscordNotificationConfig(
            bot_token=self.config.token,
            status_channel_id=self.config.status_channel_id,
            alerts_channel_id=self.config.alerts_channel_id,
            general_channel_id=self.config.general_channel_id
        )
        
        self._notification_service = DiscordNotificationService(config)
        
        # Initialize the service (but don't fail if it doesn't work)
        try:
            await self._notification_service.initialize()
            logger.info("Discord notification service initialized")
        except Exception as e:
            logger.warning(f"Could not initialize Discord notification service: {e}")
            # Continue without notifications rather than failing completely
    
    async def _initialize_observatory_integration(self) -> None:
        """Initialize Observatory service integration"""
        if not self.service_registry:
            return
        
        try:
            # Check which Observatory services are available
            available_services = await self.service_registry.get_available_services()
            logger.info(f"Available Observatory services: {available_services}")
            
            # Initialize integrations based on available services
            if 'ai_consultation' in available_services:
                logger.info("AI consultation service available for Discord integration")
            
            if 'health_monitor' in available_services:
                logger.info("Health monitor service available for Discord integration")
            
        except Exception as e:
            logger.warning(f"Could not initialize Observatory integration: {e}")
            # Continue in degraded mode
    
    async def _initialize_discord_client(self) -> None:
        """Initialize Discord client (placeholder)"""
        # This is where we would initialize the actual Discord client
        # For now, just log that we're ready
        logger.info("Discord client initialization placeholder - ready for implementation")
    
    def get_status(self) -> BotStatus:
        """Get current bot status"""
        return self._status
    
    def is_healthy(self) -> bool:
        """Check if bot is healthy"""
        return self._status in [BotStatus.ONLINE, BotStatus.DEGRADED]


# Global bot manager instance (singleton pattern)
_bot_manager: Optional[BotManager] = None


def get_bot_manager() -> Optional[BotManager]:
    """Get the global bot manager instance"""
    return _bot_manager


def initialize_bot_manager(config: BotConfig, service_registry: Optional[ObservatoryServiceRegistry] = None) -> BotManager:
    """Initialize the global bot manager"""
    global _bot_manager
    _bot_manager = BotManager(config, service_registry)
    return _bot_manager


async def cleanup_bot_manager() -> None:
    """Clean up the global bot manager"""
    global _bot_manager
    if _bot_manager:
        await _bot_manager.cleanup()
        _bot_manager = None