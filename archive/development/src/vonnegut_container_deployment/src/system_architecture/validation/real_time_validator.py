#!/usr/bin/env python3
"""
Real-Time Validator - Phase 5 Task 5.2

Validates generated documentation against actual system behavior
with real-time monitoring and accuracy tracking.
"""

import os
import asyncio
import json
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
import aiohttp
import websockets

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


@dataclass
class ValidationResult:
    """Represents a validation result."""
    validation_id: str
    validation_type: str  # 'endpoint', 'websocket', 'makefile', 'service', 'documentation'
    target: str  # What was validated
    status: str  # 'passed', 'failed', 'warning', 'skipped'
    accuracy_score: float  # 0.0 to 1.0
    timestamp: datetime
    execution_time: float  # seconds
    details: Dict[str, Any]
    error_message: Optional[str] = None
    recommendations: List[str] = None


@dataclass
class ValidationRule:
    """Defines a validation rule."""
    rule_id: str
    rule_type: str
    target_pattern: str  # Pattern to match targets
    validation_function: str  # Function name to call
    priority: int  # 1=highest, 5=lowest
    timeout: int = 30  # seconds
    retry_attempts: int = 3
    enabled: bool = True
    description: Optional[str] = None


class RealTimeValidator(ReflectiveModule):
    """
    Real-time validation system for documentation accuracy.
    
    Continuously validates generated documentation against actual system
    behavior, monitoring accuracy and alerting when thresholds are breached.
    """
    
    def __init__(self, accuracy_threshold: float = 0.95):
        super().__init__()
        self.accuracy_threshold = accuracy_threshold
        self.validation_rules: Dict[str, ValidationRule] = {}
        self.validation_history: List[ValidationResult] = []
        self.max_history_size = 10000
        self.websocket_connections: Dict[str, websockets.WebSocketClientProtocol] = {}
        self.validation_tasks: Set[asyncio.Task] = set()
        self.continuous_validation_active = False
        self.last_accuracy_check = datetime.now()
        
        # Validation metrics
        self.validation_metrics = {
            'total_validations': 0,
            'passed_validations': 0,
            'failed_validations': 0,
            'current_accuracy': 1.0,
            'accuracy_trend': [],
            'last_validation': None
        }
        
        # Initialize validation rules
        self._initialize_validation_rules()
        
        # Register capabilities
        self.register_capability('real_time_validation', {
            'description': 'Real-time validation of documentation against live system',
            'accuracy_threshold': self.accuracy_threshold,
            'validation_rules': len(self.validation_rules),
            'continuous_validation': self.continuous_validation_active
        })
    
    def _initialize_validation_rules(self):
        """Initialize standard validation rules."""
        rules = [
            # Endpoint validation rules
            ValidationRule(
                rule_id='validate_observatory_health',
                rule_type='endpoint',
                target_pattern='http://localhost:8888/health',
                validation_function='validate_health_endpoint',
                priority=1,
                timeout=10,
                description='Validate Observatory health endpoint'
            ),
            ValidationRule(
                rule_id='validate_prometheus_metrics',
                rule_type='endpoint',
                target_pattern='http://localhost:9090/api/v1/query',
                validation_function='validate_prometheus_endpoint',
                priority=2,
                timeout=15,
                description='Validate Prometheus metrics endpoint'
            ),
            ValidationRule(
                rule_id='validate_grafana_api',
                rule_type='endpoint',
                target_pattern='http://localhost:3000/api/health',
                validation_function='validate_grafana_endpoint',
                priority=2,
                timeout=10,
                description='Validate Grafana API endpoint'
            ),
            ValidationRule(
                rule_id='validate_directus_cms',
                rule_type='endpoint',
                target_pattern='http://localhost:8055/server/ping',
                validation_function='validate_directus_endpoint',
                priority=3,
                timeout=10,
                description='Validate Directus CMS endpoint'
            ),
            
            # WebSocket validation rules
            ValidationRule(
                rule_id='validate_observatory_websocket',
                rule_type='websocket',
                target_pattern='ws://localhost:8888/ws/observatory',
                validation_function='validate_websocket_connection',
                priority=1,
                timeout=20,
                description='Validate Observatory WebSocket connection'
            ),
            ValidationRule(
                rule_id='validate_emoji_rain_websocket',
                rule_type='websocket',
                target_pattern='ws://localhost:8888/ws/emoji-rain',
                validation_function='validate_websocket_connection',
                priority=2,
                timeout=20,
                description='Validate Emoji Rain WebSocket connection'
            ),
            ValidationRule(
                rule_id='validate_anomalies_websocket',
                rule_type='websocket',
                target_pattern='ws://localhost:8888/ws/anomalies',
                validation_function='validate_websocket_connection',
                priority=2,
                timeout=20,
                description='Validate Anomalies WebSocket connection'
            ),
            ValidationRule(
                rule_id='validate_doctor_status_websocket',
                rule_type='websocket',
                target_pattern='ws://localhost:8888/ws/doctor-status',
                validation_function='validate_websocket_connection',
                priority=3,
                timeout=20,
                description='Validate Doctor Status WebSocket connection'
            ),
            
            # Makefile validation rules
            ValidationRule(
                rule_id='validate_makefile_targets',
                rule_type='makefile',
                target_pattern='Makefile',
                validation_function='validate_makefile_targets',
                priority=2,
                timeout=30,
                description='Validate Makefile targets exist and are documented'
            ),
            ValidationRule(
                rule_id='validate_tunnel_commands',
                rule_type='makefile',
                target_pattern='tunnel-*',
                validation_function='validate_tunnel_makefile_targets',
                priority=1,
                timeout=45,
                description='Validate tunnel-related Makefile targets'
            ),
            ValidationRule(
                rule_id='validate_dashboard_commands',
                rule_type='makefile',
                target_pattern='dashboard-*',
                validation_function='validate_dashboard_makefile_targets',
                priority=1,
                timeout=60,
                description='Validate dashboard-related Makefile targets'
            ),
            
            # Service validation rules
            ValidationRule(
                rule_id='validate_redis_coordination',
                rule_type='service',
                target_pattern='redis://192.168.1.119:6379',
                validation_function='validate_redis_service',
                priority=1,
                timeout=10,
                description='Validate Redis coordination service'
            ),
            ValidationRule(
                rule_id='validate_tunnel_connectivity',
                rule_type='service',
                target_pattern='tunnel:d1e53e43-033f-4994-8f46-c83962ae3785',
                validation_function='validate_tunnel_service',
                priority=2,
                timeout=30,
                description='Validate Cloudflare tunnel connectivity'
            ),
            
            # Documentation validation rules
            ValidationRule(
                rule_id='validate_operational_workflows',
                rule_type='documentation',
                target_pattern='docs/operational-workflows/*.md',
                validation_function='validate_documentation_accuracy',
                priority=3,
                timeout=20,
                description='Validate operational workflow documentation'
            ),
            ValidationRule(
                rule_id='validate_troubleshooting_guides',
                rule_type='documentation',
                target_pattern='docs/troubleshooting/*.md',
                validation_function='validate_troubleshooting_accuracy',
                priority=3,
                timeout=20,
                description='Validate troubleshooting guide accuracy'
            )
        ]
        
        for rule in rules:
            self.validation_rules[rule.rule_id] = rule
    
    async def start_continuous_validation(self, interval_minutes: int = 15) -> Dict[str, Any]:
        """Start continuous validation process."""
        try:
            if self.continuous_validation_active:
                return {'status': 'already_running'}
            
            self.continuous_validation_active = True
            
            # Start continuous validation task
            validation_task = asyncio.create_task(
                self._continuous_validation_loop(interval_minutes)
            )
            self.validation_tasks.add(validation_task)
            
            # Start WebSocket monitoring
            websocket_task = asyncio.create_task(self._monitor_websocket_connections())
            self.validation_tasks.add(websocket_task)
            
            self.logger.info(f"Continuous validation started with {interval_minutes} minute intervals")
            
            return {
                'status': 'started',
                'interval_minutes': interval_minutes,
                'validation_rules': len(self.validation_rules),
                'accuracy_threshold': self.accuracy_threshold
            }
            
        except Exception as e:
            self.logger.error(f"Failed to start continuous validation: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def stop_continuous_validation(self) -> Dict[str, Any]:
        """Stop continuous validation process."""
        try:
            self.continuous_validation_active = False
            
            # Cancel all validation tasks
            for task in self.validation_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            if self.validation_tasks:
                await asyncio.gather(*self.validation_tasks, return_exceptions=True)
            
            self.validation_tasks.clear()
            
            # Close WebSocket connections
            for ws in self.websocket_connections.values():
                if not ws.closed:
                    await ws.close()
            self.websocket_connections.clear()
            
            self.logger.info("Continuous validation stopped")
            return {'status': 'stopped'}
            
        except Exception as e:
            self.logger.error(f"Error stopping continuous validation: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _continuous_validation_loop(self, interval_minutes: int):
        """Main continuous validation loop."""
        while self.continuous_validation_active:
            try:
                # Run validation cycle
                await self._run_validation_cycle()
                
                # Check accuracy and alert if needed
                await self._check_accuracy_threshold()
                
                # Wait for next cycle
                await asyncio.sleep(interval_minutes * 60)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in continuous validation loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def _run_validation_cycle(self) -> Dict[str, Any]:
        """Run a complete validation cycle."""
        start_time = time.time()
        results = []
        
        # Group rules by type for efficient execution
        rule_groups = {}
        for rule in self.validation_rules.values():
            if rule.enabled:
                if rule.rule_type not in rule_groups:
                    rule_groups[rule.rule_type] = []
                rule_groups[rule.rule_type].append(rule)
        
        # Execute validation groups
        for rule_type, rules in rule_groups.items():
            try:
                group_results = await self._validate_rule_group(rule_type, rules)
                results.extend(group_results)
            except Exception as e:
                self.logger.error(f"Error validating {rule_type} rules: {e}")
        
        # Update metrics
        self._update_validation_metrics(results)
        
        execution_time = time.time() - start_time
        self.logger.info(f"Validation cycle completed in {execution_time:.2f}s - {len(results)} validations")
        
        return {
            'total_validations': len(results),
            'execution_time': execution_time,
            'results': [asdict(r) for r in results]
        }
    
    async def _validate_rule_group(self, rule_type: str, rules: List[ValidationRule]) -> List[ValidationResult]:
        """Validate a group of rules of the same type."""
        results = []
        
        if rule_type == 'endpoint':
            results = await self._validate_endpoint_rules(rules)
        elif rule_type == 'websocket':
            results = await self._validate_websocket_rules(rules)
        elif rule_type == 'makefile':
            results = await self._validate_makefile_rules(rules)
        elif rule_type == 'service':
            results = await self._validate_service_rules(rules)
        elif rule_type == 'documentation':
            results = await self._validate_documentation_rules(rules)
        
        return results
    
    async def _validate_endpoint_rules(self, rules: List[ValidationRule]) -> List[ValidationResult]:
        """Validate HTTP endpoint rules."""
        results = []
        
        async with aiohttp.ClientSession() as session:
            for rule in rules:
                result = await self._validate_single_endpoint(session, rule)
                results.append(result)
        
        return results
    
    async def _validate_single_endpoint(self, session: aiohttp.ClientSession, 
                                      rule: ValidationRule) -> ValidationResult:
        """Validate a single HTTP endpoint."""
        start_time = time.time()
        validation_id = f"{rule.rule_id}_{int(time.time())}"
        
        try:
            timeout = aiohttp.ClientTimeout(total=rule.timeout)
            
            async with session.get(rule.target_pattern, timeout=timeout) as response:
                execution_time = time.time() - start_time
                
                if response.status == 200:
                    # Try to parse response
                    try:
                        data = await response.json()
                        details = {
                            'status_code': response.status,
                            'response_time': execution_time,
                            'response_data': data,
                            'headers': dict(response.headers)
                        }
                        
                        # Additional validation based on endpoint type
                        accuracy_score = await self._calculate_endpoint_accuracy(rule, data, response)
                        
                        return ValidationResult(
                            validation_id=validation_id,
                            validation_type='endpoint',
                            target=rule.target_pattern,
                            status='passed',
                            accuracy_score=accuracy_score,
                            timestamp=datetime.now(),
                            execution_time=execution_time,
                            details=details
                        )
                        
                    except Exception as parse_error:
                        # Non-JSON response, but still successful
                        return ValidationResult(
                            validation_id=validation_id,
                            validation_type='endpoint',
                            target=rule.target_pattern,
                            status='passed',
                            accuracy_score=0.8,  # Lower score for non-JSON
                            timestamp=datetime.now(),
                            execution_time=execution_time,
                            details={
                                'status_code': response.status,
                                'response_time': execution_time,
                                'parse_error': str(parse_error)
                            }
                        )
                else:
                    return ValidationResult(
                        validation_id=validation_id,
                        validation_type='endpoint',
                        target=rule.target_pattern,
                        status='failed',
                        accuracy_score=0.0,
                        timestamp=datetime.now(),
                        execution_time=execution_time,
                        details={'status_code': response.status},
                        error_message=f'HTTP {response.status}'
                    )
        
        except asyncio.TimeoutError:
            return ValidationResult(
                validation_id=validation_id,
                validation_type='endpoint',
                target=rule.target_pattern,
                status='failed',
                accuracy_score=0.0,
                timestamp=datetime.now(),
                execution_time=time.time() - start_time,
                details={},
                error_message='Timeout'
            )
        
        except Exception as e:
            return ValidationResult(
                validation_id=validation_id,
                validation_type='endpoint',
                target=rule.target_pattern,
                status='failed',
                accuracy_score=0.0,
                timestamp=datetime.now(),
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e)
            )
    
    async def _calculate_endpoint_accuracy(self, rule: ValidationRule, data: Any, 
                                         response: aiohttp.ClientResponse) -> float:
        """Calculate accuracy score for endpoint validation."""
        accuracy = 1.0
        
        # Check response time (penalize slow responses)
        response_time = response.headers.get('X-Response-Time')
        if response_time:
            try:
                time_ms = float(response_time.replace('ms', ''))
                if time_ms > 1000:  # > 1 second
                    accuracy -= 0.1
                elif time_ms > 5000:  # > 5 seconds
                    accuracy -= 0.2
            except:
                pass
        
        # Check for expected fields based on endpoint type
        if 'health' in rule.target_pattern:
            if isinstance(data, dict):
                if 'status' not in data:
                    accuracy -= 0.2
                if data.get('status') != 'healthy':
                    accuracy -= 0.3
            else:
                accuracy -= 0.5
        
        elif 'metrics' in rule.target_pattern or 'prometheus' in rule.target_pattern:
            if isinstance(data, dict):
                if 'data' not in data:
                    accuracy -= 0.3
            else:
                accuracy -= 0.5
        
        return max(0.0, accuracy)
    
    async def _validate_websocket_rules(self, rules: List[ValidationRule]) -> List[ValidationResult]:
        """Validate WebSocket connection rules."""
        results = []
        
        for rule in rules:
            result = await self._validate_single_websocket(rule)
            results.append(result)
        
        return results
    
    async def _validate_single_websocket(self, rule: ValidationRule) -> ValidationResult:
        """Validate a single WebSocket connection."""
        start_time = time.time()
        validation_id = f"{rule.rule_id}_{int(time.time())}"
        
        try:
            # Convert http to ws URL if needed
            ws_url = rule.target_pattern.replace('http://', 'ws://').replace('https://', 'wss://')
            
            async with websockets.connect(ws_url, timeout=rule.timeout) as websocket:
                execution_time = time.time() - start_time
                
                # Send a ping and wait for response
                await websocket.ping()
                
                # Try to receive a message (with timeout)
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    message_received = True
                    message_content = message
                except asyncio.TimeoutError:
                    message_received = False
                    message_content = None
                
                return ValidationResult(
                    validation_id=validation_id,
                    validation_type='websocket',
                    target=ws_url,
                    status='passed',
                    accuracy_score=1.0 if message_received else 0.8,
                    timestamp=datetime.now(),
                    execution_time=execution_time,
                    details={
                        'connection_time': execution_time,
                        'message_received': message_received,
                        'message_content': message_content[:100] if message_content else None
                    }
                )
        
        except Exception as e:
            return ValidationResult(
                validation_id=validation_id,
                validation_type='websocket',
                target=rule.target_pattern,
                status='failed',
                accuracy_score=0.0,
                timestamp=datetime.now(),
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e)
            )
    
    async def _validate_makefile_rules(self, rules: List[ValidationRule]) -> List[ValidationResult]:
        """Validate Makefile-related rules."""
        results = []
        
        for rule in rules:
            result = await self._validate_single_makefile_rule(rule)
            results.append(result)
        
        return results
    
    async def _validate_single_makefile_rule(self, rule: ValidationRule) -> ValidationResult:
        """Validate a single Makefile rule."""
        start_time = time.time()
        validation_id = f"{rule.rule_id}_{int(time.time())}"
        
        try:
            if rule.validation_function == 'validate_makefile_targets':
                return await self._validate_makefile_targets(validation_id, rule, start_time)
            elif rule.validation_function == 'validate_tunnel_makefile_targets':
                return await self._validate_tunnel_targets(validation_id, rule, start_time)
            elif rule.validation_function == 'validate_dashboard_makefile_targets':
                return await self._validate_dashboard_targets(validation_id, rule, start_time)
            else:
                raise ValueError(f"Unknown validation function: {rule.validation_function}")
        
        except Exception as e:
            return ValidationResult(
                validation_id=validation_id,
                validation_type='makefile',
                target=rule.target_pattern,
                status='failed',
                accuracy_score=0.0,
                timestamp=datetime.now(),
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e)
            )
    
    async def _validate_makefile_targets(self, validation_id: str, rule: ValidationRule, 
                                       start_time: float) -> ValidationResult:
        """Validate that Makefile targets exist and are documented."""
        try:
            # Check if Makefile exists
            if not os.path.exists('Makefile'):
                return ValidationResult(
                    validation_id=validation_id,
                    validation_type='makefile',
                    target='Makefile',
                    status='failed',
                    accuracy_score=0.0,
                    timestamp=datetime.now(),
                    execution_time=time.time() - start_time,
                    details={},
                    error_message='Makefile not found'
                )
            
            # Parse Makefile for targets
            with open('Makefile', 'r') as f:
                makefile_content = f.read()
            
            # Extract targets (simple regex approach)
            import re
            targets = re.findall(r'^([a-zA-Z0-9_-]+):', makefile_content, re.MULTILINE)
            
            # Expected critical targets
            expected_targets = [
                'tunnel-start', 'tunnel-stop', 'tunnel-status',
                'dashboard-up', 'dashboard-stop', 'dashboard-restart', 'dashboard-status',
                'prometheus-start', 'prometheus-stop',
                'grafana-start', 'grafana-stop'
            ]
            
            missing_targets = [t for t in expected_targets if t not in targets]
            accuracy_score = 1.0 - (len(missing_targets) / len(expected_targets))
            
            status = 'passed' if accuracy_score >= 0.8 else 'warning' if accuracy_score >= 0.5 else 'failed'
            
            return ValidationResult(
                validation_id=validation_id,
                validation_type='makefile',
                target='Makefile',
                status=status,
                accuracy_score=accuracy_score,
                timestamp=datetime.now(),
                execution_time=time.time() - start_time,
                details={
                    'total_targets': len(targets),
                    'expected_targets': len(expected_targets),
                    'missing_targets': missing_targets,
                    'found_targets': targets
                },
                recommendations=[f"Add missing target: {t}" for t in missing_targets] if missing_targets else None
            )
        
        except Exception as e:
            return ValidationResult(
                validation_id=validation_id,
                validation_type='makefile',
                target='Makefile',
                status='failed',
                accuracy_score=0.0,
                timestamp=datetime.now(),
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e)
            )
    
    async def _validate_tunnel_targets(self, validation_id: str, rule: ValidationRule, 
                                     start_time: float) -> ValidationResult:
        """Validate tunnel-related Makefile targets."""
        try:
            # Test tunnel-status target (safe to run)
            result = subprocess.run(['make', 'tunnel-status'], 
                                  capture_output=True, text=True, timeout=30)
            
            accuracy_score = 1.0 if result.returncode == 0 else 0.5
            status = 'passed' if result.returncode == 0 else 'warning'
            
            return ValidationResult(
                validation_id=validation_id,
                validation_type='makefile',
                target='tunnel-status',
                status=status,
                accuracy_score=accuracy_score,
                timestamp=datetime.now(),
                execution_time=time.time() - start_time,
                details={
                    'return_code': result.returncode,
                    'stdout': result.stdout[:500],  # Limit output
                    'stderr': result.stderr[:500]
                }
            )
        
        except subprocess.TimeoutExpired:
            return ValidationResult(
                validation_id=validation_id,
                validation_type='makefile',
                target='tunnel-status',
                status='failed',
                accuracy_score=0.0,
                timestamp=datetime.now(),
                execution_time=time.time() - start_time,
                details={},
                error_message='Command timeout'
            )
        
        except Exception as e:
            return ValidationResult(
                validation_id=validation_id,
                validation_type='makefile',
                target='tunnel-status',
                status='failed',
                accuracy_score=0.0,
                timestamp=datetime.now(),
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e)
            )
    
    async def _validate_dashboard_targets(self, validation_id: str, rule: ValidationRule, 
                                        start_time: float) -> ValidationResult:
        """Validate dashboard-related Makefile targets."""
        try:
            # Test dashboard-status target (safe to run)
            result = subprocess.run(['make', 'dashboard-status'], 
                                  capture_output=True, text=True, timeout=30)
            
            accuracy_score = 1.0 if result.returncode == 0 else 0.5
            status = 'passed' if result.returncode == 0 else 'warning'
            
            return ValidationResult(
                validation_id=validation_id,
                validation_type='makefile',
                target='dashboard-status',
                status=status,
                accuracy_score=accuracy_score,
                timestamp=datetime.now(),
                execution_time=time.time() - start_time,
                details={
                    'return_code': result.returncode,
                    'stdout': result.stdout[:500],
                    'stderr': result.stderr[:500]
                }
            )
        
        except Exception as e:
            return ValidationResult(
                validation_id=validation_id,
                validation_type='makefile',
                target='dashboard-status',
                status='failed',
                accuracy_score=0.0,
                timestamp=datetime.now(),
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e)
            )
    
    async def _validate_service_rules(self, rules: List[ValidationRule]) -> List[ValidationResult]:
        """Validate service-related rules."""
        results = []
        
        for rule in rules:
            result = await self._validate_single_service(rule)
            results.append(result)
        
        return results
    
    async def _validate_single_service(self, rule: ValidationRule) -> ValidationResult:
        """Validate a single service."""
        start_time = time.time()
        validation_id = f"{rule.rule_id}_{int(time.time())}"
        
        try:
            if 'redis' in rule.target_pattern:
                return await self._validate_redis_service(validation_id, rule, start_time)
            elif 'tunnel' in rule.target_pattern:
                return await self._validate_tunnel_service(validation_id, rule, start_time)
            else:
                raise ValueError(f"Unknown service type: {rule.target_pattern}")
        
        except Exception as e:
            return ValidationResult(
                validation_id=validation_id,
                validation_type='service',
                target=rule.target_pattern,
                status='failed',
                accuracy_score=0.0,
                timestamp=datetime.now(),
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e)
            )
    
    async def _validate_redis_service(self, validation_id: str, rule: ValidationRule, 
                                    start_time: float) -> ValidationResult:
        """Validate Redis service connectivity."""
        try:
            import redis.asyncio as redis
            
            # Try primary Redis
            try:
                redis_client = redis.Redis(host='192.168.1.119', port=6379, socket_timeout=5)
                await redis_client.ping()
                await redis_client.close()
                
                return ValidationResult(
                    validation_id=validation_id,
                    validation_type='service',
                    target='redis://192.168.1.119:6379',
                    status='passed',
                    accuracy_score=1.0,
                    timestamp=datetime.now(),
                    execution_time=time.time() - start_time,
                    details={'connection': 'primary', 'host': '192.168.1.119', 'port': 6379}
                )
            
            except Exception:
                # Try fallback Redis
                redis_client = redis.Redis(host='localhost', port=6380, socket_timeout=5)
                await redis_client.ping()
                await redis_client.close()
                
                return ValidationResult(
                    validation_id=validation_id,
                    validation_type='service',
                    target='redis://localhost:6380',
                    status='warning',
                    accuracy_score=0.8,  # Lower score for fallback
                    timestamp=datetime.now(),
                    execution_time=time.time() - start_time,
                    details={'connection': 'fallback', 'host': 'localhost', 'port': 6380}
                )
        
        except Exception as e:
            return ValidationResult(
                validation_id=validation_id,
                validation_type='service',
                target=rule.target_pattern,
                status='failed',
                accuracy_score=0.0,
                timestamp=datetime.now(),
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e)
            )
    
    async def _validate_tunnel_service(self, validation_id: str, rule: ValidationRule, 
                                     start_time: float) -> ValidationResult:
        """Validate Cloudflare tunnel service."""
        try:
            # Test tunnel connectivity by checking a known endpoint through the tunnel
            tunnel_endpoints = [
                'https://observatory.louispotok.com/health',
                'https://prometheus.louispotok.com/api/v1/query?query=up',
                'https://grafana.louispotok.com/api/health'
            ]
            
            successful_endpoints = 0
            total_endpoints = len(tunnel_endpoints)
            
            async with aiohttp.ClientSession() as session:
                for endpoint in tunnel_endpoints:
                    try:
                        async with session.get(endpoint, timeout=aiohttp.ClientTimeout(total=10)) as response:
                            if response.status == 200:
                                successful_endpoints += 1
                    except:
                        pass  # Endpoint failed, continue
            
            accuracy_score = successful_endpoints / total_endpoints
            status = 'passed' if accuracy_score >= 0.7 else 'warning' if accuracy_score >= 0.3 else 'failed'
            
            return ValidationResult(
                validation_id=validation_id,
                validation_type='service',
                target='tunnel:d1e53e43-033f-4994-8f46-c83962ae3785',
                status=status,
                accuracy_score=accuracy_score,
                timestamp=datetime.now(),
                execution_time=time.time() - start_time,
                details={
                    'successful_endpoints': successful_endpoints,
                    'total_endpoints': total_endpoints,
                    'tested_endpoints': tunnel_endpoints
                }
            )
        
        except Exception as e:
            return ValidationResult(
                validation_id=validation_id,
                validation_type='service',
                target=rule.target_pattern,
                status='failed',
                accuracy_score=0.0,
                timestamp=datetime.now(),
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e)
            )
    
    async def _validate_documentation_rules(self, rules: List[ValidationRule]) -> List[ValidationResult]:
        """Validate documentation accuracy rules."""
        results = []
        
        for rule in rules:
            result = await self._validate_single_documentation_rule(rule)
            results.append(result)
        
        return results
    
    async def _validate_single_documentation_rule(self, rule: ValidationRule) -> ValidationResult:
        """Validate a single documentation rule."""
        start_time = time.time()
        validation_id = f"{rule.rule_id}_{int(time.time())}"
        
        try:
            # Find matching documentation files
            import glob
            matching_files = glob.glob(rule.target_pattern)
            
            if not matching_files:
                return ValidationResult(
                    validation_id=validation_id,
                    validation_type='documentation',
                    target=rule.target_pattern,
                    status='failed',
                    accuracy_score=0.0,
                    timestamp=datetime.now(),
                    execution_time=time.time() - start_time,
                    details={},
                    error_message='No matching documentation files found'
                )
            
            # Validate each file
            total_score = 0.0
            file_scores = {}
            
            for file_path in matching_files:
                score = await self._validate_documentation_file(file_path)
                file_scores[file_path] = score
                total_score += score
            
            average_score = total_score / len(matching_files)
            status = 'passed' if average_score >= 0.8 else 'warning' if average_score >= 0.5 else 'failed'
            
            return ValidationResult(
                validation_id=validation_id,
                validation_type='documentation',
                target=rule.target_pattern,
                status=status,
                accuracy_score=average_score,
                timestamp=datetime.now(),
                execution_time=time.time() - start_time,
                details={
                    'files_validated': len(matching_files),
                    'file_scores': file_scores,
                    'average_score': average_score
                }
            )
        
        except Exception as e:
            return ValidationResult(
                validation_id=validation_id,
                validation_type='documentation',
                target=rule.target_pattern,
                status='failed',
                accuracy_score=0.0,
                timestamp=datetime.now(),
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e)
            )
    
    async def _validate_documentation_file(self, file_path: str) -> float:
        """Validate a single documentation file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            score = 1.0
            
            # Check for basic documentation structure
            if '# ' not in content:  # No main heading
                score -= 0.2
            
            if '## ' not in content:  # No subheadings
                score -= 0.1
            
            # Check for outdated timestamps (if any)
            import re
            date_patterns = re.findall(r'\d{4}-\d{2}-\d{2}', content)
            if date_patterns:
                # Check if any dates are very old (> 6 months)
                from datetime import datetime, timedelta
                six_months_ago = datetime.now() - timedelta(days=180)
                
                for date_str in date_patterns:
                    try:
                        doc_date = datetime.strptime(date_str, '%Y-%m-%d')
                        if doc_date < six_months_ago:
                            score -= 0.1
                            break
                    except:
                        pass
            
            # Check for TODO or FIXME markers
            if 'TODO' in content or 'FIXME' in content:
                score -= 0.1
            
            # Check file size (very small files might be incomplete)
            if len(content) < 500:  # Less than 500 characters
                score -= 0.2
            
            return max(0.0, score)
        
        except Exception:
            return 0.0
    
    async def _monitor_websocket_connections(self):
        """Monitor WebSocket connections continuously."""
        while self.continuous_validation_active:
            try:
                # Test WebSocket connections every 5 minutes
                await asyncio.sleep(300)
                
                websocket_rules = [r for r in self.validation_rules.values() 
                                 if r.rule_type == 'websocket' and r.enabled]
                
                for rule in websocket_rules:
                    try:
                        result = await self._validate_single_websocket(rule)
                        self._add_validation_result(result)
                    except Exception as e:
                        self.logger.error(f"Error monitoring WebSocket {rule.target_pattern}: {e}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in WebSocket monitoring: {e}")
    
    def _update_validation_metrics(self, results: List[ValidationResult]):
        """Update validation metrics based on results."""
        for result in results:
            self.validation_metrics['total_validations'] += 1
            
            if result.status == 'passed':
                self.validation_metrics['passed_validations'] += 1
            else:
                self.validation_metrics['failed_validations'] += 1
            
            self._add_validation_result(result)
        
        # Calculate current accuracy
        if self.validation_metrics['total_validations'] > 0:
            self.validation_metrics['current_accuracy'] = (
                self.validation_metrics['passed_validations'] / 
                self.validation_metrics['total_validations']
            )
        
        # Update accuracy trend
        self.validation_metrics['accuracy_trend'].append({
            'timestamp': datetime.now().isoformat(),
            'accuracy': self.validation_metrics['current_accuracy']
        })
        
        # Keep only last 100 trend points
        if len(self.validation_metrics['accuracy_trend']) > 100:
            self.validation_metrics['accuracy_trend'] = self.validation_metrics['accuracy_trend'][-100:]
        
        self.validation_metrics['last_validation'] = datetime.now().isoformat()
    
    def _add_validation_result(self, result: ValidationResult):
        """Add validation result to history."""
        self.validation_history.append(result)
        
        # Trim history if too large
        if len(self.validation_history) > self.max_history_size:
            self.validation_history = self.validation_history[-self.max_history_size:]
    
    async def _check_accuracy_threshold(self):
        """Check if accuracy has dropped below threshold and alert."""
        current_accuracy = self.validation_metrics['current_accuracy']
        
        if current_accuracy < self.accuracy_threshold:
            self.logger.warning(
                f"Documentation accuracy ({current_accuracy:.2f}) below threshold ({self.accuracy_threshold})"
            )
            
            # Get recent failed validations for context
            recent_failures = [
                r for r in self.validation_history[-50:] 
                if r.status == 'failed' and r.timestamp > datetime.now() - timedelta(hours=1)
            ]
            
            if recent_failures:
                self.logger.warning(f"Recent failures: {[r.target for r in recent_failures]}")
        
        self.last_accuracy_check = datetime.now()
    
    async def run_single_validation(self, rule_id: str) -> Dict[str, Any]:
        """Run a single validation rule."""
        if rule_id not in self.validation_rules:
            return {'status': 'error', 'error': f'Rule {rule_id} not found'}
        
        rule = self.validation_rules[rule_id]
        if not rule.enabled:
            return {'status': 'skipped', 'reason': 'Rule disabled'}
        
        try:
            if rule.rule_type == 'endpoint':
                async with aiohttp.ClientSession() as session:
                    result = await self._validate_single_endpoint(session, rule)
            elif rule.rule_type == 'websocket':
                result = await self._validate_single_websocket(rule)
            elif rule.rule_type == 'makefile':
                result = await self._validate_single_makefile_rule(rule)
            elif rule.rule_type == 'service':
                result = await self._validate_single_service(rule)
            elif rule.rule_type == 'documentation':
                result = await self._validate_single_documentation_rule(rule)
            else:
                return {'status': 'error', 'error': f'Unknown rule type: {rule.rule_type}'}
            
            self._add_validation_result(result)
            return {'status': 'completed', 'result': asdict(result)}
            
        except Exception as e:
            self.logger.error(f"Error running validation {rule_id}: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def get_validation_status(self) -> Dict[str, Any]:
        """Get current validation status."""
        return {
            'continuous_validation_active': self.continuous_validation_active,
            'accuracy_threshold': self.accuracy_threshold,
            'current_accuracy': self.validation_metrics['current_accuracy'],
            'total_validations': self.validation_metrics['total_validations'],
            'passed_validations': self.validation_metrics['passed_validations'],
            'failed_validations': self.validation_metrics['failed_validations'],
            'last_validation': self.validation_metrics['last_validation'],
            'last_accuracy_check': self.last_accuracy_check.isoformat(),
            'validation_rules_enabled': len([r for r in self.validation_rules.values() if r.enabled]),
            'validation_tasks_active': len(self.validation_tasks)
        }
    
    def get_validation_history(self, limit: Optional[int] = None, 
                             status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get validation history with optional filtering."""
        history = self.validation_history
        
        # Filter by status if specified
        if status_filter:
            history = [r for r in history if r.status == status_filter]
        
        # Apply limit
        if limit:
            history = history[-limit:]
        
        return [asdict(result) for result in history]
    
    def get_accuracy_trend(self) -> List[Dict[str, Any]]:
        """Get accuracy trend data."""
        return self.validation_metrics['accuracy_trend']
    
    # ReflectiveModule health endpoints
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint."""
        return {
            'status': 'healthy',
            'continuous_validation_active': self.continuous_validation_active,
            'current_accuracy': self.validation_metrics['current_accuracy'],
            'validation_tasks_active': len(self.validation_tasks),
            'last_validation': self.validation_metrics['last_validation']
        }
    
    async def ready_check(self) -> Dict[str, Any]:
        """Readiness check endpoint."""
        return {
            'ready': True,
            'validation_rules_configured': len(self.validation_rules) > 0,
            'accuracy_threshold_set': self.accuracy_threshold > 0
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get validation metrics."""
        return {
            'real_time_validator_total_validations': self.validation_metrics['total_validations'],
            'real_time_validator_passed_validations': self.validation_metrics['passed_validations'],
            'real_time_validator_failed_validations': self.validation_metrics['failed_validations'],
            'real_time_validator_current_accuracy': self.validation_metrics['current_accuracy'],
            'real_time_validator_continuous_active': 1 if self.continuous_validation_active else 0,
            'real_time_validator_rules_enabled': len([r for r in self.validation_rules.values() if r.enabled])
        }


