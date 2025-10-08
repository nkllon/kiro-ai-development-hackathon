#!/usr/bin/env python3
"""
Deployment Validation Suite
Task 7.2: Deployment Automation and Validation

This script provides comprehensive post-deployment validation including:
- Health checks for all environments
- WebSocket functionality validation
- Performance metrics validation
- Configuration validation
- Automated rollback triggers
"""

import asyncio
import json
import logging
import time
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import aiohttp
import websockets
from websockets.exceptions import ConnectionClosed, InvalidStatusCode

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.beast_mode.observatory.tunnel.tunnel_config_manager import TunnelConfigManager
from src.beast_mode.observatory.websocket.manager import WebSocketManager, WebSocketManagerConfig


class ValidationStatus(Enum):
    """Validation status enumeration."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


class ValidationSeverity(Enum):
    """Validation severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ValidationResult:
    """Result of a validation check."""
    name: str
    status: ValidationStatus
    severity: ValidationSeverity
    message: str
    details: Dict[str, Any] = None
    execution_time_ms: float = 0.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.details is None:
            self.details = {}


@dataclass
class ValidationSuite:
    """Complete validation suite results."""
    suite_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    overall_status: ValidationStatus = ValidationStatus.PASSED
    results: List[ValidationResult] = None
    summary: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.results is None:
            self.results = []
        if self.summary is None:
            self.summary = {}


