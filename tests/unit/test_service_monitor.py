"""
RDI Enhanced Test Module

Requirements Traceability:

Enhanced: 2025-09-14T06:30:15.485130
"""






import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
import subprocess

from beast_mode.deployment.config_manager import ConfigManager, DeploymentConfig, MonitoringConfig
from beast_mode.deployment.service_monitor import (
    ServiceMonitor, MonitoredService, ServiceStatus, ServiceMetrics
)


class TestServiceMonitor(ReflectiveModule):
    """Test service monitor functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        config = DeploymentConfig(
            environment="test",
            redis=Mock(),
            agent=Mock(),
            monitoring=MonitoringConfig(health_check_interval=1)  # Fast for testing
        )
        self.monitor = ServiceMonitor(config)
    
    def teardown_method(self):
        """Cleanup test environment"""
        self.monitor.stop_monitoring()
        self.monitor.cleanup()
    
    def test_add_service(self):
        """Test adding service to monitor"""
        service = MonitoredService(
            name="test_service",
            command=["echo", "test"],
            working_directory="/tmp",
            environment={}
        )
        
        self.monitor.add_service(service)
        
        assert "test_service" in self.monitor.services
        assert self.monitor.services["test_service"] == service
    
    def test_remove_service(self):
        """Test removing service from monitor"""
        service = MonitoredService(
            name="test_service",
            command=["echo", "test"],
            working_directory="/tmp",
            environment={}
        )
        
        self.monitor.add_service(service)
        assert "test_service" in self.monitor.services
        
        self.monitor.remove_service("test_service")
        assert "test_service" not in self.monitor.services
    
    @patch('subprocess.Popen')
    def test_start_service(self, mock_popen):
        """Test starting a service"""
        # Mock process
        mock_process = Mock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        service = MonitoredService(
            name="test_service",
            command=["python", "-c", "import time; time.sleep(10)"],
            working_directory="/tmp",
            environment={"TEST": "value"}
        )
        
        self.monitor.add_service(service)
        
        # Start service
        success = self.monitor.start_service("test_service")
        
        assert success
        assert service.status == ServiceStatus.RUNNING
        assert service.pid == 12345
        assert service.process == mock_process
        assert service.started_at is not None
        assert service.metrics.restart_count == 1
    
    def test_start_nonexistent_service(self):
        """Test starting non-existent service"""
        success = self.monitor.start_service("nonexistent")
        assert not success
    
    def test_start_already_running_service(self):
        """Test starting already running service"""
        service = MonitoredService(
            name="test_service",
            command=["echo", "test"],
            working_directory="/tmp",
            environment={},
            status=ServiceStatus.RUNNING
        )
        
        self.monitor.add_service(service)
        
        success = self.monitor.start_service("test_service")
        assert success  # Should return True for already running
    
    @patch('subprocess.Popen')
    def test_start_service_failure(self, mock_popen):
        """Test service start failure"""
        # Mock process creation failure
        mock_popen.side_effect = Exception("Failed to start")
        
        service = MonitoredService(
            name="test_service",
            command=["invalid_command"],
            working_directory="/tmp",
            environment={}
        )
        
        self.monitor.add_service(service)
        
        success = self.monitor.start_service("test_service")
        
        assert not success
        assert service.status == ServiceStatus.FAILED
    
    def test_stop_service(self):
        """Test stopping a service"""
        # Mock process
        mock_process = Mock()
        mock_process.terminate = Mock()
        mock_process.wait = Mock()
        
        service = MonitoredService(
            name="test_service",
            command=["echo", "test"],
            working_directory="/tmp",
            environment={},
            status=ServiceStatus.RUNNING,
            process=mock_process,
            pid=12345
        )
        
        self.monitor.add_service(service)
        
        success = self.monitor.stop_service("test_service")
        
        assert success
        assert service.status == ServiceStatus.STOPPED
        assert service.pid is None
        assert service.process is None
        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once()
    
    def test_stop_service_force_kill(self):
        """Test force killing service that doesn't stop gracefully"""
        # Mock process that doesn't stop gracefully
        mock_process = Mock()
        mock_process.terminate = Mock()
        mock_process.wait = Mock(side_effect=subprocess.TimeoutExpired("cmd", 30))
        mock_process.kill = Mock()
        
        service = MonitoredService(
            name="test_service",
            command=["echo", "test"],
            working_directory="/tmp",
            environment={},
            status=ServiceStatus.RUNNING,
            process=mock_process,
            pid=12345
        )
        
        self.monitor.add_service(service)
        
        success = self.monitor.stop_service("test_service")
        
        assert success
        assert service.status == ServiceStatus.STOPPED
        mock_process.terminate.assert_called_once()
        mock_process.kill.assert_called_once()
    
    def test_stop_nonexistent_service(self):
        """Test stopping non-existent service"""
        success = self.monitor.stop_service("nonexistent")
        assert not success
    
    def test_stop_not_running_service(self):
        """Test stopping service that's not running"""
        service = MonitoredService(
            name="test_service",
            command=["echo", "test"],
            working_directory="/tmp",
            environment={},
            status=ServiceStatus.STOPPED
        )
        
        self.monitor.add_service(service)
        
        success = self.monitor.stop_service("test_service")
        assert success  # Should return True for already stopped
    
    @patch('subprocess.Popen')
    def test_restart_service(self, mock_popen):
        """Test restarting a service"""
        # Mock process
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.terminate = Mock()
        mock_process.wait = Mock()
        mock_popen.return_value = mock_process
        
        service = MonitoredService(
            name="test_service",
            command=["echo", "test"],
            working_directory="/tmp",
            environment={},
            status=ServiceStatus.RUNNING,
            process=mock_process,
            pid=12345,
            restart_delay=0  # No delay for testing
        )
        
        self.monitor.add_service(service)
        
        success = self.monitor.restart_service("test_service")
        
        assert success
        assert service.status == ServiceStatus.RUNNING
        assert service.metrics.restart_count == 1  # Incremented by start
    
    def test_restart_service_max_restarts_exceeded(self):
        """Test restart failure when max restarts exceeded"""
        service = MonitoredService(
            name="test_service",
            command=["echo", "test"],
            working_directory="/tmp",
            environment={},
            max_restarts=2
        )
        
        # Simulate exceeding max restarts
        service.metrics.restart_count = 3
        
        self.monitor.add_service(service)
        
        success = self.monitor.restart_service("test_service")
        
        assert not success
        assert service.status == ServiceStatus.FAILED
    
    def test_start_monitoring(self):
        """Test starting monitoring thread"""
        assert not self.monitor.running
        
        self.monitor.start_monitoring()
        
        assert self.monitor.running
        assert self.monitor.monitoring_thread is not None
        assert self.monitor.monitoring_thread.is_alive()
    
    def test_stop_monitoring(self):
        """Test stopping monitoring thread"""
        self.monitor.start_monitoring()
        assert self.monitor.running
        
        self.monitor.stop_monitoring()
        
        assert not self.monitor.running
    
    @patch('psutil.Process')
    def test_check_service_health_running(self, mock_psutil_process):
        """Test health check for running service"""
        # Mock psutil process
        mock_proc = Mock()
        mock_proc.is_running.return_value = True
        mock_psutil_process.return_value = mock_proc
        
        # Mock subprocess process
        mock_process = Mock()
        mock_process.poll.return_value = None  # Still running
        
        service = MonitoredService(
            name="test_service",
            command=["echo", "test"],
            working_directory="/tmp",
            environment={},
            status=ServiceStatus.RUNNING,
            process=mock_process,
            pid=12345
        )
        
        self.monitor.add_service(service)
        self.monitor._check_service_health(service)
        
        # Service should still be running
        assert service.status == ServiceStatus.RUNNING
        assert service.last_health_check is not None
    
    @patch('psutil.Process')
    def test_check_service_health_terminated(self, mock_psutil_process):
        """Test health check for terminated service"""
        # Mock subprocess process that has terminated
        mock_process = Mock()
        mock_process.poll.return_value = 1  # Exit code 1
        mock_process.returncode = 1
        
        service = MonitoredService(
            name="test_service",
            command=["echo", "test"],
            working_directory="/tmp",
            environment={},
            status=ServiceStatus.RUNNING,
            process=mock_process,
            pid=12345,
            auto_restart=False  # Disable auto-restart for test
        )
        
        self.monitor.add_service(service)
        self.monitor._check_service_health(service)
        
        # Service should be marked as failed
        assert service.status == ServiceStatus.FAILED
        assert service.process is None
        assert service.pid is None
    
    @patch('psutil.Process')
    def test_update_service_metrics(self, mock_psutil_process):
        """Test updating service metrics"""
        # Mock psutil process
        mock_proc = Mock()
        mock_proc.cpu_percent.return_value = 25.5
        mock_proc.memory_percent.return_value = 15.2
        mock_proc.memory_info.return_value = Mock(rss=1024*1024*50)  # 50MB
        mock_proc.open_files.return_value = [1, 2, 3]  # 3 files
        mock_proc.connections.return_value = [1, 2]  # 2 connections
        mock_psutil_process.return_value = mock_proc
        
        service = MonitoredService(
            name="test_service",
            command=["echo", "test"],
            working_directory="/tmp",
            environment={},
            status=ServiceStatus.RUNNING,
            pid=12345,
            started_at=time.time() - 100  # Started 100 seconds ago
        )
        
        self.monitor.add_service(service)
        self.monitor._update_service_metrics(service)
        
        # Check metrics were updated
        assert service.metrics.cpu_percent == 25.5
        assert service.metrics.memory_percent == 15.2
        assert service.metrics.memory_mb == 50.0
        assert service.metrics.open_files == 3
        assert service.metrics.connections == 2
        assert service.metrics.uptime_seconds >= 100
    
    def test_get_service_status(self):
        """Test getting service status"""
        service = MonitoredService(
            name="test_service",
            command=["echo", "test"],
            working_directory="/tmp",
            environment={}
        )
        
        self.monitor.add_service(service)
        
        status = self.monitor.get_service_status("test_service")
        assert status == service
        
        status = self.monitor.get_service_status("nonexistent")
        assert status is None
    
    def test_get_all_services_status(self):
        """Test getting all services status"""
        service1 = MonitoredService(
            name="service1",
            command=["echo", "test1"],
            working_directory="/tmp",
            environment={}
        )
        
        service2 = MonitoredService(
            name="service2",
            command=["echo", "test2"],
            working_directory="/tmp",
            environment={}
        )
        
        self.monitor.add_service(service1)
        self.monitor.add_service(service2)
        
        all_status = self.monitor.get_all_services_status()
        
        assert len(all_status) == 2
        assert "service1" in all_status
        assert "service2" in all_status
        assert all_status["service1"] == service1
        assert all_status["service2"] == service2
    
    def test_add_callback(self):
        """Test adding event callbacks"""
        callback_called = []
        
        def test_callback(service):
            callback_called.append(service.name)
        
        self.monitor.add_callback('service_started', test_callback)
        
        # Trigger callback
        service = MonitoredService(
            name="test_service",
            command=["echo", "test"],
            working_directory="/tmp",
            environment={}
        )
        
        self.monitor._trigger_callbacks('service_started', service)
        
        assert len(callback_called) == 1
        assert callback_called[0] == "test_service"
    
    def test_export_metrics(self):
        """Test exporting service metrics"""
        import tempfile
        import json
        import os
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

        
        service = MonitoredService(
            name="test_service",
            command=["echo", "test"],
            working_directory="/tmp",
            environment={},
            status=ServiceStatus.RUNNING
        )
        
        # Set some metrics
        service.metrics.cpu_percent = 25.0
        service.metrics.memory_percent = 15.0
        service.metrics.uptime_seconds = 300.0
        
        self.monitor.add_service(service)
        
        # Export metrics
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            metrics_file = f.name
        
        try:
            self.monitor.export_metrics(metrics_file)
            
            # Verify file was created and contains expected data
            assert os.path.exists(metrics_file)
            
            with open(metrics_file, 'r') as f:
                data = json.load(f)
            
            assert "timestamp" in data
            assert "services" in data
            assert "test_service" in data["services"]
            
            service_data = data["services"]["test_service"]
            assert service_data["status"] == "running"
            assert service_data["metrics"]["cpu_percent"] == 25.0
            assert service_data["metrics"]["memory_percent"] == 15.0
            assert service_data["metrics"]["uptime_seconds"] == 300.0
            
        finally:
            if os.path.exists(metrics_file):
                os.unlink(metrics_file)