# Example usage and testing
if __name__ == "__main__":
    async def main():
        # Create validator
        validator = RealTimeValidator(accuracy_threshold=0.90)
        
        # Start continuous validation
        result = await validator.start_continuous_validation(interval_minutes=5)
        print(f"Continuous validation started: {result}")
        
        # Run a single validation
        single_result = await validator.run_single_validation('validate_observatory_health')
        print(f"Single validation: {single_result}")
        
        # Wait a bit
        await asyncio.sleep(10)
        
        # Get status
        status = validator.get_validation_status()
        print(f"Status: {status}")
        
        # Get recent history
        history = validator.get_validation_history(limit=5)
        print(f"Recent history: {len(history)} results")
        
        # Stop validation
        await validator.stop_continuous_validation()
    
    asyncio.run(main())#!/usr/bin/env python3
"""
Real-Time Validator - Task 5.2 Implementation
=============================================

Creates automated validation of generated documentation against actual system behavior
with real-time validation against Observatory WebSocket feeds and continuous accuracy monitoring.

Author: Beast Mode Framework
Date: 2025-01-03
Version: 1.0
"""

import logging
import asyncio
import json
import time
import subprocess
from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import threading
import websockets
import requests

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleCapability
from src.system_architecture.validation.websocket_validator import WebSocketValidator
from src.system_architecture.validation.accuracy_monitor import AccuracyMonitor


