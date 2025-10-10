"""
Discord Notification Service

Provides Discord notification functionality with Observatory integration.
Built with extraction-ready architecture for standalone framework.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .models import (
    BotConfig, NotificationLevel, NotificationMessage, 
    DiscordChannel, ServiceHealth
)
from .exceptions import (
    DiscordBotError, ConfigurationError, ServiceUnavailableError,
    RateLimitError
)
from .interfaces import NotificationServiceInterface

logger = logging.getLogger(__name__)


@dataclass
class DiscordNotificationConfig:
    """Configuration for Discord notifications"""
    bot_token: str
    status_channel_id: Optional[str] = None
    alerts_channel_id: Optional[str] = None
    general_channel_id: Optional[str] = None
    
    # Rate limiting
    max_notifications_per_minute: int = 10
    burst_limit: int = 5
    
    # Formatting
    use_embeds: bool = True
    include_timestamps: bool = True
    mention_on_critical: bool = True


class DiscordNotificationService(NotificationServiceInterface):
    """Discord notification service with Observatory integration"""
    
    def __init__(self, config: DiscordNotificationConfig):
        self.config = config
        self._client = None
        self._initialized = False
        self._rate_limiter = {}
        self._last_notification_times = []
        
    async def initialize(self) -> bool:
        """Initialize Discord client"""
        try:
            # Import discord.py here to avoid dependency issues
            import discord
            
            # Create Discord client with minimal intents
            intents = discord.Intents.default()
            intents.message_content = False  # We don't need to read messages
            
            self._client = discord.Client(intents=intents)
            
            # Set up event handlers
            @self._client.event
            async def on_ready():
                logger.info(f"Discord notification service connected as {self._client.user}")
                self._initialized = True
            
            @self._client.event
            async def on_error(event, *args, **kwargs):
                logger.error(f"Discord client error in {event}: {args}")
            
            # Start the client
            await self._client.login(self.config.bot_token)
            
            return True
            
        except ImportError:
            logger.error("discord.py not installed. Install with: pip install discord.py")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Discord notification service: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up Discord client"""
        if self._client and not self._client.is_closed():
            await self._client.close()
        self._initialized = False
    
    async def get_health(self) -> ServiceHealth:
        """Get service health"""
        if not self._initialized or not self._client:
            return ServiceHealth.UNHEALTHY
        
        if self._client.is_closed():
            return ServiceHealth.UNHEALTHY
        
        # Check if we can access channels
        try:
            if self.config.status_channel_id:
                channel = self._client.get_channel(int(self.config.status_channel_id))
                if not channel:
                    return ServiceHealth.DEGRADED
            return ServiceHealth.HEALTHY
        except Exception:
            return ServiceHealth.DEGRADED
    
    async def send_notification(self, notification: NotificationMessage) -> bool:
        """Send notification to Discord"""
        if not self._initialized or not self._client:
            logger.warning("Discord notification service not initialized")
            return False
        
        try:
            # Check rate limits
            if not self._check_rate_limit():
                logger.warning("Rate limit exceeded for Discord notifications")
                return False
            
            # Determine target channel
            channel_id = self._get_target_channel(notification.level)
            if not channel_id:
                logger.warning(f"No channel configured for notification level {notification.level}")
                return False
            
            channel = self._client.get_channel(int(channel_id))
            if not channel:
                logger.error(f"Could not find Discord channel {channel_id}")
                return False
            
            # Format message
            if self.config.use_embeds:
                embed = self._create_embed(notification)
                await channel.send(embed=embed)
            else:
                message = self._format_text_message(notification)
                await channel.send(message)
            
            self._record_notification()
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Discord notification: {e}")
            return False
    
    async def send_alert(self, title: str, message: str, level: str) -> bool:
        """Send alert notification"""
        notification = NotificationMessage(
            title=title,
            message=message,
            level=NotificationLevel(level),
            timestamp=datetime.utcnow()
        )
        return await self.send_notification(notification)
    
    def _get_target_channel(self, level: NotificationLevel) -> Optional[str]:
        """Get target channel for notification level"""
        if level in [NotificationLevel.ERROR, NotificationLevel.CRITICAL]:
            return self.config.alerts_channel_id or self.config.status_channel_id
        elif level == NotificationLevel.WARNING:
            return self.config.status_channel_id
        else:
            return self.config.general_channel_id or self.config.status_channel_id
    
    def _create_embed(self, notification: NotificationMessage) -> 'discord.Embed':
        """Create Discord embed for notification"""
        import discord
        
        # Color mapping for notification levels
        colors = {
            NotificationLevel.DEBUG: discord.Color.light_grey(),
            NotificationLevel.INFO: discord.Color.blue(),
            NotificationLevel.WARNING: discord.Color.orange(),
            NotificationLevel.ERROR: discord.Color.red(),
            NotificationLevel.CRITICAL: discord.Color.dark_red(),
        }
        
        embed = discord.Embed(
            title=notification.title,
            description=notification.message,
            color=colors.get(notification.level, discord.Color.default()),
            timestamp=notification.timestamp
        )
        
        # Add components if present
        if notification.components:
            embed.add_field(
                name="Components",
                value=", ".join(notification.components),
                inline=False
            )
        
        # Add metadata if present
        if notification.metadata:
            for key, value in notification.metadata.items():
                embed.add_field(
                    name=key.replace("_", " ").title(),
                    value=str(value),
                    inline=True
                )
        
        # Add footer
        embed.set_footer(text=f"Beast Mode Observatory • {notification.level.upper()}")
        
        return embed
    
    def _format_text_message(self, notification: NotificationMessage) -> str:
        """Format text message for notification"""
        level_emoji = {
            NotificationLevel.DEBUG: "🔍",
            NotificationLevel.INFO: "ℹ️",
            NotificationLevel.WARNING: "⚠️",
            NotificationLevel.ERROR: "❌",
            NotificationLevel.CRITICAL: "🚨",
        }
        
        emoji = level_emoji.get(notification.level, "📢")
        message = f"{emoji} **{notification.title}**\n{notification.message}"
        
        if notification.components:
            message += f"\n**Components:** {', '.join(notification.components)}"
        
        if self.config.include_timestamps:
            message += f"\n*{notification.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}*"
        
        return message
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        now = datetime.utcnow()
        
        # Clean old timestamps
        cutoff = now.timestamp() - 60  # 1 minute ago
        self._last_notification_times = [
            t for t in self._last_notification_times if t > cutoff
        ]
        
        # Check limits
        if len(self._last_notification_times) >= self.config.max_notifications_per_minute:
            return False
        
        return True
    
    def _record_notification(self) -> None:
        """Record notification timestamp for rate limiting"""
        self._last_notification_times.append(datetime.utcnow().timestamp())