class DeploymentValidator:
    """Comprehensive deployment validation system."""
    
    def __init__(self, config_path: str = "deployment-config.yml"):
        """Initialize deployment validator."""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.tunnel_manager = TunnelConfigManager()
        self.logger = self._setup_logging()
        
        self.log_action("deployment_validator_init", "completed", {
            "config_path": str(self.config_path),
            "environments": list(self.config.environments.keys())
        })
    
    def _load_config(self) -> Dict[str, Any]:
        """Load deployment configuration."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger("deployment_validator")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def log_action(self, action: str, status: str, details: Dict[str, Any] = None):
        """Log action in JSON format as required."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task": "7.2",
            "action": f"DeploymentValidator.{action}",
            "status": status,
            "details": details or {}
        }
        print(json.dumps(log_entry))
    
    async def validate_deployment(self, 
                                environment: str = "production",
                                validate_all_envs: bool = False) -> ValidationSuite:
        """Perform comprehensive deployment validation."""
        start_time = datetime.now()
        
        self.log_action("validate_deployment_start", "in_progress", {
            "environment": environment,
            "validate_all_envs": validate_all_envs
        })
        
        suite = ValidationSuite(
            suite_name=f"deployment_validation_{environment}",
            start_time=start_time
        )
        
        try:
            # Determine environments to validate
            if validate_all_envs:
                environments = list(self.config["environments"].keys())
            else:
                environments = [environment]
            
            # Run validation for each environment
            for env in environments:
                env_results = await self._validate_environment(env)
                suite.results.extend(env_results)
            
            # Run cross-environment validations
            cross_env_results = await self._validate_cross_environment()
            suite.results.extend(cross_env_results)
            
            # Run configuration validations
            config_results = await self._validate_configuration()
            suite.results.extend(config_results)
            
            # Run performance validations
            performance_results = await self._validate_performance(environment)
            suite.results.extend(performance_results)
            
            # Run security validations
            security_results = await self._validate_security(environment)
            suite.results.extend(security_results)
            
            # Calculate overall status
            suite.overall_status = self._calculate_overall_status(suite.results)
            suite.end_time = datetime.now()
            suite.summary = self._generate_summary(suite.results)
            
            self.log_action("validate_deployment_complete", "completed", {
                "environment": environment,
                "overall_status": suite.overall_status.value,
                "total_checks": len(suite.results),
                "duration_seconds": (suite.end_time - suite.start_time).total_seconds()
            })
            
        except Exception as e:
            suite.end_time = datetime.now()
            suite.overall_status = ValidationStatus.FAILED
            
            error_result = ValidationResult(
                name="validation_suite_error",
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.CRITICAL,
                message=f"Validation suite failed: {str(e)}",
                details={"error_type": type(e).__name__}
            )
            suite.results.append(error_result)
            
            self.log_action("validate_deployment_error", "error", {"error": str(e)})
        
        return suite
    
    async def _validate_environment(self, environment: str) -> List[ValidationResult]:
        """Validate a specific environment."""
        self.log_action("validate_environment", "in_progress", {"environment": environment})
        
        results = []
        env_config = self.config["environments"][environment]
        
        try:
            # HTTP Health Check
            http_result = await self._validate_http_health(environment, env_config)
            results.append(http_result)
            
            # WebSocket Health Check
            websocket_result = await self._validate_websocket_health(environment, env_config)
            results.append(websocket_result)
            
            # Response Time Check
            response_time_result = await self._validate_response_time(environment, env_config)
            results.append(response_time_result)
            
            # WebSocket Endpoints Check
            endpoints_result = await self._validate_websocket_endpoints(environment, env_config)
            results.append(endpoints_result)
            
            # Tunnel Configuration Check
            tunnel_result = await self._validate_tunnel_configuration(environment)
            results.append(tunnel_result)
            
            self.log_action("validate_environment", "completed", {
                "environment": environment,
                "checks_performed": len(results)
            })
            
        except Exception as e:
            error_result = ValidationResult(
                name=f"environment_validation_error_{environment}",
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.CRITICAL,
                message=f"Environment validation failed: {str(e)}",
                details={"environment": environment, "error": str(e)}
            )
            results.append(error_result)
            self.log_action("validate_environment", "error", {"environment": environment, "error": str(e)})
        
        return results
    
    async def _validate_http_health(self, environment: str, env_config: Dict[str, Any]) -> ValidationResult:
        """Validate HTTP health endpoint."""
        start_time = time.time()
        
        try:
            health_url = f"{env_config['url']}{env_config['health_endpoint']}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(health_url, timeout=10) as response:
                    execution_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        return ValidationResult(
                            name=f"http_health_{environment}",
                            status=ValidationStatus.PASSED,
                            severity=ValidationSeverity.HIGH,
                            message=f"HTTP health check passed for {environment}",
                            details={
                                "url": health_url,
                                "status_code": response.status,
                                "response_time_ms": execution_time
                            },
                            execution_time_ms=execution_time
                        )
                    else:
                        return ValidationResult(
                            name=f"http_health_{environment}",
                            status=ValidationStatus.FAILED,
                            severity=ValidationSeverity.CRITICAL,
                            message=f"HTTP health check failed for {environment}: Status {response.status}",
                            details={
                                "url": health_url,
                                "status_code": response.status,
                                "response_time_ms": execution_time
                            },
                            execution_time_ms=execution_time
                        )
                        
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return ValidationResult(
                name=f"http_health_{environment}",
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.CRITICAL,
                message=f"HTTP health check failed for {environment}: {str(e)}",
                details={
                    "url": f"{env_config['url']}{env_config['health_endpoint']}",
                    "error": str(e),
                    "response_time_ms": execution_time
                },
                execution_time_ms=execution_time
            )
    
    async def _validate_websocket_health(self, environment: str, env_config: Dict[str, Any]) -> ValidationResult:
        """Validate WebSocket health."""
        start_time = time.time()
        
        try:
            websocket_url = env_config["websocket_url"]
            
            async with websockets.connect(websocket_url, timeout=10) as websocket:
                # Test basic connectivity
                await websocket.ping()
                
                # Test message sending
                test_message = {
                    "type": "health_check",
                    "timestamp": datetime.now().isoformat(),
                    "environment": environment
                }
                await websocket.send(json.dumps(test_message))
                
                execution_time = (time.time() - start_time) * 1000
                
                return ValidationResult(
                    name=f"websocket_health_{environment}",
                    status=ValidationStatus.PASSED,
                    severity=ValidationSeverity.HIGH,
                    message=f"WebSocket health check passed for {environment}",
                    details={
                        "url": websocket_url,
                        "connection_time_ms": execution_time,
                        "message_test": True
                    },
                    execution_time_ms=execution_time
                )
                
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return ValidationResult(
                name=f"websocket_health_{environment}",
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.CRITICAL,
                message=f"WebSocket health check failed for {environment}: {str(e)}",
                details={
                    "url": env_config["websocket_url"],
                    "error": str(e),
                    "response_time_ms": execution_time
                },
                execution_time_ms=execution_time
            )
    
    async def _validate_response_time(self, environment: str, env_config: Dict[str, Any]) -> ValidationResult:
        """Validate response time."""
        start_time = time.time()
        
        try:
            base_url = env_config["url"]
            expected_time = env_config.get("expected_response_time_ms", 2000)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(base_url, timeout=15) as response:
                    execution_time = (time.time() - start_time) * 1000
                    
                    if execution_time <= expected_time:
                        return ValidationResult(
                            name=f"response_time_{environment}",
                            status=ValidationStatus.PASSED,
                            severity=ValidationSeverity.MEDIUM,
                            message=f"Response time check passed for {environment}",
                            details={
                                "url": base_url,
                                "response_time_ms": execution_time,
                                "expected_time_ms": expected_time,
                                "status_code": response.status
                            },
                            execution_time_ms=execution_time
                        )
                    else:
                        return ValidationResult(
                            name=f"response_time_{environment}",
                            status=ValidationStatus.WARNING,
                            severity=ValidationSeverity.MEDIUM,
                            message=f"Response time exceeded threshold for {environment}",
                            details={
                                "url": base_url,
                                "response_time_ms": execution_time,
                                "expected_time_ms": expected_time,
                                "status_code": response.status
                            },
                            execution_time_ms=execution_time
                        )
                        
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return ValidationResult(
                name=f"response_time_{environment}",
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.HIGH,
                message=f"Response time check failed for {environment}: {str(e)}",
                details={
                    "url": env_config["url"],
                    "error": str(e),
                    "response_time_ms": execution_time
                },
                execution_time_ms=execution_time
            )
    
    async def _validate_websocket_endpoints(self, environment: str, env_config: Dict[str, Any]) -> ValidationResult:
        """Validate all WebSocket endpoints."""
        start_time = time.time()
        
        try:
            websocket_url = env_config["websocket_url"]
            endpoints = ["/ws/emoji-rain", "/ws/observatory", "/ws/anomalies", "/ws/doctor-status"]
            
            endpoint_results = {}
            failed_endpoints = []
            
            for endpoint in endpoints:
                full_url = f"{websocket_url}{endpoint}"
                try:
                    async with websockets.connect(full_url, timeout=10) as websocket:
                        await websocket.ping()
                        
                        # Test message functionality
                        test_message = {
                            "type": "endpoint_test",
                            "endpoint": endpoint,
                            "timestamp": datetime.now().isoformat()
                        }
                        await websocket.send(json.dumps(test_message))
                        
                        endpoint_results[endpoint] = {
                            "status": "healthy",
                            "connectivity": True,
                            "message_test": True
                        }
                        
                except Exception as e:
                    endpoint_results[endpoint] = {
                        "status": "unhealthy",
                        "error": str(e)
                    }
                    failed_endpoints.append(endpoint)
            
            execution_time = (time.time() - start_time) * 1000
            
            if not failed_endpoints:
                return ValidationResult(
                    name=f"websocket_endpoints_{environment}",
                    status=ValidationStatus.PASSED,
                    severity=ValidationSeverity.HIGH,
                    message=f"All WebSocket endpoints healthy for {environment}",
                    details={
                        "environment": environment,
                        "endpoints_tested": len(endpoints),
                        "healthy_endpoints": len(endpoints) - len(failed_endpoints),
                        "failed_endpoints": failed_endpoints,
                        "endpoint_results": endpoint_results
                    },
                    execution_time_ms=execution_time
                )
            else:
                return ValidationResult(
                    name=f"websocket_endpoints_{environment}",
                    status=ValidationStatus.FAILED,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"WebSocket endpoints failed for {environment}: {failed_endpoints}",
                    details={
                        "environment": environment,
                        "endpoints_tested": len(endpoints),
                        "healthy_endpoints": len(endpoints) - len(failed_endpoints),
                        "failed_endpoints": failed_endpoints,
                        "endpoint_results": endpoint_results
                    },
                    execution_time_ms=execution_time
                )
                
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return ValidationResult(
                name=f"websocket_endpoints_{environment}",
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.CRITICAL,
                message=f"WebSocket endpoints validation failed for {environment}: {str(e)}",
                details={
                    "environment": environment,
                    "error": str(e)
                },
                execution_time_ms=execution_time
            )
    
    async def _validate_tunnel_configuration(self, environment: str) -> ValidationResult:
        """Validate tunnel configuration."""
        start_time = time.time()
        
        try:
            config_info = self.tunnel_manager.get_config_info()
            execution_time = (time.time() - start_time) * 1000
            
            validation_status = config_info.get("validation_status", "unknown")
            websocket_enabled = config_info.get("websocket_enabled", False)
            validation_errors = config_info.get("validation_errors", [])
            
            if validation_status == "valid" and websocket_enabled:
                return ValidationResult(
                    name=f"tunnel_config_{environment}",
                    status=ValidationStatus.PASSED,
                    severity=ValidationSeverity.HIGH,
                    message=f"Tunnel configuration valid for {environment}",
                    details={
                        "environment": environment,
                        "validation_status": validation_status,
                        "websocket_enabled": websocket_enabled,
                        "tunnel_name": config_info.get("tunnel_name"),
                        "hostnames": config_info.get("hostnames", [])
                    },
                    execution_time_ms=execution_time
                )
            else:
                return ValidationResult(
                    name=f"tunnel_config_{environment}",
                    status=ValidationStatus.FAILED,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Tunnel configuration invalid for {environment}",
                    details={
                        "environment": environment,
                        "validation_status": validation_status,
                        "websocket_enabled": websocket_enabled,
                        "validation_errors": validation_errors
                    },
                    execution_time_ms=execution_time
                )
                
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return ValidationResult(
                name=f"tunnel_config_{environment}",
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.CRITICAL,
                message=f"Tunnel configuration validation failed for {environment}: {str(e)}",
                details={
                    "environment": environment,
                    "error": str(e)
                },
                execution_time_ms=execution_time
            )
    
    async def _validate_cross_environment(self) -> List[ValidationResult]:
        """Validate cross-environment consistency."""
        self.log_action("validate_cross_environment", "in_progress")
        
        results = []
        
        try:
            # Check environment consistency
            environments = self.config["environments"]
            
            # Validate that all environments have required fields
            required_fields = ["url", "websocket_url", "health_endpoint"]
            missing_fields = {}
            
            for env_name, env_config in environments.items():
                missing = [field for field in required_fields if field not in env_config]
                if missing:
                    missing_fields[env_name] = missing
            
            if missing_fields:
                results.append(ValidationResult(
                    name="cross_environment_config_consistency",
                    status=ValidationStatus.FAILED,
                    severity=ValidationSeverity.HIGH,
                    message="Environment configuration inconsistency detected",
                    details={"missing_fields": missing_fields}
                ))
            else:
                results.append(ValidationResult(
                    name="cross_environment_config_consistency",
                    status=ValidationStatus.PASSED,
                    severity=ValidationSeverity.MEDIUM,
                    message="Environment configuration consistency validated",
                    details={"environments_checked": list(environments.keys())}
                ))
            
            # Check URL format consistency
            url_format_issues = []
            for env_name, env_config in environments.items():
                url = env_config.get("url", "")
                websocket_url = env_config.get("websocket_url", "")
                
                if not url.startswith(("http://", "https://")):
                    url_format_issues.append(f"{env_name}.url: Invalid protocol")
                
                if not websocket_url.startswith(("ws://", "wss://")):
                    url_format_issues.append(f"{env_name}.websocket_url: Invalid protocol")
            
            if url_format_issues:
                results.append(ValidationResult(
                    name="cross_environment_url_format",
                    status=ValidationStatus.FAILED,
                    severity=ValidationSeverity.MEDIUM,
                    message="URL format issues detected",
                    details={"url_format_issues": url_format_issues}
                ))
            else:
                results.append(ValidationResult(
                    name="cross_environment_url_format",
                    status=ValidationStatus.PASSED,
                    severity=ValidationSeverity.LOW,
                    message="URL format consistency validated",
                    details={"environments_checked": list(environments.keys())}
                ))
            
            self.log_action("validate_cross_environment", "completed", {
                "checks_performed": len(results)
            })
            
        except Exception as e:
            results.append(ValidationResult(
                name="cross_environment_validation_error",
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.CRITICAL,
                message=f"Cross-environment validation failed: {str(e)}",
                details={"error": str(e)}
            ))
            self.log_action("validate_cross_environment", "error", {"error": str(e)})
        
        return results
    
    async def _validate_configuration(self) -> List[ValidationResult]:
        """Validate deployment configuration."""
        self.log_action("validate_configuration", "in_progress")
        
        results = []
        
        try:
            # Check required configuration sections
            required_sections = ["environments", "health_check_timeout", "rollback_timeout"]
            missing_sections = [section for section in required_sections if section not in self.config]
            
            if missing_sections:
                results.append(ValidationResult(
                    name="configuration_completeness",
                    status=ValidationStatus.FAILED,
                    severity=ValidationSeverity.CRITICAL,
                    message="Missing required configuration sections",
                    details={"missing_sections": missing_sections}
                ))
            else:
                results.append(ValidationResult(
                    name="configuration_completeness",
                    status=ValidationStatus.PASSED,
                    severity=ValidationSeverity.HIGH,
                    message="Configuration completeness validated",
                    details={"sections_checked": required_sections}
                ))
            
            # Check validation thresholds
            validation_thresholds = self.config.get("validation_thresholds", {})
            if validation_thresholds:
                results.append(ValidationResult(
                    name="validation_thresholds",
                    status=ValidationStatus.PASSED,
                    severity=ValidationSeverity.MEDIUM,
                    message="Validation thresholds configured",
                    details={"thresholds": validation_thresholds}
                ))
            else:
                results.append(ValidationResult(
                    name="validation_thresholds",
                    status=ValidationStatus.WARNING,
                    severity=ValidationSeverity.MEDIUM,
                    message="No validation thresholds configured",
                    details={}
                ))
            
            # Check rollback triggers
            rollback_triggers = self.config.get("rollback_triggers", {})
            if rollback_triggers:
                enabled_triggers = [name for name, config in rollback_triggers.items() 
                                  if config.get("enabled", False)]
                results.append(ValidationResult(
                    name="rollback_triggers",
                    status=ValidationStatus.PASSED,
                    severity=ValidationSeverity.HIGH,
                    message="Rollback triggers configured",
                    details={"enabled_triggers": enabled_triggers}
                ))
            else:
                results.append(ValidationResult(
                    name="rollback_triggers",
                    status=ValidationStatus.WARNING,
                    severity=ValidationSeverity.HIGH,
                    message="No rollback triggers configured",
                    details={}
                ))
            
            self.log_action("validate_configuration", "completed", {
                "checks_performed": len(results)
            })
            
        except Exception as e:
            results.append(ValidationResult(
                name="configuration_validation_error",
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.CRITICAL,
                message=f"Configuration validation failed: {str(e)}",
                details={"error": str(e)}
            ))
            self.log_action("validate_configuration", "error", {"error": str(e)})
        
        return results
    
    async def _validate_performance(self, environment: str) -> List[ValidationResult]:
        """Validate performance metrics."""
        self.log_action("validate_performance", "in_progress", {"environment": environment})
        
        results = []
        
        try:
            env_config = self.config["environments"][environment]
            validation_thresholds = self.config.get("validation_thresholds", {})
            
            # Response time validation
            max_response_time = validation_thresholds.get("max_response_time_ms", 2000)
            response_time_result = await self._validate_response_time(environment, env_config)
            results.append(response_time_result)
            
            # Throughput validation (simplified)
            throughput_result = await self._validate_throughput(environment, env_config)
            results.append(throughput_result)
            
            # Connection failure rate validation
            connection_failure_result = await self._validate_connection_failure_rate(environment, env_config)
            results.append(connection_failure_result)
            
            self.log_action("validate_performance", "completed", {
                "environment": environment,
                "checks_performed": len(results)
            })
            
        except Exception as e:
            results.append(ValidationResult(
                name="performance_validation_error",
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.CRITICAL,
                message=f"Performance validation failed: {str(e)}",
                details={"environment": environment, "error": str(e)}
            ))
            self.log_action("validate_performance", "error", {"environment": environment, "error": str(e)})
        
        return results
    
    async def _validate_throughput(self, environment: str, env_config: Dict[str, Any]) -> ValidationResult:
        """Validate message throughput."""
        start_time = time.time()
        
        try:
            websocket_url = env_config["websocket_url"]
            min_throughput = self.config.get("validation_thresholds", {}).get("min_throughput_msgs_per_sec", 1.0)
            
            # Test message throughput
            message_count = 10
            test_start = time.time()
            
            async with websockets.connect(websocket_url, timeout=10) as websocket:
                for i in range(message_count):
                    test_message = {
                        "type": "throughput_test",
                        "message_id": i,
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send(json.dumps(test_message))
                
                # Wait for responses or timeout
                await asyncio.sleep(1)
            
            test_duration = time.time() - test_start
            actual_throughput = message_count / test_duration if test_duration > 0 else 0
            
            execution_time = (time.time() - start_time) * 1000
            
            if actual_throughput >= min_throughput:
                return ValidationResult(
                    name=f"throughput_{environment}",
                    status=ValidationStatus.PASSED,
                    severity=ValidationSeverity.MEDIUM,
                    message=f"Throughput validation passed for {environment}",
                    details={
                        "environment": environment,
                        "actual_throughput": actual_throughput,
                        "min_throughput": min_throughput,
                        "messages_sent": message_count,
                        "test_duration": test_duration
                    },
                    execution_time_ms=execution_time
                )
            else:
                return ValidationResult(
                    name=f"throughput_{environment}",
                    status=ValidationStatus.WARNING,
                    severity=ValidationSeverity.MEDIUM,
                    message=f"Throughput below threshold for {environment}",
                    details={
                        "environment": environment,
                        "actual_throughput": actual_throughput,
                        "min_throughput": min_throughput,
                        "messages_sent": message_count,
                        "test_duration": test_duration
                    },
                    execution_time_ms=execution_time
                )
                
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return ValidationResult(
                name=f"throughput_{environment}",
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.MEDIUM,
                message=f"Throughput validation failed for {environment}: {str(e)}",
                details={
                    "environment": environment,
                    "error": str(e)
                },
                execution_time_ms=execution_time
            )
    
    async def _validate_connection_failure_rate(self, environment: str, env_config: Dict[str, Any]) -> ValidationResult:
        """Validate connection failure rate."""
        start_time = time.time()
        
        try:
            websocket_url = env_config["websocket_url"]
            max_failure_rate = self.config.get("validation_thresholds", {}).get("max_connection_failure_rate", 0.1)
            
            # Test multiple connections
            connection_attempts = 10
            successful_connections = 0
            failed_connections = 0
            
            for i in range(connection_attempts):
                try:
                    async with websockets.connect(websocket_url, timeout=5) as websocket:
                        await websocket.ping()
                        successful_connections += 1
                except Exception:
                    failed_connections += 1
            
            failure_rate = failed_connections / connection_attempts if connection_attempts > 0 else 0
            
            execution_time = (time.time() - start_time) * 1000
            
            if failure_rate <= max_failure_rate:
                return ValidationResult(
                    name=f"connection_failure_rate_{environment}",
                    status=ValidationStatus.PASSED,
                    severity=ValidationSeverity.HIGH,
                    message=f"Connection failure rate acceptable for {environment}",
                    details={
                        "environment": environment,
                        "failure_rate": failure_rate,
                        "max_failure_rate": max_failure_rate,
                        "successful_connections": successful_connections,
                        "failed_connections": failed_connections,
                        "total_attempts": connection_attempts
                    },
                    execution_time_ms=execution_time
                )
            else:
                return ValidationResult(
                    name=f"connection_failure_rate_{environment}",
                    status=ValidationStatus.FAILED,
                    severity=ValidationSeverity.HIGH,
                    message=f"Connection failure rate too high for {environment}",
                    details={
                        "environment": environment,
                        "failure_rate": failure_rate,
                        "max_failure_rate": max_failure_rate,
                        "successful_connections": successful_connections,
                        "failed_connections": failed_connections,
                        "total_attempts": connection_attempts
                    },
                    execution_time_ms=execution_time
                )
                
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return ValidationResult(
                name=f"connection_failure_rate_{environment}",
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.HIGH,
                message=f"Connection failure rate validation failed for {environment}: {str(e)}",
                details={
                    "environment": environment,
                    "error": str(e)
                },
                execution_time_ms=execution_time
            )
    
    async def _validate_security(self, environment: str) -> List[ValidationResult]:
        """Validate security aspects."""
        self.log_action("validate_security", "in_progress", {"environment": environment})
        
        results = []
        
        try:
            env_config = self.config["environments"][environment]
            
            # Check HTTPS/WSS usage
            url = env_config.get("url", "")
            websocket_url = env_config.get("websocket_url", "")
            
            if url.startswith("https://") and websocket_url.startswith("wss://"):
                results.append(ValidationResult(
                    name=f"secure_protocols_{environment}",
                    status=ValidationStatus.PASSED,
                    severity=ValidationSeverity.HIGH,
                    message=f"Secure protocols (HTTPS/WSS) used for {environment}",
                    details={
                        "environment": environment,
                        "http_protocol": "https",
                        "websocket_protocol": "wss"
                    }
                ))
            else:
                results.append(ValidationResult(
                    name=f"secure_protocols_{environment}",
                    status=ValidationStatus.WARNING,
                    severity=ValidationSeverity.MEDIUM,
                    message=f"Insecure protocols detected for {environment}",
                    details={
                        "environment": environment,
                        "http_protocol": "https" if url.startswith("https://") else "http",
                        "websocket_protocol": "wss" if websocket_url.startswith("wss://") else "ws"
                    }
                ))
            
            # Check tunnel configuration security
            tunnel_security_result = await self._validate_tunnel_security(environment)
            results.append(tunnel_security_result)
            
            self.log_action("validate_security", "completed", {
                "environment": environment,
                "checks_performed": len(results)
            })
            
        except Exception as e:
            results.append(ValidationResult(
                name="security_validation_error",
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.CRITICAL,
                message=f"Security validation failed: {str(e)}",
                details={"environment": environment, "error": str(e)}
            ))
            self.log_action("validate_security", "error", {"environment": environment, "error": str(e)})
        
        return results
    
    async def _validate_tunnel_security(self, environment: str) -> ValidationResult:
        """Validate tunnel security configuration."""
        start_time = time.time()
        
        try:
            config_info = self.tunnel_manager.get_config_info()
            execution_time = (time.time() - start_time) * 1000
            
            # Check if tunnel configuration exists and is valid
            if config_info.get("validation_status") == "valid":
                return ValidationResult(
                    name=f"tunnel_security_{environment}",
                    status=ValidationStatus.PASSED,
                    severity=ValidationSeverity.HIGH,
                    message=f"Tunnel security configuration valid for {environment}",
                    details={
                        "environment": environment,
                        "validation_status": "valid",
                        "websocket_enabled": config_info.get("websocket_enabled", False)
                    },
                    execution_time_ms=execution_time
                )
            else:
                return ValidationResult(
                    name=f"tunnel_security_{environment}",
                    status=ValidationStatus.WARNING,
                    severity=ValidationSeverity.MEDIUM,
                    message=f"Tunnel security configuration needs review for {environment}",
                    details={
                        "environment": environment,
                        "validation_status": config_info.get("validation_status", "unknown"),
                        "validation_errors": config_info.get("validation_errors", [])
                    },
                    execution_time_ms=execution_time
                )
                
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return ValidationResult(
                name=f"tunnel_security_{environment}",
                status=ValidationStatus.FAILED,
                severity=ValidationSeverity.HIGH,
                message=f"Tunnel security validation failed for {environment}: {str(e)}",
                details={
                    "environment": environment,
                    "error": str(e)
                },
                execution_time_ms=execution_time
            )
    
    def _calculate_overall_status(self, results: List[ValidationResult]) -> ValidationStatus:
        """Calculate overall validation status."""
        if not results:
            return ValidationStatus.FAILED
        
        # Check for any critical failures
        critical_failures = [r for r in results if r.severity == ValidationSeverity.CRITICAL and r.status == ValidationStatus.FAILED]
        if critical_failures:
            return ValidationStatus.FAILED
        
        # Check for any failures
        failures = [r for r in results if r.status == ValidationStatus.FAILED]
        if failures:
            return ValidationStatus.FAILED
        
        # Check for warnings
        warnings = [r for r in results if r.status == ValidationStatus.WARNING]
        if warnings:
            return ValidationStatus.WARNING
        
        return ValidationStatus.PASSED
    
    def _generate_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Generate validation summary."""
        total_checks = len(results)
        passed_checks = len([r for r in results if r.status == ValidationStatus.PASSED])
        failed_checks = len([r for r in results if r.status == ValidationStatus.FAILED])
        warning_checks = len([r for r in results if r.status == ValidationStatus.WARNING])
        
        # Group by severity
        critical_checks = len([r for r in results if r.severity == ValidationSeverity.CRITICAL])
        high_checks = len([r for r in results if r.severity == ValidationSeverity.HIGH])
        medium_checks = len([r for r in results if r.severity == ValidationSeverity.MEDIUM])
        low_checks = len([r for r in results if r.severity == ValidationSeverity.LOW])
        
        # Calculate average execution time
        avg_execution_time = sum(r.execution_time_ms for r in results) / total_checks if total_checks > 0 else 0
        
        return {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "warning_checks": warning_checks,
            "critical_checks": critical_checks,
            "high_checks": high_checks,
            "medium_checks": medium_checks,
            "low_checks": low_checks,
            "average_execution_time_ms": avg_execution_time,
            "success_rate": (passed_checks / total_checks * 100) if total_checks > 0 else 0
        }


async def main():
    """Main entry point for validation script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate deployment")
    parser.add_argument("--environment", choices=["dev", "staging", "production"], 
                       default="production", help="Environment to validate")
    parser.add_argument("--all-environments", action="store_true",
                       help="Validate all environments")
    parser.add_argument("--config", default="deployment-config.yml",
                       help="Path to deployment configuration file")
    parser.add_argument("--output", choices=["json", "text"], default="json",
                       help="Output format")
    
    args = parser.parse_args()
    
    try:
        # Initialize validator
        validator = DeploymentValidator(args.config)
        
        # Run validation
        suite = await validator.validate_deployment(
            environment=args.environment,
            validate_all_envs=args.all_environments
        )
        
        # Generate output
        if args.output == "json":
            output_data = {
                "suite_name": suite.suite_name,
                "start_time": suite.start_time.isoformat(),
                "end_time": suite.end_time.isoformat() if suite.end_time else None,
                "overall_status": suite.overall_status.value,
                "summary": suite.summary,
                "results": [
                    {
                        "name": r.name,
                        "status": r.status.value,
                        "severity": r.severity.value,
                        "message": r.message,
                        "details": r.details,
                        "execution_time_ms": r.execution_time_ms,
                        "timestamp": r.timestamp.isoformat()
                    }
                    for r in suite.results
                ]
            }
            print(json.dumps(output_data, indent=2, default=str))
        else:
            # Text output
            print(f"\n{'='*80}")
            print(f"DEPLOYMENT VALIDATION REPORT")
            print(f"{'='*80}")
            print(f"Suite: {suite.suite_name}")
            print(f"Start Time: {suite.start_time}")
            print(f"End Time: {suite.end_time}")
            print(f"Overall Status: {suite.overall_status.value.upper()}")
            print(f"\nSUMMARY:")
            print(f"  Total Checks: {suite.summary['total_checks']}")
            print(f"  Passed: {suite.summary['passed_checks']}")
            print(f"  Failed: {suite.summary['failed_checks']}")
            print(f"  Warnings: {suite.summary['warning_checks']}")
            print(f"  Success Rate: {suite.summary['success_rate']:.1f}%")
            print(f"  Avg Execution Time: {suite.summary['average_execution_time_ms']:.1f}ms")
            
            print(f"\nRESULTS:")
            for result in suite.results:
                status_icon = "✅" if result.status == ValidationStatus.PASSED else "❌" if result.status == ValidationStatus.FAILED else "⚠️"
                print(f"  {status_icon} {result.name} ({result.severity.value})")
                print(f"     {result.message}")
                if result.details:
                    for key, value in result.details.items():
                        print(f"     {key}: {value}")
                print(f"     Execution Time: {result.execution_time_ms:.1f}ms")
                print()
        
        # Exit with appropriate code
        if suite.overall_status == ValidationStatus.PASSED:
            print("\n✅ Validation completed successfully!")
            sys.exit(0)
        elif suite.overall_status == ValidationStatus.WARNING:
            print("\n⚠️ Validation completed with warnings!")
            sys.exit(1)
        else:
            print("\n❌ Validation failed!")
            sys.exit(2)
            
    except Exception as e:
        print(f"\n❌ Validation error: {e}")
        sys.exit(3)


if __name__ == "__main__":
    asyncio.run(main())