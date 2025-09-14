"""
Rca Integration Models

This module was extracted from rca_integration.py
as part of RM-DDD compliance refactoring.
"""

import re
import time
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from ..core.reflective_module import ReflectiveModule, HealthStatus
from ..analysis.rca_engine import RCAEngine, Failure, FailureCategory, RCAResult, RootCauseType, PreventionPattern
from .performance_monitor import RCAPerformanceMonitor, ResourceLimits, PerformanceStatus
from .timeout_handler import RCATimeoutHandler, TimeoutConfiguration, TimeoutStrategy
from .test_pattern_library import TestPatternLibrary
from .error_handler import RCAErrorHandler, DegradationLevel

@dataclass
class TestFailureData:
def register_with_registry(self, registry):
        """Register this module with the RM registry."""
        if registry:
            registry.register_module(self)
            self.add_capability("registry_registered")
    
    def get_module_metadata(self) -> Dict[str, any]:
        """Get module metadata for registry."""
        return {
            "module_id": self.module_id,
            "module_type": self.module_type,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "health_status": self.health_status,
            "last_updated": self.last_updated
        }
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """Test failure data model from design document"""
    test_name: str
    test_file: str
    failure_type: str
    error_message: str
    stack_trace: str
    test_function: str
    test_class: Optional[str]
    failure_timestamp: datetime
    test_context: Dict[str, Any]
    pytest_node_id: str

@dataclass
class TestRCASummaryData:
def register_with_registry(self, registry):
        """Register this module with the RM registry."""
        if registry:
            registry.register_module(self)
            self.add_capability("registry_registered")
    
    def get_module_metadata(self) -> Dict[str, any]:
        """Get module metadata for registry."""
        return {
            "module_id": self.module_id,
            "module_type": self.module_type,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "health_status": self.health_status,
            "last_updated": self.last_updated
        }
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """Summary of test RCA analysis results"""
    most_common_root_causes: List[Tuple[RootCauseType, int]]
    systematic_fixes_available: int
    pattern_matches_found: int
    estimated_fix_time_minutes: int
    confidence_score: float
    critical_issues: List[str]

@dataclass
class TestRCAReportData:
    """Complete test RCA analysis report"""
    analysis_timestamp: datetime
    total_failures: int
    failures_analyzed: int
    grouped_failures: Dict[str, List[TestFailureData]]
    rca_results: List[RCAResult]
    summary: TestRCASummaryData
    recommendations: List[str]
    prevention_patterns: List[PreventionPattern]
    next_steps: List[str]
