"""
Discord Client Implementation

Core Discord client with event handling and Observatory integration.
Built with extraction-ready architecture for standalone framework.
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime

from .models import BotConfig, BotStatus, CommandContext, CommandResult
from .exceptions import DiscordBotError, AuthenticationError, RateLimitError
from .interfaces import ObservatoryServiceRegistry

logger = logging.getLogger(__name__)


class DiscordClient:
    """Discord client wrapper with Observatory integration"""
    
    def __init__(self, config: BotConfig, service_registry: Optional[ObservatoryServiceRegistry] = None):
        self.config = config
        self.service_registry = service_registry
        self._client = None
        self._status = BotStatus.OFFLINE
        self._event_handlers = {}
        self._command_handlers = {}
        
    async def initialize(self) -> bool:
        """Initialize Discord client"""
        try:
            # Import discord.py here to avoid dependency issues
            import discord
            
            # Create Discord client
            intents = discord.Intents.default()
            intents.message_content = True  # Needed for command processing
            
            self._client = discord.Client(intents=intents)
            
            # Set up event handlers
            self._setup_event_handlers()
            
            # Login and connect
            await self._client.login(self.config.token)
            
            self._status = BotStatus.ONLINE
            logger.info("Discord client initialized successfully")
            return True
            
        except ImportError:
            logger.error("discord.py not installed. Install with: pip install discord.py")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Discord client: {e}")
            self._status = BotStatus.ERROR
            return False
    
    async def cleanup(self) -> None:
        """Clean up Discord client"""
        if self._client and not self._client.is_closed():
            await self._client.close()
        self._status = BotStatus.OFFLINE
    
    def _setup_event_handlers(self) -> None:
        """Set up Discord event handlers"""
        
        @self._client.event
        async def on_ready():
            logger.info(f"Discord bot connected as {self._client.user}")
            self._status = BotStatus.ONLINE
            
            # Send startup notification if configured
            if self.config.status_channel_id:
                await self._send_startup_notification()
        
        @self._client.event
        async def on_message(message):
            # Ignore messages from the bot itself
            if message.author == self._client.user:
                return
            
            # Handle commands and mentions
            await self._handle_message(message)
        
        @self._client.event
        async def on_error(event, *args, **kwargs):
            logger.error(f"Discord client error in {event}: {args}")
    
    async def _handle_message(self, message) -> None:
        """Handle incoming Discord message"""
        try:
            # Check if message is a command
            if message.content.startswith(self.config.command_prefix):
                await self._handle_command(message)
            
            # Check if bot is mentioned
            elif self._client.user in message.mentions and self.config.auto_respond_mentions:
                await self._handle_mention(message)
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def _handle_command(self, message) -> None:
        """Handle command message"""
        try:
            # Parse command
            content = message.content[len(self.config.command_prefix):].strip()
            parts = content.split()
            
            if not parts:
                return
            
            command = parts[0].lower()
            args = parts[1:]
            
            # Create command context
            context = CommandContext(
                channel_id=str(message.channel.id),
                user_id=str(message.author.id),
                guild_id=str(message.guild.id) if message.guild else None,
                message_id=str(message.id),
                command=command,
                args=args,
                raw_message=message.content,
                timestamp=datetime.utcnow()
            )
            
            # Execute command
            result = await self._execute_command(context)
            
            # Send response
            if result.success:
                await message.channel.send(result.message)
            else:
                await message.channel.send(f"Error: {result.message}")
                
        except Exception as e:
            logger.error(f"Error handling command: {e}")
            await message.channel.send("Sorry, I encountered an error processing that command.")
    
    async def _handle_mention(self, message) -> None:
        """Handle bot mention"""
        try:
            # Extract query (remove bot mention)
            query = message.content
            for mention in message.mentions:
                if mention == self._client.user:
                    query = query.replace(f'<@{mention.id}>', '').strip()
                    query = query.replace(f'<@!{mention.id}>', '').strip()
            
            if not query:
                await message.channel.send("Hi! How can I help you? Try `!bmo help` for available commands.")
                return
            
            # Generate AI response if available
            if self.config.ai_enabled and self.service_registry:
                response = await self._generate_ai_response(query, message)
                await message.channel.send(response)
            else:
                await message.channel.send("I see you mentioned me! Try `!bmo help` for available commands.")
                
        except Exception as e:
            logger.error(f"Error handling mention: {e}")
            await message.channel.send("Sorry, I encountered an error processing your message.")
    
    async def _execute_command(self, context: CommandContext) -> CommandResult:
        """Execute a command"""
        command = context.command
        
        # Built-in commands
        if command == "help":
            return await self._command_help(context)
        elif command == "status":
            return await self._command_status(context)
        elif command == "health":
            return await self._command_health(context)
        elif command == "ping":
            return await self._command_ping(context)
        else:
            return CommandResult(
                success=False,
                message=f"Unknown command: {command}. Try `!bmo help` for available commands."
            )
    
    async def _command_help(self, context: CommandContext) -> CommandResult:
        """Help command"""
        help_text = """