class TestMonitoredService(ReflectiveModule):
    """Test monitored service data model"""
    
    def test_monitored_service_creation(self):
        """Test creating monitored service"""
        service = MonitoredService(
            name="test_service",
            command=["python", "-m", "test"],
            working_directory="/app",
            environment={"TEST": "value"}
        )
        
        assert service.name == "test_service"
        assert service.command == ["python", "-m", "test"]
        assert service.working_directory == "/app"
        assert service.environment == {"TEST": "value"}
        assert service.status == ServiceStatus.STOPPED
        assert service.auto_restart == True
        assert service.max_restarts == 5
        assert service.restart_delay == 10
        assert isinstance(service.metrics, ServiceMetrics)
    
    def test_service_metrics_defaults(self):
        """Test service metrics defaults"""
        metrics = ServiceMetrics()
        
        assert metrics.cpu_percent == 0.0
        assert metrics.memory_percent == 0.0
        assert metrics.memory_mb == 0.0
        assert metrics.open_files == 0
        assert metrics.connections == 0
        assert metrics.uptime_seconds == 0.0
        assert metrics.restart_count == 0
        assert metrics.last_restart is None


class TestServiceStatus(ReflectiveModule):
    """Test service status enumeration"""
    
    def test_service_status_values(self):
        """Test service status enum values"""
        assert ServiceStatus.STARTING == "starting"
        assert ServiceStatus.RUNNING == "running"
        assert ServiceStatus.STOPPING == "stopping"
        assert ServiceStatus.STOPPED == "stopped"
        assert ServiceStatus.FAILED == "failed"

    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }
        
    def register_module(self, registry):
        """Register module with registry."""
        if hasattr(registry, 'register'):
            registry.register(self.get_interface_metadata())
            
    def health_check(self):
        """Perform health check."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'module_id': getattr(self, 'module_id', self.__class__.__name__)
        }
        
    def get_health_status(self):
        """Get current health status."""
        return self.health_check()

        assert ServiceStatus.RESTARTING == "restarting"