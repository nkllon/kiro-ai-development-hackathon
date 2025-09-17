# Enhanced Design: Comprehensive Interface Specifications and Runtime Monitoring

## Runtime Monitoring and Tracing Architecture

### Core Monitoring Infrastructure

```python
from typing import Protocol, Dict, Any, List, Optional, Callable, AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import asyncio
from contextlib import contextmanager
import functools

class TraceLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class OperationTrace:
    """Complete operation trace with performance metrics"""
    trace_id: str
    operation_name: str
    component_name: str
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[timedelta]
    input_parameters: Dict[str, Any]
    output_result: Optional[Any]
    error_info: Optional[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    memory_usage: Dict[str, int]
    nested_traces: List['OperationTrace']
    correlation_id: str
    user_context: Optional[Dict[str, Any]]

@dataclass
class PerformanceProfile:
    """Performance profiling data for operations"""
    operation_name: str
    total_calls: int
    total_duration: timedelta
    average_duration: timedelta
    min_duration: timedelta
    max_duration: timedelta
    p95_duration: timedelta
    p99_duration: timedelta
    error_rate: float
    memory_peak: int
    memory_average: int
    cpu_usage_average: float

class OperationTracer:
    """Comprehensive operation tracing and monitoring"""
    
    def __init__(self):
        self._traces: Dict[str, OperationTrace] = {}
        self._active_traces: Dict[str, OperationTrace] = {}
        self._performance_profiles: Dict[str, PerformanceProfile] = {}
        self._trace_listeners: List[Callable[[OperationTrace], None]] = []
    
    def start_trace(
        self,
        operation_name: str,
        component_name: str,
        input_parameters: Dict[str, Any],
        correlation_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Start operation tracing with full context"""
        trace_id = str(uuid.uuid4())
        correlation_id = correlation_id or str(uuid.uuid4())
        
        trace = OperationTrace(
            trace_id=trace_id,
            operation_name=operation_name,
            component_name=component_name,
            start_time=datetime.now(),
            end_time=None,
            duration=None,
            input_parameters=input_parameters,
            output_result=None,
            error_info=None,
            performance_metrics={},
            memory_usage={},
            nested_traces=[],
            correlation_id=correlation_id,
            user_context=user_context
        )
        
        self._active_traces[trace_id] = trace
        return trace_id
    
    def end_trace(
        self,
        trace_id: str,
        output_result: Optional[Any] = None,
        error_info: Optional[Dict[str, Any]] = None,
        performance_metrics: Optional[Dict[str, float]] = None
    ) -> OperationTrace:
        """End operation tracing with results and metrics"""
        if trace_id not in self._active_traces:
            raise ValueError(f"No active trace found for ID: {trace_id}")
        
        trace = self._active_traces[trace_id]
        trace.end_time = datetime.now()
        trace.duration = trace.end_time - trace.start_time
        trace.output_result = output_result
        trace.error_info = error_info
        trace.performance_metrics = performance_metrics or {}
        
        # Update performance profile
        self._update_performance_profile(trace)
        
        # Move to completed traces
        self._traces[trace_id] = trace
        del self._active_traces[trace_id]
        
        # Notify listeners
        for listener in self._trace_listeners:
            listener(trace)
        
        return trace
    
    def add_nested_trace(self, parent_trace_id: str, nested_trace: OperationTrace) -> None:
        """Add nested trace for hierarchical operation tracking"""
        if parent_trace_id in self._active_traces:
            self._active_traces[parent_trace_id].nested_traces.append(nested_trace)
        elif parent_trace_id in self._traces:
            self._traces[parent_trace_id].nested_traces.append(nested_trace)
    
    def get_performance_profile(self, operation_name: str) -> Optional[PerformanceProfile]:
        """Get performance profile for specific operation"""
        return self._performance_profiles.get(operation_name)
    
    def get_traces_by_correlation(self, correlation_id: str) -> List[OperationTrace]:
        """Get all traces for a correlation ID (request/workflow)"""
        return [
            trace for trace in self._traces.values()
            if trace.correlation_id == correlation_id
        ]
    
    def add_trace_listener(self, listener: Callable[[OperationTrace], None]) -> None:
        """Add listener for real-time trace events"""
        self._trace_listeners.append(listener)

def traced_operation(func):
    """Decorator for automatic operation tracing"""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, '_tracer'):
            return func(self, *args, **kwargs)
        
        # Extract parameters for tracing
        input_params = {
            'args': [str(arg) for arg in args],
            'kwargs': {k: str(v) for k, v in kwargs.items()}
        }
        
        trace_id = self._tracer.start_trace(
            operation_name=func.__name__,
            component_name=self.__class__.__name__,
            input_parameters=input_params
        )
        
        try:
            result = func(self, *args, **kwargs)
            self._tracer.end_trace(trace_id, output_result=str(result))
            return result
        except Exception as e:
            error_info = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'error_traceback': str(e.__traceback__)
            }
            self._tracer.end_trace(trace_id, error_info=error_info)
            raise
    
    return wrapper

class PerformanceMonitor:
    """Real-time performance monitoring for RM-DDD components"""
    
    def __init__(self):
        self._metrics: Dict[str, List[float]] = {}
        self._thresholds: Dict[str, float] = {}
        self._alerts: List[PerformanceAlert] = []
    
    def record_metric(self, metric_name: str, value: float) -> None:
        """Record performance metric value"""
        if metric_name not in self._metrics:
            self._metrics[metric_name] = []
        
        self._metrics[metric_name].append(value)
        
        # Check thresholds
        if metric_name in self._thresholds:
            if value > self._thresholds[metric_name]:
                self._trigger_alert(metric_name, value)
    
    def set_threshold(self, metric_name: str, threshold: float) -> None:
        """Set performance threshold for alerting"""
        self._thresholds[metric_name] = threshold
    
    def get_metric_statistics(self, metric_name: str) -> Dict[str, float]:
        """Get statistical analysis of metric"""
        if metric_name not in self._metrics:
            return {}
        
        values = self._metrics[metric_name]
        return {
            'count': len(values),
            'average': sum(values) / len(values),
            'min': min(values),
            'max': max(values),
            'p95': self._percentile(values, 95),
            'p99': self._percentile(values, 99)
        }

@dataclass
class PerformanceAlert:
    """Performance threshold violation alert"""
    alert_id: str
    metric_name: str
    threshold: float
    actual_value: float
    timestamp: datetime
    component_name: str
    severity: str
```

