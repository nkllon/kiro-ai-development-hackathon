"""
IntegrationTester - Performs end-to-end WebSocket functionality testing.

This module implements comprehensive end-to-end WebSocket testing including:
- Real WebSocket connection establishment and lifecycle testing
- Bidirectional message delivery validation
- Feature-specific testing (emoji rain, etc.)
- Performance and load testing
- Connection failure and recovery scenarios

Implements requirements 6.1, 6.2, 6.3 from the WebSocket validation specification.
"""

import asyncio
import json
import time
import websockets
import concurrent.futures
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urlparse

from ..models import TestResult, TestStatus, ConnectionAnalysis, MessageAnalysis, PerformanceAnalysis
from ..config import ValidationConfig
from ..collectors import EvidenceCollector
from ..utils.logging import get_logger, log_test_start, log_test_end
from ..utils.errors import ValidationError


class IntegrationTester:
    """
    Performs end-to-end WebSocket functionality testing.
    
    Establishes real WebSocket connections, tests message delivery and reception,
    validates emoji rain and other features, and performs load and stress testing.
    """
    
    def __init__(self, config: ValidationConfig, evidence_collector: EvidenceCollector):
        """Initialize IntegrationTester."""
        self.config = config
        self.evidence_collector = evidence_collector
        self.logger = get_logger(__name__)
        
        # WebSocket endpoints to test
        self.websocket_endpoints = [
            "ws://localhost:8000/ws/emoji-rain",
            "ws://localhost:8000/ws/observatory", 
            "ws://localhost:8000/ws/test"
        ]
        
        # Test domains for external testing
        self.test_domains = [
            "nkllon.com",
            "louspringer.com"
        ]
    
    def run_all_tests(self) -> List[TestResult]:
        """
        Run all integration tests.
        
        Returns:
            List[TestResult]: Results from all integration tests
        """
        self.logger.info("Running all integration tests")
        results = []
        
        # Phase 1: End-to-end WebSocket connection testing
        connection_results = self.test_websocket_connections()
        results.extend(connection_results)
        
        # Phase 2: Feature-specific testing (emoji rain)
        feature_results = self.test_websocket_features()
        results.extend(feature_results)
        
        # Phase 3: Performance and load testing
        performance_results = self.test_websocket_performance()
        results.extend(performance_results)
        
        self.logger.info(f"Integration testing completed: {len(results)} tests run")
        return results  
  
    def test_websocket_connections(self) -> List[TestResult]:
        """Test end-to-end WebSocket connections."""
        self.logger.info("Testing WebSocket connections")
        results = []
        
        for endpoint in self.websocket_endpoints:
            connection_result = self._test_single_websocket_connection(endpoint)
            results.append(connection_result)
        
        return results
    
    def _test_single_websocket_connection(self, endpoint: str) -> TestResult:
        """Test a single WebSocket connection end-to-end."""
        test_name = f"websocket_connection_{self._sanitize_endpoint_name(endpoint)}"
        start_time = datetime.utcnow()
        
        log_test_start(self.logger, test_name, "integration")
        
        try:
            # Run the async WebSocket test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                connection_analysis = loop.run_until_complete(
                    self._async_test_websocket_connection(endpoint)
                )
            finally:
                loop.close()
            
            # Store connection analysis as evidence
            connection_data = {
                "endpoint": endpoint,
                "connection_analysis": {
                    "connection_successful": connection_analysis.connection_successful,
                    "connection_time": connection_analysis.connection_time,
                    "messages_sent": connection_analysis.messages_sent,
                    "messages_received": connection_analysis.messages_received,
                    "message_delivery_success": connection_analysis.message_delivery_success,
                    "connection_errors": connection_analysis.connection_errors,
                    "graceful_closure": connection_analysis.graceful_closure
                },
                "test_timestamp": connection_analysis.test_timestamp.isoformat()
            }
            
            evidence_id = self.evidence_collector.snapshot_configuration(
                config_type="websocket_connection_test",
                config_data=connection_data
            )
            
            # Determine test status
            if connection_analysis.connection_errors:
                status = TestStatus.FAILED
                error_details = f"Connection errors: {', '.join(connection_analysis.connection_errors)}"
            elif not connection_analysis.connection_successful:
                status = TestStatus.FAILED
                error_details = "WebSocket connection failed"
            elif not connection_analysis.message_delivery_success:
                status = TestStatus.FAILED
                error_details = "Message delivery failed"
            else:
                status = TestStatus.PASSED
                error_details = None
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            test_result = TestResult(
                test_name=test_name,
                test_category="integration",
                status=status,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                evidence_ids=[evidence_id],
                metrics={
                    "endpoint": endpoint,
                    "connection_successful": connection_analysis.connection_successful,
                    "connection_time": connection_analysis.connection_time,
                    "messages_sent": connection_analysis.messages_sent,
                    "messages_received": connection_analysis.messages_received,
                    "message_delivery_success": connection_analysis.message_delivery_success,
                    "graceful_closure": connection_analysis.graceful_closure,
                    "connection_errors": len(connection_analysis.connection_errors)
                },
                error_details=error_details,
                assertions_passed=1 if status == TestStatus.PASSED else 0,
                assertions_failed=1 if status == TestStatus.FAILED else 0
            )
            
            log_test_end(
                self.logger, test_name, "integration",
                status.value, execution_time,
                f"Connection: {connection_analysis.connection_successful}, Messages: {connection_analysis.messages_sent}/{connection_analysis.messages_received}"
            )
            
            return test_result
            
        except Exception as e:
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            self.logger.error(f"WebSocket connection test failed for {endpoint}: {e}")
            
            test_result = TestResult(
                test_name=test_name,
                test_category="integration",
                status=TestStatus.ERROR,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                error_details=str(e),
                assertions_passed=0,
                assertions_failed=1
            )
            
            log_test_end(
                self.logger, test_name, "integration",
                "ERROR", execution_time, str(e)
            )
            
            return test_result   
 
    async def _async_test_websocket_connection(self, endpoint: str) -> ConnectionAnalysis:
        """Async method to test WebSocket connection."""
        connection_successful = False
        connection_time = 0.0
        messages_sent = 0
        messages_received = 0
        message_delivery_success = False
        connection_errors = []
        graceful_closure = False
        
        connection_start = time.time()
        
        try:
            # Attempt to connect to WebSocket
            async with websockets.connect(endpoint, timeout=10) as websocket:
                connection_time = time.time() - connection_start
                connection_successful = True
                
                # Test message sending and receiving
                test_messages = [
                    {"type": "test", "message": "Hello WebSocket"},
                    {"type": "ping", "timestamp": datetime.utcnow().isoformat()},
                    {"type": "echo", "data": "test_data_123"}
                ]
                
                for test_message in test_messages:
                    try:
                        # Send message
                        await websocket.send(json.dumps(test_message))
                        messages_sent += 1
                        
                        # Try to receive response (with timeout)
                        try:
                            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                            messages_received += 1
                            
                            # Validate response
                            try:
                                response_data = json.loads(response)
                                self.logger.debug(f"Received response: {response_data}")
                            except json.JSONDecodeError:
                                self.logger.debug(f"Received non-JSON response: {response}")
                                
                        except asyncio.TimeoutError:
                            connection_errors.append(f"Timeout waiting for response to message: {test_message['type']}")
                            
                    except Exception as e:
                        connection_errors.append(f"Error sending message {test_message['type']}: {str(e)}")
                
                # Check if message delivery was successful
                message_delivery_success = messages_sent > 0 and messages_received > 0
                
                # Test graceful closure
                try:
                    await websocket.close()
                    graceful_closure = True
                except Exception as e:
                    connection_errors.append(f"Error during graceful closure: {str(e)}")
                    
        except websockets.exceptions.ConnectionClosed as e:
            connection_errors.append(f"Connection closed unexpectedly: {str(e)}")
        except websockets.exceptions.InvalidURI as e:
            connection_errors.append(f"Invalid WebSocket URI: {str(e)}")
        except websockets.exceptions.InvalidHandshake as e:
            connection_errors.append(f"Invalid WebSocket handshake: {str(e)}")
        except asyncio.TimeoutError:
            connection_errors.append("Connection timeout")
        except Exception as e:
            connection_errors.append(f"Unexpected connection error: {str(e)}")
        
        return ConnectionAnalysis(
            endpoint=endpoint,
            connection_successful=connection_successful,
            connection_time=connection_time,
            messages_sent=messages_sent,
            messages_received=messages_received,
            message_delivery_success=message_delivery_success,
            connection_errors=connection_errors,
            graceful_closure=graceful_closure,
            test_timestamp=datetime.utcnow()
        )
    
    def test_websocket_features(self) -> List[TestResult]:
        """Test WebSocket feature-specific functionality."""
        self.logger.info("Testing WebSocket features")
        results = []
        
        # Test emoji rain feature
        emoji_rain_result = self._test_emoji_rain_feature()
        results.append(emoji_rain_result)
        
        # Test observatory feature
        observatory_result = self._test_observatory_feature()
        results.append(observatory_result)
        
        return results
    
    def _test_emoji_rain_feature(self) -> TestResult:
        """Test emoji rain WebSocket feature."""
        test_name = "emoji_rain_feature_test"
        start_time = datetime.utcnow()
        
        log_test_start(self.logger, test_name, "integration")
        
        try:
            # Test emoji rain endpoint
            endpoint = "ws://localhost:8000/ws/emoji-rain"
            
            # Run the async emoji rain test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                feature_analysis = loop.run_until_complete(
                    self._async_test_emoji_rain_feature(endpoint)
                )
            finally:
                loop.close()
            
            # Store feature analysis as evidence
            feature_data = {
                "endpoint": endpoint,
                "feature": "emoji_rain",
                "feature_analysis": {
                    "connection_successful": feature_analysis.get("connection_successful", False),
                    "emoji_messages_received": feature_analysis.get("emoji_messages_received", 0),
                    "message_format_valid": feature_analysis.get("message_format_valid", False),
                    "real_time_delivery": feature_analysis.get("real_time_delivery", False),
                    "feature_errors": feature_analysis.get("feature_errors", [])
                },
                "test_timestamp": datetime.utcnow().isoformat()
            }
            
            evidence_id = self.evidence_collector.snapshot_configuration(
                config_type="websocket_feature_test",
                config_data=feature_data
            )
            
            # Determine test status
            feature_errors = feature_analysis.get("feature_errors", [])
            if feature_errors:
                status = TestStatus.FAILED
                error_details = f"Feature errors: {', '.join(feature_errors)}"
            elif not feature_analysis.get("connection_successful", False):
                status = TestStatus.FAILED
                error_details = "Failed to connect to emoji rain endpoint"
            else:
                status = TestStatus.PASSED
                error_details = None
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            test_result = TestResult(
                test_name=test_name,
                test_category="integration",
                status=status,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                evidence_ids=[evidence_id],
                metrics={
                    "endpoint": endpoint,
                    "connection_successful": feature_analysis.get("connection_successful", False),
                    "emoji_messages_received": feature_analysis.get("emoji_messages_received", 0),
                    "message_format_valid": feature_analysis.get("message_format_valid", False),
                    "real_time_delivery": feature_analysis.get("real_time_delivery", False),
                    "feature_errors": len(feature_errors)
                },
                error_details=error_details,
                assertions_passed=1 if status == TestStatus.PASSED else 0,
                assertions_failed=1 if status == TestStatus.FAILED else 0
            )
            
            log_test_end(
                self.logger, test_name, "integration",
                status.value, execution_time,
                f"Emoji messages: {feature_analysis.get('emoji_messages_received', 0)}"
            )
            
            return test_result
            
        except Exception as e:
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            self.logger.error(f"Emoji rain feature test failed: {e}")
            
            test_result = TestResult(
                test_name=test_name,
                test_category="integration",
                status=TestStatus.ERROR,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                error_details=str(e),
                assertions_passed=0,
                assertions_failed=1
            )
            
            log_test_end(
                self.logger, test_name, "integration",
                "ERROR", execution_time, str(e)
            )
            
            return test_result    
    
