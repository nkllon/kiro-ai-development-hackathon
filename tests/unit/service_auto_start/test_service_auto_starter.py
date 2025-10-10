#!/usr/bin/env python3
"""
Unit tests for ServiceAutoStarter base class.
"""

import pytest
from unittest.mock import Mock, patch
from src.service_auto_start.core.service_auto_starter import (
    ServiceAutoStarter, 
    ServiceDefinition, 
    PlatformDetector,
    ServiceAutoStarterFactory
)


class MockServiceAutoStarter(ServiceAutoStarter):
    """Mock implementation for testing."""
    
    def generate_config(self, service):
        return {"mock": "config"}
    
    def install_config(self, service, config):
        return True
    
    def verify_autostart(self, service):
        return True
    
    def remove_autostart(self, service):
        return True
    
    def get_capabilities(self):
        return {"mock": True}
    
    def get_module_info(self):
        return {"name": "MockServiceAutoStarter", "version": "1.0.0"}
    
    def graceful_degradation(self, error):
        return {"status": "degraded", "error": str(error)}


class TestPlatformDetector:
    """Test platform detection functionality."""
    
    @patch('platform.system')
    def test_detect_macos(self, mock_system):
        mock_system.return_value = "Darwin"
        assert PlatformDetector.get_platform() == "macos"
    
    @patch('platform.system')
    @patch('os.path.exists')
    def test_detect_linux_with_systemd(self, mock_exists, mock_system):
        mock_system.return_value = "Linux"
        mock_exists.side_effect = lambda path: path in ["/bin/systemctl", "/usr/bin/systemctl"]
        assert PlatformDetector.get_platform() == "linux"
    
    @patch('platform.system')
    @patch('os.path.exists')
    def test_detect_docker_container(self, mock_exists, mock_system):
        mock_system.return_value = "Linux"
        mock_exists.side_effect = lambda path: path == "/.dockerenv"
        assert PlatformDetector.get_platform() == "docker"
    
    @patch('os.system')
    def test_has_docker_available(self, mock_system):
        mock_system.return_value = 0
        assert PlatformDetector.has_docker() is True
    
    @patch('os.system')
    def test_has_docker_unavailable(self, mock_system):
        mock_system.return_value = 1
        assert PlatformDetector.has_docker() is False


class TestServiceDefinition:
    """Test ServiceDefinition data class."""
    
    def test_create_basic_service(self):
        service = ServiceDefinition(
            name="test-service",
            command="python app.py",
            working_directory="/app"
        )
        assert service.name == "test-service"
        assert service.command == "python app.py"
        assert service.working_directory == "/app"
        assert service.dependencies == []
        assert service.restart_policy == "always"
    
    def test_create_service_with_dependencies(self):
        service = ServiceDefinition(
            name="web-service",
            command="python web.py",
            working_directory="/app",
            dependencies=["database", "redis"],
            health_check_url="http://localhost:8000/health"
        )
        assert service.dependencies == ["database", "redis"]
        assert service.health_check_url == "http://localhost:8000/health"


class TestServiceAutoStarter:
    """Test ServiceAutoStarter base class."""
    
    def test_initialization(self):
        starter = MockServiceAutoStarter()
        assert starter.platform in ["macos", "linux", "docker", "windows", "unknown"]
    
    def test_initialization_with_config(self):
        config = {"test": "value"}
        starter = MockServiceAutoStarter(config)
        assert starter._config == config
    
    def test_configure_service_success(self):
        starter = MockServiceAutoStarter()
        service = ServiceDefinition(
            name="test-service",
            command="python app.py",
            working_directory="/app"
        )
        
        result = starter.configure_service(service)
        assert result is True
    
    @patch.object(MockServiceAutoStarter, 'generate_config')
    def test_configure_service_config_failure(self, mock_generate):
        mock_generate.return_value = None
        
        starter = MockServiceAutoStarter()
        service = ServiceDefinition(
            name="test-service",
            command="python app.py",
            working_directory="/app"
        )
        
        result = starter.configure_service(service)
        assert result is False
    
    @patch.object(MockServiceAutoStarter, 'install_config')
    def test_configure_service_install_failure(self, mock_install):
        mock_install.return_value = False
        
        starter = MockServiceAutoStarter()
        service = ServiceDefinition(
            name="test-service",
            command="python app.py",
            working_directory="/app"
        )
        
        result = starter.configure_service(service)
        assert result is False
    
    @patch.object(MockServiceAutoStarter, 'verify_autostart')
    def test_configure_service_verify_failure(self, mock_verify):
        mock_verify.return_value = False
        
        starter = MockServiceAutoStarter()
        service = ServiceDefinition(
            name="test-service",
            command="python app.py",
            working_directory="/app"
        )
        
        result = starter.configure_service(service)
        assert result is False
    
    def test_get_health_status(self):
        starter = MockServiceAutoStarter()
        status = starter.get_health_status()
        
        assert status["status"] == "healthy"
        assert "platform" in status
        assert "capabilities" in status


class TestServiceAutoStarterFactory:
    """Test ServiceAutoStarterFactory."""
    
    @patch('src.service_auto_start.core.service_auto_starter.PlatformDetector.get_platform')
    def test_create_for_detected_platform(self, mock_get_platform):
        mock_get_platform.return_value = "macos"
        
        with pytest.raises(ImportError):  # Expected since platform adapters don't exist yet
            ServiceAutoStarterFactory.create()
    
    def test_create_for_unsupported_platform(self):
        with pytest.raises(ValueError, match="Unsupported platform"):
            ServiceAutoStarterFactory.create("unsupported")


if __name__ == "__main__":
    pytest.main([__file__])