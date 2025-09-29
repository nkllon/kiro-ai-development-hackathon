#!/usr/bin/env python3
"""
Comprehensive Tests for Deployment Automation
Task 7.2: Deployment Automation and Validation

This test suite covers:
- Deployment automation functionality
- Validation system testing
- Rollback system testing
- Integration testing
- Error handling and edge cases
"""

import asyncio
import json
import pytest
import tempfile
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from typing import Dict, List, Any

import aiohttp
import websockets

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.deploy_websocket_fix import (
    DeploymentAutomation, DeploymentConfig, DeploymentResult, 
    DeploymentStage, DeploymentStatus
)
from scripts.validate_deployment import (
    DeploymentValidator, ValidationResult, ValidationStatus, 
    ValidationSeverity, ValidationSuite
)
from scripts.rollback_deployment import (
    RollbackAutomation, RollbackPlan, RollbackStatus, 
    RollbackTrigger, RollbackMetrics, RollbackTriggerConfig
)


class TestDeploymentAutomation:
    """Test suite for deployment automation."""
    
    @pytest.fixture
    def temp_config_file(self):
        """Create temporary configuration file for testing."""
        config_data = {
            "environments": {
                "dev": {
                    "url": "http://localhost:8888",
                    "websocket_url": "ws://localhost:8888/ws",
                    "health_endpoint": "/health",
                    "tunnel_config": "test-config.yml",
                    "replicas": 1,
                    "expected_response_time_ms": 500
                },
                "staging": {
                    "url": "https://staging-test.nkllon.com",
                    "websocket_url": "wss://staging-test.nkllon.com/ws",
                    "health_endpoint": "/health",
                    "tunnel_config": "test-config-staging.yml",
                    "replicas": 2,
                    "expected_response_time_ms": 1000
                },
                "production": {
                    "url": "https://test.nkllon.com",
                    "websocket_url": "wss://test.nkllon.com/ws",
                    "health_endpoint": "/health",
                    "tunnel_config": "test-config.yml",
                    "replicas": 3,
                    "expected_response_time_ms": 1500
                }
            },
            "health_check_timeout": 300,
            "health_check_interval": 10,
            "max_health_check_retries": 30,
            "rollback_timeout": 180,
            "auto_rollback_threshold": 0.8,
            "zero_downtime": True,
            "max_parallel_deployments": 1,
            "deployment_timeout": 600,
            "validation_thresholds": {
                "max_latency_ms": 1000,
                "max_error_rate": 0.05,
                "min_throughput_msgs_per_sec": 1.0,
                "max_connection_failure_rate": 0.1,
                "min_health_score": 0.8,
                "max_response_time_ms": 2000
            },
            "rollback_triggers": {
                "health_threshold": {
                    "enabled": True,
                    "threshold": 0.7,
                    "check_interval": 30
                },
                "error_rate": {
                    "enabled": True,
                    "threshold": 0.1,
                    "check_interval": 60
                }
            },
            "backup_retention_days": 7,
            "generate_report": True,
            "alert_on_failure": True
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config_data, f)
            yield f.name
        
        # Cleanup
        Path(f.name).unlink(missing_ok=True)
    
    @pytest.fixture
    def deployment_automation(self, temp_config_file):
        """Create deployment automation instance for testing."""
        with patch('scripts.deploy_websocket_fix.TunnelConfigManager'):
            return DeploymentAutomation(temp_config_file)
    
    def test_deployment_automation_init(self, temp_config_file):
        """Test deployment automation initialization."""
        with patch('scripts.deploy_websocket_fix.TunnelConfigManager'):
            deployment = DeploymentAutomation(temp_config_file)
            
            assert deployment.config_path == Path(temp_config_file)
            assert "dev" in deployment.config.environments
            assert "staging" in deployment.config.environments
            assert "production" in deployment.config.environments
            assert deployment.config.zero_downtime is True
            assert deployment.config.auto_rollback_threshold == 0.8
    
    def test_get_deployment_stages(self, deployment_automation):
        """Test deployment stage determination."""
        # Test dev stage
        stages = deployment_automation._get_deployment_stages("dev")
        assert stages == ["dev"]
        
        # Test staging stage
        stages = deployment_automation._get_deployment_stages("staging")
        assert stages == ["dev", "staging"]
        
        # Test production stage
        stages = deployment_automation._get_deployment_stages("production")
        assert stages == ["dev", "staging", "production"]
    
    @pytest.mark.asyncio
    async def test_pre_deployment_validation(self, deployment_automation):
        """Test pre-deployment validation."""
        with patch.object(deployment_automation, '_check_observatory_server') as mock_server, \
             patch.object(deployment_automation, '_validate_tunnel_config') as mock_tunnel, \
             patch.object(deployment_automation, '_check_websocket_endpoints') as mock_websocket, \
             patch.object(deployment_automation, '_validate_deployment_config') as mock_config:
            
            # Mock successful checks
            mock_server.return_value = {"running": True}
            mock_tunnel.return_value = {"valid": True, "errors": []}
            mock_websocket.return_value = {"all_healthy": True}
            mock_config.return_value = {"valid": True, "errors": []}
            
            result = await deployment_automation._pre_deployment_validation()
            
            assert result["success"] is True
            assert len(result["errors"]) == 0
            assert "observatory_server" in result["checks"]
            assert "tunnel_config" in result["checks"]
            assert "websocket_endpoints" in result["checks"]
            assert "deployment_config" in result["checks"]
    
    @pytest.mark.asyncio
    async def test_pre_deployment_validation_failure(self, deployment_automation):
        """Test pre-deployment validation with failures."""
        with patch.object(deployment_automation, '_check_observatory_server') as mock_server, \
             patch.object(deployment_automation, '_validate_tunnel_config') as mock_tunnel, \
             patch.object(deployment_automation, '_check_websocket_endpoints') as mock_websocket, \
             patch.object(deployment_automation, '_validate_deployment_config') as mock_config:
            
            # Mock failed checks
            mock_server.return_value = {"running": False}
            mock_tunnel.return_value = {"valid": False, "errors": ["Invalid config"]}
            mock_websocket.return_value = {"all_healthy": True}
            mock_config.return_value = {"valid": True, "errors": []}
            
            result = await deployment_automation._pre_deployment_validation()
            
            assert result["success"] is False
            assert len(result["errors"]) > 0
            assert "Observatory server is not running" in result["errors"]
            assert "Invalid config" in result["errors"]
    
    @pytest.mark.asyncio
    async def test_deploy_to_stage_success(self, deployment_automation):
        """Test successful deployment to stage."""
        with patch.object(deployment_automation, '_apply_tunnel_config') as mock_apply, \
             patch.object(deployment_automation, '_perform_health_checks') as mock_health, \
             patch.object(deployment_automation, '_validate_websocket_functionality') as mock_websocket:
            
            # Mock successful operations
            mock_apply.return_value = {"success": True}
            mock_health.return_value = {"health_score": 0.9}
            mock_websocket.return_value = {"success": True, "errors": []}
            
            result = await deployment_automation._deploy_to_stage("dev")
            
            assert result.success is True
            assert result.status == DeploymentStatus.COMPLETED
            assert result.health_score == 0.9
            assert result.error_message is None
    
    @pytest.mark.asyncio
    async def test_deploy_to_stage_failure(self, deployment_automation):
        """Test failed deployment to stage."""
        with patch.object(deployment_automation, '_apply_tunnel_config') as mock_apply:
            
            # Mock failed tunnel configuration
            mock_apply.return_value = {"success": False, "error": "Config failed"}
            
            result = await deployment_automation._deploy_to_stage("dev")
            
            assert result.success is False
            assert result.status == DeploymentStatus.FAILED
            assert "Config failed" in result.error_message
    
    @pytest.mark.asyncio
    async def test_perform_health_checks(self, deployment_automation):
        """Test health check performance."""
        with patch.object(deployment_automation, '_check_http_health') as mock_http, \
             patch.object(deployment_automation, '_check_websocket_health') as mock_ws, \
             patch.object(deployment_automation, '_check_response_time') as mock_response:
            
            # Mock successful health checks
            mock_http.return_value = {"status": "healthy", "status_code": 200}
            mock_ws.return_value = {"status": "healthy"}
            mock_response.return_value = {"status": "healthy", "response_time_ms": 500}
            
            env_config = deployment_automation.config.environments["dev"]
            result = await deployment_automation._perform_health_checks("dev", env_config)
            
            assert result["health_score"] > 0
            assert result["overall_status"] == "healthy"
            assert "http" in result["checks"]
            assert "websocket" in result["checks"]
            assert "response_time" in result["checks"]
    
    @pytest.mark.asyncio
    async def test_calculate_health_score(self, deployment_automation):
        """Test health score calculation."""
        # Test all healthy
        checks = {
            "http": {"status": "healthy"},
            "websocket": {"status": "healthy"},
            "response_time": {"status": "healthy"}
        }
        score = deployment_automation._calculate_health_score(checks)
        assert score == 1.0
        
        # Test mixed results
        checks = {
            "http": {"status": "healthy"},
            "websocket": {"status": "slow"},
            "response_time": {"status": "unhealthy"}
        }
        score = deployment_automation._calculate_health_score(checks)
        assert score == 0.5  # (1.0 + 0.5 + 0.0) / 3
        
        # Test empty checks
        score = deployment_automation._calculate_health_score({})
        assert score == 0.0
    
    @pytest.mark.asyncio
    async def test_validate_websocket_functionality(self, deployment_automation):
        """Test WebSocket functionality validation."""
        with patch('websockets.connect') as mock_connect:
            # Mock successful WebSocket connection
            mock_websocket = AsyncMock()
            mock_websocket.ping = AsyncMock()
            mock_websocket.send = AsyncMock()
            mock_connect.return_value.__aenter__.return_value = mock_websocket
            
            env_config = deployment_automation.config.environments["dev"]
            result = await deployment_automation._validate_websocket_functionality("dev", env_config)
            
            assert result["success"] is True
            assert len(result["errors"]) == 0
            assert len(result["endpoints"]) == 4  # All WebSocket endpoints
    
    @pytest.mark.asyncio
    async def test_rollback_deployment(self, deployment_automation):
        """Test deployment rollback."""
        # Create mock deployment results
        mock_results = [
            DeploymentResult(
                stage="dev",
                status=DeploymentStatus.COMPLETED,
                start_time=datetime.now(),
                end_time=datetime.now(),
                success=True
            )
        ]
        
        with patch.object(deployment_automation.tunnel_manager, 'get_version_history') as mock_history, \
             patch.object(deployment_automation.tunnel_manager, 'rollback_config') as mock_rollback:
            
            # Mock version history
            mock_version = Mock()
            mock_version.version_id = "test-version"
            mock_version.description = "Backup before configuration change"
            mock_history.return_value = [mock_version]
            
            # Mock successful rollback
            mock_rollback.return_value = True, "Rollback successful"
            
            result = await deployment_automation._rollback_deployment(mock_results)
            
            assert result["success"] is True
            assert len(result["stages_rolled_back"]) == 1
            assert "dev" in result["stages_rolled_back"]
    
    @pytest.mark.asyncio
    async def test_backup_current_config(self, deployment_automation):
        """Test configuration backup."""
        with patch.object(deployment_automation.tunnel_manager, 'backup_current_config') as mock_backup:
            mock_backup.return_value = "backup-123"
            
            result = await deployment_automation._backup_current_config()
            
            assert result["success"] is True
            assert result["backup_id"] == "backup-123"
    
    @pytest.mark.asyncio
    async def test_check_observatory_server(self, deployment_automation):
        """Test observatory server check."""
        with patch('aiohttp.ClientSession') as mock_session:
            # Mock successful response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            result = await deployment_automation._check_observatory_server()
            
            assert result["running"] is True
            assert result["status_code"] == 200
    
    def test_validate_deployment_config(self, deployment_automation):
        """Test deployment configuration validation."""
        result = deployment_automation._validate_deployment_config()
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    @pytest.mark.asyncio
    async def test_generate_deployment_report(self, deployment_automation):
        """Test deployment report generation."""
        # Create mock deployment results
        mock_results = [
            DeploymentResult(
                stage="dev",
                status=DeploymentStatus.COMPLETED,
                start_time=datetime.now(),
                end_time=datetime.now(),
                success=True,
                health_score=0.9
            ),
            DeploymentResult(
                stage="staging",
                status=DeploymentStatus.COMPLETED,
                start_time=datetime.now(),
                end_time=datetime.now(),
                success=True,
                health_score=0.85
            )
        ]
        
        report = await deployment_automation._generate_deployment_report(mock_results)
        
        assert report["overall_success"] is True
        assert report["summary"]["total_stages"] == 2
        assert report["summary"]["successful_stages"] == 2
        assert report["summary"]["failed_stages"] == 0
        assert len(report["stages"]) == 2


