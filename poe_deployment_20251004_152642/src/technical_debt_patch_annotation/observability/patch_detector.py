"""
Observability-based patch detection system.

This module integrates with Jaeger tracing and Prometheus metrics to automatically
detect potential patches and workarounds through performance anomalies and patterns.
"""

import os
import time
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleCapability, ModuleStatus
from ..core.models import PatchAnnotation, DebtLevel, BypassType


class AnomalyType(Enum):
    """Types of observability anomalies that may indicate patches."""
    PERFORMANCE_DEGRADATION = "performance_degradation"
    UNUSUAL_RETRY_PATTERN = "unusual_retry_pattern"
    FALLBACK_ACTIVATION = "fallback_activation"
    ERROR_SUPPRESSION = "error_suppression"
    TIMEOUT_WORKAROUND = "timeout_workaround"
    RESOURCE_LEAK = "resource_leak"
    CIRCUIT_BREAKER_BYPASS = "circuit_breaker_bypass"


class ConfidenceLevel(Enum):
    """Confidence levels for patch detection."""
    LOW = "low"           # 0-40% confidence
    MEDIUM = "medium"     # 40-70% confidence
    HIGH = "high"         # 70-90% confidence
    CRITICAL = "critical" # 90%+ confidence


@dataclass
class PerformanceAnomaly:
    """Performance anomaly that may indicate a patch."""
    anomaly_id: str
    anomaly_type: AnomalyType
    component: str
    service_name: str
    operation_name: str
    detected_at: datetime
    confidence: ConfidenceLevel
    
    # Performance metrics
    baseline_latency_ms: float
    current_latency_ms: float
    latency_increase_percent: float
    
    # Context information
    trace_ids: List[str] = field(default_factory=list)
    error_rate: float = 0.0
    throughput_impact: float = 0.0
    
    # Evidence
    evidence: Dict[str, Any] = field(default_factory=dict)
    suggested_patch_location: Optional[str] = None
    remediation_suggestion: Optional[str] = None


@dataclass
class MetricsAnomaly:
    """Metrics anomaly detected through Prometheus analysis."""
    anomaly_id: str
    metric_name: str
    component: str
    detected_at: datetime
    confidence: ConfidenceLevel
    
    # Metric values
    baseline_value: float
    current_value: float
    deviation_percent: float
    
    # Pattern information
    pattern_type: str  # "spike", "gradual_increase", "oscillation", etc.
    duration_minutes: int
    frequency: Optional[str] = None  # For recurring patterns
    
    # Context
    related_metrics: List[str] = field(default_factory=list)
    correlation_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TraceCorrelation:
    """Correlation between traces and potential patch locations."""
    correlation_id: str
    trace_id: str
    component: str
    operation: str
    timestamp: datetime
    
    # Correlation strength
    correlation_score: float  # 0.0 to 1.0
    correlation_type: str     # "performance", "error", "pattern"
    
    # Trace analysis
    execution_path: List[str] = field(default_factory=list)
    unusual_patterns: List[str] = field(default_factory=list)
    performance_impact: Dict[str, float] = field(default_factory=dict)


@dataclass
class SuspiciousPattern:
    """Suspicious pattern detected in observability data."""
    pattern_id: str
    pattern_type: str
    component: str
    detected_at: datetime
    confidence: ConfidenceLevel
    
    # Pattern details
    pattern_description: str
    frequency: int
    duration: timedelta
    
    # Evidence
    trace_evidence: List[str] = field(default_factory=list)
    metric_evidence: List[str] = field(default_factory=list)
    log_evidence: List[str] = field(default_factory=list)


@dataclass
class WorkaroundCandidate:
    """Candidate location for a potential workaround or patch."""
    candidate_id: str
    component: str
    service_name: str
    operation_name: str
    detected_at: datetime
    confidence: ConfidenceLevel
    
    # Location information
    suspected_file_path: Optional[str] = None
    suspected_function: Optional[str] = None
    code_patterns: List[str] = field(default_factory=list)
    
    # Supporting evidence
    performance_anomalies: List[PerformanceAnomaly] = field(default_factory=list)
    metrics_anomalies: List[MetricsAnomaly] = field(default_factory=list)
    trace_correlations: List[TraceCorrelation] = field(default_factory=list)
    
    # Suggested patch annotation
    suggested_annotation: Optional[PatchAnnotation] = None


