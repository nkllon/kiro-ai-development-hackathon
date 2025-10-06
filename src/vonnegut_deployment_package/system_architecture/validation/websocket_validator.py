#!/usr/bin/env python3
"""
WebSocket Validator - Phase 5 Task 5.2 Component

Specialized WebSocket connection validation with real-time monitoring,
connection health tracking, and message flow validation.
"""

import asyncio
import json
import time
import websockets
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, asdict
from urllib.parse import urlparse
import ssl

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


@dataclass
class WebSocketEndpoint:
    """Represents a WebSocket endpoint configuration."""
    endpoint_id: str
    url: str
    description: str
    expected_message_types: List[str] = None
    authentication_required: bool = False
    heartbeat_interval: int = 30  # seconds
    connection_timeout: int = 10  # seconds
    message_timeout: int = 5     # seconds
    retry_attempts: int = 3
    retry_delay: float = 2.0
    enabled: bool = True


@dataclass
class WebSocketConnectionStatus:
    """Represents WebSocket connection status."""
    endpoint_id: str
    url: str
    status: str  # 'connected', 'disconnected', 'connecting', 'error'
    connection_time: Optional[datetime] = None
    last_message_time: Optional[datetime] = None
    last_heartbeat_time: Optional[datetime] = None
    message_count: int = 0
    error_count: int = 0
    last_error: Optional[str] = None
    latency_ms: Optional[float] = None
    connection_duration: Optional[float] = None


@dataclass
class WebSocketValidationResult:
    """Represents WebSocket validation result."""
    validation_id: str
    endpoint_id: str
    url: str
    timestamp: datetime
    status: str  # 'passed', 'failed', 'warning'
    connection_successful: bool
    message_received: bool
    heartbeat_successful: bool
    authentication_successful: bool
    latency_ms: float
    execution_time: float
    details: Dict[str, Any]
    error_message: Optional[str] = None
    recommendations: List[str] = None


