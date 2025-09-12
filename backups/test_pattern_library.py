"""
Beast Mode Framework - Test-Specific Pattern Library Integration
Implements Task 9: Add Test-Specific Pattern Library Integration
Requirements: 2.4, 4.2, 4.4 - Pattern learning, sub-second performance, prevention patterns
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

class TestPatternType(Enum):
    """Test-specific pattern types for categorization"""
    PYTEST_IMPORT_ERROR = "pytest_import_error"
    PYTEST_ASSERTION_FAILURE = "pytest_assertion_failure"
    PYTEST_FIXTURE_ERROR = "pytest_fixture_error"
    PYTEST_TIMEOUT = "pytest_timeout"
    PYTEST_SETUP_ERROR = "pytest_setup_error"
    MAKEFILE_TARGET_ERROR = "makefile_target_error"
    MAKEFILE_SYNTAX_ERROR = "makefile_syntax_error"
    BUILD_DEPENDENCY_ERROR = "build_dependency_error"
    INFRASTRUCTURE_PERMISSION = "infrastructure_permission"
    INFRASTRUCTURE_NETWORK = "infrastructure_network"
    INFRASTRUCTURE_RESOURCE = "infrastructure_resource"
    TEST_ENVIRONMENT_SETUP = "test_environment_setup"
    TEST_DATA_CORRUPTION = "test_data_corruption"

@dataclass
class TestPatternMetrics:
    """Metrics for test pattern performance and effectiveness"""
    pattern_id: str
    match_count: int = 0
    successful_applications: int = 0
    average_match_time_ms: float = 0.0
    last_matched: Optional[datetime] = None
    effectiveness_score: float = 0.0
    false_positive_count: int = 0

@dataclass
class TestPatternLearning:
    """Learning data from successful RCA analyses"""
    pattern_id: str
    source_failure_signature: str
    successful_fix_applied: bool
    fix_validation_score: float
    learning_timestamp: datetime
    context_factors: Dict[str, Any]
    generalization_potential: float

class TestPatternLibrary(ReflectiveModule):
    """
    Test-specific pattern library with learning and optimization
    Extends existing pattern library with test-focused functionality
    Requirements: 2.4 (prevention patterns), 4.2 (sub-second performance), 4.4 (pattern learning)
    """
    
    def __init__(self, base_pattern_library_path: str = "patterns/rca_patterns.json"):
        super().__init__("test_pattern_library")
        
        # Pattern storage paths
        self.base_pattern_library_path = base_pattern_library_path
        self.test_patterns_path = "patterns/test_specific_patterns.json"
        self.pattern_metrics_path = "patterns/test_pattern_metrics.json"
        self.learning_data_path = "patterns/test_pattern_learning.json"
        
        # Test-specific pattern storage
        self.test_patterns: Dict[str, PreventionPattern] = {}
        self.pattern_metrics: Dict[str, TestPatternMetrics] = {}
        self.learning_data: List[TestPatternLearning] = []
        
        # Performance optimization structures
        self.pattern_hash_index: Dict[str, List[str]] = {}  # Hash -> pattern_ids
        self.pattern_type_index: Dict[TestPatternType, List[str]] = {}  # Type -> pattern_ids
        self.component_index: Dict[str, List[str]] = {}  # Component -> pattern_ids
        
        # Performance metrics
        self.total_matches_performed = 0
        self.total_match_time_ms = 0.0
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Pattern learning configuration
        self.learning_threshold = 0.8  # Minimum fix validation score for learning
        self.max_patterns_per_type = 100  # Prevent unbounded growth
        self.cleanup_interval_hours = 24
        self.last_cleanup = datetime.now()
        
        # Load existing data
        self._load_test_patterns()
        self._load_pattern_metrics()
        self._load_learning_data()
        self._build_performance_indexes()
        
        self._update_health_indicator(
            "test_pattern_library_ready",
            HealthStatus.HEALTHY,
            f"loaded_{len(self.test_patterns)}_test_patterns",
            "Test pattern library ready for high-performance matching"
        )
        
    def get_module_status(self) -> Dict[str, Any]:
        """Operational visibility for test pattern library"""
        avg_match_time = self.total_match_time_ms / max(1, self.total_matches_performed)
        cache_hit_rate = self.cache_hits / max(1, self.cache_hits + self.cache_misses)
        
        return {
            "module_name": self.module_name,
            "status": "operational" if self.is_healthy() else "degraded",
            "test_patterns_count": len(self.test_patterns),
            "total_matches_performed": self.total_matches_performed,
            "average_match_time_ms": avg_match_time,
            "cache_hit_rate": cache_hit_rate,
            "learning_samples": len(self.learning_data),
            "performance_target_met": avg_match_time < 1000,  # Sub-second requirement
            "degradation_active": self._degradation_active
        }
        
    def is_healthy(self) -> bool:
        """Health assessment for test pattern library"""
        avg_match_time = self.total_match_time_ms / max(1, self.total_matches_performed)
        return not self._degradation_active and avg_match_time < 1000
        
    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics for operational visibility"""
        avg_match_time = self.total_match_time_ms / max(1, self.total_matches_performed)
        cache_hit_rate = self.cache_hits / max(1, self.cache_hits + self.cache_misses)
        
        return {
            "pattern_library_health": {
                "status": "healthy" if not self._degradation_active else "degraded",
                "pattern_count": len(self.test_patterns),
                "learning_samples": len(self.learning_data)
            },
            "performance_health": {
                "status": "healthy" if avg_match_time < 1000 else "degraded",
                "average_match_time_ms": avg_match_time,
                "sub_second_compliance": avg_match_time < 1000,
                "cache_hit_rate": cache_hit_rate
            },
            "learning_health": {
                "status": "healthy" if len(self.learning_data) > 0 else "degraded",
                "learning_samples": len(self.learning_data),
                "patterns_learned": len([r for r in self.learning_data if r.successful_fix_applied])
            }
        }
        
    def match_test_patterns(self, failure: Failure) -> List[PreventionPattern]:
        """
        High-performance test pattern matching with sub-second requirement
        Requirement 4.2: Sub-second performance for pattern matching
        """
        start_time = time.time()
        matching_patterns = []
        
        try:
            # Generate failure signature for matching
            failure_signature = self._generate_test_failure_signature(failure)
            failure_hash = hashlib.md5(failure_signature.encode()).hexdigest()[:8]
            
            # Fast hash-based lookup
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
                
            # Fallback to component-based matching if no hash matches
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
                                
            # Update performance metrics
            match_time_ms = (time.time() - start_time) * 1000
            self.total_matches_performed += 1
            self.total_match_time_ms += match_time_ms
            
            self.logger.info(f"Test pattern matching completed in {match_time_ms:.2f}ms, found {len(matching_patterns)} matches")
            
            # Ensure sub-second performance (Requirement 4.2)
            if match_time_ms > 1000:
                self.logger.warning(f"Test pattern matching exceeded 1 second: {match_time_ms:.2f}ms")
                self._trigger_performance_optimization()
                
            return matching_patterns
            
        except Exception as e:
            self.logger.error(f"Test pattern matching failed: {e}")
            return []
            
    def learn_from_successful_rca(self, failure: Failure, root_causes: List[RootCause], 
                                 systematic_fixes: List[SystematicFix], validation_score: float) -> bool:
        """
        Learn patterns from successful RCA analyses
        Requirement 2.4: Document prevention patterns from successful analyses
        """
        try:
            # Only learn from high-quality fixes
            if validation_score < self.learning_threshold:
                self.logger.debug(f"Skipping pattern learning - validation score {validation_score} below threshold {self.learning_threshold}")
                return False
                
            # Generate pattern from successful analysis
            new_pattern = self._generate_pattern_from_rca(failure, root_causes, systematic_fixes)
            
            if new_pattern:
                # Check if similar pattern already exists
                existing_pattern = self._find_similar_pattern(new_pattern)
                
                if existing_pattern:
                    # Enhance existing pattern with new learning
                    self._enhance_existing_pattern(existing_pattern, new_pattern, validation_score)
                else:
                    # Add new pattern to library
                    self._add_new_test_pattern(new_pattern)
                    
                # Record learning data
                learning_record = TestPatternLearning(
                    pattern_id=new_pattern.pattern_id,
                    source_failure_signature=new_pattern.failure_signature,
                    successful_fix_applied=True,
                    fix_validation_score=validation_score,
                    learning_timestamp=datetime.now(),
                    context_factors=failure.context,
                    generalization_potential=self._calculate_generalization_potential(failure, root_causes)
                )
                
                self.learning_data.append(learning_record)
                self._save_learning_data()
                
                self.logger.info(f"Learned new test pattern: {new_pattern.pattern_name}")
                return True
                
        except Exception as e:
            self.logger.error(f"Pattern learning failed: {e}")
            
        return False
        
    def optimize_pattern_performance(self) -> Dict[str, Any]:
        """
        Optimize pattern library for sub-second performance
        Requirement 4.2: Maintain sub-second pattern matching performance
        """
        optimization_results = {
            "patterns_before": len(self.test_patterns),
            "patterns_removed": 0,
            "indexes_rebuilt": 0,
            "performance_improvement": 0.0
        }
        
        try:
            # Record performance before optimization
            avg_time_before = self.total_match_time_ms / max(1, self.total_matches_performed)
            
            # Remove low-performing patterns
            patterns_to_remove = []
            for pattern_id, metrics in self.pattern_metrics.items():
                if (metrics.match_count > 10 and 
                    metrics.effectiveness_score < 0.3 and
                    metrics.false_positive_count > metrics.successful_applications):
                    patterns_to_remove.append(pattern_id)
                    
            for pattern_id in patterns_to_remove:
                self._remove_pattern(pattern_id)
                optimization_results["patterns_removed"] += 1
                
            # Rebuild performance indexes
            self._build_performance_indexes()
            optimization_results["indexes_rebuilt"] = 1
            
            # Calculate performance improvement
            avg_time_after = self.total_match_time_ms / max(1, self.total_matches_performed)
            optimization_results["performance_improvement"] = avg_time_before - avg_time_after
            
            optimization_results["patterns_after"] = len(self.test_patterns)
            
            self.logger.info(f"Pattern optimization complete: removed {optimization_results['patterns_removed']} patterns, "
                           f"performance improvement: {optimization_results['performance_improvement']:.2f}ms")
            
        except Exception as e:
            self.logger.error(f"Pattern optimization failed: {e}")
            
        return optimization_results
        
    def cleanup_pattern_library(self) -> Dict[str, Any]:
        """
        Perform maintenance and cleanup of pattern library
        Prevents unbounded growth and maintains performance
        """
        cleanup_results = {
            "duplicate_patterns_removed": 0,
            "stale_patterns_removed": 0,
            "learning_data_pruned": 0,
            "total_patterns_before": len(self.test_patterns),
            "total_patterns_after": 0
        }
        
        try:
            # Remove duplicate patterns
            duplicates = self._find_duplicate_patterns()
            for pattern_id in duplicates:
                self._remove_pattern(pattern_id)
                cleanup_results["duplicate_patterns_removed"] += 1
                
            # Remove stale patterns (not matched in 30 days)
            cutoff_date = datetime.now().replace(day=datetime.now().day - 30)
            stale_patterns = []
            
            for pattern_id, metrics in self.pattern_metrics.items():
                if (metrics.last_matched and 
                    metrics.last_matched < cutoff_date and
                    metrics.match_count < 5):
                    stale_patterns.append(pattern_id)
                    
            for pattern_id in stale_patterns:
                self._remove_pattern(pattern_id)
                cleanup_results["stale_patterns_removed"] += 1
                
            # Prune old learning data (keep last 1000 records)
            if len(self.learning_data) > 1000:
                self.learning_data.sort(key=lambda x: x.learning_timestamp, reverse=True)
                pruned_count = len(self.learning_data) - 1000
                self.learning_data = self.learning_data[:1000]
                cleanup_results["learning_data_pruned"] = pruned_count
                self._save_learning_data()
                
            cleanup_results["total_patterns_after"] = len(self.test_patterns)
            
            # Update last cleanup time
            self.last_cleanup = datetime.now()
            
            self.logger.info(f"Pattern library cleanup complete: "
                           f"removed {cleanup_results['duplicate_patterns_removed']} duplicates, "
                           f"{cleanup_results['stale_patterns_removed']} stale patterns")
            
        except Exception as e:
            self.logger.error(f"Pattern library cleanup failed: {e}")
            
        return cleanup_results
        
    def get_pattern_effectiveness_report(self) -> Dict[str, Any]:
        """
        Generate effectiveness report for test patterns
        Provides insights into pattern performance and learning
        """
        report = {
            "total_patterns": len(self.test_patterns),
            "total_matches": self.total_matches_performed,
            "average_match_time_ms": self.total_match_time_ms / max(1, self.total_matches_performed),
            "cache_hit_rate": self.cache_hits / max(1, self.cache_hits + self.cache_misses),
            "learning_samples": len(self.learning_data),
            "pattern_types": {},
            "top_performing_patterns": [],
            "performance_issues": []
        }
        
        # Analyze patterns by type
        type_counts = {}
        for pattern in self.test_patterns.values():
            pattern_type = self._classify_test_pattern(pattern)
            type_counts[pattern_type.value] = type_counts.get(pattern_type.value, 0) + 1
            
        report["pattern_types"] = type_counts
        
        # Find top performing patterns
        sorted_patterns = sorted(
            self.pattern_metrics.items(),
            key=lambda x: x[1].effectiveness_score,
            reverse=True
        )[:10]
        
        for pattern_id, metrics in sorted_patterns:
            if pattern_id in self.test_patterns:
                pattern = self.test_patterns[pattern_id]
                report["top_performing_patterns"].append({
                    "pattern_id": pattern_id,
                    "pattern_name": pattern.pattern_name,
                    "effectiveness_score": metrics.effectiveness_score,
                    "match_count": metrics.match_count,
                    "success_rate": metrics.successful_applications / max(1, metrics.match_count)
                })
                
        # Identify performance issues
        avg_match_time = report["average_match_time_ms"]
        if avg_match_time > 1000:
            report["performance_issues"].append(f"Average match time {avg_match_time:.2f}ms exceeds 1 second target")
            
        if report["cache_hit_rate"] < 0.7:
            report["performance_issues"].append(f"Cache hit rate {report['cache_hit_rate']:.2f} below optimal threshold")
            
        return report        

    # Private helper methods
    
    def _load_test_patterns(self):
        """Load test-specific patterns from disk"""
        try:
            if Path(self.test_patterns_path).exists():
                with open(self.test_patterns_path, 'r') as f:
                    data = json.load(f)
                    
                for pattern_data in data.get('test_patterns', []):
                    pattern = PreventionPattern(**pattern_data)
                    self.test_patterns[pattern.pattern_id] = pattern
                    
                self.logger.info(f"Loaded {len(self.test_patterns)} test-specific patterns")
        except Exception as e:
            self.logger.warning(f"Failed to load test patterns: {e}")
            
    def _save_test_patterns(self):
        """Save test-specific patterns to disk"""
        try:
            Path(self.test_patterns_path).parent.mkdir(parents=True, exist_ok=True)
            
            patterns_data = []
            for pattern in self.test_patterns.values():
                patterns_data.append({
                    'pattern_id': pattern.pattern_id,
                    'pattern_name': pattern.pattern_name,
                    'failure_signature': pattern.failure_signature,
                    'root_cause_pattern': pattern.root_cause_pattern,
                    'prevention_steps': pattern.prevention_steps,
                    'detection_criteria': pattern.detection_criteria,
                    'automated_checks': pattern.automated_checks,
                    'pattern_hash': pattern.pattern_hash
                })
                
            data = {
                'test_patterns': patterns_data,
                'last_updated': datetime.now().isoformat(),
                'pattern_count': len(patterns_data)
            }
            
            with open(self.test_patterns_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save test patterns: {e}")
            
    def _load_pattern_metrics(self):
        """Load pattern performance metrics"""
        try:
            if Path(self.pattern_metrics_path).exists():
                with open(self.pattern_metrics_path, 'r') as f:
                    data = json.load(f)
                    
                for metrics_data in data.get('metrics', []):
                    metrics = TestPatternMetrics(
                        pattern_id=metrics_data['pattern_id'],
                        match_count=metrics_data.get('match_count', 0),
                        successful_applications=metrics_data.get('successful_applications', 0),
                        average_match_time_ms=metrics_data.get('average_match_time_ms', 0.0),
                        last_matched=datetime.fromisoformat(metrics_data['last_matched']) if metrics_data.get('last_matched') else None,
                        effectiveness_score=metrics_data.get('effectiveness_score', 0.0),
                        false_positive_count=metrics_data.get('false_positive_count', 0)
                    )
                    self.pattern_metrics[metrics.pattern_id] = metrics
                    
        except Exception as e:
            self.logger.warning(f"Failed to load pattern metrics: {e}")
            
    def _save_pattern_metrics(self):
        """Save pattern performance metrics"""
        try:
            Path(self.pattern_metrics_path).parent.mkdir(parents=True, exist_ok=True)
            
            metrics_data = []
            for metrics in self.pattern_metrics.values():
                metrics_data.append({
                    'pattern_id': metrics.pattern_id,
                    'match_count': metrics.match_count,
                    'successful_applications': metrics.successful_applications,
                    'average_match_time_ms': metrics.average_match_time_ms,
                    'last_matched': metrics.last_matched.isoformat() if metrics.last_matched else None,
                    'effectiveness_score': metrics.effectiveness_score,
                    'false_positive_count': metrics.false_positive_count
                })
                
            data = {
                'metrics': metrics_data,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.pattern_metrics_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save pattern metrics: {e}")
            
    def _load_learning_data(self):
        """Load pattern learning data"""
        try:
            if Path(self.learning_data_path).exists():
                with open(self.learning_data_path, 'r') as f:
                    data = json.load(f)
                    
                for learning_data in data.get('learning_records', []):
                    record = TestPatternLearning(
                        pattern_id=learning_data['pattern_id'],
                        source_failure_signature=learning_data['source_failure_signature'],
                        successful_fix_applied=learning_data['successful_fix_applied'],
                        fix_validation_score=learning_data['fix_validation_score'],
                        learning_timestamp=datetime.fromisoformat(learning_data['learning_timestamp']),
                        context_factors=learning_data.get('context_factors', {}),
                        generalization_potential=learning_data.get('generalization_potential', 0.0)
                    )
                    self.learning_data.append(record)
                    
        except Exception as e:
            self.logger.warning(f"Failed to load learning data: {e}")
            
    def _save_learning_data(self):
        """Save pattern learning data"""
        try:
            Path(self.learning_data_path).parent.mkdir(parents=True, exist_ok=True)
            
            learning_records = []
            for record in self.learning_data:
                learning_records.append({
                    'pattern_id': record.pattern_id,
                    'source_failure_signature': record.source_failure_signature,
                    'successful_fix_applied': record.successful_fix_applied,
                    'fix_validation_score': record.fix_validation_score,
                    'learning_timestamp': record.learning_timestamp.isoformat(),
                    'context_factors': record.context_factors,
                    'generalization_potential': record.generalization_potential
                })
                
            data = {
                'learning_records': learning_records,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.learning_data_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save learning data: {e}")
            
    def _build_performance_indexes(self):
        """Build performance optimization indexes"""
        # Clear existing indexes
        self.pattern_hash_index.clear()
        self.pattern_type_index.clear()
        self.component_index.clear()
        
        for pattern_id, pattern in self.test_patterns.items():
            # Hash index for fast lookup
            pattern_hash = pattern.pattern_hash
            if pattern_hash not in self.pattern_hash_index:
                self.pattern_hash_index[pattern_hash] = []
            self.pattern_hash_index[pattern_hash].append(pattern_id)
            
            # Type index for categorized matching
            pattern_type = self._classify_test_pattern(pattern)
            if pattern_type not in self.pattern_type_index:
                self.pattern_type_index[pattern_type] = []
            self.pattern_type_index[pattern_type].append(pattern_id)
            
            # Component index for component-based matching
            component = self._extract_component_from_signature(pattern.failure_signature)
            if component:
                if component not in self.component_index:
                    self.component_index[component] = []
                self.component_index[component].append(pattern_id)
                
    def _generate_test_failure_signature(self, failure: Failure) -> str:
        """Generate test-specific failure signature for pattern matching"""
        signature_parts = [
            f"test:{failure.component}",
            failure.category.value if failure.category else "unknown",
            failure.error_message[:200],  # Truncate long messages
            str(sorted(failure.context.keys())) if failure.context else "[]"
        ]
        
        return "|".join(signature_parts)
        
    def _verify_test_pattern_match(self, failure: Failure, pattern: PreventionPattern) -> bool:
        """Verify if failure matches test pattern with enhanced matching logic"""
        failure_signature = self._generate_test_failure_signature(failure)
        
        # Enhanced matching logic for test patterns
        signature_parts = pattern.failure_signature.split("|")
        failure_parts = failure_signature.split("|")
        
        if len(signature_parts) >= 3 and len(failure_parts) >= 3:
            # Component match
            component_match = signature_parts[0] in failure_parts[0] or failure_parts[0] in signature_parts[0]
            
            # Error type match
            error_type_match = signature_parts[1] == failure_parts[1]
            
            # Error message similarity (fuzzy matching)
            error_msg_similarity = self._calculate_message_similarity(signature_parts[2], failure_parts[2])
            
            return component_match and error_type_match and error_msg_similarity > 0.7
            
        return False
        
    def _calculate_message_similarity(self, msg1: str, msg2: str) -> float:
        """Calculate similarity between error messages"""
        if not msg1 or not msg2:
            return 0.0
            
        # Simple word-based similarity
        words1 = set(msg1.lower().split())
        words2 = set(msg2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
        
    def _classify_test_pattern(self, pattern: PreventionPattern) -> TestPatternType:
        """Classify test pattern by type"""
        signature = pattern.failure_signature.lower()
        
        if "importerror" in signature:
            return TestPatternType.PYTEST_IMPORT_ERROR
        elif "assertionerror" in signature:
            return TestPatternType.PYTEST_ASSERTION_FAILURE
        elif "fixture" in signature:
            return TestPatternType.PYTEST_FIXTURE_ERROR
        elif "timeout" in signature:
            return TestPatternType.PYTEST_TIMEOUT
        elif "makefile" in signature or "make" in signature:
            if "syntax" in signature:
                return TestPatternType.MAKEFILE_SYNTAX_ERROR
            else:
                return TestPatternType.MAKEFILE_TARGET_ERROR
        elif "permission" in signature:
            return TestPatternType.INFRASTRUCTURE_PERMISSION
        elif "network" in signature or "connection" in signature:
            return TestPatternType.INFRASTRUCTURE_NETWORK
        elif "resource" in signature:
            return TestPatternType.INFRASTRUCTURE_RESOURCE
        else:
            return TestPatternType.TEST_ENVIRONMENT_SETUP
            
    def _extract_component_from_signature(self, signature: str) -> Optional[str]:
        """Extract component name from failure signature"""
        parts = signature.split("|")
        if parts and parts[0].startswith("test:"):
            return parts[0][5:]  # Remove "test:" prefix
        return None
        
    def _update_pattern_metrics(self, pattern_id: str, match_successful: bool):
        """Update performance metrics for pattern"""
        if pattern_id not in self.pattern_metrics:
            self.pattern_metrics[pattern_id] = TestPatternMetrics(pattern_id=pattern_id)
            
        metrics = self.pattern_metrics[pattern_id]
        metrics.match_count += 1
        metrics.last_matched = datetime.now()
        
        if match_successful:
            metrics.successful_applications += 1
            
        # Update effectiveness score
        metrics.effectiveness_score = metrics.successful_applications / max(1, metrics.match_count)
        
        # Save updated metrics periodically
        if metrics.match_count % 10 == 0:
            self._save_pattern_metrics()
            
    def _generate_pattern_from_rca(self, failure: Failure, root_causes: List[RootCause], 
                                  systematic_fixes: List[SystematicFix]) -> Optional[PreventionPattern]:
        """Generate new pattern from successful RCA analysis"""
        if not root_causes or not systematic_fixes:
            return None
            
        primary_root_cause = root_causes[0]  # Use primary root cause
        primary_fix = systematic_fixes[0]    # Use primary fix
        
        pattern_id = f"test_pattern_{primary_root_cause.cause_type.value}_{int(time.time())}"
        failure_signature = self._generate_test_failure_signature(failure)
        pattern_hash = hashlib.md5(failure_signature.encode()).hexdigest()[:8]
        
        # Generate prevention steps from systematic fixes
        prevention_steps = []
        for fix in systematic_fixes:
            prevention_steps.extend(fix.implementation_steps[:3])  # Take first 3 steps
            
        # Generate detection criteria
        detection_criteria = [
            f"Monitor for {primary_root_cause.cause_type.value} in test execution",
            f"Automated detection of {failure.category.value} failures",
            "Proactive test environment validation"
        ]
        
        # Generate automated checks
        automated_checks = [
            f"Automated check for {primary_root_cause.cause_type.value}",
            "Continuous test environment monitoring",
            "Preventive test dependency validation"
        ]
        
        return PreventionPattern(
            pattern_id=pattern_id,
            pattern_name=f"Prevent {primary_root_cause.cause_type.value} in {failure.component}",
            failure_signature=failure_signature,
            root_cause_pattern=primary_root_cause.description,
            prevention_steps=prevention_steps,
            detection_criteria=detection_criteria,
            automated_checks=automated_checks,
            pattern_hash=pattern_hash
        )
        
    def _find_similar_pattern(self, new_pattern: PreventionPattern) -> Optional[str]:
        """Find existing similar pattern"""
        for pattern_id, existing_pattern in self.test_patterns.items():
            if existing_pattern.pattern_hash == new_pattern.pattern_hash:
                return pattern_id
                
            # Check for high similarity
            similarity = self._calculate_pattern_similarity(new_pattern, existing_pattern)
            if similarity > 0.8:
                return pattern_id
                
        return None
        
    def _calculate_pattern_similarity(self, pattern1: PreventionPattern, pattern2: PreventionPattern) -> float:
        """Calculate similarity between two patterns"""
        # Compare failure signatures
        sig_similarity = self._calculate_message_similarity(pattern1.failure_signature, pattern2.failure_signature)
        
        # Compare root cause patterns
        cause_similarity = self._calculate_message_similarity(pattern1.root_cause_pattern, pattern2.root_cause_pattern)
        
        return (sig_similarity + cause_similarity) / 2
        
    def _enhance_existing_pattern(self, existing_pattern_id: str, new_pattern: PreventionPattern, validation_score: float):
        """Enhance existing pattern with new learning"""
        existing_pattern = self.test_patterns[existing_pattern_id]
        
        # Merge prevention steps (avoid duplicates)
        existing_steps = set(existing_pattern.prevention_steps)
        new_steps = set(new_pattern.prevention_steps)
        merged_steps = list(existing_steps.union(new_steps))
        
        # Update pattern with enhanced information
        existing_pattern.prevention_steps = merged_steps[:10]  # Limit to 10 steps
        
        # Update effectiveness based on validation score
        if existing_pattern_id in self.pattern_metrics:
            metrics = self.pattern_metrics[existing_pattern_id]
            metrics.effectiveness_score = (metrics.effectiveness_score + validation_score) / 2
            
        self._save_test_patterns()
        
    def _add_new_test_pattern(self, pattern: PreventionPattern):
        """Add new test pattern to library"""
        # Check if we're at capacity for this pattern type
        pattern_type = self._classify_test_pattern(pattern)
        type_patterns = self.pattern_type_index.get(pattern_type, [])
        
        if len(type_patterns) >= self.max_patterns_per_type:
            # Remove least effective pattern of this type
            self._remove_least_effective_pattern(pattern_type)
            
        # Add new pattern
        self.test_patterns[pattern.pattern_id] = pattern
        
        # Initialize metrics
        self.pattern_metrics[pattern.pattern_id] = TestPatternMetrics(pattern_id=pattern.pattern_id)
        
        # Update indexes
        self._build_performance_indexes()
        
        # Save to disk
        self._save_test_patterns()
        self._save_pattern_metrics()
        
    def _remove_least_effective_pattern(self, pattern_type: TestPatternType):
        """Remove least effective pattern of given type"""
        type_patterns = self.pattern_type_index.get(pattern_type, [])
        
        if not type_patterns:
            return
            
        # Find least effective pattern
        least_effective_id = None
        lowest_score = float('inf')
        
        for pattern_id in type_patterns:
            if pattern_id in self.pattern_metrics:
                score = self.pattern_metrics[pattern_id].effectiveness_score
                if score < lowest_score:
                    lowest_score = score
                    least_effective_id = pattern_id
                    
        if least_effective_id:
            self._remove_pattern(least_effective_id)
            
    def _remove_pattern(self, pattern_id: str):
        """Remove pattern from library"""
        if pattern_id in self.test_patterns:
            del self.test_patterns[pattern_id]
            
        if pattern_id in self.pattern_metrics:
            del self.pattern_metrics[pattern_id]
            
        # Rebuild indexes to remove references
        self._build_performance_indexes()
        
    def _find_duplicate_patterns(self) -> List[str]:
        """Find duplicate patterns for cleanup"""
        duplicates = []
        seen_hashes = {}
        
        for pattern_id, pattern in self.test_patterns.items():
            pattern_hash = pattern.pattern_hash
            if pattern_hash in seen_hashes:
                # Keep the one with better metrics
                existing_id = seen_hashes[pattern_hash]
                existing_metrics = self.pattern_metrics.get(existing_id, TestPatternMetrics(pattern_id=existing_id))
                current_metrics = self.pattern_metrics.get(pattern_id, TestPatternMetrics(pattern_id=pattern_id))
                
                if current_metrics.effectiveness_score < existing_metrics.effectiveness_score:
                    duplicates.append(pattern_id)
                else:
                    duplicates.append(existing_id)
                    seen_hashes[pattern_hash] = pattern_id
            else:
                seen_hashes[pattern_hash] = pattern_id
                
        return duplicates
        
    def _calculate_generalization_potential(self, failure: Failure, root_causes: List[RootCause]) -> float:
        """Calculate how generalizable this pattern might be"""
        # Factors that increase generalization potential:
        # - Common error types
        # - Generic components
        # - Broad root cause categories
        
        generalization_score = 0.0
        
        # Check for common error patterns
        common_errors = ["ImportError", "AssertionError", "PermissionError", "ConnectionError"]
        for error in common_errors:
            if error in failure.error_message:
                generalization_score += 0.2
                
        # Check for generic components
        if "test" in failure.component.lower():
            generalization_score += 0.3
            
        # Check for broad root cause categories
        broad_causes = ["broken_dependencies", "configuration_error", "permission_denied"]
        for root_cause in root_causes:
            if root_cause.cause_type.value in broad_causes:
                generalization_score += 0.2
                
        return min(1.0, generalization_score)
        
    def _trigger_performance_optimization(self):
        """Trigger performance optimization when matching is slow"""
        self.logger.info("Triggering performance optimization due to slow pattern matching")
        
        # Perform immediate optimization
        optimization_results = self.optimize_pattern_performance()
        
        # If still slow, trigger more aggressive cleanup
        if self.total_match_time_ms / max(1, self.total_matches_performed) > 1000:
            cleanup_results = self.cleanup_pattern_library()
            self.logger.info(f"Aggressive cleanup completed: {cleanup_results}")
            
    def _get_primary_responsibility(self) -> str:
        """Single responsibility: Test-specific pattern library management"""
        return "test_specific_pattern_library_with_learning_and_optimization"