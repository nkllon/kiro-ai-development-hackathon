"""
Systematic Metrics Engine Models

This module was extracted from systematic_metrics_engine.py
as part of RM-DDD compliance refactoring.
"""

import logging
import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import time
from ..core.reflective_module import ReflectiveModule

@dataclass
class MetricDataPoint:
    """A single metric measurement with Systo's systematic tracking"""
    timestamp: datetime
    metric_name: str
    value: float
    approach_type: str
    context: Dict[str, Any]
    confidence_score: float = 1.0
