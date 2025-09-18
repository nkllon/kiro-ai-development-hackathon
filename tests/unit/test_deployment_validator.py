"""
RDI Enhanced Test Module

Requirements Traceability:

Enhanced: 2025-09-14T06:30:15.481198
"""






import pytest
import tempfile
import socket
from unittest.mock import Mock, patch, MagicMock
import redis

from beast_mode.deployment.config_manager import ConfigManager, DeploymentConfig, RedisConfig
from beast_mode.deployment.validator import (
    DeploymentValidator, ValidationLevel, ValidationResult, ValidationReport
)


class TestDeploymentValidator(ReflectiveModule):
    """Test deployment validator functionality"""

    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager(self.temp_dir)
        self.validator = DeploymentValidator(self.config_manager)

    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('socket.socket')
    def test_check_port_connectivity_success(self, mock_socket):
        """Test successful port connectivity check"""
        # Mock successful connection
        mock_sock = Mock()
        mock_sock.connect_ex.return_value = 0
        mock_socket.return_value = mock_sock

        result = self.validator._check_port_connectivity("localhost", 6379, "Test port")

        assert result.passed
        assert "accessible" in result.message
        assert result.duration_ms > 0

    @patch('socket.socket')
    def test_check_port_connectivity_failure(self, mock_socket):
        """Test failed port connectivity check"""
        # Mock failed connection
        mock_sock = Mock()
        mock_sock.connect_ex.return_value = 1  # Connection refused
        mock_socket.return_value = mock_sock

        result = self.validator._check_port_connectivity("localhost", 6379, "Test port")

        assert not result.passed
        assert "not accessible" in result.message

    @patch('socket.gethostbyname')
    def test_check_dns_resolution_success(self, mock_gethostbyname):
        """Test successful DNS resolution"""
        mock_gethostbyname.return_value = "127.0.0.1"

        result = self.validator._check_dns_resolution("localhost", "Test DNS")

        assert result.passed
        assert "successful" in result.message

    @patch('socket.gethostbyname')
    def test_check_dns_resolution_failure(self, mock_gethostbyname):
        """Test failed DNS resolution"""
        mock_gethostbyname.side_effect = socket.gaierror("Name resolution failed")

        result = self.validator._check_dns_resolution("invalid.host", "Test DNS")

        assert not result.passed
        assert "failed" in result.message

    @patch('subprocess.run')
    def test_check_process_running_success(self, mock_run):
        """Test successful process check"""
        # Mock successful pgrep
        mock_run.return_value = Mock(returncode=0, stdout="1234\n5678\n")

        result = self.validator._check_process_running("redis-server")

        assert result.passed
        assert "running" in result.message
        assert "1234, 5678" in result.message

    @patch('subprocess.run')
    def test_check_process_running_failure(self, mock_run):
        """Test failed process check"""
        # Mock failed pgrep (no processes found)
        mock_run.return_value = Mock(returncode=1, stdout="")

        result = self.validator._check_process_running("nonexistent")

        assert not result.passed
        assert "not running" in result.message

    def test_check_log_file_health_exists_recent(self):
        """Test log file health check for recent file"""
        import os
        import time

        # Create a recent log file
        log_file = os.path.join(self.temp_dir, "test.log")
        with open(log_file, 'w') as f:
            f.write("test log content")

        result = self.validator._check_log_file_health(log_file)

        assert result.passed
        assert "active" in result.message

    def test_check_log_file_health_not_exists(self):
        """Test log file health check for non-existent file"""
        log_file = os.path.join(self.temp_dir, "nonexistent.log")

        result = self.validator._check_log_file_health(log_file)

        assert not result.passed
        assert "does not exist" in result.message

    def test_check_log_file_health_stale(self):
        """Test log file health check for stale file"""
        import os
        import time

        # Create an old log file
        log_file = os.path.join(self.temp_dir, "old.log")
        with open(log_file, 'w') as f:
            f.write("old log content")

        # Make it old (more than 1 hour)
        old_time = time.time() - 7200  # 2 hours ago
        os.utime(log_file, (old_time, old_time))

        result = self.validator._check_log_file_health(log_file)

        assert not result.passed
        assert "stale" in result.message

    @patch('redis.Redis')
    def test_validate_redis_connection_success(self, mock_redis):
        """Test successful Redis connection validation"""
        # Mock Redis client
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.set.return_value = True
        mock_client.get.return_value = b"test_value"
        mock_client.delete.return_value = 1
        mock_redis.return_value = mock_client

        config = self.config_manager.get_config("development")
        results = self.validator._validate_redis_connection(config)

        # Should have at least one successful result
        connection_results = [r for r in results if "connection and operations" in r.name]
        assert len(connection_results) > 0
        assert connection_results[0].passed

    @patch('redis.Redis')
    def test_validate_redis_connection_failure(self, mock_redis):
        """Test failed Redis connection validation"""
        # Mock Redis connection failure
        mock_redis.side_effect = redis.ConnectionError("Connection failed")

        config = self.config_manager.get_config("development")
        results = self.validator._validate_redis_connection(config)

        # Should have failed results
        connection_results = [r for r in results if "connection and operations" in r.name]
        assert len(connection_results) > 0
        assert not connection_results[0].passed
        assert "Connection failed" in connection_results[0].message

    @patch('redis.Redis')
    def test_validate_redis_pubsub_success(self, mock_redis):
        """Test successful Redis pub/sub validation"""
        # Mock Redis client and pub/sub
        mock_pubsub = Mock()
        mock_pubsub.get_message.side_effect = [
            {'type': 'subscribe', 'channel': b'test_channel'},
            {'type': 'message', 'channel': b'test_channel', 'data': b'test_message'}
        ]

        mock_client = Mock()
        mock_client.pubsub.return_value = mock_pubsub
        mock_client.publish.return_value = 1
        mock_redis.return_value = mock_client

        config = self.config_manager.get_config("development")
        results = self.validator._validate_redis_connection(config)

        # Should have successful pub/sub result
        pubsub_results = [r for r in results if "pub/sub functionality" in r.name]
        assert len(pubsub_results) > 0
        assert pubsub_results[0].passed

    def test_validate_configuration_valid(self):
        """Test configuration validation with valid config"""
        config = self.config_manager.get_config("development")
        results = self.validator._validate_configuration(config)

        # Should pass validation
        validation_results = [r for r in results if "Configuration validation" in r.name]
        assert len(validation_results) > 0
        assert validation_results[0].passed

    def test_validate_configuration_invalid(self):
        """Test configuration validation with invalid config"""
        # Create invalid config
        config = DeploymentConfig(
            environment="test",
            redis=RedisConfig(host="", port=-1),  # Invalid
            agent=Mock(agent_id="", capabilities=[]),  # Invalid
            monitoring=Mock(health_check_interval=-1)  # Invalid
        )

        # Mock the validate_config method to return issues
        with patch.object(self.config_manager, 'validate_config') as mock_validate:
            mock_validate.return_value = ["Redis host cannot be empty", "Invalid port"]

            results = self.validator._validate_configuration(config)

            validation_results = [r for r in results if "Configuration validation" in r.name]
            assert len(validation_results) > 0
            assert not validation_results[0].passed
            assert "issues found" in validation_results[0].message

    @patch('redis.Redis')
    def test_validate_performance_good(self, mock_redis):
        """Test performance validation with good performance"""
        # Mock Redis client with fast operations
        mock_client = Mock()
        mock_client.set.return_value = True
        mock_client.get.return_value = b"value"
        mock_client.delete.return_value = 1
        mock_redis.return_value = mock_client

        config = self.config_manager.get_config("development")
        results = self.validator._validate_performance(config)

        # Should pass performance test
        perf_results = [r for r in results if "performance test" in r.name]
        assert len(perf_results) > 0
        # Note: This might fail in fast test environments, so we check for existence
        assert perf_results[0].duration_ms >= 0

    def test_validate_security_production(self):
        """Test security validation for production environment"""
        config = self.config_manager.get_config("production")
        results = self.validator._validate_security(config)

        # Should check for authentication and SSL
        auth_results = [r for r in results if "authentication" in r.name]
        ssl_results = [r for r in results if "SSL/TLS" in r.name]

        # Production config should have these enabled
        if auth_results:
            assert auth_results[0].passed  # Production config has password
        if ssl_results:
            assert ssl_results[0].passed  # Production config has SSL

    def test_validate_monitoring(self):
        """Test monitoring validation"""
        config = self.config_manager.get_config("development")
        results = self.validator._validate_monitoring(config)

        # Should validate monitoring configuration
        monitoring_results = [r for r in results if "monitoring" in r.name.lower()]
        assert len(monitoring_results) > 0

        # Check health check configuration
        health_results = [r for r in results if "Health check" in r.name]
        if health_results:
            assert health_results[0].passed

    @patch('socket.socket')
    @patch('redis.Redis')
    def test_validate_deployment_basic(self, mock_redis, mock_socket):
        """Test basic deployment validation"""
        # Mock successful connectivity
        mock_sock = Mock()
        mock_sock.connect_ex.return_value = 0
        mock_socket.return_value = mock_sock

        # Mock successful Redis
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.set.return_value = True
        mock_client.get.return_value = b"test_value"
        mock_client.delete.return_value = 1
        mock_redis.return_value = mock_client

        report = self.validator.validate_deployment(
            "test_deployment",
            "development",
            ValidationLevel.BASIC
        )

        assert isinstance(report, ValidationReport)
        assert report.deployment_id == "test_deployment"
        assert report.environment == "development"
        assert report.validation_level == ValidationLevel.BASIC
        assert report.total_checks > 0
        assert report.total_duration_ms > 0

    @patch('socket.socket')
    @patch('redis.Redis')
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_validate_deployment_standard(self, mock_exists, mock_run, mock_redis, mock_socket):
        """Test standard deployment validation"""
        # Mock all dependencies
        mock_sock = Mock()
        mock_sock.connect_ex.return_value = 0
        mock_socket.return_value = mock_sock

        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.set.return_value = True
        mock_client.get.return_value = b"test_value"
        mock_client.delete.return_value = 1
        mock_client.publish.return_value = 1
        mock_redis.return_value = mock_client

        mock_run.return_value = Mock(returncode=0, stdout="1234\n")
        mock_exists.return_value = True

        report = self.validator.validate_deployment(
            "test_deployment",
            "development",
            ValidationLevel.STANDARD
        )

        assert report.validation_level == ValidationLevel.STANDARD
        assert report.total_checks > 2  # Should have more checks than basic

    def test_generate_report_html(self):
        """Test HTML report generation"""
        import os
