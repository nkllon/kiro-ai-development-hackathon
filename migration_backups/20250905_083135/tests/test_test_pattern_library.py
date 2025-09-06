"""
Unit tests for Test-Specific Pattern Library Integration
Tests Task 9 implementation: pattern learning, performance optimization, and maintenance
"""

import pytest
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.beast_mode.testing.test_pattern_library import (
    TestPatternLibrary, TestPatternType, TestPatternMetrics, TestPatternLearning
)
from src.beast_mode.analysis.rca_engine import (
    Failure, RootCause, SystematicFix, PreventionPattern, FailureCategory, RootCauseType
)

class TestTestPatternLibrary:
    """Test suite for TestPatternLibrary class"""
    
    @pytest.fixture
    def temp_pattern_dir(self, tmp_path):
        """Create temporary directory for pattern files"""
        pattern_dir = tmp_path / "patterns"
        pattern_dir.mkdir()
        return pattern_dir
        
    @pytest.fixture
    def pattern_library(self, temp_pattern_dir):
        """Create TestPatternLibrary instance with temporary directory"""
        base_path = str(temp_pattern_dir / "rca_patterns.json")
        library = TestPatternLibrary(base_pattern_library_path=base_path)
        
        # Override paths to use temp directory
        library.test_patterns_path = str(temp_pattern_dir / "test_specific_patterns.json")
        library.pattern_metrics_path = str(temp_pattern_dir / "test_pattern_metrics.json")
        library.learning_data_path = str(temp_pattern_dir / "test_pattern_learning.json")
        
        return library
        
    @pytest.fixture
    def sample_failure(self):
        """Create sample test failure"""
        return Failure(
            failure_id="test_failure_001",
            timestamp=datetime.now(),
            component="tests/test_example.py",
            error_message="ImportError: No module named 'missing_module'",
            stack_trace="Traceback (most recent call last):\n  File test_example.py...",
            context={
                "test_file": "tests/test_example.py",
                "test_function": "test_import_functionality",
                "pytest_node_id": "tests/test_example.py::test_import_functionality"
            },
            category=FailureCategory.DEPENDENCY_ISSUE
        )
        
    @pytest.fixture
    def sample_root_cause(self):
        """Create sample root cause"""
        return RootCause(
            cause_type=RootCauseType.TEST_IMPORT_ERROR,
            description="Missing test dependency module",
            evidence=["ImportError in test execution", "Module not found in environment"],
            confidence_score=0.9,
            impact_severity="high",
            affected_components=["tests/test_example.py"]
        )
        
    @pytest.fixture
    def sample_systematic_fix(self):
        """Create sample systematic fix"""
        return SystematicFix(
            fix_id="fix_001",
            root_cause=Mock(),
            fix_description="Install missing test dependency",
            implementation_steps=[
                "Identify missing module",
                "Add to requirements.txt",
                "Install with pip"
            ],
            validation_criteria=["Module imports successfully", "Tests pass"],
            rollback_plan="Remove from requirements.txt",
            estimated_time_minutes=5
        )
        
    def test_initialization(self, pattern_library):
        """Test TestPatternLibrary initialization"""
        assert pattern_library.module_name == "test_pattern_library"
        assert pattern_library.is_healthy()
        assert isinstance(pattern_library.test_patterns, dict)
        assert isinstance(pattern_library.pattern_metrics, dict)
        assert isinstance(pattern_library.learning_data, list)
        
    def test_module_status(self, pattern_library):
        """Test module status reporting"""
        status = pattern_library.get_module_status()
        
        assert status["module_name"] == "test_pattern_library"
        assert status["status"] == "operational"
        assert "test_patterns_count" in status
        assert "total_matches_performed" in status
        assert "average_match_time_ms" in status
        assert "cache_hit_rate" in status
        assert "performance_target_met" in status
        
    def test_pattern_matching_performance(self, pattern_library, sample_failure):
        """Test pattern matching meets sub-second performance requirement"""
        # Add some test patterns
        for i in range(10):
            pattern = PreventionPattern(
                pattern_id=f"test_pattern_{i}",
                pattern_name=f"Test Pattern {i}",
                failure_signature=f"test:tests/test_{i}.py|dependency_issue|ImportError|[]",
                root_cause_pattern="Test import error",
                prevention_steps=["Check dependencies"],
                detection_criteria=["Monitor imports"],
                automated_checks=["Automated dependency check"],
                pattern_hash=f"hash_{i:08d}"
            )
            pattern_library.test_patterns[pattern.pattern_id] = pattern
            
        # Rebuild indexes
        pattern_library._build_performance_indexes()
        
        # Measure matching performance
        start_time = time.time()
        matches = pattern_library.match_test_patterns(sample_failure)
        match_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Verify sub-second performance (Requirement 4.2)
        assert match_time < 1000, f"Pattern matching took {match_time:.2f}ms, exceeds 1 second requirement"
        assert isinstance(matches, list)
        
    def test_pattern_learning_from_successful_rca(self, pattern_library, sample_failure, 
                                                 sample_root_cause, sample_systematic_fix):
        """Test pattern learning from successful RCA analyses"""
        # Test learning with high validation score
        success = pattern_library.learn_from_successful_rca(
            failure=sample_failure,
            root_causes=[sample_root_cause],
            systematic_fixes=[sample_systematic_fix],
            validation_score=0.9
        )
        
        assert success is True
        assert len(pattern_library.learning_data) > 0
        
        # Verify learning record
        learning_record = pattern_library.learning_data[-1]
        assert learning_record.successful_fix_applied is True
        assert learning_record.fix_validation_score == 0.9
        assert learning_record.generalization_potential >= 0.0
        
    def test_pattern_learning_threshold(self, pattern_library, sample_failure, 
                                       sample_root_cause, sample_systematic_fix):
        """Test pattern learning respects validation score threshold"""
        # Test learning with low validation score (below threshold)
        success = pattern_library.learn_from_successful_rca(
            failure=sample_failure,
            root_causes=[sample_root_cause],
            systematic_fixes=[sample_systematic_fix],
            validation_score=0.5  # Below default threshold of 0.8
        )
        
        assert success is False
        
    def test_pattern_optimization(self, pattern_library):
        """Test pattern library optimization functionality"""
        # Add patterns with different effectiveness scores
        for i in range(5):
            pattern = PreventionPattern(
                pattern_id=f"pattern_{i}",
                pattern_name=f"Pattern {i}",
                failure_signature=f"test:test_{i}.py|error|message|[]",
                root_cause_pattern="Test error",
                prevention_steps=["Fix error"],
                detection_criteria=["Monitor"],
                automated_checks=["Check"],
                pattern_hash=f"hash_{i}"
            )
            pattern_library.test_patterns[pattern.pattern_id] = pattern
            
            # Create metrics with varying effectiveness
            metrics = TestPatternMetrics(
                pattern_id=pattern.pattern_id,
                match_count=20,
                successful_applications=i * 2,  # Varying success rates
                effectiveness_score=i * 0.2,
                false_positive_count=10 - i
            )
            pattern_library.pattern_metrics[pattern.pattern_id] = metrics
            
        initial_count = len(pattern_library.test_patterns)
        
        # Run optimization
        results = pattern_library.optimize_pattern_performance()
        
        assert "patterns_before" in results
        assert "patterns_removed" in results
        assert "indexes_rebuilt" in results
        assert results["patterns_before"] == initial_count
        
    def test_pattern_cleanup(self, pattern_library):
        """Test pattern library cleanup functionality"""
        # Add duplicate patterns
        pattern1 = PreventionPattern(
            pattern_id="pattern_1",
            pattern_name="Pattern 1",
            failure_signature="test:test.py|error|message|[]",
            root_cause_pattern="Error",
            prevention_steps=["Fix"],
            detection_criteria=["Monitor"],
            automated_checks=["Check"],
            pattern_hash="duplicate_hash"
        )
        
        pattern2 = PreventionPattern(
            pattern_id="pattern_2",
            pattern_name="Pattern 2",
            failure_signature="test:test.py|error|message|[]",
            root_cause_pattern="Error",
            prevention_steps=["Fix"],
            detection_criteria=["Monitor"],
            automated_checks=["Check"],
            pattern_hash="duplicate_hash"  # Same hash = duplicate
        )
        
        pattern_library.test_patterns["pattern_1"] = pattern1
        pattern_library.test_patterns["pattern_2"] = pattern2
        
        # Add metrics
        pattern_library.pattern_metrics["pattern_1"] = TestPatternMetrics(
            pattern_id="pattern_1", effectiveness_score=0.8
        )
        pattern_library.pattern_metrics["pattern_2"] = TestPatternMetrics(
            pattern_id="pattern_2", effectiveness_score=0.6
        )
        
        initial_count = len(pattern_library.test_patterns)
        
        # Run cleanup
        results = pattern_library.cleanup_pattern_library()
        
        assert "duplicate_patterns_removed" in results
        assert "stale_patterns_removed" in results
        assert results["duplicate_patterns_removed"] > 0
        assert len(pattern_library.test_patterns) < initial_count
        
    def test_pattern_effectiveness_report(self, pattern_library):
        """Test pattern effectiveness reporting"""
        # Add test patterns with metrics
        for i in range(3):
            pattern = PreventionPattern(
                pattern_id=f"pattern_{i}",
                pattern_name=f"Pattern {i}",
                failure_signature=f"test:test_{i}.py|error|message|[]",
                root_cause_pattern="Error",
                prevention_steps=["Fix"],
                detection_criteria=["Monitor"],
                automated_checks=["Check"],
                pattern_hash=f"hash_{i}"
            )
            pattern_library.test_patterns[pattern.pattern_id] = pattern
            
            metrics = TestPatternMetrics(
                pattern_id=pattern.pattern_id,
                match_count=10 + i,
                successful_applications=5 + i,
                effectiveness_score=0.5 + (i * 0.2)
            )
            pattern_library.pattern_metrics[pattern.pattern_id] = metrics
            
        report = pattern_library.get_pattern_effectiveness_report()
        
        assert "total_patterns" in report
        assert "total_matches" in report
        assert "average_match_time_ms" in report
        assert "cache_hit_rate" in report
        assert "pattern_types" in report
        assert "top_performing_patterns" in report
        assert report["total_patterns"] == 3
        
    def test_test_failure_signature_generation(self, pattern_library, sample_failure):
        """Test test-specific failure signature generation"""
        signature = pattern_library._generate_test_failure_signature(sample_failure)
        
        assert signature.startswith("test:")
        assert sample_failure.component in signature
        assert sample_failure.category.value in signature
        assert sample_failure.error_message[:200] in signature
        
    def test_pattern_classification(self, pattern_library):
        """Test pattern classification by type"""
        # Test different pattern types
        import_pattern = PreventionPattern(
            pattern_id="import_pattern",
            pattern_name="Import Pattern",
            failure_signature="test:test.py|error|ImportError: No module|[]",
            root_cause_pattern="Import error",
            prevention_steps=["Fix import"],
            detection_criteria=["Monitor"],
            automated_checks=["Check"],
            pattern_hash="import_hash"
        )
        
        assertion_pattern = PreventionPattern(
            pattern_id="assertion_pattern",
            pattern_name="Assertion Pattern",
            failure_signature="test:test.py|error|AssertionError: Expected|[]",
            root_cause_pattern="Assertion error",
            prevention_steps=["Fix assertion"],
            detection_criteria=["Monitor"],
            automated_checks=["Check"],
            pattern_hash="assertion_hash"
        )
        
        import_type = pattern_library._classify_test_pattern(import_pattern)
        assertion_type = pattern_library._classify_test_pattern(assertion_pattern)
        
        assert import_type == TestPatternType.PYTEST_IMPORT_ERROR
        assert assertion_type == TestPatternType.PYTEST_ASSERTION_FAILURE
        
    def test_pattern_similarity_calculation(self, pattern_library):
        """Test pattern similarity calculation"""
        pattern1 = PreventionPattern(
            pattern_id="pattern_1",
            pattern_name="Pattern 1",
            failure_signature="test:test.py|error|ImportError: No module 'x'|[]",
            root_cause_pattern="Missing module x",
            prevention_steps=["Install x"],
            detection_criteria=["Monitor"],
            automated_checks=["Check"],
            pattern_hash="hash1"
        )
        
        pattern2 = PreventionPattern(
            pattern_id="pattern_2",
            pattern_name="Pattern 2",
            failure_signature="test:test.py|error|ImportError: No module 'y'|[]",
            root_cause_pattern="Missing module y",
            prevention_steps=["Install y"],
            detection_criteria=["Monitor"],
            automated_checks=["Check"],
            pattern_hash="hash2"
        )
        
        similarity = pattern_library._calculate_pattern_similarity(pattern1, pattern2)
        
        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.5  # Should be similar due to ImportError pattern
        
    def test_message_similarity_calculation(self, pattern_library):
        """Test error message similarity calculation"""
        msg1 = "ImportError: No module named 'test_module'"
        msg2 = "ImportError: No module named 'other_module'"
        msg3 = "AssertionError: Expected True, got False"
        
        similarity_similar = pattern_library._calculate_message_similarity(msg1, msg2)
        similarity_different = pattern_library._calculate_message_similarity(msg1, msg3)
        
        assert similarity_similar > similarity_different
        assert 0.0 <= similarity_similar <= 1.0
        assert 0.0 <= similarity_different <= 1.0
        
    def test_performance_index_building(self, pattern_library):
        """Test performance index building"""
        # Add test patterns
        pattern = PreventionPattern(
            pattern_id="test_pattern",
            pattern_name="Test Pattern",
            failure_signature="test:tests/test.py|error|ImportError|[]",
            root_cause_pattern="Import error",
            prevention_steps=["Fix import"],
            detection_criteria=["Monitor"],
            automated_checks=["Check"],
            pattern_hash="test_hash"
        )
        
        pattern_library.test_patterns["test_pattern"] = pattern
        pattern_library._build_performance_indexes()
        
        # Verify indexes were built
        assert "test_hash" in pattern_library.pattern_hash_index
        assert "test_pattern" in pattern_library.pattern_hash_index["test_hash"]
        assert "tests/test.py" in pattern_library.component_index
        assert len(pattern_library.pattern_type_index) > 0
        
    def test_pattern_metrics_update(self, pattern_library):
        """Test pattern metrics updating"""
        pattern_id = "test_pattern"
        
        # Update metrics for successful match
        pattern_library._update_pattern_metrics(pattern_id, True)
        
        assert pattern_id in pattern_library.pattern_metrics
        metrics = pattern_library.pattern_metrics[pattern_id]
        assert metrics.match_count == 1
        assert metrics.successful_applications == 1
        assert metrics.effectiveness_score == 1.0
        assert metrics.last_matched is not None
        
        # Update metrics for failed match
        pattern_library._update_pattern_metrics(pattern_id, False)
        
        metrics = pattern_library.pattern_metrics[pattern_id]
        assert metrics.match_count == 2
        assert metrics.successful_applications == 1
        assert metrics.effectiveness_score == 0.5
        
    def test_generalization_potential_calculation(self, pattern_library, sample_failure, sample_root_cause):
        """Test generalization potential calculation"""
        potential = pattern_library._calculate_generalization_potential(sample_failure, [sample_root_cause])
        
        assert 0.0 <= potential <= 1.0
        # Should have some potential due to common error type and test component
        assert potential > 0.0
        
    def test_pattern_persistence(self, pattern_library, temp_pattern_dir):
        """Test pattern persistence to disk"""
        # Add a test pattern
        pattern = PreventionPattern(
            pattern_id="persist_test",
            pattern_name="Persistence Test",
            failure_signature="test:test.py|error|message|[]",
            root_cause_pattern="Test error",
            prevention_steps=["Fix"],
            detection_criteria=["Monitor"],
            automated_checks=["Check"],
            pattern_hash="persist_hash"
        )
        
        pattern_library.test_patterns["persist_test"] = pattern
        pattern_library._save_test_patterns()
        
        # Verify file was created
        pattern_file = Path(pattern_library.test_patterns_path)
        assert pattern_file.exists()
        
        # Verify content
        with open(pattern_file, 'r') as f:
            data = json.load(f)
            
        assert "test_patterns" in data
        assert len(data["test_patterns"]) == 1
        assert data["test_patterns"][0]["pattern_id"] == "persist_test"
        
    def test_performance_optimization_trigger(self, pattern_library):
        """Test performance optimization trigger"""
        # Simulate slow performance
        pattern_library.total_matches_performed = 10
        pattern_library.total_match_time_ms = 15000  # 15 seconds total = 1.5s average
        
        with patch.object(pattern_library, 'optimize_pattern_performance') as mock_optimize:
            mock_optimize.return_value = {"patterns_removed": 2}
            
            pattern_library._trigger_performance_optimization()
            
            mock_optimize.assert_called_once()
            
    @pytest.mark.performance
    def test_large_scale_pattern_matching(self, pattern_library, sample_failure):
        """Test pattern matching performance with large number of patterns"""
        # Add many patterns to test scalability
        for i in range(1000):
            pattern = PreventionPattern(
                pattern_id=f"scale_pattern_{i}",
                pattern_name=f"Scale Pattern {i}",
                failure_signature=f"test:test_{i}.py|error|Error {i}|[]",
                root_cause_pattern=f"Error {i}",
                prevention_steps=[f"Fix {i}"],
                detection_criteria=[f"Monitor {i}"],
                automated_checks=[f"Check {i}"],
                pattern_hash=f"hash_{i:08d}"
            )
            pattern_library.test_patterns[pattern.pattern_id] = pattern
            
        # Rebuild indexes
        pattern_library._build_performance_indexes()
        
        # Test matching performance
        start_time = time.time()
        matches = pattern_library.match_test_patterns(sample_failure)
        match_time = (time.time() - start_time) * 1000
        
        # Should still meet sub-second requirement even with 1000 patterns
        assert match_time < 1000, f"Large scale matching took {match_time:.2f}ms"
        
    def test_error_handling(self, pattern_library):
        """Test error handling in pattern operations"""
        # Test with invalid failure object
        invalid_failure = Mock()
        invalid_failure.component = None
        invalid_failure.error_message = None
        invalid_failure.category = None
        invalid_failure.context = None
        
        # Should not crash and return empty list
        matches = pattern_library.match_test_patterns(invalid_failure)
        assert matches == []
        
        # Test learning with invalid data
        success = pattern_library.learn_from_successful_rca(
            failure=invalid_failure,
            root_causes=[],
            systematic_fixes=[],
            validation_score=0.9
        )
        assert success is False