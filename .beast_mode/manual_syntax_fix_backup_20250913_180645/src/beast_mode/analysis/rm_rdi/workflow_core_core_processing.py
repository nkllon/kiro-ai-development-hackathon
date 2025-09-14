"""
Workflow Core Core Processing

This module was extracted from workflow_core_core.py
as part of RM-DDD compliance refactoring.
"""

from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
from .data_models import AnalysisResult, AnalysisStatus
from .safety import get_safety_manager

def _post_process_results(self, aggregated_result: AggregatedResult) -> None:
    """Post-process aggregated results"""
    aggregated_result.summary['post_processing'] = {'processed_at': datetime.now().isoformat(), 'total_execution_time': sum((result.execution_time for result in aggregated_result.step_results.values())), 'step_count': len(aggregated_result.step_results)}
    if not self._validate_result_safety(aggregated_result):
        raise SafetyViolationError('Aggregated result failed safety validation')