## Enhanced Component Interface Specifications

### 1. ContentScanner with Full Interface Definition

```python
from typing import List, Dict, Optional, Iterator, Protocol, Union
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timedelta
from enum import Enum
import uuid

class ContentType(Enum):
    SPECIFICATION = "specification"
    SOURCE_CODE = "source_code"
    DOCUMENTATION = "documentation"
    ANALYSIS = "analysis"
    SCRIPT = "script"
    CONFIGURATION = "configuration"
    UNKNOWN = "unknown"

class ScanStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ScanMetadata:
    """Immutable scan operation metadata with comprehensive tracking"""
    scan_id: str
    start_time: datetime
    end_time: Optional[datetime]
    total_files_scanned: int
    total_directories_scanned: int
    scan_depth_achieved: int
    exclusions_applied: List[str]
    performance_metrics: Dict[str, float]
    memory_usage_peak: int
    cpu_usage_average: float
    scan_status: ScanStatus

@dataclass
class ScanError:
    """Scan error with comprehensive tracing context"""
    error_id: str
    file_path: Path
    error_type: str
    error_message: str
    timestamp: datetime
    trace_id: str
    recovery_attempted: bool
    recovery_successful: bool

@dataclass
class ContentScanResult:
    """Complete scan result with monitoring and performance data"""
    scan_id: str
    discovered_paths: List[Path]
    scan_metadata: ScanMetadata
    errors_encountered: List[ScanError]
    performance_profile: Dict[str, timedelta]
    quality_metrics: Dict[str, float]

@dataclass
class ScanProgress:
    """Real-time scan progress with detailed metrics"""
    scan_id: str
    files_processed: int
    directories_processed: int
    current_path: Path
    estimated_completion: datetime
    performance_metrics: Dict[str, float]
    throughput_files_per_second: float
    memory_usage_current: int

class ContentDiscoveryError(Exception):
    """Content discovery operation failed"""
    def __init__(self, message: str, error_context: Dict[str, Any], trace_id: str):
        super().__init__(message)
        self.error_context = error_context
        self.trace_id = trace_id
        self.timestamp = datetime.now()

class ValidationError(Exception):
    """Input validation failed"""
    def __init__(self, message: str, invalid_parameters: Dict[str, Any]):
        super().__init__(message)
        self.invalid_parameters = invalid_parameters

class ContentScanner(ReflectiveModule):
    """
    Discovers repository content with comprehensive monitoring and tracing.
    
    Responsibilities:
    - Systematic filesystem scanning with performance monitoring
    - Real-time progress reporting and cancellation support
    - Comprehensive error handling and recovery
    - Performance profiling and optimization
    """
    
    def __init__(self, tracer: OperationTracer, performance_monitor: PerformanceMonitor):
        super().__init__("content_scanner", "1.0.0")
        self._tracer = tracer
        self._performance_monitor = performance_monitor
        self._active_scans: Dict[str, ScanProgress] = {}
        self._scan_cancellation_tokens: Dict[str, bool] = {}
    
    @traced_operation
    def discover_all_content(
        self,
        root_path: Path,
        exclusion_patterns: Optional[List[str]] = None,
        max_depth: Optional[int] = None,
        follow_symlinks: bool = False,
        progress_callback: Optional[Callable[[ScanProgress], None]] = None
    ) -> ContentScanResult:
        """
        Systematically scan repository filesystem with comprehensive monitoring.
        
        Args:
            root_path: Root directory to scan (must exist and be readable)
            exclusion_patterns: Glob patterns to exclude (e.g., ['*.pyc', '__pycache__'])
            max_depth: Maximum directory depth to scan (None for unlimited)
            follow_symlinks: Whether to follow symbolic links
            progress_callback: Optional callback for real-time progress updates
            
        Returns:
            ContentScanResult with discovered paths and comprehensive metrics
            
        Raises:
            ContentDiscoveryError: When filesystem access fails or scan cannot complete
            ValidationError: When input parameters are invalid
            PermissionError: When access is denied to required directories
            FileNotFoundError: When root_path does not exist
            
        Performance Requirements:
            - Scan 10,000 files within 30 seconds on standard hardware
            - Memory usage < 500MB for repositories up to 1GB
            - Progress reporting every 1000 files or 5 seconds
            - Cancellation response within 1 second
            
        Quality Requirements:
            - 100% file discovery accuracy (no false negatives)
            - Exclusion pattern accuracy > 99.9%
            - Error recovery success rate > 95%
        """
        
    @traced_operation
    def get_scan_progress(self, scan_id: str) -> ScanProgress:
        """
        Get real-time progress of ongoing scan operation.
        
        Args:
            scan_id: Unique identifier for the scan operation
            
        Returns:
            ScanProgress with current status and performance metrics
            
        Raises:
            ValueError: When scan_id is not found or invalid
        """
        
    @traced_operation
    def cancel_scan(self, scan_id: str) -> bool:
        """
        Cancel ongoing scan operation gracefully.
        
        Args:
            scan_id: Unique identifier for the scan operation to cancel
            
        Returns:
            True if cancellation was successful, False if scan was already complete
            
        Raises:
            ValueError: When scan_id is not found or invalid
            
        Performance Requirements:
            - Cancellation response within 1 second
            - Graceful cleanup of resources
            - Partial results preserved where possible
        """
        
    @traced_operation
    def validate_scan_parameters(
        self,
        root_path: Path,
        exclusion_patterns: Optional[List[str]] = None,
        max_depth: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Validate scan parameters before operation.
        
        Args:
            root_path: Root directory path to validate
            exclusion_patterns: Patterns to validate for syntax
            max_depth: Depth limit to validate
            
        Returns:
            Dictionary with validation results and recommendations
            
        Raises:
            ValidationError: When parameters are invalid with detailed error info
        """
        
    def get_scan_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics for all scan operations.
        
        Returns:
            Dictionary with performance statistics, error rates, and trends
        """
```

