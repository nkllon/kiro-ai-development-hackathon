"""
Unit tests for deployment configuration management
"""

import pytest
import tempfile
import os
from pathlib import Path

from beast_mode.deployment.config_manager import (
    ConfigManager, DeploymentConfig, RedisConfig, 
    AgentConfig, MonitoringConfig, DeploymentEnvironment
)


class TestConfigManager:
    """Test configuration manager functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager(self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_default_configs_loaded(self):
        """Test that default configurations are loaded"""
        environments = self.config_manager.list_environments()
        
        expected_envs = ["development", "production", "single_machine", "distributed"]
        for env in expected_envs:
            assert env in environments
    
    def test_get_development_config(self):
        """Test getting development configuration"""
        config = self.config_manager.get_config("development")
        
        assert config.environment == DeploymentEnvironment.DEVELOPMENT
        assert config.redis.host == "localhost"
        assert config.redis.port == 6379
        assert config.agent.log_level == "DEBUG"
        assert not config.monitoring.enable_performance_monitoring
    
    def test_get_production_config(self):
        """Test getting production configuration"""
        config = self.config_manager.get_config("production")
        
        assert config.environment == DeploymentEnvironment.PRODUCTION
        assert config.redis.ssl == True
        assert config.agent.log_level == "INFO"
        assert config.monitoring.enable_performance_monitoring
    
    def test_get_unknown_environment(self):
        """Test getting unknown environment raises error"""
        with pytest.raises(ValueError, match="Unknown environment"):
            self.config_manager.get_config("unknown")
    
    def test_save_and_load_config(self):
        """Test saving and loading configuration"""
        # Create custom config
        config = DeploymentConfig(
            environment=DeploymentEnvironment.DEVELOPMENT,
            redis=RedisConfig(host="custom-redis", port=6380),
            agent=AgentConfig(agent_id="test_agent", capabilities=["test"]),
            monitoring=MonitoringConfig()
        )
        
        # Save config
        self.config_manager.save_config("test_env", config)
        
        # Load config
        loaded_config = self.config_manager.load_config("test_env")
        
        assert loaded_config.environment == DeploymentEnvironment.DEVELOPMENT
        assert loaded_config.redis.host == "custom-redis"
        assert loaded_config.redis.port == 6380
        assert loaded_config.agent.agent_id == "test_agent"
        assert loaded_config.agent.capabilities == ["test"]
    
    def test_load_nonexistent_config(self):
        """Test loading non-existent configuration"""
        with pytest.raises(FileNotFoundError):
            self.config_manager.load_config("nonexistent")
    
    def test_validate_valid_config(self):
        """Test validating valid configuration"""
        config = self.config_manager.get_config("development")
        issues = self.config_manager.validate_config(config)
        
        assert len(issues) == 0
    
    def test_validate_invalid_config(self):
        """Test validating invalid configuration"""
        config = DeploymentConfig(
            environment=DeploymentEnvironment.DEVELOPMENT,
            redis=RedisConfig(host="", port=-1),  # Invalid
            agent=AgentConfig(agent_id="", capabilities=[]),  # Invalid
            monitoring=MonitoringConfig(health_check_interval=-1)  # Invalid
        )
        
        issues = self.config_manager.validate_config(config)
        
        assert len(issues) > 0
        assert any("Redis host cannot be empty" in issue for issue in issues)
        assert any("Redis port must be between" in issue for issue in issues)
        assert any("Agent ID cannot be empty" in issue for issue in issues)
        assert any("Agent must have at least one capability" in issue for issue in issues)
        assert any("Health check interval must be positive" in issue for issue in issues)
    
    def test_get_environment_variables(self):
        """Test getting environment variables"""
        env_vars = self.config_manager.get_environment_variables("development")
        
        expected_vars = [
            "BEAST_MODE_ENVIRONMENT", "REDIS_HOST", "REDIS_PORT", 
            "AGENT_ID", "AGENT_CAPABILITIES", "LOG_LEVEL"
        ]
        
        for var in expected_vars:
            assert var in env_vars
        
        assert env_vars["BEAST_MODE_ENVIRONMENT"] == "development"
        assert env_vars["REDIS_HOST"] == "localhost"
        assert env_vars["REDIS_PORT"] == "6379"
    
    def test_create_docker_env_file(self):
        """Test creating Docker environment file"""
        env_file = os.path.join(self.temp_dir, "test.env")
        self.config_manager.create_docker_env_file("development", env_file)
        
        assert os.path.exists(env_file)
        
        with open(env_file, 'r') as f:
            content = f.read()
        
        assert "BEAST_MODE_ENVIRONMENT=development" in content
        assert "REDIS_HOST=localhost" in content
        assert "REDIS_PORT=6379" in content


class TestDataModels:
    """Test configuration data models"""
    
    def test_redis_config_defaults(self):
        """Test Redis configuration defaults"""
        config = RedisConfig()
        
        assert config.host == "localhost"
        assert config.port == 6379
        assert config.password is None
        assert config.db == 0
        assert config.ssl == False
        assert config.connection_pool_size == 10
    
    def test_agent_config_defaults(self):
        """Test agent configuration defaults"""
        config = AgentConfig(agent_id="test", capabilities=["test"])
        
        assert config.agent_id == "test"
        assert config.capabilities == ["test"]
        assert config.log_level == "INFO"
        assert config.mailbox_log_file == "beast_mode_mailbox.log"
        assert config.spore_directory == "./spores"
        assert config.max_message_size == 1048576
    
    def test_monitoring_config_defaults(self):
        """Test monitoring configuration defaults"""
        config = MonitoringConfig()
        
        assert config.health_check_interval == 30
        assert config.metrics_collection_interval == 60
        assert config.log_retention_days == 7
        assert config.enable_performance_monitoring == True
        
        # Check default alert thresholds
        assert "cpu_usage" in config.alert_thresholds
        assert "memory_usage" in config.alert_thresholds
        assert "disk_usage" in config.alert_thresholds
        assert "message_latency" in config.alert_thresholds
    
    def test_deployment_config_defaults(self):
        """Test deployment configuration defaults"""
        config = DeploymentConfig(
            environment=DeploymentEnvironment.DEVELOPMENT,
            redis=RedisConfig(),
            agent=AgentConfig(agent_id="test", capabilities=["test"]),
            monitoring=MonitoringConfig()
        )
        
        assert config.environment == DeploymentEnvironment.DEVELOPMENT
        assert config.service_management is not None
        assert config.service_management["auto_restart"] == True
        assert config.service_management["max_restarts"] == 5
    
    def test_deployment_environment_enum(self):
        """Test deployment environment enumeration"""
        assert DeploymentEnvironment.DEVELOPMENT == "development"
        assert DeploymentEnvironment.STAGING == "staging"
        assert DeploymentEnvironment.PRODUCTION == "production"
        assert DeploymentEnvironment.SINGLE_MACHINE == "single_machine"
        assert DeploymentEnvironment.DISTRIBUTED == "distributed"


class TestConfigValidation:
    """Test configuration validation"""
    
    def test_redis_config_validation(self):
        """Test Redis configuration validation"""
        config_manager = ConfigManager()
        
        # Valid config
        valid_config = DeploymentConfig(
            environment=DeploymentEnvironment.DEVELOPMENT,
            redis=RedisConfig(host="localhost", port=6379),
            agent=AgentConfig(agent_id="test", capabilities=["test"]),
            monitoring=MonitoringConfig()
        )
        
        issues = config_manager.validate_config(valid_config)
        assert len(issues) == 0
        
        # Invalid Redis host
        invalid_config = DeploymentConfig(
            environment=DeploymentEnvironment.DEVELOPMENT,
            redis=RedisConfig(host="", port=6379),
            agent=AgentConfig(agent_id="test", capabilities=["test"]),
            monitoring=MonitoringConfig()
        )
        
        issues = config_manager.validate_config(invalid_config)
        assert any("Redis host cannot be empty" in issue for issue in issues)
        
        # Invalid Redis port
        invalid_config.redis.host = "localhost"
        invalid_config.redis.port = 0
        
        issues = config_manager.validate_config(invalid_config)
        assert any("Redis port must be between" in issue for issue in issues)
    
    def test_agent_config_validation(self):
        """Test agent configuration validation"""
        config_manager = ConfigManager()
        
        # Invalid agent ID
        invalid_config = DeploymentConfig(
            environment=DeploymentEnvironment.DEVELOPMENT,
            redis=RedisConfig(),
            agent=AgentConfig(agent_id="", capabilities=["test"]),
            monitoring=MonitoringConfig()
        )
        
        issues = config_manager.validate_config(invalid_config)
        assert any("Agent ID cannot be empty" in issue for issue in issues)
        
        # Invalid capabilities
        invalid_config.agent.agent_id = "test"
        invalid_config.agent.capabilities = []
        
        issues = config_manager.validate_config(invalid_config)
        assert any("Agent must have at least one capability" in issue for issue in issues)
    
    def test_monitoring_config_validation(self):
        """Test monitoring configuration validation"""
        config_manager = ConfigManager()
        
        # Invalid health check interval
        invalid_config = DeploymentConfig(
            environment=DeploymentEnvironment.DEVELOPMENT,
            redis=RedisConfig(),
            agent=AgentConfig(agent_id="test", capabilities=["test"]),
            monitoring=MonitoringConfig(health_check_interval=0)
        )
        
        issues = config_manager.validate_config(invalid_config)
        assert any("Health check interval must be positive" in issue for issue in issues)