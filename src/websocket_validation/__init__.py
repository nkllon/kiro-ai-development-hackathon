"""
WebSocket Implementation Validation Framework

A systematic framework for validating or refuting WebSocket implementation claims
through comprehensive testing, analysis, and evidence collection.
"""

__version__ = "1.0.0"
__author__ = "WebSocket Validation Team"

from .engine import ValidationEngine
from .models import ValidationReport, TestResult, Evidence
from .collectors import EvidenceCollector

__all__ = [
    "ValidationEngine",
    "ValidationReport", 
    "TestResult",
    "Evidence",
    "EvidenceCollector"
]