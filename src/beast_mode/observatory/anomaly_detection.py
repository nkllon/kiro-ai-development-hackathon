"""
Anomaly Detection Engine - Detects unusual patterns in coordination behavior, costs, and performance.

This module provides comprehensive anomaly detection using both statistical methods and machine learning
to identify and classify unusual system behavior patterns before they impact coordination effectiveness.
"""

import asyncio
import json
import logging
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Deque, Tuple
from uuid import uuid4
from enum import Enum

import redis.asyncio as redis
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from ..core import ReflectiveModule
from .models import (
    CoordinationMetrics,
    CostMetrics,
    CoordinationEvent,
    CoordinationEventType,
)
from .config import ObservatoryConfig


logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Types of anomalies that can be detected."""
    COORDINATION_HEALTH = "coordination_health"
    COST_SPIKE = "cost_spike"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    ERROR_RATE_INCREASE = "error_rate_increase"
    RESPONSE_TIME_ANOMALY = "response_time_anomaly"
    USAGE_PATTERN_ANOMALY = "usage_pattern_anomaly"
    COMPONENT_FAILURE = "component_failure"


class AnomalySeverity(Enum):
    """Severity levels for anomalies."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Baseline:
    """Baseline statistics for normal system operation."""
    metric_name: str
    mean: float
    std_dev: float
    percentile_95: float
    percentile_99: float
    sample_count: int
    last_updated: datetime = field(default_factory=datetime.now)

    def calculate_z_score(self, value: float) -> float:
        """Calculate z-score for a value against this baseline."""
        if self.std_dev == 0:
            return 0.0
        return (value - self.mean) / self.std_dev

    def is_outlier(self, value: float, threshold: float = 2.0) -> bool:
        """Check if a value is an outlier based on z-score."""
        return abs(self.calculate_z_score(value)) > threshold


@dataclass
class Anomaly:
    """Detected anomaly in system behavior."""
    anomaly_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    anomaly_type: AnomalyType = AnomalyType.COORDINATION_HEALTH
    severity: AnomalySeverity = AnomalySeverity.MEDIUM
    affected_components: List[str] = field(default_factory=list)
    description: str = ""
    confidence_score: float = 0.8
    suggested_actions: List[str] = field(default_factory=list)
    data_points: Dict[str, Any] = field(default_factory=dict)
    baseline_deviation: float = 0.0
    auto_resolved: bool = False


@dataclass
class AnomalyClassification:
    """Classification result for an anomaly."""
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    confidence: float
    reasoning: str
    suggested_actions: List[str]


class BaselineCalculator:
    """Calculates and maintains baseline statistics from historical data."""

    def __init__(self):
        self._baselines: Dict[str, Baseline] = {}
        self._historical_data: Dict[str, Deque[float]] = defaultdict(lambda: deque(maxlen=1000))
        self._update_frequency_hours = 6  # Update baselines every 6 hours
        self._last_update = {}

    def add_data_point(self, metric_name: str, value: float) -> None:
        """Add a data point for baseline calculation."""
        try:
            self._historical_data[metric_name].append(value)

            # Update baseline if enough time has passed or if we don't have one
            if (metric_name not in self._last_update or
                datetime.now() - self._last_update[metric_name] > timedelta(hours=self._update_frequency_hours)):
                self._update_baseline(metric_name)

        except Exception as e:
            logger.error(f"Error adding data point for {metric_name}: {e}")

    def _update_baseline(self, metric_name: str) -> None:
        """Update baseline for a specific metric."""
        try:
            data = list(self._historical_data[metric_name])
            if len(data) < 10:  # Need at least 10 data points
                return

            mean_val = statistics.mean(data)
            std_dev = statistics.stdev(data) if len(data) > 1 else 0.0
            percentile_95 = np.percentile(data, 95)
            percentile_99 = np.percentile(data, 99)

            baseline = Baseline(
                metric_name=metric_name,
                mean=mean_val,
                std_dev=std_dev,
                percentile_95=float(percentile_95),
                percentile_99=float(percentile_99),
                sample_count=len(data),
                last_updated=datetime.now()
            )

            self._baselines[metric_name] = baseline
            self._last_update[metric_name] = datetime.now()

            logger.debug(f"Updated baseline for {metric_name}: mean={mean_val:.3f}, std={std_dev:.3f}")

        except Exception as e:
            logger.error(f"Error updating baseline for {metric_name}: {e}")

    def get_baseline(self, metric_name: str) -> Optional[Baseline]:
        """Get baseline for a metric."""
        return self._baselines.get(metric_name)

    def get_all_baselines(self) -> Dict[str, Baseline]:
        """Get all current baselines."""
        return self._baselines.copy()