### 2. ContentClassifier with Confidence Scoring

```python
@dataclass
class ClassificationResult:
    """Content classification with confidence and detailed reasoning"""
    file_path: Path
    content_type: ContentType
    confidence_score: float  # 0.0 to 1.0
    classification_reasons: List[str]
    alternative_types: List[tuple[ContentType, float]]
    classification_metadata: Dict[str, Any]
    processing_time: timedelta
    classifier_version: str

@dataclass
class ClassificationBatch:
    """Batch classification results with comprehensive performance data"""
    batch_id: str
    results: List[ClassificationResult]
    batch_metadata: BatchMetadata
    performance_profile: Dict[str, timedelta]
    accuracy_metrics: Dict[str, float]
    confidence_calibration: Dict[str, float]

@dataclass
class BatchMetadata:
    """Metadata for batch classification operations"""
    batch_size: int
    processing_start: datetime
    processing_end: datetime
    total_files_processed: int
    successful_classifications: int
    failed_classifications: int
    average_confidence: float

class ClassificationError(Exception):
    """Classification operation failed"""
    def __init__(self, message: str, file_path: Path, error_context: Dict[str, Any]):
        super().__init__(message)
        self.file_path = file_path
        self.error_context = error_context

class ContentClassifier(ReflectiveModule):
    """
    Classifies content types with confidence scoring and batch processing.
    
    Responsibilities:
    - Accurate content type classification with confidence scoring
    - Batch processing for performance optimization
    - Confidence calibration and model updating
    - Comprehensive error handling and recovery
    """
    
    def __init__(self, tracer: OperationTracer, performance_monitor: PerformanceMonitor):
        super().__init__("content_classifier", "1.0.0")
        self._tracer = tracer
        self._performance_monitor = performance_monitor
        self._confidence_calibrator = ConfidenceCalibrator()
        self._classification_model = ClassificationModel()
    
    @traced_operation
    def classify_content_types(
        self,
        file_paths: List[Path],
        batch_size: int = 100,
        confidence_threshold: float = 0.7,
        include_alternatives: bool = True,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> ClassificationBatch:
        """
        Classify content types with confidence scoring and batch processing.
        
        Args:
            file_paths: List of file paths to classify
            batch_size: Number of files to process in each batch (1-1000)
            confidence_threshold: Minimum confidence for classification (0.0-1.0)
            include_alternatives: Whether to include alternative classifications
            progress_callback: Optional callback for progress updates (processed, total)
            
        Returns:
            ClassificationBatch with results and comprehensive performance metrics
            
        Raises:
            ClassificationError: When classification logic fails
            FileAccessError: When files cannot be read
            ValidationError: When parameters are invalid
            
        Performance Requirements:
            - Classify 1000 files within 10 seconds
            - Memory usage < 200MB per batch
            - Throughput > 100 files/second for known types
            
        Quality Requirements:
            - Accuracy > 95% for known file types
            - Confidence calibration within 5% of actual accuracy
            - False positive rate < 2%
        """
        
    @traced_operation
    def get_classification_confidence(
        self,
        file_path: Path,
        detailed_analysis: bool = False
    ) -> Union[float, Dict[str, Any]]:
        """
        Get confidence score for single file classification.
        
        Args:
            file_path: Path to file for confidence analysis
            detailed_analysis: Whether to return detailed confidence breakdown
            
        Returns:
            Float confidence score (0.0-1.0) or detailed analysis dictionary
            
        Raises:
            FileAccessError: When file cannot be read
            ClassificationError: When confidence calculation fails
        """
        
    @traced_operation
    def update_classification_model(
        self,
        training_data: List[tuple[Path, ContentType]],
        validation_split: float = 0.2
    ) -> Dict[str, float]:
        """
        Update classification model with new training data.
        
        Args:
            training_data: List of (file_path, correct_type) tuples
            validation_split: Fraction of data to use for validation
            
        Returns:
            Dictionary with model performance metrics after update
            
        Raises:
            ValidationError: When training data is insufficient or invalid
            ModelUpdateError: When model update fails
            
        Performance Requirements:
            - Model update completion within 5 minutes for 1000 samples
            - Accuracy improvement or maintenance after update
        """
        
    @traced_operation
    def calibrate_confidence_scores(self) -> Dict[str, float]:
        """
        Calibrate confidence scores based on historical accuracy.
        
        Returns:
            Dictionary with calibration metrics and adjustments applied
        """
```

