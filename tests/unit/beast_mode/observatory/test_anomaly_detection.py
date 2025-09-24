"""
Comprehensive unit tests for Observatory Anomaly Detection

Tests anomaly detection algorithms, threshold monitoring, pattern-based detection,
and real-time alert generation for production reliability.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any

from src.beast_mode.observatory.anomaly_detection import (
    AnomalyDetector,
    ThresholdMonitor,
    StatisticalAnomalyDetector,
    PatternAnomalyDetector,
    RealTimeAnomalyProcessor,
    AnomalyClassifier,
    AnomalyAggregator,
)
from src.beast_mode.observatory.models import (
    CoordinationEvent,
    CoordinationEventType,
    CoordinationMetrics,
    LLMMetrics,
    CostMetrics,
    HealthScore,
    Anomaly,
    AnomalyType,
    AnomalySeverity,
    ObservatoryConfig,
)


class TestThresholdMonitor:
    """Test suite for ThresholdMonitor component."""

    @pytest.fixture
    def threshold_monitor(self):
        """Create ThresholdMonitor instance for testing."""
        thresholds = {
            'cost': {'warning': 100.0, 'critical': 200.0},
            'error_rate': {'warning': 0.05, 'critical': 0.10},
            'health_score': {'warning': 0.8, 'critical': 0.7},
            'queue_depth': {'warning': 100, 'critical': 200},
            'response_time': {'warning': 2000, 'critical': 5000}
        }
        return ThresholdMonitor(thresholds)

    @pytest.fixture
    def sample_metrics(self):
        """Create sample metrics for testing."""
        return CoordinationMetrics(
            timestamp=datetime.now(),
            active_tasks=50,
            completed_tasks=1000,
            failed_tasks=20,  # 2% error rate
            queue_depth=75,
            api_calls_count=500,
            total_cost=Decimal("150.00"),  # Above warning threshold
            health_score=0.85,  # Above critical threshold
            event_id="test_metric_1"
        )

    def test_monitor_initialization(self, threshold_monitor):
        """Test ThresholdMonitor initialization."""
        assert threshold_monitor is not None
        assert hasattr(threshold_monitor, 'check_thresholds')
        assert hasattr(threshold_monitor, 'update_thresholds')

    def test_check_cost_threshold_warning(self, threshold_monitor, sample_metrics):
        """Test cost threshold warning detection."""
        anomalies = threshold_monitor.check_thresholds(sample_metrics)

        cost_anomalies = [a for a in anomalies if a.anomaly_type == AnomalyType.COST_SPIKE]
        assert len(cost_anomalies) == 1
        assert cost_anomalies[0].severity == AnomalySeverity.MEDIUM

    def test_check_cost_threshold_critical(self, threshold_monitor):
        """Test cost threshold critical detection."""
        critical_metrics = CoordinationMetrics(
            timestamp=datetime.now(),
            active_tasks=50,
            completed_tasks=1000,
            failed_tasks=10,
            queue_depth=75,
            api_calls_count=500,
            total_cost=Decimal("250.00"),  # Above critical threshold
            health_score=0.85,
            event_id="critical_metric"
        )

        anomalies = threshold_monitor.check_thresholds(critical_metrics)

        cost_anomalies = [a for a in anomalies if a.anomaly_type == AnomalyType.COST_SPIKE]
        assert len(cost_anomalies) == 1
        assert cost_anomalies[0].severity == AnomalySeverity.CRITICAL

    def test_check_health_score_threshold(self, threshold_monitor):
        """Test health score threshold detection."""
        unhealthy_metrics = CoordinationMetrics(
            timestamp=datetime.now(),
            active_tasks=50,
            completed_tasks=1000,
            failed_tasks=10,
            queue_depth=75,
            api_calls_count=500,
            total_cost=Decimal("50.00"),
            health_score=0.65,  # Below critical threshold
            event_id="unhealthy_metric"
        )

        anomalies = threshold_monitor.check_thresholds(unhealthy_metrics)

        health_anomalies = [a for a in anomalies if 'health' in a.description.lower()]
        assert len(health_anomalies) == 1
        assert health_anomalies[0].severity == AnomalySeverity.CRITICAL

    def test_check_error_rate_threshold(self, threshold_monitor):
        """Test error rate threshold detection."""
        high_error_metrics = CoordinationMetrics(
            timestamp=datetime.now(),
            active_tasks=50,
            completed_tasks=800,
            failed_tasks=100,  # 11.1% error rate (above critical)
            queue_depth=75,
            api_calls_count=500,
            total_cost=Decimal("50.00"),
            health_score=0.85,
            event_id="high_error_metric"
        )

        anomalies = threshold_monitor.check_thresholds(high_error_metrics)

        error_anomalies = [a for a in anomalies if a.anomaly_type == AnomalyType.ERROR_RATE_INCREASE]
        assert len(error_anomalies) == 1
        assert error_anomalies[0].severity == AnomalySeverity.CRITICAL

    def test_update_thresholds(self, threshold_monitor):
        """Test threshold updates."""
        new_thresholds = {
            'cost': {'warning': 75.0, 'critical': 150.0}
        }

        threshold_monitor.update_thresholds(new_thresholds)

        # Test that new thresholds are applied
        test_metrics = CoordinationMetrics(
            timestamp=datetime.now(),
            active_tasks=50,
            completed_tasks=1000,
            failed_tasks=10,
            queue_depth=75,
            api_calls_count=500,
            total_cost=Decimal("80.00"),  # Between new warning and critical
            health_score=0.85,
            event_id="threshold_update_test"
        )

        anomalies = threshold_monitor.check_thresholds(test_metrics)
        cost_anomalies = [a for a in anomalies if a.anomaly_type == AnomalyType.COST_SPIKE]
        assert len(cost_anomalies) == 1
        assert cost_anomalies[0].severity == AnomalySeverity.MEDIUM

    def test_no_anomalies_within_thresholds(self, threshold_monitor):
        """Test that no anomalies are detected when within thresholds."""
        normal_metrics = CoordinationMetrics(
            timestamp=datetime.now(),
            active_tasks=50,
            completed_tasks=1000,
            failed_tasks=10,  # 1% error rate
            queue_depth=50,
            api_calls_count=500,
            total_cost=Decimal("50.00"),  # Below warning
            health_score=0.95,  # Above warning
            event_id="normal_metric"
        )

        anomalies = threshold_monitor.check_thresholds(normal_metrics)
        assert len(anomalies) == 0


class TestStatisticalAnomalyDetector:
    """Test suite for StatisticalAnomalyDetector component."""

    @pytest.fixture
    def statistical_detector(self):
        """Create StatisticalAnomalyDetector instance for testing."""
        return StatisticalAnomalyDetector(
            window_size=100,
            std_threshold=2.5,
            min_samples=10
        )

    @pytest.fixture
    def normal_data(self):
        """Create normal distribution data for testing."""
        import random
        random.seed(42)  # For reproducible tests
        return [random.gauss(100, 10) for _ in range(100)]

    def test_detector_initialization(self, statistical_detector):
        """Test StatisticalAnomalyDetector initialization."""
        assert statistical_detector is not None
        assert statistical_detector.window_size == 100
        assert statistical_detector.std_threshold == 2.5
        assert statistical_detector.min_samples == 10

    def test_detect_outliers_normal_data(self, statistical_detector, normal_data):
        """Test outlier detection with normal data."""
        anomalies = statistical_detector.detect_outliers(normal_data)

        # With normal data, should have very few outliers
        assert len(anomalies) < 5  # Less than 5% outliers

    def test_detect_outliers_with_anomalies(self, statistical_detector, normal_data):
        """Test outlier detection with injected anomalies."""
        # Inject clear anomalies
        anomalous_data = normal_data.copy()
        anomalous_data.extend([200, 250, 300])  # Clear outliers

        anomalies = statistical_detector.detect_outliers(anomalous_data)

        # Should detect the injected anomalies
        assert len(anomalies) >= 3

        # Check that the anomalies are at the expected positions
        anomaly_indices = [a['index'] for a in anomalies]
        assert any(idx >= 100 for idx in anomaly_indices)  # Injected anomalies

    def test_detect_insufficient_data(self, statistical_detector):
        """Test detection with insufficient data."""
        sparse_data = [1, 2, 3, 4, 5]  # Less than min_samples

        anomalies = statistical_detector.detect_outliers(sparse_data)
        assert len(anomalies) == 0  # Should return no anomalies

    def test_calculate_z_scores(self, statistical_detector):
        """Test Z-score calculation."""
        test_data = [1, 2, 3, 4, 5, 100]  # 100 is clearly an outlier

        z_scores = statistical_detector.calculate_z_scores(test_data)

        assert len(z_scores) == len(test_data)
        assert abs(z_scores[-1]) > abs(z_scores[0])  # Last value should have higher Z-score

    def test_adaptive_threshold(self, statistical_detector):
        """Test adaptive threshold adjustment."""
        # Data with varying volatility
        stable_data = [10] * 50
        volatile_data = list(range(1, 51))

        # Should adapt threshold based on data characteristics
        stable_anomalies = statistical_detector.detect_outliers(stable_data + [20])
        volatile_anomalies = statistical_detector.detect_outliers(volatile_data + [100])

        # Stable data should be more sensitive to small changes
        assert len(stable_anomalies) > 0


class TestPatternAnomalyDetector:
    """Test suite for PatternAnomalyDetector component."""

    @pytest.fixture
    def pattern_detector(self):
        """Create PatternAnomalyDetector instance for testing."""
        return PatternAnomalyDetector(
            pattern_window=24,  # 24 hour window
            similarity_threshold=0.8,
            min_pattern_length=4
        )

    @pytest.fixture
    def regular_pattern_data(self):
        """Create data with regular daily pattern."""
        data = []
        base_time = datetime.now()

        # Create 7 days of regular pattern (high during day, low at night)
        for day in range(7):
            for hour in range(24):
                if 8 <= hour <= 18:  # Business hours
                    value = 100 + (hour - 8) * 10
                else:  # Off hours
                    value = 20 + hour * 2

                data.append({
                    'timestamp': base_time - timedelta(days=day, hours=23-hour),
                    'value': value,
                    'metric': 'active_tasks'
                })

        return data

    def test_detector_initialization(self, pattern_detector):
        """Test PatternAnomalyDetector initialization."""
        assert pattern_detector is not None
        assert pattern_detector.pattern_window == 24
        assert pattern_detector.similarity_threshold == 0.8

    def test_learn_normal_patterns(self, pattern_detector, regular_pattern_data):
        """Test learning of normal patterns."""
        pattern_detector.learn_normal_patterns(regular_pattern_data)

        assert len(pattern_detector.learned_patterns) > 0
        assert 'daily' in pattern_detector.learned_patterns

    def test_detect_pattern_anomalies(self, pattern_detector, regular_pattern_data):
        """Test detection of pattern anomalies."""
        # Learn normal pattern first
        pattern_detector.learn_normal_patterns(regular_pattern_data)

        # Create anomalous data (high activity at night)
        anomalous_data = []
        base_time = datetime.now()

        for hour in range(24):
            if 0 <= hour <= 6:  # Unusual high activity at night
                value = 150  # Much higher than normal
            else:
                value = 50

            anomalous_data.append({
                'timestamp': base_time - timedelta(hours=23-hour),
                'value': value,
                'metric': 'active_tasks'
            })

        anomalies = pattern_detector.detect_pattern_anomalies(anomalous_data)

        # Should detect the unusual night activity
        assert len(anomalies) > 0
        night_anomalies = [a for a in anomalies if 0 <= a['hour'] <= 6]
        assert len(night_anomalies) > 0

    def test_seasonal_pattern_detection(self, pattern_detector):
        """Test detection of seasonal/weekly patterns."""
        # Create weekly pattern data
        weekly_data = []
        base_time = datetime.now()

        for week in range(4):  # 4 weeks
            for day in range(7):
                if day < 5:  # Weekdays
                    value = 100
                else:  # Weekends
                    value = 30

                weekly_data.append({
                    'timestamp': base_time - timedelta(weeks=week, days=day),
                    'value': value,
                    'metric': 'api_calls'
                })

        pattern_detector.learn_normal_patterns(weekly_data)

        # Should learn weekly pattern
        assert 'weekly' in pattern_detector.learned_patterns

    def test_pattern_similarity_calculation(self, pattern_detector):
        """Test pattern similarity calculation."""
        pattern1 = [10, 20, 30, 40, 50]
        pattern2 = [12, 22, 32, 42, 52]  # Similar pattern
        pattern3 = [50, 40, 30, 20, 10]  # Opposite pattern

        similarity_high = pattern_detector.calculate_pattern_similarity(pattern1, pattern2)
        similarity_low = pattern_detector.calculate_pattern_similarity(pattern1, pattern3)

        assert similarity_high > similarity_low
        assert similarity_high > 0.8  # Should be highly similar


class TestRealTimeAnomalyProcessor:
    """Test suite for RealTimeAnomalyProcessor component."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ObservatoryConfig(
            redis_host="localhost",
            redis_port=6379,
            enable_real_time=True,
            anomaly_detection_enabled=True,
            alert_cooldown_seconds=300
        )

    @pytest.fixture
    def processor(self, config):
        """Create RealTimeAnomalyProcessor instance for testing."""
        return RealTimeAnomalyProcessor(config)

    def test_processor_initialization(self, processor):
        """Test RealTimeAnomalyProcessor initialization."""
        assert processor is not None
        assert hasattr(processor, 'process_event')
        assert hasattr(processor, 'check_anomalies')

    @pytest.mark.asyncio
    async def test_process_normal_event(self, processor):
        """Test processing of normal events."""
        normal_event = CoordinationEvent(
            event_type=CoordinationEventType.TASK_COMPLETED,
            timestamp=datetime.now(),
            details={
                'task_id': 'normal_task',
                'duration_ms': 1000,
                'cost': 0.05
            }
        )

        result = await processor.process_event(normal_event)

        assert result is not None
        assert result['anomalies_detected'] == 0
        assert result['alerts_triggered'] == 0

    @pytest.mark.asyncio
    async def test_process_anomalous_event(self, processor):
        """Test processing of anomalous events."""
        anomalous_event = CoordinationEvent(
            event_type=CoordinationEventType.API_CALL_FAILURE,
            timestamp=datetime.now(),
            details={
                'api_call': 'llm_request',
                'error': 'timeout',
                'duration_ms': 30000,  # Unusually long
                'retry_count': 5
            }
        )

        with patch.object(processor, '_classify_event_anomaly') as mock_classify:
            mock_classify.return_value = Anomaly(
                anomaly_type=AnomalyType.PERFORMANCE_DEGRADATION,
                severity=AnomalySeverity.HIGH,
                description="Unusually long API call duration",
                timestamp=datetime.now(),
                details={'duration_ms': 30000},
                confidence_score=0.9
            )

            result = await processor.process_event(anomalous_event)

            assert result['anomalies_detected'] == 1
            mock_classify.assert_called_once_with(anomalous_event)

    @pytest.mark.asyncio
    async def test_batch_processing(self, processor):
        """Test batch processing of multiple events."""
        events = [
            CoordinationEvent(
                event_type=CoordinationEventType.TASK_COMPLETED,
                timestamp=datetime.now() - timedelta(seconds=i),
                details={'task_id': f'task_{i}', 'duration_ms': 1000 + i*100}
            )
            for i in range(10)
        ]

        results = await processor.process_batch(events)

        assert len(results) == 10
        assert all('anomalies_detected' in result for result in results)

    def test_alert_cooldown(self, processor):
        """Test alert cooldown mechanism."""
        anomaly = Anomaly(
            anomaly_type=AnomalyType.COST_SPIKE,
            severity=AnomalySeverity.HIGH,
            description="High cost detected",
            timestamp=datetime.now(),
            details={'cost': 200.0},
            confidence_score=0.8
        )

        # First alert should be sent
        should_alert_1 = processor.should_trigger_alert(anomaly)
        assert should_alert_1 == True

        # Immediate second alert of same type should be suppressed
        should_alert_2 = processor.should_trigger_alert(anomaly)
        assert should_alert_2 == False

        # Different anomaly type should still alert
        different_anomaly = Anomaly(
            anomaly_type=AnomalyType.ERROR_RATE_INCREASE,
            severity=AnomalySeverity.HIGH,
            description="High error rate detected",
            timestamp=datetime.now(),
            details={'error_rate': 0.15},
            confidence_score=0.8
        )

        should_alert_3 = processor.should_trigger_alert(different_anomaly)
        assert should_alert_3 == True


