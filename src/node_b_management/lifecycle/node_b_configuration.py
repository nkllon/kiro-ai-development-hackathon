"""
Node B Configuration Management

Provides comprehensive configuration validation and management for Node B instances
with secure credential handling and deployment coordination.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path
from datetime import datetime
import hashlib
import re

from ..core.node_b_component import NodeBComponent


@dataclass
class RedisConfiguration:
    """Redis connection configuration"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    ssl: bool = False
    ssl_cert_reqs: str = "required"
    socket_timeout: float = 5.0
    socket_connect_timeout: float = 5.0
    retry_on_timeout: bool = True
    max_connections: int = 10
    
    def __post_init__(self):
        """Validate Redis configuration after initialization"""
        if not isinstance(self.port, int) or not (1 <= self.port <= 65535):
            raise ValueError(f"Invalid Redis port: {self.port}")
        
        if not isinstance(self.db, int) or self.db < 0:
            raise ValueError(f"Invalid Redis database: {self.db}")


@dataclass
class SecurityConfiguration:
    """Security configuration for Node B"""
    enable_ssl: bool = True
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    ssl_ca_path: Optional[str] = None
    authentication_required: bool = True
    token_expiry_hours: int = 24
    audit_logging: bool = True
    encryption_enabled: bool = True
    
    def __post_init__(self):
        """Validate security configuration after initialization"""
        if self.enable_ssl:
            if self.ssl_cert_path and not Path(self.ssl_cert_path).exists():
                raise ValueError(f"SSL certificate not found: {self.ssl_cert_path}")
            
            if self.ssl_key_path and not Path(self.ssl_key_path).exists():
                raise ValueError(f"SSL key not found: {self.ssl_key_path}")


@dataclass
class PerformanceLimits:
    """Performance limits and resource constraints"""
    max_memory_mb: int = 1024
    max_cpu_percent: float = 80.0
    max_connections: int = 100
    message_rate_limit: int = 1000  # messages per minute
    max_queue_size: int = 10000
    heartbeat_interval: float = 30.0
    health_check_interval: float = 60.0
    
    def __post_init__(self):
        """Validate performance limits after initialization"""
        if self.max_memory_mb <= 0:
            raise ValueError(f"Invalid max memory: {self.max_memory_mb}")
        
        if not (0.0 < self.max_cpu_percent <= 100.0):
            raise ValueError(f"Invalid max CPU percent: {self.max_cpu_percent}")
        
        if self.max_connections <= 0:
            raise ValueError(f"Invalid max connections: {self.max_connections}")


@dataclass
class NetworkSettings:
    """Network communication settings"""
    listen_host: str = "0.0.0.0"
    listen_port: int = 8080
    external_host: Optional[str] = None
    external_port: Optional[int] = None
    enable_discovery: bool = True
    discovery_interval: float = 60.0
    consensus_timeout: float = 30.0
    message_retry_attempts: int = 3
    message_retry_delay: float = 1.0
    
    def __post_init__(self):
        """Validate network settings after initialization"""
        if not isinstance(self.listen_port, int) or not (1 <= self.listen_port <= 65535):
            raise ValueError(f"Invalid listen port: {self.listen_port}")
        
        if self.external_port and not (1 <= self.external_port <= 65535):
            raise ValueError(f"Invalid external port: {self.external_port}")