class ThresholdAnomalyDetector:
    """Threshold-based anomaly detection for immediate alerts."""

    def __init__(self, baseline_calculator: BaselineCalculator):
        self._baseline_calculator = baseline_calculator

        # Configurable thresholds
        self._thresholds = {
            "coordination_health_score": {"min": 0.7, "critical_min": 0.5},
            "error_rate_percent": {"max": 10.0, "critical_max": 25.0},
            "avg_response_time_ms": {"max": 5000.0, "critical_max": 10000.0},
            "cost_per_call": {"max": 0.05, "critical_max": 0.10},
            "z_score": {"threshold": 2.0, "critical_threshold": 3.0}
        }

    def detect_anomalies(self, metrics: Dict[str, float]) -> List[Anomaly]:
        """Detect anomalies using threshold-based rules."""
        anomalies = []

        try:
            # Check coordination health
            if "coordination_health_score" in metrics:
                health_score = metrics["coordination_health_score"]
                if health_score < self._thresholds["coordination_health_score"]["critical_min"]:
                    anomalies.append(self._create_health_anomaly(health_score, AnomalySeverity.CRITICAL))
                elif health_score < self._thresholds["coordination_health_score"]["min"]:
                    anomalies.append(self._create_health_anomaly(health_score, AnomalySeverity.HIGH))

            # Check error rate
            if "error_rate_percent" in metrics:
                error_rate = metrics["error_rate_percent"]
                if error_rate > self._thresholds["error_rate_percent"]["critical_max"]:
                    anomalies.append(self._create_error_rate_anomaly(error_rate, AnomalySeverity.CRITICAL))
                elif error_rate > self._thresholds["error_rate_percent"]["max"]:
                    anomalies.append(self._create_error_rate_anomaly(error_rate, AnomalySeverity.HIGH))

            # Check response time
            if "avg_response_time_ms" in metrics:
                response_time = metrics["avg_response_time_ms"]
                if response_time > self._thresholds["avg_response_time_ms"]["critical_max"]:
                    anomalies.append(self._create_response_time_anomaly(response_time, AnomalySeverity.CRITICAL))
                elif response_time > self._thresholds["avg_response_time_ms"]["max"]:
                    anomalies.append(self._create_response_time_anomaly(response_time, AnomalySeverity.HIGH))

            # Check cost per call
            if "avg_cost_per_call" in metrics:
                cost_per_call = metrics["avg_cost_per_call"]
                if cost_per_call > self._thresholds["cost_per_call"]["critical_max"]:
                    anomalies.append(self._create_cost_anomaly(cost_per_call, AnomalySeverity.CRITICAL))
                elif cost_per_call > self._thresholds["cost_per_call"]["max"]:
                    anomalies.append(self._create_cost_anomaly(cost_per_call, AnomalySeverity.HIGH))

            # Check baseline deviations
            for metric_name, value in metrics.items():
                baseline = self._baseline_calculator.get_baseline(metric_name)
                if baseline and baseline.sample_count > 10:
                    z_score = abs(baseline.calculate_z_score(value))

                    if z_score > self._thresholds["z_score"]["critical_threshold"]:
                        anomalies.append(self._create_baseline_anomaly(
                            metric_name, value, baseline, z_score, AnomalySeverity.CRITICAL
                        ))
                    elif z_score > self._thresholds["z_score"]["threshold"]:
                        anomalies.append(self._create_baseline_anomaly(
                            metric_name, value, baseline, z_score, AnomalySeverity.MEDIUM
                        ))

        except Exception as e:
            logger.error(f"Error in threshold anomaly detection: {e}")

        return anomalies

    def _create_health_anomaly(self, health_score: float, severity: AnomalySeverity) -> Anomaly:
        """Create coordination health anomaly."""
        return Anomaly(
            anomaly_type=AnomalyType.COORDINATION_HEALTH,
            severity=severity,
            description=f"Coordination health score dropped to {health_score:.2f}",
            confidence_score=0.95,
            suggested_actions=[
                "Review component logs for errors",
                "Check network connectivity between components",
                "Investigate recent configuration changes"
            ],
            data_points={"health_score": health_score}
        )

    def _create_error_rate_anomaly(self, error_rate: float, severity: AnomalySeverity) -> Anomaly:
        """Create error rate anomaly."""
        return Anomaly(
            anomaly_type=AnomalyType.ERROR_RATE_INCREASE,
            severity=severity,
            description=f"Error rate increased to {error_rate:.1f}%",
            confidence_score=0.90,
            suggested_actions=[
                "Check API service status",
                "Review recent deployments",
                "Implement retry logic if not present"
            ],
            data_points={"error_rate_percent": error_rate}
        )

    def _create_response_time_anomaly(self, response_time: float, severity: AnomalySeverity) -> Anomaly:
        """Create response time anomaly."""
        return Anomaly(
            anomaly_type=AnomalyType.RESPONSE_TIME_ANOMALY,
            severity=severity,
            description=f"Average response time increased to {response_time:.0f}ms",
            confidence_score=0.85,
            suggested_actions=[
                "Check system resource usage",
                "Review database query performance",
                "Consider scaling up resources"
            ],
            data_points={"avg_response_time_ms": response_time}
        )

    def _create_cost_anomaly(self, cost_per_call: float, severity: AnomalySeverity) -> Anomaly:
        """Create cost anomaly."""
        return Anomaly(
            anomaly_type=AnomalyType.COST_SPIKE,
            severity=severity,
            description=f"Average cost per call increased to ${cost_per_call:.4f}",
            confidence_score=0.88,
            suggested_actions=[
                "Review model selection strategy",
                "Optimize prompt efficiency",
                "Consider using cheaper models for simple tasks"
            ],
            data_points={"avg_cost_per_call": cost_per_call}
        )

    def _create_baseline_anomaly(self, metric_name: str, value: float, baseline: Baseline,
                                z_score: float, severity: AnomalySeverity) -> Anomaly:
        """Create baseline deviation anomaly."""
        return Anomaly(
            anomaly_type=AnomalyType.USAGE_PATTERN_ANOMALY,
            severity=severity,
            description=f"{metric_name} deviated significantly from baseline (z-score: {z_score:.2f})",
            confidence_score=min(0.95, 0.5 + (z_score / 10.0)),  # Higher z-score = higher confidence
            suggested_actions=[
                f"Investigate recent changes affecting {metric_name}",
                "Check for external factors influencing system behavior",
                "Consider updating baseline if this represents new normal"
            ],
            data_points={
                "metric_name": metric_name,
                "current_value": value,
                "baseline_mean": baseline.mean,
                "z_score": z_score
            },
            baseline_deviation=z_score
        )


