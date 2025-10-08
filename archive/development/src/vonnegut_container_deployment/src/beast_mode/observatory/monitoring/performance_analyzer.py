"""
Performance Analyzer

Real-time performance analysis for WebSocket connections with metrics aggregation.
Calculates latency, throughput, and performance trends with minimal overhead.
"""

import asyncio
import time
from collections import deque, defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import json
from datetime import datetime, timedelta
import statistics


@dataclass
class MessageEvent:
    """Represents a message event for latency calculation"""
    timestamp: float
    message_id: Optional[str] = None
    size: int = 0


@dataclass
class PerformanceMetrics:
    """Performance metrics for an endpoint"""
    endpoint: str
    avg_latency_ms: float = 0.0
    min_latency_ms: float = 0.0
    max_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    throughput_msgs_per_sec: float = 0.0
    throughput_bytes_per_sec: float = 0.0
    error_rate: float = 0.0
    connection_uptime_sec: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)


class PerformanceAnalyzer:
    """
    Analyzes WebSocket performance metrics in real-time.
    
    Tracks latency, throughput, error rates, and performance trends
    with minimal computational overhead and accurate metrics.
    """

    def __init__(self, max_latency_samples: int = 1000, analysis_window_sec: int = 60):
        """
        Initialize the performance analyzer.
        
        Args:
            max_latency_samples: Maximum number of latency samples to keep
            analysis_window_sec: Time window for throughput analysis
        """
        self.max_latency_samples = max_latency_samples
        self.analysis_window_sec = analysis_window_sec
        
        # Per-endpoint tracking
        self._endpoint_metrics: Dict[str, PerformanceMetrics] = {}
        self._sent_messages: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_latency_samples))
        self._received_messages: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_latency_samples))
        self._message_pairs: Dict[str, List[Tuple[float, float]]] = defaultdict(list)
        
        # Throughput tracking
        self._throughput_windows: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=analysis_window_sec)
        )
        self._bytes_windows: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=analysis_window_sec)
        )
        
        # Error tracking
        self._error_counts: Dict[str, int] = defaultdict(int)
        self._total_messages: Dict[str, int] = defaultdict(int)
        
        # Connection start times
        self._connection_start_times: Dict[str, float] = {}

    async def record_message_sent(self, endpoint: str, timestamp: Optional[float] = None, 
                                 message_id: Optional[str] = None, size: int = 0) -> None:
        """
        Record a message sent event.
        
        Args:
            endpoint: The WebSocket endpoint
            timestamp: Message timestamp (defaults to current time)
            message_id: Optional message identifier for pairing
            size: Message size in bytes
        """
        if timestamp is None:
            timestamp = time.time()
        
        event = MessageEvent(timestamp=timestamp, message_id=message_id, size=size)
        self._sent_messages[endpoint].append(event)
        self._total_messages[endpoint] += 1
        
        # Update throughput window
        self._throughput_windows[endpoint].append(timestamp)
        self._bytes_windows[endpoint].append(size)
        
        self._log_action("message_sent_recorded", {
            "endpoint": endpoint,
            "timestamp": timestamp,
            "message_id": message_id,
            "size": size
        })

    async def record_message_received(self, endpoint: str, timestamp: Optional[float] = None,
                                    message_id: Optional[str] = None, size: int = 0) -> None:
        """
        Record a message received event.
        
        Args:
            endpoint: The WebSocket endpoint
            timestamp: Message timestamp (defaults to current time)
            message_id: Optional message identifier for pairing
            size: Message size in bytes
        """
        if timestamp is None:
            timestamp = time.time()
        
        event = MessageEvent(timestamp=timestamp, message_id=message_id, size=size)
        self._received_messages[endpoint].append(event)
        self._total_messages[endpoint] += 1
        
        # Update throughput window
        self._throughput_windows[endpoint].append(timestamp)
        self._bytes_windows[endpoint].append(size)
        
        self._log_action("message_received_recorded", {
            "endpoint": endpoint,
            "timestamp": timestamp,
            "message_id": message_id,
            "size": size
        })

    async def calculate_latency(self, endpoint: str, received_timestamp: float,
                              message_id: Optional[str] = None) -> Optional[float]:
        """
        Calculate latency for a received message.
        
        Args:
            endpoint: The WebSocket endpoint
            received_timestamp: Timestamp when message was received
            message_id: Optional message ID for exact pairing
            
        Returns:
            Latency in milliseconds, or None if no matching sent message
        """
        if endpoint not in self._sent_messages or not self._sent_messages[endpoint]:
            return None
        
        sent_messages = self._sent_messages[endpoint]
        
        # Try to find matching message by ID first
        if message_id:
            for sent_event in reversed(sent_messages):
                if sent_event.message_id == message_id:
                    latency_ms = (received_timestamp - sent_event.timestamp) * 1000
                    self._message_pairs[endpoint].append((sent_event.timestamp, received_timestamp))
                    return latency_ms
        
        # Fallback: use most recent sent message
        if sent_messages:
            most_recent_sent = sent_messages[-1]
            latency_ms = (received_timestamp - most_recent_sent.timestamp) * 1000
            
            # Only record if latency is reasonable (not negative or too large)
            if 0 <= latency_ms <= 30000:  # 0-30 seconds
                self._message_pairs[endpoint].append((most_recent_sent.timestamp, received_timestamp))
                return latency_ms
        
        return None

    async def get_endpoint_metrics(self, endpoint: str) -> PerformanceMetrics:
        """
        Get comprehensive performance metrics for an endpoint.
        
        Args:
            endpoint: The WebSocket endpoint
            
        Returns:
            PerformanceMetrics object with current metrics
        """
        current_time = time.time()
        
        # Calculate latency statistics
        latencies = await self._calculate_latency_stats(endpoint)
        
        # Calculate throughput
        throughput_msgs, throughput_bytes = await self._calculate_throughput(endpoint)
        
        # Calculate error rate
        error_rate = await self._calculate_error_rate(endpoint)
        
        # Calculate connection uptime
        uptime_sec = await self._calculate_uptime(endpoint, current_time)
        
        # Create or update metrics
        if endpoint not in self._endpoint_metrics:
            self._endpoint_metrics[endpoint] = PerformanceMetrics(endpoint=endpoint)
        
        metrics = self._endpoint_metrics[endpoint]
        metrics.avg_latency_ms = latencies.get('avg', 0.0)
        metrics.min_latency_ms = latencies.get('min', 0.0)
        metrics.max_latency_ms = latencies.get('max', 0.0)
        metrics.p95_latency_ms = latencies.get('p95', 0.0)
        metrics.p99_latency_ms = latencies.get('p99', 0.0)
        metrics.throughput_msgs_per_sec = throughput_msgs
        metrics.throughput_bytes_per_sec = throughput_bytes
        metrics.error_rate = error_rate
        metrics.connection_uptime_sec = uptime_sec
        metrics.last_updated = datetime.now()
        
        return metrics

    async def get_throughput(self, endpoint: str) -> float:
        """
        Get current throughput for an endpoint in messages per second.
        
        Args:
            endpoint: The WebSocket endpoint
            
        Returns:
            Throughput in messages per second
        """
        throughput_msgs, _ = await self._calculate_throughput(endpoint)
        return throughput_msgs

    async def record_error(self, endpoint: str, error_type: str = "unknown") -> None:
        """Record an error for an endpoint"""
        self._error_counts[endpoint] += 1
        
        self._log_action("error_recorded", {
            "endpoint": endpoint,
            "error_type": error_type,
            "error_count": self._error_counts[endpoint]
        })

    def set_connection_start_time(self, endpoint: str, start_time: Optional[float] = None) -> None:
        """Set the connection start time for uptime calculation"""
        if start_time is None:
            start_time = time.time()
        
        self._connection_start_times[endpoint] = start_time

    async def _calculate_latency_stats(self, endpoint: str) -> Dict[str, float]:
        """Calculate latency statistics for an endpoint"""
        if endpoint not in self._message_pairs or not self._message_pairs[endpoint]:
            return {'min': 0.0, 'max': 0.0, 'avg': 0.0, 'p95': 0.0, 'p99': 0.0}
        
        pairs = self._message_pairs[endpoint]
        
        # Calculate latencies
        latencies = []
        for sent_time, received_time in pairs:
            latency_ms = (received_time - sent_time) * 1000
            if 0 <= latency_ms <= 30000:  # Reasonable latency range
                latencies.append(latency_ms)
        
        if not latencies:
            return {'min': 0.0, 'max': 0.0, 'avg': 0.0, 'p95': 0.0, 'p99': 0.0}
        
        # Calculate statistics
        latencies.sort()
        count = len(latencies)
        
        return {
            'min': latencies[0],
            'max': latencies[-1],
            'avg': statistics.mean(latencies),
            'p95': latencies[int(count * 0.95)] if count > 0 else 0.0,
            'p99': latencies[int(count * 0.99)] if count > 0 else 0.0
        }

    async def _calculate_throughput(self, endpoint: str) -> Tuple[float, float]:
        """Calculate throughput for an endpoint"""
        current_time = time.time()
        window_start = current_time - self.analysis_window_sec
        
        # Count messages in window
        throughput_window = self._throughput_windows[endpoint]
        messages_in_window = sum(1 for timestamp in throughput_window if timestamp >= window_start)
        
        # Count bytes in window
        bytes_window = self._bytes_windows[endpoint]
        bytes_in_window = sum(bytes_window)
        
        # Calculate rates
        throughput_msgs_per_sec = messages_in_window / self.analysis_window_sec
        throughput_bytes_per_sec = bytes_in_window / self.analysis_window_sec
        
        return throughput_msgs_per_sec, throughput_bytes_per_sec

    async def _calculate_error_rate(self, endpoint: str) -> float:
        """Calculate error rate for an endpoint"""
        total_messages = self._total_messages[endpoint]
        error_count = self._error_counts[endpoint]
        
        if total_messages == 0:
            return 0.0
        
        return error_count / total_messages

    async def _calculate_uptime(self, endpoint: str, current_time: float) -> float:
        """Calculate connection uptime in seconds"""
        if endpoint not in self._connection_start_times:
            return 0.0
        
        start_time = self._connection_start_times[endpoint]
        return current_time - start_time

    def get_all_endpoint_metrics(self) -> Dict[str, PerformanceMetrics]:
        """Get metrics for all endpoints"""
        return self._endpoint_metrics.copy()

    def get_overall_performance_stats(self) -> Dict[str, Any]:
        """Get overall performance statistics across all endpoints"""
        if not self._endpoint_metrics:
            return {
                'total_endpoints': 0,
                'avg_latency_ms': 0.0,
                'total_throughput_msgs_per_sec': 0.0,
                'total_throughput_bytes_per_sec': 0.0,
                'overall_error_rate': 0.0
            }
        
        # Aggregate metrics across all endpoints
        total_latencies = []
        total_throughput_msgs = 0.0
        total_throughput_bytes = 0.0
        total_errors = 0
        total_messages = 0
        
        for metrics in self._endpoint_metrics.values():
            if metrics.avg_latency_ms > 0:
                total_latencies.append(metrics.avg_latency_ms)
            
            total_throughput_msgs += metrics.throughput_msgs_per_sec
            total_throughput_bytes += metrics.throughput_bytes_per_sec
        
        # Calculate overall error rate
        for endpoint in self._endpoint_metrics:
            total_errors += self._error_counts[endpoint]
            total_messages += self._total_messages[endpoint]
        
        overall_error_rate = total_errors / max(total_messages, 1)
        
        return {
            'total_endpoints': len(self._endpoint_metrics),
            'avg_latency_ms': statistics.mean(total_latencies) if total_latencies else 0.0,
            'total_throughput_msgs_per_sec': total_throughput_msgs,
            'total_throughput_bytes_per_sec': total_throughput_bytes,
            'overall_error_rate': overall_error_rate,
            'total_messages': total_messages,
            'total_errors': total_errors
        }

    def _log_action(self, action: str, details: Dict[str, Any]) -> None:
        """Log action in JSON format to stdout"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task": "3.1",
            "action": f"performance_analyzer_{action}",
            "status": "in_progress",
            "details": details
        }
        
        print(json.dumps(log_entry))