async def _async_test_emoji_rain_feature(self, endpoint: str) -> Dict[str, Any]:
        """Async method to test emoji rain feature."""
        feature_analysis = {
            "connection_successful": False,
            "emoji_messages_received": 0,
            "message_format_valid": False,
            "real_time_delivery": False,
            "feature_errors": []
        }
        
        try:
            async with websockets.connect(endpoint, timeout=10) as websocket:
                feature_analysis["connection_successful"] = True
                
                # Send emoji rain request
                emoji_request = {
                    "type": "start_emoji_rain",
                    "duration": 5,
                    "emoji_types": ["🎉", "🚀", "⭐", "💫"]
                }
                
                await websocket.send(json.dumps(emoji_request))
                
                # Listen for emoji messages for a short duration
                start_time = time.time()
                timeout_duration = 10  # seconds
                
                while time.time() - start_time < timeout_duration:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                        
                        try:
                            message_data = json.loads(message)
                            
                            # Check if it's an emoji rain message
                            if message_data.get("type") == "emoji" or "emoji" in message_data:
                                feature_analysis["emoji_messages_received"] += 1
                                feature_analysis["message_format_valid"] = True
                                feature_analysis["real_time_delivery"] = True
                                
                        except json.JSONDecodeError:
                            # Handle non-JSON messages
                            if any(emoji in message for emoji in ["🎉", "🚀", "⭐", "💫"]):
                                feature_analysis["emoji_messages_received"] += 1
                                feature_analysis["real_time_delivery"] = True
                                
                    except asyncio.TimeoutError:
                        # No message received in timeout period, continue listening
                        continue
                    except Exception as e:
                        feature_analysis["feature_errors"].append(f"Error receiving message: {str(e)}")
                        break
                
        except Exception as e:
            feature_analysis["feature_errors"].append(f"Connection error: {str(e)}")
        
        return feature_analysis
    
    def _test_observatory_feature(self) -> TestResult:
        """Test observatory WebSocket feature."""
        test_name = "observatory_feature_test"
        start_time = datetime.utcnow()
        
        log_test_start(self.logger, test_name, "integration")
        
        try:
            # Test observatory endpoint
            endpoint = "ws://localhost:8000/ws/observatory"
            
            # Run the async observatory test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                feature_analysis = loop.run_until_complete(
                    self._async_test_observatory_feature(endpoint)
                )
            finally:
                loop.close()
            
            # Store feature analysis as evidence
            feature_data = {
                "endpoint": endpoint,
                "feature": "observatory",
                "feature_analysis": feature_analysis,
                "test_timestamp": datetime.utcnow().isoformat()
            }
            
            evidence_id = self.evidence_collector.snapshot_configuration(
                config_type="websocket_feature_test",
                config_data=feature_data
            )
            
            # Determine test status
            feature_errors = feature_analysis.get("feature_errors", [])
            if feature_errors:
                status = TestStatus.FAILED
                error_details = f"Feature errors: {', '.join(feature_errors)}"
            elif not feature_analysis.get("connection_successful", False):
                status = TestStatus.FAILED
                error_details = "Failed to connect to observatory endpoint"
            else:
                status = TestStatus.PASSED
                error_details = None
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            test_result = TestResult(
                test_name=test_name,
                test_category="integration",
                status=status,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                evidence_ids=[evidence_id],
                metrics={
                    "endpoint": endpoint,
                    "connection_successful": feature_analysis.get("connection_successful", False),
                    "status_messages_received": feature_analysis.get("status_messages_received", 0),
                    "real_time_updates": feature_analysis.get("real_time_updates", False),
                    "feature_errors": len(feature_errors)
                },
                error_details=error_details,
                assertions_passed=1 if status == TestStatus.PASSED else 0,
                assertions_failed=1 if status == TestStatus.FAILED else 0
            )
            
            log_test_end(
                self.logger, test_name, "integration",
                status.value, execution_time,
                f"Status messages: {feature_analysis.get('status_messages_received', 0)}"
            )
            
            return test_result
            
        except Exception as e:
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            self.logger.error(f"Observatory feature test failed: {e}")
            
            test_result = TestResult(
                test_name=test_name,
                test_category="integration",
                status=TestStatus.ERROR,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                error_details=str(e),
                assertions_passed=0,
                assertions_failed=1
            )
            
            log_test_end(
                self.logger, test_name, "integration",
                "ERROR", execution_time, str(e)
            )
            
            return test_result
    
    async def _async_test_observatory_feature(self, endpoint: str) -> Dict[str, Any]:
        """Async method to test observatory feature."""
        feature_analysis = {
            "connection_successful": False,
            "status_messages_received": 0,
            "real_time_updates": False,
            "feature_errors": []
        }
        
        try:
            async with websockets.connect(endpoint, timeout=10) as websocket:
                feature_analysis["connection_successful"] = True
                
                # Send observatory status request
                status_request = {
                    "type": "get_status",
                    "components": ["all"]
                }
                
                await websocket.send(json.dumps(status_request))
                
                # Listen for status messages
                start_time = time.time()
                timeout_duration = 8  # seconds
                
                while time.time() - start_time < timeout_duration:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                        
                        try:
                            message_data = json.loads(message)
                            
                            # Check if it's a status message
                            if (message_data.get("type") == "status" or 
                                "status" in message_data or 
                                "components" in message_data):
                                feature_analysis["status_messages_received"] += 1
                                feature_analysis["real_time_updates"] = True
                                
                        except json.JSONDecodeError:
                            # Handle non-JSON status messages
                            if "status" in message.lower():
                                feature_analysis["status_messages_received"] += 1
                                feature_analysis["real_time_updates"] = True
                                
                    except asyncio.TimeoutError:
                        # No message received in timeout period, continue listening
                        continue
                    except Exception as e:
                        feature_analysis["feature_errors"].append(f"Error receiving message: {str(e)}")
                        break
                
        except Exception as e:
            feature_analysis["feature_errors"].append(f"Connection error: {str(e)}")
        
        return feature_analysis
    
    def test_websocket_performance(self) -> List[TestResult]:
        """Test WebSocket performance and load."""
        self.logger.info("Testing WebSocket performance")
        results = []
        
        # Test basic performance
        performance_result = self._test_websocket_performance()
        results.append(performance_result)
        
        # Test concurrent connections
        concurrent_result = self._test_concurrent_connections()
        results.append(concurrent_result)
        
        return results
    
    def _test_websocket_performance(self) -> TestResult:
        """Test WebSocket performance metrics."""
        test_name = "websocket_performance_test"
        start_time = datetime.utcnow()
        
        log_test_start(self.logger, test_name, "integration")
        
        try:
            # Test performance on primary endpoint
            endpoint = "ws://localhost:8000/ws/test"
            
            # Run the async performance test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                performance_analysis = loop.run_until_complete(
                    self._async_test_websocket_performance(endpoint)
                )
            finally:
                loop.close()
            
            # Store performance analysis as evidence
            performance_data = {
                "endpoint": endpoint,
                "performance_analysis": performance_analysis,
                "test_timestamp": datetime.utcnow().isoformat()
            }
            
            evidence_id = self.evidence_collector.snapshot_configuration(
                config_type="websocket_performance_test",
                config_data=performance_data
            )
            
            # Determine test status based on performance metrics
            avg_latency = performance_analysis.get("average_latency", float('inf'))
            message_throughput = performance_analysis.get("message_throughput", 0)
            performance_errors = performance_analysis.get("performance_errors", [])
            
            if performance_errors:
                status = TestStatus.FAILED
                error_details = f"Performance errors: {', '.join(performance_errors)}"
            elif avg_latency > 1000:  # 1 second threshold
                status = TestStatus.FAILED
                error_details = f"High latency: {avg_latency:.2f}ms"
            elif message_throughput < 10:  # 10 messages/second threshold
                status = TestStatus.FAILED
                error_details = f"Low throughput: {message_throughput:.2f} msg/s"
            else:
                status = TestStatus.PASSED
                error_details = None
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            test_result = TestResult(
                test_name=test_name,
                test_category="integration",
                status=status,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                evidence_ids=[evidence_id],
                metrics={
                    "endpoint": endpoint,
                    "average_latency": avg_latency,
                    "message_throughput": message_throughput,
                    "total_messages": performance_analysis.get("total_messages", 0),
                    "connection_time": performance_analysis.get("connection_time", 0),
                    "performance_errors": len(performance_errors)
                },
                error_details=error_details,
                assertions_passed=1 if status == TestStatus.PASSED else 0,
                assertions_failed=1 if status == TestStatus.FAILED else 0
            )
            
            log_test_end(
                self.logger, test_name, "integration",
                status.value, execution_time,
                f"Latency: {avg_latency:.2f}ms, Throughput: {message_throughput:.2f} msg/s"
            )
            
            return test_result
            
        except Exception as e:
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            self.logger.error(f"WebSocket performance test failed: {e}")
            
            test_result = TestResult(
                test_name=test_name,
                test_category="integration",
                status=TestStatus.ERROR,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                error_details=str(e),
                assertions_passed=0,
                assertions_failed=1
            )
            
            log_test_end(
                self.logger, test_name, "integration",
                "ERROR", execution_time, str(e)
            )
            
            return test_result    
 
   async def _async_test_websocket_performance(self, endpoint: str) -> Dict[str, Any]:
        """Async method to test WebSocket performance."""
        performance_analysis = {
            "connection_time": 0.0,
            "total_messages": 0,
            "average_latency": 0.0,
            "message_throughput": 0.0,
            "performance_errors": []
        }
        
        try:
            connection_start = time.time()
            
            async with websockets.connect(endpoint, timeout=10) as websocket:
                performance_analysis["connection_time"] = time.time() - connection_start
                
                # Performance test parameters
                num_messages = 50
                latencies = []
                
                test_start = time.time()
                
                # Send messages and measure latency
                for i in range(num_messages):
                    message = {
                        "type": "performance_test",
                        "sequence": i,
                        "timestamp": time.time()
                    }
                    
                    message_start = time.time()
                    
                    try:
                        await websocket.send(json.dumps(message))
                        
                        # Wait for response
                        response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        
                        message_latency = (time.time() - message_start) * 1000  # Convert to ms
                        latencies.append(message_latency)
                        
                        performance_analysis["total_messages"] += 1
                        
                    except asyncio.TimeoutError:
                        performance_analysis["performance_errors"].append(f"Timeout for message {i}")
                    except Exception as e:
                        performance_analysis["performance_errors"].append(f"Error for message {i}: {str(e)}")
                
                test_duration = time.time() - test_start
                
                # Calculate performance metrics
                if latencies:
                    performance_analysis["average_latency"] = sum(latencies) / len(latencies)
                
                if test_duration > 0:
                    performance_analysis["message_throughput"] = performance_analysis["total_messages"] / test_duration
                
        except Exception as e:
            performance_analysis["performance_errors"].append(f"Connection error: {str(e)}")
        
        return performance_analysis
    
    def _test_concurrent_connections(self) -> TestResult:
        """Test concurrent WebSocket connections."""
        test_name = "concurrent_connections_test"
        start_time = datetime.utcnow()
        
        log_test_start(self.logger, test_name, "integration")
        
        try:
            # Test concurrent connections
            endpoint = "ws://localhost:8000/ws/test"
            num_connections = 5  # Conservative number for testing
            
            # Run the async concurrent test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                concurrent_analysis = loop.run_until_complete(
                    self._async_test_concurrent_connections(endpoint, num_connections)
                )
            finally:
                loop.close()
            
            # Store concurrent analysis as evidence
            concurrent_data = {
                "endpoint": endpoint,
                "num_connections": num_connections,
                "concurrent_analysis": concurrent_analysis,
                "test_timestamp": datetime.utcnow().isoformat()
            }
            
            evidence_id = self.evidence_collector.snapshot_configuration(
                config_type="websocket_concurrent_test",
                config_data=concurrent_data
            )
            
            # Determine test status
            successful_connections = concurrent_analysis.get("successful_connections", 0)
            concurrent_errors = concurrent_analysis.get("concurrent_errors", [])
            
            if concurrent_errors:
                status = TestStatus.FAILED
                error_details = f"Concurrent errors: {', '.join(concurrent_errors[:3])}"  # Show first 3 errors
            elif successful_connections < num_connections * 0.8:  # 80% success threshold
                status = TestStatus.FAILED
                error_details = f"Low connection success rate: {successful_connections}/{num_connections}"
            else:
                status = TestStatus.PASSED
                error_details = None
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            test_result = TestResult(
                test_name=test_name,
                test_category="integration",
                status=status,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                evidence_ids=[evidence_id],
                metrics={
                    "endpoint": endpoint,
                    "num_connections": num_connections,
                    "successful_connections": successful_connections,
                    "connection_success_rate": (successful_connections / num_connections) * 100,
                    "average_connection_time": concurrent_analysis.get("average_connection_time", 0),
                    "concurrent_errors": len(concurrent_errors)
                },
                error_details=error_details,
                assertions_passed=1 if status == TestStatus.PASSED else 0,
                assertions_failed=1 if status == TestStatus.FAILED else 0
            )
            
            log_test_end(
                self.logger, test_name, "integration",
                status.value, execution_time,
                f"Connections: {successful_connections}/{num_connections}"
            )
            
            return test_result
            
        except Exception as e:
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            self.logger.error(f"Concurrent connections test failed: {e}")
            
            test_result = TestResult(
                test_name=test_name,
                test_category="integration",
                status=TestStatus.ERROR,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                error_details=str(e),
                assertions_passed=0,
                assertions_failed=1
            )
            
            log_test_end(
                self.logger, test_name, "integration",
                "ERROR", execution_time, str(e)
            )
            
            return test_result
    
    async def _async_test_concurrent_connections(self, endpoint: str, num_connections: int) -> Dict[str, Any]:
        """Async method to test concurrent WebSocket connections."""
        concurrent_analysis = {
            "successful_connections": 0,
            "average_connection_time": 0.0,
            "concurrent_errors": []
        }
        
        async def test_single_connection(connection_id: int) -> Tuple[bool, float]:
            """Test a single concurrent connection."""
            try:
                connection_start = time.time()
                
                async with websockets.connect(endpoint, timeout=10) as websocket:
                    connection_time = time.time() - connection_start
                    
                    # Send a test message
                    test_message = {
                        "type": "concurrent_test",
                        "connection_id": connection_id,
                        "timestamp": time.time()
                    }
                    
                    await websocket.send(json.dumps(test_message))
                    
                    # Try to receive response
                    try:
                        await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    except asyncio.TimeoutError:
                        pass  # Response not required for concurrent test
                    
                    return True, connection_time
                    
            except Exception as e:
                concurrent_analysis["concurrent_errors"].append(f"Connection {connection_id}: {str(e)}")
                return False, 0.0
        
        # Create concurrent connection tasks
        tasks = [test_single_connection(i) for i in range(num_connections)]
        
        try:
            # Run all connections concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            connection_times = []
            
            for result in results:
                if isinstance(result, tuple):
                    success, connection_time = result
                    if success:
                        concurrent_analysis["successful_connections"] += 1
                        connection_times.append(connection_time)
                elif isinstance(result, Exception):
                    concurrent_analysis["concurrent_errors"].append(f"Task exception: {str(result)}")
            
            # Calculate average connection time
            if connection_times:
                concurrent_analysis["average_connection_time"] = sum(connection_times) / len(connection_times)
                
        except Exception as e:
            concurrent_analysis["concurrent_errors"].append(f"Concurrent test error: {str(e)}")
        
        return concurrent_analysis
    
    def _sanitize_endpoint_name(self, endpoint: str) -> str:
        """Sanitize endpoint name for use in test names."""
        # Remove protocol and replace special characters
        name = endpoint.replace("ws://", "").replace("wss://", "")
        name = name.replace("/", "_").replace(":", "_").replace(".", "_")
        return name