class MLAnomalyDetector:
    """Machine learning-based anomaly detection using isolation forests."""

    def __init__(self):
        self._model = IsolationForest(
            contamination=0.1,  # Assume 10% of data points are anomalies
            random_state=42,
            n_estimators=100
        )
        self._scaler = StandardScaler()
        self._feature_names: List[str] = []
        self._is_trained = False
        self._training_data: List[List[float]] = []
        self._min_training_samples = 100

    async def add_training_data(self, features: Dict[str, float]) -> None:
        """Add training data for ML model."""
        try:
            if not self._feature_names:
                self._feature_names = list(features.keys())

            # Ensure consistent feature order
            feature_vector = [features.get(name, 0.0) for name in self._feature_names]
            self._training_data.append(feature_vector)

            # Retrain if we have enough data and every 100 new samples
            if (len(self._training_data) >= self._min_training_samples and
                len(self._training_data) % 100 == 0):
                await self._retrain_model()

        except Exception as e:
            logger.error(f"Error adding training data: {e}")

    async def _retrain_model(self) -> None:
        """Retrain the ML model with accumulated data."""
        try:
            if len(self._training_data) < self._min_training_samples:
                return

            # Use only recent data to avoid concept drift
            recent_data = self._training_data[-1000:]  # Last 1000 samples

            # Scale the data
            X_scaled = self._scaler.fit_transform(recent_data)

            # Train the model
            self._model.fit(X_scaled)
            self._is_trained = True

            logger.info(f"ML anomaly detection model retrained with {len(recent_data)} samples")

        except Exception as e:
            logger.error(f"Error retraining ML model: {e}")

    def detect_anomalies(self, features: Dict[str, float]) -> List[Anomaly]:
        """Detect anomalies using ML model."""
        if not self._is_trained or not self._feature_names:
            return []

        try:
            # Prepare feature vector
            feature_vector = [features.get(name, 0.0) for name in self._feature_names]
            X_scaled = self._scaler.transform([feature_vector])

            # Predict anomaly
            anomaly_score = self._model.decision_function(X_scaled)[0]
            is_anomaly = self._model.predict(X_scaled)[0] == -1

            if is_anomaly:
                # Convert anomaly score to confidence (more negative = more anomalous)
                confidence = min(0.95, max(0.6, 1.0 - (anomaly_score + 1.0) / 2.0))

                # Determine severity based on anomaly score
                if anomaly_score < -0.5:
                    severity = AnomalySeverity.CRITICAL
                elif anomaly_score < -0.3:
                    severity = AnomalySeverity.HIGH
                else:
                    severity = AnomalySeverity.MEDIUM

                anomaly = Anomaly(
                    anomaly_type=AnomalyType.USAGE_PATTERN_ANOMALY,
                    severity=severity,
                    description=f"ML model detected unusual pattern (anomaly score: {anomaly_score:.3f})",
                    confidence_score=confidence,
                    suggested_actions=[
                        "Investigate recent system changes",
                        "Check for unusual workload patterns",
                        "Review system logs for errors or warnings"
                    ],
                    data_points={
                        "anomaly_score": anomaly_score,
                        "features": features,
                        "feature_names": self._feature_names
                    }
                )

                return [anomaly]

        except Exception as e:
            logger.error(f"Error in ML anomaly detection: {e}")

        return []