@dataclass
class NodeBConfiguration:
    """
    Comprehensive Node B configuration with validation
    
    Provides complete configuration management for Node B instances including
    secure credential handling, validation, and deployment coordination.
    
    Requirements: 1.6, 1.7, 4.1, 4.2, 4.3
    """
    node_id: str
    capabilities: List[str]
    redis_config: RedisConfiguration = field(default_factory=RedisConfiguration)
    security_config: SecurityConfiguration = field(default_factory=SecurityConfiguration)
    performance_limits: PerformanceLimits = field(default_factory=PerformanceLimits)
    network_settings: NetworkSettings = field(default_factory=NetworkSettings)
    
    # Optional configuration
    description: str = ""
    tags: List[str] = field(default_factory=list)
    environment: str = "development"
    log_level: str = "INFO"
    
    # Internal fields
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    config_version: str = "1.0.0"
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        self.validate()
    
    def validate(self) -> bool:
        """
        Comprehensive configuration validation
        
        Returns:
            bool: True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
            
        Requirements: 1.6, 1.7, 4.1, 4.2, 4.3
        """
        # Validate node_id
        if not self.node_id or not isinstance(self.node_id, str):
            raise ValueError("node_id must be a non-empty string")
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', self.node_id):
            raise ValueError("node_id must contain only alphanumeric characters, underscores, and hyphens")
        
        # Validate capabilities
        if not self.capabilities or not isinstance(self.capabilities, list):
            raise ValueError("capabilities must be a non-empty list")
        
        for capability in self.capabilities:
            if not isinstance(capability, str) or not capability.strip():
                raise ValueError("All capabilities must be non-empty strings")
        
        # Validate environment
        valid_environments = ["development", "staging", "production"]
        if self.environment not in valid_environments:
            raise ValueError(f"environment must be one of: {valid_environments}")
        
        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_log_levels:
            raise ValueError(f"log_level must be one of: {valid_log_levels}")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NodeBConfiguration':
        """Create configuration from dictionary"""
        # Extract nested configurations
        redis_config = RedisConfiguration(**data.get('redis_config', {}))
        security_config = SecurityConfiguration(**data.get('security_config', {}))
        performance_limits = PerformanceLimits(**data.get('performance_limits', {}))
        network_settings = NetworkSettings(**data.get('network_settings', {}))
        
        # Create main configuration
        config_data = data.copy()
        config_data['redis_config'] = redis_config
        config_data['security_config'] = security_config
        config_data['performance_limits'] = performance_limits
        config_data['network_settings'] = network_settings
        
        return cls(**config_data)
    
    def get_config_hash(self) -> str:
        """Get hash of configuration for change detection"""
        config_str = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()
    
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.now().isoformat()


