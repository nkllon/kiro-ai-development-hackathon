"""
Rca Integration Services Processing

This module was extracted from rca_integration_services.py
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

def convert_to_rca_failure(self, test_failure: TestFailureData) -> Failure:
    """
        Convert TestFailure object to RCA-compatible Failure object
        Requirements: 4.1 - Integration with existing RCAEngine
        """
    try:
        failure_id = f'test_{hashlib.md5(test_failure.pytest_node_id.encode()).hexdigest()[:8]}'
        category = self._categorize_test_failure(test_failure)
        context = {'test_file': test_failure.test_file, 'test_function': test_failure.test_function, 'test_class': test_failure.test_class, 'pytest_node_id': test_failure.pytest_node_id, 'failure_type': test_failure.failure_type, 'test_context': test_failure.test_context, 'analysis_source': 'test_rca_integrator'}
        return Failure(failure_id=failure_id, timestamp=test_failure.failure_timestamp, component=f'test:{test_failure.test_file}', error_message=test_failure.error_message, stack_trace=test_failure.stack_trace, context=context, category=category)
    except Exception as e:
        self.logger.error(f'Failed to convert test failure to RCA failure: {e}')
        return Failure(failure_id=f'test_conversion_failed_{int(time.time())}', timestamp=datetime.now(), component='test:unknown', error_message=f'Conversion failed: {e}', stack_trace=None, context={'conversion_error': str(e)}, category=FailureCategory.UNKNOWN)
