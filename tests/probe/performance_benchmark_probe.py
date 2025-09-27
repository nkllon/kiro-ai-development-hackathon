"""
Performance Benchmark Probe

Tests WebSocket latency, throughput, concurrent connections, memory usage,
CPU usage, and overall system performance under various load conditions.
"""

import asyncio
import json
import time
import psutil
import websockets
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import aiohttp


@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    metric_name: str
    value: float
    unit: str
    threshold: Optional[float]
    passed: bool


@dataclass
class BenchmarkResult:
    """Result of performance benchmark testing"""
    test_name: str
    metrics: List[PerformanceMetric]
    overall_success: bool
    test_duration_seconds: float
    error_message: Optional[str]


@dataclass
class PerformanceProbeResult:
    """Result of performance benchmark probe"""
    probe_type: str
    benchmarks_performed: Dict[str, BenchmarkResult]
    total_benchmarks: int
    successful_benchmarks: int
    success_rate: float
    overall_duration_seconds: float


class PerformanceBenchmarkProbe:
    """Comprehensive performance benchmarking probe"""
    
    def __init__(self, base_url: str = "wss://observatory.nkllon.com"):
        self.base_url = base_url
        self.endpoints = [
            '/ws/emoji-rain',
            '/ws/observatory',
            '/ws/anomalies', 
            '/ws/doctor-status'
        ]
        
        # Performance thresholds
        self.thresholds = {
            'websocket_latency_ms': 100.0,
            'message_throughput_msg_sec': 100.0,
            'concurrent_connections': 10,
            'memory_usage_mb': 50.0,
            'cpu_usage_percent': 10.0,
            'connection_success_rate': 99.0
        }
        
    def log_action(self, action: str, status: str, results: Dict[str, Any] = None) -> None:
        """Log probe activity in JSON format to stdout"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "probe": "performance_benchmark",
            "action": action,
            "status": status
        }
        if results:
            log_entry["results"] = results
        print(json.dumps(log_entry))
    
    async def benchmark_websocket_performance(self) -> PerformanceProbeResult:
        """Comprehensive performance testing"""
        self.log_action("benchmark_websocket_performance", "in_progress", {
            "endpoints": self.endpoints,
            "thresholds": self.thresholds
        })
        
        start_time = time.time()
        results = {}
        
        # Performance test scenarios
        test_scenarios = [
            ("connection_latency", self._test_connection_latency),
            ("message_throughput", self._test_message_throughput),
            ("concurrent_connections", self._test_concurrent_connections),
            ("connection_stability", self._test_connection_stability),
            ("memory_usage", self._test_memory_usage),
            ("cpu_usage", self._test_cpu_usage)
        ]
        
        for test_name, test_func in test_scenarios:
            result = await test_func()
            results[test_name] = result
            
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Calculate success metrics
        successful_benchmarks = sum(1 for r in results.values() if r.overall_success)
        success_rate = (successful_benchmarks / len(test_scenarios)) * 100
        
        probe_result = PerformanceProbeResult(
            probe_type="performance_benchmark",
            benchmarks_performed=results,
            total_benchmarks=len(test_scenarios),
            successful_benchmarks=successful_benchmarks,
            success_rate=success_rate,
            overall_duration_seconds=total_duration
        )
        
        self.log_action("benchmark_websocket_performance", "completed", {
            "total_benchmarks": len(test_scenarios),
            "successful_benchmarks": successful_benchmarks,
            "success_rate": f"{success_rate:.1f}%",
            "duration_seconds": total_duration
        })
        
        return probe_result
    
    async def _test_connection_latency(self) -> BenchmarkResult:
        """Test WebSocket connection latency"""
        self.log_action("test_connection_latency", "in_progress")
        
        start_time = time.time()
        
        try:
            latencies = []
            total_tests = 20
            
            for _ in range(total_tests):
                for endpoint in self.endpoints:
                    url = f"{self.base_url}{endpoint}"
                    try:
                        connection_start = time.time()
                        async with websockets.connect(url, timeout=5) as websocket:
                            connection_end = time.time()
                            latency_ms = (connection_end - connection_start) * 1000
                            latencies.append(latency_ms)
                    except Exception:
                        pass
                    
            if latencies:
                avg_latency = sum(latencies) / len(latencies)
                max_latency = max(latencies)
                min_latency = min(latencies)
                
                metrics = [
                    PerformanceMetric(
                        "avg_latency_ms", avg_latency, "ms", 
                        self.thresholds['websocket_latency_ms'], 
                        avg_latency <= self.thresholds['websocket_latency_ms']
                    ),
                    PerformanceMetric(
                        "max_latency_ms", max_latency, "ms",
                        self.thresholds['websocket_latency_ms'],
                        max_latency <= self.thresholds['websocket_latency_ms']
                    ),
                    PerformanceMetric(
                        "min_latency_ms", min_latency, "ms", None, True
                    )
                ]
                
                overall_success = all(m.passed for m in metrics)
            else:
                metrics = []
                overall_success = False
                
            end_time = time.time()
            duration = end_time - start_time
            
            result = BenchmarkResult(
                test_name="connection_latency",
                metrics=metrics,
                overall_success=overall_success,
                test_duration_seconds=duration,
                error_message=None
            )
            
            self.log_action("test_connection_latency", "completed", {
                "overall_success": overall_success,
                "avg_latency_ms": avg_latency if latencies else None,
                "tests_performed": len(latencies)
            })
            
            return result
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            result = BenchmarkResult(
                test_name="connection_latency",
                metrics=[],
                overall_success=False,
                test_duration_seconds=duration,
                error_message=str(e)
            )
            
            self.log_action("test_connection_latency", "error", {
                "error": str(e)
            })
            
            return result
    
    async def _test_message_throughput(self) -> BenchmarkResult:
        """Test message throughput"""
        self.log_action("test_message_throughput", "in_progress")
        
        start_time = time.time()
        
        try:
            throughput_results = []
            
            for endpoint in self.endpoints:
                url = f"{self.base_url}{endpoint}"
                try:
                    async with websockets.connect(url, timeout=5) as websocket:
                        test_duration = 10  # seconds
                        messages_sent = 0
                        
                        test_start = time.time()
                        while time.time() - test_start < test_duration:
                            test_message = json.dumps({
                                "type": "throughput_test",
                                "timestamp": time.time(),
                                "message_id": messages_sent
                            })
                            
                            await websocket.send(test_message)
                            messages_sent += 1
                            
                            # Small delay to avoid overwhelming
                            await asyncio.sleep(0.01)
                        
                        actual_duration = time.time() - test_start
                        throughput = messages_sent / actual_duration
                        throughput_results.append(throughput)
                        
                except Exception:
                    pass
            
            if throughput_results:
                avg_throughput = sum(throughput_results) / len(throughput_results)
                max_throughput = max(throughput_results)
                
                metrics = [
                    PerformanceMetric(
                        "avg_throughput_msg_sec", avg_throughput, "msg/sec",
                        self.thresholds['message_throughput_msg_sec'],
                        avg_throughput >= self.thresholds['message_throughput_msg_sec']
                    ),
                    PerformanceMetric(
                        "max_throughput_msg_sec", max_throughput, "msg/sec", None, True
                    )
                ]
                
                overall_success = all(m.passed for m in metrics)
            else:
                metrics = []
                overall_success = False
                
            end_time = time.time()
            duration = end_time - start_time
            
            result = BenchmarkResult(
                test_name="message_throughput",
                metrics=metrics,
                overall_success=overall_success,
                test_duration_seconds=duration,
                error_message=None
            )
            
            self.log_action("test_message_throughput", "completed", {
                "overall_success": overall_success,
                "avg_throughput_msg_sec": avg_throughput if throughput_results else None,
                "endpoints_tested": len(throughput_results)
            })
            
            return result
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            result = BenchmarkResult(
                test_name="message_throughput",
                metrics=[],
                overall_success=False,
                test_duration_seconds=duration,
                error_message=str(e)
            )
            
            self.log_action("test_message_throughput", "error", {
                "error": str(e)
            })
            
            return result
    
    async def _test_concurrent_connections(self) -> BenchmarkResult:
        """Test concurrent connection support"""
        self.log_action("test_concurrent_connections", "in_progress")
        
        start_time = time.time()
        
        try:
            max_concurrent = 0
            connection_counts = [1, 5, 10, 15, 20]
            
            for concurrent_count in connection_counts:
                successful_connections = 0
                
                # Test each endpoint
                for endpoint in self.endpoints:
                    url = f"{self.base_url}{endpoint}"
                    try:
                        connections = []
                        for _ in range(concurrent_count):
                            connection = websockets.connect(url, timeout=5)
                            connections.append(connection)
                        
                        websockets_list = await asyncio.gather(*connections, return_exceptions=True)
                        
                        endpoint_successful = sum(1 for ws in websockets_list 
                                               if not isinstance(ws, Exception) and ws.open)
                        successful_connections += endpoint_successful
                        
                        # Close connections
                        for ws in websockets_list:
                            if not isinstance(ws, Exception):
                                await ws.close()
                                
                    except Exception:
                        pass
                
                if successful_connections >= concurrent_count * len(self.endpoints) * 0.8:
                    max_concurrent = concurrent_count
                else:
                    break
            
            metrics = [
                PerformanceMetric(
                    "max_concurrent_connections", max_concurrent, "connections",
                    self.thresholds['concurrent_connections'],
                    max_concurrent >= self.thresholds['concurrent_connections']
                )
            ]
            
            overall_success = all(m.passed for m in metrics)
            
            end_time = time.time()
            duration = end_time - start_time
            
            result = BenchmarkResult(
                test_name="concurrent_connections",
                metrics=metrics,
                overall_success=overall_success,
                test_duration_seconds=duration,
                error_message=None
            )
            
            self.log_action("test_concurrent_connections", "completed", {
                "overall_success": overall_success,
                "max_concurrent_connections": max_concurrent
            })
            
            return result
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            result = BenchmarkResult(
                test_name="concurrent_connections",
                metrics=[],
                overall_success=False,
                test_duration_seconds=duration,
                error_message=str(e)
            )
            
            self.log_action("test_concurrent_connections", "error", {
                "error": str(e)
            })
            
            return result
    
    async def _test_connection_stability(self) -> BenchmarkResult:
        """Test connection stability over time"""
        self.log_action("test_connection_stability", "in_progress")
        
        start_time = time.time()
        
        try:
            stability_results = []
            test_duration = 60  # 1 minute
            
            for endpoint in self.endpoints:
                url = f"{self.base_url}{endpoint}"
                try:
                    async with websockets.connect(url, timeout=5) as websocket:
                        stable_duration = 0
                        test_start = time.time()
                        
                        while time.time() - test_start < test_duration:
                            if websocket.open:
                                stable_duration += 1
                            else:
                                break
                            await asyncio.sleep(1)
                        
                        stability_percent = (stable_duration / test_duration) * 100
                        stability_results.append(stability_percent)
                        
                except Exception:
                    stability_results.append(0)
            
            if stability_results:
                avg_stability = sum(stability_results) / len(stability_results)
                min_stability = min(stability_results)
                
                metrics = [
                    PerformanceMetric(
                        "avg_stability_percent", avg_stability, "%",
                        self.thresholds['connection_success_rate'],
                        avg_stability >= self.thresholds['connection_success_rate']
                    ),
                    PerformanceMetric(
                        "min_stability_percent", min_stability, "%", None, True
                    )
                ]
                
                overall_success = all(m.passed for m in metrics)
            else:
                metrics = []
                overall_success = False
                
            end_time = time.time()
            duration = end_time - start_time
            
            result = BenchmarkResult(
                test_name="connection_stability",
                metrics=metrics,
                overall_success=overall_success,
                test_duration_seconds=duration,
                error_message=None
            )
            
            self.log_action("test_connection_stability", "completed", {
                "overall_success": overall_success,
                "avg_stability_percent": avg_stability if stability_results else None,
                "test_duration_seconds": test_duration
            })
            
            return result
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            result = BenchmarkResult(
                test_name="connection_stability",
                metrics=[],
                overall_success=False,
                test_duration_seconds=duration,
                error_message=str(e)
            )
            
            self.log_action("test_connection_stability", "error", {
                "error": str(e)
            })
            
            return result
    
    async def _test_memory_usage(self) -> BenchmarkResult:
        """Test memory usage during WebSocket operations"""
        self.log_action("test_memory_usage", "in_progress")
        
        start_time = time.time()
        
        try:
            # Get initial memory usage
            initial_memory = psutil.virtual_memory().used / (1024 * 1024)  # MB
            
            # Perform WebSocket operations
            connections = []
            for endpoint in self.endpoints:
                url = f"{self.base_url}{endpoint}"
                try:
                    connection = websockets.connect(url, timeout=5)
                    connections.append(connection)
                except Exception:
                    pass
            
            # Wait for connections to establish
            websockets_list = await asyncio.gather(*connections, return_exceptions=True)
            
            # Send some messages
            for ws in websockets_list:
                if not isinstance(ws, Exception):
                    for _ in range(10):
                        test_message = json.dumps({
                            "type": "memory_test",
                            "timestamp": time.time()
                        })
                        await ws.send(test_message)
                        await asyncio.sleep(0.1)
            
            # Measure memory usage
            peak_memory = psutil.virtual_memory().used / (1024 * 1024)  # MB
            memory_increase = peak_memory - initial_memory
            
            # Close connections
            for ws in websockets_list:
                if not isinstance(ws, Exception):
                    await ws.close()
            
            metrics = [
                PerformanceMetric(
                    "memory_increase_mb", memory_increase, "MB",
                    self.thresholds['memory_usage_mb'],
                    memory_increase <= self.thresholds['memory_usage_mb']
                ),
                PerformanceMetric(
                    "peak_memory_mb", peak_memory, "MB", None, True
                )
            ]
            
            overall_success = all(m.passed for m in metrics)
            
            end_time = time.time()
            duration = end_time - start_time
            
            result = BenchmarkResult(
                test_name="memory_usage",
                metrics=metrics,
                overall_success=overall_success,
                test_duration_seconds=duration,
                error_message=None
            )
            
            self.log_action("test_memory_usage", "completed", {
                "overall_success": overall_success,
                "memory_increase_mb": memory_increase,
                "peak_memory_mb": peak_memory
            })
            
            return result
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            result = BenchmarkResult(
                test_name="memory_usage",
                metrics=[],
                overall_success=False,
                test_duration_seconds=duration,
                error_message=str(e)
            )
            
            self.log_action("test_memory_usage", "error", {
                "error": str(e)
            })
            
            return result
    
    async def _test_cpu_usage(self) -> BenchmarkResult:
        """Test CPU usage during WebSocket operations"""
        self.log_action("test_cpu_usage", "in_progress")
        
        start_time = time.time()
        
        try:
            # Get initial CPU usage
            initial_cpu = psutil.cpu_percent(interval=1)
            
            # Perform intensive WebSocket operations
            connections = []
            for endpoint in self.endpoints:
                url = f"{self.base_url}{endpoint}"
                try:
                    connection = websockets.connect(url, timeout=5)
                    connections.append(connection)
                except Exception:
                    pass
            
            websockets_list = await asyncio.gather(*connections, return_exceptions=True)
            
            # Send many messages rapidly
            for ws in websockets_list:
                if not isinstance(ws, Exception):
                    for _ in range(100):
                        test_message = json.dumps({
                            "type": "cpu_test",
                            "timestamp": time.time(),
                            "data": "x" * 1000  # Larger message
                        })
                        await ws.send(test_message)
                        await asyncio.sleep(0.001)  # Very small delay
            
            # Measure peak CPU usage
            peak_cpu = psutil.cpu_percent(interval=1)
            
            # Close connections
            for ws in websockets_list:
                if not isinstance(ws, Exception):
                    await ws.close()
            
            metrics = [
                PerformanceMetric(
                    "peak_cpu_percent", peak_cpu, "%",
                    self.thresholds['cpu_usage_percent'],
                    peak_cpu <= self.thresholds['cpu_usage_percent']
                ),
                PerformanceMetric(
                    "initial_cpu_percent", initial_cpu, "%", None, True
                )
            ]
            
            overall_success = all(m.passed for m in metrics)
            
            end_time = time.time()
            duration = end_time - start_time
            
            result = BenchmarkResult(
                test_name="cpu_usage",
                metrics=metrics,
                overall_success=overall_success,
                test_duration_seconds=duration,
                error_message=None
            )
            
            self.log_action("test_cpu_usage", "completed", {
                "overall_success": overall_success,
                "peak_cpu_percent": peak_cpu,
                "initial_cpu_percent": initial_cpu
            })
            
            return result
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            result = BenchmarkResult(
                test_name="cpu_usage",
                metrics=[],
                overall_success=False,
                test_duration_seconds=duration,
                error_message=str(e)
            )
            
            self.log_action("test_cpu_usage", "error", {
                "error": str(e)
            })
            
            return result