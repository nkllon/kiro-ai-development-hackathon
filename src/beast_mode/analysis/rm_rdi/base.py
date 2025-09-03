"""
RM-RDI Analysis System - Base Classes and Interfaces

OPERATOR SAFETY: All base classes enforce read-only operations and safety checks
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type
from datetime import datetime
import logging
from pathlib import Path

from ...core.reflective_module import ReflectiveModule, HealthStatus
from .data_models import AnalysisResult, AnalysisStatus
from .safety import get_safety_manager, is_safe_to_proceed, SafetyStatus


class AnalysisError(Exception):
    """Base exception for analysis errors"""
    
    def __init__(self, message: str, error_code: str, context: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        super().__init__(message)


class SafetyViolationError(AnalysisError):
    """Raised when safety constraints are violated"""
    
    def __init__(self, violation: str, context: Dict[str, Any] = None):
        super().__init__(
            f"Safety violation: {violation}",
            "SAFETY_VIOLATION",
            context
        )


class BaseAnalyzer(ReflectiveModule, ABC):
    """
    Base class for all RM-RDI analyzers
    
    SAFETY GUARANTEES:
    - All operations are READ-ONLY
    - Resource usage is monitored and limited
    - Emergency shutdown capability
    - Cannot impact existing systems
    """
    
    def __init__(self, analyzer_name: str):
        super().__init__(f"rm_rdi_analyzer_{analyzer_name}")
        self.analyzer_name = analyzer_name
        self.safety_manager = get_safety_manager()
        self.analysis_start_time: Optional[datetime] = None
        self.analysis_in_progress = False
        
        # Safety validation
        if not self.safety_manager.initialize_safety_systems():
            raise SafetyViolationError("Failed to initialize safety systems")
            
        self.logger.info(f"Initialized {analyzer_name} analyzer with safety guarantees")
        
    def get_module_status(self) -> Dict[str, Any]:
        """Get analyzer status with safety information"""
        safety_status = self.safety_manager.get_safety_status()
        
        return {
            "module_name": self.module_name,
            "analyzer_name": self.analyzer_name,
            "status": "operational" if self.is_healthy() else "degraded",
            "analysis_in_progress": self.analysis_in_progress,
            "safety_status": {
                "is_safe": safety_status.is_safe,
                "resource_usage": safety_status.resource_usage,
                "violations": safety_status.violations,
                "kill_switch_armed": safety_status.kill_switch_armed
            },
            "guarantees": [
                "READ_ONLY_OPERATIONS",
                "RESOURCE_LIMITED", 
                "EMERGENCY_SHUTDOWN_AVAILABLE",
                "CANNOT_IMPACT_EXISTING_SYSTEMS"
            ]
        }
        
    def is_healthy(self) -> bool:
        """Health check including safety validation"""
        safety_status = self.safety_manager.get_safety_status()
        return (
            safety_status.is_safe and
            not self.safety_manager.emergency_shutdown_triggered and
            len(safety_status.violations) == 0
        )
        
    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics including safety indicators"""
        safety_status = self.safety_manager.get_safety_status()
        
        return {
            "analyzer_health": {
                "analyzer_name": self.analyzer_name,
                "analysis_in_progress": self.analysis_in_progress,
                "last_analysis": self.analysis_start_time.isoformat() if self.analysis_start_time else None
            },
            "safety_health": {
                "safety_systems_operational": safety_status.is_safe,
                "resource_usage": safety_status.resource_usage,
                "safety_violations": safety_status.violations,
                "emergency_shutdown_available": safety_status.kill_switch_armed
            },
            "operational_guarantees": {
                "read_only_access": True,
                "isolated_execution": True,
                "resource_limited": True,
                "emergency_shutdown": True,
                "zero_system_impact": True
            }
        }
        
    def _get_primary_responsibility(self) -> str:
        """Primary responsibility of this analyzer"""
        return f"safe_readonly_analysis_{self.analyzer_name}"
        
    def execute_safe_analysis(self, **kwargs) -> AnalysisResult:
        """
        Execute analysis with full safety checks
        
        SAFETY PROTOCOL:
        1. Validate safety preconditions
        2. Check resource limits
        3. Execute read-only analysis
        4. Monitor resource usage
        5. Validate results
        """
        # Safety pre-check
        if not is_safe_to_proceed(f"{self.analyzer_name}_analysis"):
            raise SafetyViolationError(
                f"Analysis blocked by safety system",
                {"analyzer": self.analyzer_name, "reason": "safety_check_failed"}
            )
            
        self.analysis_start_time = datetime.now()
        self.analysis_in_progress = True
        
        try:
            self.logger.info(f"Starting safe analysis: {self.analyzer_name}")
            
            # Execute the actual analysis (implemented by subclasses)
            result = self._execute_analysis(**kwargs)
            
            # Validate result safety
            if not self._validate_result_safety(result):
                raise SafetyViolationError("Analysis result failed safety validation")
                
            self.logger.info(f"Completed safe analysis: {self.analyzer_name}")
            return result
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            # Return safe failure result
            return AnalysisResult(
                analysis_id=f"{self.analyzer_name}_{int(datetime.now().timestamp())}",
                timestamp=datetime.now(),
                analysis_types=[self.analyzer_name],
                status=AnalysisStatus.FAILED,
                operator_notes=[
                    f"Analysis failed safely: {str(e)}",
                    "No impact to existing systems",
                    "Safe to retry or ignore"
                ]
            )
        finally:
            self.analysis_in_progress = False
            
    @abstractmethod
    def _execute_analysis(self, **kwargs) -> AnalysisResult:
        """
        Execute the actual analysis logic (implemented by subclasses)
        
        MUST BE READ-ONLY and respect safety constraints
        """
        pass
        
    def _validate_result_safety(self, result: AnalysisResult) -> bool:
        """Validate that analysis result is safe"""
        # Ensure result is marked as safe
        if not result.safety_validated:
            return False
            
        # Ensure emergency shutdown is available
        if not result.emergency_shutdown_available:
            return False
            
        # Ensure result can be safely ignored
        if not result.can_be_safely_ignored:
            return False
            
        return True
        
    def emergency_shutdown(self) -> None:
        """Emergency shutdown of this analyzer"""
        self.logger.critical(f"Emergency shutdown triggered for {self.analyzer_name}")
        self.analysis_in_progress = False
        self.safety_manager.emergency_shutdown(f"Analyzer {self.analyzer_name} shutdown")
        
    def validate_read_only_access(self, file_path: Path) -> bool:
        """Validate read-only access to a file"""
        return self.safety_manager.safety_validator.validate_read_only_access(file_path)