class TestAnomalyClassifier:
    """Test suite for AnomalyClassifier component."""

    @pytest.fixture
    def classifier(self):
        """Create AnomalyClassifier instance for testing."""
        return AnomalyClassifier()

    def test_classify_cost_anomaly(self, classifier):
        """Test classification of cost anomalies."""
        cost_event = CoordinationEvent(
            event_type=CoordinationEventType.COST_THRESHOLD_REACHED,
            timestamp=datetime.now(),
            details={
                'current_cost': 250.0,
                'threshold': 200.0,
                'increase_rate': 0.25
            }
        )

        anomaly = classifier.classify_event(cost_event)

        assert anomaly is not None
        assert anomaly.anomaly_type == AnomalyType.COST_SPIKE
        assert anomaly.severity in [AnomalySeverity.MEDIUM, AnomalySeverity.HIGH]

    def test_classify_performance_anomaly(self, classifier):
        """Test classification of performance anomalies."""
        performance_event = CoordinationEvent(
            event_type=CoordinationEventType.TASK_FAILED,
            timestamp=datetime.now(),
            details={
                'task_id': 'slow_task',
                'duration_ms': 15000,  # Very slow
                'failure_reason': 'timeout',
                'expected_duration_ms': 2000
            }
        )

        anomaly = classifier.classify_event(performance_event)

        assert anomaly is not None
        assert anomaly.anomaly_type == AnomalyType.PERFORMANCE_DEGRADATION
        assert anomaly.confidence_score > 0.5

    def test_classify_coordination_breakdown(self, classifier):
        """Test classification of coordination breakdown anomalies."""
        coordination_event = CoordinationEvent(
            event_type=CoordinationEventType.SYSTEM_HEALTH_CHANGE,
            timestamp=datetime.now(),
            details={
                'previous_health': 0.95,
                'current_health': 0.4,
                'affected_components': ['redis', 'task_queue', 'api_gateway'],
                'failure_cascade': True
            }
        )

        anomaly = classifier.classify_event(coordination_event)

        assert anomaly is not None
        assert anomaly.anomaly_type == AnomalyType.COORDINATION_BREAKDOWN
        assert anomaly.severity == AnomalySeverity.CRITICAL

    def test_no_classification_for_normal_event(self, classifier):
        """Test that normal events don't get classified as anomalies."""
        normal_event = CoordinationEvent(
            event_type=CoordinationEventType.TASK_COMPLETED,
            timestamp=datetime.now(),
            details={
                'task_id': 'normal_task',
                'duration_ms': 1200,
                'cost': 0.03
            }
        )

        anomaly = classifier.classify_event(normal_event)
        assert anomaly is None


