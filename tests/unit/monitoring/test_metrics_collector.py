"""
Unit tests for Metrics Collector

Tests high-performance metrics collection functionality including
counters, gauges, histograms, and metrics aggregation.
"""

import asyncio
import pytest
import time
import json
import threading
from datetime import datetime
from unittest.mock import Mock, patch

from src.beast_mode.observatory.monitoring.metrics_collector import (
    MetricsCollector, CounterMetric, GaugeMetric, HistogramMetric, MetricValue
)


class TestMetricsCollector:
    """Test cases for MetricsCollector"""

    @pytest.fixture
    def collector(self):
        """Create a metrics collector instance for testing"""
        return MetricsCollector(max_histogram_samples=100)

    def test_initialization(self, collector):
        """Test metrics collector initialization"""
        assert collector.max_histogram_samples == 100
        assert len(collector._counters) == 0
        assert len(collector._gauges) == 0
        assert len(collector._histograms) == 0
        assert collector._total_metrics_collected == 0
        assert isinstance(collector._lock, threading.RLock)

    @pytest.mark.asyncio
    async def test_increment_counter(self, collector):
        """Test counter increment functionality"""
        name = "test_counter"
        value = 5
        labels = {"endpoint": "test_endpoint", "type": "websocket"}
        
        await collector.increment_counter(name, value, labels)
        
        # Verify counter was created and incremented
        full_name = f"{name}{{endpoint=test_endpoint,type=websocket}}"
        assert full_name in collector._counters
        
        counter = collector._counters[full_name]
        assert counter.name == name
        assert counter.value == value
        assert counter.labels == labels
        assert collector._total_metrics_collected == 1

    @pytest.mark.asyncio
    async def test_increment_counter_default_value(self, collector):
        """Test counter increment with default value"""
        name = "test_counter"
        
        await collector.increment_counter(name)
        
        # Should increment by 1
        full_name = f"{name}"
        assert collector._counters[full_name].value == 1

    @pytest.mark.asyncio
    async def test_increment_counter_multiple_times(self, collector):
        """Test multiple counter increments"""
        name = "test_counter"
        
        await collector.increment_counter(name, 3)
        await collector.increment_counter(name, 2)
        await collector.increment_counter(name, 1)
        
        full_name = f"{name}"
        assert collector._counters[full_name].value == 6
        assert collector._total_metrics_collected == 3

    @pytest.mark.asyncio
    async def test_set_gauge(self, collector):
        """Test gauge setting functionality"""
        name = "test_gauge"
        value = 42.5
        labels = {"endpoint": "test_endpoint"}
        
        await collector.set_gauge(name, value, labels)
        
        # Verify gauge was created and set
        full_name = f"{name}{{endpoint=test_endpoint}}"
        assert full_name in collector._gauges
        
        gauge = collector._gauges[full_name]
        assert gauge.name == name
        assert gauge.value == value
        assert gauge.labels == labels
        assert collector._total_metrics_collected == 1

    @pytest.mark.asyncio
    async def test_set_gauge_overwrite(self, collector):
        """Test gauge value overwriting"""
        name = "test_gauge"
        
        await collector.set_gauge(name, 10.0)
        await collector.set_gauge(name, 20.0)
        
        full_name = f"{name}"
        assert collector._gauges[full_name].value == 20.0

    @pytest.mark.asyncio
    async def test_observe_histogram(self, collector):
        """Test histogram observation functionality"""
        name = "test_histogram"
        value = 150.0
        labels = {"endpoint": "test_endpoint"}
        
        await collector.observe_histogram(name, value, labels)
        
        # Verify histogram was created and value observed
        full_name = f"{name}{{endpoint=test_endpoint}}"
        assert full_name in collector._histograms
        
        histogram = collector._histograms[full_name]
        assert histogram.name == name
        assert histogram.labels == labels
        assert value in histogram.values
        assert collector._total_metrics_collected == 1

    @pytest.mark.asyncio
    async def test_observe_histogram_multiple_values(self, collector):
        """Test multiple histogram observations"""
        name = "test_histogram"
        values = [10.0, 20.0, 30.0, 40.0, 50.0]
        
        for value in values:
            await collector.observe_histogram(name, value)
        
        full_name = f"{name}"
        histogram = collector._histograms[full_name]
        assert len(histogram.values) == 5
        assert all(value in histogram.values for value in values)

    def test_get_counter(self, collector):
        """Test getting counter values"""
        name = "test_counter"
        labels = {"endpoint": "test_endpoint"}
        
        # Test non-existent counter
        value = collector.get_counter(name, labels)
        assert value == 0
        
        # Add counter manually
        full_name = f"{name}{{endpoint=test_endpoint}}"
        collector._counters[full_name] = CounterMetric(name=name, value=42, labels=labels)
        
        value = collector.get_counter(name, labels)
        assert value == 42

    def test_get_gauge(self, collector):
        """Test getting gauge values"""
        name = "test_gauge"
        labels = {"endpoint": "test_endpoint"}
        
        # Test non-existent gauge
        value = collector.get_gauge(name, labels)
        assert value == 0.0
        
        # Add gauge manually
        full_name = f"{name}{{endpoint=test_endpoint}}"
        collector._gauges[full_name] = GaugeMetric(name=name, value=3.14, labels=labels)
        
        value = collector.get_gauge(name, labels)
        assert value == 3.14

    def test_get_histogram_stats(self, collector):
        """Test getting histogram statistics"""
        name = "test_histogram"
        labels = {"endpoint": "test_endpoint"}
        
        # Test non-existent histogram
        stats = collector.get_histogram_stats(name, labels)
        assert stats['count'] == 0
        assert stats['min'] == 0.0
        assert stats['max'] == 0.0
        assert stats['avg'] == 0.0
        
        # Add histogram with data
        full_name = f"{name}{{endpoint=test_endpoint}}"
        histogram = HistogramMetric(name=name, labels=labels)
        histogram.values.extend([10.0, 20.0, 30.0, 40.0, 50.0])
        collector._histograms[full_name] = histogram
        
        stats = collector.get_histogram_stats(name, labels)
        
        assert stats['count'] == 5
        assert stats['min'] == 10.0
        assert stats['max'] == 50.0
        assert stats['avg'] == 30.0
        assert stats['p50'] == 30.0
        assert stats['p95'] == 50.0
        assert stats['p99'] == 50.0

    def test_get_all_metrics(self, collector):
        """Test getting all collected metrics"""
        # Initially empty
        metrics = collector.get_all_metrics()
        
        assert len(metrics['counters']) == 0
        assert len(metrics['gauges']) == 0
        assert len(metrics['histograms']) == 0
        assert 'metadata' in metrics
        assert metrics['metadata']['total_metrics_collected'] == 0
        
        # Add some metrics
        collector._counters['counter1'] = CounterMetric(name='counter1', value=10)
        collector._gauges['gauge1'] = GaugeMetric(name='gauge1', value=5.5)
        collector._histograms['histogram1'] = HistogramMetric(name='histogram1')
        
        metrics = collector.get_all_metrics()
        
        assert len(metrics['counters']) == 1
        assert len(metrics['gauges']) == 1
        assert len(metrics['histograms']) == 1
        assert 'counter1' in metrics['counters']
        assert 'gauge1' in metrics['gauges']
        assert 'histogram1' in metrics['histograms']

    def test_get_metrics_summary(self, collector):
        """Test getting metrics summary"""
        summary = collector.get_metrics_summary()
        
        assert summary['total_counters'] == 0
        assert summary['total_gauges'] == 0
        assert summary['total_histograms'] == 0
        assert summary['total_metrics_collected'] == 0
        assert summary['uptime_sec'] > 0
        assert summary['collection_rate_per_sec'] >= 0

    def test_clear_metrics_all(self, collector):
        """Test clearing all metrics"""
        # Add some metrics
        collector._counters['counter1'] = CounterMetric(name='counter1', value=10)
        collector._gauges['gauge1'] = GaugeMetric(name='gauge1', value=5.5)
        collector._histograms['histogram1'] = HistogramMetric(name='histogram1')
        collector._total_metrics_collected = 3
        
        collector.clear_metrics()
        
        assert len(collector._counters) == 0
        assert len(collector._gauges) == 0
        assert len(collector._histograms) == 0
        assert collector._total_metrics_collected == 0

    def test_clear_metrics_specific_type(self, collector):
        """Test clearing specific metric types"""
        # Add metrics of different types
        collector._counters['counter1'] = CounterMetric(name='counter1', value=10)
        collector._gauges['gauge1'] = GaugeMetric(name='gauge1', value=5.5)
        collector._histograms['histogram1'] = HistogramMetric(name='histogram1')
        
        # Clear only counters
        collector.clear_metrics('counters')
        
        assert len(collector._counters) == 0
        assert len(collector._gauges) == 1
        assert len(collector._histograms) == 1

    def test_export_metrics_json(self, collector):
        """Test exporting metrics in JSON format"""
        # Add some metrics
        collector._counters['counter1'] = CounterMetric(name='counter1', value=10)
        collector._gauges['gauge1'] = GaugeMetric(name='gauge1', value=5.5)
        
        json_output = collector.export_metrics('json')
        
        # Should be valid JSON
        data = json.loads(json_output)
        assert 'counters' in data
        assert 'gauges' in data
        assert 'metadata' in data

    def test_export_metrics_prometheus(self, collector):
        """Test exporting metrics in Prometheus format"""
        # Add some metrics
        collector._counters['counter1'] = CounterMetric(name='counter1', value=10, labels={'endpoint': 'test'})
        collector._gauges['gauge1'] = GaugeMetric(name='gauge1', value=5.5, labels={'endpoint': 'test'})
        
        histogram = HistogramMetric(name='histogram1', labels={'endpoint': 'test'})
        histogram.values.extend([10.0, 20.0, 30.0])
        collector._histograms['histogram1'] = histogram
        
        prometheus_output = collector.export_metrics('prometheus')
        
        # Should contain Prometheus format elements
        assert '# TYPE counter1 counter' in prometheus_output
        assert '# TYPE gauge1 gauge' in prometheus_output
        assert '# TYPE histogram1 histogram' in prometheus_output
        assert 'counter1{endpoint="test"} 10' in prometheus_output
        assert 'gauge1{endpoint="test"} 5.5' in prometheus_output

    def test_export_metrics_unsupported_format(self, collector):
        """Test exporting metrics with unsupported format"""
        with pytest.raises(ValueError):
            collector.export_metrics('unsupported_format')

    def test_create_label_key(self, collector):
        """Test label key creation"""
        # Test empty labels
        key = collector._create_label_key({})
        assert key == ""
        
        # Test single label
        key = collector._create_label_key({"endpoint": "test"})
        assert key == "{endpoint=test}"
        
        # Test multiple labels (should be sorted)
        key = collector._create_label_key({"endpoint": "test", "type": "websocket"})
        assert key == "{endpoint=test,type=websocket}"
        
        # Test with different order (should still be sorted)
        key = collector._create_label_key({"type": "websocket", "endpoint": "test"})
        assert key == "{endpoint=test,type=websocket}"

    def test_thread_safety(self, collector):
        """Test thread safety of metrics collection"""
        def increment_counter():
            for _ in range(100):
                collector._counters[f"counter_{threading.current_thread().ident}"] = \
                    CounterMetric(name=f"counter_{threading.current_thread().ident}", value=1)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=increment_counter)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should have 5 counters (one per thread)
        assert len(collector._counters) == 5

    def test_log_action(self, collector, capsys):
        """Test JSON logging functionality"""
        collector._log_action("test_action", {"key": "value"})
        
        captured = capsys.readouterr()
        log_output = captured.out.strip()
        
        # Should be valid JSON
        log_data = json.loads(log_output)
        
        assert log_data["task"] == "3.1"
        assert log_data["action"] == "metrics_collector_test_action"
        assert log_data["status"] == "in_progress"
        assert log_data["details"]["key"] == "value"
        assert "timestamp" in log_data


