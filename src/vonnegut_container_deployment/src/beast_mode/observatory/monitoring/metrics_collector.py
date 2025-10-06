"""
Metrics Collector

High-performance metrics collection for WebSocket monitoring with minimal overhead.
Collects and aggregates various metrics for health monitoring and performance analysis.
"""

import asyncio
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
import json
from datetime import datetime, timedelta
import threading


@dataclass
class MetricValue:
    """Represents a metric value with timestamp"""
    value: Union[int, float]
    timestamp: float
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class CounterMetric:
    """Counter metric that only increases"""
    name: str
    value: int = 0
    labels: Dict[str, str] = field(default_factory=dict)
    last_updated: float = field(default_factory=time.time)


@dataclass
class GaugeMetric:
    """Gauge metric that can increase or decrease"""
    name: str
    value: Union[int, float] = 0.0
    labels: Dict[str, str] = field(default_factory=dict)
    last_updated: float = field(default_factory=time.time)


@dataclass
class HistogramMetric:
    """Histogram metric for distribution analysis"""
    name: str
    values: deque = field(default_factory=lambda: deque(maxlen=1000))
    labels: Dict[str, str] = field(default_factory=dict)
    last_updated: float = field(default_factory=time.time)


class MetricsCollector:
    """
    High-performance metrics collector for WebSocket monitoring.
    
    Collects counters, gauges, and histograms with minimal overhead
    and provides aggregation capabilities for health monitoring.
    """

    def __init__(self, max_histogram_samples: int = 1000):
        """
        Initialize the metrics collector.
        
        Args:
            max_histogram_samples: Maximum samples to keep in histograms
        """
        self.max_histogram_samples = max_histogram_samples
        
        # Metric storage
        self._counters: Dict[str, CounterMetric] = {}
        self._gauges: Dict[str, GaugeMetric] = {}
        self._histograms: Dict[str, HistogramMetric] = {}
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Collection metadata
        self._collection_start_time = time.time()
        self._total_metrics_collected = 0

    async def increment_counter(self, name: str, value: int = 1, 
                              labels: Optional[Dict[str, str]] = None) -> None:
        """
        Increment a counter metric.
        
        Args:
            name: Metric name
            value: Value to increment by (default: 1)
            labels: Optional labels for the metric
        """
        labels = labels or {}
        label_key = self._create_label_key(labels)
        full_name = f"{name}{label_key}"
        
        with self._lock:
            if full_name not in self._counters:
                self._counters[full_name] = CounterMetric(
                    name=name, labels=labels
                )
            
            self._counters[full_name].value += value
            self._counters[full_name].last_updated = time.time()
            self._total_metrics_collected += 1
        
        self._log_action("counter_incremented", {
            "name": name,
            "value": value,
            "labels": labels,
            "new_total": self._counters[full_name].value
        })

    async def set_gauge(self, name: str, value: Union[int, float],
                       labels: Optional[Dict[str, str]] = None) -> None:
        """
        Set a gauge metric value.
        
        Args:
            name: Metric name
            value: Value to set
            labels: Optional labels for the metric
        """
        labels = labels or {}
        label_key = self._create_label_key(labels)
        full_name = f"{name}{label_key}"
        
        with self._lock:
            if full_name not in self._gauges:
                self._gauges[full_name] = GaugeMetric(
                    name=name, labels=labels
                )
            
            self._gauges[full_name].value = value
            self._gauges[full_name].last_updated = time.time()
            self._total_metrics_collected += 1
        
        self._log_action("gauge_set", {
            "name": name,
            "value": value,
            "labels": labels
        })

    async def observe_histogram(self, name: str, value: Union[int, float],
                               labels: Optional[Dict[str, str]] = None) -> None:
        """
        Observe a value in a histogram metric.
        
        Args:
            name: Metric name
            value: Value to observe
            labels: Optional labels for the metric
        """
        labels = labels or {}
        label_key = self._create_label_key(labels)
        full_name = f"{name}{label_key}"
        
        with self._lock:
            if full_name not in self._histograms:
                self._histograms[full_name] = HistogramMetric(
                    name=name, labels=labels
                )
            
            self._histograms[full_name].values.append(value)
            self._histograms[full_name].last_updated = time.time()
            self._total_metrics_collected += 1
        
        self._log_action("histogram_observed", {
            "name": name,
            "value": value,
            "labels": labels,
            "sample_count": len(self._histograms[full_name].values)
        })

    def get_counter(self, name: str, labels: Optional[Dict[str, str]] = None) -> int:
        """Get counter value"""
        labels = labels or {}
        label_key = self._create_label_key(labels)
        full_name = f"{name}{label_key}"
        
        with self._lock:
            return self._counters.get(full_name, CounterMetric(name=name)).value

    def get_gauge(self, name: str, labels: Optional[Dict[str, str]] = None) -> Union[int, float]:
        """Get gauge value"""
        labels = labels or {}
        label_key = self._create_label_key(labels)
        full_name = f"{name}{label_key}"
        
        with self._lock:
            return self._gauges.get(full_name, GaugeMetric(name=name)).value

    def get_histogram_stats(self, name: str, labels: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """Get histogram statistics"""
        labels = labels or {}
        label_key = self._create_label_key(labels)
        full_name = f"{name}{label_key}"
        
        with self._lock:
            histogram = self._histograms.get(full_name)
            if not histogram or not histogram.values:
                return {
                    'count': 0, 'min': 0.0, 'max': 0.0, 'avg': 0.0,
                    'p50': 0.0, 'p95': 0.0, 'p99': 0.0
                }
            
            values = list(histogram.values)
            values.sort()
            count = len(values)
            
            return {
                'count': count,
                'min': values[0],
                'max': values[-1],
                'avg': sum(values) / count,
                'p50': values[int(count * 0.5)] if count > 0 else 0.0,
                'p95': values[int(count * 0.95)] if count > 0 else 0.0,
                'p99': values[int(count * 0.99)] if count > 0 else 0.0
            }

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics"""
        with self._lock:
            metrics = {
                'counters': {},
                'gauges': {},
                'histograms': {},
                'metadata': {
                    'collection_start_time': self._collection_start_time,
                    'total_metrics_collected': self._total_metrics_collected,
                    'uptime_sec': time.time() - self._collection_start_time
                }
            }
            
            # Collect counters
            for name, counter in self._counters.items():
                metrics['counters'][name] = {
                    'value': counter.value,
                    'labels': counter.labels,
                    'last_updated': counter.last_updated
                }
            
            # Collect gauges
            for name, gauge in self._gauges.items():
                metrics['gauges'][name] = {
                    'value': gauge.value,
                    'labels': gauge.labels,
                    'last_updated': gauge.last_updated
                }
            
            # Collect histogram stats
            for name, histogram in self._histograms.items():
                metrics['histograms'][name] = {
                    'stats': self.get_histogram_stats(histogram.name, histogram.labels),
                    'labels': histogram.labels,
                    'last_updated': histogram.last_updated
                }
            
            return metrics

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics"""
        with self._lock:
            return {
                'total_counters': len(self._counters),
                'total_gauges': len(self._gauges),
                'total_histograms': len(self._histograms),
                'total_metrics_collected': self._total_metrics_collected,
                'uptime_sec': time.time() - self._collection_start_time,
                'collection_rate_per_sec': self._total_metrics_collected / max(
                    time.time() - self._collection_start_time, 1
                )
            }

    def clear_metrics(self, metric_type: Optional[str] = None) -> None:
        """
        Clear metrics.
        
        Args:
            metric_type: Type to clear ('counters', 'gauges', 'histograms', or None for all)
        """
        with self._lock:
            if metric_type is None or metric_type == 'counters':
                self._counters.clear()
            
            if metric_type is None or metric_type == 'gauges':
                self._gauges.clear()
            
            if metric_type is None or metric_type == 'histograms':
                self._histograms.clear()
            
            self._total_metrics_collected = 0
        
        self._log_action("metrics_cleared", {
            "metric_type": metric_type or "all"
        })

    def export_metrics(self, format_type: str = "json") -> str:
        """
        Export metrics in specified format.
        
        Args:
            format_type: Export format ('json', 'prometheus')
            
        Returns:
            Exported metrics as string
        """
        if format_type == "json":
            return json.dumps(self.get_all_metrics(), indent=2)
        elif format_type == "prometheus":
            return self._export_prometheus_format()
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def _create_label_key(self, labels: Dict[str, str]) -> str:
        """Create a key from labels for metric identification"""
        if not labels:
            return ""
        
        sorted_labels = sorted(labels.items())
        return "{" + ",".join(f"{k}={v}" for k, v in sorted_labels) + "}"

    def _export_prometheus_format(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []
        
        with self._lock:
            # Export counters
            for name, counter in self._counters.items():
                label_str = ""
                if counter.labels:
                    label_str = "{" + ",".join(f'{k}="{v}"' for k, v in counter.labels.items()) + "}"
                
                lines.append(f"# TYPE {counter.name} counter")
                lines.append(f"{counter.name}{label_str} {counter.value}")
            
            # Export gauges
            for name, gauge in self._gauges.items():
                label_str = ""
                if gauge.labels:
                    label_str = "{" + ",".join(f'{k}="{v}"' for k, v in gauge.labels.items()) + "}"
                
                lines.append(f"# TYPE {gauge.name} gauge")
                lines.append(f"{gauge.name}{label_str} {gauge.value}")
            
            # Export histograms
            for name, histogram in self._histograms.items():
                stats = self.get_histogram_stats(histogram.name, histogram.labels)
                label_str = ""
                if histogram.labels:
                    label_str = "{" + ",".join(f'{k}="{v}"' for k, v in histogram.labels.items()) + "}"
                
                lines.append(f"# TYPE {histogram.name} histogram")
                lines.append(f"{histogram.name}_count{label_str} {stats['count']}")
                lines.append(f"{histogram.name}_sum{label_str} {stats['avg'] * stats['count']}")
                lines.append(f"{histogram.name}_bucket{{le=\"+Inf\"}}{label_str} {stats['count']}")
        
        return "\n".join(lines)

    def _log_action(self, action: str, details: Dict[str, Any]) -> None:
        """Log action in JSON format to stdout"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task": "3.1",
            "action": f"metrics_collector_{action}",
            "status": "in_progress",
            "details": details
        }
        
        print(json.dumps(log_entry))