class TestAnomalyAggregator:
    """Test suite for AnomalyAggregator component."""

    @pytest.fixture
    def aggregator(self):
        """Create AnomalyAggregator instance for testing."""
        return AnomalyAggregator(
            aggregation_window_minutes=5,
            similarity_threshold=0.8
        )

    @pytest.fixture
    def sample_anomalies(self):
        """Create sample anomalies for testing."""
        base_time = datetime.now()
        return [
            Anomaly(
                anomaly_type=AnomalyType.COST_SPIKE,
                severity=AnomalySeverity.MEDIUM,
                description="Cost increase detected",
                timestamp=base_time - timedelta(minutes=i),
                details={'cost': 120.0 + i*5},
                confidence_score=0.7
            )
            for i in range(3)
        ] + [
            Anomaly(
                anomaly_type=AnomalyType.ERROR_RATE_INCREASE,
                severity=AnomalySeverity.HIGH,
                description="High error rate",
                timestamp=base_time - timedelta(minutes=2),
                details={'error_rate': 0.15},
                confidence_score=0.8
            )
        ]

    def test_aggregator_initialization(self, aggregator):
        """Test AnomalyAggregator initialization."""
        assert aggregator is not None
        assert aggregator.aggregation_window_minutes == 5

    def test_aggregate_similar_anomalies(self, aggregator, sample_anomalies):
        """Test aggregation of similar anomalies."""
        # Get only cost anomalies (first 3)
        cost_anomalies = sample_anomalies[:3]

        aggregated = aggregator.aggregate_anomalies(cost_anomalies)

        # Should aggregate similar cost anomalies
        assert len(aggregated) == 1
        assert aggregated[0].anomaly_type == AnomalyType.COST_SPIKE

        # Aggregated anomaly should have higher severity
        assert aggregated[0].severity in [AnomalySeverity.HIGH, AnomalySeverity.CRITICAL]

    def test_no_aggregation_for_different_types(self, aggregator, sample_anomalies):
        """Test that different anomaly types are not aggregated."""
        aggregated = aggregator.aggregate_anomalies(sample_anomalies)

        # Should have separate entries for cost and error rate anomalies
        anomaly_types = [a.anomaly_type for a in aggregated]
        assert AnomalyType.COST_SPIKE in anomaly_types
        assert AnomalyType.ERROR_RATE_INCREASE in anomaly_types

    def test_time_window_aggregation(self, aggregator):
        """Test aggregation within time windows."""
        base_time = datetime.now()

        # Anomalies within window
        recent_anomalies = [
            Anomaly(
                anomaly_type=AnomalyType.PERFORMANCE_DEGRADATION,
                severity=AnomalySeverity.MEDIUM,
                description="Slow response",
                timestamp=base_time - timedelta(minutes=i),
                details={'response_time': 3000 + i*100},
                confidence_score=0.6
            )
            for i in range(3)  # Within 5-minute window
        ]

        # Anomaly outside window
        old_anomaly = Anomaly(
            anomaly_type=AnomalyType.PERFORMANCE_DEGRADATION,
            severity=AnomalySeverity.MEDIUM,
            description="Old slow response",
            timestamp=base_time - timedelta(minutes=10),  # Outside window
            details={'response_time': 3500},
            confidence_score=0.6
        )

        all_anomalies = recent_anomalies + [old_anomaly]
        aggregated = aggregator.aggregate_anomalies(all_anomalies)

        # Should have 2 groups: recent aggregated + old separate
        assert len(aggregated) == 2

    def test_severity_escalation(self, aggregator):
        """Test severity escalation in aggregated anomalies."""
        # Multiple medium severity anomalies
        medium_anomalies = [
            Anomaly(
                anomaly_type=AnomalyType.ERROR_RATE_INCREASE,
                severity=AnomalySeverity.MEDIUM,
                description=f"Error rate increase {i}",
                timestamp=datetime.now() - timedelta(seconds=i*30),
                details={'error_rate': 0.06 + i*0.01},
                confidence_score=0.7
            )
            for i in range(4)
        ]

        aggregated = aggregator.aggregate_anomalies(medium_anomalies)

        # Multiple medium anomalies should escalate to high
        assert len(aggregated) == 1
        assert aggregated[0].severity == AnomalySeverity.HIGH


