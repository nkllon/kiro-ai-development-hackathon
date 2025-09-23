"""
Deployment Validator for Beast Mode

Provides deployment validation and smoke tests to ensure
proper deployment and configuration.
"""

import os
import time
import redis
import requests
import subprocess
import socket
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import json

from .config_manager import DeploymentConfig, ConfigManager
from .deployment_manager import DeploymentManager


class ValidationLevel(str, Enum):
    """Validation levels"""

    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"


@dataclass
class ValidationResult:
    """Result of a validation check"""

    name: str
    passed: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    duration_ms: float = 0.0


@dataclass
class ValidationReport:
    """Complete validation report"""

    deployment_id: str
    environment: str
    validation_level: ValidationLevel
    overall_passed: bool
    total_checks: int
    passed_checks: int
    failed_checks: int
    results: List[ValidationResult]
    started_at: str
    completed_at: str
    total_duration_ms: float


class DeploymentValidator:
    """Validates deployment health and functionality"""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)

    def validate_deployment(
        self,
        deployment_id: str,
        environment: str,
        level: ValidationLevel = ValidationLevel.STANDARD,
    ) -> ValidationReport:
        """Validate a deployment"""
        start_time = time.time()
        started_at = time.strftime("%Y-%m-%d %H:%M:%S")

        self.logger.info(
            f"Starting {level.value} validation for deployment {deployment_id}"
        )

        config = self.config_manager.get_config(environment)
        results = []

        # Basic validations (always run)
        results.extend(self._validate_basic_connectivity(config))
        results.extend(self._validate_redis_connection(config))

        # Standard validations
        if level in [ValidationLevel.STANDARD, ValidationLevel.COMPREHENSIVE]:
            results.extend(self._validate_service_health(config))
            results.extend(self._validate_message_flow(config))
            results.extend(self._validate_configuration(config))

        # Comprehensive validations
        if level == ValidationLevel.COMPREHENSIVE:
            results.extend(self._validate_performance(config))
            results.extend(self._validate_security(config))
            results.extend(self._validate_monitoring(config))

        # Calculate summary
        end_time = time.time()
        completed_at = time.strftime("%Y-%m-%d %H:%M:%S")
        total_duration_ms = (end_time - start_time) * 1000

        passed_checks = sum(1 for r in results if r.passed)
        failed_checks = len(results) - passed_checks
        overall_passed = failed_checks == 0

        report = ValidationReport(
            deployment_id=deployment_id,
            environment=environment,
            validation_level=level,
            overall_passed=overall_passed,
            total_checks=len(results),
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            results=results,
            started_at=started_at,
            completed_at=completed_at,
            total_duration_ms=total_duration_ms,
        )

        self.logger.info(
            f"Validation completed: {passed_checks}/{len(results)} checks passed"
        )
        return report

    def _validate_basic_connectivity(
        self, config: DeploymentConfig
    ) -> List[ValidationResult]:
        """Basic connectivity checks"""
        results = []

        # Check if Redis port is accessible
        result = self._check_port_connectivity(
            config.redis.host, config.redis.port, "Redis port connectivity"
        )
        results.append(result)

        # Check DNS resolution (if not localhost)
        if config.redis.host not in ["localhost", "127.0.0.1"]:
            result = self._check_dns_resolution(
                config.redis.host, "Redis host DNS resolution"
            )
            results.append(result)

        return results

    def _validate_redis_connection(
        self, config: DeploymentConfig
    ) -> List[ValidationResult]:
        """Redis connection validation"""
        results = []

        # Test Redis connection
        start_time = time.time()
        try:
            redis_client = redis.Redis(
                host=config.redis.host,
                port=config.redis.port,
                password=config.redis.password,
                db=config.redis.db,
                ssl=config.redis.ssl,
                socket_timeout=5,
            )

            # Test basic operations
            redis_client.ping()
            test_key = "beast_mode_validation_test"
            redis_client.set(test_key, "test_value", ex=60)
            value = redis_client.get(test_key)
            redis_client.delete(test_key)

            duration_ms = (time.time() - start_time) * 1000

            if value == b"test_value":
                results.append(
                    ValidationResult(
                        name="Redis connection and operations",
                        passed=True,
                        message="Redis connection successful, basic operations working",
                        duration_ms=duration_ms,
                        details={"host": config.redis.host, "port": config.redis.port},
                    )
                )
            else:
                results.append(
                    ValidationResult(
                        name="Redis connection and operations",
                        passed=False,
                        message="Redis operations failed - value mismatch",
                        duration_ms=duration_ms,
                    )
                )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            results.append(
                ValidationResult(
                    name="Redis connection and operations",
                    passed=False,
                    message=f"Redis connection failed: {str(e)}",
                    duration_ms=duration_ms,
                )
            )

        # Test pub/sub functionality
        start_time = time.time()
        try:
            redis_client = redis.Redis(
                host=config.redis.host,
                port=config.redis.port,
                password=config.redis.password,
                db=config.redis.db,
                ssl=config.redis.ssl,
            )

            pubsub = redis_client.pubsub()
            test_channel = "beast_mode_validation_channel"
            pubsub.subscribe(test_channel)

            # Wait for subscription confirmation
            message = pubsub.get_message(timeout=5)
            if message and message["type"] == "subscribe":
                # Publish test message
                redis_client.publish(test_channel, "test_message")

                # Try to receive the message
                message = pubsub.get_message(timeout=5)
                if message and message["type"] == "message":
                    duration_ms = (time.time() - start_time) * 1000
                    results.append(
                        ValidationResult(
                            name="Redis pub/sub functionality",
                            passed=True,
                            message="Redis pub/sub working correctly",
                            duration_ms=duration_ms,
                        )
                    )
                else:
                    duration_ms = (time.time() - start_time) * 1000
                    results.append(
                        ValidationResult(
                            name="Redis pub/sub functionality",
                            passed=False,
                            message="Failed to receive pub/sub message",
                            duration_ms=duration_ms,
                        )
                    )
            else:
                duration_ms = (time.time() - start_time) * 1000
                results.append(
                    ValidationResult(
                        name="Redis pub/sub functionality",
                        passed=False,
                        message="Failed to subscribe to channel",
                        duration_ms=duration_ms,
                    )
                )

            pubsub.close()

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            results.append(
                ValidationResult(
                    name="Redis pub/sub functionality",
                    passed=False,
                    message=f"Redis pub/sub test failed: {str(e)}",
                    duration_ms=duration_ms,
                )
            )

        return results

    def _validate_service_health(
        self, config: DeploymentConfig
    ) -> List[ValidationResult]:
        """Service health validation"""
        results = []

        # Check if expected processes are running
        expected_processes = ["redis-server", "python"]  # Basic expected processes

        for process_name in expected_processes:
            result = self._check_process_running(process_name)
            results.append(result)

        # Check log files exist and are being written to
        log_files = [config.agent.mailbox_log_file]

        for log_file in log_files:
            result = self._check_log_file_health(log_file)
            results.append(result)

        return results

    def _validate_message_flow(
        self, config: DeploymentConfig
    ) -> List[ValidationResult]:
        """Message flow validation"""
        results = []

        # Test message sending and receiving
        start_time = time.time()
        try:
            # This would require the actual bus client to be available
            # For now, we'll do a basic Redis pub/sub test
            redis_client = redis.Redis(
                host=config.redis.host,
                port=config.redis.port,
                password=config.redis.password,
                db=config.redis.db,
                ssl=config.redis.ssl,
            )

            # Test message publishing to beast_mode_network channel
            test_message = {
                "id": "validation_test",
                "type": "simple_message",
                "source": "validator",
                "payload": {"test": True},
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            }

            result = redis_client.publish(
                "beast_mode_network", json.dumps(test_message)
            )
            duration_ms = (time.time() - start_time) * 1000

            if result > 0:
                results.append(
                    ValidationResult(
                        name="Message publishing",
                        passed=True,
                        message=f"Successfully published message to {result} subscribers",
                        duration_ms=duration_ms,
                    )
                )
            else:
                results.append(
                    ValidationResult(
                        name="Message publishing",
                        passed=True,  # Still passes even with 0 subscribers
                        message="Message published successfully (no active subscribers)",
                        duration_ms=duration_ms,
                    )
                )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            results.append(
                ValidationResult(
                    name="Message publishing",
                    passed=False,
                    message=f"Message publishing failed: {str(e)}",
                    duration_ms=duration_ms,
                )
            )

        return results

    def _validate_configuration(
        self, config: DeploymentConfig
    ) -> List[ValidationResult]:
        """Configuration validation"""
        results = []

        # Validate configuration completeness
        issues = self.config_manager.validate_config(config)

        if not issues:
            results.append(
                ValidationResult(
                    name="Configuration validation",
                    passed=True,
                    message="Configuration is valid and complete",
                )
            )
        else:
            results.append(
                ValidationResult(
                    name="Configuration validation",
                    passed=False,
                    message=f"Configuration issues found: {', '.join(issues)}",
                    details={"issues": issues},
                )
            )

        # Check required directories exist
        directories = [config.agent.spore_directory]

        for directory in directories:
            if os.path.exists(directory):
                results.append(
                    ValidationResult(
                        name=f"Directory exists: {directory}",
                        passed=True,
                        message=f"Required directory exists: {directory}",
                    )
                )
            else:
                results.append(
                    ValidationResult(
                        name=f"Directory exists: {directory}",
                        passed=False,
                        message=f"Required directory missing: {directory}",
                    )
                )

        return results

    def _validate_performance(self, config: DeploymentConfig) -> List[ValidationResult]:
        """Performance validation"""
        results = []

        # Test Redis performance
        start_time = time.time()
        try:
            redis_client = redis.Redis(
                host=config.redis.host,
                port=config.redis.port,
                password=config.redis.password,
                db=config.redis.db,
                ssl=config.redis.ssl,
            )

            # Perform multiple operations to test performance
            operations = 100
            for i in range(operations):
                redis_client.set(f"perf_test_{i}", f"value_{i}")
                redis_client.get(f"perf_test_{i}")
                redis_client.delete(f"perf_test_{i}")

            duration_ms = (time.time() - start_time) * 1000
            ops_per_second = (operations * 3) / (
                duration_ms / 1000
            )  # 3 ops per iteration

            if ops_per_second > 1000:  # Threshold for good performance
                results.append(
                    ValidationResult(
                        name="Redis performance test",
                        passed=True,
                        message=f"Good performance: {ops_per_second:.0f} ops/sec",
                        duration_ms=duration_ms,
                        details={"ops_per_second": ops_per_second},
                    )
                )
            else:
                results.append(
                    ValidationResult(
                        name="Redis performance test",
                        passed=False,
                        message=f"Poor performance: {ops_per_second:.0f} ops/sec (expected >1000)",
                        duration_ms=duration_ms,
                        details={"ops_per_second": ops_per_second},
                    )
                )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            results.append(
                ValidationResult(
                    name="Redis performance test",
                    passed=False,
                    message=f"Performance test failed: {str(e)}",
                    duration_ms=duration_ms,
                )
            )

        return results

    def _validate_security(self, config: DeploymentConfig) -> List[ValidationResult]:
        """Security validation"""
        results = []

        # Check if Redis has authentication enabled in production
        if config.environment.value == "production":
            if config.redis.password:
                results.append(
                    ValidationResult(
                        name="Redis authentication",
                        passed=True,
                        message="Redis authentication is configured for production",
                    )
                )
            else:
                results.append(
                    ValidationResult(
                        name="Redis authentication",
                        passed=False,
                        message="Redis authentication should be enabled in production",
                    )
                )

            # Check SSL configuration
            if config.redis.ssl:
                results.append(
                    ValidationResult(
                        name="Redis SSL/TLS",
                        passed=True,
                        message="Redis SSL/TLS is enabled for production",
                    )
                )
            else:
                results.append(
                    ValidationResult(
                        name="Redis SSL/TLS",
                        passed=False,
                        message="Redis SSL/TLS should be enabled in production",
                    )
                )

        return results

    def _validate_monitoring(self, config: DeploymentConfig) -> List[ValidationResult]:
        """Monitoring validation"""
        results = []

        # Check if monitoring is properly configured
        if config.monitoring.enable_performance_monitoring:
            results.append(
                ValidationResult(
                    name="Performance monitoring",
                    passed=True,
                    message="Performance monitoring is enabled",
                )
            )

        # Validate monitoring intervals
        if config.monitoring.health_check_interval > 0:
            results.append(
                ValidationResult(
                    name="Health check configuration",
                    passed=True,
                    message=f"Health checks configured every {config.monitoring.health_check_interval}s",
                )
            )
        else:
            results.append(
                ValidationResult(
                    name="Health check configuration",
                    passed=False,
                    message="Health check interval must be positive",
                )
            )

        return results

    def _check_port_connectivity(
        self, host: str, port: int, name: str
    ) -> ValidationResult:
        """Check if a port is accessible"""
        start_time = time.time()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()

            duration_ms = (time.time() - start_time) * 1000

            if result == 0:
                return ValidationResult(
                    name=name,
                    passed=True,
                    message=f"Port {port} on {host} is accessible",
                    duration_ms=duration_ms,
                )
            else:
                return ValidationResult(
                    name=name,
                    passed=False,
                    message=f"Port {port} on {host} is not accessible",
                    duration_ms=duration_ms,
                )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return ValidationResult(
                name=name,
                passed=False,
                message=f"Port connectivity check failed: {str(e)}",
                duration_ms=duration_ms,
            )

    def _check_dns_resolution(self, hostname: str, name: str) -> ValidationResult:
        """Check DNS resolution"""
        start_time = time.time()
        try:
            socket.gethostbyname(hostname)
            duration_ms = (time.time() - start_time) * 1000
            return ValidationResult(
                name=name,
                passed=True,
                message=f"DNS resolution successful for {hostname}",
                duration_ms=duration_ms,
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return ValidationResult(
                name=name,
                passed=False,
                message=f"DNS resolution failed for {hostname}: {str(e)}",
                duration_ms=duration_ms,
            )

    def _check_process_running(self, process_name: str) -> ValidationResult:
        """Check if a process is running"""
        start_time = time.time()
        try:
            result = subprocess.run(
                ["pgrep", "-f", process_name], capture_output=True, text=True
            )

            duration_ms = (time.time() - start_time) * 1000

            if result.returncode == 0:
                pids = result.stdout.strip().split("\n")
                return ValidationResult(
                    name=f"Process running: {process_name}",
                    passed=True,
                    message=f"Process {process_name} is running (PIDs: {', '.join(pids)})",
                    duration_ms=duration_ms,
                    details={"pids": pids},
                )
            else:
                return ValidationResult(
                    name=f"Process running: {process_name}",
                    passed=False,
                    message=f"Process {process_name} is not running",
                    duration_ms=duration_ms,
                )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return ValidationResult(
                name=f"Process running: {process_name}",
                passed=False,
                message=f"Process check failed: {str(e)}",
                duration_ms=duration_ms,
            )

    def _check_log_file_health(self, log_file: str) -> ValidationResult:
        """Check log file health"""
        start_time = time.time()
        try:
            if not os.path.exists(log_file):
                duration_ms = (time.time() - start_time) * 1000
                return ValidationResult(
                    name=f"Log file exists: {log_file}",
                    passed=False,
                    message=f"Log file does not exist: {log_file}",
                    duration_ms=duration_ms,
                )

            # Check if file was modified recently (within last hour)
            mtime = os.path.getmtime(log_file)
            age_seconds = time.time() - mtime

            duration_ms = (time.time() - start_time) * 1000

            if age_seconds < 3600:  # 1 hour
                return ValidationResult(
                    name=f"Log file activity: {log_file}",
                    passed=True,
                    message=f"Log file is active (last modified {age_seconds:.0f}s ago)",
                    duration_ms=duration_ms,
                    details={"age_seconds": age_seconds},
                )
            else:
                return ValidationResult(
                    name=f"Log file activity: {log_file}",
                    passed=False,
                    message=f"Log file may be stale (last modified {age_seconds:.0f}s ago)",
                    duration_ms=duration_ms,
                    details={"age_seconds": age_seconds},
                )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return ValidationResult(
                name=f"Log file health: {log_file}",
                passed=False,
                message=f"Log file check failed: {str(e)}",
                duration_ms=duration_ms,
            )

    def generate_report_html(self, report: ValidationReport, output_file: str):
        """Generate HTML report"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Beast Mode Deployment Validation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
        .result {{ margin: 10px 0; padding: 10px; border-left: 4px solid #ccc; }}
        .result.passed {{ border-left-color: green; }}
        .result.failed {{ border-left-color: red; }}
        .details {{ margin-top: 10px; font-size: 0.9em; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Beast Mode Deployment Validation Report</h1>
        <p><strong>Deployment ID:</strong> {report.deployment_id}</p>
        <p><strong>Environment:</strong> {report.environment}</p>
        <p><strong>Validation Level:</strong> {report.validation_level.value}</p>
        <p><strong>Started:</strong> {report.started_at}</p>
        <p><strong>Completed:</strong> {report.completed_at}</p>
        <p><strong>Duration:</strong> {report.total_duration_ms:.0f}ms</p>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
        <p class="{'passed' if report.overall_passed else 'failed'}">
            <strong>Overall Status:</strong> {'PASSED' if report.overall_passed else 'FAILED'}
        </p>
        <p><strong>Total Checks:</strong> {report.total_checks}</p>
        <p class="passed"><strong>Passed:</strong> {report.passed_checks}</p>
        <p class="failed"><strong>Failed:</strong> {report.failed_checks}</p>
    </div>
    
    <div class="results">
        <h2>Detailed Results</h2>
"""

        for result in report.results:
            status_class = "passed" if result.passed else "failed"
            status_text = "PASSED" if result.passed else "FAILED"

            html_content += f"""
        <div class="result {status_class}">
            <h3>{result.name} - {status_text}</h3>
            <p>{result.message}</p>
            <div class="details">
                Duration: {result.duration_ms:.0f}ms
"""

            if result.details:
                html_content += f"<br>Details: {json.dumps(result.details, indent=2)}"

            html_content += """
            </div>
        </div>
"""

        html_content += """
    </div>
</body>
</html>
"""

        with open(output_file, "w") as f:
            f.write(html_content)

        self.logger.info(f"HTML report generated: {output_file}")
