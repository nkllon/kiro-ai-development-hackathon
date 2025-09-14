"""
Code Quality Core Core Validation

This module was extracted from code_quality_core_core.py
as part of RM-DDD compliance refactoring.
"""

import ast
import re
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from ..core.interfaces import GhostbustersExpertAgent
from ..core.models import AnalysisResult, AnalysisContext, Finding, Recommendation, FindingType, Severity, CodeLocation
from src.rm_ddd.core.health import ModuleHealth


def validate_confidence(self, result: AnalysisResult) -> bool:
    """Validate confidence score accuracy"""
    if not 0.0 <= result.confidence <= 1.0:
        return False
    if result.confidence > 0.8:
        return len(result.findings) > 0 or result.metadata.get('lines_analyzed', 0) > 0
    if result.confidence < 0.3:
        return any((f.severity == Severity.CRITICAL for f in result.findings))
    return True