class TestAnomalyDetectorIntegration:
    """Integration tests for the complete anomaly detection system."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ObservatoryConfig(
            redis_host="localhost",
            redis_port=6379,
            enable_real_time=True,
            anomaly_detection_enabled=True
        )

    @pytest.fixture
    def anomaly_detector(self, config):
        """Create main AnomalyDetector instance for testing."""
        return AnomalyDetector(config)

    @pytest.mark.asyncio
    async def test_end_to_end_anomaly_detection(self, anomaly_detector):
        """Test end-to-end anomaly detection pipeline."""
        # Create metrics with anomalous values
        anomalous_metrics = CoordinationMetrics(
            timestamp=datetime.now(),
            active_tasks=500,  # Very high
            completed_tasks=1000,
            failed_tasks=200,  # High error rate
            queue_depth=300,   # High queue depth
            api_calls_count=2000,
            total_cost=Decimal("500.00"),  # High cost
            health_score=0.5,  # Low health
            event_id="anomalous_test"
        )

        # Process through complete pipeline
        with patch.object(anomaly_detector, '_store_anomalies') as mock_store:
            result = await anomaly_detector.detect_anomalies(anomalous_metrics)

            assert result is not None
            assert len(result['anomalies']) > 0

            # Should detect multiple types of anomalies
            anomaly_types = [a.anomaly_type for a in result['anomalies']]
            assert AnomalyType.COST_SPIKE in anomaly_types
            assert AnomalyType.ERROR_RATE_INCREASE in anomaly_types

            # Should have called storage
            mock_store.assert_called_once()

    @pytest.mark.asyncio
    async def test_real_time_processing_pipeline(self, anomaly_detector):
        """Test real-time event processing pipeline."""
        events = [
            CoordinationEvent(
                event_type=CoordinationEventType.API_CALL_FAILURE,
                timestamp=datetime.now() - timedelta(seconds=i),
                details={
                    'api': 'llm_request',
                    'error': 'timeout',
                    'duration_ms': 5000 + i*1000
                }
            )
            for i in range(5)  # Burst of failures
        ]

        with patch.object(anomaly_detector, '_trigger_alerts') as mock_alert:
            results = []
            for event in events:
                result = await anomaly_detector.process_real_time_event(event)
                results.append(result)

            # Should detect pattern of failures
            total_anomalies = sum(r['anomalies_detected'] for r in results)
            assert total_anomalies > 0

            # Should trigger alerts for significant anomalies
            mock_alert.assert_called()

    def test_get_detector_status(self, anomaly_detector):
        """Test anomaly detector status reporting."""
        status = anomaly_detector.get_detector_status()

        assert status is not None
        assert 'detection_enabled' in status
        assert 'detectors_active' in status
        assert 'recent_anomaly_count' in status
        assert 'alert_count' in status