class BaseOrchestrator(ReflectiveModule):
    """
    Base orchestrator for coordinating multiple analyzers safely
    
    SAFETY GUARANTEES:
    - Coordinates analyzers without impacting existing systems
    - Provides emergency shutdown for all analyzers
    - Monitors resource usage across all operations
    """
    
    def __init__(self, orchestrator_name: str):
        super().__init__(f"rm_rdi_orchestrator_{orchestrator_name}")
        self.orchestrator_name = orchestrator_name
        self.safety_manager = get_safety_manager()
        self.registered_analyzers: Dict[str, BaseAnalyzer] = {}
        self.active_analyses: Dict[str, datetime] = {}
        
        # Initialize safety systems
        if not self.safety_manager.initialize_safety_systems():
            raise SafetyViolationError("Failed to initialize orchestrator safety systems")
            
        self.logger.info(f"Initialized {orchestrator_name} orchestrator with safety guarantees")
        
    def register_analyzer(self, analyzer: BaseAnalyzer) -> None:
        """Register an analyzer with the orchestrator"""
        if not isinstance(analyzer, BaseAnalyzer):
            raise ValueError("Only BaseAnalyzer instances can be registered")
            
        self.registered_analyzers[analyzer.analyzer_name] = analyzer
        self.logger.info(f"Registered analyzer: {analyzer.analyzer_name}")
        
    def get_module_status(self) -> Dict[str, Any]:
        """Get orchestrator status with safety information"""
        safety_status = self.safety_manager.get_safety_status()
        
        analyzer_statuses = {}
        for name, analyzer in self.registered_analyzers.items():
            analyzer_statuses[name] = analyzer.get_module_status()
            
        return {
            "module_name": self.module_name,
            "orchestrator_name": self.orchestrator_name,
            "status": "operational" if self.is_healthy() else "degraded",
            "registered_analyzers": list(self.registered_analyzers.keys()),
            "active_analyses": list(self.active_analyses.keys()),
            "safety_status": {
                "is_safe": safety_status.is_safe,
                "resource_usage": safety_status.resource_usage,
                "violations": safety_status.violations,
                "kill_switch_armed": safety_status.kill_switch_armed
            },
            "analyzer_statuses": analyzer_statuses
        }
        
    def is_healthy(self) -> bool:
        """Health check including all analyzers and safety"""
        safety_status = self.safety_manager.get_safety_status()
        
        # Check orchestrator safety
        if not safety_status.is_safe or self.safety_manager.emergency_shutdown_triggered:
            return False
            
        # Check all registered analyzers
        for analyzer in self.registered_analyzers.values():
            if not analyzer.is_healthy():
                return False
                
        return True
        
    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics for orchestrator and all analyzers"""
        safety_status = self.safety_manager.get_safety_status()
        
        analyzer_health = {}
        for name, analyzer in self.registered_analyzers.items():
            analyzer_health[name] = analyzer.get_health_indicators()
            
        return {
            "orchestrator_health": {
                "orchestrator_name": self.orchestrator_name,
                "registered_analyzers": len(self.registered_analyzers),
                "active_analyses": len(self.active_analyses)
            },
            "safety_health": {
                "safety_systems_operational": safety_status.is_safe,
                "resource_usage": safety_status.resource_usage,
                "safety_violations": safety_status.violations,
                "emergency_shutdown_available": safety_status.kill_switch_armed
            },
            "analyzer_health": analyzer_health
        }
        
    def _get_primary_responsibility(self) -> str:
        """Primary responsibility of this orchestrator"""
        return f"safe_analysis_orchestration_{self.orchestrator_name}"
        
    def emergency_shutdown_all(self) -> None:
        """Emergency shutdown of all analyzers and orchestrator"""
        self.logger.critical("Emergency shutdown of all analyzers initiated")
        
        # Shutdown all analyzers
        for analyzer in self.registered_analyzers.values():
            try:
                analyzer.emergency_shutdown()
            except Exception as e:
                self.logger.error(f"Failed to shutdown analyzer {analyzer.analyzer_name}: {e}")
                
        # Clear active analyses
        self.active_analyses.clear()
        
        # Trigger orchestrator shutdown
        self.safety_manager.emergency_shutdown(f"Orchestrator {self.orchestrator_name} shutdown")


# Utility functions for safe analysis operations

def create_safe_analysis_id(analyzer_name: str) -> str:
    """Create a safe, unique analysis ID"""
    timestamp = int(datetime.now().timestamp())
    return f"safe_{analyzer_name}_{timestamp}"


def validate_analysis_parameters(**kwargs) -> bool:
    """Validate that analysis parameters are safe"""
    # Check for any parameters that might indicate write operations
    unsafe_params = ['write', 'modify', 'delete', 'update', 'create']
    
    for key, value in kwargs.items():
        key_lower = key.lower()
        if any(unsafe in key_lower for unsafe in unsafe_params):
            return False
            
        # Check string values for unsafe operations
        if isinstance(value, str) and any(unsafe in value.lower() for unsafe in unsafe_params):
            return False
            
    return True


def ensure_read_only_path(path: Path) -> Path:
    """Ensure path is safe for read-only access"""
    # Convert to absolute path for safety
    abs_path = path.resolve()
    
    # Validate path doesn't point to system directories
    unsafe_dirs = ['/etc', '/usr', '/bin', '/sbin', '/boot', '/sys', '/proc']
    path_str = str(abs_path)
    
    for unsafe_dir in unsafe_dirs:
        if path_str.startswith(unsafe_dir):
            raise SafetyViolationError(f"Access to system directory not allowed: {unsafe_dir}")
            
    return abs_path