class ObservabilityPatchDetector(ReflectiveModule):
    """
    Observability-based patch detection system using Jaeger and Prometheus.
    
    This system analyzes distributed traces and metrics to automatically detect
    potential patches, workarounds, and technical debt through performance
    anomalies and suspicious patterns.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.module_id = "observability_patch_detector"
        
        # Configuration
        self.config = config or {}
        self._jaeger_enabled = self.config.get('jaeger_enabled', True)
        self._prometheus_enabled = self.config.get('prometheus_enabled', True)
        
        # Jaeger configuration
        self._jaeger_endpoint = self.config.get('jaeger_endpoint', 'http://localhost:14268')
        self._jaeger_service_name = self.config.get('jaeger_service_name', 'patch-detector')
        
        # Prometheus configuration  
        self._prometheus_endpoint = self.config.get('prometheus_endpoint', 'http://localhost:9090')
        self._prometheus_query_timeout = self.config.get('prometheus_query_timeout', 30)
        
        # Detection thresholds
        self._performance_threshold = self.config.get('performance_threshold_percent', 50.0)
        self._error_rate_threshold = self.config.get('error_rate_threshold', 0.05)
        self._anomaly_detection_window = self.config.get('anomaly_detection_window_minutes', 60)
        
        # Storage for detected anomalies
        self._performance_anomalies: List[PerformanceAnomaly] = []
        self._metrics_anomalies: List[MetricsAnomaly] = []
        self._trace_correlations: List[TraceCorrelation] = []
        self._suspicious_patterns: List[SuspiciousPattern] = []
        self._workaround_candidates: List[WorkaroundCandidate] = []
        
        # Initialize integrations
        self._initialize_integrations()
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": self.module_id,
            "module_name": "Observability Patch Detector",
            "version": "1.0.0",
            "description": "Automated patch detection through observability signals",
            "jaeger_enabled": self._jaeger_enabled,
            "prometheus_enabled": self._prometheus_enabled,
            "jaeger_endpoint": self._jaeger_endpoint,
            "prometheus_endpoint": self._prometheus_endpoint,
            "detection_thresholds": {
                "performance_threshold_percent": self._performance_threshold,
                "error_rate_threshold": self._error_rate_threshold,
                "anomaly_detection_window_minutes": self._anomaly_detection_window
            }
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [
            ModuleCapability.MONITORING,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION
        ]
    
    def get_health_status(self):
        """Get module health status."""
        from src.rm_ddd.core.unified_reflective_module import ModuleHealth
        
        issues = []
        health_score = 1.0
        
        # Check Jaeger connectivity
        if self._jaeger_enabled and not self._check_jaeger_connectivity():
            issues.append("Jaeger endpoint not accessible")
            health_score -= 0.3
        
        # Check Prometheus connectivity
        if self._prometheus_enabled and not self._check_prometheus_connectivity():
            issues.append("Prometheus endpoint not accessible")
            health_score -= 0.3
        
        # Determine status
        if health_score >= 0.8:
            status = ModuleStatus.HEALTHY
        elif health_score >= 0.5:
            status = ModuleStatus.WARNING
        else:
            status = ModuleStatus.ERROR
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds(),
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self):
        """Perform graceful degradation."""
        from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult
        
        degraded_capabilities = []
        remaining_capabilities = list(self.get_capabilities())
        
        # Disable Jaeger if not accessible
        if self._jaeger_enabled and not self._check_jaeger_connectivity():
            self._jaeger_enabled = False
            degraded_capabilities.append("Jaeger tracing analysis")
            self._logger.warning("Jaeger integration disabled due to connectivity issues")
        
        # Disable Prometheus if not accessible
        if self._prometheus_enabled and not self._check_prometheus_connectivity():
            self._prometheus_enabled = False
            degraded_capabilities.append("Prometheus metrics analysis")
            self._logger.warning("Prometheus integration disabled due to connectivity issues")
        
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=degraded_capabilities,
            remaining_capabilities=[cap.value for cap in remaining_capabilities]
        )
    
    def _initialize_integrations(self):
        """Initialize Jaeger and Prometheus integrations."""
        try:
            # Initialize Jaeger client
            if self._jaeger_enabled:
                self._initialize_jaeger_client()
            
            # Initialize Prometheus client
            if self._prometheus_enabled:
                self._initialize_prometheus_client()
                
            self._logger.info("Observability integrations initialized successfully")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize observability integrations: {e}")
            self._increment_error_count()
    
    def _initialize_jaeger_client(self):
        """Initialize Jaeger client for trace analysis."""
        try:
            # Try to import Jaeger client libraries
            try:
                import requests
                self._jaeger_client = requests.Session()
                self._jaeger_client.timeout = 30
                self._logger.info("Jaeger client initialized")
            except ImportError:
                self._logger.warning("Jaeger client libraries not available, using fallback")
                self._jaeger_client = None
                
        except Exception as e:
            self._logger.error(f"Failed to initialize Jaeger client: {e}")
            self._jaeger_enabled = False
    
    def _initialize_prometheus_client(self):
        """Initialize Prometheus client for metrics analysis."""
        try:
            # Try to import Prometheus client libraries
            try:
                import requests
                self._prometheus_client = requests.Session()
                self._prometheus_client.timeout = self._prometheus_query_timeout
                self._logger.info("Prometheus client initialized")
            except ImportError:
                self._logger.warning("Prometheus client libraries not available, using fallback")
                self._prometheus_client = None
                
        except Exception as e:
            self._logger.error(f"Failed to initialize Prometheus client: {e}")
            self._prometheus_enabled = False
    
    def _check_jaeger_connectivity(self) -> bool:
        """Check if Jaeger endpoint is accessible."""
        if not self._jaeger_enabled or not self._jaeger_client:
            return False
        
        try:
            # Try to query Jaeger API
            response = self._jaeger_client.get(f"{self._jaeger_endpoint}/api/services")
            return response.status_code == 200
        except Exception:
            return False
    
    def _check_prometheus_connectivity(self) -> bool:
        """Check if Prometheus endpoint is accessible."""
        if not self._prometheus_enabled or not self._prometheus_client:
            return False
        
        try:
            # Try to query Prometheus API
            response = self._prometheus_client.get(f"{self._prometheus_endpoint}/api/v1/query?query=up")
            return response.status_code == 200
        except Exception:
            return False
    
    def detect_performance_anomalies(self, 
                                   component: str, 
                                   timeframe: timedelta = None) -> List[PerformanceAnomaly]:
        """
        Detect performance anomalies that may indicate patches.
        
        Args:
            component: Component name to analyze
            timeframe: Time window for analysis (default: 1 hour)
            
        Returns:
            List of detected performance anomalies
        """
        with self.trace_operation("detect_performance_anomalies", component=component) as trace:
            try:
                timeframe = timeframe or timedelta(minutes=self._anomaly_detection_window)
                anomalies = []
                
                if self._jaeger_enabled:
                    # Analyze Jaeger traces for performance anomalies
                    trace_anomalies = self._analyze_trace_performance(component, timeframe)
                    anomalies.extend(trace_anomalies)
                
                if self._prometheus_enabled:
                    # Analyze Prometheus metrics for performance anomalies
                    metrics_anomalies = self._analyze_metrics_performance(component, timeframe)
                    anomalies.extend(metrics_anomalies)
                
                # Store detected anomalies
                self._performance_anomalies.extend(anomalies)
                
                # Keep only recent anomalies (last 24 hours)
                cutoff_time = datetime.now() - timedelta(hours=24)
                self._performance_anomalies = [
                    a for a in self._performance_anomalies 
                    if a.detected_at > cutoff_time
                ]
                
                trace.output_result = {"anomalies_detected": len(anomalies)}
                self._logger.info(f"Detected {len(anomalies)} performance anomalies for component {component}")
                
                return anomalies
                
            except Exception as e:
                self._logger.error(f"Failed to detect performance anomalies: {e}")
                self._increment_error_count()
                return []
    
    def _analyze_trace_performance(self, 
                                 component: str, 
                                 timeframe: timedelta) -> List[PerformanceAnomaly]:
        """Analyze Jaeger traces for performance anomalies."""
        anomalies = []
        
        try:
            if not self._jaeger_client:
                return anomalies
            
            # Query traces for the component
            end_time = datetime.now()
            start_time = end_time - timeframe
            
            # Mock trace analysis (in real implementation, would query Jaeger API)
            # This demonstrates the pattern for trace-based anomaly detection
            mock_traces = self._get_mock_trace_data(component, start_time, end_time)
            
            for trace_data in mock_traces:
                # Analyze trace for performance patterns
                if self._is_performance_anomaly(trace_data):
                    anomaly = self._create_performance_anomaly_from_trace(trace_data)
                    anomalies.append(anomaly)
            
        except Exception as e:
            self._logger.error(f"Failed to analyze trace performance: {e}")
        
        return anomalies
    
    def _analyze_metrics_performance(self, 
                                   component: str, 
                                   timeframe: timedelta) -> List[PerformanceAnomaly]:
        """Analyze Prometheus metrics for performance anomalies."""
        anomalies = []
        
        try:
            if not self._prometheus_client:
                return anomalies
            
            # Query relevant metrics
            metrics_to_analyze = [
                f'http_request_duration_seconds{{service="{component}"}}',
                f'http_requests_total{{service="{component}"}}',
                f'error_rate{{service="{component}"}}',
                f'retry_count_total{{service="{component}"}}'
            ]
            
            for metric_query in metrics_to_analyze:
                try:
                    # Mock metrics analysis (in real implementation, would query Prometheus)
                    mock_metrics = self._get_mock_metrics_data(metric_query, timeframe)
                    
                    # Analyze metrics for anomalies
                    metric_anomalies = self._detect_metrics_anomalies(mock_metrics, component)
                    
                    # Convert metrics anomalies to performance anomalies
                    for metrics_anomaly in metric_anomalies:
                        perf_anomaly = self._convert_metrics_to_performance_anomaly(metrics_anomaly)
                        if perf_anomaly:
                            anomalies.append(perf_anomaly)
                            
                except Exception as e:
                    self._logger.warning(f"Failed to analyze metric {metric_query}: {e}")
            
        except Exception as e:
            self._logger.error(f"Failed to analyze metrics performance: {e}")
        
        return anomalies
    
    def correlate_observability_signals(self, 
                                      component: str,
                                      timeframe: timedelta = None) -> List[TraceCorrelation]:
        """
        Correlate observability signals to identify potential patch locations.
        
        Args:
            component: Component name to analyze
            timeframe: Time window for correlation analysis
            
        Returns:
            List of trace correlations indicating potential patches
        """
        with self.trace_operation("correlate_observability_signals", component=component) as trace:
            try:
                timeframe = timeframe or timedelta(minutes=self._anomaly_detection_window)
                correlations = []
                
                # Get recent performance anomalies
                recent_anomalies = [
                    a for a in self._performance_anomalies
                    if a.component == component and 
                    a.detected_at > (datetime.now() - timeframe)
                ]
                
                # Correlate anomalies with trace data
                for anomaly in recent_anomalies:
                    for trace_id in anomaly.trace_ids:
                        correlation = self._analyze_trace_correlation(trace_id, anomaly)
                        if correlation:
                            correlations.append(correlation)
                
                # Store correlations
                self._trace_correlations.extend(correlations)
                
                # Keep only recent correlations
                cutoff_time = datetime.now() - timedelta(hours=24)
                self._trace_correlations = [
                    c for c in self._trace_correlations 
                    if c.timestamp > cutoff_time
                ]
                
                trace.output_result = {"correlations_found": len(correlations)}
                self._logger.info(f"Found {len(correlations)} trace correlations for component {component}")
                
                return correlations
                
            except Exception as e:
                self._logger.error(f"Failed to correlate observability signals: {e}")
                self._increment_error_count()
                return []
    
    def identify_workaround_candidates(self, 
                                     component: str = None,
                                     confidence_threshold: ConfidenceLevel = ConfidenceLevel.MEDIUM) -> List[WorkaroundCandidate]:
        """
        Identify potential workaround candidates based on observability analysis.
        
        Args:
            component: Specific component to analyze (None for all)
            confidence_threshold: Minimum confidence level for candidates
            
        Returns:
            List of workaround candidates
        """
        with self.trace_operation("identify_workaround_candidates", 
                                component=component, 
                                confidence_threshold=confidence_threshold.value) as trace:
            try:
                candidates = []
                
                # Filter anomalies by component if specified
                anomalies_to_analyze = self._performance_anomalies
                if component:
                    anomalies_to_analyze = [
                        a for a in anomalies_to_analyze 
                        if a.component == component
                    ]
                
                # Group anomalies by component and operation
                anomaly_groups = self._group_anomalies_by_operation(anomalies_to_analyze)
                
                # Analyze each group for workaround patterns
                for group_key, group_anomalies in anomaly_groups.items():
                    candidate = self._analyze_anomaly_group_for_workarounds(group_key, group_anomalies)
                    
                    if candidate and candidate.confidence.value >= confidence_threshold.value:
                        candidates.append(candidate)
                
                # Store candidates
                self._workaround_candidates.extend(candidates)
                
                # Keep only recent candidates
                cutoff_time = datetime.now() - timedelta(hours=24)
                self._workaround_candidates = [
                    c for c in self._workaround_candidates 
                    if c.detected_at > cutoff_time
                ]
                
                trace.output_result = {"candidates_identified": len(candidates)}
                self._logger.info(f"Identified {len(candidates)} workaround candidates")
                
                return candidates
                
            except Exception as e:
                self._logger.error(f"Failed to identify workaround candidates: {e}")
                self._increment_error_count()
                return []
    
    def generate_patch_suggestions(self, 
                                 workaround_candidates: List[WorkaroundCandidate] = None) -> List[PatchAnnotation]:
        """
        Generate patch annotation suggestions based on workaround candidates.
        
        Args:
            workaround_candidates: Candidates to generate suggestions for (None for all recent)
            
        Returns:
            List of suggested patch annotations
        """
        with self.trace_operation("generate_patch_suggestions") as trace:
            try:
                candidates = workaround_candidates or self._workaround_candidates
                suggestions = []
                
                for candidate in candidates:
                    # Generate patch annotation based on candidate analysis
                    patch_suggestion = self._create_patch_annotation_from_candidate(candidate)
                    if patch_suggestion:
                        suggestions.append(patch_suggestion)
                
                trace.output_result = {"suggestions_generated": len(suggestions)}
                self._logger.info(f"Generated {len(suggestions)} patch annotation suggestions")
                
                return suggestions
                
            except Exception as e:
                self._logger.error(f"Failed to generate patch suggestions: {e}")
                self._increment_error_count()
                return []
    
    def get_detection_summary(self) -> Dict[str, Any]:
        """Get summary of all detection activities."""
        return {
            "detection_summary": {
                "performance_anomalies": len(self._performance_anomalies),
                "metrics_anomalies": len(self._metrics_anomalies),
                "trace_correlations": len(self._trace_correlations),
                "suspicious_patterns": len(self._suspicious_patterns),
                "workaround_candidates": len(self._workaround_candidates)
            },
            "recent_activity": {
                "last_detection_run": datetime.now().isoformat(),
                "jaeger_enabled": self._jaeger_enabled,
                "prometheus_enabled": self._prometheus_enabled,
                "detection_window_minutes": self._anomaly_detection_window
            },
            "thresholds": {
                "performance_threshold_percent": self._performance_threshold,
                "error_rate_threshold": self._error_rate_threshold
            }
        }
    
    # Mock data methods for demonstration (would be replaced with real API calls)
    
    def _get_mock_trace_data(self, component: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Generate mock trace data for demonstration."""
        return [
            {
                "trace_id": "trace_001",
                "component": component,
                "operation": "process_request",
                "duration_ms": 1500,  # Unusually high
                "error_count": 0,
                "retry_count": 3,     # Suspicious retry pattern
                "timestamp": datetime.now(),
                "spans": [
                    {"name": "database_query", "duration_ms": 50},
                    {"name": "external_api_call", "duration_ms": 1400},  # Bottleneck
                    {"name": "response_processing", "duration_ms": 50}
                ]
            },
            {
                "trace_id": "trace_002", 
                "component": component,
                "operation": "handle_timeout",
                "duration_ms": 5000,  # Timeout workaround
                "error_count": 1,
                "retry_count": 0,
                "timestamp": datetime.now(),
                "spans": [
                    {"name": "timeout_handler", "duration_ms": 5000}  # Suspicious
                ]
            }
        ]
    
    def _get_mock_metrics_data(self, metric_query: str, timeframe: timedelta) -> Dict[str, Any]:
        """Generate mock metrics data for demonstration."""
        return {
            "metric_name": metric_query,
            "values": [
                {"timestamp": datetime.now() - timedelta(minutes=30), "value": 0.1},
                {"timestamp": datetime.now() - timedelta(minutes=20), "value": 0.8},  # Spike
                {"timestamp": datetime.now() - timedelta(minutes=10), "value": 0.2},
                {"timestamp": datetime.now(), "value": 0.1}
            ],
            "baseline": 0.1,
            "current": 0.2
        }
    
    def _is_performance_anomaly(self, trace_data: Dict[str, Any]) -> bool:
        """Check if trace data indicates a performance anomaly."""
        # Check for suspicious patterns
        duration_ms = trace_data.get("duration_ms", 0)
        retry_count = trace_data.get("retry_count", 0)
        
        # High duration or retry patterns indicate potential patches
        return duration_ms > 1000 or retry_count > 2
    
    def _create_performance_anomaly_from_trace(self, trace_data: Dict[str, Any]) -> PerformanceAnomaly:
        """Create performance anomaly from trace data."""
        return PerformanceAnomaly(
            anomaly_id=f"perf_{trace_data['trace_id']}",
            anomaly_type=AnomalyType.PERFORMANCE_DEGRADATION,
            component=trace_data["component"],
            service_name=trace_data["component"],
            operation_name=trace_data["operation"],
            detected_at=datetime.now(),
            confidence=ConfidenceLevel.HIGH if trace_data.get("retry_count", 0) > 2 else ConfidenceLevel.MEDIUM,
            baseline_latency_ms=200.0,  # Mock baseline
            current_latency_ms=trace_data["duration_ms"],
            latency_increase_percent=((trace_data["duration_ms"] - 200.0) / 200.0) * 100,
            trace_ids=[trace_data["trace_id"]],
            evidence=trace_data
        )
    
    def _detect_metrics_anomalies(self, metrics_data: Dict[str, Any], component: str) -> List[MetricsAnomaly]:
        """Detect anomalies in metrics data."""
        anomalies = []
        
        values = [v["value"] for v in metrics_data.get("values", [])]
        if not values:
            return anomalies
        
        baseline = metrics_data.get("baseline", statistics.mean(values))
        current = values[-1] if values else 0
        
        # Check for significant deviation
        if baseline > 0:
            deviation_percent = ((current - baseline) / baseline) * 100
            if abs(deviation_percent) > self._performance_threshold:
                anomaly = MetricsAnomaly(
                    anomaly_id=f"metrics_{component}_{int(time.time())}",
                    metric_name=metrics_data["metric_name"],
                    component=component,
                    detected_at=datetime.now(),
                    confidence=ConfidenceLevel.HIGH if abs(deviation_percent) > 100 else ConfidenceLevel.MEDIUM,
                    baseline_value=baseline,
                    current_value=current,
                    deviation_percent=deviation_percent,
                    pattern_type="spike" if deviation_percent > 0 else "drop",
                    duration_minutes=30  # Mock duration
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    def _convert_metrics_to_performance_anomaly(self, metrics_anomaly: MetricsAnomaly) -> Optional[PerformanceAnomaly]:
        """Convert metrics anomaly to performance anomaly."""
        if "duration" in metrics_anomaly.metric_name or "latency" in metrics_anomaly.metric_name:
            return PerformanceAnomaly(
                anomaly_id=f"perf_from_metrics_{metrics_anomaly.anomaly_id}",
                anomaly_type=AnomalyType.PERFORMANCE_DEGRADATION,
                component=metrics_anomaly.component,
                service_name=metrics_anomaly.component,
                operation_name="unknown",
                detected_at=metrics_anomaly.detected_at,
                confidence=metrics_anomaly.confidence,
                baseline_latency_ms=metrics_anomaly.baseline_value * 1000,  # Convert to ms
                current_latency_ms=metrics_anomaly.current_value * 1000,
                latency_increase_percent=metrics_anomaly.deviation_percent,
                evidence={"source_metric": metrics_anomaly.metric_name}
            )
        return None
    
    def _analyze_trace_correlation(self, trace_id: str, anomaly: PerformanceAnomaly) -> Optional[TraceCorrelation]:
        """Analyze trace correlation with anomaly."""
        # Mock correlation analysis
        return TraceCorrelation(
            correlation_id=f"corr_{trace_id}_{anomaly.anomaly_id}",
            trace_id=trace_id,
            component=anomaly.component,
            operation=anomaly.operation_name,
            timestamp=datetime.now(),
            correlation_score=0.8,  # High correlation
            correlation_type="performance",
            execution_path=["entry", "middleware", "handler", "exit"],
            unusual_patterns=["retry_loop", "timeout_handling"],
            performance_impact={"latency_increase_ms": anomaly.current_latency_ms - anomaly.baseline_latency_ms}
        )
    
    def _group_anomalies_by_operation(self, anomalies: List[PerformanceAnomaly]) -> Dict[str, List[PerformanceAnomaly]]:
        """Group anomalies by component and operation."""
        groups = {}
        for anomaly in anomalies:
            key = f"{anomaly.component}::{anomaly.operation_name}"
            if key not in groups:
                groups[key] = []
            groups[key].append(anomaly)
        return groups
    
    def _analyze_anomaly_group_for_workarounds(self, 
                                             group_key: str, 
                                             anomalies: List[PerformanceAnomaly]) -> Optional[WorkaroundCandidate]:
        """Analyze group of anomalies for workaround patterns."""
        if len(anomalies) < 2:  # Need multiple occurrences
            return None
        
        component, operation = group_key.split("::")
        
        # Calculate confidence based on frequency and severity
        avg_latency_increase = statistics.mean([a.latency_increase_percent for a in anomalies])
        frequency = len(anomalies)
        
        if avg_latency_increase > 100 and frequency > 3:
            confidence = ConfidenceLevel.HIGH
        elif avg_latency_increase > 50 and frequency > 2:
            confidence = ConfidenceLevel.MEDIUM
        else:
            confidence = ConfidenceLevel.LOW
        
        return WorkaroundCandidate(
            candidate_id=f"candidate_{component}_{operation}_{int(time.time())}",
            component=component,
            service_name=component,
            operation_name=operation,
            detected_at=datetime.now(),
            confidence=confidence,
            suspected_function=operation,
            code_patterns=["retry_loop", "timeout_handling", "fallback_mechanism"],
            performance_anomalies=anomalies
        )
    
    def _create_patch_annotation_from_candidate(self, candidate: WorkaroundCandidate) -> Optional[PatchAnnotation]:
        """Create patch annotation suggestion from workaround candidate."""
        if candidate.confidence == ConfidenceLevel.LOW:
            return None
        
        # Determine debt level based on confidence and impact
        if candidate.confidence == ConfidenceLevel.CRITICAL:
            debt_level = DebtLevel.CRITICAL
        elif candidate.confidence == ConfidenceLevel.HIGH:
            debt_level = DebtLevel.HIGH
        else:
            debt_level = DebtLevel.MEDIUM
        
        # Generate reason based on detected patterns
        patterns = ", ".join(candidate.code_patterns)
        reason = f"Performance anomaly detected in {candidate.operation_name}: {patterns}"
        
        # Generate cleanup task
        cleanup_task = f"Investigate and optimize {candidate.operation_name} in {candidate.component}"
        
        return PatchAnnotation(
            reason=reason,
            upstream_issue=f"OBSERVABILITY-DETECTED-{candidate.candidate_id}",
            cleanup_task=cleanup_task,
            debt_level=debt_level,
            bypass_type=BypassType.PERFORMANCE,
            component=candidate.component,
            expected_resolution=datetime.now() + timedelta(days=30),
            validation_criteria=[
                f"Latency for {candidate.operation_name} reduced by 50%",
                "No retry patterns detected in traces",
                "Error rate below 1%"
            ],
            tags=["observability-detected", "performance-anomaly"]
        )