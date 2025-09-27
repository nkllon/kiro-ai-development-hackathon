#!/usr/bin/env python3
"""
Deployment Validation Suite

Comprehensive validation system for WebSocket deployment with health checks,
performance monitoring, and quality assurance validation.

Features:
- Multi-stage health validation
- Performance metrics validation
- End-to-end connectivity testing
- Quality assurance checks
- Automated reporting and alerting
"""

import asyncio
import json
import logging
import requests
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import yaml
import websockets
from concurrent.futures import ThreadPoolExecutor

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from beast_mode.observatory.websocket import (
    WebSocketHealthValidator,
    HealthStatus,
    EndpointMonitor,
    FailureDetector,
    QualityMetricsCollector
)
from beast_mode.observatory.monitoring.health_monitor import WebSocketHealthMonitor


class ValidationStatus(Enum):
    """Validation status levels"""
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"
    SKIPPED = "skipped"


class ValidationSeverity(Enum):
    """Validation severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ValidationResult:
    """Result of a validation check"""
    check_name: str
    status: ValidationStatus
    severity: ValidationSeverity
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: float = 0.0


@dataclass
class ValidationConfig:
    """Configuration for validation suite"""
    # Environment configurations
    environments: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Validation thresholds
    thresholds: Dict[str, float] = field(default_factory=lambda: {
        "max_latency_ms": 1000,
        "max_error_rate": 0.05,
        "min_throughput_msgs_per_sec": 1.0,
        "max_connection_failure_rate": 0.1,
        "min_health_score": 0.8,
        "max_response_time_ms": 2000
    })
    
    # Test configuration
    test_duration_seconds: int = 300  # 5 minutes
    test_interval_seconds: int = 10
    max_concurrent_tests: int = 5
    
    # Reporting configuration
    generate_report: bool = True
    report_format: str = "json"  # json, html, text
    alert_on_failure: bool = True


class DeploymentValidator:
    """
    Comprehensive deployment validation system.
    
    Performs multi-stage validation including health checks, performance
    monitoring, and quality assurance validation.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize validator with configuration"""
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        
        # Initialize monitoring components
        self.health_validator = WebSocketHealthValidator()
        self.endpoint_monitor = EndpointMonitor()
        self.failure_detector = FailureDetector()
        self.health_monitor = WebSocketHealthMonitor()
        self.quality_metrics = QualityMetricsCollector()
        
        # Validation tracking
        self.validation_results: List[ValidationResult] = []
        self.test_metrics: Dict[str, List[float]] = {}
        
        self.logger.info("Deployment Validator initialized")
    
    def _load_config(self, config_path: Optional[str]) -> ValidationConfig:
        """Load validation configuration from file or use defaults"""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
                return ValidationConfig(**config_data)
        
        # Default configuration
        return ValidationConfig(
            environments={
                "dev": {
                    "url": "http://localhost:8888",
                    "websocket_url": "ws://localhost:8888/ws",
                    "health_endpoint": "/health",
                    "expected_response_time_ms": 500
                },
                "staging": {
                    "url": "https://staging-observatory.nkllon.com",
                    "websocket_url": "wss://staging-observatory.nkllon.com/ws",
                    "health_endpoint": "/health",
                    "expected_response_time_ms": 1000
                },
                "production": {
                    "url": "https://observatory.nkllon.com",
                    "websocket_url": "wss://observatory.nkllon.com/ws",
                    "health_endpoint": "/health",
                    "expected_response_time_ms": 1500
                }
            }
        )
    
    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging for validation operations"""
        logger = logging.getLogger("deployment_validator")
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # File handler for validation logs
        file_handler = logging.FileHandler(
            logs_dir / f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        file_handler.setLevel(logging.INFO)
        
        # Console handler for real-time output
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # JSON formatter for structured logs
        json_formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"component": "validation", "message": "%(message)s"}'
        )
        file_handler.setFormatter(json_formatter)
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    async def validate_deployment(
        self,
        environments: List[str] = None,
        validation_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Execute comprehensive deployment validation.
        
        Args:
            environments: List of environments to validate (default: all)
            validation_types: List of validation types to run (default: all)
            
        Returns:
            Dict containing validation results and summary
        """
        if environments is None:
            environments = list(self.config.environments.keys())
        
        if validation_types is None:
            validation_types = [
                "health_check", "performance", "connectivity", 
                "websocket", "tunnel", "monitoring", "quality_assurance"
            ]
        
        self.logger.info(f"Starting deployment validation for environments: {environments}")
        
        validation_start = datetime.now()
        overall_status = "passed"
        environment_results = {}
        
        try:
            # Execute validation for each environment
            for env in environments:
                self.logger.info(f"Validating environment: {env}")
                
                env_result = await self._validate_environment(env, validation_types)
                environment_results[env] = env_result
                
                # Check if validation failed
                if env_result["overall_status"] == "failed":
                    self.logger.error(f"Validation failed for environment: {env}")
                    overall_status = "failed"
                
            # Generate comprehensive report
            if self.config.generate_report:
                await self._generate_validation_report(environment_results)
            
        except Exception as e:
            self.logger.error(f"Validation failed with exception: {e}")
            overall_status = "failed"
        
        validation_end = datetime.now()
        validation_duration = (validation_end - validation_start).total_seconds()
        
        # Generate summary
        summary = {
            "overall_status": overall_status,
            "validation_duration_seconds": validation_duration,
            "environments_validated": environments,
            "total_checks": len(self.validation_results),
            "passed_checks": len([r for r in self.validation_results if r.status == ValidationStatus.PASSED]),
            "failed_checks": len([r for r in self.validation_results if r.status == ValidationStatus.FAILED]),
            "warning_checks": len([r for r in self.validation_results if r.status == ValidationStatus.WARNING]),
            "environment_results": environment_results,
            "critical_issues": [
                r for r in self.validation_results 
                if r.status == ValidationStatus.FAILED and r.severity == ValidationSeverity.CRITICAL
            ]
        }
        
        self.logger.info(f"Validation completed with status: {overall_status}")
        return summary
    
    async def _validate_environment(
        self, 
        environment: str, 
        validation_types: List[str]
    ) -> Dict[str, Any]:
        """Validate a specific environment"""
        env_config = self.config.environments[environment]
        
        self.logger.info(f"Starting validation for {environment}")
        
        validation_tasks = []
        
        # Create validation tasks based on types
        if "health_check" in validation_types:
            validation_tasks.append(self._validate_health_endpoints(environment, env_config))
        
        if "performance" in validation_types:
            validation_tasks.append(self._validate_performance_metrics(environment, env_config))
        
        if "connectivity" in validation_types:
            validation_tasks.append(self._validate_connectivity(environment, env_config))
        
        if "websocket" in validation_types:
            validation_tasks.append(self._validate_websocket_functionality(environment, env_config))
        
        if "tunnel" in validation_types:
            validation_tasks.append(self._validate_tunnel_health(environment, env_config))
        
        if "monitoring" in validation_types:
            validation_tasks.append(self._validate_monitoring_systems(environment, env_config))
        
        if "quality_assurance" in validation_types:
            validation_tasks.append(self._validate_quality_assurance(environment, env_config))
        
        # Execute validation tasks
        results = await asyncio.gather(*validation_tasks, return_exceptions=True)
        
        # Process results
        env_results = []
        env_status = "passed"
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_result = ValidationResult(
                    check_name=f"validation_task_{i}",
                    status=ValidationStatus.FAILED,
                    severity=ValidationSeverity.HIGH,
                    message=f"Validation task failed: {result}"
                )
                env_results.append(error_result)
                env_status = "failed"
            else:
                env_results.extend(result)
                # Check if any critical failures
                if any(r.status == ValidationStatus.FAILED and r.severity == ValidationSeverity.CRITICAL 
                      for r in result):
                    env_status = "failed"
        
        return {
            "environment": environment,
            "overall_status": env_status,
            "validation_results": env_results,
            "total_checks": len(env_results),
            "passed": len([r for r in env_results if r.status == ValidationStatus.PASSED]),
            "failed": len([r for r in env_results if r.status == ValidationStatus.FAILED]),
            "warnings": len([r for r in env_results if r.status == ValidationStatus.WARNING])
        }
    
    async def _validate_health_endpoints(
        self, 
        environment: str, 
        config: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate health endpoints"""
        results = []
        
        try:
            start_time = time.time()
            
            # Test HTTP health endpoint
            health_url = f"{config['url']}{config['health_endpoint']}"
            response = requests.get(health_url, timeout=10)
            
            duration_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                status = ValidationStatus.PASSED
                message = f"Health endpoint responding correctly"
                severity = ValidationSeverity.LOW
            else:
                status = ValidationStatus.FAILED
                message = f"Health endpoint returned status {response.status_code}"
                severity = ValidationSeverity.CRITICAL
            
            results.append(ValidationResult(
                check_name="health_endpoint",
                status=status,
                severity=severity,
                message=message,
                details={
                    "url": health_url,
                    "status_code": response.status_code,
                    "response_time_ms": duration_ms,
                    "response_size_bytes": len(response.content)
                },
                duration_ms=duration_ms
            ))
            
        except Exception as e:
            results.append(ValidationResult(
                check_name="health_endpoint",
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.CRITICAL,
                message=f"Health endpoint check failed: {e}",
                details={"url": health_url, "error": str(e)}
            ))
        
        return results
    
    async def _validate_performance_metrics(
        self, 
        environment: str, 
        config: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate performance metrics"""
        results = []
        
        try:
            # Get current performance metrics
            metrics = self.health_monitor.get_performance_metrics()
            
            # Validate latency
            latency_stats = metrics.get('latency_stats', {})
            avg_latency = latency_stats.get('avg', 0)
            
            if avg_latency <= self.config.thresholds['max_latency_ms']:
                latency_status = ValidationStatus.PASSED
                latency_severity = ValidationSeverity.LOW
            else:
                latency_status = ValidationStatus.FAILED
                latency_severity = ValidationSeverity.HIGH
            
            results.append(ValidationResult(
                check_name="latency_check",
                status=latency_status,
                severity=latency_severity,
                message=f"Average latency: {avg_latency:.1f}ms",
                details={
                    "avg_latency_ms": avg_latency,
                    "threshold_ms": self.config.thresholds['max_latency_ms'],
                    "latency_stats": latency_stats
                }
            ))
            
            # Validate error rate
            error_rate = metrics.get('websocket_error_rate', 0)
            
            if error_rate <= self.config.thresholds['max_error_rate']:
                error_status = ValidationStatus.PASSED
                error_severity = ValidationSeverity.LOW
            else:
                error_status = ValidationStatus.FAILED
                error_severity = ValidationSeverity.CRITICAL
            
            results.append(ValidationResult(
                check_name="error_rate_check",
                status=error_status,
                severity=error_severity,
                message=f"Error rate: {error_rate:.2%}",
                details={
                    "error_rate": error_rate,
                    "threshold": self.config.thresholds['max_error_rate']
                }
            ))
            
            # Validate throughput
            throughput = metrics.get('websocket_throughput_msgs_per_sec', 0)
            
            if throughput >= self.config.thresholds['min_throughput_msgs_per_sec']:
                throughput_status = ValidationStatus.PASSED
                throughput_severity = ValidationSeverity.LOW
            else:
                throughput_status = ValidationStatus.WARNING
                throughput_severity = ValidationSeverity.MEDIUM
            
            results.append(ValidationResult(
                check_name="throughput_check",
                status=throughput_status,
                severity=throughput_severity,
                message=f"Throughput: {throughput:.1f} msgs/sec",
                details={
                    "throughput_msgs_per_sec": throughput,
                    "threshold": self.config.thresholds['min_throughput_msgs_per_sec']
                }
            ))
            
        except Exception as e:
            results.append(ValidationResult(
                check_name="performance_metrics",
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.HIGH,
                message=f"Performance metrics validation failed: {e}",
                details={"error": str(e)}
            ))
        
        return results
    
    async def _validate_connectivity(
        self, 
        environment: str, 
        config: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate connectivity to the environment"""
        results = []
        
        try:
            start_time = time.time()
            
            # Test HTTP connectivity
            response = requests.get(config['url'], timeout=10)
            duration_ms = (time.time() - start_time) * 1000
            
            if response.status_code in [200, 404]:  # 404 is acceptable for root
                status = ValidationStatus.PASSED
                message = f"HTTP connectivity successful"
                severity = ValidationSeverity.LOW
            else:
                status = ValidationStatus.FAILED
                message = f"HTTP connectivity failed with status {response.status_code}"
                severity = ValidationSeverity.CRITICAL
            
            results.append(ValidationResult(
                check_name="http_connectivity",
                status=status,
                severity=severity,
                message=message,
                details={
                    "url": config['url'],
                    "status_code": response.status_code,
                    "response_time_ms": duration_ms
                },
                duration_ms=duration_ms
            ))
            
        except Exception as e:
            results.append(ValidationResult(
                check_name="http_connectivity",
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.CRITICAL,
                message=f"HTTP connectivity failed: {e}",
                details={"url": config['url'], "error": str(e)}
            ))
        
        return results
    
    async def _validate_websocket_functionality(
        self, 
        environment: str, 
        config: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate WebSocket functionality"""
        results = []
        
        try:
            websocket_url = config['websocket_url']
            
            # Test WebSocket connection
            async with websockets.connect(websocket_url, timeout=10) as websocket:
                # Send test message
                test_message = json.dumps({
                    "type": "health_check",
                    "timestamp": datetime.now().isoformat()
                })
                
                start_time = time.time()
                await websocket.send(test_message)
                
                # Wait for response
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                duration_ms = (time.time() - start_time) * 1000
                
                if response:
                    status = ValidationStatus.PASSED
                    message = f"WebSocket communication successful"
                    severity = ValidationSeverity.LOW
                else:
                    status = ValidationStatus.FAILED
                    message = f"WebSocket communication failed - no response"
                    severity = ValidationSeverity.HIGH
            
            results.append(ValidationResult(
                check_name="websocket_communication",
                status=status,
                severity=severity,
                message=message,
                details={
                    "websocket_url": websocket_url,
                    "response_time_ms": duration_ms,
                    "response_received": bool(response)
                },
                duration_ms=duration_ms
            ))
            
        except Exception as e:
            results.append(ValidationResult(
                check_name="websocket_communication",
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.CRITICAL,
                message=f"WebSocket functionality test failed: {e}",
                details={"websocket_url": config['websocket_url'], "error": str(e)}
            ))
        
        return results
    
    async def _validate_tunnel_health(
        self, 
        environment: str, 
        config: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate Cloudflare tunnel health"""
        results = []
        
        try:
            # Check if cloudflared process is running
            result = subprocess.run(
                ["pgrep", "-f", "cloudflared"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                status = ValidationStatus.PASSED
                message = f"Cloudflare tunnel process is running"
                severity = ValidationSeverity.LOW
                details = {"process_count": len(result.stdout.strip().split('\n'))}
            else:
                status = ValidationStatus.FAILED
                message = f"Cloudflare tunnel process not found"
                severity = ValidationSeverity.CRITICAL
                details = {"error": "Process not running"}
            
            results.append(ValidationResult(
                check_name="tunnel_process",
                status=status,
                severity=severity,
                message=message,
                details=details
            ))
            
        except Exception as e:
            results.append(ValidationResult(
                check_name="tunnel_process",
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.HIGH,
                message=f"Tunnel health check failed: {e}",
                details={"error": str(e)}
            ))
        
        return results
    
    async def _validate_monitoring_systems(
        self, 
        environment: str, 
        config: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate monitoring systems"""
        results = []
        
        try:
            # Check health monitor status
            health_status = self.health_monitor.get_all_health_status()
            
            if health_status:
                status = ValidationStatus.PASSED
                message = f"Health monitoring active for {len(health_status)} endpoints"
                severity = ValidationSeverity.LOW
            else:
                status = ValidationStatus.WARNING
                message = f"No health monitoring data available"
                severity = ValidationSeverity.MEDIUM
            
            results.append(ValidationResult(
                check_name="health_monitoring",
                status=status,
                severity=severity,
                message=message,
                details={
                    "monitored_endpoints": len(health_status),
                    "health_data_available": bool(health_status)
                }
            ))
            
            # Check endpoint monitor
            try:
                monitor_config = self.endpoint_monitor.get_config()
                if monitor_config:
                    status = ValidationStatus.PASSED
                    message = f"Endpoint monitoring configured"
                    severity = ValidationSeverity.LOW
                else:
                    status = ValidationStatus.WARNING
                    message = f"Endpoint monitoring not configured"
                    severity = ValidationSeverity.MEDIUM
            except Exception:
                status = ValidationStatus.WARNING
                message = f"Endpoint monitoring check failed"
                severity = ValidationSeverity.MEDIUM
            
            results.append(ValidationResult(
                check_name="endpoint_monitoring",
                status=status,
                severity=severity,
                message=message,
                details={"monitoring_configured": status == ValidationStatus.PASSED}
            ))
            
        except Exception as e:
            results.append(ValidationResult(
                check_name="monitoring_systems",
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.HIGH,
                message=f"Monitoring systems validation failed: {e}",
                details={"error": str(e)}
            ))
        
        return results
    
    async def _validate_quality_assurance(
        self, 
        environment: str, 
        config: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate quality assurance metrics"""
        results = []
        
        try:
            # Get quality metrics
            quality_metrics = await self.quality_metrics.collect_metrics()
            
            # Validate overall quality score
            overall_score = quality_metrics.get('overall_score', 0)
            
            if overall_score >= self.config.thresholds['min_health_score']:
                status = ValidationStatus.PASSED
                message = f"Quality score: {overall_score:.2f}"
                severity = ValidationSeverity.LOW
            else:
                status = ValidationStatus.FAILED
                message = f"Quality score below threshold: {overall_score:.2f}"
                severity = ValidationSeverity.HIGH
            
            results.append(ValidationResult(
                check_name="quality_score",
                status=status,
                severity=severity,
                message=message,
                details={
                    "quality_score": overall_score,
                    "threshold": self.config.thresholds['min_health_score'],
                    "quality_metrics": quality_metrics
                }
            ))
            
        except Exception as e:
            results.append(ValidationResult(
                check_name="quality_assurance",
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.MEDIUM,
                message=f"Quality assurance validation failed: {e}",
                details={"error": str(e)}
            ))
        
        return results
    
    async def _generate_validation_report(self, environment_results: Dict[str, Any]) -> None:
        """Generate comprehensive validation report"""
        report_dir = Path("reports")
        report_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.config.report_format == "json":
            report_path = report_dir / f"validation_report_{timestamp}.json"
            
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "validation_summary": {
                    "total_checks": len(self.validation_results),
                    "passed": len([r for r in self.validation_results if r.status == ValidationStatus.PASSED]),
                    "failed": len([r for r in self.validation_results if r.status == ValidationStatus.FAILED]),
                    "warnings": len([r for r in self.validation_results if r.status == ValidationStatus.WARNING])
                },
                "environment_results": environment_results,
                "detailed_results": [
                    {
                        "check_name": r.check_name,
                        "status": r.status.value,
                        "severity": r.severity.value,
                        "message": r.message,
                        "timestamp": r.timestamp.isoformat(),
                        "duration_ms": r.duration_ms,
                        "details": r.details
                    }
                    for r in self.validation_results
                ]
            }
            
            with open(report_path, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            self.logger.info(f"Validation report generated: {report_path}")
        
        elif self.config.report_format == "html":
            # Generate HTML report
            html_content = self._generate_html_report(environment_results)
            report_path = report_dir / f"validation_report_{timestamp}.html"
            
            with open(report_path, 'w') as f:
                f.write(html_content)
            
            self.logger.info(f"HTML validation report generated: {report_path}")
    
    def _generate_html_report(self, environment_results: Dict[str, Any]) -> str:
        """Generate HTML validation report"""
        total_checks = len(self.validation_results)
        passed_checks = len([r for r in self.validation_results if r.status == ValidationStatus.PASSED])
        failed_checks = len([r for r in self.validation_results if r.status == ValidationStatus.FAILED])
        warning_checks = len([r for r in self.validation_results if r.status == ValidationStatus.WARNING])
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Deployment Validation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
        .summary-item {{ padding: 15px; border-radius: 5px; text-align: center; }}
        .passed {{ background-color: #d4edda; color: #155724; }}
        .failed {{ background-color: #f8d7da; color: #721c24; }}
        .warning {{ background-color: #fff3cd; color: #856404; }}
        .environment {{ margin: 20px 0; border: 1px solid #ddd; border-radius: 5px; }}
        .environment-header {{ background-color: #e9ecef; padding: 10px; font-weight: bold; }}
        .environment-content {{ padding: 15px; }}
        .check {{ margin: 10px 0; padding: 10px; border-left: 4px solid; }}
        .check.passed {{ border-color: #28a745; }}
        .check.failed {{ border-color: #dc3545; }}
        .check.warning {{ border-color: #ffc107; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Deployment Validation Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <div class="summary-item passed">
            <h3>{passed_checks}</h3>
            <p>Passed</p>
        </div>
        <div class="summary-item failed">
            <h3>{failed_checks}</h3>
            <p>Failed</p>
        </div>
        <div class="summary-item warning">
            <h3>{warning_checks}</h3>
            <p>Warnings</p>
        </div>
    </div>
"""
        
        for env, result in environment_results.items():
            html += f"""
    <div class="environment">
        <div class="environment-header">
            {env.upper()} Environment - {result['overall_status'].upper()}
        </div>
        <div class="environment-content">
            <p>Total Checks: {result['total_checks']} | 
               Passed: {result['passed']} | 
               Failed: {result['failed']} | 
               Warnings: {result['warnings']}</p>
"""
            
            for check in result['validation_results']:
                status_class = check['status']
                html += f"""
            <div class="check {status_class}">
                <strong>{check['check_name']}</strong> - {check['message']}
                <br><small>Severity: {check['severity']} | Duration: {check['duration_ms']:.1f}ms</small>
            </div>
"""
            
            html += """
        </div>
    </div>
"""
        
        html += """
</body>
</html>
"""
        
        return html


async def main():
    """Main entry point for validation script"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate WebSocket deployment")
    parser.add_argument("--environments", nargs="+", 
                       choices=["dev", "staging", "production"],
                       default=["dev", "staging", "production"],
                       help="Environments to validate")
    parser.add_argument("--types", nargs="+",
                       choices=["health_check", "performance", "connectivity", 
                               "websocket", "tunnel", "monitoring", "quality_assurance"],
                       default=["health_check", "performance", "connectivity", 
                               "websocket", "tunnel", "monitoring", "quality_assurance"],
                       help="Validation types to run")
    parser.add_argument("--config", type=str,
                       help="Path to validation configuration file")
    parser.add_argument("--report-format", choices=["json", "html", "text"],
                       default="json", help="Report format")
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = DeploymentValidator(args.config)
    
    # Set report format
    validator.config.report_format = args.report_format
    
    try:
        # Execute validation
        result = await validator.validate_deployment(
            environments=args.environments,
            validation_types=args.types
        )
        
        # Print results
        print("\n" + "="*60)
        print("VALIDATION RESULTS")
        print("="*60)
        print(json.dumps(result, indent=2, default=str))
        
        # Exit with appropriate code
        if result["overall_status"] == "passed":
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nValidation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())