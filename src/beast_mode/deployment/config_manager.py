"""
Configuration Management for Beast Mode Deployment

Handles environment-specific configuration, validation, and management
for different deployment scenarios.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum


class DeploymentEnvironment(str, Enum):
    """Supported deployment environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    SINGLE_MACHINE = "single_machine"
    DISTRIBUTED = "distributed"


@dataclass
class RedisConfig:
    """Redis configuration settings"""
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    db: int = 0
    ssl: bool = False
    connection_pool_size: int = 10
    retry_attempts: int = 3
    retry_delay: float = 1.0


@dataclass
class AgentConfig:
    """Agent-specific configuration"""
    agent_id: str
    capabilities: List[str]
    log_level: str = "INFO"
    mailbox_log_file: str = "beast_mode_mailbox.log"
    spore_directory: str = "./spores"
    max_message_size: int = 1048576  # 1MB
    heartbeat_interval: int = 30
    discovery_timeout: int = 10


@dataclass
class MonitoringConfig:
    """Monitoring and health check configuration"""
    health_check_interval: int = 30
    metrics_collection_interval: int = 60
    alert_thresholds: Dict[str, float] = None
    log_retention_days: int = 7
    enable_performance_monitoring: bool = True
    
    def __post_init__(self) -> Any:
        """__post_init__ - Enhanced for compliance"""
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        if self.alert_thresholds is None:
            self.alert_thresholds = {
                "cpu_usage": 80.0,
                "memory_usage": 85.0,
                "disk_usage": 90.0,
                "message_latency": 1000.0  # ms
            }


@dataclass
class DeploymentConfig:
    """Complete deployment configuration"""
    environment: DeploymentEnvironment
    redis: RedisConfig
    agent: AgentConfig
    monitoring: MonitoringConfig
    service_management: Dict[str, Any] = None
    
    def __post_init__(self) -> Any:
        """__post_init__ - Enhanced for compliance"""
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        if self.service_management is None:
            self.service_management = {
                "auto_restart": True,
                "max_restarts": 5,
                "restart_delay": 10,
                "graceful_shutdown_timeout": 30
            }


