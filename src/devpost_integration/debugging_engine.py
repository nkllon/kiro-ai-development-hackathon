"""
Debugging Engine Module

Provides comprehensive debugging and diagnostic capabilities.
Implements R9.3: Debugging and Diagnostics requirements.
"""

import traceback
import inspect
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from enum import Enum

from .reflective_module import ReflectiveModule, register_module, ModuleCapability, ModuleHealth, ModuleStatus
from .logging_infrastructure import get_logging_infrastructure, LogLevel
from .performance_profiler import get_performance_profiler


class DebugLevel(Enum):
    """Debug level enumeration"""
    BASIC = "BASIC"
    DETAILED = "DETAILED"
    COMPREHENSIVE = "COMPREHENSIVE"


@dataclass
class DebugInfo:
    """Debug information for a module"""
    module_id: str
    debug_level: str
    debug_data: Dict[str, Any]
    execution_trace: List[str]
    performance_metrics: Dict[str, Any]
    error_logs: List[str]
    warning_logs: List[str]
    timestamp: datetime


@dataclass
class TraceStep:
    """Individual step in execution trace"""
    step_id: str
    step_name: str
    start_time: datetime
    end_time: datetime
    duration: float
    status: str  # SUCCESS, ERROR, WARNING
    metadata: Dict[str, Any]


@dataclass
class ExecutionTrace:
    """Complete execution trace for an operation"""
    operation_id: str
    operation_name: str
    start_time: datetime
    end_time: datetime
    steps: List[TraceStep]
    performance_data: Dict[str, Any]
    error_data: Optional[Dict[str, Any]]


@dataclass
class DiagnosticResult:
    """Diagnostic result for issue resolution"""
    issue_id: str
    issue_description: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    root_cause: str
    resolution_steps: List[str]
    prevention_measures: List[str]
    related_issues: List[str]
    timestamp: datetime