class WebSocketValidator(ReflectiveModule):
    """
    Specialized WebSocket connection validator.
    
    Validates WebSocket endpoints with comprehensive connection testing,
    message flow validation, and real-time health monitoring.
    """
    
    def __init__(self):
        super().__init__()
        self.endpoints: Dict[str, WebSocketEndpoint] = {}
        self.connection_status: Dict[str, WebSocketConnectionStatus] = {}
        self.validation_history: List[WebSocketValidationResult] = []
        self.active_connections: Dict[str, websockets.WebSocketClientProtocol] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.validation_callbacks: List[Callable[[WebSocketValidationResult], None]] = []
        self.continuous_monitoring = False
        self.max_history_size = 5000
        
        # Initialize default endpoints
        self._initialize_default_endpoints()
        
        # Register capabilities
        self.register_capability('websocket_validation', {
            'description': 'Specialized WebSocket endpoint validation and monitoring',
            'endpoints_configured': len(self.endpoints),
            'continuous_monitoring': self.continuous_monitoring
        })
    
    def _initialize_default_endpoints(self):
        """Initialize default WebSocket endpoints for validation."""
        default_endpoints = [
            WebSocketEndpoint(
                endpoint_id='observatory_main',
                url='ws://localhost:8888/ws/observatory',
                description='Main Observatory WebSocket endpoint',
                expected_message_types=['status', 'metrics', 'health'],
                heartbeat_interval=30,
                connection_timeout=15
            ),
            WebSocketEndpoint(
                endpoint_id='emoji_rain',
                url='ws://localhost:8888/ws/emoji-rain',
                description='Emoji Rain celebration WebSocket',
                expected_message_types=['celebration', 'achievement'],
                heartbeat_interval=60,
                connection_timeout=10
            ),
            WebSocketEndpoint(
                endpoint_id='anomalies',
                url='ws://localhost:8888/ws/anomalies',
                description='Anomaly detection WebSocket',
                expected_message_types=['anomaly', 'alert', 'detection'],
                heartbeat_interval=30,
                connection_timeout=10
            ),
            WebSocketEndpoint(
                endpoint_id='doctor_status',
                url='ws://localhost:8888/ws/doctor-status',
                description='Doctor Status monitoring WebSocket',
                expected_message_types=['status', 'health', 'diagnostic'],
                heartbeat_interval=45,
                connection_timeout=10
            )
        ]
        
        for endpoint in default_endpoints:
            self.endpoints[endpoint.endpoint_id] = endpoint
            self.connection_status[endpoint.endpoint_id] = WebSocketConnectionStatus(
                endpoint_id=endpoint.endpoint_id,
                url=endpoint.url,
                status='disconnected'
            )
    
    async def start_continuous_monitoring(self, check_interval_minutes: int = 5) -> Dict[str, Any]:
        """Start continuous WebSocket monitoring."""
        try:
            if self.continuous_monitoring:
                return {'status': 'already_running'}
            
            self.continuous_monitoring = True
            
            # Start monitoring tasks for each enabled endpoint
            started_tasks = []
            for endpoint_id, endpoint in self.endpoints.items():
                if endpoint.enabled:
                    task = asyncio.create_task(
                        self._monitor_endpoint_continuously(endpoint, check_interval_minutes)
                    )
                    self.monitoring_tasks[endpoint_id] = task
                    started_tasks.append(endpoint_id)
            
            self.logger.info(f"WebSocket continuous monitoring started for {len(started_tasks)} endpoints")
            
            return {
                'status': 'started',
                'monitored_endpoints': started_tasks,
                'check_interval_minutes': check_interval_minutes
            }
            
        except Exception as e:
            self.logger.error(f"Failed to start WebSocket monitoring: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def stop_continuous_monitoring(self) -> Dict[str, Any]:
        """Stop continuous WebSocket monitoring."""
        try:
            self.continuous_monitoring = False
            
            # Cancel all monitoring tasks
            cancelled_tasks = []
            for endpoint_id, task in self.monitoring_tasks.items():
                task.cancel()
                cancelled_tasks.append(endpoint_id)
            
            # Wait for tasks to complete
            if self.monitoring_tasks:
                await asyncio.gather(*self.monitoring_tasks.values(), return_exceptions=True)
            
            self.monitoring_tasks.clear()
            
            # Close active connections
            closed_connections = []
            for endpoint_id, connection in self.active_connections.items():
                if not connection.closed:
                    await connection.close()
                    closed_connections.append(endpoint_id)
            
            self.active_connections.clear()
            
            self.logger.info(f"WebSocket monitoring stopped for {len(cancelled_tasks)} endpoints")
            
            return {
                'status': 'stopped',
                'cancelled_tasks': cancelled_tasks,
                'closed_connections': closed_connections
            }
            
        except Exception as e:
            self.logger.error(f"Error stopping WebSocket monitoring: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _monitor_endpoint_continuously(self, endpoint: WebSocketEndpoint, 
                                           check_interval_minutes: int):
        """Continuously monitor a single WebSocket endpoint."""
        while self.continuous_monitoring:
            try:
                # Validate the endpoint
                result = await self.validate_endpoint(endpoint.endpoint_id)
                
                # Update connection status
                self._update_connection_status(endpoint.endpoint_id, result)
                
                # Wait for next check
                await asyncio.sleep(check_interval_minutes * 60)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error monitoring endpoint {endpoint.endpoint_id}: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def validate_endpoint(self, endpoint_id: str) -> WebSocketValidationResult:
        """Validate a specific WebSocket endpoint."""
        if endpoint_id not in self.endpoints:
            raise ValueError(f"Endpoint {endpoint_id} not found")
        
        endpoint = self.endpoints[endpoint_id]
        start_time = time.time()
        validation_id = f"{endpoint_id}_{int(time.time())}"
        
        try:
            # Perform comprehensive validation
            result = await self._perform_endpoint_validation(endpoint, validation_id, start_time)
            
            # Add to history
            self.validation_history.append(result)
            
            # Trim history if needed
            if len(self.validation_history) > self.max_history_size:
                self.validation_history = self.validation_history[-self.max_history_size:]
            
            # Notify callbacks
            for callback in self.validation_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(result)
                    else:
                        callback(result)
                except Exception as e:
                    self.logger.error(f"Error in validation callback: {e}")
            
            return result
            
        except Exception as e:
            # Create failed result
            result = WebSocketValidationResult(
                validation_id=validation_id,
                endpoint_id=endpoint_id,
                url=endpoint.url,
                timestamp=datetime.now(),
                status='failed',
                connection_successful=False,
                message_received=False,
                heartbeat_successful=False,
                authentication_successful=False,
                latency_ms=0.0,
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e)
            )
            
            self.validation_history.append(result)
            return result
    
    async def _perform_endpoint_validation(self, endpoint: WebSocketEndpoint, 
                                         validation_id: str, start_time: float) -> WebSocketValidationResult:
        """Perform comprehensive endpoint validation."""
        details = {}
        connection_successful = False
        message_received = False
        heartbeat_successful = False
        authentication_successful = not endpoint.authentication_required
        latency_ms = 0.0
        
        try:
            # Test connection
            connection_start = time.time()
            
            # Configure SSL context if needed
            ssl_context = None
            if endpoint.url.startswith('wss://'):
                ssl_context = ssl.create_default_context()
            
            # Connect to WebSocket
            async with websockets.connect(
                endpoint.url,
                timeout=endpoint.connection_timeout,
                ssl=ssl_context
            ) as websocket:
                connection_time = time.time() - connection_start
                connection_successful = True
                latency_ms = connection_time * 1000
                
                details['connection_time_ms'] = latency_ms
                details['connection_successful'] = True
                
                # Test authentication if required
                if endpoint.authentication_required:
                    auth_result = await self._test_authentication(websocket, endpoint)
                    authentication_successful = auth_result['success']
                    details['authentication'] = auth_result
                
                # Test message reception
                message_result = await self._test_message_reception(websocket, endpoint)
                message_received = message_result['received']
                details['message_test'] = message_result
                
                # Test heartbeat/ping
                heartbeat_result = await self._test_heartbeat(websocket, endpoint)
                heartbeat_successful = heartbeat_result['successful']
                details['heartbeat_test'] = heartbeat_result
                
                # Test expected message types if any received
                if message_received and endpoint.expected_message_types:
                    message_type_result = await self._test_message_types(websocket, endpoint)
                    details['message_types_test'] = message_type_result
        
        except asyncio.TimeoutError:
            details['error'] = 'Connection timeout'
            details['timeout_seconds'] = endpoint.connection_timeout
        
        except websockets.exceptions.ConnectionClosed as e:
            details['error'] = f'Connection closed: {e}'
            details['close_code'] = e.code
            details['close_reason'] = e.reason
        
        except Exception as e:
            details['error'] = str(e)
        
        # Determine overall status
        if connection_successful and message_received and heartbeat_successful and authentication_successful:
            status = 'passed'
        elif connection_successful:
            status = 'warning'
        else:
            status = 'failed'
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            endpoint, connection_successful, message_received, 
            heartbeat_successful, authentication_successful, details
        )
        
        return WebSocketValidationResult(
            validation_id=validation_id,
            endpoint_id=endpoint.endpoint_id,
            url=endpoint.url,
            timestamp=datetime.now(),
            status=status,
            connection_successful=connection_successful,
            message_received=message_received,
            heartbeat_successful=heartbeat_successful,
            authentication_successful=authentication_successful,
            latency_ms=latency_ms,
            execution_time=time.time() - start_time,
            details=details,
            recommendations=recommendations
        )
    
    async def _test_authentication(self, websocket: websockets.WebSocketClientProtocol, 
                                 endpoint: WebSocketEndpoint) -> Dict[str, Any]:
        """Test WebSocket authentication."""
        try:
            # Send authentication message (placeholder implementation)
            auth_message = {
                'type': 'auth',
                'token': 'test_token',  # In real implementation, use actual token
                'timestamp': datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(auth_message))
            
            # Wait for auth response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            response_data = json.loads(response)
            
            if response_data.get('type') == 'auth_success':
                return {'success': True, 'response': response_data}
            else:
                return {'success': False, 'response': response_data, 'error': 'Authentication failed'}
        
        except asyncio.TimeoutError:
            return {'success': False, 'error': 'Authentication timeout'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _test_message_reception(self, websocket: websockets.WebSocketClientProtocol, 
                                    endpoint: WebSocketEndpoint) -> Dict[str, Any]:
        """Test message reception from WebSocket."""
        try:
            # Wait for a message
            message = await asyncio.wait_for(websocket.recv(), timeout=endpoint.message_timeout)
            
            # Try to parse as JSON
            try:
                message_data = json.loads(message)
                return {
                    'received': True,
                    'message_type': 'json',
                    'message_size': len(message),
                    'parsed_data': message_data
                }
            except json.JSONDecodeError:
                return {
                    'received': True,
                    'message_type': 'text',
                    'message_size': len(message),
                    'message_preview': message[:100]
                }
        
        except asyncio.TimeoutError:
            return {
                'received': False,
                'error': f'No message received within {endpoint.message_timeout} seconds'
            }
        
        except Exception as e:
            return {'received': False, 'error': str(e)}
    
    async def _test_heartbeat(self, websocket: websockets.WebSocketClientProtocol, 
                            endpoint: WebSocketEndpoint) -> Dict[str, Any]:
        """Test WebSocket heartbeat/ping functionality."""
        try:
            # Send ping
            ping_start = time.time()
            pong_waiter = await websocket.ping()
            
            # Wait for pong
            await asyncio.wait_for(pong_waiter, timeout=5.0)
            ping_time = (time.time() - ping_start) * 1000  # Convert to ms
            
            return {
                'successful': True,
                'ping_time_ms': ping_time
            }
        
        except asyncio.TimeoutError:
            return {'successful': False, 'error': 'Ping timeout'}
        
        except Exception as e:
            return {'successful': False, 'error': str(e)}
    
    async def _test_message_types(self, websocket: websockets.WebSocketClientProtocol, 
                                endpoint: WebSocketEndpoint) -> Dict[str, Any]:
        """Test expected message types."""
        try:
            received_types = set()
            messages_checked = 0
            max_messages = 5
            
            # Collect a few messages to check types
            while messages_checked < max_messages:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    messages_checked += 1
                    
                    try:
                        message_data = json.loads(message)
                        if 'type' in message_data:
                            received_types.add(message_data['type'])
                    except json.JSONDecodeError:
                        pass  # Skip non-JSON messages
                
                except asyncio.TimeoutError:
                    break  # No more messages available
            
            expected_types = set(endpoint.expected_message_types)
            found_types = received_types.intersection(expected_types)
            missing_types = expected_types - received_types
            
            return {
                'expected_types': list(expected_types),
                'received_types': list(received_types),
                'found_types': list(found_types),
                'missing_types': list(missing_types),
                'messages_checked': messages_checked,
                'type_coverage': len(found_types) / len(expected_types) if expected_types else 1.0
            }
        
        except Exception as e:
            return {'error': str(e)}
    
    def _generate_recommendations(self, endpoint: WebSocketEndpoint, 
                                connection_successful: bool, message_received: bool,
                                heartbeat_successful: bool, authentication_successful: bool,
                                details: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        if not connection_successful:
            recommendations.append(f"Check if service is running on {endpoint.url}")
            recommendations.append("Verify network connectivity and firewall settings")
            
            if 'timeout' in details.get('error', '').lower():
                recommendations.append(f"Consider increasing connection timeout (current: {endpoint.connection_timeout}s)")
        
        if connection_successful and not message_received:
            recommendations.append("Check if WebSocket endpoint is actively sending messages")
            recommendations.append(f"Consider increasing message timeout (current: {endpoint.message_timeout}s)")
        
        if connection_successful and not heartbeat_successful:
            recommendations.append("Check WebSocket ping/pong implementation")
            recommendations.append("Verify heartbeat configuration on server side")
        
        if endpoint.authentication_required and not authentication_successful:
            recommendations.append("Verify authentication token and credentials")
            recommendations.append("Check authentication implementation on server side")
        
        # Performance recommendations
        latency_ms = details.get('connection_time_ms', 0)
        if latency_ms > 1000:  # > 1 second
            recommendations.append(f"High connection latency ({latency_ms:.1f}ms) - investigate network issues")
        elif latency_ms > 500:  # > 500ms
            recommendations.append(f"Elevated connection latency ({latency_ms:.1f}ms) - monitor performance")
        
        return recommendations
    
    def _update_connection_status(self, endpoint_id: str, result: WebSocketValidationResult):
        """Update connection status based on validation result."""
        status = self.connection_status[endpoint_id]
        
        if result.connection_successful:
            status.status = 'connected'
            status.connection_time = result.timestamp
            status.latency_ms = result.latency_ms
            status.connection_duration = result.execution_time
            
            if result.message_received:
                status.last_message_time = result.timestamp
                status.message_count += 1
            
            if result.heartbeat_successful:
                status.last_heartbeat_time = result.timestamp
        else:
            status.status = 'error'
            status.error_count += 1
            status.last_error = result.error_message
    
    def add_endpoint(self, endpoint: WebSocketEndpoint):
        """Add a new WebSocket endpoint for validation."""
        self.endpoints[endpoint.endpoint_id] = endpoint
        self.connection_status[endpoint.endpoint_id] = WebSocketConnectionStatus(
            endpoint_id=endpoint.endpoint_id,
            url=endpoint.url,
            status='disconnected'
        )
        
        self.logger.info(f"Added WebSocket endpoint: {endpoint.endpoint_id} ({endpoint.url})")
    
    def remove_endpoint(self, endpoint_id: str) -> bool:
        """Remove a WebSocket endpoint."""
        if endpoint_id in self.endpoints:
            # Stop monitoring if active
            if endpoint_id in self.monitoring_tasks:
                self.monitoring_tasks[endpoint_id].cancel()
                del self.monitoring_tasks[endpoint_id]
            
            # Close connection if active
            if endpoint_id in self.active_connections:
                asyncio.create_task(self.active_connections[endpoint_id].close())
                del self.active_connections[endpoint_id]
            
            # Remove from tracking
            del self.endpoints[endpoint_id]
            del self.connection_status[endpoint_id]
            
            self.logger.info(f"Removed WebSocket endpoint: {endpoint_id}")
            return True
        
        return False
    
    def get_endpoint_status(self, endpoint_id: Optional[str] = None) -> Dict[str, Any]:
        """Get connection status for endpoint(s)."""
        if endpoint_id:
            if endpoint_id in self.connection_status:
                return asdict(self.connection_status[endpoint_id])
            else:
                return {}
        else:
            return {
                endpoint_id: asdict(status) 
                for endpoint_id, status in self.connection_status.items()
            }
    
    def get_validation_history(self, endpoint_id: Optional[str] = None, 
                             limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get validation history with optional filtering."""
        history = self.validation_history
        
        # Filter by endpoint
        if endpoint_id:
            history = [r for r in history if r.endpoint_id == endpoint_id]
        
        # Apply limit
        if limit:
            history = history[-limit:]
        
        return [asdict(result) for result in history]
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation summary statistics."""
        if not self.validation_history:
            return {
                'total_validations': 0,
                'success_rate': 0.0,
                'endpoints_monitored': len(self.endpoints)
            }
        
        total_validations = len(self.validation_history)
        successful_validations = len([r for r in self.validation_history if r.status == 'passed'])
        success_rate = successful_validations / total_validations
        
        # Recent validations (last hour)
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_validations = [r for r in self.validation_history if r.timestamp > one_hour_ago]
        
        # Endpoint breakdown
        endpoint_stats = {}
        for endpoint_id in self.endpoints:
            endpoint_validations = [r for r in self.validation_history if r.endpoint_id == endpoint_id]
            if endpoint_validations:
                endpoint_success = len([r for r in endpoint_validations if r.status == 'passed'])
                endpoint_stats[endpoint_id] = {
                    'total_validations': len(endpoint_validations),
                    'success_rate': endpoint_success / len(endpoint_validations),
                    'last_validation': max(r.timestamp for r in endpoint_validations).isoformat(),
                    'current_status': self.connection_status[endpoint_id].status
                }
        
        return {
            'total_validations': total_validations,
            'successful_validations': successful_validations,
            'success_rate': success_rate,
            'recent_validations_1h': len(recent_validations),
            'endpoints_monitored': len(self.endpoints),
            'continuous_monitoring': self.continuous_monitoring,
            'endpoint_statistics': endpoint_stats
        }
    
    def add_validation_callback(self, callback: Callable[[WebSocketValidationResult], None]):
        """Add a callback for validation results."""
        self.validation_callbacks.append(callback)
    
    def remove_validation_callback(self, callback: Callable[[WebSocketValidationResult], None]):
        """Remove a validation callback."""
        if callback in self.validation_callbacks:
            self.validation_callbacks.remove(callback)
    
    # ReflectiveModule health endpoints
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint."""
        summary = self.get_validation_summary()
        
        return {
            'status': 'healthy',
            'continuous_monitoring': self.continuous_monitoring,
            'endpoints_monitored': summary['endpoints_monitored'],
            'success_rate': summary['success_rate'],
            'monitoring_tasks_active': len(self.monitoring_tasks)
        }
    
    async def ready_check(self) -> Dict[str, Any]:
        """Readiness check endpoint."""
        return {
            'ready': True,
            'endpoints_configured': len(self.endpoints) > 0,
            'monitoring_available': True
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get WebSocket validation metrics."""
        summary = self.get_validation_summary()
        
        return {
            'websocket_validator_total_validations': summary['total_validations'],
            'websocket_validator_success_rate': summary['success_rate'],
            'websocket_validator_endpoints_monitored': summary['endpoints_monitored'],
            'websocket_validator_continuous_monitoring': 1 if self.continuous_monitoring else 0,
            'websocket_validator_monitoring_tasks': len(self.monitoring_tasks)
        }


# Example usage and testing
if __name__ == "__main__":
    async def main():
        # Create WebSocket validator
        validator = WebSocketValidator()
        
        # Add validation callback
        async def handle_validation(result: WebSocketValidationResult):
            print(f"Validation result: {result.endpoint_id} - {result.status}")
        
        validator.add_validation_callback(handle_validation)
        
        # Validate a single endpoint
        result = await validator.validate_endpoint('observatory_main')
        print(f"Single validation: {result.status}")
        
        # Start continuous monitoring
        monitoring_result = await validator.start_continuous_monitoring(check_interval_minutes=2)
        print(f"Monitoring started: {monitoring_result}")
        
        # Wait a bit
        await asyncio.sleep(10)
        
        # Get summary
        summary = validator.get_validation_summary()
        print(f"Summary: {summary}")
        
        # Stop monitoring
        await validator.stop_continuous_monitoring()
    
    asyncio.run(main())