@dataclass
class ValidationConfig:
    """Configuration for real-time validation."""
    # Observatory integration
    observatory_url: str = "http://localhost:8888"
    websocket_url: str = "ws://localhost:8888"
    websocket_endpoints: List[str] = field(default_factory=lambda: [
        "/ws/observatory", "/ws/anomalies", "/ws/emoji-rain", "/ws/doctor-status"
    ])
    
    # Validation settings
    accuracy_threshold: float = 0.95
    validation_interval_seconds: int = 60
    real_time_validation_enabled: bool = True
    
    # Makefile validation
    makefile_targets: List[str] = field(default_factory=lambda: [
        "dashboard-status", "tunnel-status", "dashboard-up", "dashboard-stop"
    ])
    makefile_timeout_seconds: int = 30
    
    # Alert settings
    alert_threshold: float = 0.95
    alert_cooldown_seconds: int = 300  # 5 minutes
    
    # Correlation tracking
    correlation_id_enabled: bool = True
    correlation_id_header: str = "X-Correlation-ID"


@dataclass
class ValidationResult:
    """Result of a validation check."""
    validation_id: str
    validation_type: str  # websocket, makefile, endpoint, documentation
    target: str  # what was validated
    status: str  # passed, failed, warning, error
    accuracy_score: float
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None


