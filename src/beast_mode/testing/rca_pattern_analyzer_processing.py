"""
Rca Pattern Analyzer Processing

This module was extracted from rca_pattern_analyzer.py
as part of RM-DDD compliance refactoring.
"""

import re
import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from ..core.reflective_module import ReflectiveModule

def _convert_logging_to_pattern_result(self, analysis: LoggingAnalysis) -> PatternAnalysisResult:
    """Convert logging analysis to pattern result"""
    return PatternAnalysisResult(pattern_type=f'logging_deficiency_{analysis.deficiency_type.value}', confidence_score=0.9, evidence=[f'Logging deficiency detected: {analysis.deficiency_type.value}', f'Severity: {analysis.severity}', f"Affected modules: {', '.join(analysis.affected_modules)}"], root_causes=['Insufficient logging infrastructure', 'Missing debug information', 'Inadequate error tracing'], recommended_actions=['Implement comprehensive logging framework', f'Set log level to {analysis.recommended_log_level}', 'Add contextual logging to all critical paths'] + analysis.suggested_improvements, priority='HIGH', estimated_fix_time='1-2 hours', related_patterns=[])

def _convert_profiling_to_pattern_result(self, analysis: ProfilingAnalysis) -> PatternAnalysisResult:
    """Convert profiling analysis to pattern result"""
    return PatternAnalysisResult(pattern_type=f'profiling_deficiency_{analysis.deficiency_type.value}', confidence_score=0.85, evidence=[f'Profiling deficiency detected: {analysis.deficiency_type.value}', f'Impact level: {analysis.impact_level}', f"Missing metrics: {', '.join(analysis.missing_metrics)}"], root_causes=['Missing performance monitoring infrastructure', 'Inadequate profiling setup', 'No performance baseline established'], recommended_actions=['Enable comprehensive profiling', 'Implement performance monitoring', 'Establish performance baselines'] + [f'Add {metric} tracking' for metric in analysis.suggested_metrics], priority='HIGH', estimated_fix_time='2-3 hours', related_patterns=[])