class AnomalyClassifier:
    """Classifies and scores anomaly severity."""

    def classify_anomaly(self, anomaly_data: Dict[str, Any]) -> AnomalyClassification:
        """Classify an anomaly and determine its severity."""
        try:
            # Analyze the type of anomaly based on affected metrics
            anomaly_type = self._determine_anomaly_type(anomaly_data)
            severity = self._calculate_severity(anomaly_data, anomaly_type)
            confidence = self._calculate_confidence(anomaly_data, anomaly_type)
            reasoning = self._generate_reasoning(anomaly_data, anomaly_type)
            actions = self._suggest_actions(anomaly_type, severity)

            return AnomalyClassification(
                anomaly_type=anomaly_type,
                severity=severity,
                confidence=confidence,
                reasoning=reasoning,
                suggested_actions=actions
            )

        except Exception as e:
            logger.error(f"Error classifying anomaly: {e}")
            return AnomalyClassification(
                anomaly_type=AnomalyType.USAGE_PATTERN_ANOMALY,
                severity=AnomalySeverity.MEDIUM,
                confidence=0.5,
                reasoning="Error in classification",
                suggested_actions=["Investigate manually"]
            )

    def _determine_anomaly_type(self, data: Dict[str, Any]) -> AnomalyType:
        """Determine the type of anomaly based on data."""
        if "coordination_health_score" in data and data["coordination_health_score"] < 0.7:
            return AnomalyType.COORDINATION_HEALTH
        elif "error_rate_percent" in data and data["error_rate_percent"] > 10:
            return AnomalyType.ERROR_RATE_INCREASE
        elif "avg_response_time_ms" in data and data["avg_response_time_ms"] > 5000:
            return AnomalyType.RESPONSE_TIME_ANOMALY
        elif "avg_cost_per_call" in data and data["avg_cost_per_call"] > 0.05:
            return AnomalyType.COST_SPIKE
        else:
            return AnomalyType.USAGE_PATTERN_ANOMALY

    def _calculate_severity(self, data: Dict[str, Any], anomaly_type: AnomalyType) -> AnomalySeverity:
        """Calculate severity based on anomaly type and data."""
        if anomaly_type == AnomalyType.COORDINATION_HEALTH:
            health_score = data.get("coordination_health_score", 1.0)
            if health_score < 0.3:
                return AnomalySeverity.CRITICAL
            elif health_score < 0.5:
                return AnomalySeverity.HIGH
            elif health_score < 0.7:
                return AnomalySeverity.MEDIUM
            else:
                return AnomalySeverity.LOW

        elif anomaly_type == AnomalyType.ERROR_RATE_INCREASE:
            error_rate = data.get("error_rate_percent", 0.0)
            if error_rate > 50:
                return AnomalySeverity.CRITICAL
            elif error_rate > 25:
                return AnomalySeverity.HIGH
            elif error_rate > 10:
                return AnomalySeverity.MEDIUM
            else:
                return AnomalySeverity.LOW

        # Default to medium severity
        return AnomalySeverity.MEDIUM

    def _calculate_confidence(self, data: Dict[str, Any], anomaly_type: AnomalyType) -> float:
        """Calculate confidence score for the classification."""
        # Base confidence based on data completeness
        base_confidence = 0.7

        # Increase confidence if we have baseline data
        if "z_score" in data:
            z_score = abs(data["z_score"])
            base_confidence += min(0.2, z_score / 10.0)

        # Increase confidence for clear threshold violations
        if anomaly_type in [AnomalyType.COORDINATION_HEALTH, AnomalyType.ERROR_RATE_INCREASE]:
            base_confidence += 0.1

        return min(0.95, base_confidence)

    def _generate_reasoning(self, data: Dict[str, Any], anomaly_type: AnomalyType) -> str:
        """Generate human-readable reasoning for the classification."""
        reasons = []

        if anomaly_type == AnomalyType.COORDINATION_HEALTH:
            health_score = data.get("coordination_health_score", 1.0)
            reasons.append(f"Coordination health dropped to {health_score:.2f}")

        if "z_score" in data:
            z_score = data["z_score"]
            reasons.append(f"Metric deviated {z_score:.1f} standard deviations from baseline")

        if "error_rate_percent" in data:
            error_rate = data["error_rate_percent"]
            reasons.append(f"Error rate increased to {error_rate:.1f}%")

        return "; ".join(reasons) if reasons else "Unusual pattern detected in system metrics"

    def _suggest_actions(self, anomaly_type: AnomalyType, severity: AnomalySeverity) -> List[str]:
        """Suggest actions based on anomaly type and severity."""
        actions = []

        if anomaly_type == AnomalyType.COORDINATION_HEALTH:
            actions.extend([
                "Review component health status",
                "Check network connectivity",
                "Investigate recent configuration changes"
            ])
        elif anomaly_type == AnomalyType.ERROR_RATE_INCREASE:
            actions.extend([
                "Check API service status",
                "Review error logs",
                "Implement circuit breaker if needed"
            ])
        elif anomaly_type == AnomalyType.COST_SPIKE:
            actions.extend([
                "Review model usage patterns",
                "Optimize prompt efficiency",
                "Consider cost-effective alternatives"
            ])

        if severity in [AnomalySeverity.HIGH, AnomalySeverity.CRITICAL]:
            actions.insert(0, "Alert operations team immediately")

        return actions


