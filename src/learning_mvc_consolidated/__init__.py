"""
🎯 LEARNING MVC CONSOLIDATED MODULES
===================================
Consolidated modules for Learning MVC System.
Split from monolithic file for better maintainability.

Modules:
- page_types: Page type enumeration
- telemetry: Telemetry event and analysis classes
- learning_state: Learning state management
- collector: Telemetry collection
- analyzer: Page analysis and curiosity
- mvc_system: Main MVC system

Author: Beast Mode Framework
Date: 2025-01-27
Version: 2.0
"""

from .page_types import PageType
from .telemetry import TelemetryEvent, PageAnalysis
from .learning_state import LearningState
from .collector import TelemetryCollector
from .analyzer import CuriousPageAnalyzer
from .mvc_system import LearningMVCSystem

__all__ = [
    "PageType",
    "TelemetryEvent",
    "PageAnalysis", 
    "LearningState",
    "TelemetryCollector",
    "CuriousPageAnalyzer",
    "LearningMVCSystem"
]