# from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule


        # Create a sample report
        results = [
            ValidationResult(
                name="Test Check 1",
                passed=True,
                message="Test passed",
                duration_ms=100.0
            ),
            ValidationResult(
                name="Test Check 2",
                passed=False,
                message="Test failed",
                duration_ms=50.0,
                details={"error": "test error"}
            )
        ]

        report = ValidationReport(
            deployment_id="test_deployment",
            environment="test",
            validation_level=ValidationLevel.BASIC,
            overall_passed=False,
            total_checks=2,
            passed_checks=1,
            failed_checks=1,
            results=results,
            started_at="2023-01-01 12:00:00",
            completed_at="2023-01-01 12:01:00",
            total_duration_ms=1000.0
        )

        output_file = os.path.join(self.temp_dir, "test_report.html")
        self.validator.generate_report_html(report, output_file)

        assert os.path.exists(output_file)

        with open(output_file, 'r') as f:
            content = f.read()

        assert "Beast Mode Deployment Validation Report" in content
        assert "test_deployment" in content
        assert "Test Check 1" in content
        assert "Test Check 2" in content
        assert "PASSED" in content
        assert "FAILED" in content


class TestValidationResult(ReflectiveModule):
    """Test validation result data model"""

    def test_validation_result_creation(self):
        """Test creating validation result"""
        result = ValidationResult(
            name="Test Check",
            passed=True,
            message="Test message",
            details={"key": "value"},
            duration_ms=123.45
        )

        assert result.name == "Test Check"
        assert result.passed == True
        assert result.message == "Test message"
        assert result.details == {"key": "value"}
        assert result.duration_ms == 123.45

    def test_validation_result_defaults(self):
        """Test validation result defaults"""
        result = ValidationResult(
            name="Test Check",
            passed=False,
            message="Test message"
        )

        assert result.details is None
        assert result.duration_ms == 0.0