**Beast Mode Observatory Discord Bot**

Available commands:
• `!bmo help` - Show this help message
• `!bmo status` - Show bot status
• `!bmo health` - Show system health
• `!bmo ping` - Test bot responsiveness

You can also mention me (@{bot_name}) with questions and I'll try to help!
        """.strip()
        
        bot_name = self._client.user.display_name if self._client.user else "Bot"
        help_text = help_text.format(bot_name=bot_name)
        
        return CommandResult(success=True, message=help_text)
    
    async def _command_status(self, context: CommandContext) -> CommandResult:
        """Status command"""
        status_info = f"🤖 **Bot Status**: {self._status.value.title()}\n"
        
        if self.service_registry:
            try:
                services = await self.service_registry.get_available_services()
                status_info += f"🔧 **Observatory Services**: {len(services)} available\n"
                status_info += f"📊 **Services**: {', '.join(services)}"
            except Exception as e:
                status_info += f"⚠️ **Observatory**: Connection issues ({str(e)[:50]}...)"
        else:
            status_info += "🔧 **Mode**: Standalone (no Observatory integration)"
        
        return CommandResult(success=True, message=status_info)
    
    async def _command_health(self, context: CommandContext) -> CommandResult:
        """Health command"""
        health_info = f"❤️ **Bot Health**: {self._status.value.title()}\n"
        
        if self.service_registry:
            try:
                health_status = await self.service_registry.health_check_all()
                healthy_count = sum(1 for h in health_status.values() if h.value == "healthy")
                total_count = len(health_status)
                
                health_info += f"🏥 **Services Health**: {healthy_count}/{total_count} healthy\n"
                
                for service, health in health_status.items():
                    emoji = "✅" if health.value == "healthy" else "⚠️" if health.value == "degraded" else "❌"
                    health_info += f"{emoji} {service}: {health.value}\n"
                    
            except Exception as e:
                health_info += f"⚠️ **Health Check Failed**: {str(e)[:100]}..."
        else:
            health_info += "🔧 **Standalone Mode**: Basic health only"
        
        return CommandResult(success=True, message=health_info)
    
    async def _command_ping(self, context: CommandContext) -> CommandResult:
        """Ping command"""
        latency = round(self._client.latency * 1000, 2) if self._client else 0
        return CommandResult(
            success=True,
            message=f"🏓 Pong! Latency: {latency}ms"
        )
    
    async def _generate_ai_response(self, query: str, message) -> str:
        """Generate AI response using Observatory services"""
        if not self.service_registry:
            return "AI services are not available in standalone mode."
        
        try:
            ai_service = await self.service_registry.get_service('ai_consultation')
            if not ai_service:
                return "AI consultation service is not available."
            
            # Create context for AI
            context = CommandContext(
                channel_id=str(message.channel.id),
                user_id=str(message.author.id),
                guild_id=str(message.guild.id) if message.guild else None,
                message_id=str(message.id),
                command="mention",
                args=[],
                raw_message=query,
                timestamp=datetime.utcnow()
            )
            
            # Generate response
            response = await ai_service.generate_response(query, context)
            return response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "Sorry, I'm having trouble generating a response right now. Please try again later."
    
    async def _send_startup_notification(self) -> None:
        """Send startup notification"""
        try:
            channel = self._client.get_channel(int(self.config.status_channel_id))
            if channel:
                await channel.send("🤖 Beast Mode Observatory Discord Bot is now online!")
        except Exception as e:
            logger.error(f"Failed to send startup notification: {e}")
    
    def get_status(self) -> BotStatus:
        """Get current bot status"""
        return self._status
    
    def is_connected(self) -> bool:
        """Check if Discord client is connected"""
        return self._client and not self._client.is_closed()


class DiscordEventHandler:
    """Event handler for Discord events"""
    
    def __init__(self, client: DiscordClient):
        self.client = client
        self._handlers = {}
    
    def register_handler(self, event_type: str, handler: Callable) -> None:
        """Register event handler"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    async def handle_event(self, event_type: str, *args, **kwargs) -> None:
        """Handle Discord event"""
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    await handler(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")