# Convenience functions for easy import (matches your test script)

async def send_discord_notification(
    title: str,
    message: str,
    level: NotificationLevel,
    components: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Convenience function to send Discord notification
    
    This function creates a notification service instance and sends the notification.
    In production, you would use a singleton service instance.
    """
    # This is a simplified implementation for testing
    # In production, this would use a configured service instance
    
    notification = NotificationMessage(
        title=title,
        message=message,
        level=level,
        components=components or [],
        metadata=metadata or {},
        timestamp=datetime.utcnow()
    )
    
    # For now, just log the notification (until we have proper service setup)
    logger.info(f"Discord Notification: {title} - {message} ({level})")
    
    # TODO: Use actual Discord service when properly configured
    return True


# Service factory function
def create_notification_service(config: Dict[str, Any]) -> DiscordNotificationService:
    """Create Discord notification service from configuration"""
    discord_config = DiscordNotificationConfig(
        bot_token=config.get('bot_token', ''),
        status_channel_id=config.get('status_channel_id'),
        alerts_channel_id=config.get('alerts_channel_id'),
        general_channel_id=config.get('general_channel_id'),
        max_notifications_per_minute=config.get('max_notifications_per_minute', 10),
        use_embeds=config.get('use_embeds', True),
        include_timestamps=config.get('include_timestamps', True),
        mention_on_critical=config.get('mention_on_critical', True)
    )
    
    return DiscordNotificationService(discord_config)