### 3. Activity Models for Component Interactions

```python
# Activity Model: ContentScanner Internal Execution
class ContentScannerActivityModel:
    """
    Defines the internal execution flow and object interactions for ContentScanner.
    
    State Transitions:
    IDLE -> VALIDATING -> SCANNING -> PROCESSING -> COMPLETED/FAILED/CANCELLED
    
    Object Interactions:
    1. ContentScanner receives scan request
    2. ParameterValidator validates input parameters
    3. FileSystemTraverser performs directory traversal
    4. MetadataExtractor extracts file metadata
    5. FilterEngine applies exclusion patterns
    6. ProgressReporter updates scan progress
    7. ResultBuilder constructs final result
    """
    
    @traced_operation
    def execute_scan_workflow(self, scan_request: ScanRequest) -> ContentScanResult:
        """
        Execute complete scan workflow with state management.
        
        Workflow Steps:
        1. Validate Parameters -> ParameterValidator.validate()
        2. Initialize Scan -> ScanInitializer.setup()
        3. Traverse Filesystem -> FileSystemTraverser.traverse()
        4. Extract Metadata -> MetadataExtractor.extract_batch()
        5. Apply Filters -> FilterEngine.apply_exclusions()
        6. Report Progress -> ProgressReporter.update()
        7. Build Result -> ResultBuilder.construct()
        8. Cleanup Resources -> ResourceManager.cleanup()
        """

# Activity Model: Multi-Component Interaction
class RepositoryDiscoveryActivityModel:
    """
    Defines interactions between ContentScanner, ContentClassifier, and ContentInventoryManager.
    
    Interaction Flow:
    1. ContentScanner discovers files
    2. ContentClassifier classifies discovered files
    3. ContentInventoryManager builds comprehensive inventory
    4. ChangeTracker monitors for updates
    5. Real-time notifications sent to subscribers
    """
    
    @traced_operation
    def execute_discovery_pipeline(self, discovery_request: DiscoveryRequest) -> RepositoryInventory:
        """
        Execute complete discovery pipeline with component coordination.
        
        Pipeline Steps:
        1. ContentScanner.discover_all_content() -> ContentScanResult
        2. ContentClassifier.classify_content_types() -> ClassificationBatch
        3. ContentInventoryManager.build_inventory() -> ContentInventory
        4. ChangeTracker.initialize_tracking() -> TrackingSession
        5. NotificationService.setup_subscriptions() -> SubscriptionManager
        """
```

