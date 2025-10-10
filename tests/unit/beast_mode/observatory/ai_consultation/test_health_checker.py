"""
Unit tests for Health Checker implementation
"""

import pytest
import asyncio
from unittest.mock import patch, mock_open, MagicMock
import os
import tempfile

from src.beast_mode.observatory.ai_consultation.health_checker import (
    AIConsultationHealthChecker,
    HealthStatus,
    health_checker
)


class TestAIConsultationHealthChecker:
    """Test AIConsultationHealthChecker class"""
    
    @pytest.fixture
    def health_checker_instance(self):
        """Create a health checker instance for testing"""
        return AIConsultationHealthChecker()
    
    @pytest.mark.asyncio
    async def test_check_health_basic(self, health_checker_instance):
        """Test basic health check functionality"""
        result = await health_checker_instance.check_health()
        
        assert 'status' in result
        assert 'timestamp' in result
        assert 'uptime_seconds' in result
        assert 'checks' in result
        assert 'version' in result
        assert 'service' in result
        
        assert result['service'] == 'ai-consultation'
        assert result['version'] == '0.1.0'
        assert isinstance(result['uptime_seconds'], float)
        assert result['uptime_seconds'] >= 0
    
    @pytest.mark.asyncio
    async def test_check_health_caching(self, health_checker_instance):
        """Test health check result caching"""
        # First call
        result1 = await health_checker_instance.check_health()
        timestamp1 = result1['timestamp']
        
        # Second call immediately after should return cached result
        result2 = await health_checker_instance.check_health()
        timestamp2 = result2['timestamp']
        
        assert timestamp1 == timestamp2  # Should be cached
    
    @pytest.mark.asyncio
    async def test_check_readiness(self, health_checker_instance):
        """Test readiness check"""
        result = await health_checker_instance.check_readiness()
        
        assert 'ready' in result
        assert 'timestamp' in result
        assert 'checks' in result
        
        assert isinstance(result['ready'], bool)
        assert 'feature_flags_loaded' in result['checks']
        assert 'circuit_breakers_initialized' in result['checks']
        assert 'configuration_valid' in result['checks']
        assert 'dependencies_available' in result['checks']
    
    @pytest.mark.asyncio
    async def test_get_metrics(self, health_checker_instance):
        """Test metrics collection"""
        result = await health_checker_instance.get_metrics()
        
        assert 'uptime_seconds' in result
        assert 'start_time' in result
        assert 'circuit_breakers' in result
        assert 'feature_flags' in result
        assert 'system' in result
        
        # Check circuit breaker metrics
        cb_metrics = result['circuit_breakers']
        assert 'total' in cb_metrics
        assert 'open' in cb_metrics
        assert 'open_breakers' in cb_metrics
        assert 'stats' in cb_metrics
        
        # Check feature flag metrics
        ff_metrics = result['feature_flags']
        assert 'total' in ff_metrics
        assert 'enabled' in ff_metrics
        assert 'disabled' in ff_metrics
        assert 'flags' in ff_metrics
        
        # Check system metrics
        sys_metrics = result['system']
        assert 'cpu_percent' in sys_metrics
        assert 'memory_percent' in sys_metrics
        assert 'disk_percent' in sys_metrics
        assert 'process_count' in sys_metrics
    
    @pytest.mark.asyncio
    async def test_system_health_check(self, health_checker_instance):
        """Test system health check"""
        result = await health_checker_instance._check_system_health()
        
        assert result['status'] == HealthStatus.HEALTHY.value
        assert 'message' in result
        assert 'response_time_ms' in result
        assert isinstance(result['response_time_ms'], float)
        assert result['response_time_ms'] >= 0
    
    @pytest.mark.asyncio
    async def test_feature_flags_health_check(self, health_checker_instance):
        """Test feature flags health check"""
        result = await health_checker_instance._check_feature_flags()
        
        assert 'status' in result
        assert 'message' in result
        assert 'total_flags' in result
        assert 'test_flag_result' in result
        
        # Should be healthy since feature flags are initialized
        assert result['status'] == HealthStatus.HEALTHY.value
        assert isinstance(result['total_flags'], int)
        assert isinstance(result['test_flag_result'], bool)
    
    @pytest.mark.asyncio
    async def test_circuit_breakers_health_check(self, health_checker_instance):
        """Test circuit breakers health check"""
        result = await health_checker_instance._check_circuit_breakers()
        
        assert 'status' in result
        assert 'message' in result
        assert 'total_breakers' in result
        assert 'open_breakers' in result
        assert 'open_breaker_names' in result
        
        # Should be healthy since no breakers are open initially
        assert result['status'] == HealthStatus.HEALTHY.value
        assert result['total_breakers'] >= 0
        assert result['open_breakers'] == 0
        assert result['open_breaker_names'] == []
    
    @pytest.mark.asyncio
    async def test_file_system_health_check(self, health_checker_instance):
        """Test file system health check"""
        result = await health_checker_instance._check_file_system()
        
        assert 'status' in result
        assert 'message' in result
        
        # Should be healthy since we can write to /tmp
        assert result['status'] == HealthStatus.HEALTHY.value
    
    @pytest.mark.asyncio
    async def test_file_system_health_check_failure(self, health_checker_instance):
        """Test file system health check failure"""
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            result = await health_checker_instance._check_file_system()
            
            assert result['status'] == HealthStatus.UNHEALTHY.value
            assert 'error' in result
    
    @pytest.mark.asyncio
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    async def test_resource_usage_healthy(self, mock_disk, mock_memory, mock_cpu, health_checker_instance):
        """Test resource usage check when healthy"""
        # Mock healthy resource usage
        mock_cpu.return_value = 30.0
        mock_memory.return_value = MagicMock(percent=40.0, available=8*1024**3)
        mock_disk.return_value = MagicMock(percent=50.0, free=100*1024**3)
        
        result = await health_checker_instance._check_resource_usage()
        
        assert result['status'] == HealthStatus.HEALTHY.value
        assert result['cpu_percent'] == 30.0
        assert result['memory_percent'] == 40.0
        assert result['disk_percent'] == 50.0
    
    @pytest.mark.asyncio
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    async def test_resource_usage_degraded(self, mock_disk, mock_memory, mock_cpu, health_checker_instance):
        """Test resource usage check when degraded"""
        # Mock elevated resource usage
        mock_cpu.return_value = 80.0
        mock_memory.return_value = MagicMock(percent=75.0, available=2*1024**3)
        mock_disk.return_value = MagicMock(percent=85.0, free=10*1024**3)
        
        result = await health_checker_instance._check_resource_usage()
        
        assert result['status'] == HealthStatus.DEGRADED.value
        assert result['cpu_percent'] == 80.0
        assert result['memory_percent'] == 75.0
        assert result['disk_percent'] == 85.0
    
    @pytest.mark.asyncio
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    async def test_resource_usage_unhealthy(self, mock_disk, mock_memory, mock_cpu, health_checker_instance):
        """Test resource usage check when unhealthy"""
        # Mock high resource usage
        mock_cpu.return_value = 95.0
        mock_memory.return_value = MagicMock(percent=95.0, available=0.5*1024**3)
        mock_disk.return_value = MagicMock(percent=95.0, free=1*1024**3)
        
        result = await health_checker_instance._check_resource_usage()
        
        assert result['status'] == HealthStatus.UNHEALTHY.value
        assert result['cpu_percent'] == 95.0
        assert result['memory_percent'] == 95.0
        assert result['disk_percent'] == 95.0
    
    @pytest.mark.asyncio
    async def test_configuration_check_with_existing_config(self, health_checker_instance):
        """Test configuration check when config files exist"""
        with patch('os.path.exists', return_value=True):
            result = await health_checker_instance._check_configuration()
            
            assert result['status'] == HealthStatus.HEALTHY.value
            assert 'checks' in result
            assert result['checks']['feature_flags_config'] is True
    
    @pytest.mark.asyncio
    async def test_configuration_check_with_missing_config(self, health_checker_instance):
        """Test configuration check when config files are missing"""
        with patch('os.path.exists', return_value=False):
            result = await health_checker_instance._check_configuration()
            
            assert result['status'] == HealthStatus.DEGRADED.value
            assert 'checks' in result
            assert result['checks']['feature_flags_config'] is False
    
    @pytest.mark.asyncio
    async def test_determine_overall_status_all_healthy(self, health_checker_instance):
        """Test overall status determination when all checks are healthy"""
        health_checks = {
            'check1': {'status': HealthStatus.HEALTHY.value},
            'check2': {'status': HealthStatus.HEALTHY.value},
            'check3': {'status': HealthStatus.HEALTHY.value}
        }
        
        status = health_checker_instance._determine_overall_status(health_checks)
        assert status == HealthStatus.HEALTHY
    
    @pytest.mark.asyncio
    async def test_determine_overall_status_with_unhealthy(self, health_checker_instance):
        """Test overall status determination when some checks are unhealthy"""
        health_checks = {
            'check1': {'status': HealthStatus.HEALTHY.value},
            'check2': {'status': HealthStatus.UNHEALTHY.value},
            'check3': {'status': HealthStatus.HEALTHY.value}
        }
        
        status = health_checker_instance._determine_overall_status(health_checks)
        assert status == HealthStatus.UNHEALTHY
    
    @pytest.mark.asyncio
    async def test_determine_overall_status_with_degraded(self, health_checker_instance):
        """Test overall status determination when some checks are degraded"""
        health_checks = {
            'check1': {'status': HealthStatus.HEALTHY.value},
            'check2': {'status': HealthStatus.DEGRADED.value},
            'check3': {'status': HealthStatus.HEALTHY.value}
        }
        
        status = health_checker_instance._determine_overall_status(health_checks)
        assert status == HealthStatus.DEGRADED
    
    @pytest.mark.asyncio
    async def test_determine_overall_status_unknown(self, health_checker_instance):
        """Test overall status determination with unknown status"""
        health_checks = {
            'check1': {'status': HealthStatus.UNKNOWN.value},
            'check2': {'status': HealthStatus.UNKNOWN.value}
        }
        
        status = health_checker_instance._determine_overall_status(health_checks)
        assert status == HealthStatus.UNKNOWN


class TestGlobalHealthChecker:
    """Test global health checker instance"""
    
    @pytest.mark.asyncio
    async def test_global_health_checker_instance(self):
        """Test that global health checker instance works"""
        result = await health_checker.check_health()
        
        assert 'status' in result
        assert 'service' in result
        assert result['service'] == 'ai-consultation'
    
    @pytest.mark.asyncio
    async def test_global_health_checker_readiness(self):
        """Test global health checker readiness"""
        result = await health_checker.check_readiness()
        
        assert 'ready' in result
        assert 'checks' in result
    
    @pytest.mark.asyncio
    async def test_global_health_checker_metrics(self):
        """Test global health checker metrics"""
        result = await health_checker.get_metrics()
        
        assert 'uptime_seconds' in result
        assert 'circuit_breakers' in result
        assert 'feature_flags' in result
        assert 'system' in result


if __name__ == "__main__":
    pytest.main([__file__])