class TestCounterMetric:
    """Test cases for CounterMetric dataclass"""
    
    def test_counter_metric_creation(self):
        """Test CounterMetric creation"""
        counter = CounterMetric(
            name="test_counter",
            value=42,
            labels={"endpoint": "test_endpoint"},
            last_updated=time.time()
        )
        
        assert counter.name == "test_counter"
        assert counter.value == 42
        assert counter.labels == {"endpoint": "test_endpoint"}
        assert counter.last_updated > 0

    def test_counter_metric_defaults(self):
        """Test CounterMetric default values"""
        counter = CounterMetric(name="test_counter")
        
        assert counter.name == "test_counter"
        assert counter.value == 0
        assert counter.labels == {}
        assert counter.last_updated > 0


class TestGaugeMetric:
    """Test cases for GaugeMetric dataclass"""
    
    def test_gauge_metric_creation(self):
        """Test GaugeMetric creation"""
        gauge = GaugeMetric(
            name="test_gauge",
            value=3.14,
            labels={"endpoint": "test_endpoint"},
            last_updated=time.time()
        )
        
        assert gauge.name == "test_gauge"
        assert gauge.value == 3.14
        assert gauge.labels == {"endpoint": "test_endpoint"}
        assert gauge.last_updated > 0

    def test_gauge_metric_defaults(self):
        """Test GaugeMetric default values"""
        gauge = GaugeMetric(name="test_gauge")
        
        assert gauge.name == "test_gauge"
        assert gauge.value == 0.0
        assert gauge.labels == {}
        assert gauge.last_updated > 0


