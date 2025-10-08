#!/usr/bin/env python3
"""
Real-time Validation System - Phase 5 Task 5.2

Validates generated documentation against actual system behavior with real-time
monitoring, WebSocket integration, and automated accuracy tracking.
"""

import asyncio
import aiohttp
import websockets
import json
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import time

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


@dataclass
class ValidationRule:
    """Represents a validation rule for documentation accuracy."""
    rule_id: str
    rule_type: str  # 'websocket', 'makefile', 'endpoint', 'service'
    target: str
    expected_result: Any
    tolerance: float = 0.0
    enabled: bool = True
    last_validated: Optional[datetime] = None
    validation_count: int = 0
    success_count: int = 0


@dataclass
class ValidationResult:
    """Result of a validation check."""
    rule_id: str
    timestamp: datetime
    success: bool
    actual_result: Any
    expected_result: Any
    error_message: Optional[str] = None
    response_time_ms: Optional[float] = None
    correlation_id: Optional[str] = None


class RealTimeValidator(ReflectiveModule):
    """
    Real-time validation system that continuously validates documentation
    accuracy against live system behavior.
    """
    
    def __init__(self):
        super().__init__()
        self.validation_rules: Dict[str, ValidationRule] = {}
        self.validation_results: List[ValidationResult] = []
        self.websocket_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.observatory_ws_client = None
        self.accuracy_threshold = 0.95
        self.validation_interval = 60  # seconds
        self.is_running = False
        
        # Initialize metrics
        self.metrics.update({
            'total_validations': 0,
            'successful_validations': 0,
            'failed_validations': 0,
            'accuracy_score': 0.0,
            'websocket_connections': 0,
            'endpoint_response_time_avg': 0.0,
            'makefile_validations': 0,
            'last_validation_timestamp': 0
        })
        
        self.logger.info("RealTimeValidator initialized")
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the real-time validation system."""
        correlation_id = self.generate_correlation_id()
        
        try:
            # Load validation rules
            await self._load_validation_rules()
            
            # Initialize WebSocket connections
            await self._initialize_websocket_connections()
            
            # Start validation loops
            asyncio.create_task(self._continuous_validation_loop())
            asyncio.create_task(self._websocket_monitoring_loop())
            asyncio.create_task(self._accuracy_monitoring_loop())
            
            self.is_running = True
            
            self.logger.info("RealTimeValidator initialized successfully",
                           extra={"correlation_id": correlation_id})
            
            return {
                "status": "initialized",
                "validation_rules_count": len(self.validation_rules),
                "websocket_connections": len(self.websocket_connections),
                "correlation_id": correlation_id
            }
            
        except Exception as e:
            self.logger.error(f"Failed to initialize RealTimeValidator: {e}",
                            extra={"correlation_id": correlation_id})
            return {
                "status": "failed",
                "error": str(e),
                "correlation_id": correlation_id
            }
    
    async def _load_validation_rules(self):
        """Load validation rules from configuration."""
        # Default validation rules for Observatory system
        default_rules = [
            # WebSocket endpoint validations
            ValidationRule(
                rule_id="ws_observatory_health",
                rule_type="websocket",
                target="ws://localhost:8888/ws/observatory",
                expected_result="connection_success"
            ),
            ValidationRule(
                rule_id="ws_emoji_rain_health",
                rule_type="websocket", 
                target="ws://localhost:8888/ws/emoji-rain",
                expected_result="connection_success"
            ),
            ValidationRule(
                rule_id="ws_anomalies_health",
                rule_type="websocket",
                target="ws://localhost:8888/ws/anomalies", 
                expected_result="connection_success"
            ),
            ValidationRule(
                rule_id="ws_doctor_status_health",
                rule_type="websocket",
                target="ws://localhost:8888/ws/doctor-status",
                expected_result="connection_success"
            ),
            
            # HTTP endpoint validations
            ValidationRule(
                rule_id="observatory_health_endpoint",
                rule_type="endpoint",
                target="http://localhost:8888/health",
                expected_result={"status": "healthy"}
            ),
            ValidationRule(
                rule_id="prometheus_health_endpoint", 
                rule_type="endpoint",
                target="http://localhost:9090/-/healthy",
                expected_result="Prometheus is Healthy."
            ),
            ValidationRule(
                rule_id="grafana_health_endpoint",
                rule_type="endpoint", 
                target="http://localhost:3000/api/health",
                expected_result={"database": "ok"}
            ),
            ValidationRule(
                rule_id="directus_health_endpoint",
                rule_type="endpoint",
                target="http://localhost:8055/server/health", 
                expected_result={"status": "ok"}
            ),
            
            # Makefile target validations
            ValidationRule(
                rule_id="makefile_dashboard_status",
                rule_type="makefile",
                target="dashboard-status",
                expected_result="success"
            ),
            ValidationRule(
                rule_id="makefile_tunnel_status",
                rule_type="makefile", 
                target="tunnel-status",
                expected_result="success"
            ),
            
            # Service availability validations
            ValidationRule(
                rule_id="redis_coordination_service",
                rule_type="service",
                target="redis://192.168.1.119:6379",
                expected_result="PONG"
            ),
            ValidationRule(
                rule_id="redis_fallback_service", 
                rule_type="service",
                target="redis://localhost:6380",
                expected_result="PONG"
            )
        ]
        
        for rule in default_rules:
            self.validation_rules[rule.rule_id] = rule
        
        self.logger.info(f"Loaded {len(self.validation_rules)} validation rules")
    
    async def _initialize_websocket_connections(self):
        """Initialize WebSocket connections for real-time monitoring."""
        try:
            # Connect to Observatory WebSocket for real-time updates
            await self._connect_to_observatory_websocket()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize WebSocket connections: {e}")
    
    async def _connect_to_observatory_websocket(self):
        """Connect to Observatory WebSocket for real-time monitoring."""
        try:
            uri = "ws://localhost:8888/ws/observatory"
            self.observatory_ws_client = await websockets.connect(uri)
            
            self.logger.info("Connected to Observatory WebSocket")
            
            # Start listening for messages
            asyncio.create_task(self._listen_to_observatory_websocket())
            
        except Exception as e:
            self.logger.warning(f"Failed to connect to Observatory WebSocket: {e}")
    
    async def _listen_to_observatory_websocket(self):
        """Listen to Observatory WebSocket messages for validation triggers."""
        try:
            async for message in self.observatory_ws_client:
                try:
                    data = json.loads(message)
                    await self._process_websocket_message(data)
                except json.JSONDecodeError:
                    self.logger.warning(f"Invalid JSON from Observatory WebSocket: {message}")
                    
        except websockets.exceptions.ConnectionClosed:
            self.logger.warning("Observatory WebSocket connection closed")
            # Attempt reconnection
            await asyncio.sleep(5)
            await self._connect_to_observatory_websocket()
        except Exception as e:
            self.logger.error(f"Error listening to Observatory WebSocket: {e}")
    
    async def _process_websocket_message(self, data: Dict[str, Any]):
        """Process WebSocket message and trigger relevant validations."""
        message_type = data.get('type', '')
        
        if message_type == 'system_change':
            # System change detected, trigger validation
            await self._trigger_validation_by_component(data.get('component', 'all'))
        elif message_type == 'health_update':
            # Health status update, validate related endpoints
            await self._validate_health_endpoints()
        elif message_type == 'error_detected':
            # Error detected, increase validation frequency
            await self._increase_validation_frequency()
    
    async def _continuous_validation_loop(self):
        """Continuous validation loop that runs all validation rules."""
        while self.is_running:
            try:
                await self._run_all_validations()
                await asyncio.sleep(self.validation_interval)
                
            except Exception as e:
                self.logger.error(f"Error in continuous validation loop: {e}")
                await asyncio.sleep(self.validation_interval)
    
    async def _run_all_validations(self) -> Dict[str, Any]:
        """Run all enabled validation rules."""
        correlation_id = self.generate_correlation_id()
        start_time = time.time()
        
        validation_tasks = []
        for rule in self.validation_rules.values():
            if rule.enabled:
                task = asyncio.create_task(self._validate_rule(rule, correlation_id))
                validation_tasks.append(task)
        
        # Wait for all validations to complete
        results = await asyncio.gather(*validation_tasks, return_exceptions=True)
        
        # Process results
        successful_validations = 0
        total_validations = len(results)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Validation task failed: {result}")
                continue
            
            if result and result.success:
                successful_validations += 1
        
        # Update metrics
        accuracy = successful_validations / total_validations if total_validations > 0 else 0
        self.metrics.update({
            'total_validations': self.metrics['total_validations'] + total_validations,
            'successful_validations': self.metrics['successful_validations'] + successful_validations,
            'failed_validations': self.metrics['failed_validations'] + (total_validations - successful_validations),
            'accuracy_score': accuracy,
            'last_validation_timestamp': time.time()
        })
        
        duration = time.time() - start_time
        
        self.logger.info(f"Completed validation cycle: {successful_validations}/{total_validations} successful",
                        extra={
                            "correlation_id": correlation_id,
                            "accuracy": accuracy,
                            "duration": duration
                        })
        
        # Check if accuracy is below threshold
        if accuracy < self.accuracy_threshold:
            await self._handle_low_accuracy_alert(accuracy, correlation_id)
        
        return {
            "total_validations": total_validations,
            "successful_validations": successful_validations,
            "accuracy": accuracy,
            "duration": duration,
            "correlation_id": correlation_id
        }
    
    async def _validate_rule(self, rule: ValidationRule, correlation_id: str) -> ValidationResult:
        """Validate a specific rule."""
        start_time = time.time()
        
        try:
            if rule.rule_type == "websocket":
                result = await self._validate_websocket_rule(rule)
            elif rule.rule_type == "endpoint":
                result = await self._validate_endpoint_rule(rule)
            elif rule.rule_type == "makefile":
                result = await self._validate_makefile_rule(rule)
            elif rule.rule_type == "service":
                result = await self._validate_service_rule(rule)
            else:
                raise ValueError(f"Unknown rule type: {rule.rule_type}")
            
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Update rule statistics
            rule.last_validated = datetime.utcnow()
            rule.validation_count += 1
            if result.success:
                rule.success_count += 1
            
            result.response_time_ms = response_time
            result.correlation_id = correlation_id
            
            # Store result
            self.validation_results.append(result)
            
            # Keep only recent results (last 1000)
            if len(self.validation_results) > 1000:
                self.validation_results = self.validation_results[-1000:]
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to validate rule {rule.rule_id}: {e}")
            return ValidationResult(
                rule_id=rule.rule_id,
                timestamp=datetime.utcnow(),
                success=False,
                actual_result=None,
                expected_result=rule.expected_result,
                error_message=str(e),
                correlation_id=correlation_id
            )
    
    async def _validate_websocket_rule(self, rule: ValidationRule) -> ValidationResult:
        """Validate WebSocket endpoint accessibility."""
        try:
            # Test WebSocket connection
            async with websockets.connect(rule.target, timeout=5) as websocket:
                # Send a ping to test connectivity
                await websocket.ping()
                
                return ValidationResult(
                    rule_id=rule.rule_id,
                    timestamp=datetime.utcnow(),
                    success=True,
                    actual_result="connection_success",
                    expected_result=rule.expected_result
                )
                
        except Exception as e:
            return ValidationResult(
                rule_id=rule.rule_id,
                timestamp=datetime.utcnow(),
                success=False,
                actual_result="connection_failed",
                expected_result=rule.expected_result,
                error_message=str(e)
            )
    
    async def _validate_endpoint_rule(self, rule: ValidationRule) -> ValidationResult:
        """Validate HTTP endpoint response."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(rule.target, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        if response.content_type == 'application/json':
                            actual_result = await response.json()
                        else:
                            actual_result = await response.text()
                        
                        # Check if result matches expected
                        success = self._compare_results(actual_result, rule.expected_result)
                        
                        return ValidationResult(
                            rule_id=rule.rule_id,
                            timestamp=datetime.utcnow(),
                            success=success,
                            actual_result=actual_result,
                            expected_result=rule.expected_result
                        )
                    else:
                        return ValidationResult(
                            rule_id=rule.rule_id,
                            timestamp=datetime.utcnow(),
                            success=False,
                            actual_result=f"HTTP {response.status}",
                            expected_result=rule.expected_result,
                            error_message=f"HTTP {response.status}"
                        )
                        
        except Exception as e:
            return ValidationResult(
                rule_id=rule.rule_id,
                timestamp=datetime.utcnow(),
                success=False,
                actual_result=None,
                expected_result=rule.expected_result,
                error_message=str(e)
            )
    
    async def _validate_makefile_rule(self, rule: ValidationRule) -> ValidationResult:
        """Validate Makefile target execution."""
        try:
            # Execute makefile target
            result = subprocess.run(
                ["make", rule.target],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            success = result.returncode == 0
            actual_result = "success" if success else "failed"
            
            self.metrics['makefile_validations'] += 1
            
            return ValidationResult(
                rule_id=rule.rule_id,
                timestamp=datetime.utcnow(),
                success=success,
                actual_result=actual_result,
                expected_result=rule.expected_result,
                error_message=result.stderr if not success else None
            )
            
        except Exception as e:
            return ValidationResult(
                rule_id=rule.rule_id,
                timestamp=datetime.utcnow(),
                success=False,
                actual_result="execution_failed",
                expected_result=rule.expected_result,
                error_message=str(e)
            )
    
    async def _validate_service_rule(self, rule: ValidationRule) -> ValidationResult:
        """Validate service availability (Redis, etc.)."""
        try:
            if rule.target.startswith("redis://"):
                # Redis ping validation
                import redis.asyncio as redis
                
                # Parse Redis URL
                url_parts = rule.target.replace("redis://", "").split(":")
                host = url_parts[0]
                port = int(url_parts[1]) if len(url_parts) > 1 else 6379
                
                redis_client = redis.Redis(host=host, port=port, decode_responses=True)
                result = await redis_client.ping()
                await redis_client.close()
                
                success = result == True
                actual_result = "PONG" if success else "NO_RESPONSE"
                
                return ValidationResult(
                    rule_id=rule.rule_id,
                    timestamp=datetime.utcnow(),
                    success=success,
                    actual_result=actual_result,
                    expected_result=rule.expected_result
                )
            else:
                raise ValueError(f"Unsupported service type: {rule.target}")
                
        except Exception as e:
            return ValidationResult(
                rule_id=rule.rule_id,
                timestamp=datetime.utcnow(),
                success=False,
                actual_result=None,
                expected_result=rule.expected_result,
                error_message=str(e)
            )
    
    def _compare_results(self, actual: Any, expected: Any) -> bool:
        """Compare actual result with expected result."""
        if isinstance(expected, dict) and isinstance(actual, dict):
            # For dictionaries, check if expected keys are present with correct values
            for key, value in expected.items():
                if key not in actual or actual[key] != value:
                    return False
            return True
        elif isinstance(expected, str) and isinstance(actual, str):
            return expected.lower() in actual.lower()
        else:
            return actual == expected
    
    async def _websocket_monitoring_loop(self):
        """Monitor WebSocket connections and update metrics."""
        while self.is_running:
            try:
                # Count active WebSocket connections
                active_connections = len([conn for conn in self.websocket_connections.values() 
                                        if not conn.closed])
                self.metrics['websocket_connections'] = active_connections
                
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"Error in WebSocket monitoring loop: {e}")
                await asyncio.sleep(30)
    
    async def _accuracy_monitoring_loop(self):
        """Monitor accuracy and trigger alerts when below threshold."""
        while self.is_running:
            try:
                current_accuracy = self.metrics.get('accuracy_score', 0.0)
                
                if current_accuracy < self.accuracy_threshold:
                    await self._handle_low_accuracy_alert(current_accuracy)
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in accuracy monitoring loop: {e}")
                await asyncio.sleep(300)
    
    async def _handle_low_accuracy_alert(self, accuracy: float, correlation_id: str = None):
        """Handle low accuracy alert."""
        if not correlation_id:
            correlation_id = self.generate_correlation_id()
        
        self.logger.warning(f"Documentation accuracy below threshold: {accuracy:.2%} < {self.accuracy_threshold:.2%}",
                          extra={
                              "correlation_id": correlation_id,
                              "accuracy": accuracy,
                              "threshold": self.accuracy_threshold
                          })
        
        # Trigger immediate re-validation
        await self._trigger_validation_by_component("all")
    
    async def _trigger_validation_by_component(self, component: str):
        """Trigger validation for specific component."""
        relevant_rules = [rule for rule in self.validation_rules.values() 
                         if component == "all" or component in rule.target]
        
        validation_tasks = []
        correlation_id = self.generate_correlation_id()
        
        for rule in relevant_rules:
            if rule.enabled:
                task = asyncio.create_task(self._validate_rule(rule, correlation_id))
                validation_tasks.append(task)
        
        if validation_tasks:
            await asyncio.gather(*validation_tasks, return_exceptions=True)
            self.logger.info(f"Triggered validation for component: {component}",
                           extra={"correlation_id": correlation_id})
    
    async def _validate_health_endpoints(self):
        """Validate all health endpoints."""
        health_rules = [rule for rule in self.validation_rules.values() 
                       if "health" in rule.rule_id and rule.enabled]
        
        validation_tasks = []
        correlation_id = self.generate_correlation_id()
        
        for rule in health_rules:
            task = asyncio.create_task(self._validate_rule(rule, correlation_id))
            validation_tasks.append(task)
        
        if validation_tasks:
            await asyncio.gather(*validation_tasks, return_exceptions=True)
    
    async def _increase_validation_frequency(self):
        """Temporarily increase validation frequency due to detected issues."""
        original_interval = self.validation_interval
        self.validation_interval = min(30, self.validation_interval)  # Increase to every 30 seconds
        
        self.logger.info(f"Increased validation frequency to {self.validation_interval}s due to detected issues")
        
        # Reset after 10 minutes
        await asyncio.sleep(600)
        self.validation_interval = original_interval
        self.logger.info(f"Reset validation frequency to {self.validation_interval}s")
    
    async def get_validation_status(self) -> Dict[str, Any]:
        """Get current validation status and metrics."""
        recent_results = [r for r in self.validation_results 
                         if r.timestamp > datetime.utcnow() - timedelta(hours=1)]
        
        return {
            "status": "running" if self.is_running else "stopped",
            "validation_rules": len(self.validation_rules),
            "enabled_rules": len([r for r in self.validation_rules.values() if r.enabled]),
            "recent_validations": len(recent_results),
            "recent_success_rate": (len([r for r in recent_results if r.success]) / len(recent_results)) if recent_results else 0,
            "metrics": self.metrics,
            "accuracy_threshold": self.accuracy_threshold,
            "validation_interval": self.validation_interval,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def add_validation_rule(self, rule: ValidationRule) -> Dict[str, Any]:
        """Add a new validation rule."""
        self.validation_rules[rule.rule_id] = rule
        
        self.logger.info(f"Added validation rule: {rule.rule_id}",
                        extra={"rule_type": rule.rule_type, "target": rule.target})
        
        return {
            "status": "added",
            "rule_id": rule.rule_id,
            "total_rules": len(self.validation_rules)
        }
    
    async def remove_validation_rule(self, rule_id: str) -> Dict[str, Any]:
        """Remove a validation rule."""
        if rule_id in self.validation_rules:
            del self.validation_rules[rule_id]
            
            self.logger.info(f"Removed validation rule: {rule_id}")
            
            return {
                "status": "removed",
                "rule_id": rule_id,
                "total_rules": len(self.validation_rules)
            }
        else:
            return {
                "status": "not_found",
                "rule_id": rule_id
            }
    
    async def stop(self):
        """Stop the validation system."""
        self.is_running = False
        
        if self.observatory_ws_client:
            await self.observatory_ws_client.close()
        
        self.logger.info("RealTimeValidator stopped")


if __name__ == "__main__":
    async def main():
        validator = RealTimeValidator()
        await validator.initialize()
        
        # Run a validation cycle
        results = await validator._run_all_validations()
        print(f"Validation Results: {json.dumps(results, indent=2)}")
        
        # Get status
        status = await validator.get_validation_status()
        print(f"Validator Status: {json.dumps(status, indent=2)}")
        
        await validator.stop()
    
    asyncio.run(main())