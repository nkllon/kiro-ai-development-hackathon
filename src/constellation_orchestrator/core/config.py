"""Configuration management for Constellation Orchestrator."""

import os
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from pathlib import Path


@dataclass
class ConstellationConfig:
    """Configuration for Constellation Orchestrator with environment variable support."""
    
    # Redis configuration
    redis_url: str = field(default_factory=lambda: os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
    redis_password: str = field(default_factory=lambda: os.getenv('REDIS_PASSWORD', ''))
    
    # Agent configuration
    max_concurrent_agents: int = field(default_factory=lambda: int(os.getenv('MAX_CONCURRENT_AGENTS', '5')))
    base_agent_count: int = field(default_factory=lambda: int(os.getenv('BASE_AGENT_COUNT', '3')))
    max_agent_count: int = field(default_factory=lambda: int(os.getenv('MAX_AGENT_COUNT', '20')))
    claude_cli_path: str = field(default_factory=lambda: os.getenv('CLAUDE_CLI_PATH', 'claude'))
    
    # Execution configuration
    default_task_timeout: int = field(default_factory=lambda: int(os.getenv('DEFAULT_TASK_TIMEOUT', '300')))
    max_retry_count: int = field(default_factory=lambda: int(os.getenv('MAX_RETRY_COUNT', '3')))
    scale_threshold: float = field(default_factory=lambda: float(os.getenv('SCALE_THRESHOLD', '0.8')))
    scale_cooldown: int = field(default_factory=lambda: int(os.getenv('SCALE_COOLDOWN', '60')))
    
    # Storage configuration
    log_directory: str = field(default_factory=lambda: os.getenv('LOG_DIRECTORY', '/tmp/constellation_logs'))
    max_memory_tasks: int = field(default_factory=lambda: int(os.getenv('MAX_MEMORY_TASKS', '1000')))
    
    # Monitoring configuration
    enable_metrics: bool = field(default_factory=lambda: os.getenv('ENABLE_METRICS', 'true').lower() == 'true')
    metrics_port: int = field(default_factory=lambda: int(os.getenv('METRICS_PORT', '8080')))
    health_check_interval: int = field(default_factory=lambda: int(os.getenv('HEALTH_CHECK_INTERVAL', '30')))
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.redis_password:
            redis_password = os.getenv('BEAST_MODE_REDIS_PASSWORD', '')
            if redis_password:
                self.redis_password = redis_password
        
        # Ensure log directory exists
        Path(self.log_directory).mkdir(parents=True, exist_ok=True)
        
        # Validate numeric constraints
        if self.max_concurrent_agents <= 0:
            raise ValueError("max_concurrent_agents must be positive")
        if self.base_agent_count <= 0:
            raise ValueError("base_agent_count must be positive")
        if self.max_agent_count < self.base_agent_count:
            raise ValueError("max_agent_count must be >= base_agent_count")
        if self.default_task_timeout <= 0:
            raise ValueError("default_task_timeout must be positive")
        if not (0.0 < self.scale_threshold < 1.0):
            raise ValueError("scale_threshold must be between 0 and 1")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'redis_url': self.redis_url,
            'max_concurrent_agents': self.max_concurrent_agents,
            'base_agent_count': self.base_agent_count,
            'max_agent_count': self.max_agent_count,
            'claude_cli_path': self.claude_cli_path,
            'default_task_timeout': self.default_task_timeout,
            'max_retry_count': self.max_retry_count,
            'scale_threshold': self.scale_threshold,
            'scale_cooldown': self.scale_cooldown,
            'log_directory': self.log_directory,
            'max_memory_tasks': self.max_memory_tasks,
            'enable_metrics': self.enable_metrics,
            'metrics_port': self.metrics_port,
            'health_check_interval': self.health_check_interval
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ConstellationConfig':
        """Create configuration from dictionary."""
        return cls(**config_dict)
    
    @classmethod
    def load_from_env(cls) -> 'ConstellationConfig':
        """Load configuration from environment variables."""
        return cls()  # Uses default_factory functions that read from env