## Runtime Monitoring Implementation

### Monitoring Dashboard Interface

```python
class MonitoringDashboard(ReflectiveModule):
    """
    Comprehensive monitoring dashboard for repository discovery system.
    
    Provides real-time visibility into:
    - Component performance metrics
    - Operation tracing and profiling
    - Error rates and recovery statistics
    - Resource utilization trends
    - System health indicators
    """
    
    def __init__(self, tracer: OperationTracer, performance_monitor: PerformanceMonitor):
        super().__init__("monitoring_dashboard", "1.0.0")
        self._tracer = tracer
        self._performance_monitor = performance_monitor
        self._dashboard_server = DashboardServer()
        self._metrics_collector = MetricsCollector()
    
    @traced_operation
    def get_system_health_status(self) -> SystemHealthStatus:
        """
        Get comprehensive system health status.
        
        Returns:
            SystemHealthStatus with component health, performance metrics, and alerts
        """
        
    @traced_operation
    def get_performance_dashboard_data(
        self,
        time_range: timedelta = timedelta(hours=1)
    ) -> DashboardData:
        """
        Get performance dashboard data for specified time range.
        
        Args:
            time_range: Time range for metrics aggregation
            
        Returns:
            DashboardData with charts, metrics, and trend analysis
        """
        
    @traced_operation
    def setup_real_time_monitoring(
        self,
        components: List[str],
        metrics: List[str],
        alert_thresholds: Dict[str, float]
    ) -> MonitoringSession:
        """
        Setup real-time monitoring for specified components and metrics.
        
        Args:
            components: List of component names to monitor
            metrics: List of metric names to track
            alert_thresholds: Threshold values for alerting
            
        Returns:
            MonitoringSession for managing real-time monitoring
        """

@dataclass
class SystemHealthStatus:
    """Comprehensive system health status"""
    overall_health: str  # "healthy", "warning", "critical"
    component_health: Dict[str, ComponentHealth]
    active_alerts: List[Alert]
    performance_summary: PerformanceSummary
    resource_utilization: ResourceUtilization
    last_updated: datetime

@dataclass
class ComponentHealth:
    """Individual component health status"""
    component_name: str
    status: str  # "healthy", "warning", "error"
    last_heartbeat: datetime
    error_rate: float
    performance_score: float
    active_operations: int
    resource_usage: Dict[str, float]
```

## Summary: Monitoring Capabilities

### ✅ **Runtime Monitoring: COMPREHENSIVE**

**Tracing Capabilities:**
- ✅ **Operation-level tracing** with start/end times, parameters, results
- ✅ **Nested trace support** for hierarchical operation tracking
- ✅ **Correlation IDs** for request/workflow tracing
- ✅ **Performance profiling** with percentile analysis
- ✅ **Error tracking** with context and recovery information

**Performance Monitoring:**
- ✅ **Real-time metrics collection** for all operations
- ✅ **Threshold-based alerting** for performance violations
- ✅ **Statistical analysis** (avg, min, max, p95, p99)
- ✅ **Resource utilization tracking** (memory, CPU)
- ✅ **Throughput monitoring** (operations/second)

**Observability Features:**
- ✅ **Component health monitoring** with heartbeat tracking
- ✅ **System-wide dashboard** with real-time updates
- ✅ **Historical trend analysis** for performance optimization
- ✅ **Comprehensive logging** with correlation IDs
- ✅ **Alert management** with severity levels

The enhanced design now provides comprehensive interface specifications, detailed type definitions, activity models, and robust runtime monitoring capabilities that address all the identified gaps in the original specification.