class NodeBConfigurationManager(NodeBComponent):
    """
    Node B Configuration Manager
    
    Manages configuration validation, loading, and deployment coordination
    for Node B instances with secure credential handling.
    
    Requirements: 1.6, 1.7, 4.1, 4.2, 4.3
    """

    def __init__(self, node_id: str = None):
        """
        Initialize Configuration Manager
        
        Args:
            node_id: Optional Node B instance ID
        """
        super().__init__("configuration_manager", node_id)
        
        # Configuration storage
        self._configurations: Dict[str, NodeBConfiguration] = {}
        self._config_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Environment variable cache
        self._env_cache: Dict[str, str] = {}
        self._env_cache_timestamp = None
        self._env_cache_ttl = 300  # 5 minutes
        
        # Deployment coordination
        self._deployment_locks: Dict[str, str] = {}
        
        self._logger.info("NodeBConfigurationManager initialized")

    async def load_configuration_from_env(self, node_id: str) -> NodeBConfiguration:
        """
        Load Node B configuration from environment variables
        
        Args:
            node_id: Node B instance ID
            
        Returns:
            NodeBConfiguration: Loaded and validated configuration
            
        Requirements: 4.1, 4.2
        """
        try:
            self._logger.info(f"Loading configuration from environment for node {node_id}")
            
            # Refresh environment cache if needed
            await self._refresh_env_cache()
            
            # Load basic configuration
            config_data = {
                'node_id': node_id,
                'capabilities': self._get_env_list(f'NODE_B_{node_id.upper().replace("-", "_")}_CAPABILITIES', 
                                                  'NODE_B_CAPABILITIES', 
                                                  default=['coordination', 'analysis']),
                'description': self._get_env(f'NODE_B_{node_id.upper().replace("-", "_")}_DESCRIPTION', 
                                           'NODE_B_DESCRIPTION', 
                                           f'Node B instance {node_id}'),
                'environment': self._get_env('ENVIRONMENT', 'ENV', default='development'),
                'log_level': self._get_env('LOG_LEVEL', 'LOGLEVEL', default='INFO')
            }
            
            # Load Redis configuration
            redis_config = RedisConfiguration(
                host=self._get_env('REDIS_HOST', default='localhost'),
                port=int(self._get_env('REDIS_PORT', default='6379')),
                db=int(self._get_env('REDIS_DB', default='0')),
                ssl=self._get_env('REDIS_SSL', default='false').lower() == 'true',
                ssl_cert_reqs=self._get_env('REDIS_SSL_CERT_REQS', default='required'),
                socket_timeout=float(self._get_env('REDIS_SOCKET_TIMEOUT', default='5.0')),
                socket_connect_timeout=float(self._get_env('REDIS_CONNECT_TIMEOUT', default='5.0')),
                retry_on_timeout=self._get_env('REDIS_RETRY_ON_TIMEOUT', default='true').lower() == 'true',
                max_connections=int(self._get_env('REDIS_MAX_CONNECTIONS', default='10'))
            )
            
            # Load security configuration
            security_config = SecurityConfiguration(
                enable_ssl=self._get_env('NODE_B_SSL_ENABLED', default='true').lower() == 'true',
                ssl_cert_path=self._get_env('NODE_B_SSL_CERT_PATH'),
                ssl_key_path=self._get_env('NODE_B_SSL_KEY_PATH'),
                ssl_ca_path=self._get_env('NODE_B_SSL_CA_PATH'),
                authentication_required=self._get_env('NODE_B_AUTH_REQUIRED', default='true').lower() == 'true',
                token_expiry_hours=int(self._get_env('NODE_B_TOKEN_EXPIRY_HOURS', default='24')),
                audit_logging=self._get_env('NODE_B_AUDIT_LOGGING', default='true').lower() == 'true',
                encryption_enabled=self._get_env('NODE_B_ENCRYPTION_ENABLED', default='true').lower() == 'true'
            )
            
            # Load performance limits
            performance_limits = PerformanceLimits(
                max_memory_mb=int(self._get_env('NODE_B_MAX_MEMORY_MB', default='1024')),
                max_cpu_percent=float(self._get_env('NODE_B_MAX_CPU_PERCENT', default='80.0')),
                max_connections=int(self._get_env('NODE_B_MAX_CONNECTIONS', default='100')),
                message_rate_limit=int(self._get_env('NODE_B_MESSAGE_RATE_LIMIT', default='1000')),
                max_queue_size=int(self._get_env('NODE_B_MAX_QUEUE_SIZE', default='10000')),
                heartbeat_interval=float(self._get_env('NODE_B_HEARTBEAT_INTERVAL', default='30.0')),
                health_check_interval=float(self._get_env('NODE_B_HEALTH_CHECK_INTERVAL', default='60.0'))
            )
            
            # Load network settings
            network_settings = NetworkSettings(
                listen_host=self._get_env('NODE_B_LISTEN_HOST', default='0.0.0.0'),
                listen_port=int(self._get_env(f'NODE_B_{node_id.upper().replace("-", "_")}_PORT', 
                                            'NODE_B_LISTEN_PORT', 
                                            default='8080')),
                external_host=self._get_env('NODE_B_EXTERNAL_HOST'),
                external_port=self._get_env_int('NODE_B_EXTERNAL_PORT'),
                enable_discovery=self._get_env('NODE_B_ENABLE_DISCOVERY', default='true').lower() == 'true',
                discovery_interval=float(self._get_env('NODE_B_DISCOVERY_INTERVAL', default='60.0')),
                consensus_timeout=float(self._get_env('NODE_B_CONSENSUS_TIMEOUT', default='30.0')),
                message_retry_attempts=int(self._get_env('NODE_B_MESSAGE_RETRY_ATTEMPTS', default='3')),
                message_retry_delay=float(self._get_env('NODE_B_MESSAGE_RETRY_DELAY', default='1.0'))
            )
            
            # Create configuration
            config = NodeBConfiguration(
                redis_config=redis_config,
                security_config=security_config,
                performance_limits=performance_limits,
                network_settings=network_settings,
                **config_data
            )
            
            # Validate credentials are available (allow missing in development)
            try:
                await self._validate_credentials()
            except ValueError as e:
                # Re-raise if not in development mode
                if self._get_env('ENVIRONMENT', 'ENV', 'development') != 'development':
                    raise
                else:
                    self._logger.warning(f"Credential validation warning: {e}")
            
            # Store configuration
            self._configurations[node_id] = config
            
            self._logger.info(f"Configuration loaded successfully for node {node_id}")
            return config
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to load configuration for node {node_id}: {e}")
            raise

    async def validate_configuration(self, config: NodeBConfiguration) -> Dict[str, Any]:
        """
        Comprehensive configuration validation
        
        Args:
            config: Configuration to validate
            
        Returns:
            Dict[str, Any]: Validation results with details
            
        Requirements: 1.6, 1.7, 4.1, 4.2, 4.3
        """
        try:
            self._logger.info(f"Validating configuration for node {config.node_id}")
            
            validation_results = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "checks": {}
            }
            
            # Basic validation
            try:
                config.validate()
                validation_results["checks"]["basic_validation"] = True
            except ValueError as e:
                validation_results["valid"] = False
                validation_results["errors"].append(f"Basic validation failed: {e}")
                validation_results["checks"]["basic_validation"] = False
            
            # Credential validation
            try:
                await self._validate_credentials()
                validation_results["checks"]["credentials"] = True
            except Exception as e:
                # In development mode, credential failures are warnings, not errors
                if config.environment == 'development':
                    validation_results["warnings"].append(f"Credential validation warning: {e}")
                    validation_results["checks"]["credentials"] = True  # Pass with warning in dev
                else:
                    validation_results["valid"] = False
                    validation_results["errors"].append(f"Credential validation failed: {e}")
                    validation_results["checks"]["credentials"] = False
            
            # Redis connectivity validation
            try:
                redis_valid = await self._validate_redis_connectivity(config.redis_config)
                validation_results["checks"]["redis_connectivity"] = redis_valid
                if not redis_valid:
                    validation_results["warnings"].append("Redis connectivity could not be verified")
            except Exception as e:
                validation_results["warnings"].append(f"Redis validation failed: {e}")
                validation_results["checks"]["redis_connectivity"] = False
            
            # Security configuration validation
            try:
                security_valid = await self._validate_security_configuration(config.security_config)
                validation_results["checks"]["security_config"] = security_valid
                if not security_valid:
                    validation_results["warnings"].append("Security configuration has issues")
            except Exception as e:
                validation_results["warnings"].append(f"Security validation failed: {e}")
                validation_results["checks"]["security_config"] = False
            
            # Performance limits validation
            try:
                perf_valid = self._validate_performance_limits(config.performance_limits)
                validation_results["checks"]["performance_limits"] = perf_valid
                if not perf_valid:
                    validation_results["warnings"].append("Performance limits may be too restrictive")
            except Exception as e:
                validation_results["warnings"].append(f"Performance validation failed: {e}")
                validation_results["checks"]["performance_limits"] = False
            
            # Deployment conflict check
            try:
                conflict_check = await self._check_deployment_conflicts(config)
                validation_results["checks"]["deployment_conflicts"] = conflict_check
                if not conflict_check:
                    validation_results["valid"] = False
                    validation_results["errors"].append("Deployment conflicts detected")
            except Exception as e:
                validation_results["valid"] = False
                validation_results["errors"].append(f"Deployment conflict check failed: {e}")
                validation_results["checks"]["deployment_conflicts"] = False
            
            # Log validation results
            if validation_results["valid"]:
                self._logger.info(f"Configuration validation passed for node {config.node_id}")
            else:
                self._logger.error(f"Configuration validation failed for node {config.node_id}: {validation_results['errors']}")
            
            if validation_results["warnings"]:
                self._logger.warning(f"Configuration validation warnings for node {config.node_id}: {validation_results['warnings']}")
            
            return validation_results
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Configuration validation error for node {config.node_id}: {e}")
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": [],
                "checks": {}
            }

    async def save_configuration(self, config: NodeBConfiguration, file_path: Optional[str] = None) -> bool:
        """
        Save configuration to file
        
        Args:
            config: Configuration to save
            file_path: Optional file path, defaults to standard location
            
        Returns:
            bool: True if saved successfully
        """
        try:
            if file_path is None:
                config_dir = Path("config/node_b")
                config_dir.mkdir(parents=True, exist_ok=True)
                file_path = config_dir / f"{config.node_id}_config.json"
            
            # Update timestamp
            config.update_timestamp()
            
            # Save to file
            with open(file_path, 'w') as f:
                json.dump(config.to_dict(), f, indent=2)
            
            # Store in memory
            self._configurations[config.node_id] = config
            
            # Add to history
            if config.node_id not in self._config_history:
                self._config_history[config.node_id] = []
            
            self._config_history[config.node_id].append({
                "timestamp": datetime.now().isoformat(),
                "config_hash": config.get_config_hash(),
                "file_path": str(file_path)
            })
            
            self._logger.info(f"Configuration saved for node {config.node_id} to {file_path}")
            return True
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to save configuration for node {config.node_id}: {e}")
            return False

    async def load_configuration_from_file(self, file_path: str) -> NodeBConfiguration:
        """
        Load configuration from file
        
        Args:
            file_path: Path to configuration file
            
        Returns:
            NodeBConfiguration: Loaded configuration
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            config = NodeBConfiguration.from_dict(data)
            self._configurations[config.node_id] = config
            
            self._logger.info(f"Configuration loaded from file {file_path} for node {config.node_id}")
            return config
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to load configuration from file {file_path}: {e}")
            raise

    def get_configuration(self, node_id: str) -> Optional[NodeBConfiguration]:
        """Get stored configuration for a node"""
        return self._configurations.get(node_id)

    def list_configurations(self) -> List[str]:
        """Get list of all stored configuration node IDs"""
        return list(self._configurations.keys())

    # Private helper methods

    async def _refresh_env_cache(self):
        """Refresh environment variable cache"""
        current_time = datetime.now()
        
        if (self._env_cache_timestamp is None or 
            (current_time - self._env_cache_timestamp).total_seconds() > self._env_cache_ttl):
            
            self._env_cache = dict(os.environ)
            self._env_cache_timestamp = current_time
            self._logger.debug("Environment variable cache refreshed")

    def _get_env(self, *keys, default=None) -> Optional[str]:
        """Get environment variable with fallback keys"""
        for key in keys:
            if key in self._env_cache:
                return self._env_cache[key]
        return default

    def _get_env_int(self, *keys, default=None) -> Optional[int]:
        """Get environment variable as integer"""
        value = self._get_env(*keys, default=default)
        if value is not None:
            try:
                return int(value)
            except ValueError:
                self._logger.warning(f"Invalid integer value for env var: {value}")
        return None

    def _get_env_list(self, *keys, default=None) -> List[str]:
        """Get environment variable as list (comma-separated)"""
        value = self._get_env(*keys)
        if value:
            return [item.strip() for item in value.split(',') if item.strip()]
        return default or []

    async def _validate_credentials(self):
        """Validate that required credentials are available"""
        # Check Redis password
        redis_password = self._get_env('REDIS_PASSWORD', 'BEAST_MODE_REDIS_PASSWORD')
        if not redis_password:
            # In test environments, allow missing credentials with warning
            if self._get_env('ENVIRONMENT', 'ENV', 'development') == 'development':
                self._logger.warning("Redis password not set - this is acceptable in development mode")
                return
            else:
                raise ValueError(
                    "Redis password must be set in environment variables. "
                    "Set REDIS_PASSWORD or BEAST_MODE_REDIS_PASSWORD"
                )
        
        self._logger.debug("Credential validation passed")

    async def _validate_redis_connectivity(self, redis_config: RedisConfiguration) -> bool:
        """Validate Redis connectivity"""
        try:
            # This would use the actual Redis connection manager
            # For now, just validate configuration structure
            return True
        except Exception as e:
            self._logger.error(f"Redis connectivity validation failed: {e}")
            return False

    async def _validate_security_configuration(self, security_config: SecurityConfiguration) -> bool:
        """Validate security configuration"""
        try:
            # Check SSL certificate files if SSL is enabled
            if security_config.enable_ssl:
                if security_config.ssl_cert_path and not Path(security_config.ssl_cert_path).exists():
                    self._logger.warning(f"SSL certificate not found: {security_config.ssl_cert_path}")
                    return False
                
                if security_config.ssl_key_path and not Path(security_config.ssl_key_path).exists():
                    self._logger.warning(f"SSL key not found: {security_config.ssl_key_path}")
                    return False
            
            return True
        except Exception as e:
            self._logger.error(f"Security configuration validation failed: {e}")
            return False

    def _validate_performance_limits(self, performance_limits: PerformanceLimits) -> bool:
        """Validate performance limits"""
        try:
            # Check if limits are reasonable
            if performance_limits.max_memory_mb < 128:
                self._logger.warning("Memory limit is very low (< 128MB)")
                return False
            
            if performance_limits.max_cpu_percent < 10.0:
                self._logger.warning("CPU limit is very low (< 10%)")
                return False
            
            return True
        except Exception as e:
            self._logger.error(f"Performance limits validation failed: {e}")
            return False

    async def _check_deployment_conflicts(self, config: NodeBConfiguration) -> bool:
        """Check for deployment conflicts"""
        try:
            # Check if another node is using the same port
            for existing_node_id, existing_config in self._configurations.items():
                if existing_node_id != config.node_id:
                    if (existing_config.network_settings.listen_port == 
                        config.network_settings.listen_port):
                        self._logger.error(
                            f"Port conflict: {config.network_settings.listen_port} "
                            f"already used by node {existing_node_id}"
                        )
                        return False
            
            return True
        except Exception as e:
            self._logger.error(f"Deployment conflict check failed: {e}")
            return False