class TestHistogramMetric:
    """Test cases for HistogramMetric dataclass"""
    
    def test_histogram_metric_creation(self):
        """Test HistogramMetric creation"""
        histogram = HistogramMetric(
            name="test_histogram",
            labels={"endpoint": "test_endpoint"},
            last_updated=time.time()
        )
        
        assert histogram.name == "test_histogram"
        assert histogram.labels == {"endpoint": "test_endpoint"}
        assert histogram.last_updated > 0
        assert len(histogram.values) == 0

    def test_histogram_metric_defaults(self):
        """Test HistogramMetric default values"""
        histogram = HistogramMetric(name="test_histogram")
        
        assert histogram.name == "test_histogram"
        assert histogram.labels == {}
        assert histogram.last_updated > 0
        assert len(histogram.values) == 0


class TestMetricValue:
    """Test cases for MetricValue dataclass"""
    
    def test_metric_value_creation(self):
        """Test MetricValue creation"""
        value = MetricValue(
            value=42.5,
            timestamp=time.time(),
            labels={"endpoint": "test_endpoint"}
        )
        
        assert value.value == 42.5
        assert value.timestamp > 0
        assert value.labels == {"endpoint": "test_endpoint"}

    def test_metric_value_defaults(self):
        """Test MetricValue default values"""
        value = MetricValue(value=42.5, timestamp=time.time())
        
        assert value.value == 42.5
        assert value.timestamp > 0
        assert value.labels == {}