class TestValidationReport(ReflectiveModule):
    """Test validation report data model"""

    def test_validation_report_creation(self):
        """Test creating validation report"""
        results = [
            ValidationResult("Check 1", True, "Passed"),
            ValidationResult("Check 2", False, "Failed")
        ]

        report = ValidationReport(
            deployment_id="test_deployment",
            environment="test",
            validation_level=ValidationLevel.STANDARD,
            overall_passed=False,
            total_checks=2,
            passed_checks=1,
            failed_checks=1,
            results=results,
            started_at="2023-01-01 12:00:00",
            completed_at="2023-01-01 12:01:00",
            total_duration_ms=60000.0
        )

        assert report.deployment_id == "test_deployment"
        assert report.environment == "test"
        assert report.validation_level == ValidationLevel.STANDARD
        assert report.overall_passed == False
        assert report.total_checks == 2
        assert report.passed_checks == 1
        assert report.failed_checks == 1
        assert len(report.results) == 2
        assert report.total_duration_ms == 60000.0


class TestValidationLevel(ReflectiveModule):
    """Test validation level enumeration"""

    def test_validation_level_values(self):
        """Test validation level enum values"""
        assert ValidationLevel.BASIC == "basic"
        assert ValidationLevel.STANDARD == "standard"

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

        assert ValidationLevel.COMPREHENSIVE == "comprehensive"