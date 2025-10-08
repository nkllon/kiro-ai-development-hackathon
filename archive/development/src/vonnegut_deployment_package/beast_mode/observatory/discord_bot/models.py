"""
Data models for Discord Bot Integration

These models are designed for easy extraction to standalone framework.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pathlib import Path


class NotificationLevel(str, Enum):
    """Notification severity levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class BotStatus(str, Enum):
    """Discord bot operational status"""
    STARTING = "starting"
    ONLINE = "online"
    DEGRADED = "degraded"  # Some services unavailable
    OFFLINE = "offline"
    ERROR = "error"


class ServiceHealth(str, Enum):
    """Health status for integrated services"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class BotConfig:
    """Configuration for Discord bot"""
    # Discord Configuration
    token: str
    status_channel_id: Optional[str] = None
    alerts_channel_id: Optional[str] = None
    general_channel_id: Optional[str] = None
    
    # Bot Behavior
    command_prefix: str = "!bmo"
    ai_enabled: bool = True
    auto_respond_mentions: bool = True
    
    # Observatory Integration
    observatory_integration: bool = True
    health_monitoring: bool = True
    
    # Security
    audit_logging: bool = True
    rate_limiting: bool = True
    
    # Framework Extraction Ready
    service_registry_config: Dict[str, Any] = field(default_factory=dict)
    plugin_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DiscordChannel:
    """Discord channel information"""
    id: str
    name: str
    type: str
    guild_id: str
    permissions: List[str] = field(default_factory=list)


@dataclass
class CommandContext:
    """Context for command execution"""
    # Discord Context
    channel_id: str
    user_id: str
    guild_id: Optional[str]
    message_id: str
    
    # Command Context
    command: str
    args: List[str]
    raw_message: str
    
    # Observatory Context (optional)
    observatory_context: Optional[Dict[str, Any]] = None
    user_permissions: List[str] = field(default_factory=list)
    
    # Execution Context
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: str = ""


@dataclass
class CommandResult:
    """Result of command execution"""
    success: bool
    message: str
    embed_data: Optional[Dict[str, Any]] = None
    attachments: List[str] = field(default_factory=list)
    
    # Error Information
    error_code: Optional[str] = None
    error_details: Optional[str] = None
    
    # Execution Metadata
    execution_time_ms: float = 0.0
    service_calls: List[str] = field(default_factory=list)
    fallback_used: bool = False


@dataclass
class ServiceStatus:
    """Status of an integrated service"""
    name: str
    health: ServiceHealth
    response_time_ms: float
    last_check: datetime
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BotHealthStatus:
    """Overall bot health status"""
    status: BotStatus
    uptime_seconds: float
    total_commands: int
    successful_commands: int
    failed_commands: int
    
    # Service Health
    services: List[ServiceStatus] = field(default_factory=list)
    
    # Performance Metrics
    avg_response_time_ms: float = 0.0
    memory_usage_mb: float = 0.0
    
    # Last Update
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class NotificationMessage:
    """Discord notification message"""
    title: str
    message: str
    level: NotificationLevel
    
    # Optional Metadata
    components: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Formatting
    embed: bool = True
    mention_roles: List[str] = field(default_factory=list)
    
    # Tracking
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: str = ""


@dataclass
class PluginConfig:
    """Configuration for bot plugins (framework extraction ready)"""
    name: str
    enabled: bool
    version: str
    
    # Plugin Metadata
    description: str = ""
    author: str = ""
    permissions: List[str] = field(default_factory=list)
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Security
    sandboxed: bool = True
    resource_limits: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditLogEntry:
    """Audit log entry for bot operations"""
    timestamp: datetime
    user_id: str
    action: str
    resource: str
    
    # Context
    channel_id: Optional[str] = None
    guild_id: Optional[str] = None
    
    # Details
    details: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error_message: Optional[str] = None
    
    # Correlation
    correlation_id: str = ""
    session_id: str = ""