class AnomalyDetectionEngine(ReflectiveModule):
    """Advanced anomaly detection for coordination and cost metrics."""

    def __init__(self, config: ObservatoryConfig):
        super().__init__()
        self.module_id = "anomaly_detection_engine"
        self._config = config
        self._redis_client: Optional[redis.Redis] = None
        self._running = False
        self._detection_task: Optional[asyncio.Task] = None

        # Initialize components
        self._baseline_calculator = BaselineCalculator()
        self._threshold_detector = ThresholdAnomalyDetector(self._baseline_calculator)
        self._ml_detector = MLAnomalyDetector() if config.anomaly_config.enable_ml else None
        self._classifier = AnomalyClassifier()

        # Anomaly storage
        self._active_anomalies: Deque[Anomaly] = deque(maxlen=100)
        self._resolved_anomalies: Deque[Anomaly] = deque(maxlen=200)

        # Performance tracking
        self._start_time = time.time()
        self._anomalies_detected = 0
        self._false_positives = 0
        self._detection_errors = 0

        logger.info("🔍 AnomalyDetectionEngine initialized - Ready to detect the unusual")

    async def start_detection(self) -> bool:
        """Start anomaly detection processing."""
        try:
            if self._running:
                logger.warning("AnomalyDetectionEngine is already running")
                return True

            # Connect to Redis
            await self._connect_redis()

            # Start detection task
            self._running = True
            self._detection_task = asyncio.create_task(self._detection_loop())

            logger.info("🚀 AnomalyDetectionEngine started - watching for anomalies")
            return True

        except Exception as e:
            logger.error(f"Failed to start AnomalyDetectionEngine: {e}")
            return False

    async def stop_detection(self) -> None:
        """Stop anomaly detection gracefully."""
        logger.info("🛑 Stopping AnomalyDetectionEngine...")

        self._running = False

        # Cancel detection task
        if self._detection_task and not self._detection_task.done():
            self._detection_task.cancel()
            try:
                await self._detection_task
            except asyncio.CancelledError:
                pass

        # Close Redis connection
        if self._redis_client:
            await self._redis_client.close()

        logger.info("✅ AnomalyDetectionEngine stopped gracefully")

    async def _connect_redis(self) -> None:
        """Connect to Redis for data streaming."""
        try:
            self._redis_client = redis.Redis(
                host=self._config.redis_config.host,
                port=self._config.redis_config.port,
                password=self._config.redis_config.password,
                ssl=self._config.redis_config.ssl,
                decode_responses=True
            )

            # Test connection
            await self._redis_client.ping()
            logger.info("📡 AnomalyDetectionEngine connected to Redis")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def _detection_loop(self) -> None:
        """Main anomaly detection loop."""
        logger.info("🔍 Starting anomaly detection loop")

        while self._running:
            try:
                # Get current metrics from analytics engine
                await self._process_current_metrics()

                # Check for resolved anomalies
                await self._check_resolved_anomalies()

                # Sleep for detection interval
                await asyncio.sleep(self._config.anomaly_config.detection_interval_seconds)

            except asyncio.CancelledError:
                logger.info("Anomaly detection loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in anomaly detection loop: {e}")
                self._detection_errors += 1
                await asyncio.sleep(1)  # Brief pause on error

        logger.info("Anomaly detection loop stopped")

    async def _process_current_metrics(self) -> None:
        """Process current metrics for anomaly detection."""
        try:
            if not self._redis_client:
                return

            # Get metrics from analytics stream
            stream_name = f"{self._config.redis_config.stream_name}:analytics"

            try:
                entries = await self._redis_client.xread({stream_name: '$'}, count=1, block=100)

                for stream, messages in entries:
                    for message_id, fields in messages:
                        await self._analyze_metrics(fields)

            except Exception as e:
                logger.debug(f"No new analytics data: {e}")

        except Exception as e:
            logger.error(f"Error processing current metrics: {e}")

    async def _analyze_metrics(self, metrics_data: Dict[str, str]) -> None:
        """Analyze metrics for anomalies."""
        try:
            # Convert string metrics to float
            metrics = {}
            for key, value in metrics_data.items():
                try:
                    if key.endswith("_score") or key.endswith("_percent") or key.endswith("_ms") or key.endswith("_cost"):
                        metrics[key] = float(value)
                except (ValueError, TypeError):
                    continue

            if not metrics:
                return

            # Add data points to baseline calculator
            for metric_name, value in metrics.items():
                self._baseline_calculator.add_data_point(metric_name, value)

            # Detect anomalies using threshold detector
            threshold_anomalies = self._threshold_detector.detect_anomalies(metrics)

            # Detect anomalies using ML detector if available
            ml_anomalies = []
            if self._ml_detector:
                await self._ml_detector.add_training_data(metrics)
                ml_anomalies = self._ml_detector.detect_anomalies(metrics)

            # Process all detected anomalies
            all_anomalies = threshold_anomalies + ml_anomalies

            for anomaly in all_anomalies:
                await self._process_new_anomaly(anomaly)

        except Exception as e:
            logger.error(f"Error analyzing metrics: {e}")

    async def _process_new_anomaly(self, anomaly: Anomaly) -> None:
        """Process a newly detected anomaly."""
        try:
            # Check if similar anomaly already exists
            if self._is_duplicate_anomaly(anomaly):
                return

            # Add to active anomalies
            self._active_anomalies.append(anomaly)
            self._anomalies_detected += 1

            # Log the anomaly
            logger.warning(f"🚨 Anomaly detected: {anomaly.anomaly_type.value} - {anomaly.description}")

            # Store in Redis for real-time updates
            await self._store_anomaly_in_redis(anomaly)

        except Exception as e:
            logger.error(f"Error processing new anomaly: {e}")

    def _is_duplicate_anomaly(self, new_anomaly: Anomaly) -> bool:
        """Check if a similar anomaly already exists."""
        for existing in self._active_anomalies:
            if (existing.anomaly_type == new_anomaly.anomaly_type and
                existing.severity == new_anomaly.severity and
                (datetime.now() - existing.timestamp) < timedelta(minutes=15)):
                return True
        return False

    async def _store_anomaly_in_redis(self, anomaly: Anomaly) -> None:
        """Store anomaly in Redis for real-time access."""
        try:
            if not self._redis_client:
                return

            anomaly_data = {
                "anomaly_id": anomaly.anomaly_id,
                "timestamp": anomaly.timestamp.isoformat(),
                "anomaly_type": anomaly.anomaly_type.value,
                "severity": anomaly.severity.value,
                "description": anomaly.description,
                "confidence_score": str(anomaly.confidence_score),
                "suggested_actions": json.dumps(anomaly.suggested_actions),
                "data_points": json.dumps(anomaly.data_points)
            }

            stream_name = f"{self._config.redis_config.stream_name}:anomalies"
            await self._redis_client.xadd(stream_name, anomaly_data)

        except Exception as e:
            logger.error(f"Error storing anomaly in Redis: {e}")

    async def _check_resolved_anomalies(self) -> None:
        """Check if any anomalies have been resolved."""
        try:
            resolved_indices = []

            for i, anomaly in enumerate(self._active_anomalies):
                # Check if anomaly is older than resolution timeout
                if (datetime.now() - anomaly.timestamp) > timedelta(hours=1):
                    anomaly.auto_resolved = True
                    self._resolved_anomalies.append(anomaly)
                    resolved_indices.append(i)
                    logger.info(f"✅ Auto-resolved anomaly: {anomaly.anomaly_id}")

            # Remove resolved anomalies (in reverse order to maintain indices)
            for i in reversed(resolved_indices):
                del self._active_anomalies[i]

        except Exception as e:
            logger.error(f"Error checking resolved anomalies: {e}")

    def get_active_anomalies(self) -> List[Dict[str, Any]]:
        """Get currently active anomalies."""
        try:
            return [
                {
                    "anomaly_id": anomaly.anomaly_id,
                    "timestamp": anomaly.timestamp.isoformat(),
                    "anomaly_type": anomaly.anomaly_type.value,
                    "severity": anomaly.severity.value,
                    "description": anomaly.description,
                    "confidence_score": anomaly.confidence_score,
                    "suggested_actions": anomaly.suggested_actions,
                    "data_points": anomaly.data_points,
                    "baseline_deviation": anomaly.baseline_deviation
                }
                for anomaly in self._active_anomalies
            ]
        except Exception as e:
            logger.error(f"Error getting active anomalies: {e}")
            return []

    def get_anomaly_stats(self) -> Dict[str, Any]:
        """Get anomaly detection statistics."""
        uptime = time.time() - self._start_time

        return {
            "uptime_seconds": uptime,
            "anomalies_detected": self._anomalies_detected,
            "active_anomalies": len(self._active_anomalies),
            "resolved_anomalies": len(self._resolved_anomalies),
            "detection_errors": self._detection_errors,
            "detection_rate_per_hour": (self._anomalies_detected / (uptime / 3600)) if uptime > 0 else 0,
            "ml_detection_enabled": self._ml_detector is not None,
            "baseline_metrics": len(self._baseline_calculator.get_all_baselines())
        }

    # ReflectiveModule implementation

    def get_capabilities(self) -> List['ModuleCapability']:
        """Get AnomalyDetectionEngine capabilities."""
        from src.rm_ddd.core.unified_reflective_module import ModuleCapability
        return [
            ModuleCapability.MONITORING,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.ANALYTICS,
        ]

    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": self.module_id,
            "name": "Anomaly Detection Engine",
            "version": "1.0.0",
            "description": "Detects unusual patterns in coordination behavior and performance",
            "config": {
                "detection_interval_seconds": self._config.anomaly_config.detection_interval_seconds,
                "ml_detection_enabled": self._ml_detector is not None,
                "max_active_anomalies": 100,
                "max_resolved_anomalies": 200
            }
        }

    def get_health_status(self) -> 'ModuleHealth':
        """Get health status of the AnomalyDetectionEngine."""
        from src.rm_ddd.core.unified_reflective_module import ModuleHealth, ModuleStatus

        if not self._running:
            status = ModuleStatus.ERROR
            health_score = 0.0
            issues = ["AnomalyDetectionEngine is not running"]
        else:
            # Check detection health
            uptime = time.time() - self._start_time
            error_rate = (self._detection_errors / max(1, self._anomalies_detected)) * 100 if self._anomalies_detected > 0 else 0

            if error_rate > 20:
                status = ModuleStatus.ERROR
                health_score = 0.3
                issues = [f"High detection error rate: {error_rate:.1f}%"]
            elif error_rate > 10:
                status = ModuleStatus.WARNING
                health_score = 0.7
                issues = [f"Elevated detection error rate: {error_rate:.1f}%"]
            elif uptime > 60 or self._anomalies_detected > 0:  # Allow 1 minute warmup
                status = ModuleStatus.HEALTHY
                health_score = 1.0
                issues = []
            else:
                status = ModuleStatus.WARNING
                health_score = 0.8
                issues = ["Anomaly detection warming up"]

        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=time.time() - self._start_time,
            error_count=self._detection_errors,
            warning_count=len([a for a in self._active_anomalies if a.severity == AnomalySeverity.HIGH])
        )

    def graceful_degradation(self) -> 'GracefulDegradationResult':
        """Perform graceful degradation of anomaly detection functionality."""
        from src.rm_ddd.core.unified_reflective_module import (
            GracefulDegradationResult,
            ModuleCapability
        )

        try:
            # In degraded mode, we can still detect threshold-based anomalies
            degraded_capabilities = []
            remaining_capabilities = [
                ModuleCapability.MONITORING,
                ModuleCapability.DATA_PROCESSING,
            ]

            # If Redis is unavailable, we lose analytics capability
            if not self._redis_client:
                degraded_capabilities.append(ModuleCapability.ANALYTICS)
            else:
                remaining_capabilities.append(ModuleCapability.ANALYTICS)

            # If ML detection is enabled, we can still do basic threshold detection
            if self._ml_detector:
                degraded_capabilities.append("ML_DETECTION")

            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=degraded_capabilities,
                remaining_capabilities=remaining_capabilities
            )

        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[],
                remaining_capabilities=[],
                error_message=str(e)
            )

    async def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics for this engine."""
        return {
            "anomaly_stats": self.get_anomaly_stats(),
            "active_anomalies": self.get_active_anomalies(),
            "running": self._running
        }