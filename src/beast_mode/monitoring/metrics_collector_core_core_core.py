"""
Metrics Collector Core Core Core

This module was extracted from metrics_collector_core_core.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json

class MetricType(str, Enum):
    """Types of metrics that can be collected."""
    COUNTER = 'counter'
    GAUGE = 'gauge'
    HISTOGRAM = 'histogram'
    TIMER = 'timer'

@dataclass
class Metric:
    """A single metric measurement."""
    name: str
    type: MetricType
    value: Union[int, float]
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    unit: str = ''

@dataclass
class MetricSummary:
    """Summary statistics for a metric."""
    name: str
    type: MetricType
    count: int
    min_value: float
    max_value: float
    avg_value: float
    sum_value: float
    percentiles: Dict[str, float] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)

class MetricsCollector:
    """
    Comprehensive metrics collection system for Beast Mode components.
    
    Collects performance metrics, aggregates them, and provides reporting
    capabilities for monitoring system performance and identifying bottlenecks.
    """

    def __init__(self, retention_hours: int=24, max_metrics_per_type: int=10000):
        self.retention_hours = retention_hours
        self.max_metrics_per_type = max_metrics_per_type
        self.logger = logging.getLogger(__name__)
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_metrics_per_type))
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        self.cleanup_task: Optional[asyncio.Task] = None
        self.collecting = False

    async def start_collection(self) -> None:
        """Start metrics collection and cleanup."""
        if self.collecting:
            self.logger.warning('Metrics collection already active')
            return
        self.collecting = True
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        await self._initialize_default_metrics()
        self.logger.info('Metrics collection started')

    async def stop_collection(self) -> None:
        """Stop metrics collection."""
        self.collecting = False
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        self.logger.info('Metrics collection stopped')

    def increment_counter(self, name: str, value: float=1.0, labels: Optional[Dict[str, str]]=None) -> None:
        """Increment a counter metric."""
        labels = labels or {}
        metric_key = self._create_metric_key(name, labels)
        self.counters[metric_key] += value
        metric = Metric(name=name, type=MetricType.COUNTER, value=value, timestamp=datetime.now(), labels=labels)
        self.metrics[metric_key].append(metric)

    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]]=None) -> None:
        """Set a gauge metric value."""
        labels = labels or {}
        metric_key = self._create_metric_key(name, labels)
        self.gauges[metric_key] = value
        metric = Metric(name=name, type=MetricType.GAUGE, value=value, timestamp=datetime.now(), labels=labels)
        self.metrics[metric_key].append(metric)

    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]]=None) -> None:
        """Record a value in a histogram metric."""
        labels = labels or {}
        metric_key = self._create_metric_key(name, labels)
        self.histograms[metric_key].append(value)
        if len(self.histograms[metric_key]) > 1000:
            self.histograms[metric_key] = self.histograms[metric_key][-1000:]
        metric = Metric(name=name, type=MetricType.HISTOGRAM, value=value, timestamp=datetime.now(), labels=labels)
        self.metrics[metric_key].append(metric)

    def record_timer(self, name: str, duration_ms: float, labels: Optional[Dict[str, str]]=None) -> None:
        """Record a timer metric (duration in milliseconds)."""
        labels = labels or {}
        metric_key = self._create_metric_key(name, labels)
        self.timers[metric_key].append(duration_ms)
        if len(self.timers[metric_key]) > 1000:
            self.timers[metric_key] = self.timers[metric_key][-1000:]
        metric = Metric(name=name, type=MetricType.TIMER, value=duration_ms, timestamp=datetime.now(), labels=labels, unit='ms')
        self.metrics[metric_key].append(metric)

    def get_counter_value(self, name: str, labels: Optional[Dict[str, str]]=None) -> float:
        """Get current counter value."""
        metric_key = self._create_metric_key(name, labels or {})
        return self.counters.get(metric_key, 0.0)

    def get_gauge_value(self, name: str, labels: Optional[Dict[str, str]]=None) -> Optional[float]:
        """Get current gauge value."""
        metric_key = self._create_metric_key(name, labels or {})
        return self.gauges.get(metric_key)

    def get_histogram_summary(self, name: str, labels: Optional[Dict[str, str]]=None) -> Optional[MetricSummary]:
        """Get histogram summary statistics."""
        metric_key = self._create_metric_key(name, labels or {})
        values = self.histograms.get(metric_key, [])
        if not values:
            return None
        return self._calculate_summary(name, MetricType.HISTOGRAM, values, labels or {})

    def get_timer_summary(self, name: str, labels: Optional[Dict[str, str]]=None) -> Optional[MetricSummary]:
        """Get timer summary statistics."""
        metric_key = self._create_metric_key(name, labels or {})
        values = self.timers.get(metric_key, [])
        if not values:
            return None
        return self._calculate_summary(name, MetricType.TIMER, values, labels or {})

    def get_all_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all collected metrics."""
        summary = {'counters': {}, 'gauges': {}, 'histograms': {}, 'timers': {}, 'collection_time': datetime.now().isoformat()}
        for metric_key, value in self.counters.items():
            name, labels = self._parse_metric_key(metric_key)
            summary['counters'][metric_key] = {'name': name, 'value': value, 'labels': labels}
        for metric_key, value in self.gauges.items():
            name, labels = self._parse_metric_key(metric_key)
            summary['gauges'][metric_key] = {'name': name, 'value': value, 'labels': labels}
        for metric_key, values in self.histograms.items():
            if values:
                name, labels = self._parse_metric_key(metric_key)
                summary_stats = self._calculate_summary(name, MetricType.HISTOGRAM, values, labels)
                summary['histograms'][metric_key] = summary_stats.__dict__
        for metric_key, values in self.timers.items():
            if values:
                name, labels = self._parse_metric_key(metric_key)
                summary_stats = self._calculate_summary(name, MetricType.TIMER, values, labels)
                summary['timers'][metric_key] = summary_stats.__dict__
        return summary

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate a comprehensive performance report."""
        summary = self.get_all_metrics_summary()
        report = {'timestamp': datetime.now().isoformat(), 'summary': summary, 'kpis': {}}
        messages_sent = self.get_counter_value('messages_sent')
        messages_received = self.get_counter_value('messages_received')
        if messages_sent > 0 or messages_received > 0:
            report['kpis']['message_throughput'] = {'messages_sent': messages_sent, 'messages_received': messages_received, 'total_messages': messages_sent + messages_received}
        latency_summary = self.get_timer_summary('message_latency')
        if latency_summary:
            report['kpis']['message_latency'] = {'avg_ms': latency_summary.avg_value, 'p95_ms': latency_summary.percentiles.get('p95', 0), 'p99_ms': latency_summary.percentiles.get('p99', 0)}
        errors = self.get_counter_value('errors')
        total_operations = self.get_counter_value('operations')
        if total_operations > 0:
            error_rate = errors / total_operations * 100
            report['kpis']['error_rate'] = {'errors': errors, 'total_operations': total_operations, 'error_rate_percent': round(error_rate, 2)}
        active_connections = self.get_gauge_value('active_connections')
        if active_connections is not None:
            report['kpis']['connections'] = {'active_connections': active_connections}
        return report

    async def _initialize_default_metrics(self) -> None:
        """Initialize default metrics for Beast Mode components."""
        self.increment_counter('messages_sent', 0)
        self.increment_counter('messages_received', 0)
        self.increment_counter('errors', 0)
        self.increment_counter('operations', 0)
        self.set_gauge('active_connections', 0)
        self.set_gauge('active_agents', 0)
        self.logger.info('Default metrics initialized')

    async def _cleanup_loop(self) -> None:
        """Periodic cleanup of old metrics."""
        while self.collecting:
            try:
                await self._cleanup_old_metrics()
                await asyncio.sleep(3600)
            except Exception as e:
                self.logger.error(f'Error in metrics cleanup: {e}')
                await asyncio.sleep(300)

    async def _cleanup_old_metrics(self) -> None:
        """Remove metrics older than retention period."""
        cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
        for metric_key, metric_deque in self.metrics.items():
            while metric_deque and metric_deque[0].timestamp < cutoff_time:
                metric_deque.popleft()
        for histogram_values in self.histograms.values():
            if len(histogram_values) > 1000:
                histogram_values[:] = histogram_values[-1000:]
        for timer_values in self.timers.values():
            if len(timer_values) > 1000:
                timer_values[:] = timer_values[-1000:]
        self.logger.debug('Metrics cleanup completed')

    def _create_metric_key(self, name: str, labels: Dict[str, str]) -> str:
        """Create a unique key for a metric with labels."""
        if not labels:
            return name
        sorted_labels = sorted(labels.items())
        label_str = ','.join((f'{k}={v}' for k, v in sorted_labels))
        return f'{name}{{{label_str}}}'

    def _parse_metric_key(self, metric_key: str) -> tuple[str, Dict[str, str]]:
        """Parse a metric key back into name and labels."""
        if '{' not in metric_key:
            return (metric_key, {})
        name, label_part = metric_key.split('{', 1)
        label_part = label_part.rstrip('}')
        labels = {}
        if label_part:
            for label_pair in label_part.split(','):
                key, value = label_pair.split('=', 1)
                labels[key] = value
        return (name, labels)

    def _calculate_summary(self, name: str, metric_type: MetricType, values: List[float], labels: Dict[str, str]) -> MetricSummary:
        """Calculate summary statistics for a list of values."""
        if not values:
            return MetricSummary(name=name, type=metric_type, count=0, min_value=0, max_value=0, avg_value=0, sum_value=0, labels=labels)
        sorted_values = sorted(values)
        count = len(sorted_values)
        percentiles = {}
        for p in [50, 90, 95, 99]:
            index = int(p / 100 * count)
            if index >= count:
                index = count - 1
            percentiles[f'p{p}'] = sorted_values[index]
        return MetricSummary(name=name, type=metric_type, count=count, min_value=min(values), max_value=max(values), avg_value=sum(values) / count, sum_value=sum(values), percentiles=percentiles, labels=labels)

def __init__(self, retention_hours: int=24, max_metrics_per_type: int=10000):
    self.retention_hours = retention_hours
    self.max_metrics_per_type = max_metrics_per_type
    self.logger = logging.getLogger(__name__)
    self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_metrics_per_type))
    self.counters: Dict[str, float] = defaultdict(float)
    self.gauges: Dict[str, float] = {}
    self.histograms: Dict[str, List[float]] = defaultdict(list)
    self.timers: Dict[str, List[float]] = defaultdict(list)
    self.cleanup_task: Optional[asyncio.Task] = None
    self.collecting = False

def increment_counter(self, name: str, value: float=1.0, labels: Optional[Dict[str, str]]=None) -> None:
    """Increment a counter metric."""
    labels = labels or {}
    metric_key = self._create_metric_key(name, labels)
    self.counters[metric_key] += value
    metric = Metric(name=name, type=MetricType.COUNTER, value=value, timestamp=datetime.now(), labels=labels)
    self.metrics[metric_key].append(metric)

def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]]=None) -> None:
    """Set a gauge metric value."""
    labels = labels or {}
    metric_key = self._create_metric_key(name, labels)
    self.gauges[metric_key] = value
    metric = Metric(name=name, type=MetricType.GAUGE, value=value, timestamp=datetime.now(), labels=labels)
    self.metrics[metric_key].append(metric)

def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]]=None) -> None:
    """Record a value in a histogram metric."""
    labels = labels or {}
    metric_key = self._create_metric_key(name, labels)
    self.histograms[metric_key].append(value)
    if len(self.histograms[metric_key]) > 1000:
        self.histograms[metric_key] = self.histograms[metric_key][-1000:]
    metric = Metric(name=name, type=MetricType.HISTOGRAM, value=value, timestamp=datetime.now(), labels=labels)
    self.metrics[metric_key].append(metric)

def record_timer(self, name: str, duration_ms: float, labels: Optional[Dict[str, str]]=None) -> None:
    """Record a timer metric (duration in milliseconds)."""
    labels = labels or {}
    metric_key = self._create_metric_key(name, labels)
    self.timers[metric_key].append(duration_ms)
    if len(self.timers[metric_key]) > 1000:
        self.timers[metric_key] = self.timers[metric_key][-1000:]
    metric = Metric(name=name, type=MetricType.TIMER, value=duration_ms, timestamp=datetime.now(), labels=labels, unit='ms')
    self.metrics[metric_key].append(metric)

def get_counter_value(self, name: str, labels: Optional[Dict[str, str]]=None) -> float:
    """Get current counter value."""
    metric_key = self._create_metric_key(name, labels or {})
    return self.counters.get(metric_key, 0.0)

def get_gauge_value(self, name: str, labels: Optional[Dict[str, str]]=None) -> Optional[float]:
    """Get current gauge value."""
    metric_key = self._create_metric_key(name, labels or {})
    return self.gauges.get(metric_key)

def get_histogram_summary(self, name: str, labels: Optional[Dict[str, str]]=None) -> Optional[MetricSummary]:
    """Get histogram summary statistics."""
    metric_key = self._create_metric_key(name, labels or {})
    values = self.histograms.get(metric_key, [])
    if not values:
        return None
    return self._calculate_summary(name, MetricType.HISTOGRAM, values, labels or {})

def get_timer_summary(self, name: str, labels: Optional[Dict[str, str]]=None) -> Optional[MetricSummary]:
    """Get timer summary statistics."""
    metric_key = self._create_metric_key(name, labels or {})
    values = self.timers.get(metric_key, [])
    if not values:
        return None
    return self._calculate_summary(name, MetricType.TIMER, values, labels or {})

def get_all_metrics_summary(self) -> Dict[str, Any]:
    """Get summary of all collected metrics."""
    summary = {'counters': {}, 'gauges': {}, 'histograms': {}, 'timers': {}, 'collection_time': datetime.now().isoformat()}
    for metric_key, value in self.counters.items():
        name, labels = self._parse_metric_key(metric_key)
        summary['counters'][metric_key] = {'name': name, 'value': value, 'labels': labels}
    for metric_key, value in self.gauges.items():
        name, labels = self._parse_metric_key(metric_key)
        summary['gauges'][metric_key] = {'name': name, 'value': value, 'labels': labels}
    for metric_key, values in self.histograms.items():
        if values:
            name, labels = self._parse_metric_key(metric_key)
            summary_stats = self._calculate_summary(name, MetricType.HISTOGRAM, values, labels)
            summary['histograms'][metric_key] = summary_stats.__dict__
    for metric_key, values in self.timers.items():
        if values:
            name, labels = self._parse_metric_key(metric_key)
            summary_stats = self._calculate_summary(name, MetricType.TIMER, values, labels)
            summary['timers'][metric_key] = summary_stats.__dict__
    return summary

def get_performance_report(self) -> Dict[str, Any]:
    """Generate a comprehensive performance report."""
    summary = self.get_all_metrics_summary()
    report = {'timestamp': datetime.now().isoformat(), 'summary': summary, 'kpis': {}}
    messages_sent = self.get_counter_value('messages_sent')
    messages_received = self.get_counter_value('messages_received')
    if messages_sent > 0 or messages_received > 0:
        report['kpis']['message_throughput'] = {'messages_sent': messages_sent, 'messages_received': messages_received, 'total_messages': messages_sent + messages_received}
    latency_summary = self.get_timer_summary('message_latency')
    if latency_summary:
        report['kpis']['message_latency'] = {'avg_ms': latency_summary.avg_value, 'p95_ms': latency_summary.percentiles.get('p95', 0), 'p99_ms': latency_summary.percentiles.get('p99', 0)}
    errors = self.get_counter_value('errors')
    total_operations = self.get_counter_value('operations')
    if total_operations > 0:
        error_rate = errors / total_operations * 100
        report['kpis']['error_rate'] = {'errors': errors, 'total_operations': total_operations, 'error_rate_percent': round(error_rate, 2)}
    active_connections = self.get_gauge_value('active_connections')
    if active_connections is not None:
        report['kpis']['connections'] = {'active_connections': active_connections}
    return report

def _create_metric_key(self, name: str, labels: Dict[str, str]) -> str:
    """Create a unique key for a metric with labels."""
    if not labels:
        return name
    sorted_labels = sorted(labels.items())
    label_str = ','.join((f'{k}={v}' for k, v in sorted_labels))
    return f'{name}{{{label_str}}}'

def _calculate_summary(self, name: str, metric_type: MetricType, values: List[float], labels: Dict[str, str]) -> MetricSummary:
    """Calculate summary statistics for a list of values."""
    if not values:
        return MetricSummary(name=name, type=metric_type, count=0, min_value=0, max_value=0, avg_value=0, sum_value=0, labels=labels)
    sorted_values = sorted(values)
    count = len(sorted_values)
    percentiles = {}
    for p in [50, 90, 95, 99]:
        index = int(p / 100 * count)
        if index >= count:
            index = count - 1
        percentiles[f'p{p}'] = sorted_values[index]
    return MetricSummary(name=name, type=metric_type, count=count, min_value=min(values), max_value=max(values), avg_value=sum(values) / count, sum_value=sum(values), percentiles=percentiles, labels=labels)

def __init__(self, retention_hours: int=24, max_metrics_per_type: int=10000):
    self.retention_hours = retention_hours
    self.max_metrics_per_type = max_metrics_per_type
    self.logger = logging.getLogger(__name__)
    self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_metrics_per_type))
    self.counters: Dict[str, float] = defaultdict(float)
    self.gauges: Dict[str, float] = {}
    self.histograms: Dict[str, List[float]] = defaultdict(list)
    self.timers: Dict[str, List[float]] = defaultdict(list)
    self.cleanup_task: Optional[asyncio.Task] = None
    self.collecting = False

def increment_counter(self, name: str, value: float=1.0, labels: Optional[Dict[str, str]]=None) -> None:
    """Increment a counter metric."""
    labels = labels or {}
    metric_key = self._create_metric_key(name, labels)
    self.counters[metric_key] += value
    metric = Metric(name=name, type=MetricType.COUNTER, value=value, timestamp=datetime.now(), labels=labels)
    self.metrics[metric_key].append(metric)

def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]]=None) -> None:
    """Set a gauge metric value."""
    labels = labels or {}
    metric_key = self._create_metric_key(name, labels)
    self.gauges[metric_key] = value
    metric = Metric(name=name, type=MetricType.GAUGE, value=value, timestamp=datetime.now(), labels=labels)
    self.metrics[metric_key].append(metric)

def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]]=None) -> None:
    """Record a value in a histogram metric."""
    labels = labels or {}
    metric_key = self._create_metric_key(name, labels)
    self.histograms[metric_key].append(value)
    if len(self.histograms[metric_key]) > 1000:
        self.histograms[metric_key] = self.histograms[metric_key][-1000:]
    metric = Metric(name=name, type=MetricType.HISTOGRAM, value=value, timestamp=datetime.now(), labels=labels)
    self.metrics[metric_key].append(metric)

def record_timer(self, name: str, duration_ms: float, labels: Optional[Dict[str, str]]=None) -> None:
    """Record a timer metric (duration in milliseconds)."""
    labels = labels or {}
    metric_key = self._create_metric_key(name, labels)
    self.timers[metric_key].append(duration_ms)
    if len(self.timers[metric_key]) > 1000:
        self.timers[metric_key] = self.timers[metric_key][-1000:]
    metric = Metric(name=name, type=MetricType.TIMER, value=duration_ms, timestamp=datetime.now(), labels=labels, unit='ms')
    self.metrics[metric_key].append(metric)

def get_counter_value(self, name: str, labels: Optional[Dict[str, str]]=None) -> float:
    """Get current counter value."""
    metric_key = self._create_metric_key(name, labels or {})
    return self.counters.get(metric_key, 0.0)

def get_gauge_value(self, name: str, labels: Optional[Dict[str, str]]=None) -> Optional[float]:
    """Get current gauge value."""
    metric_key = self._create_metric_key(name, labels or {})
    return self.gauges.get(metric_key)

def get_histogram_summary(self, name: str, labels: Optional[Dict[str, str]]=None) -> Optional[MetricSummary]:
    """Get histogram summary statistics."""
    metric_key = self._create_metric_key(name, labels or {})
    values = self.histograms.get(metric_key, [])
    if not values:
        return None
    return self._calculate_summary(name, MetricType.HISTOGRAM, values, labels or {})

def get_timer_summary(self, name: str, labels: Optional[Dict[str, str]]=None) -> Optional[MetricSummary]:
    """Get timer summary statistics."""
    metric_key = self._create_metric_key(name, labels or {})
    values = self.timers.get(metric_key, [])
    if not values:
        return None
    return self._calculate_summary(name, MetricType.TIMER, values, labels or {})

def get_all_metrics_summary(self) -> Dict[str, Any]:
    """Get summary of all collected metrics."""
    summary = {'counters': {}, 'gauges': {}, 'histograms': {}, 'timers': {}, 'collection_time': datetime.now().isoformat()}
    for metric_key, value in self.counters.items():
        name, labels = self._parse_metric_key(metric_key)
        summary['counters'][metric_key] = {'name': name, 'value': value, 'labels': labels}
    for metric_key, value in self.gauges.items():
        name, labels = self._parse_metric_key(metric_key)
        summary['gauges'][metric_key] = {'name': name, 'value': value, 'labels': labels}
    for metric_key, values in self.histograms.items():
        if values:
            name, labels = self._parse_metric_key(metric_key)
            summary_stats = self._calculate_summary(name, MetricType.HISTOGRAM, values, labels)
            summary['histograms'][metric_key] = summary_stats.__dict__
    for metric_key, values in self.timers.items():
        if values:
            name, labels = self._parse_metric_key(metric_key)
            summary_stats = self._calculate_summary(name, MetricType.TIMER, values, labels)
            summary['timers'][metric_key] = summary_stats.__dict__
    return summary

def get_performance_report(self) -> Dict[str, Any]:
    """Generate a comprehensive performance report."""
    summary = self.get_all_metrics_summary()
    report = {'timestamp': datetime.now().isoformat(), 'summary': summary, 'kpis': {}}
    messages_sent = self.get_counter_value('messages_sent')
    messages_received = self.get_counter_value('messages_received')
    if messages_sent > 0 or messages_received > 0:
        report['kpis']['message_throughput'] = {'messages_sent': messages_sent, 'messages_received': messages_received, 'total_messages': messages_sent + messages_received}
    latency_summary = self.get_timer_summary('message_latency')
    if latency_summary:
        report['kpis']['message_latency'] = {'avg_ms': latency_summary.avg_value, 'p95_ms': latency_summary.percentiles.get('p95', 0), 'p99_ms': latency_summary.percentiles.get('p99', 0)}
    errors = self.get_counter_value('errors')
    total_operations = self.get_counter_value('operations')
    if total_operations > 0:
        error_rate = errors / total_operations * 100
        report['kpis']['error_rate'] = {'errors': errors, 'total_operations': total_operations, 'error_rate_percent': round(error_rate, 2)}
    active_connections = self.get_gauge_value('active_connections')
    if active_connections is not None:
        report['kpis']['connections'] = {'active_connections': active_connections}
    return report

def _create_metric_key(self, name: str, labels: Dict[str, str]) -> str:
    """Create a unique key for a metric with labels."""
    if not labels:
        return name
    sorted_labels = sorted(labels.items())
    label_str = ','.join((f'{k}={v}' for k, v in sorted_labels))
    return f'{name}{{{label_str}}}'

def _calculate_summary(self, name: str, metric_type: MetricType, values: List[float], labels: Dict[str, str]) -> MetricSummary:
    """Calculate summary statistics for a list of values."""
    if not values:
        return MetricSummary(name=name, type=metric_type, count=0, min_value=0, max_value=0, avg_value=0, sum_value=0, labels=labels)
    sorted_values = sorted(values)
    count = len(sorted_values)
    percentiles = {}
    for p in [50, 90, 95, 99]:
        index = int(p / 100 * count)
        if index >= count:
            index = count - 1
        percentiles[f'p{p}'] = sorted_values[index]
    return MetricSummary(name=name, type=metric_type, count=count, min_value=min(values), max_value=max(values), avg_value=sum(values) / count, sum_value=sum(values), percentiles=percentiles, labels=labels)

def __init__(self, retention_hours: int=24, max_metrics_per_type: int=10000):
    self.retention_hours = retention_hours
    self.max_metrics_per_type = max_metrics_per_type
    self.logger = logging.getLogger(__name__)
    self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_metrics_per_type))
    self.counters: Dict[str, float] = defaultdict(float)
    self.gauges: Dict[str, float] = {}
    self.histograms: Dict[str, List[float]] = defaultdict(list)
    self.timers: Dict[str, List[float]] = defaultdict(list)
    self.cleanup_task: Optional[asyncio.Task] = None
    self.collecting = False

def increment_counter(self, name: str, value: float=1.0, labels: Optional[Dict[str, str]]=None) -> None:
    """Increment a counter metric."""
    labels = labels or {}
    metric_key = self._create_metric_key(name, labels)
    self.counters[metric_key] += value
    metric = Metric(name=name, type=MetricType.COUNTER, value=value, timestamp=datetime.now(), labels=labels)
    self.metrics[metric_key].append(metric)

def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]]=None) -> None:
    """Set a gauge metric value."""
    labels = labels or {}
    metric_key = self._create_metric_key(name, labels)
    self.gauges[metric_key] = value
    metric = Metric(name=name, type=MetricType.GAUGE, value=value, timestamp=datetime.now(), labels=labels)
    self.metrics[metric_key].append(metric)

def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]]=None) -> None:
    """Record a value in a histogram metric."""
    labels = labels or {}
    metric_key = self._create_metric_key(name, labels)
    self.histograms[metric_key].append(value)
    if len(self.histograms[metric_key]) > 1000:
        self.histograms[metric_key] = self.histograms[metric_key][-1000:]
    metric = Metric(name=name, type=MetricType.HISTOGRAM, value=value, timestamp=datetime.now(), labels=labels)
    self.metrics[metric_key].append(metric)

def record_timer(self, name: str, duration_ms: float, labels: Optional[Dict[str, str]]=None) -> None:
    """Record a timer metric (duration in milliseconds)."""
    labels = labels or {}
    metric_key = self._create_metric_key(name, labels)
    self.timers[metric_key].append(duration_ms)
    if len(self.timers[metric_key]) > 1000:
        self.timers[metric_key] = self.timers[metric_key][-1000:]
    metric = Metric(name=name, type=MetricType.TIMER, value=duration_ms, timestamp=datetime.now(), labels=labels, unit='ms')
    self.metrics[metric_key].append(metric)

def get_counter_value(self, name: str, labels: Optional[Dict[str, str]]=None) -> float:
    """Get current counter value."""
    metric_key = self._create_metric_key(name, labels or {})
    return self.counters.get(metric_key, 0.0)

def get_gauge_value(self, name: str, labels: Optional[Dict[str, str]]=None) -> Optional[float]:
    """Get current gauge value."""
    metric_key = self._create_metric_key(name, labels or {})
    return self.gauges.get(metric_key)

def get_histogram_summary(self, name: str, labels: Optional[Dict[str, str]]=None) -> Optional[MetricSummary]:
    """Get histogram summary statistics."""
    metric_key = self._create_metric_key(name, labels or {})
    values = self.histograms.get(metric_key, [])
    if not values:
        return None
    return self._calculate_summary(name, MetricType.HISTOGRAM, values, labels or {})

def get_timer_summary(self, name: str, labels: Optional[Dict[str, str]]=None) -> Optional[MetricSummary]:
    """Get timer summary statistics."""
    metric_key = self._create_metric_key(name, labels or {})
    values = self.timers.get(metric_key, [])
    if not values:
        return None
    return self._calculate_summary(name, MetricType.TIMER, values, labels or {})

def get_all_metrics_summary(self) -> Dict[str, Any]:
    """Get summary of all collected metrics."""
    summary = {'counters': {}, 'gauges': {}, 'histograms': {}, 'timers': {}, 'collection_time': datetime.now().isoformat()}
    for metric_key, value in self.counters.items():
        name, labels = self._parse_metric_key(metric_key)
        summary['counters'][metric_key] = {'name': name, 'value': value, 'labels': labels}
    for metric_key, value in self.gauges.items():
        name, labels = self._parse_metric_key(metric_key)
        summary['gauges'][metric_key] = {'name': name, 'value': value, 'labels': labels}
    for metric_key, values in self.histograms.items():
        if values:
            name, labels = self._parse_metric_key(metric_key)
            summary_stats = self._calculate_summary(name, MetricType.HISTOGRAM, values, labels)
            summary['histograms'][metric_key] = summary_stats.__dict__
    for metric_key, values in self.timers.items():
        if values:
            name, labels = self._parse_metric_key(metric_key)
            summary_stats = self._calculate_summary(name, MetricType.TIMER, values, labels)
            summary['timers'][metric_key] = summary_stats.__dict__
    return summary

def get_performance_report(self) -> Dict[str, Any]:
    """Generate a comprehensive performance report."""
    summary = self.get_all_metrics_summary()
    report = {'timestamp': datetime.now().isoformat(), 'summary': summary, 'kpis': {}}
    messages_sent = self.get_counter_value('messages_sent')
    messages_received = self.get_counter_value('messages_received')
    if messages_sent > 0 or messages_received > 0:
        report['kpis']['message_throughput'] = {'messages_sent': messages_sent, 'messages_received': messages_received, 'total_messages': messages_sent + messages_received}
    latency_summary = self.get_timer_summary('message_latency')
    if latency_summary:
        report['kpis']['message_latency'] = {'avg_ms': latency_summary.avg_value, 'p95_ms': latency_summary.percentiles.get('p95', 0), 'p99_ms': latency_summary.percentiles.get('p99', 0)}
    errors = self.get_counter_value('errors')
    total_operations = self.get_counter_value('operations')
    if total_operations > 0:
        error_rate = errors / total_operations * 100
        report['kpis']['error_rate'] = {'errors': errors, 'total_operations': total_operations, 'error_rate_percent': round(error_rate, 2)}
    active_connections = self.get_gauge_value('active_connections')
    if active_connections is not None:
        report['kpis']['connections'] = {'active_connections': active_connections}
    return report

def _create_metric_key(self, name: str, labels: Dict[str, str]) -> str:
    """Create a unique key for a metric with labels."""
    if not labels:
        return name
    sorted_labels = sorted(labels.items())
    label_str = ','.join((f'{k}={v}' for k, v in sorted_labels))
    return f'{name}{{{label_str}}}'

def _calculate_summary(self, name: str, metric_type: MetricType, values: List[float], labels: Dict[str, str]) -> MetricSummary:
    """Calculate summary statistics for a list of values."""
    if not values:
        return MetricSummary(name=name, type=metric_type, count=0, min_value=0, max_value=0, avg_value=0, sum_value=0, labels=labels)
    sorted_values = sorted(values)
    count = len(sorted_values)
    percentiles = {}
    for p in [50, 90, 95, 99]:
        index = int(p / 100 * count)
        if index >= count:
            index = count - 1
        percentiles[f'p{p}'] = sorted_values[index]
    return MetricSummary(name=name, type=metric_type, count=count, min_value=min(values), max_value=max(values), avg_value=sum(values) / count, sum_value=sum(values), percentiles=percentiles, labels=labels)