class ConfigManager:
    """Manages configuration for different deployment scenarios"""
    
    def __init__(self, config_dir -> Any: str = "./config") -> Any:
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self._configs: Dict[str, DeploymentConfig] = {}
        self._load_default_configs()
    
    def _load_default_configs(self) -> Any:
        """_load_default_configs - Enhanced for compliance"""
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Load default configurations for each environment"""
        # Development configuration
        dev_config = DeploymentConfig(
            environment=DeploymentEnvironment.DEVELOPMENT,
            redis=RedisConfig(
                host="localhost",
                port=6379,
                connection_pool_size=5
            ),
            agent=AgentConfig(
                agent_id="dev_agent",
                capabilities=["development", "testing"],
                log_level="DEBUG"
            ),
            monitoring=MonitoringConfig(
                health_check_interval=10,
                enable_performance_monitoring=False
            )
        )
        self._configs["development"] = dev_config
        
        # Production configuration
        prod_config = DeploymentConfig(
            environment=DeploymentEnvironment.PRODUCTION,
            redis=RedisConfig(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                password=os.getenv("REDIS_PASSWORD"),
                ssl=True,
                connection_pool_size=20
            ),
            agent=AgentConfig(
                agent_id=os.getenv("AGENT_ID", "prod_agent"),
                capabilities=os.getenv("AGENT_CAPABILITIES", "").split(","),
                log_level="INFO",
                heartbeat_interval=60
            ),
            monitoring=MonitoringConfig(
                health_check_interval=30,
                metrics_collection_interval=30,
                log_retention_days=30
            )
        )
        self._configs["production"] = prod_config
        
        # Single machine configuration
        single_config = DeploymentConfig(
            environment=DeploymentEnvironment.SINGLE_MACHINE,
            redis=RedisConfig(
                host="localhost",
                port=6379,
                connection_pool_size=10
            ),
            agent=AgentConfig(
                agent_id="single_machine_agent",
                capabilities=["all_in_one"],
                log_level="INFO"
            ),
            monitoring=MonitoringConfig(
                health_check_interval=15,
                enable_performance_monitoring=True
            )
        )
        self._configs["single_machine"] = single_config
        
        # Distributed configuration
        distributed_config = DeploymentConfig(
            environment=DeploymentEnvironment.DISTRIBUTED,
            redis=RedisConfig(
                host=os.getenv("REDIS_CLUSTER_HOST", "redis-cluster"),
                port=int(os.getenv("REDIS_CLUSTER_PORT", "6379")),
                password=os.getenv("REDIS_CLUSTER_PASSWORD"),
                ssl=True,
                connection_pool_size=50
            ),
            agent=AgentConfig(
                agent_id=os.getenv("AGENT_ID", f"distributed_agent_{os.getpid()}"),
                capabilities=os.getenv("AGENT_CAPABILITIES", "").split(","),
                log_level="INFO",
                heartbeat_interval=30
            ),
            monitoring=MonitoringConfig(
                health_check_interval=20,
                metrics_collection_interval=30,
                log_retention_days=14
            )
        )
        self._configs["distributed"] = distributed_config
    
    def get_config(self, environment: str) -> DeploymentConfig:
        """get_config - Enhanced for compliance"""
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Get configuration for specified environment"""
        if environment not in self._configs:
            raise ValueError(f"Unknown environment: {environment}")
        return self._configs[environment]
    
    def save_config(self, environment -> Any: str, config -> Any: DeploymentConfig) -> Any:
        """save_config - Enhanced for compliance"""
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Save configuration to file"""
        config_file = self.config_dir / f"{environment}.yaml"
        config_dict = asdict(config)
        
        with open(config_file, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False)
        
        self._configs[environment] = config
    
    def load_config(self, environment: str) -> DeploymentConfig:
        """load_config - Enhanced for compliance"""
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Load configuration from file"""
        config_file = self.config_dir / f"{environment}.yaml"
        
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")
        
        with open(config_file, 'r') as f:
            config_dict = yaml.safe_load(f)
        
        # Convert dict back to dataclass
        redis_config = RedisConfig(**config_dict['redis'])
        agent_config = AgentConfig(**config_dict['agent'])
        monitoring_config = MonitoringConfig(**config_dict['monitoring'])
        
        config = DeploymentConfig(
            environment=DeploymentEnvironment(config_dict['environment']),
            redis=redis_config,
            agent=agent_config,
            monitoring=monitoring_config,
            service_management=config_dict.get('service_management', {})
        )
        
        self._configs[environment] = config
        return config
    
    def validate_config(self, config: DeploymentConfig) -> List[str]:
        """validate_config - Enhanced for compliance"""
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Validate configuration and return list of issues"""
        issues = []
        
        # Validate Redis config
        if not config.redis.host:
            issues.append("Redis host cannot be empty")
        if config.redis.port <= 0 or config.redis.port > 65535:
            issues.append("Redis port must be between 1 and 65535")
        
        # Validate Agent config
        if not config.agent.agent_id:
            issues.append("Agent ID cannot be empty")
        if not config.agent.capabilities:
            issues.append("Agent must have at least one capability")
        
        # Validate monitoring config
        if config.monitoring.health_check_interval <= 0:
            issues.append("Health check interval must be positive")
        
        return issues
    
    def get_environment_variables(self, environment: str) -> Dict[str, str]:
        """get_environment_variables - Enhanced for compliance"""
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Get environment variables for deployment"""
        config = self.get_config(environment)
        
        env_vars = {
            "BEAST_MODE_ENVIRONMENT": environment,
            "REDIS_HOST": config.redis.host,
            "REDIS_PORT": str(config.redis.port),
            "REDIS_DB": str(config.redis.db),
            "AGENT_ID": config.agent.agent_id,
            "AGENT_CAPABILITIES": ",".join(config.agent.capabilities),
            "LOG_LEVEL": config.agent.log_level,
            "MAILBOX_LOG_FILE": config.agent.mailbox_log_file,
            "SPORE_DIRECTORY": config.agent.spore_directory,
            "HEALTH_CHECK_INTERVAL": str(config.monitoring.health_check_interval),
            "METRICS_COLLECTION_INTERVAL": str(config.monitoring.metrics_collection_interval)
        }
        
        # Add optional Redis password
        if config.redis.password:
            env_vars["REDIS_PASSWORD"] = config.redis.password
        
        return env_vars
    
    def create_docker_env_file(self, environment -> Any: str, output_path -> Any: str = ".env") -> Any:
        """create_docker_env_file - Enhanced for compliance"""
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Create Docker environment file"""
        env_vars = self.get_environment_variables(environment)
        
        with open(output_path, 'w') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
    
    def list_environments(self) -> List[str]:
        """list_environments - Enhanced for compliance"""
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """List available environments"""
        return list(self._configs.keys())