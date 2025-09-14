"""
Rca Report Generator Core Core Utils

This module was extracted from rca_report_generator_core_core.py
as part of RM-DDD compliance refactoring.
"""

import json
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from ..core.reflective_module import ReflectiveModule, HealthStatus
from ..analysis.rca_engine import RCAResult, RootCauseType, PreventionPattern
from .rca_integration import TestFailureData, TestRCASummaryData, TestRCAReportData
from src.rm_ddd.core.health import ModuleHealth


class FormatforconsoleClass:
    """Auto-generated class for functions."""

    def format_for_console(self, rca_report: TestRCAReportData, use_colors: bool=True) -> str:
    """
    Format RCA report for console output with clear sections
    Requirements: 2.3 - Console output formatting with clear sections
    """
    try:
    config = ReportConfiguration(format=ReportFormat.CONSOLE, color_output=use_colors, include_sections=list(ReportSection))
    formatted_report = self.generate_report(rca_report, config)
    console_output = []
    for section in formatted_report.sections:
    console_output.append(section.content)
    console_output.append('')
    return '\n'.join(console_output)
    except Exception as e:
    self.logger.error(f'Console formatting failed: {e}')
    return f'Console formatting error: {e}'

    def register_module(self, registry):
    """Register module with registry."""
    metadata = self.get_interface_metadata()
    if hasattr(registry, 'register'):
    registry.register(metadata)

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