class TestDeploymentValidator:
    """Test suite for deployment validator."""
    
    @pytest.fixture
    def temp_config_file(self):
        """Create temporary configuration file for testing."""
        config_data = {
            "environments": {
                "dev": {
                    "url": "http://localhost:8888",
                    "websocket_url": "ws://localhost:8888/ws",
                    "health_endpoint": "/health",
                    "expected_response_time_ms": 500
                }
            },
            "validation_thresholds": {
                "max_latency_ms": 1000,
                "max_error_rate": 0.05,
                "min_throughput_msgs_per_sec": 1.0,
                "max_connection_failure_rate": 0.1
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config_data, f)
            yield f.name
        
        Path(f.name).unlink(missing_ok=True)
    
    @pytest.fixture
    def deployment_validator(self, temp_config_file):
        """Create deployment validator instance for testing."""
        with patch('scripts.validate_deployment.TunnelConfigManager'):
            return DeploymentValidator(temp_config_file)
    
    @pytest.mark.asyncio
    async def test_validate_deployment(self, deployment_validator):
        """Test complete deployment validation."""
        with patch.object(deployment_validator, '_validate_environment') as mock_env, \
             patch.object(deployment_validator, '_validate_cross_environment') as mock_cross, \
             patch.object(deployment_validator, '_validate_configuration') as mock_config, \
             patch.object(deployment_validator, '_validate_performance') as mock_perf, \
             patch.object(deployment_validator, '_validate_security') as mock_security:
            
            # Mock validation results
            mock_env.return_value = [
                ValidationResult("test_check", ValidationStatus.PASSED, ValidationSeverity.HIGH, "Test passed")
            ]
            mock_cross.return_value = []
            mock_config.return_value = []
            mock_perf.return_value = []
            mock_security.return_value = []
            
            suite = await deployment_validator.validate_deployment("dev")
            
            assert suite.suite_name == "deployment_validation_dev"
            assert suite.overall_status == ValidationStatus.PASSED
            assert len(suite.results) == 1
    
    @pytest.mark.asyncio
    async def test_validate_environment(self, deployment_validator):
        """Test environment validation."""
        with patch.object(deployment_validator, '_validate_http_health') as mock_http, \
             patch.object(deployment_validator, '_validate_websocket_health') as mock_ws, \
             patch.object(deployment_validator, '_validate_response_time') as mock_response, \
             patch.object(deployment_validator, '_validate_websocket_endpoints') as mock_endpoints, \
             patch.object(deployment_validator, '_validate_tunnel_configuration') as mock_tunnel:
            
            # Mock successful validations
            mock_http.return_value = ValidationResult("http_health", ValidationStatus.PASSED, ValidationSeverity.HIGH, "HTTP healthy")
            mock_ws.return_value = ValidationResult("websocket_health", ValidationStatus.PASSED, ValidationSeverity.HIGH, "WebSocket healthy")
            mock_response.return_value = ValidationResult("response_time", ValidationStatus.PASSED, ValidationSeverity.MEDIUM, "Response time OK")
            mock_endpoints.return_value = ValidationResult("websocket_endpoints", ValidationStatus.PASSED, ValidationSeverity.HIGH, "All endpoints healthy")
            mock_tunnel.return_value = ValidationResult("tunnel_config", ValidationStatus.PASSED, ValidationSeverity.HIGH, "Tunnel config valid")
            
            results = await deployment_validator._validate_environment("dev")
            
            assert len(results) == 5
            assert all(r.status == ValidationStatus.PASSED for r in results)
    
    @pytest.mark.asyncio
    async def test_validate_http_health(self, deployment_validator):
        """Test HTTP health validation."""
        with patch('aiohttp.ClientSession') as mock_session:
            # Mock successful response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            env_config = deployment_validator.config["environments"]["dev"]
            result = await deployment_validator._validate_http_health("dev", env_config)
            
            assert result.status == ValidationStatus.PASSED
            assert result.severity == ValidationSeverity.HIGH
            assert "HTTP health check passed" in result.message
    
    @pytest.mark.asyncio
    async def test_validate_websocket_health(self, deployment_validator):
        """Test WebSocket health validation."""
        with patch('websockets.connect') as mock_connect:
            # Mock successful WebSocket connection
            mock_websocket = AsyncMock()
            mock_websocket.ping = AsyncMock()
            mock_websocket.send = AsyncMock()
            mock_connect.return_value.__aenter__.return_value = mock_websocket
            
            env_config = deployment_validator.config["environments"]["dev"]
            result = await deployment_validator._validate_websocket_health("dev", env_config)
            
            assert result.status == ValidationStatus.PASSED
            assert result.severity == ValidationSeverity.HIGH
            assert "WebSocket health check passed" in result.message
    
    @pytest.mark.asyncio
    async def test_validate_response_time(self, deployment_validator):
        """Test response time validation."""
        with patch('aiohttp.ClientSession') as mock_session:
            # Mock response with good timing
            mock_response = AsyncMock()
            mock_response.status = 200
            
            async def mock_get(*args, **kwargs):
                await asyncio.sleep(0.1)  # Simulate 100ms response
                return mock_response
            
            mock_session.return_value.__aenter__.return_value.get = mock_get
            
            env_config = deployment_validator.config["environments"]["dev"]
            result = await deployment_validator._validate_response_time("dev", env_config)
            
            assert result.status == ValidationStatus.PASSED
            assert result.severity == ValidationSeverity.MEDIUM
    
    @pytest.mark.asyncio
    async def test_validate_websocket_endpoints(self, deployment_validator):
        """Test WebSocket endpoints validation."""
        with patch('websockets.connect') as mock_connect:
            # Mock successful WebSocket connections
            mock_websocket = AsyncMock()
            mock_websocket.ping = AsyncMock()
            mock_websocket.send = AsyncMock()
            mock_connect.return_value.__aenter__.return_value = mock_websocket
            
            env_config = deployment_validator.config["environments"]["dev"]
            result = await deployment_validator._validate_websocket_endpoints("dev", env_config)
            
            assert result.status == ValidationStatus.PASSED
            assert result.severity == ValidationSeverity.HIGH
            assert "All WebSocket endpoints healthy" in result.message
    
    def test_calculate_overall_status(self, deployment_validator):
        """Test overall status calculation."""
        # Test all passed
        results = [
            ValidationResult("test1", ValidationStatus.PASSED, ValidationSeverity.HIGH, "Test 1"),
            ValidationResult("test2", ValidationStatus.PASSED, ValidationSeverity.MEDIUM, "Test 2")
        ]
        status = deployment_validator._calculate_overall_status(results)
        assert status == ValidationStatus.PASSED
        
        # Test with failures
        results = [
            ValidationResult("test1", ValidationStatus.PASSED, ValidationSeverity.HIGH, "Test 1"),
            ValidationResult("test2", ValidationStatus.FAILED, ValidationSeverity.CRITICAL, "Test 2")
        ]
        status = deployment_validator._calculate_overall_status(results)
        assert status == ValidationStatus.FAILED
        
        # Test with warnings
        results = [
            ValidationResult("test1", ValidationStatus.PASSED, ValidationSeverity.HIGH, "Test 1"),
            ValidationResult("test2", ValidationStatus.WARNING, ValidationSeverity.MEDIUM, "Test 2")
        ]
        status = deployment_validator._calculate_overall_status(results)
        assert status == ValidationStatus.WARNING
    
    def test_generate_summary(self, deployment_validator):
        """Test summary generation."""
        results = [
            ValidationResult("test1", ValidationStatus.PASSED, ValidationSeverity.HIGH, "Test 1", execution_time_ms=100),
            ValidationResult("test2", ValidationStatus.FAILED, ValidationSeverity.CRITICAL, "Test 2", execution_time_ms=200),
            ValidationResult("test3", ValidationStatus.WARNING, ValidationSeverity.MEDIUM, "Test 3", execution_time_ms=150)
        ]
        
        summary = deployment_validator._generate_summary(results)
        
        assert summary["total_checks"] == 3
        assert summary["passed_checks"] == 1
        assert summary["failed_checks"] == 1
        assert summary["warning_checks"] == 1
        assert summary["critical_checks"] == 1
        assert summary["high_checks"] == 1
        assert summary["medium_checks"] == 1
        assert summary["average_execution_time_ms"] == 150.0
        assert summary["success_rate"] == 33.3


class TestRollbackAutomation:
    """Test suite for rollback automation."""
    
    @pytest.fixture
    def temp_config_file(self):
        """Create temporary configuration file for testing."""
        config_data = {
            "environments": {
                "dev": {
                    "url": "http://localhost:8888",
                    "websocket_url": "ws://localhost:8888/ws",
                    "health_endpoint": "/health"
                }
            },
            "rollback_triggers": {
                "health_threshold": {
                    "enabled": True,
                    "threshold": 0.7,
                    "check_interval": 30,
                    "cooldown_period": 300
                },
                "error_rate": {
                    "enabled": True,
                    "threshold": 0.1,
                    "check_interval": 60,
                    "cooldown_period": 300
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config_data, f)
            yield f.name
        
        Path(f.name).unlink(missing_ok=True)
    
    @pytest.fixture
    def rollback_automation(self, temp_config_file):
        """Create rollback automation instance for testing."""
        with patch('scripts.rollback_deployment.TunnelConfigManager'):
            return RollbackAutomation(temp_config_file)
    
    def test_rollback_automation_init(self, temp_config_file):
        """Test rollback automation initialization."""
        with patch('scripts.rollback_deployment.TunnelConfigManager'):
            rollback = RollbackAutomation(temp_config_file)
            
            assert rollback.config_path == Path(temp_config_file)
            assert "dev" in rollback.config["environments"]
            assert len(rollback.trigger_configs) == 2
            assert rollback.trigger_configs["health_threshold"].enabled is True
            assert rollback.trigger_configs["error_rate"].enabled is True
    
    @pytest.mark.asyncio
    async def test_collect_metrics(self, rollback_automation):
        """Test metrics collection."""
        with patch.object(rollback_automation, '_calculate_health_score') as mock_health, \
             patch.object(rollback_automation, '_calculate_error_rate') as mock_error, \
             patch.object(rollback_automation, '_calculate_latency') as mock_latency, \
             patch.object(rollback_automation, '_calculate_connection_failure_rate') as mock_connection:
            
            # Mock metrics
            mock_health.return_value = 0.9
            mock_error.return_value = 0.05
            mock_latency.return_value = 500.0
            mock_connection.return_value = 0.02
            
            metrics = await rollback_automation._collect_metrics("dev")
            
            assert metrics.health_score == 0.9
            assert metrics.error_rate == 0.05
            assert metrics.latency_ms == 500.0
            assert metrics.connection_failure_rate == 0.02
            assert metrics.environment == "dev"
    
    @pytest.mark.asyncio
    async def test_evaluate_trigger_health_threshold(self, rollback_automation):
        """Test health threshold trigger evaluation."""
        trigger_config = RollbackTriggerConfig(enabled=True, threshold=0.7, check_interval=30)
        metrics = RollbackMetrics(
            health_score=0.5,  # Below threshold
            error_rate=0.05,
            latency_ms=500.0,
            connection_failure_rate=0.02,
            timestamp=datetime.now(),
            environment="dev"
        )
        
        should_rollback, reason = await rollback_automation._evaluate_trigger(
            "health_threshold", trigger_config, metrics
        )
        
        assert should_rollback is True
        assert "Health score 0.50 below threshold 0.7" in reason
    
    @pytest.mark.asyncio
    async def test_evaluate_trigger_error_rate(self, rollback_automation):
        """Test error rate trigger evaluation."""
        trigger_config = RollbackTriggerConfig(enabled=True, threshold=0.1, check_interval=60)
        metrics = RollbackMetrics(
            health_score=0.9,
            error_rate=0.15,  # Above threshold
            latency_ms=500.0,
            connection_failure_rate=0.02,
            timestamp=datetime.now(),
            environment="dev"
        )
        
        should_rollback, reason = await rollback_automation._evaluate_trigger(
            "error_rate", trigger_config, metrics
        )
        
        assert should_rollback is True
        assert "Error rate 0.15 above threshold 0.1" in reason
    
    @pytest.mark.asyncio
    async def test_manual_rollback(self, rollback_automation):
        """Test manual rollback."""
        with patch.object(rollback_automation.tunnel_manager, 'get_version_history') as mock_history, \
             patch.object(rollback_automation, '_execute_rollback') as mock_execute:
            
            # Mock version history
            mock_version = Mock()
            mock_version.version_id = "test-version"
            mock_history.return_value = [mock_version]
            
            # Mock successful rollback execution
            mock_execute.return_value = {
                "success": True,
                "rollback_id": "manual-123",
                "target_version": "test-version"
            }
            
            result = await rollback_automation.manual_rollback("dev", "test-version", "Test rollback")
            
            assert result["success"] is True
            assert result["rollback_id"] == "manual-123"
    
    @pytest.mark.asyncio
    async def test_emergency_rollback(self, rollback_automation):
        """Test emergency rollback."""
        with patch.object(rollback_automation.tunnel_manager, 'get_version_history') as mock_history, \
             patch.object(rollback_automation, '_execute_rollback') as mock_execute:
            
            # Mock version history with stable version
            mock_current = Mock()
            mock_current.version_id = "current-version"
            
            mock_stable = Mock()
            mock_stable.version_id = "stable-version"
            mock_stable.description = "Backup before configuration change"
            
            mock_history.return_value = [mock_current, mock_stable]
            
            # Mock successful rollback execution
            mock_execute.return_value = {
                "success": True,
                "rollback_id": "emergency-123",
                "target_version": "stable-version"
            }
            
            result = await rollback_automation.emergency_rollback("dev", "Emergency test")
            
            assert result["success"] is True
            assert result["rollback_id"] == "emergency-123"
    
    @pytest.mark.asyncio
    async def test_execute_rollback(self, rollback_automation):
        """Test rollback execution."""
        plan = RollbackPlan(
            rollback_id="test-rollback",
            trigger=RollbackTrigger.MANUAL,
            target_version="target-version",
            current_version="current-version",
            environment="dev",
            reason="Test rollback",
            created_at=datetime.now()
        )
        
        with patch.object(rollback_automation.tunnel_manager, 'rollback_config') as mock_rollback, \
             patch.object(rollback_automation, '_verify_rollback') as mock_verify:
            
            # Mock successful rollback
            mock_rollback.return_value = True, "Rollback successful"
            mock_verify.return_value = {"success": True, "checks": {}}
            
            result = await rollback_automation._execute_rollback(plan)
            
            assert result["success"] is True
            assert result["rollback_id"] == "test-rollback"
            assert result["target_version"] == "target-version"
    
    @pytest.mark.asyncio
    async def test_verify_rollback(self, rollback_automation):
        """Test rollback verification."""
        plan = RollbackPlan(
            rollback_id="test-rollback",
            trigger=RollbackTrigger.MANUAL,
            target_version="target-version",
            current_version="current-version",
            environment="dev",
            reason="Test rollback",
            created_at=datetime.now()
        )
        
        with patch.object(rollback_automation, '_verify_http_health') as mock_http, \
             patch.object(rollback_automation, '_verify_websocket_health') as mock_ws, \
             patch.object(rollback_automation, '_verify_tunnel_config') as mock_tunnel:
            
            # Mock successful verifications
            mock_http.return_value = {"success": True, "status_code": 200}
            mock_ws.return_value = {"success": True}
            mock_tunnel.return_value = {"success": True, "validation_status": "valid"}
            
            result = await rollback_automation._verify_rollback(plan)
            
            assert result["success"] is True
            assert len(result["checks"]) == 3
            assert len(result["errors"]) == 0
    
    def test_get_rollback_status(self, rollback_automation):
        """Test rollback status retrieval."""
        # Test general status
        status = rollback_automation.get_rollback_status()
        
        assert "active_rollbacks" in status
        assert "total_rollbacks" in status
        assert "monitoring_active" in status
        assert "triggers_enabled" in status
    
    def test_get_rollback_history(self, rollback_automation):
        """Test rollback history retrieval."""
        # Add some mock rollbacks to history
        mock_rollback = RollbackPlan(
            rollback_id="test-1",
            trigger=RollbackTrigger.MANUAL,
            target_version="target-1",
            current_version="current-1",
            environment="dev",
            reason="Test 1",
            created_at=datetime.now(),
            status=RollbackStatus.COMPLETED
        )
        rollback_automation.rollback_history.append(mock_rollback)
        
        history = rollback_automation.get_rollback_history()
        
        assert len(history) == 1
        assert history[0]["rollback_id"] == "test-1"
        assert history[0]["status"] == "completed"
    
    def test_get_available_versions(self, rollback_automation):
        """Test available versions retrieval."""
        with patch.object(rollback_automation.tunnel_manager, 'get_version_history') as mock_history:
            # Mock version history
            mock_version = Mock()
            mock_version.version_id = "test-version"
            mock_version.description = "Backup before configuration change"
            mock_version.created_at = datetime.now()
            mock_history.return_value = [mock_version]
            
            versions = rollback_automation.get_available_versions()
            
            assert len(versions) == 1
            assert versions[0]["version_id"] == "test-version"
            assert versions[0]["is_stable"] is True


class TestIntegration:
    """Integration tests for deployment automation."""
    
    @pytest.fixture
    def temp_config_file(self):
        """Create temporary configuration file for integration testing."""
        config_data = {
            "environments": {
                "dev": {
                    "url": "http://localhost:8888",
                    "websocket_url": "ws://localhost:8888/ws",
                    "health_endpoint": "/health",
                    "expected_response_time_ms": 500
                }
            },
            "health_check_timeout": 300,
            "rollback_timeout": 180,
            "auto_rollback_threshold": 0.8,
            "validation_thresholds": {
                "max_latency_ms": 1000,
                "max_error_rate": 0.05
            },
            "rollback_triggers": {
                "health_threshold": {
                    "enabled": True,
                    "threshold": 0.7,
                    "check_interval": 30
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config_data, f)
            yield f.name
        
        Path(f.name).unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_full_deployment_workflow(self, temp_config_file):
        """Test complete deployment workflow."""
        with patch('scripts.deploy_websocket_fix.TunnelConfigManager') as mock_tunnel_manager, \
             patch('scripts.deploy_websocket_fix.aiohttp.ClientSession') as mock_session, \
             patch('scripts.deploy_websocket_fix.websockets.connect') as mock_websockets:
            
            # Mock tunnel manager
            mock_tunnel_instance = Mock()
            mock_tunnel_instance.generate_websocket_config.return_value = {"tunnel": "test"}
            mock_tunnel_instance.validate_config.return_value = Mock(is_valid=True, errors=[])
            mock_tunnel_instance.apply_config.return_value = True
            mock_tunnel_instance.backup_current_config.return_value = "backup-123"
            mock_tunnel_instance.get_version_history.return_value = [
                Mock(version_id="current", description="Current"),
                Mock(version_id="backup", description="Backup before configuration change")
            ]
            mock_tunnel_instance.rollback_config.return_value = True, "Rollback successful"
            mock_tunnel_manager.return_value = mock_tunnel_instance
            
            # Mock HTTP responses
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            # Mock WebSocket connections
            mock_websocket = AsyncMock()
            mock_websocket.ping = AsyncMock()
            mock_websocket.send = AsyncMock()
            mock_websockets.return_value.__aenter__.return_value = mock_websocket
            
            # Initialize deployment automation
            deployment = DeploymentAutomation(temp_config_file)
            
            # Execute deployment
            result = await deployment.deploy_websocket_fix("dev", force_deploy=True)
            
            assert result["overall_success"] is True
            assert result["summary"]["total_stages"] == 1
            assert result["summary"]["successful_stages"] == 1
    
    @pytest.mark.asyncio
    async def test_deployment_with_rollback(self, temp_config_file):
        """Test deployment with automatic rollback."""
        with patch('scripts.deploy_websocket_fix.TunnelConfigManager') as mock_tunnel_manager, \
             patch('scripts.deploy_websocket_fix.aiohttp.ClientSession') as mock_session, \
             patch('scripts.deploy_websocket_fix.websockets.connect') as mock_websockets:
            
            # Mock tunnel manager
            mock_tunnel_instance = Mock()
            mock_tunnel_instance.generate_websocket_config.return_value = {"tunnel": "test"}
            mock_tunnel_instance.validate_config.return_value = Mock(is_valid=True, errors=[])
            mock_tunnel_instance.apply_config.return_value = True
            mock_tunnel_instance.backup_current_config.return_value = "backup-123"
            mock_tunnel_instance.get_version_history.return_value = [
                Mock(version_id="current", description="Current"),
                Mock(version_id="backup", description="Backup before configuration change")
            ]
            mock_tunnel_instance.rollback_config.return_value = True, "Rollback successful"
            mock_tunnel_manager.return_value = mock_tunnel_instance
            
            # Mock HTTP responses (simulate failure)
            mock_response = AsyncMock()
            mock_response.status = 500  # Simulate server error
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            # Mock WebSocket connections (simulate failure)
            mock_websockets.side_effect = Exception("Connection failed")
            
            # Initialize deployment automation
            deployment = DeploymentAutomation(temp_config_file)
            
            # Execute deployment (should trigger rollback)
            result = await deployment.deploy_websocket_fix("dev", force_deploy=True)
            
            # Should have attempted rollback due to failures
            assert result["overall_success"] is False
            assert result["summary"]["failed_stages"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])