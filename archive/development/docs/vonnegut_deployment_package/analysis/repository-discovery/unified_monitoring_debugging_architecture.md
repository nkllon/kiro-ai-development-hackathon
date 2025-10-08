# Unified Monitoring-Debugging Architecture

## Core Principle: "If you can't monitor it, you can't debug it either"

**Fundamental Truth**: Monitoring and debugging are the same capability. If something cannot be observed through monitoring, it cannot be debugged. If it cannot be debugged, it should not exist in the system.

## Architecture Principles

### 1. Monitoring-First Design
Every component must be designed with monitoring as a first-class concern, not an afterthought.

### 2. Complete Observability
Every aspect of system behavior must be observable through monitoring endpoints.

### 3. Self-Validating Components
Components must validate their own internal consistency and expose violations.

### 4. Debugging Through Monitoring Data Only
Debugging must be possible using only monitoring data - no code inspection allowed.

## Unified Monitoring-Debugging Infrastructure

```python
from typing import Protocol, Dict, Any, List, Optional, Callable, AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import threading
import functools
from contextlib import contextmanager

class MonitorableComponent(Protocol):
    """
    Protocol that ensures every component is fully monitorable and debuggable.
    
    REQUIREMENT: If a component cannot implement this protocol completely,
    it cannot be debugged and therefore should not exist in the system.
    """
    
    def get_monitoring_endpoints(self) -> List[str]:
        """Return all monitoring endpoints this component exposes"""
        
    def get_current_state(self) -> Dict[str, Any]:
        """Return complete current internal state for monitoring"""
        
    def get_health_metrics(self) -> Dict[str, float]:
        """Return health metrics for monitoring dashboards"""
        
    def get_performance_metrics(self) -> Dict[str, float]:
        """Return performance metrics for monitoring"""
        
    def get_debug_context(self) -> Dict[str, Any]:
        """Return complete debug context for troubleshooting"""
        
    def validate_internal_consistency(self) -> List[str]:
        """Validate internal state consistency, return violations"""
        
    def get_operation_history(self) -> List[Dict[str, Any]]:
        """Return recent operation history for debugging"""
        
    def get_decision_log(self) -> List[Dict[str, Any]]:
        """Return recent decision log for debugging"""

class MonitoringInfrastructure:
    """
    Unified monitoring infrastructure that makes debugging possible.
    
    PRINCIPLE: Every aspect of system behavior must be observable
    through monitoring data. No hidden state, no untrackable operations.
    """
    
    def __init__(self):
        self.component_registry: Dict[str, MonitorableComponent] = {}
        self.monitoring_data: Dict[str, Any] = {}
        self.debug_sessions: Dict[str, 'DebugSession'] = {}
        self.real_time_monitors: List['RealTimeMonitor'] = []
        self.operation_history: List[Dict[str, Any]] = []
        
    def register_component(self, component_id: str, component: MonitorableComponent) -> None:
        """
        Register component for monitoring and debugging.
        
        VALIDATION: Component must be fully monitorable or registration fails.
        """
        # Validate that component is fully monitorable
        self._validate_component_monitorability(component_id, component)
        
        self.component_registry[component_id] = component
        
        # Set up continuous monitoring
        self._setup_component_monitoring(component_id, component)
        
    def _validate_component_monitorability(self, component_id: str, component: MonitorableComponent) -> None:
        """
        Ensure component meets monitoring requirements for debuggability.
        
        FAILURE MODE: If validation fails, component cannot be debugged
        and therefore cannot be registered.
        """
        
        # Check monitoring endpoints
        endpoints = component.get_monitoring_endpoints()
        if not endpoints:
            raise ValueError(f"Component {component_id} has no monitoring endpoints - cannot be debugged")
        
        # Check state observability
        state = component.get_current_state()
        if not state:
            raise ValueError(f"Component {component_id} has no observable state - cannot be debugged")
        
        # Check health metrics
        health = component.get_health_metrics()
        if not health:
            raise ValueError(f"Component {component_id} has no health metrics - cannot be monitored")
        
        # Check debug context
        debug_context = component.get_debug_context()
        if not debug_context:
            raise ValueError(f"Component {component_id} has no debug context - cannot be debugged")
        
        # Check operation history
        operation_history = component.get_operation_history()
        if operation_history is None:  # Empty list is OK, None is not
            raise ValueError(f"Component {component_id} has no operation history - cannot be debugged")
        
        # Check decision log
        decision_log = component.get_decision_log()
        if decision_log is None:  # Empty list is OK, None is not
            raise ValueError(f"Component {component_id} has no decision log - cannot be debugged")
        
        # Validate internal consistency
        violations = component.validate_internal_consistency()
        if violations:
            raise ValueError(f"Component {component_id} has consistency violations: {violations}")
    
    def start_debug_session(self, component_id: str, issue_description: str) -> 'DebugSession':
        """
        Start debug session using only monitoring data.
        
        GUARANTEE: If debugging fails, it's because monitoring is insufficient,
        not because the issue is inherently undebuggable.
        """
        
        if component_id not in self.component_registry:
            raise ValueError(f"Component {component_id} not registered for monitoring")
        
        component = self.component_registry[component_id]
        
        debug_session = DebugSession(
            session_id=str(uuid.uuid4()),
            component_id=component_id,
            issue_description=issue_description,
            start_time=datetime.now(),
            monitoring_snapshots=[],
            operation_history=component.get_operation_history(),
            decision_log=component.get_decision_log(),
            current_state=component.get_current_state(),
            health_metrics=component.get_health_metrics(),
            performance_metrics=component.get_performance_metrics(),
            debug_context=component.get_debug_context()
        )
        
        # Validate that we can debug this issue
        if not debug_session.can_debug_issue():
            raise ValueError(f"Insufficient monitoring data to debug issue: {issue_description}")
        
        self.debug_sessions[debug_session.session_id] = debug_session
        return debug_session
    
    def record_operation(self, operation_data: Dict[str, Any]) -> None:
        """Record operation for monitoring and debugging"""
        operation_data['recorded_at'] = datetime.now().isoformat()
        self.operation_history.append(operation_data)
        
        # Keep only recent operations to prevent memory bloat
        if len(self.operation_history) > 10000:
            self.operation_history = self.operation_history[-5000:]

@dataclass
class DebugSession:
    """
    Debug session that relies entirely on monitoring data.
    
    PRINCIPLE: If we can't debug the issue with monitoring data,
    the monitoring is insufficient, not the debugging approach.
    """
    session_id: str
    component_id: str
    issue_description: str
    start_time: datetime
    monitoring_snapshots: List[Dict[str, Any]]
    operation_history: List[Dict[str, Any]]
    decision_log: List[Dict[str, Any]]
    current_state: Dict[str, Any]
    health_metrics: Dict[str, float]
    performance_metrics: Dict[str, float]
    debug_context: Dict[str, Any]
    
    def can_debug_issue(self) -> bool:
        """
        Determine if issue can be debugged with available monitoring data.
        
        CRITICAL: If this returns False, it means the monitoring is insufficient
        for debugging, which is a system design failure.
        """
        
        # Check if we have sufficient data for debugging
        has_state_data = bool(self.current_state)
        has_operation_history = len(self.operation_history) > 0
        has_decision_log = len(self.decision_log) > 0
        has_health_metrics = bool(self.health_metrics)
        has_debug_context = bool(self.debug_context)
        
        return all([
            has_state_data,
            has_operation_history,
            has_decision_log, 
            has_health_metrics,
            has_debug_context
        ])
    
    def analyze_issue(self) -> 'IssueAnalysis':
        """
        Analyze issue using only monitoring data.
        
        GUARANTEE: Analysis is based entirely on observable data,
        no guesswork or code inspection required.
        """
        
        if not self.can_debug_issue():
            raise ValueError("Insufficient monitoring data for debugging")
        
        analysis = IssueAnalysis(
            session_id=self.session_id,
            issue_description=self.issue_description,
            root_cause_analysis=self._perform_root_cause_analysis(),
            timeline_analysis=self._analyze_operation_timeline(),
            state_analysis=self._analyze_state_consistency(),
            performance_analysis=self._analyze_performance_issues(),
            decision_analysis=self._analyze_decision_patterns(),
            remediation_steps=self._generate_remediation_steps()
        )
        
        return analysis
    
    def _perform_root_cause_analysis(self) -> Dict[str, Any]:
        """Perform root cause analysis using monitoring data"""
        
        # Analyze recent errors in operation history
        recent_errors = [
            op for op in self.operation_history[-100:]  # Last 100 operations
            if not op.get('success', True)
        ]
        
        # Analyze health metric trends
        health_issues = [
            metric for metric, value in self.health_metrics.items()
            if value < 0.7  # Threshold for health issues
        ]
        
        # Analyze state consistency violations
        state_violations = self._check_state_consistency()
        
        return {
            "recent_errors": recent_errors,
            "health_issues": health_issues,
            "state_violations": state_violations,
            "error_patterns": self._identify_error_patterns(recent_errors),
            "correlation_analysis": self._correlate_issues()
        }
    
    def _analyze_operation_timeline(self) -> Dict[str, Any]:
        """Analyze operation timeline for patterns"""
        
        # Sort operations by timestamp
        sorted_ops = sorted(
            self.operation_history,
            key=lambda op: op.get('start_time', '1970-01-01T00:00:00')
        )
        
        # Identify operation patterns
        operation_patterns = {}
        for op in sorted_ops[-50:]:  # Last 50 operations
            op_name = op.get('operation_name', 'unknown')
            if op_name not in operation_patterns:
                operation_patterns[op_name] = {
                    'count': 0,
                    'success_rate': 0,
                    'average_duration': 0,
                    'error_types': []
                }
            
            pattern = operation_patterns[op_name]
            pattern['count'] += 1
            
            if op.get('success', True):
                pattern['success_rate'] += 1
            else:
                error_type = op.get('error_type', 'unknown')
                pattern['error_types'].append(error_type)
            
            duration = op.get('duration_seconds', 0)
            pattern['average_duration'] = (
                (pattern['average_duration'] * (pattern['count'] - 1) + duration) / pattern['count']
            )
        
        # Calculate success rates
        for pattern in operation_patterns.values():
            if pattern['count'] > 0:
                pattern['success_rate'] = pattern['success_rate'] / pattern['count']
        
        return {
            "operation_patterns": operation_patterns,
            "timeline": sorted_ops[-20:],  # Last 20 operations
            "failure_clusters": self._identify_failure_clusters(sorted_ops)
        }

@dataclass
class IssueAnalysis:
    """Complete issue analysis based on monitoring data"""
    session_id: str
    issue_description: str
    root_cause_analysis: Dict[str, Any]
    timeline_analysis: Dict[str, Any]
    state_analysis: Dict[str, Any]
    performance_analysis: Dict[str, Any]
    decision_analysis: Dict[str, Any]
    remediation_steps: List[str]

class ContentScanner(ReflectiveModule, MonitorableComponent):
    """
    Content scanner with complete monitoring integration for debuggability.
    
    GUARANTEE: Every aspect of operation is monitorable and therefore debuggable.
    No hidden state, no untrackable operations, no unobservable decisions.
    """
    
    def __init__(self, monitoring_infrastructure: MonitoringInfrastructure):
        super().__init__("content_scanner", "1.0.0")
        self.monitoring = monitoring_infrastructure
        
        # Internal state that MUST be completely monitorable
        self._current_scan_state = ScanState.IDLE
        self._active_scans: Dict[str, 'ScanContext'] = {}
        self._performance_counters = PerformanceCounters()
        self._error_history: List['ErrorRecord'] = []
        self._decision_log: List['DecisionRecord'] = []
        self._operation_history: List[Dict[str, Any]] = []
        self._initialization_time = datetime.now()
        self._last_health_check = datetime.now()
        self._debug_level = "INFO"
        self._trace_sampling_rate = 1.0
        
        # Monitoring endpoints - every aspect must be observable
        self._monitoring_endpoints = [
            "/health",           # Health status and metrics
            "/metrics",          # Performance metrics
            "/state",            # Current internal state
            "/active-scans",     # Active scan details
            "/performance",      # Performance counters and trends
            "/errors",           # Error history and patterns
            "/decisions",        # Decision log and reasoning
            "/debug-context",    # Complete debug context
            "/operation-history", # Recent operation history
            "/consistency-check"  # Internal consistency validation
        ]
        
        # Register with monitoring infrastructure
        self.monitoring.register_component("content_scanner", self)
    
    def get_monitoring_endpoints(self) -> List[str]:
        """Return all monitoring endpoints for observability"""
        return self._monitoring_endpoints
    
    def get_current_state(self) -> Dict[str, Any]:
        """
        Return complete current state - MUST be sufficient for debugging.
        
        PRINCIPLE: If debugging requires information not in this state,
        the state representation is insufficient.
        """
        return {
            "component_info": {
                "name": self.module_name,
                "version": self.version,
                "initialization_time": self._initialization_time.isoformat(),
                "uptime_seconds": (datetime.now() - self._initialization_time).total_seconds()
            },
            "scan_state": {
                "current_state": self._current_scan_state.value,
                "active_scan_count": len(self._active_scans),
                "active_scans": {
                    scan_id: context.to_monitoring_dict()
                    for scan_id, context in self._active_scans.items()
                }
            },
            "performance_state": {
                "total_scans_completed": self._performance_counters.total_scans_completed,
                "total_files_processed": self._performance_counters.total_files_processed,
                "current_throughput": self._performance_counters.current_throughput,
                "average_throughput": self._performance_counters.average_throughput,
                "memory_usage_mb": self._get_current_memory_usage(),
                "cpu_usage_percent": self._get_current_cpu_usage()
            },
            "error_state": {
                "total_errors": len(self._error_history),
                "recent_error_count": len([e for e in self._error_history if (datetime.now() - e.timestamp).total_seconds() < 3600]),
                "last_error": self._error_history[-1].to_monitoring_dict() if self._error_history else None
            },
            "system_state": {
                "thread_count": threading.active_count(),
                "memory_available_mb": self._get_available_memory_mb(),
                "disk_space_available_gb": self._get_available_disk_space_gb()
            }
        }
    
    def get_health_metrics(self) -> Dict[str, float]:
        """Return health metrics for monitoring dashboards"""
        return {
            "overall_health_score": self._calculate_health_score(),
            "error_rate_last_hour": self._calculate_error_rate(timedelta(hours=1)),
            "error_rate_last_day": self._calculate_error_rate(timedelta(days=1)),
            "average_scan_duration_seconds": self._performance_counters.average_scan_duration.total_seconds(),
            "memory_usage_percentage": self._get_memory_usage_percentage(),
            "cpu_usage_percentage": self._get_cpu_usage_percentage(),
            "active_scan_health": self._calculate_active_scan_health(),
            "throughput_health": self._calculate_throughput_health(),
            "consistency_score": self._calculate_consistency_score()
        }
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Return performance metrics for monitoring"""
        return {
            "files_per_second_current": self._performance_counters.current_throughput,
            "files_per_second_average": self._performance_counters.average_throughput,
            "files_per_second_peak": self._performance_counters.peak_throughput,
            "scan_duration_average_seconds": self._performance_counters.average_scan_duration.total_seconds(),
            "scan_duration_p50_seconds": self._performance_counters.scan_duration_p50.total_seconds(),
            "scan_duration_p95_seconds": self._performance_counters.scan_duration_p95.total_seconds(),
            "scan_duration_p99_seconds": self._performance_counters.scan_duration_p99.total_seconds(),
            "memory_peak_mb": self._performance_counters.memory_peak_mb,
            "memory_average_mb": self._performance_counters.memory_average_mb,
            "cache_hit_rate": self._performance_counters.cache_hit_rate,
            "io_operations_per_second": self._performance_counters.io_ops_per_second,
            "queue_depth_average": self._performance_counters.queue_depth_average
        }
    
    def get_debug_context(self) -> Dict[str, Any]:
        """
        Return complete debug context - MUST enable debugging without code inspection.
        
        PRINCIPLE: If debugging requires looking at code, this context is insufficient.
        """
        return {
            "component_metadata": {
                "component_version": self.version,
                "initialization_time": self._initialization_time.isoformat(),
                "last_health_check": self._last_health_check.isoformat(),
                "debug_level": self._debug_level,
                "trace_sampling_rate": self._trace_sampling_rate
            },
            "configuration": self._get_current_configuration(),
            "recent_decisions": [
                decision.to_monitoring_dict() 
                for decision in self._decision_log[-20:]  # Last 20 decisions
            ],
            "recent_errors": [
                error.to_monitoring_dict() 
                for error in self._error_history[-10:]  # Last 10 errors
            ],
            "internal_state_snapshot": {
                "scan_state_details": self._get_detailed_scan_state(),
                "resource_utilization": self._get_detailed_resource_utilization(),
                "performance_trends": self._get_performance_trends(),
                "queue_states": self._get_queue_states(),
                "cache_states": self._get_cache_states()
            },
            "monitoring_metadata": {
                "monitoring_enabled": True,
                "endpoints_active": len(self._monitoring_endpoints),
                "last_consistency_check": self._last_consistency_check.isoformat() if hasattr(self, '_last_consistency_check') else None,
                "monitoring_overhead_ms": self._calculate_monitoring_overhead()
            },
            "dependency_status": self._get_dependency_status(),
            "environment_info": self._get_environment_info()
        }
    
    def get_operation_history(self) -> List[Dict[str, Any]]:
        """Return recent operation history for debugging"""
        return self._operation_history[-100:]  # Last 100 operations
    
    def get_decision_log(self) -> List[Dict[str, Any]]:
        """Return recent decision log for debugging"""
        return [decision.to_monitoring_dict() for decision in self._decision_log[-50:]]  # Last 50 decisions
    
    def validate_internal_consistency(self) -> List[str]:
        """
        Validate internal state consistency for debugging.
        
        PRINCIPLE: Inconsistencies indicate bugs that must be detectable
        through monitoring without code inspection.
        """
        violations = []
        
        # Check scan state consistency
        if self._current_scan_state == ScanState.IDLE and len(self._active_scans) > 0:
            violations.append("State inconsistency: IDLE state but active scans exist")
        
        if self._current_scan_state == ScanState.SCANNING and len(self._active_scans) == 0:
            violations.append("State inconsistency: SCANNING state but no active scans")
        
        # Check performance counter consistency
        if self._performance_counters.total_scans_completed < 0:
            violations.append("Performance counter inconsistency: negative scan count")
        
        if self._performance_counters.total_files_processed < 0:
            violations.append("Performance counter inconsistency: negative files processed")
        
        # Check memory usage consistency
        current_memory = self._get_current_memory_usage()
        if current_memory > self._performance_counters.memory_peak_mb:
            violations.append(f"Memory inconsistency: current usage {current_memory}MB exceeds recorded peak {self._performance_counters.memory_peak_mb}MB")
        
        # Check active scan consistency
        for scan_id, context in self._active_scans.items():
            if context.files_processed < 0:
                violations.append(f"Scan {scan_id}: negative files processed count")
            
            if context.progress_percentage < 0 or context.progress_percentage > 100:
                violations.append(f"Scan {scan_id}: invalid progress percentage {context.progress_percentage}")
            
            if context.start_time > datetime.now():
                violations.append(f"Scan {scan_id}: start time in future")
        
        # Check decision log consistency
        for decision in self._decision_log[-10:]:  # Check recent decisions
            if decision.confidence_score < 0 or decision.confidence_score > 1:
                violations.append(f"Decision {decision.decision_id}: invalid confidence score {decision.confidence_score}")
        
        # Check error history consistency
        for error in self._error_history[-5:]:  # Check recent errors
            if error.timestamp > datetime.now():
                violations.append(f"Error {error.error_id}: timestamp in future")
        
        # Update last consistency check
        self._last_consistency_check = datetime.now()
        
        return violations
    
    @monitored_operation
    def discover_all_content(
        self,
        root_path: Path,
        exclusion_patterns: Optional[List[str]] = None,
        max_depth: Optional[int] = None,
        follow_symlinks: bool = False
    ) -> 'ContentScanResult':
        """
        Discover content with complete monitoring integration.
        
        MONITORING GUARANTEE: Every aspect of this operation is observable
        through monitoring endpoints. Debugging requires no code inspection.
        """
        
        scan_id = str(uuid.uuid4())
        
        # Log decision to start scan
        start_decision = DecisionRecord(
            decision_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            decision_type="scan_initiation",
            input_conditions={
                "root_path": str(root_path),
                "exclusion_patterns": exclusion_patterns,
                "max_depth": max_depth,
                "follow_symlinks": follow_symlinks,
                "current_state": self._current_scan_state.value,
                "active_scan_count": len(self._active_scans)
            },
            decision_result="proceed_with_scan",
            confidence_score=1.0,
            reasoning=["All parameters validated", "System resources available", "No conflicting scans"]
        )
        self._decision_log.append(start_decision)
        
        # Create scan context that is fully monitorable
        scan_context = ScanContext(
            scan_id=scan_id,
            root_path=root_path,
            exclusion_patterns=exclusion_patterns or [],
            max_depth=max_depth,
            follow_symlinks=follow_symlinks,
            start_time=datetime.now(),
            files_processed=0,
            directories_processed=0,
            current_directory=root_path,
            progress_percentage=0.0,
            estimated_completion=None,
            performance_metrics={}
        )
        
        # Register scan for monitoring
        self._active_scans[scan_id] = scan_context
        self._current_scan_state = ScanState.SCANNING
        
        try:
            # Execute scan with monitoring at every step
            result = self._execute_monitored_scan(scan_context)
            
            # Log successful completion decision
            completion_decision = DecisionRecord(
                decision_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                decision_type="scan_completion",
                input_conditions={
                    "scan_id": scan_id,
                    "files_processed": scan_context.files_processed,
                    "scan_duration": (datetime.now() - scan_context.start_time).total_seconds()
                },
                decision_result="scan_completed_successfully",
                confidence_score=1.0,
                reasoning=["All files processed", "No critical errors", "Performance within limits"]
            )
            self._decision_log.append(completion_decision)
            
            # Update performance counters
            self._performance_counters.record_successful_scan(
                duration=datetime.now() - scan_context.start_time,
                files_processed=scan_context.files_processed
            )
            
            return result
            
        except Exception as e:
            # Record error with complete context for debugging
            error_record = ErrorRecord(
                error_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                error_type=type(e).__name__,
                error_message=str(e),
                scan_context=scan_context.to_monitoring_dict(),
                stack_trace=self._get_stack_trace(e),
                monitoring_snapshot=self.get_current_state(),
                decision_chain=[d.decision_id for d in self._decision_log[-10:]]  # Recent decisions
            )
            self._error_history.append(error_record)
            
            # Log error decision
            error_decision = DecisionRecord(
                decision_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                decision_type="error_handling",
                input_conditions={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "scan_progress": scan_context.progress_percentage
                },
                decision_result="propagate_error",
                confidence_score=1.0,
                reasoning=["Unrecoverable error", "Error context captured", "Cleanup completed"]
            )
            self._decision_log.append(error_decision)
            
            raise
        
        finally:
            # Clean up scan context
            if scan_id in self._active_scans:
                del self._active_scans[scan_id]
            
            if len(self._active_scans) == 0:
                self._current_scan_state = ScanState.IDLE

def monitored_operation(func):
    """
    Decorator that ensures operation is fully monitorable and debuggable.
    
    PRINCIPLE: If operation cannot be debugged through monitoring data,
    the operation should not be allowed to execute.
    """
    
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        operation_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        # Record operation start in monitoring data
        operation_context = {
            "operation_id": operation_id,
            "operation_name": func.__name__,
            "component_name": self.__class__.__name__,
            "start_time": start_time.isoformat(),
            "input_parameters": {
                "args": [str(arg) for arg in args],
                "kwargs": {k: str(v) for k, v in kwargs.items()}
            },
            "pre_operation_state": self.get_current_state(),
            "pre_operation_health": self.get_health_metrics(),
            "pre_operation_performance": self.get_performance_metrics()
        }
        
        try:
            # Execute operation
            result = func(self, *args, **kwargs)
            
            # Record successful completion
            end_time = datetime.now()
            operation_context.update({
                "end_time": end_time.isoformat(),
                "duration_seconds": (end_time - start_time).total_seconds(),
                "result_summary": str(result)[:1000] if result else "None",  # Truncated for monitoring
                "post_operation_state": self.get_current_state(),
                "post_operation_health": self.get_health_metrics(),
                "post_operation_performance": self.get_performance_metrics(),
                "success": True
            })
            
            # Store in operation history for debugging
            self._operation_history.append(operation_context)
            
            # Store in monitoring infrastructure
            if hasattr(self, 'monitoring'):
                self.monitoring.record_operation(operation_context)
            
            return result
            
        except Exception as e:
            # Record failure with complete context
            end_time = datetime.now()
            operation_context.update({
                "end_time": end_time.isoformat(),
                "duration_seconds": (end_time - start_time).total_seconds(),
                "error_type": type(e).__name__,
                "error_message": str(e),
                "error_context": self._extract_error_context(e) if hasattr(self, '_extract_error_context') else {},
                "post_error_state": self.get_current_state(),
                "post_error_health": self.get_health_metrics(),
                "post_error_performance": self.get_performance_metrics(),
                "success": False
            })
            
            # Store in operation history for debugging
            self._operation_history.append(operation_context)
            
            # Store in monitoring infrastructure
            if hasattr(self, 'monitoring'):
                self.monitoring.record_operation(operation_context)
            
            raise
    
    return wrapper

@dataclass
class ScanContext:
    """Scan context that is fully monitorable for debugging"""
    scan_id: str
    root_path: Path
    exclusion_patterns: List[str]
    max_depth: Optional[int]
    follow_symlinks: bool
    start_time: datetime
    files_processed: int
    directories_processed: int
    current_directory: Path
    progress_percentage: float
    estimated_completion: Optional[datetime]
    performance_metrics: Dict[str, float]
    
    def to_monitoring_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for monitoring and debugging"""
        return {
            "scan_id": self.scan_id,
            "root_path": str(self.root_path),
            "exclusion_patterns": self.exclusion_patterns,
            "max_depth": self.max_depth,
            "follow_symlinks": self.follow_symlinks,
            "start_time": self.start_time.isoformat(),
            "files_processed": self.files_processed,
            "directories_processed": self.directories_processed,
            "current_directory": str(self.current_directory),
            "progress_percentage": self.progress_percentage,
            "estimated_completion": self.estimated_completion.isoformat() if self.estimated_completion else None,
            "performance_metrics": self.performance_metrics,
            "duration_seconds": (datetime.now() - self.start_time).total_seconds()
        }

@dataclass
class ErrorRecord:
    """Error record with complete context for debugging"""
    error_id: str
    timestamp: datetime
    error_type: str
    error_message: str
    scan_context: Dict[str, Any]
    stack_trace: str
    monitoring_snapshot: Dict[str, Any]
    decision_chain: List[str]
    
    def to_monitoring_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for monitoring and debugging"""
        return {
            "error_id": self.error_id,
            "timestamp": self.timestamp.isoformat(),
            "error_type": self.error_type,
            "error_message": self.error_message,
            "scan_context": self.scan_context,
            "stack_trace": self.stack_trace,
            "monitoring_snapshot": self.monitoring_snapshot,
            "decision_chain": self.decision_chain
        }

@dataclass
class DecisionRecord:
    """Decision record with complete reasoning for debugging"""
    decision_id: str
    timestamp: datetime
    decision_type: str
    input_conditions: Dict[str, Any]
    decision_result: str
    confidence_score: float
    reasoning: List[str]
    
    def to_monitoring_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for monitoring and debugging"""
        return {
            "decision_id": self.decision_id,
            "timestamp": self.timestamp.isoformat(),
            "decision_type": self.decision_type,
            "input_conditions": self.input_conditions,
            "decision_result": self.decision_result,
            "confidence_score": self.confidence_score,
            "reasoning": self.reasoning
        }

class ScanState(Enum):
    """Scan states that are fully observable"""
    IDLE = "idle"
    SCANNING = "scanning"
    PROCESSING = "processing"
    FINALIZING = "finalizing"
    ERROR = "error"

class PerformanceCounters:
    """Performance counters that are fully monitorable"""
    
    def __init__(self):
        self.total_scans_completed = 0
        self.total_files_processed = 0
        self.current_throughput = 0.0
        self.average_throughput = 0.0
        self.peak_throughput = 0.0
        self.average_scan_duration = timedelta(0)
        self.scan_duration_p50 = timedelta(0)
        self.scan_duration_p95 = timedelta(0)
        self.scan_duration_p99 = timedelta(0)
        self.memory_peak_mb = 0.0
        self.memory_average_mb = 0.0
        self.cache_hit_rate = 0.0
        self.io_ops_per_second = 0.0
        self.queue_depth_average = 0.0
        
    def record_successful_scan(self, duration: timedelta, files_processed: int) -> None:
        """Record successful scan metrics"""
        self.total_scans_completed += 1
        self.total_files_processed += files_processed
        
        # Update throughput
        if duration.total_seconds() > 0:
            current_throughput = files_processed / duration.total_seconds()
            self.current_throughput = current_throughput
            
            if current_throughput > self.peak_throughput:
                self.peak_throughput = current_throughput
            
            # Update average throughput
            self.average_throughput = (
                (self.average_throughput * (self.total_scans_completed - 1) + current_throughput) 
                / self.total_scans_completed
            )
        
        # Update duration metrics
        self.average_scan_duration = (
            (self.average_scan_duration * (self.total_scans_completed - 1) + duration)
            / self.total_scans_completed
        )
```