class DebuggingEngine(ReflectiveModule):
    """
    Debugging Engine for DevPost Integration
    
    Provides comprehensive debugging and diagnostic capabilities.
    Implements R9.3: Debugging and Diagnostics.
    """
    
    def __init__(self, logging_infrastructure=None, performance_profiler=None):
        """Initialize debugging engine"""
        super().__init__(module_id="debugging_engine", version="1.0.0")
        self.logging = logging_infrastructure or get_logging_infrastructure()
        self.profiler = performance_profiler or get_performance_profiler()
        self.debug_sessions: Dict[str, DebugInfo] = {}
        self.execution_traces: Dict[str, ExecutionTrace] = {}
        self.diagnostic_rules: List[Callable] = []
        register_module(self)
    
    def enable_debug_mode(self, module_id: str, debug_level: DebugLevel = DebugLevel.DETAILED) -> None:
        """Enable debug mode for specific module"""
        debug_info = self._collect_debug_info(module_id, debug_level)
        self.debug_sessions[module_id] = debug_info
        
        self.logging.log_event(
            LogLevel.INFO,
            f"Debug mode enabled for module: {module_id}",
            {"module_id": module_id, "debug_level": debug_level.value}
        )
    
    def disable_debug_mode(self, module_id: str) -> None:
        """Disable debug mode for specific module"""
        if module_id in self.debug_sessions:
            del self.debug_sessions[module_id]
            
            self.logging.log_event(
                LogLevel.INFO,
                f"Debug mode disabled for module: {module_id}",
                {"module_id": module_id}
            )
    
    def get_debug_info(self, module_id: str) -> Optional[DebugInfo]:
        """Get comprehensive debug information for module"""
        if module_id in self.debug_sessions:
            return self.debug_sessions[module_id]
        
        # Collect on-demand debug info
        return self._collect_debug_info(module_id, DebugLevel.BASIC)
    
    def _collect_debug_info(self, module_id: str, debug_level: DebugLevel) -> DebugInfo:
        """Collect debug information for a module"""
        # Get module from registry
        from .reflective_module import get_module_registry
        registry = get_module_registry()
        module = registry.get_module(module_id)
        
        debug_data = {}
        execution_trace = []
        error_logs = []
        warning_logs = []
        
        if module:
            # Get module info
            debug_data["module_info"] = module.get_module_info()
            debug_data["capabilities"] = [cap.value for cap in module.get_capabilities()]
            debug_data["dependencies"] = module.get_dependencies()
            
            # Get health status
            health = module.check_health()
            debug_data["health"] = asdict(health)
            
            if debug_level in [DebugLevel.DETAILED, DebugLevel.COMPREHENSIVE]:
                # Get performance metrics
                metrics = self.profiler.get_performance_metrics(module_id)
                debug_data["performance_metrics"] = {k: asdict(v) for k, v in metrics.items()}
                
                # Get execution trace
                execution_trace = self._get_module_execution_trace(module_id)
        
        # Get error and warning logs
        log_events = self.logging.get_log_events()
        for event in log_events:
            if event.module == module_id:
                if event.level == "ERROR":
                    error_logs.append({
                        "timestamp": event.timestamp.isoformat(),
                        "message": event.message,
                        "context": event.context
                    })
                elif event.level == "WARNING":
                    warning_logs.append({
                        "timestamp": event.timestamp.isoformat(),
                        "message": event.message,
                        "context": event.context
                    })
        
        return DebugInfo(
            module_id=module_id,
            debug_level=debug_level.value,
            debug_data=debug_data,
            execution_trace=execution_trace,
            performance_metrics=debug_data.get("performance_metrics", {}),
            error_logs=error_logs,
            warning_logs=warning_logs,
            timestamp=datetime.now()
        )
    
    def _get_module_execution_trace(self, module_id: str) -> List[str]:
        """Get execution trace for a module"""
        # This is a simplified implementation
        # In a real system, this would track actual execution flow
        return [
            f"Module {module_id} initialized",
            f"Module {module_id} registered with registry",
            f"Module {module_id} health check performed"
        ]
    
    def trace_execution(self, operation_name: str) -> ExecutionTrace:
        """Trace execution of operation for debugging"""
        operation_id = f"{operation_name}_{int(datetime.now().timestamp() * 1000)}"
        
        trace = ExecutionTrace(
            operation_id=operation_id,
            operation_name=operation_name,
            start_time=datetime.now(),
            end_time=datetime.now(),
            steps=[],
            performance_data={},
            error_data=None
        )
        
        self.execution_traces[operation_id] = trace
        
        self.logging.log_event(
            LogLevel.DEBUG,
            f"Started execution trace: {operation_name}",
            {"operation_id": operation_id}
        )
        
        return trace
    
    def add_trace_step(self, trace: ExecutionTrace, step_name: str, 
                      status: str = "SUCCESS", metadata: Dict[str, Any] = None) -> None:
        """Add step to execution trace"""
        step = TraceStep(
            step_id=f"{trace.operation_id}_{len(trace.steps)}",
            step_name=step_name,
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration=0.0,
            status=status,
            metadata=metadata or {}
        )
        
        trace.steps.append(step)
        
        self.logging.log_event(
            LogLevel.DEBUG,
            f"Trace step added: {step_name}",
            {"operation_id": trace.operation_id, "step_name": step_name, "status": status}
        )
    
    def complete_trace(self, trace: ExecutionTrace, error: Optional[Exception] = None) -> None:
        """Complete execution trace"""
        trace.end_time = datetime.now()
        
        if error:
            trace.error_data = {
                "error_type": type(error).__name__,
                "error_message": str(error),
                "traceback": traceback.format_exc()
            }
        
        self.logging.log_event(
            LogLevel.DEBUG,
            f"Completed execution trace: {trace.operation_name}",
            {
                "operation_id": trace.operation_id,
                "duration": (trace.end_time - trace.start_time).total_seconds(),
                "steps_count": len(trace.steps),
                "has_error": error is not None
            }
        )
    
    def diagnose_issue(self, issue_description: str) -> DiagnosticResult:
        """Diagnose and provide resolution for issues"""
        issue_id = f"issue_{int(datetime.now().timestamp() * 1000)}"
        
        # Basic diagnostic logic
        severity = "LOW"
        root_cause = "Unknown"
        resolution_steps = []
        prevention_measures = []
        related_issues = []
        
        # Analyze issue description
        if "error" in issue_description.lower():
            severity = "HIGH"
            root_cause = "Runtime error detected"
            resolution_steps = [
                "Check error logs for detailed information",
                "Verify module dependencies are available",
                "Check system resources and permissions",
                "Review module configuration"
            ]
            prevention_measures = [
                "Implement proper error handling",
                "Add input validation",
                "Monitor system resources",
                "Regular health checks"
            ]
        elif "performance" in issue_description.lower():
            severity = "MEDIUM"
            root_cause = "Performance degradation detected"
            resolution_steps = [
                "Check performance metrics",
                "Identify bottlenecks",
                "Optimize resource usage",
                "Consider scaling"
            ]
            prevention_measures = [
                "Regular performance monitoring",
                "Load testing",
                "Resource optimization",
                "Capacity planning"
            ]
        elif "memory" in issue_description.lower():
            severity = "HIGH"
            root_cause = "Memory issue detected"
            resolution_steps = [
                "Check memory usage patterns",
                "Look for memory leaks",
                "Optimize data structures",
                "Increase available memory"
            ]
            prevention_measures = [
                "Regular memory monitoring",
                "Proper resource cleanup",
                "Memory profiling",
                "Garbage collection tuning"
            ]
        
        result = DiagnosticResult(
            issue_id=issue_id,
            issue_description=issue_description,
            severity=severity,
            root_cause=root_cause,
            resolution_steps=resolution_steps,
            prevention_measures=prevention_measures,
            related_issues=related_issues,
            timestamp=datetime.now()
        )
        
        self.logging.log_event(
            LogLevel.INFO,
            f"Issue diagnosed: {issue_description}",
            {
                "issue_id": issue_id,
                "severity": severity,
                "root_cause": root_cause
            }
        )
        
        return result
    
    def add_diagnostic_rule(self, rule: Callable) -> None:
        """Add custom diagnostic rule"""
        self.diagnostic_rules.append(rule)
    
    def get_system_state(self) -> Dict[str, Any]:
        """Get comprehensive system state for debugging"""
        from .reflective_module import get_module_registry
        registry = get_module_registry()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "modules": {
                module.module_id: {
                    "info": module.get_module_info(),
                    "health": asdict(module.check_health())
                }
                for module in registry.get_all_modules()
            },
            "debug_sessions": {
                module_id: asdict(info) for module_id, info in self.debug_sessions.items()
            },
            "execution_traces": {
                trace_id: asdict(trace) for trace_id, trace in self.execution_traces.items()
            },
            "system_metrics": self.profiler.get_system_metrics()
        }
    
    def export_debug_data(self, filepath: str) -> None:
        """Export debug data to file"""
        import json
        
        data = {
            "debug_sessions": {k: asdict(v) for k, v in self.debug_sessions.items()},
            "execution_traces": {k: asdict(v) for k, v in self.execution_traces.items()},
            "system_state": self.get_system_state(),
            "export_time": datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, default=str, indent=2)
    
    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information"""
        return {
            "module_id": self.module_id,
            "version": self.version,
            "type": "DebuggingEngine",
            "debug_sessions": len(self.debug_sessions),
            "execution_traces": len(self.execution_traces),
            "diagnostic_rules": len(self.diagnostic_rules)
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities"""
        return [
            ModuleCapability.DEBUGGING,
            ModuleCapability.DIAGNOSTICS,
            ModuleCapability.EXECUTION_TRACING,
            ModuleCapability.ISSUE_RESOLUTION
        ]
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies"""
        return ["reflective_module", "logging_infrastructure", "performance_profiler"]
    
    def check_health(self) -> ModuleHealth:
        """Perform comprehensive health check"""
        issues = []
        
        # Check debug sessions
        if len(self.debug_sessions) > 50:  # Arbitrary threshold
            issues.append("Too many debug sessions active")
        
        # Check execution traces
        if len(self.execution_traces) > 1000:  # Arbitrary threshold
            issues.append("Too many execution traces stored")
        
        # Check dependencies
        try:
            if not self.logging:
                issues.append("Logging infrastructure not available")
            if not self.profiler:
                issues.append("Performance profiler not available")
        except Exception as e:
            issues.append(f"Failed to check dependencies: {str(e)}")
        
        status = ModuleStatus.HEALTHY if not issues else ModuleStatus.DEGRADED
        score = 100 - len(issues) * 20
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=max(0, score) / 100.0,  # Convert to 0.0-1.0 range
            issues=issues,
            capabilities=self.get_capabilities(),
            dependencies=self.get_dependencies(),
            metrics=self.get_metrics(),
            last_check=datetime.now()
        )
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get module configuration"""
        return {
            "debug_sessions": len(self.debug_sessions),
            "execution_traces": len(self.execution_traces),
            "diagnostic_rules": len(self.diagnostic_rules),
            "dependencies": self.get_dependencies()
        }
    
    def update_configuration(self, config: Dict[str, Any]) -> None:
        """Update module configuration"""
        # Update configuration as needed
        self.logging.log_event(
            LogLevel.INFO,
            "Debugging engine configuration updated",
            {"config": config}
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics"""
        return {
            "debug_sessions": len(self.debug_sessions),
            "execution_traces": len(self.execution_traces),
            "diagnostic_rules": len(self.diagnostic_rules),
            "modules_count": len(self.debug_sessions)
        }
    
    def reset_metrics(self) -> None:
        """Reset module metrics"""
        self.debug_sessions.clear()
        self.execution_traces.clear()
        self.logging.log_event(
            LogLevel.INFO,
            "Debugging engine metrics reset",
            {"module": self.module_id}
        )


# Global debugging engine instance
_debugging_engine: Optional[DebuggingEngine] = None


def get_debugging_engine() -> DebuggingEngine:
    """Get global debugging engine instance"""
    global _debugging_engine
    if _debugging_engine is None:
        _debugging_engine = DebuggingEngine()
    return _debugging_engine


def enable_debug_mode(module_id: str, debug_level: DebugLevel = DebugLevel.DETAILED) -> None:
    """Enable debug mode using global debugging engine"""
    get_debugging_engine().enable_debug_mode(module_id, debug_level)


def trace_execution(operation_name: str) -> ExecutionTrace:
    """Trace execution using global debugging engine"""
    return get_debugging_engine().trace_execution(operation_name)
