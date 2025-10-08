"""
Command System for Discord Bot

Unified command handling with fallbacks and Observatory integration.
Built with extraction-ready architecture for standalone framework.
"""

import logging
from typing import Dict, List, Optional, Any, Callable, Awaitable
from datetime import datetime
from dataclasses import dataclass

from .models import CommandContext, CommandResult, BotConfig
from .exceptions import CommandError, ValidationError
from .interfaces import ObservatoryServiceRegistry

logger = logging.getLogger(__name__)


@dataclass
class Command:
    """Command definition"""
    name: str
    description: str
    handler: Callable[[CommandContext], Awaitable[CommandResult]]
    aliases: List[str] = None
    permissions: List[str] = None
    enabled: bool = True
    
    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []
        if self.permissions is None:
            self.permissions = []


class CommandHandler:
    """Handles command execution with fallbacks"""
    
    def __init__(self, config: BotConfig, service_registry: Optional[ObservatoryServiceRegistry] = None):
        self.config = config
        self.service_registry = service_registry
        self._commands: Dict[str, Command] = {}
        self._aliases: Dict[str, str] = {}
        self._setup_builtin_commands()
    
    def register_command(self, command: Command) -> None:
        """Register a command"""
        self._commands[command.name] = command
        
        # Register aliases
        for alias in command.aliases:
            self._aliases[alias] = command.name
        
        logger.info(f"Registered command: {command.name}")
    
    def unregister_command(self, name: str) -> bool:
        """Unregister a command"""
        if name in self._commands:
            command = self._commands[name]
            
            # Remove aliases
            for alias in command.aliases:
                if alias in self._aliases:
                    del self._aliases[alias]
            
            del self._commands[name]
            logger.info(f"Unregistered command: {name}")
            return True
        return False
    
    async def execute_command(self, context: CommandContext) -> CommandResult:
        """Execute a command"""
        command_name = context.command.lower()
        
        # Resolve alias
        if command_name in self._aliases:
            command_name = self._aliases[command_name]
        
        # Find command
        if command_name not in self._commands:
            return CommandResult(
                success=False,
                message=f"Unknown command: {context.command}. Try `{self.config.command_prefix} help` for available commands.",
                error_code="COMMAND_NOT_FOUND"
            )
        
        command = self._commands[command_name]
        
        # Check if command is enabled
        if not command.enabled:
            return CommandResult(
                success=False,
                message=f"Command '{command_name}' is currently disabled.",
                error_code="COMMAND_DISABLED"
            )
        
        # Execute command
        try:
            start_time = datetime.utcnow()
            result = await command.handler(context)
            end_time = datetime.utcnow()
            
            # Add execution metadata
            result.execution_time_ms = (end_time - start_time).total_seconds() * 1000
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing command {command_name}: {e}")
            return CommandResult(
                success=False,
                message=f"An error occurred while executing the command: {str(e)}",
                error_code="COMMAND_EXECUTION_ERROR",
                error_details=str(e)
            )
    
    def get_available_commands(self) -> List[str]:
        """Get list of available commands"""
        return [name for name, cmd in self._commands.items() if cmd.enabled]
    
    def get_command_help(self, command_name: str) -> Optional[str]:
        """Get help text for a command"""
        if command_name in self._commands:
            return self._commands[command_name].description
        return None
    
    def _setup_builtin_commands(self) -> None:
        """Set up built-in commands"""
        
        # Help command
        help_command = Command(
            name="help",
            description="Show available commands and usage information",
            handler=self._handle_help,
            aliases=["h", "?"]
        )
        self.register_command(help_command)
        
        # Status command
        status_command = Command(
            name="status",
            description="Show bot and system status",
            handler=self._handle_status,
            aliases=["stat"]
        )
        self.register_command(status_command)
        
        # Health command
        health_command = Command(
            name="health",
            description="Show system health information",
            handler=self._handle_health,
            aliases=["healthcheck"]
        )
        self.register_command(health_command)
        
        # Ping command
        ping_command = Command(
            name="ping",
            description="Test bot responsiveness",
            handler=self._handle_ping,
            aliases=["pong"]
        )
        self.register_command(ping_command)
    
    async def _handle_help(self, context: CommandContext) -> CommandResult:
        """Handle help command"""
        if context.args:
            # Help for specific command
            command_name = context.args[0].lower()
            help_text = self.get_command_help(command_name)
            
            if help_text:
                message = f"**{command_name}**: {help_text}"
            else:
                message = f"No help available for command: {command_name}"
        else:
            # General help
            commands = self.get_available_commands()
            message = "**Available Commands:**\n"
            
            for cmd_name in sorted(commands):
                cmd = self._commands[cmd_name]
                message += f"• `{self.config.command_prefix} {cmd_name}` - {cmd.description}\n"
            
            message += f"\nUse `{self.config.command_prefix} help <command>` for detailed help on a specific command."
        
        return CommandResult(success=True, message=message)
    
    async def _handle_status(self, context: CommandContext) -> CommandResult:
        """Handle status command"""
        status_info = "🤖 **Beast Mode Observatory Discord Bot**\n\n"
        
        # Bot status
        status_info += "**Bot Status**: Online ✅\n"
        
        # Observatory integration status
        if self.service_registry:
            try:
                services = await self.service_registry.get_available_services()
                status_info += f"**Observatory Services**: {len(services)} available\n"
                
                if services:
                    status_info += "**Available Services**:\n"
                    for service in sorted(services):
                        status_info += f"  • {service}\n"
                else:
                    status_info += "**Services**: None available\n"
                    
            except Exception as e:
                status_info += f"**Observatory**: Connection issues\n"
                status_info += f"**Error**: {str(e)[:100]}...\n"
        else:
            status_info += "**Mode**: Standalone (no Observatory integration)\n"
        
        # Add timestamp
        status_info += f"\n*Status checked at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC*"
        
        return CommandResult(success=True, message=status_info)
    
    async def _handle_health(self, context: CommandContext) -> CommandResult:
        """Handle health command"""
        health_info = "🏥 **System Health Report**\n\n"
        
        # Bot health
        health_info += "**Discord Bot**: Healthy ✅\n"
        
        # Service health
        if self.service_registry:
            try:
                health_status = await self.service_registry.health_check_all()
                
                if health_status:
                    healthy_count = sum(1 for h in health_status.values() if h.value == "healthy")
                    total_count = len(health_status)
                    
                    health_info += f"**Service Health**: {healthy_count}/{total_count} healthy\n\n"
                    
                    for service, health in sorted(health_status.items()):
                        if health.value == "healthy":
                            emoji = "✅"
                        elif health.value == "degraded":
                            emoji = "⚠️"
                        else:
                            emoji = "❌"
                        
                        health_info += f"{emoji} **{service}**: {health.value.title()}\n"
                else:
                    health_info += "**Services**: No services registered\n"
                    
            except Exception as e:
                health_info += f"**Health Check**: Failed ❌\n"
                health_info += f"**Error**: {str(e)[:100]}...\n"
        else:
            health_info += "**Mode**: Standalone - Basic health only\n"
        
        # Add timestamp
        health_info += f"\n*Health checked at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC*"
        
        return CommandResult(success=True, message=health_info)
    
    async def _handle_ping(self, context: CommandContext) -> CommandResult:
        """Handle ping command"""
        return CommandResult(
            success=True,
            message="🏓 Pong! Bot is responsive."
        )


class CommandRouter:
    """Routes commands to appropriate handlers"""
    
    def __init__(self):
        self._handlers: Dict[str, CommandHandler] = {}
        self._default_handler: Optional[CommandHandler] = None
    
    def register_handler(self, name: str, handler: CommandHandler) -> None:
        """Register a command handler"""
        self._handlers[name] = handler
        logger.info(f"Registered command handler: {name}")
    
    def set_default_handler(self, handler: CommandHandler) -> None:
        """Set default command handler"""
        self._default_handler = handler
    
    async def route_command(self, context: CommandContext) -> CommandResult:
        """Route command to appropriate handler"""
        # For now, use default handler
        # In the future, this could route based on command prefix, permissions, etc.
        
        if self._default_handler:
            return await self._default_handler.execute_command(context)
        
        return CommandResult(
            success=False,
            message="No command handler available",
            error_code="NO_HANDLER"
        )