@dataclass
class ValidationSummary:
    """Summary of validation results."""
    total_validations: int
    passed_validations: int
    failed_validations: int
    warning_validations: int
    overall_accuracy: float
    average_response_time: float
    validation_period: timedelta
    timestamp: datetime = field(default_factory=datetime.now)


class RealTimeValidator(ReflectiveModule):
    """
    Real-time validation system for documentation accuracy.
    
    Validates generated documentation against actual system behavior
    using Observatory WebSocket feeds, Makefile target execution,
    and endpoint accessibility checks.
    """
    
    def __init__(self, config: Optional[ValidationConfig] = None):
        super().__init__()
        self.module_id = "RealTimeValidator"
        self._logger = logging.getLogger(f"system_architecture.{self.__class__.__name__}")
        
        # Configuration
        self._config = config or ValidationConfig()
        
        # Initialize components
        self._websocket_validator = WebSocketValidator(
            websocket_url=self._config.websocket_url,
            endpoints=self._config.websocket_endpoints
        )
        self._accuracy_monitor = AccuracyMonitor(
            threshold=self._config.accuracy_threshold
        )
        
        # Validation state
        self._is_running = False
        self._validation_thread: Optional[threading.Thread] = None
        self._websocket_thread: Optional[threading.Thread] = None
        
        # Results tracking
        self._validation_results: List[ValidationResult] = []
        self._validation_history: Dict[str, List[ValidationResult]] = {}
        self._last_alert_time: Optional[datetime] = None
        
        # Callbacks
        self._validation_callbacks: List[Callable[[ValidationResult], None]] = []
        self._alert_callbacks: List[Callable[[str, float], None]] = []
        
        # Metrics
        self._total_validations = 0
        self._successful_validations = 0
        self._failed_validations = 0
        self._average_accuracy = 0.0
        self._average_response_time = 0.0
        
        self._logger.info("RealTimeValidator initialized")
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING,
            ModuleCapability.DATA_PROCESSING
        ]
    
    def start_validation(self) -> None:
        """Start real-time validation system."""
        self._logger.info("Starting real-time validation system...")
        
        if self._is_running:
            self._logger.warning("Validation system already running")
            return
        
        self._is_running = True
        
        # Start WebSocket validator
        self._websocket_validator.start_monitoring()
        
        # Start accuracy monitor
        self._accuracy_monitor.start_monitoring()
        
        # Start validation thread
        self._validation_thread = threading.Thread(
            target=self._validation_loop,
            name="RealTimeValidator",
            daemon=True
        )
        self._validation_thread.start()
        
        # Start WebSocket monitoring thread
        if self._config.real_time_validation_enabled:
            self._websocket_thread = threading.Thread(
                target=self._websocket_monitoring_loop,
                name="WebSocketMonitor",
                daemon=True
            )
            self._websocket_thread.start()
        
        self._logger.info("Real-time validation system started")
    
    def stop_validation(self) -> None:
        """Stop real-time validation system."""
        self._logger.info("Stopping real-time validation system...")
        
        self._is_running = False
        
        # Stop components
        self._websocket_validator.stop_monitoring()
        self._accuracy_monitor.stop_monitoring()
        
        # Wait for threads to finish
        if self._validation_thread and self._validation_thread.is_alive():
            self._validation_thread.join(timeout=10)
        
        if self._websocket_thread and self._websocket_thread.is_alive():
            self._websocket_thread.join(timeout=10)
        
        self._logger.info("Real-time validation system stopped")
    
    def _validation_loop(self) -> None:
        """Main validation loop."""
        while self._is_running:
            try:
                # Run validation cycle
                self._run_validation_cycle()
                
                # Sleep until next cycle
                time.sleep(self._config.validation_interval_seconds)
                
            except Exception as e:
                self._logger.error(f"Error in validation loop: {e}")
                time.sleep(self._config.validation_interval_seconds)
    
    def _websocket_monitoring_loop(self) -> None:
        """WebSocket monitoring loop."""
        while self._is_running:
            try:
                # Run WebSocket validation
                asyncio.run(self._validate_websocket_real_time())
                
                # Sleep between checks
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self._logger.error(f"Error in WebSocket monitoring: {e}")
                time.sleep(30)
    
    def _run_validation_cycle(self) -> None:
        """Run a complete validation cycle."""
        self._logger.info("Running validation cycle...")
        
        cycle_results = []
        
        # Validate Observatory endpoints
        endpoint_results = self._validate_observatory_endpoints()
        cycle_results.extend(endpoint_results)
        
        # Validate WebSocket endpoints
        websocket_results = self._validate_websocket_endpoints()
        cycle_results.extend(websocket_results)
        
        # Validate Makefile targets
        makefile_results = self._validate_makefile_targets()
        cycle_results.extend(makefile_results)
        
        # Validate documentation accuracy
        documentation_results = self._validate_documentation_accuracy()
        cycle_results.extend(documentation_results)
        
        # Process results
        self._process_validation_results(cycle_results)
        
        self._logger.info(f"Validation cycle completed: {len(cycle_results)} validations")
    
    def _validate_observatory_endpoints(self) -> List[ValidationResult]:
        """Validate Observatory server endpoints."""
        results = []
        endpoints = ["/health", "/ready", "/metrics"]
        
        for endpoint in endpoints:
            result = self._validate_http_endpoint(
                f"{self._config.observatory_url}{endpoint}",
                f"observatory{endpoint}"
            )
            results.append(result)
        
        return results
    
    def _validate_http_endpoint(self, url: str, target: str) -> ValidationResult:
        """Validate a single HTTP endpoint."""
        validation_id = f"http_{target}_{int(time.time())}"
        correlation_id = self._generate_correlation_id() if self._config.correlation_id_enabled else None
        
        start_time = time.time()
        
        try:
            headers = {}
            if correlation_id:
                headers[self._config.correlation_id_header] = correlation_id
            
            response = requests.get(
                url,
                timeout=self._config.makefile_timeout_seconds,
                headers=headers
            )
            
            response_time = (time.time() - start_time) * 1000  # ms
            
            if response.status_code == 200:
                return ValidationResult(
                    validation_id=validation_id,
                    validation_type="endpoint",
                    target=target,
                    status="passed",
                    accuracy_score=1.0,
                    response_time_ms=response_time,
                    correlation_id=correlation_id,
                    metadata={
                        "url": url,
                        "status_code": response.status_code,
                        "content_length": len(response.content)
                    }
                )
            else:
                return ValidationResult(
                    validation_id=validation_id,
                    validation_type="endpoint",
                    target=target,
                    status="failed",
                    accuracy_score=0.0,
                    response_time_ms=response_time,
                    error_message=f"HTTP {response.status_code}",
                    correlation_id=correlation_id,
                    metadata={
                        "url": url,
                        "status_code": response.status_code
                    }
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return ValidationResult(
                validation_id=validation_id,
                validation_type="endpoint",
                target=target,
                status="error",
                accuracy_score=0.0,
                response_time_ms=response_time,
                error_message=str(e),
                correlation_id=correlation_id,
                metadata={"url": url}
            )
    
    def _validate_websocket_endpoints(self) -> List[ValidationResult]:
        """Validate WebSocket endpoints."""
        results = []
        
        for endpoint in self._config.websocket_endpoints:
            result = self._validate_websocket_endpoint(endpoint)
            results.append(result)
        
        return results
    
    def _validate_websocket_endpoint(self, endpoint: str) -> ValidationResult:
        """Validate a single WebSocket endpoint."""
        validation_id = f"websocket_{endpoint.replace('/', '_')}_{int(time.time())}"
        correlation_id = self._generate_correlation_id() if self._config.correlation_id_enabled else None
        
        try:
            # Use WebSocket validator component
            validation_result = self._websocket_validator.validate_endpoint(endpoint)
            
            return ValidationResult(
                validation_id=validation_id,
                validation_type="websocket",
                target=endpoint,
                status="passed" if validation_result["connected"] else "failed",
                accuracy_score=1.0 if validation_result["connected"] else 0.0,
                response_time_ms=validation_result.get("connection_time_ms"),
                error_message=validation_result.get("error"),
                correlation_id=correlation_id,
                metadata=validation_result
            )
            
        except Exception as e:
            return ValidationResult(
                validation_id=validation_id,
                validation_type="websocket",
                target=endpoint,
                status="error",
                accuracy_score=0.0,
                error_message=str(e),
                correlation_id=correlation_id
            )
    
    def _validate_makefile_targets(self) -> List[ValidationResult]:
        """Validate Makefile targets."""
        results = []
        
        for target in self._config.makefile_targets:
            result = self._validate_makefile_target(target)
            results.append(result)
        
        return results
    
    def _validate_makefile_target(self, target: str) -> ValidationResult:
        """Validate a single Makefile target."""
        validation_id = f"makefile_{target}_{int(time.time())}"
        correlation_id = self._generate_correlation_id() if self._config.correlation_id_enabled else None
        
        start_time = time.time()
        
        try:
            # Execute make target with timeout
            result = subprocess.run(
                ["make", target],
                capture_output=True,
                text=True,
                timeout=self._config.makefile_timeout_seconds,
                cwd=Path.cwd()
            )
            
            response_time = (time.time() - start_time) * 1000  # ms
            
            if result.returncode == 0:
                return ValidationResult(
                    validation_id=validation_id,
                    validation_type="makefile",
                    target=target,
                    status="passed",
                    accuracy_score=1.0,
                    response_time_ms=response_time,
                    correlation_id=correlation_id,
                    metadata={
                        "stdout": result.stdout[:500],  # Truncate for storage
                        "stderr": result.stderr[:500],
                        "return_code": result.returncode
                    }
                )
            else:
                return ValidationResult(
                    validation_id=validation_id,
                    validation_type="makefile",
                    target=target,
                    status="failed",
                    accuracy_score=0.0,
                    response_time_ms=response_time,
                    error_message=f"Exit code {result.returncode}",
                    correlation_id=correlation_id,
                    metadata={
                        "stdout": result.stdout[:500],
                        "stderr": result.stderr[:500],
                        "return_code": result.returncode
                    }
                )
                
        except subprocess.TimeoutExpired:
            response_time = (time.time() - start_time) * 1000
            return ValidationResult(
                validation_id=validation_id,
                validation_type="makefile",
                target=target,
                status="error",
                accuracy_score=0.0,
                response_time_ms=response_time,
                error_message="Timeout expired",
                correlation_id=correlation_id
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return ValidationResult(
                validation_id=validation_id,
                validation_type="makefile",
                target=target,
                status="error",
                accuracy_score=0.0,
                response_time_ms=response_time,
                error_message=str(e),
                correlation_id=correlation_id
            )
    
    def _validate_documentation_accuracy(self) -> List[ValidationResult]:
        """Validate documentation accuracy against system behavior."""
        results = []
        
        # Use accuracy monitor to get current accuracy
        accuracy_score = self._accuracy_monitor.get_current_accuracy()
        
        validation_result = ValidationResult(
            validation_id=f"documentation_accuracy_{int(time.time())}",
            validation_type="documentation",
            target="system_documentation",
            status="passed" if accuracy_score >= self._config.accuracy_threshold else "warning",
            accuracy_score=accuracy_score,
            metadata={
                "threshold": self._config.accuracy_threshold,
                "components_validated": self._accuracy_monitor.get_validation_count()
            }
        )
        
        results.append(validation_result)
        return results
    
    async def _validate_websocket_real_time(self) -> None:
        """Validate WebSocket connections in real-time."""
        for endpoint in self._config.websocket_endpoints:
            try:
                websocket_url = f"{self._config.websocket_url}{endpoint}"
                
                async with websockets.connect(websocket_url, timeout=10) as websocket:
                    # Send ping and wait for pong
                    await websocket.ping()
                    
                    # Listen for a message (with timeout)
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        self._logger.debug(f"Received real-time message from {endpoint}")
                    except asyncio.TimeoutError:
                        # No message received, but connection is working
                        pass
                    
            except Exception as e:
                self._logger.warning(f"Real-time WebSocket validation failed for {endpoint}: {e}")
    
    def _process_validation_results(self, results: List[ValidationResult]) -> None:
        """Process validation results and update metrics."""
        if not results:
            return
        
        # Add to results history
        self._validation_results.extend(results)
        
        # Update metrics
        self._total_validations += len(results)
        successful = sum(1 for r in results if r.status == "passed")
        failed = sum(1 for r in results if r.status in ["failed", "error"])
        
        self._successful_validations += successful
        self._failed_validations += failed
        
        # Calculate accuracy
        total_accuracy = sum(r.accuracy_score for r in results)
        cycle_accuracy = total_accuracy / len(results)
        
        # Update running average
        self._average_accuracy = (
            (self._average_accuracy * (self._total_validations - len(results)) + total_accuracy) /
            self._total_validations
        )
        
        # Update response time average
        response_times = [r.response_time_ms for r in results if r.response_time_ms is not None]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            self._average_response_time = (
                (self._average_response_time * (self._total_validations - len(results)) + 
                 sum(response_times)) /
                self._total_validations
            )
        
        # Check for alerts
        if cycle_accuracy < self._config.alert_threshold:
            self._trigger_accuracy_alert(cycle_accuracy)
        
        # Notify callbacks
        for result in results:
            for callback in self._validation_callbacks:
                try:
                    callback(result)
                except Exception as e:
                    self._logger.error(f"Error in validation callback: {e}")
        
        # Update accuracy monitor
        self._accuracy_monitor.record_validation_results(results)
    
    def _trigger_accuracy_alert(self, accuracy: float) -> None:
        """Trigger accuracy alert if cooldown has passed."""
        now = datetime.now()
        
        if (self._last_alert_time is None or 
            now - self._last_alert_time > timedelta(seconds=self._config.alert_cooldown_seconds)):
            
            self._last_alert_time = now
            alert_message = f"Documentation accuracy dropped to {accuracy:.2%} (threshold: {self._config.alert_threshold:.2%})"
            
            self._logger.warning(alert_message)
            
            # Notify alert callbacks
            for callback in self._alert_callbacks:
                try:
                    callback(alert_message, accuracy)
                except Exception as e:
                    self._logger.error(f"Error in alert callback: {e}")
    
    def _generate_correlation_id(self) -> str:
        """Generate correlation ID for tracking."""
        return f"val_{int(time.time() * 1000)}_{hash(threading.current_thread().ident) % 10000}"
    
    def add_validation_callback(self, callback: Callable[[ValidationResult], None]) -> None:
        """Add callback for validation results."""
        self._validation_callbacks.append(callback)
    
    def add_alert_callback(self, callback: Callable[[str, float], None]) -> None:
        """Add callback for accuracy alerts."""
        self._alert_callbacks.append(callback)
    
    def get_validation_summary(self, hours: int = 24) -> ValidationSummary:
        """Get validation summary for the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_results = [
            r for r in self._validation_results
            if r.timestamp > cutoff_time
        ]
        
        if not recent_results:
            return ValidationSummary(
                total_validations=0,
                passed_validations=0,
                failed_validations=0,
                warning_validations=0,
                overall_accuracy=0.0,
                average_response_time=0.0,
                validation_period=timedelta(hours=hours)
            )
        
        passed = sum(1 for r in recent_results if r.status == "passed")
        failed = sum(1 for r in recent_results if r.status in ["failed", "error"])
        warnings = sum(1 for r in recent_results if r.status == "warning")
        
        overall_accuracy = sum(r.accuracy_score for r in recent_results) / len(recent_results)
        
        response_times = [r.response_time_ms for r in recent_results if r.response_time_ms is not None]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
        
        return ValidationSummary(
            total_validations=len(recent_results),
            passed_validations=passed,
            failed_validations=failed,
            warning_validations=warnings,
            overall_accuracy=overall_accuracy,
            average_response_time=avg_response_time,
            validation_period=timedelta(hours=hours)
        )
    
    def force_validation_cycle(self) -> List[ValidationResult]:
        """Force immediate validation cycle."""
        self._logger.info("Forcing validation cycle...")
        
        cycle_results = []
        
        # Run all validation types
        cycle_results.extend(self._validate_observatory_endpoints())
        cycle_results.extend(self._validate_websocket_endpoints())
        cycle_results.extend(self._validate_makefile_targets())
        cycle_results.extend(self._validate_documentation_accuracy())
        
        # Process results
        self._process_validation_results(cycle_results)
        
        return cycle_results
    
    def get_health_status(self) -> Dict[str, Any]:
        """ReflectiveModule health status implementation."""
        return {
            "status": "healthy" if self._is_running else "stopped",
            "validation_system": {
                "running": self._is_running,
                "total_validations": self._total_validations,
                "success_rate": (
                    self._successful_validations / max(1, self._total_validations)
                ) * 100,
                "average_accuracy": self._average_accuracy * 100,
                "average_response_time_ms": self._average_response_time
            },
            "components": {
                "websocket_validator": self._websocket_validator.get_health_status() if hasattr(self._websocket_validator, 'get_health_status') else {"status": "unknown"},
                "accuracy_monitor": self._accuracy_monitor.get_health_status() if hasattr(self._accuracy_monitor, 'get_health_status') else {"status": "unknown"}
            },
            "alerts": {
                "last_alert": self._last_alert_time.isoformat() if self._last_alert_time else None,
                "threshold": self._config.alert_threshold
            }
        }
    
    def get_metrics(self) -> Dict[str, float]:
        """ReflectiveModule metrics implementation."""
        return {
            "validation_total": float(self._total_validations),
            "validation_successful": float(self._successful_validations),
            "validation_failed": float(self._failed_validations),
            "validation_success_rate": (
                self._successful_validations / max(1, self._total_validations)
            ) * 100,
            "validation_average_accuracy": self._average_accuracy * 100,
            "validation_average_response_time_ms": self._average_response_time,
            "validation_running": 1.0 if self._is_running else 0.0,
            "validation_callbacks": float(len(self._validation_callbacks)),
            "validation_alert_callbacks": float(len(self._alert_callbacks))
        }