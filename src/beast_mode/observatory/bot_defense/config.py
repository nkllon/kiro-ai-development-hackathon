"""
Bot Defense Configuration Management
Centralized configuration for all defense systems and attack detection.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum

class DefenseMode(Enum):
    """Defense operation modes."""
    PASSIVE = "passive"      # Monitor only, no defense actions
    ACTIVE = "active"        # Full defense with all systems enabled
    STEALTH = "stealth"      # Minimal response, maximum tracking
    CIRCUS = "circus"        # Maximum entertainment value

@dataclass
class AttackDetectionConfig:
    """Configuration for attack detection system."""
    
    # Suspicious endpoints that indicate bot behavior
    suspicious_endpoints: List[str] = field(default_factory=lambda: [
        '/wp-admin/', '/wp-login.php', '/wp-config.php',
        '/phpmyadmin/', '/pma/', '/mysql/',
        '/.env', '/.git/', '/config/',
        '/admin/', '/administrator/', '/login.php',
        '/xmlrpc.php', '/wp-content/uploads/',
        '/cgi-bin/', '/shell.php', '/c99.php'
    ])
    
    # Rate limiting thresholds
    rate_limits: Dict[str, int] = field(default_factory=lambda: {
        'requests_per_minute': 60,
        'requests_per_hour': 1000,
        'requests_per_day': 10000,
        'suspicious_requests_per_minute': 5
    })
    
    # User agent patterns that indicate bots
    suspicious_user_agents: List[str] = field(default_factory=lambda: [
        r'(?i)bot', r'(?i)crawler', r'(?i)spider', r'(?i)scraper',
        r'(?i)curl', r'(?i)wget', r'(?i)python', r'(?i)requests',
        r'(?i)scanner', r'(?i)exploit', r'(?i)hack'
    ])
    
    # Minimum confidence score to trigger defense (0.0-1.0)
    confidence_threshold: float = 0.4
    
    # Enable geolocation lookup
    enable_geolocation: bool = True
    
    # GeoIP database path (optional)
    geoip_database_path: Optional[str] = None

@dataclass 
class DefenseSystemConfig:
    """Configuration for defense systems."""
    
    # Overall defense mode
    mode: DefenseMode = DefenseMode.ACTIVE
    
    # Enable individual defense systems
    emoji_nuke_enabled: bool = True
    bandwidth_waste_enabled: bool = True
    punishment_escalation_enabled: bool = True
    ip_blocking_enabled: bool = True
    
    # Punishment escalation settings
    max_punishment_level: int = 15
    escalation_thresholds: List[int] = field(default_factory=lambda: [
        1, 3, 5, 10, 15, 25, 50, 75, 100, 150, 200, 300, 500, 750, 1000
    ])
    
    # Emoji nuke settings
    emoji_nuke_base_size: int = 1024      # Base payload size in bytes
    emoji_nuke_max_size: int = 1048576    # Max payload size (1MB)
    emoji_varieties: List[str] = field(default_factory=lambda: [
        '🤖', '💥', '⚡', '🔥', '💀', '👾', '🎪', '🎭', '🎨', '🌈'
    ])
    
    # Bandwidth waste settings
    bandwidth_waste_base_size: int = 4096     # Base waste size in bytes
    bandwidth_waste_max_size: int = 10485760  # Max waste size (10MB)
    waste_data_types: List[str] = field(default_factory=lambda: [
        'random_bytes', 'repeated_patterns', 'fake_images', 'dummy_json'
    ])
    
    # IP blocking settings
    block_duration_hours: int = 24
    permanent_block_threshold: int = 1000  # Attacks before permanent block
    
    # Performance limits
    max_concurrent_defenses: int = 100
    defense_timeout_seconds: int = 30
    
    # Entertainment settings
    enable_achievements: bool = True
    enable_hall_of_shame: bool = True
    enable_circus_mode: bool = True

@dataclass
class DatabaseConfig:
    """Database configuration for bot defense."""
    
    # Database connection (uses Observatory's database by default)
    use_observatory_db: bool = True
    
    # Custom database URL (if not using Observatory's)
    database_url: Optional[str] = None
    
    # Table name prefixes
    table_prefix: str = "bot_defense_"
    
    # Data retention settings
    attack_retention_days: int = 30
    bot_profile_retention_days: int = 90
    defense_action_retention_days: int = 7
    
    # Performance settings
    batch_insert_size: int = 100
    connection_pool_size: int = 10

@dataclass
class BotDefenseConfig:
    """Master configuration for bot defense system."""
    
    attack_detection: AttackDetectionConfig = field(default_factory=AttackDetectionConfig)
    defense_systems: DefenseSystemConfig = field(default_factory=DefenseSystemConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    
    # Global settings
    enabled: bool = True
    debug_mode: bool = False
    log_level: str = "INFO"
    
    # WebSocket settings for real-time updates
    websocket_enabled: bool = True
    websocket_update_interval: float = 1.0  # seconds
    websocket_max_connections: int = 100
    
    # Dashboard settings
    dashboard_enabled: bool = True
    dashboard_auto_refresh: bool = True
    dashboard_refresh_interval: int = 5  # seconds
    
    @classmethod
    def from_env(cls) -> 'BotDefenseConfig':
        """Create configuration from environment variables."""
        config = cls()
        
        # Override with environment variables
        if os.getenv('BOT_DEFENSE_ENABLED'):
            config.enabled = os.getenv('BOT_DEFENSE_ENABLED', 'true').lower() == 'true'
        
        if os.getenv('BOT_DEFENSE_MODE'):
            mode_str = os.getenv('BOT_DEFENSE_MODE', 'active').lower()
            try:
                config.defense_systems.mode = DefenseMode(mode_str)
            except ValueError:
                pass  # Use default
        
        if os.getenv('BOT_DEFENSE_DEBUG'):
            config.debug_mode = os.getenv('BOT_DEFENSE_DEBUG', 'false').lower() == 'true'
        
        if os.getenv('BOT_DEFENSE_LOG_LEVEL'):
            config.log_level = os.getenv('BOT_DEFENSE_LOG_LEVEL', 'INFO').upper()
        
        # Database settings
        if os.getenv('BOT_DEFENSE_DATABASE_URL'):
            config.database.use_observatory_db = False
            config.database.database_url = os.getenv('BOT_DEFENSE_DATABASE_URL')
        
        return config

# Global configuration instance
_config: Optional[BotDefenseConfig] = None

def get_config() -> BotDefenseConfig:
    """Get the global bot defense configuration."""
    global _config
    if _config is None:
        _config = BotDefenseConfig.from_env()
    return _config

def set_config(config: BotDefenseConfig) -> None:
    """Set the global bot defense configuration."""
    global _config
    _config = config

def reload_config() -> BotDefenseConfig:
    """Reload configuration from environment."""
    global _config
    _config = BotDefenseConfig.from_env()
    return _config