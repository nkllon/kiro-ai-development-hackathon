"""
Comprehensive unit tests for Observatory Analytics Engine

Tests the core analytics capabilities including trend analysis, pattern recognition,
predictive analytics, and real-time insights generation for production reliability.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any

from src.beast_mode.observatory.analytics_engine import (
    ObservatoryAnalyticsEngine,
    TrendAnalyzer,
    PatternRecognizer,
    PredictiveAnalyzer,
    InsightGenerator,
    MetricsTimeWindow,
    TrendDirection,
    AnalyticsInsight,
    PatternType,
    PredictionConfidence,
)
from src.beast_mode.observatory.models import (
    CoordinationEvent,
    CoordinationEventType,
    CoordinationMetrics,
    LLMMetrics,
    CostMetrics,
    HealthScore,
    Anomaly,
    AnomalySeverity,
    ObservatoryConfig,
)


class TestTrendAnalyzer:
    """Test suite for TrendAnalyzer component."""

    @pytest.fixture
    def trend_analyzer(self):
        """Create TrendAnalyzer instance for testing."""
        return TrendAnalyzer()

    @pytest.fixture
    def sample_metrics(self):
        """Create sample coordination metrics for testing."""
        base_time = datetime.now()
        return [
            CoordinationMetrics(
                timestamp=base_time - timedelta(minutes=i*5),
                active_tasks=100 + i*10,
                completed_tasks=500 + i*20,
                failed_tasks=5 + i,
                queue_depth=50 - i*5,
                api_calls_count=200 + i*15,
                total_cost=Decimal(f"{10.50 + i*0.25:.2f}"),
                health_score=0.95 - i*0.02,
                event_id=f"metric_{i}"
            )
            for i in range(12)  # 12 data points over 1 hour
        ]

    def test_analyzer_initialization(self, trend_analyzer):
        """Test TrendAnalyzer initialization."""
        assert trend_analyzer is not None
        assert hasattr(trend_analyzer, 'analyze_trend')
        assert hasattr(trend_analyzer, 'calculate_trend_strength')

    def test_analyze_trend_increasing(self, trend_analyzer, sample_metrics):
        """Test trend analysis for increasing metrics."""
        # Use increasing cost trend
        costs = [float(m.total_cost) for m in sample_metrics]

        trend = trend_analyzer.analyze_trend(costs, MetricsTimeWindow.HOUR_1)

        assert trend.direction == TrendDirection.INCREASING
        assert trend.strength > 0.5  # Strong upward trend
        assert trend.confidence > 0.8

    def test_analyze_trend_decreasing(self, trend_analyzer, sample_metrics):
        """Test trend analysis for decreasing metrics."""
        # Use decreasing health score trend
        health_scores = [m.health_score for m in sample_metrics]

        trend = trend_analyzer.analyze_trend(health_scores, MetricsTimeWindow.HOUR_1)

        assert trend.direction == TrendDirection.DECREASING
        assert trend.strength > 0.5
        assert trend.confidence > 0.7

    def test_analyze_trend_stable(self, trend_analyzer):
        """Test trend analysis for stable metrics."""
        stable_values = [100.0] * 10  # Completely stable

        trend = trend_analyzer.analyze_trend(stable_values, MetricsTimeWindow.MINUTE_30)

        assert trend.direction == TrendDirection.STABLE
        assert trend.strength < 0.1  # Very low strength for stable trend
        assert trend.confidence > 0.9

    def test_analyze_trend_empty_data(self, trend_analyzer):
        """Test trend analysis with empty data."""
        with pytest.raises(ValueError, match="Insufficient data"):
            trend_analyzer.analyze_trend([], MetricsTimeWindow.MINUTE_15)

    def test_calculate_trend_strength(self, trend_analyzer):
        """Test trend strength calculation."""
        # Strong linear trend
        strong_trend = list(range(1, 11))  # 1, 2, 3, ..., 10
        strength = trend_analyzer.calculate_trend_strength(strong_trend)
        assert strength > 0.9

        # Weak trend with noise
        weak_trend = [1, 1.5, 1.8, 2.1, 1.9, 2.3, 2.1, 2.4, 2.2, 2.5]
        strength = trend_analyzer.calculate_trend_strength(weak_trend)
        assert 0.3 < strength < 0.8


class TestPatternRecognizer:
    """Test suite for PatternRecognizer component."""

    @pytest.fixture
    def pattern_recognizer(self):
        """Create PatternRecognizer instance for testing."""
        return PatternRecognizer()

    @pytest.fixture
    def sample_events(self):
        """Create sample coordination events for testing."""
        base_time = datetime.now()
        return [
            CoordinationEvent(
                event_type=CoordinationEventType.TASK_COMPLETED,
                timestamp=base_time - timedelta(minutes=i),
                details={"task_id": f"task_{i}", "duration_ms": 1000 + i*100}
            )
            for i in range(20)
        ]

    def test_recognize_patterns(self, pattern_recognizer, sample_events):
        """Test pattern recognition in events."""
        patterns = pattern_recognizer.recognize_patterns(sample_events)

        assert len(patterns) > 0
        assert any(p.pattern_type == PatternType.TEMPORAL for p in patterns)

    def test_detect_cyclic_patterns(self, pattern_recognizer):
        """Test detection of cyclic patterns."""
        # Create hourly cyclic pattern
        cyclic_events = []
        base_time = datetime.now()

        for day in range(3):  # 3 days of data
            for hour in [9, 13, 17]:  # Peak hours
                for minute in range(0, 60, 15):  # Every 15 minutes
                    cyclic_events.append(
                        CoordinationEvent(
                            event_type=CoordinationEventType.API_CALL_SUCCESS,
                            timestamp=base_time - timedelta(days=day, hours=hour, minutes=minute),
                            details={"api": "test"}
                        )
                    )

        patterns = pattern_recognizer.detect_cyclic_patterns(cyclic_events)

        assert len(patterns) > 0
        hourly_pattern = next(
            (p for p in patterns if p.pattern_type == PatternType.CYCLIC_HOURLY),
            None
        )
        assert hourly_pattern is not None
        assert hourly_pattern.confidence > 0.7

    def test_detect_burst_patterns(self, pattern_recognizer):
        """Test detection of burst patterns."""
        # Create burst pattern
        burst_events = []
        base_time = datetime.now()

        # Normal activity
        for i in range(10):
            burst_events.append(
                CoordinationEvent(
                    event_type=CoordinationEventType.TASK_COMPLETED,
                    timestamp=base_time - timedelta(minutes=i*10),
                    details={"task_id": f"normal_{i}"}
                )
            )

        # Burst activity
        for i in range(50):  # 50 events in 5 minutes
            burst_events.append(
                CoordinationEvent(
                    event_type=CoordinationEventType.TASK_COMPLETED,
                    timestamp=base_time - timedelta(seconds=i*6),  # Every 6 seconds
                    details={"task_id": f"burst_{i}"}
                )
            )

        patterns = pattern_recognizer.detect_burst_patterns(burst_events)

        assert len(patterns) > 0
        burst_pattern = next(
            (p for p in patterns if p.pattern_type == PatternType.BURST),
            None
        )
        assert burst_pattern is not None
        assert burst_pattern.confidence > 0.8


class TestPredictiveAnalyzer:
    """Test suite for PredictiveAnalyzer component."""

    @pytest.fixture
    def predictive_analyzer(self):
        """Create PredictiveAnalyzer instance for testing."""
        return PredictiveAnalyzer()

    @pytest.fixture
    def training_data(self):
        """Create training data for predictive models."""
        base_time = datetime.now()
        return [
            CoordinationMetrics(
                timestamp=base_time - timedelta(hours=i),
                active_tasks=100 + i*5,
                completed_tasks=1000 + i*50,
                failed_tasks=10 + i,
                queue_depth=50 + i*2,
                api_calls_count=500 + i*25,
                total_cost=Decimal(f"{50.00 + i*2.50:.2f}"),
                health_score=0.95 - i*0.01,
                event_id=f"training_{i}"
            )
            for i in range(48)  # 48 hours of training data
        ]

    def test_predict_cost_trajectory(self, predictive_analyzer, training_data):
        """Test cost trajectory prediction."""
        prediction = predictive_analyzer.predict_cost_trajectory(
            training_data,
            hours_ahead=6
        )

        assert prediction is not None
        assert len(prediction.predicted_values) == 6
        assert prediction.confidence != PredictionConfidence.UNKNOWN
        assert prediction.trend_direction in [
            TrendDirection.INCREASING,
            TrendDirection.DECREASING,
            TrendDirection.STABLE
        ]

    def test_predict_health_score(self, predictive_analyzer, training_data):
        """Test health score prediction."""
        prediction = predictive_analyzer.predict_health_score(
            training_data,
            hours_ahead=12
        )

        assert prediction is not None
        assert len(prediction.predicted_values) == 12
        assert all(0.0 <= score <= 1.0 for score in prediction.predicted_values)
        assert prediction.confidence != PredictionConfidence.UNKNOWN

    def test_predict_with_insufficient_data(self, predictive_analyzer):
        """Test prediction with insufficient training data."""
        sparse_data = [
            CoordinationMetrics(
                timestamp=datetime.now(),
                active_tasks=100,
                completed_tasks=500,
                failed_tasks=5,
                queue_depth=25,
                api_calls_count=200,
                total_cost=Decimal("10.50"),
                health_score=0.95,
                event_id="sparse_1"
            )
        ]

        prediction = predictive_analyzer.predict_cost_trajectory(sparse_data, hours_ahead=3)
        assert prediction.confidence == PredictionConfidence.LOW

    def test_identify_risk_periods(self, predictive_analyzer, training_data):
        """Test identification of risk periods."""
        # Add some failing metrics to create risk
        risky_data = training_data.copy()
        for i in range(5):
            risky_data.append(
                CoordinationMetrics(
                    timestamp=datetime.now() + timedelta(hours=i),
                    active_tasks=200,
                    completed_tasks=900,  # Lower completion rate
                    failed_tasks=50,  # High failure rate
                    queue_depth=100,
                    api_calls_count=800,
                    total_cost=Decimal("100.00"),  # High cost
                    health_score=0.6,  # Low health
                    event_id=f"risky_{i}"
                )
            )

        risks = predictive_analyzer.identify_risk_periods(risky_data, hours_ahead=24)

        assert len(risks) > 0
        assert any(risk.severity in [AnomalySeverity.HIGH, AnomalySeverity.CRITICAL] for risk in risks)


class TestInsightGenerator:
    """Test suite for InsightGenerator component."""

    @pytest.fixture
    def insight_generator(self):
        """Create InsightGenerator instance for testing."""
        return InsightGenerator()

    @pytest.fixture
    def sample_analytics_data(self):
        """Create sample analytics data."""
        return {
            'trends': [
                MagicMock(
                    direction=TrendDirection.INCREASING,
                    strength=0.8,
                    confidence=0.9,
                    metric_name='cost'
                )
            ],
            'patterns': [
                MagicMock(
                    pattern_type=PatternType.CYCLIC_DAILY,
                    confidence=0.85,
                    details={'peak_hours': [9, 13, 17]}
                )
            ],
            'predictions': [
                MagicMock(
                    predicted_values=[100, 105, 110, 115],
                    confidence=PredictionConfidence.HIGH,
                    metric_name='active_tasks'
                )
            ]
        }

    def test_generate_insights(self, insight_generator, sample_analytics_data):
        """Test insight generation from analytics data."""
        insights = insight_generator.generate_insights(sample_analytics_data)

        assert len(insights) > 0
        assert all(isinstance(insight, AnalyticsInsight) for insight in insights)

        # Should have insights for trends, patterns, and predictions
        insight_types = [insight.insight_type for insight in insights]
        assert 'trend' in insight_types
        assert 'pattern' in insight_types

    def test_generate_performance_insights(self, insight_generator):
        """Test performance-specific insights."""
        performance_metrics = {
            'avg_task_duration_ms': 1500,
            'error_rate': 0.05,
            'throughput_per_minute': 50,
            'queue_depth_trend': TrendDirection.INCREASING
        }

        insights = insight_generator.generate_performance_insights(performance_metrics)

        assert len(insights) > 0
        performance_insight = next(
            (i for i in insights if 'performance' in i.title.lower()),
            None
        )
        assert performance_insight is not None

    def test_generate_cost_insights(self, insight_generator):
        """Test cost-specific insights."""
        cost_data = {
            'daily_cost': Decimal('125.50'),
            'cost_trend': TrendDirection.INCREASING,
            'cost_per_api_call': Decimal('0.025'),
            'projected_monthly_cost': Decimal('3765.00')
        }

        insights = insight_generator.generate_cost_insights(cost_data)

        assert len(insights) > 0
        cost_insight = next(
            (i for i in insights if 'cost' in i.title.lower()),
            None
        )
        assert cost_insight is not None
        assert 'cost' in cost_insight.description.lower()

    def test_prioritize_insights(self, insight_generator):
        """Test insight prioritization based on importance."""
        insights = [
            AnalyticsInsight(
                insight_type='trend',
                title='Minor Cost Increase',
                description='Small upward trend in costs',
                importance_score=0.3,
                actionable=True,
                timestamp=datetime.now()
            ),
            AnalyticsInsight(
                insight_type='anomaly',
                title='Critical Health Drop',
                description='System health dropped significantly',
                importance_score=0.9,
                actionable=True,
                timestamp=datetime.now()
            ),
            AnalyticsInsight(
                insight_type='pattern',
                title='Daily Usage Pattern',
                description='Consistent daily usage pattern detected',
                importance_score=0.6,
                actionable=False,
                timestamp=datetime.now()
            )
        ]

        prioritized = insight_generator.prioritize_insights(insights)

        assert len(prioritized) == 3
        assert prioritized[0].importance_score >= prioritized[1].importance_score
        assert prioritized[1].importance_score >= prioritized[2].importance_score

        # Most important should be the critical health drop
        assert prioritized[0].title == 'Critical Health Drop'


class TestObservatoryAnalyticsEngine:
    """Test suite for the main ObservatoryAnalyticsEngine."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ObservatoryConfig(
            redis_host="localhost",
            redis_port=6379,
            enable_real_time=True,
            metrics_retention_hours=24,
            enable_achievements=True
        )

    @pytest.fixture
    def analytics_engine(self, config):
        """Create ObservatoryAnalyticsEngine instance for testing."""
        return ObservatoryAnalyticsEngine(config)

    def test_engine_initialization(self, analytics_engine):
        """Test analytics engine initialization."""
        assert analytics_engine is not None
        assert hasattr(analytics_engine, 'trend_analyzer')
        assert hasattr(analytics_engine, 'pattern_recognizer')
        assert hasattr(analytics_engine, 'predictive_analyzer')
        assert hasattr(analytics_engine, 'insight_generator')

    @pytest.mark.asyncio
    async def test_analyze_coordination_metrics(self, analytics_engine):
        """Test comprehensive metrics analysis."""
        # Create test metrics
        test_metrics = [
            CoordinationMetrics(
                timestamp=datetime.now() - timedelta(hours=i),
                active_tasks=100 + i*10,
                completed_tasks=500 + i*20,
                failed_tasks=5 + i,
                queue_depth=50 - i*2,
                api_calls_count=200 + i*15,
                total_cost=Decimal(f"{25.50 + i*1.25:.2f}"),
                health_score=0.95 - i*0.01,
                event_id=f"test_metric_{i}"
            )
            for i in range(24)  # 24 hours of data
        ]

        analysis_result = await analytics_engine.analyze_coordination_metrics(test_metrics)

        assert analysis_result is not None
        assert 'trends' in analysis_result
        assert 'patterns' in analysis_result
        assert 'predictions' in analysis_result
        assert 'insights' in analysis_result

        # Should have insights
        assert len(analysis_result['insights']) > 0

    @pytest.mark.asyncio
    async def test_real_time_analysis(self, analytics_engine):
        """Test real-time analysis capabilities."""
        # Mock real-time event
        event = CoordinationEvent(
            event_type=CoordinationEventType.COST_THRESHOLD_REACHED,
            timestamp=datetime.now(),
            details={
                'threshold': 100.00,
                'current_cost': 125.50,
                'alert_level': 'WARNING'
            }
        )

        # Mock the internal methods
        with patch.object(analytics_engine, '_analyze_event_impact') as mock_analyze:
            mock_analyze.return_value = {
                'immediate_impact': 'HIGH',
                'recommended_actions': ['Review cost optimization'],
                'urgency': 'MEDIUM'
            }

            result = await analytics_engine.process_real_time_event(event)

            assert result is not None
            assert 'immediate_impact' in result
            mock_analyze.assert_called_once_with(event)

    @pytest.mark.asyncio
    async def test_generate_comprehensive_report(self, analytics_engine):
        """Test comprehensive analytics report generation."""
        # Mock data
        with patch.object(analytics_engine, 'analyze_coordination_metrics') as mock_analyze:
            mock_analyze.return_value = {
                'trends': [],
                'patterns': [],
                'predictions': [],
                'insights': []
            }

            with patch.object(analytics_engine, '_fetch_recent_metrics') as mock_fetch:
                mock_fetch.return_value = []

                report = await analytics_engine.generate_comprehensive_report(
                    time_window=MetricsTimeWindow.DAY_1
                )

                assert report is not None
                assert 'summary' in report
                assert 'trends' in report
                assert 'patterns' in report
                assert 'predictions' in report
                assert 'recommendations' in report

    def test_get_analytics_status(self, analytics_engine):
        """Test analytics engine status reporting."""
        status = analytics_engine.get_analytics_status()

        assert status is not None
        assert 'analyzer_status' in status
        assert 'last_analysis_time' in status
        assert 'analysis_count' in status
        assert 'engine_health' in status

    @pytest.mark.asyncio
    async def test_error_handling_in_analysis(self, analytics_engine):
        """Test error handling during analysis operations."""
        # Test with invalid data
        invalid_metrics = [None, "invalid", 123]

        with patch.object(analytics_engine.trend_analyzer, 'analyze_trend') as mock_analyze:
            mock_analyze.side_effect = ValueError("Invalid data")

            # Should handle errors gracefully
            try:
                result = await analytics_engine.analyze_coordination_metrics(invalid_metrics)
                # Should return empty result rather than crash
                assert result is not None
            except ValueError:
                pytest.fail("Analytics engine should handle errors gracefully")

    @pytest.mark.asyncio
    async def test_concurrent_analysis(self, analytics_engine):
        """Test concurrent analysis operations."""
        # Create multiple analysis tasks
        tasks = []
        for i in range(5):
            metrics = [
                CoordinationMetrics(
                    timestamp=datetime.now(),
                    active_tasks=100,
                    completed_tasks=500,
                    failed_tasks=5,
                    queue_depth=25,
                    api_calls_count=200,
                    total_cost=Decimal("25.50"),
                    health_score=0.95,
                    event_id=f"concurrent_{i}"
                )
            ]
            tasks.append(analytics_engine.analyze_coordination_metrics(metrics))

        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should complete successfully
        assert len(results) == 5
        assert all(not isinstance(r, Exception) for r in results)