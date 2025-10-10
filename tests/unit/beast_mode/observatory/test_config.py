"""
Comprehensive unit tests for the Observatory configuration system.

Tests configuration loading from files, environment variables, validation,
and proper instantiation of all configuration components.
"""

import os
import pytest
import tempfile
import yaml
from pathlib import Path
from decimal import Decimal
from unittest.mock import patch, MagicMock

from src.beast_mode.observatory.config import ObservatoryConfigLoader, load_observatory_config
from src.beast_mode.observatory.models import (
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


@pytest.fixture
def sample_config_dict():
    """Sample configuration dictionary for testing."""
    return {
        'redis': {
            'host': 'redis-server',
            'port': 6380,
            'password': 'secret',
            'ssl': True,
            'connection_pool_size': 20,
            'stream_name': 'test_metrics'
        },
        'websocket': {
            'host': '127.0.0.1',
            'port': 8081,
            'max_connections': 200,
            'heartbeat_interval': 60
        },
        'metrics': {
            'collection_interval_seconds': 10,
            'retention_days': 60,
            'high_frequency_metrics': ['cpu_usage', 'memory_usage'],
            'component_discovery_enabled': False,
            'performance_impact_limit': 0.02
        },
        'cost_tracking': {
            'providers': {
                'anthropic': {
                    'api_key_env_var': 'ANTHROPIC_API_KEY',
                    'cost_per_1k_tokens': {
                        'claude-3-opus': 15.0,
                        'claude-3-sonnet': 3.0
                    },
                    'rate_limit_rpm': 100
                },
                'openai': {
                    'api_key_env_var': 'OPENAI_API_KEY',
                    'cost_per_1k_tokens': {
                        'gpt-4': 30.0,
                        'gpt-3.5-turbo': 2.0
                    },
                    'rate_limit_rpm': 60
                }
            },
            'alert_thresholds': {
                'daily_limit': 100.0,
                'monthly_limit': 2000.0
            },
            'projection_window_days': 14,
            'anomaly_detection_sensitivity': 0.9
        },
        'gamification': {
            'achievements_enabled': False,
            'team_metrics_enabled': False,
            'celebration_effects_enabled': False,
            'emoji_rain_enabled': False,
            'leaderboard_enabled': True
        }
    }


@pytest.fixture
def sample_yaml_config(sample_config_dict):
    """Create a temporary YAML config file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(sample_config_dict, f)
        yield f.name
    os.unlink(f.name)


class TestObservatoryConfigLoader:
    """Test the ObservatoryConfigLoader class."""

    def test_load_from_file_success(self, sample_yaml_config):
        """Test successful loading from YAML file."""
        config = ObservatoryConfigLoader.load_from_file(sample_yaml_config)

        assert isinstance(config, ObservatoryConfig)
        assert config.redis_config.host == 'redis-server'
        assert config.redis_config.port == 6380
        assert config.redis_config.password == 'secret'
        assert config.redis_config.ssl is True
        assert config.redis_config.connection_pool_size == 20
        assert config.redis_config.stream_name == 'test_metrics'

        assert config.websocket_config.host == '127.0.0.1'
        assert config.websocket_config.port == 8081
        assert config.websocket_config.max_connections == 200
        assert config.websocket_config.heartbeat_interval == 60

        assert config.metrics_config.collection_interval_seconds == 10
        assert config.metrics_config.retention_days == 60
        assert config.metrics_config.high_frequency_metrics == ['cpu_usage', 'memory_usage']
        assert config.metrics_config.component_discovery_enabled is False
        assert config.metrics_config.performance_impact_limit == 0.02

    def test_load_from_file_not_found(self):
        """Test loading from non-existent file returns default config."""
        config = ObservatoryConfigLoader.load_from_file('nonexistent.yaml')

        assert isinstance(config, ObservatoryConfig)
        # Should have default values
        assert config.redis_config.host == 'localhost'
        assert config.redis_config.port == 6379
        assert config.websocket_config.port == 8080

    def test_load_from_file_invalid_yaml(self):
        """Test loading from invalid YAML file returns default config."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            temp_file = f.name

        try:
            config = ObservatoryConfigLoader.load_from_file(temp_file)
            assert isinstance(config, ObservatoryConfig)
            # Should have default values due to parsing error
            assert config.redis_config.host == 'localhost'
        finally:
            os.unlink(temp_file)

    def test_load_from_env_redis_config(self):
        """Test loading Redis configuration from environment variables."""
        env_vars = {
            'OBSERVATORY_REDIS_HOST': 'env-redis',
            'OBSERVATORY_REDIS_PORT': '6381',
            'OBSERVATORY_REDIS_PASSWORD': 'env-password',
            'OBSERVATORY_REDIS_SSL': 'true'
        }

        with patch.dict(os.environ, env_vars):
            config = ObservatoryConfigLoader.load_from_env()

            assert config.redis_config.host == 'env-redis'
            assert config.redis_config.port == 6381
            assert config.redis_config.password == 'env-password'
            assert config.redis_config.ssl is True

    def test_load_from_env_websocket_config(self):
        """Test loading WebSocket configuration from environment variables."""
        env_vars = {
            'OBSERVATORY_WEBSOCKET_HOST': '192.168.1.1',
            'OBSERVATORY_WEBSOCKET_PORT': '8082'
        }

        with patch.dict(os.environ, env_vars):
            config = ObservatoryConfigLoader.load_from_env()

            assert config.websocket_config.host == '192.168.1.1'
            assert config.websocket_config.port == 8082

    def test_load_from_env_metrics_config(self):
        """Test loading metrics configuration from environment variables."""
        env_vars = {
            'OBSERVATORY_METRICS_INTERVAL': '15',
            'OBSERVATORY_METRICS_RETENTION_DAYS': '45'
        }

        with patch.dict(os.environ, env_vars):
            config = ObservatoryConfigLoader.load_from_env()

            assert config.metrics_config.collection_interval_seconds == 15
            assert config.metrics_config.retention_days == 45

    def test_load_from_env_gamification_config(self):
        """Test loading gamification configuration from environment variables."""
        env_vars = {
            'OBSERVATORY_EMOJI_RAIN_ENABLED': 'false',
            'OBSERVATORY_ACHIEVEMENTS_ENABLED': 'true'
        }

        with patch.dict(os.environ, env_vars):
            config = ObservatoryConfigLoader.load_from_env()

            assert config.gamification_config.emoji_rain_enabled is False
            assert config.gamification_config.achievements_enabled is True

    def test_load_from_env_invalid_port(self):
        """Test handling of invalid port number in environment variables."""
        env_vars = {
            'OBSERVATORY_REDIS_PORT': 'invalid'
        }

        with patch.dict(os.environ, env_vars):
            config = ObservatoryConfigLoader.load_from_env()
            # Should use default port due to conversion error
            assert config.redis_config.port == 6379

    def test_build_config_from_dict_partial(self):
        """Test building config from partial dictionary."""
        partial_config = {
            'redis': {
                'host': 'partial-redis'
            },
            'websocket': {
                'port': 9000
            }
        }

        config = ObservatoryConfigLoader._build_config_from_dict(partial_config)

        # Should have specified values
        assert config.redis_config.host == 'partial-redis'
        assert config.websocket_config.port == 9000

        # Should have defaults for unspecified values
        assert config.redis_config.port == 6379  # default
        assert config.websocket_config.host == '0.0.0.0'  # default

    def test_build_config_from_dict_cost_tracking(self, sample_config_dict):
        """Test building cost tracking configuration from dictionary."""
        config = ObservatoryConfigLoader._build_config_from_dict(sample_config_dict)

        assert len(config.cost_config.provider_configs) == 2

        anthropic_config = config.cost_config.provider_configs['anthropic']
        assert anthropic_config.name == 'anthropic'
        assert anthropic_config.api_key_env_var == 'ANTHROPIC_API_KEY'
        assert anthropic_config.cost_per_1k_tokens['claude-3-opus'] == Decimal('15.0')
        assert anthropic_config.cost_per_1k_tokens['claude-3-sonnet'] == Decimal('3.0')
        assert anthropic_config.rate_limit_rpm == 100

        openai_config = config.cost_config.provider_configs['openai']
        assert openai_config.name == 'openai'
        assert openai_config.cost_per_1k_tokens['gpt-4'] == Decimal('30.0')

        assert config.cost_config.cost_alert_thresholds['daily_limit'] == Decimal('100.0')
        assert config.cost_config.cost_alert_thresholds['monthly_limit'] == Decimal('2000.0')
        assert config.cost_config.projection_window_days == 14
        assert config.cost_config.anomaly_detection_sensitivity == 0.9

    def test_build_config_from_dict_empty(self):
        """Test building config from empty dictionary."""
        config = ObservatoryConfigLoader._build_config_from_dict({})

        assert isinstance(config, ObservatoryConfig)
        # Should have all default values
        assert config.redis_config.host == 'localhost'
        assert config.websocket_config.port == 8080
        assert config.metrics_config.collection_interval_seconds == 5


class TestLoadObservatoryConfig:
    """Test the main load_observatory_config function."""

    def test_load_config_env_only(self):
        """Test loading configuration from environment variables only."""
        env_vars = {
            'OBSERVATORY_REDIS_HOST': 'env-only-redis',
            'OBSERVATORY_REDIS_PORT': '6382'
        }

        with patch.dict(os.environ, env_vars):
            config = load_observatory_config()

            assert config.redis_config.host == 'env-only-redis'
            assert config.redis_config.port == 6382

    def test_load_config_file_override(self, sample_yaml_config):
        """Test that file configuration overrides environment variables."""
        env_vars = {
            'OBSERVATORY_REDIS_HOST': 'env-redis',
            'OBSERVATORY_REDIS_PORT': '6383'
        }

        with patch.dict(os.environ, env_vars):
            config = load_observatory_config(sample_yaml_config)

            # File config should override environment
            assert config.redis_config.host == 'redis-server'  # from file
            assert config.redis_config.port == 6380  # from file

    def test_load_config_nonexistent_file(self):
        """Test loading with non-existent config file path."""
        env_vars = {
            'OBSERVATORY_REDIS_HOST': 'env-fallback-redis'
        }

        with patch.dict(os.environ, env_vars):
            config = load_observatory_config('nonexistent.yaml')

            # Should still use environment variables since file doesn't exist
            assert config.redis_config.host == 'localhost'  # default from non-existent file

    @patch('src.beast_mode.observatory.config.logger')
    def test_load_config_validation_warning(self, mock_logger, sample_yaml_config):
        """Test that validation warnings are logged."""
        # Mock the config validation to return False
        with patch.object(ObservatoryConfig, 'validate', return_value=False):
            config = load_observatory_config(sample_yaml_config)

            mock_logger.warning.assert_called_with(
                "Configuration validation failed, using defaults where possible"
            )
            mock_logger.info.assert_called_with(
                "Observatory configuration loaded successfully"
            )


class TestConfigurationValidation:
    """Test configuration validation scenarios."""

    def test_config_with_missing_required_fields(self):
        """Test configuration behavior with missing required fields."""
        minimal_config = {
            'redis': {
                'host': 'minimal-redis'
                # Missing other fields
            }
        }

        config = ObservatoryConfigLoader._build_config_from_dict(minimal_config)

        # Should fill in defaults for missing fields
        assert config.redis_config.host == 'minimal-redis'
        assert config.redis_config.port == 6379  # default
        assert config.redis_config.password is None  # default
        assert config.redis_config.ssl is False  # default

    def test_config_edge_case_values(self):
        """Test configuration with edge case values."""
        edge_config = {
            'redis': {
                'host': '',  # Empty string
                'port': 0,   # Zero port
                'connection_pool_size': -1  # Negative value
            },
            'websocket': {
                'max_connections': 0,
                'heartbeat_interval': -1
            },
            'metrics': {
                'collection_interval_seconds': 0,
                'retention_days': -1,
                'performance_impact_limit': 2.0  # > 100%
            }
        }

        config = ObservatoryConfigLoader._build_config_from_dict(edge_config)

        # Should accept the values as specified (validation happens elsewhere)
        assert config.redis_config.host == ''
        assert config.redis_config.port == 0
        assert config.redis_config.connection_pool_size == -1
        assert config.websocket_config.max_connections == 0
        assert config.metrics_config.collection_interval_seconds == 0

    def test_config_type_coercion(self):
        """Test that configuration handles type coercion correctly."""
        type_config = {
            'redis': {
                'port': '6379',  # String that should be int
                'ssl': 'true'    # String that should be bool
            },
            'cost_tracking': {
                'providers': {
                    'test': {
                        'cost_per_1k_tokens': {
                            'model1': '5.50'  # String that should be Decimal
                        }
                    }
                }
            }
        }

        config = ObservatoryConfigLoader._build_config_from_dict(type_config)

        # String should be converted to int
        assert config.redis_config.port == 6379
        assert isinstance(config.redis_config.port, int)

        # String should be converted to Decimal
        test_provider = config.cost_config.provider_configs['test']
        assert test_provider.cost_per_1k_tokens['model1'] == Decimal('5.50')
        assert isinstance(test_provider.cost_per_1k_tokens['model1'], Decimal)


class TestConfigurationIntegration:
    """Integration tests for configuration loading and usage."""

    def test_full_config_integration(self, sample_yaml_config):
        """Test full configuration loading and all components."""
        config = load_observatory_config(sample_yaml_config)

        # Verify all major components are properly configured
        assert isinstance(config.redis_config, RedisConfig)
        assert isinstance(config.websocket_config, WebSocketConfig)
        assert isinstance(config.metrics_config, MetricsConfig)
        assert isinstance(config.cost_config, CostTrackingConfig)
        assert isinstance(config.gamification_config, GamificationConfig)

        # Verify complex nested configurations
        assert len(config.cost_config.provider_configs) == 2
        assert 'anthropic' in config.cost_config.provider_configs
        assert 'openai' in config.cost_config.provider_configs

        # Verify Decimal precision is maintained
        anthropic_opus_cost = config.cost_config.provider_configs['anthropic'].cost_per_1k_tokens['claude-3-opus']
        assert isinstance(anthropic_opus_cost, Decimal)
        assert anthropic_opus_cost == Decimal('15.0')

    def test_config_serialization_roundtrip(self, sample_config_dict):
        """Test that config can be loaded and would serialize back correctly."""
        original_config = ObservatoryConfigLoader._build_config_from_dict(sample_config_dict)

        # Verify that all the data is preserved correctly
        assert original_config.redis_config.host == sample_config_dict['redis']['host']
        assert original_config.redis_config.port == sample_config_dict['redis']['port']

        # Verify nested provider configurations
        expected_providers = sample_config_dict['cost_tracking']['providers']
        actual_providers = original_config.cost_config.provider_configs

        for provider_name in expected_providers.keys():
            assert provider_name in actual_providers
            expected_costs = expected_providers[provider_name]['cost_per_1k_tokens']
            actual_costs = actual_providers[provider_name].cost_per_1k_tokens

            for model, cost in expected_costs.items():
                assert actual_costs[model] == Decimal(str(cost))

    def test_config_environment_override_precedence(self, sample_yaml_config):
        """Test the precedence of configuration sources."""
        # Set environment variables that should be overridden by file
        env_vars = {
            'OBSERVATORY_REDIS_HOST': 'should-be-overridden',
            'OBSERVATORY_REDIS_PORT': '9999'
        }

        with patch.dict(os.environ, env_vars):
            # Load config with file (should override env)
            file_config = load_observatory_config(sample_yaml_config)

            # Load config without file (should use env)
            env_config = load_observatory_config()

            # File should override environment
            assert file_config.redis_config.host == 'redis-server'  # from file
            assert file_config.redis_config.port == 6380  # from file

            # Environment should be used when no file
            assert env_config.redis_config.host == 'should-be-overridden'  # from env
            assert env_config.redis_config.port == 9999  # from env