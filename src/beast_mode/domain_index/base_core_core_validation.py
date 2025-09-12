"""
Base Core Core Validation

This module was extracted from base_core_core.py
as part of RM-DDD compliance refactoring.
"""

import logging
import time
from abc import ABC
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
from ..core.reflective_module import ReflectiveModule, HealthStatus as RMHealthStatus
from .models import HealthStatus, HealthStatusType, HealthIssue, HealthMetrics, IssueSeverity, IssueCategory
import json
import json
import json
import json
import json
import json

def _validate_config(self) -> List[str]:
    """Validate component configuration"""
    issues = []
    if self.cache_ttl <= 0:
        issues.append('cache_ttl_seconds must be positive')
    if self.max_retries < 0:
        issues.append('max_retries must be non-negative')
    if self.timeout_seconds <= 0:
        issues.append('timeout_seconds must be positive')
    return issues
