"""
Test Pattern Library Core Validation

This module was extracted from test_pattern_library_core.py
as part of RM-DDD compliance refactoring.
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from ..core.reflective_module import ReflectiveModule, HealthStatus
from ..analysis.rca_engine import PreventionPattern, Failure, RootCause, SystematicFix
from src.rm_ddd.core.health import ModuleHealth


class MatchtestpatternsClass:
    """Auto-generated class for functions."""

    def match_test_patterns(self, failure: Failure) -> List[PreventionPattern]:
    """
    High-performance test pattern matching with sub-second requirement
    Requirement 4.2: Sub-second performance for pattern matching
    """
    start_time = time.time()
    matching_patterns = []
    try:
    failure_signature = self._generate_test_failure_signature(failure)
    failure_hash = hashlib.md5(failure_signature.encode()).hexdigest()[:8]
    if failure_hash in self.pattern_hash_index:
    self.cache_hits += 1
    candidate_pattern_ids = self.pattern_hash_index[failure_hash]
    for pattern_id in candidate_pattern_ids:
    if pattern_id in self.test_patterns:
    pattern = self.test_patterns[pattern_id]
    if self._verify_test_pattern_match(failure, pattern):
    matching_patterns.append(pattern)
    self._update_pattern_metrics(pattern_id, True)
    else:
    self.cache_misses += 1
    if not matching_patterns:
    component = failure.component
    if component in self.component_index:
    candidate_pattern_ids = self.component_index[component]
    for pattern_id in candidate_pattern_ids:
    if pattern_id in self.test_patterns:
    pattern = self.test_patterns[pattern_id]
    if self._verify_test_pattern_match(failure, pattern):
    matching_patterns.append(pattern)
    self._update_pattern_metrics(pattern_id, True)
    match_time_ms = (time.time() - start_time) * 1000
    self.total_matches_performed += 1
    self.total_match_time_ms += match_time_ms
    self.logger.info(f'Test pattern matching completed in {match_time_ms:.2f}ms, found {len(matching_patterns)} matches')
    if match_time_ms > 1000:
    self.logger.warning(f'Test pattern matching exceeded 1 second: {match_time_ms:.2f}ms')
    self._trigger_performance_optimization()
    return matching_patterns
    except Exception as e:
    self.logger.error(f'Test pattern matching failed: {e}')
    return []

    def _load_test_patterns(self):
    """Load test-specific patterns from disk"""
    try:
    if Path(self.test_patterns_path).exists():
    with open(self.test_patterns_path, 'r') as f:
    data = json.load(f)
    for pattern_data in data.get('test_patterns', []):
    pattern = PreventionPattern(**pattern_data)
    self.test_patterns[pattern.pattern_id] = pattern
    self.logger.info(f'Loaded {len(self.test_patterns)} test-specific patterns')
    except Exception as e:
    self.logger.warning(f'Failed to load test patterns: {e}')

    def _save_test_patterns(self):
    """Save test-specific patterns to disk"""
    try:
    Path(self.test_patterns_path).parent.mkdir(parents=True, exist_ok=True)
    patterns_data = []
    for pattern in self.test_patterns.values():
    patterns_data.append({'pattern_id': pattern.pattern_id, 'pattern_name': pattern.pattern_name, 'failure_signature': pattern.failure_signature, 'root_cause_pattern': pattern.root_cause_pattern, 'prevention_steps': pattern.prevention_steps, 'detection_criteria': pattern.detection_criteria, 'automated_checks': pattern.automated_checks, 'pattern_hash': pattern.pattern_hash})
    data = {'test_patterns': patterns_data, 'last_updated': datetime.now().isoformat(), 'pattern_count': len(patterns_data)}
    with open(self.test_patterns_path, 'w') as f:
    json.dump(data, f, indent=2)
    except Exception as e:
    self.logger.error(f'Failed to save test patterns: {e}')

    def _generate_test_failure_signature(self, failure: Failure) -> str:
    """Generate test-specific failure signature for pattern matching"""
    signature_parts = [f'test:{failure.component}', failure.category.value if failure.category else 'unknown', failure.error_message[:200], str(sorted(failure.context.keys())) if failure.context else '[]']
    return '|'.join(signature_parts)

    def _verify_test_pattern_match(self, failure: Failure, pattern: PreventionPattern) -> bool:
    """Verify if failure matches test pattern with enhanced matching logic"""
    failure_signature = self._generate_test_failure_signature(failure)
    signature_parts = pattern.failure_signature.split('|')
    failure_parts = failure_signature.split('|')
    if len(signature_parts) >= 3 and len(failure_parts) >= 3:
    component_match = signature_parts[0] in failure_parts[0] or failure_parts[0] in signature_parts[0]
    error_type_match = signature_parts[1] == failure_parts[1]
    error_msg_similarity = self._calculate_message_similarity(signature_parts[2], failure_parts[2])
    return component_match and error_type_match and (error_msg_similarity > 0.7)
    return False

    def _classify_test_pattern(self, pattern: PreventionPattern) -> TestPatternType:
    """Classify test pattern by type"""
    signature = pattern.failure_signature.lower()
    if 'importerror' in signature:
    return TestPatternType.PYTEST_IMPORT_ERROR
    elif 'assertionerror' in signature:
    return TestPatternType.PYTEST_ASSERTION_FAILURE
    elif 'fixture' in signature:
    return TestPatternType.PYTEST_FIXTURE_ERROR
    elif 'timeout' in signature:
    return TestPatternType.PYTEST_TIMEOUT
    elif 'makefile' in signature or 'make' in signature:
    if 'syntax' in signature:
    return TestPatternType.MAKEFILE_SYNTAX_ERROR
    else:
    return TestPatternType.MAKEFILE_TARGET_ERROR
    elif 'permission' in signature:
    return TestPatternType.INFRASTRUCTURE_PERMISSION
    elif 'network' in signature or 'connection' in signature:
    return TestPatternType.INFRASTRUCTURE_NETWORK
    elif 'resource' in signature:
    return TestPatternType.INFRASTRUCTURE_RESOURCE
    else:
    return TestPatternType.TEST_ENVIRONMENT_SETUP

    def _add_new_test_pattern(self, pattern: PreventionPattern):
    """Add new test pattern to library"""
    pattern_type = self._classify_test_pattern(pattern)
    type_patterns = self.pattern_type_index.get(pattern_type, [])
    if len(type_patterns) >= self.max_patterns_per_type:
    self._remove_least_effective_pattern(pattern_type)
    self.test_patterns[pattern.pattern_id] = pattern
    self.pattern_metrics[pattern.pattern_id] = TestPatternMetrics(pattern_id=pattern.pattern_id)
    self._build_performance_indexes()
    self._save_test_patterns()
    self._save_pattern_metrics()

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