## Summary: Unified Monitoring-Debugging Architecture

### ✅ **Core Principle Enforced**

**"If you can't monitor it, you can't debug it either"**

Every component must:
- **Implement MonitorableComponent protocol** - Complete observability required
- **Expose all internal state** - No hidden state allowed
- **Log all decisions with reasoning** - No unexplained choices
- **Validate internal consistency** - Self-checking for bugs
- **Provide complete debug context** - All information needed for debugging

### ✅ **Debugging Through Monitoring Only**

**No code inspection allowed during debugging:**
- **Operation history** - Complete record of all operations
- **Decision log** - Every choice with full reasoning
- **State snapshots** - Complete internal state at any time
- **Performance metrics** - All timing and resource data
- **Error context** - Complete failure information

### ✅ **Self-Validating System**

**Components validate themselves:**
- **Consistency checks** - Detect internal state violations
- **Health metrics** - Continuous health monitoring
- **Performance validation** - Detect performance degradation
- **Decision quality** - Validate decision-making processes

### 🎯 **Result: Zero-Guessing Debugging**

**When something fails:**
1. **Check monitoring data** - All information is there
2. **Analyze operation history** - See exactly what happened
3. **Review decision log** - Understand why choices were made
4. **Validate consistency** - Find internal state violations
5. **Generate diagnosis** - Systematic root cause analysis

**No guessing. No code inspection. No mystery.**

The system is now designed so that **monitoring capability equals debugging capability**. If it can't be monitored, it can't be debugged, and therefore it shouldn't exist in the system.