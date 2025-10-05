"""
Configuration management for the Beast Mode Coordination Observatory.

This module provides configuration loading, validation, and management
for all Observatory components.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from decimal import Decimal

from .models import (
    ObservatoryConfig,
    RedisConfig,
    WebSocketConfig,
    MetricsConfig,
    AnalyticsConfig,
    AnomalyConfig,
    CostTrackingConfig,
    GamificationConfig,
    WebInterfaceConfig,
    ProviderConfig,
)


logger = logging.getLogger(__name__)


class ObservatoryConfigLoader:
    """Loads and validates Observatory configuration from various sources."""
    
    @staticmethod
    def load_from_file(config_path: str) -> ObservatoryConfig:
        """Load configuration from a YAML file."""
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                logger.warning(f"Config file {config_path} not found, using defaults")
                return ObservatoryConfig()
            
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
            
            return ObservatoryConfigLoader._build_config_from_dict(config_data)
            
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            return ObservatoryConfig()
    
    @staticmethod
    def load_from_env() -> ObservatoryConfig:
        """Load configuration from environment variables."""
        try:
            config = ObservatoryConfig()
            
            # Redis configuration
            if os.getenv('OBSERVATORY_REDIS_HOST'):
                config.redis_config.host = os.getenv('OBSERVATORY_REDIS_HOST')
            if os.getenv('OBSERVATORY_REDIS_PORT'):
                config.redis_config.port = int(os.getenv('OBSERVATORY_REDIS_PORT'))
            if os.getenv('OBSERVATORY_REDIS_PASSWORD'):
                config.redis_config.password = os.getenv('OBSERVATORY_REDIS_PASSWORD')
            if os.getenv('OBSERVATORY_REDIS_SSL'):
                config.redis_config.ssl = os.getenv('OBSERVATORY_REDIS_SSL').lower() == 'true'
            
            # WebSocket configuration
            if os.getenv('OBSERVATORY_WEBSOCKET_HOST'):
                config.websocket_config.host = os.getenv('OBSERVATORY_WEBSOCKET_HOST')
            if os.getenv('OBSERVATORY_WEBSOCKET_PORT'):
                config.websocket_config.port = int(os.getenv('OBSERVATORY_WEBSOCKET_PORT'))
            
            # Metrics configuration
            if os.getenv('OBSERVATORY_METRICS_INTERVAL'):
                config.metrics_config.collection_interval_seconds = int(os.getenv('OBSERVATORY_METRICS_INTERVAL'))
            if os.getenv('OBSERVATORY_METRICS_RETENTION_DAYS'):
                config.metrics_config.retention_days = int(os.getenv('OBSERVATORY_METRICS_RETENTION_DAYS'))
            
            # Gamification configuration
            if os.getenv('OBSERVATORY_EMOJI_RAIN_ENABLED'):
                config.gamification_config.emoji_rain_enabled = os.getenv('OBSERVATORY_EMOJI_RAIN_ENABLED').lower() == 'true'
            if os.getenv('OBSERVATORY_ACHIEVEMENTS_ENABLED'):
                config.gamification_config.achievements_enabled = os.getenv('OBSERVATORY_ACHIEVEMENTS_ENABLED').lower() == 'true'
            
            return config
            
        except Exception as e:
            logger.error(f"Failed to load config from environment: {e}")
            return ObservatoryConfig()
    
    @staticmethod
    def _build_config_from_dict(config_data: Dict[str, Any]) -> ObservatoryConfig:
        """Build ObservatoryConfig from dictionary data."""
        config = ObservatoryConfig()
        
        # Redis configuration
        if 'redis' in config_data:
            redis_data = config_data['redis']
            config.redis_config = RedisConfig(
                host=redis_data.get('host', 'localhost'),
                port=redis_data.get('port', 6379),
                password=redis_data.get('password'),
                ssl=redis_data.get('ssl', False),
                connection_pool_size=redis_data.get('connection_pool_size', 10),
                stream_name=redis_data.get('stream_name', 'observatory_metrics')
            )
        
        # WebSocket configuration
        if 'websocket' in config_data:
            ws_data = config_data['websocket']
            config.websocket_config = WebSocketConfig(
                host=ws_data.get('host', '0.0.0.0'),
                port=ws_data.get('port', 8080),
                max_connections=ws_data.get('max_connections', 100),
                heartbeat_interval=ws_data.get('heartbeat_interval', 30)
            )
        
        # Metrics configuration
        if 'metrics' in config_data:
            metrics_data = config_data['metrics']
            config.metrics_config = MetricsConfig(
                collection_interval_seconds=metrics_data.get('collection_interval_seconds', 5),
                retention_days=metrics_data.get('retention_days', 30),
                high_frequency_metrics=metrics_data.get('high_frequency_metrics', []),
                component_discovery_enabled=metrics_data.get('component_discovery_enabled', True),
                performance_impact_limit=metrics_data.get('performance_impact_limit', 0.01)
            )
        
        # Cost tracking configuration
        if 'cost_tracking' in config_data:
            cost_data = config_data['cost_tracking']
            provider_configs = {}
            
            for provider_name, provider_data in cost_data.get('providers', {}).items():
                cost_per_1k_tokens = {}
                for model, cost in provider_data.get('cost_per_1k_tokens', {}).items():
                    cost_per_1k_tokens[model] = Decimal(str(cost))
                
                provider_configs[provider_name] = ProviderConfig(
                    name=provider_name,
                    api_key_env_var=provider_data.get('api_key_env_var', f'{provider_name.upper()}_API_KEY'),
                    cost_per_1k_tokens=cost_per_1k_tokens,
                    rate_limit_rpm=provider_data.get('rate_limit_rpm', 60)
                )
            
            cost_alert_thresholds = {}
            for threshold_name, threshold_value in cost_data.get('alert_thresholds', {}).items():
                cost_alert_thresholds[threshold_name] = Decimal(str(threshold_value))
            
            config.cost_config = CostTrackingConfig(
                provider_configs=provider_configs,
                cost_alert_thresholds=cost_alert_thresholds,
                projection_window_days=cost_data.get('projection_window_days', 30),
                anomaly_detection_sensitivity=cost_data.get('anomaly_detection_sensitivity', 0.8)
            )
        
        # Gamification configuration
        if 'gamification' in config_data:
            gamif_data = config_data['gamification']
            config.gamification_config = GamificationConfig(
                achievements_enabled=gamif_data.get('achievements_enabled', True),
                team_metrics_enabled=gamif_data.get('team_metrics_enabled', True),
                celebration_effects_enabled=gamif_data.get('celebration_effects_enabled', True),
                emoji_rain_enabled=gamif_data.get('emoji_rain_enabled', True),
                leaderboard_enabled=gamif_data.get('leaderboard_enabled', False)
            )
        
        return config


def load_observatory_config(config_path: Optional[str] = None) -> ObservatoryConfig:
    """
    Load Observatory configuration from file and environment variables.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        ObservatoryConfig instance
    """
    # Start with environment variables
    config = ObservatoryConfigLoader.load_from_env()
    
    # Try to load from centralized config file
    if config_path is None:
        # Check environment variable first
        config_path = os.getenv('OBSERVATORY_CONFIG_PATH')
        
        # Fall back to default location
        if config_path is None:
            default_config = Path(__file__).parent.parent.parent.parent / "config" / "observatory.yaml"
            if default_config.exists():
                config_path = str(default_config)
    
    # Override with file configuration if available
    if config_path and Path(config_path).exists():
        file_config = ObservatoryConfigLoader.load_from_file(config_path)
        # Simple merge - file config takes precedence
        config = file_config
        logger.info(f"Loaded configuration from: {config_path}")
    else:
        logger.info("Using default configuration with environment overrides")
    
    # Validate configuration
    if not config.validate():
        logger.warning("Configuration validation failed, using defaults where possible")
    
    logger.info("Observatory configuration loaded successfully")
    return config