#!/usr/bin/env python3
"""
Tests for ContentClassifier - Repository Discovery System
========================================================

Comprehensive tests for content classification with confidence scoring.
Tests RM-DDD compliance and classification accuracy.

Author: Repository Discovery System
Date: 2025-01-16
Version: 1.0
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from src.repository_discovery.core.content_classifier import (
    ContentClassifier,
    ContentType,
    ClassificationResult,
    ClassificationBatch
)
from src.rm_ddd.core.unified_reflective_module import ModuleStatus, ModuleCapability


class TestContentClassifier:
    """Test ContentClassifier functionality"""
    
    @pytest.fixture
    def classifier(self):
        """Create ContentClassifier instance"""
        return ContentClassifier()
    
    @pytest.fixture
    def temp_files(self):
        """Create temporary test files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test files with different content types
            files = {}
            
            # Specification file
            spec_file = temp_path / "test_spec.md"
            spec_file.write_text("""
# Requirements Document

## User Story
As a user, I want to test specifications, so that I can validate requirements.

### Acceptance Criteria
1. WHEN I run tests THEN I SHALL get results
2. WHEN validation occurs THEN I SHALL see status
""")
            files['spec'] = spec_file
            
            # Source code file
            code_file = temp_path / "example_code.py"
            code_file.write_text("""
#!/usr/bin/env python3
import os
import sys

class TestClass:
    def __init__(self):
        self.value = 42
    
    def test_method(self):
        return self.value
""")
            files['code'] = code_file
            
            # Test file
            test_file = temp_path / "test_example.py"
            test_file.write_text("""
import pytest
import unittest

class TestExample(unittest.TestCase):
    def test_something(self):
        assert True
    
    def test_another_thing(self):
        self.assertEqual(1, 1)
""")
            files['test'] = test_file
            
            # Documentation file
            doc_file = temp_path / "README.md"
            doc_file.write_text("""
# Project Documentation

## Installation
pip install project

## Usage
Run the application with:
```
python app.py
```

## API Reference
See the API documentation for details.
""")
            files['doc'] = doc_file
            
            # Configuration file
            config_file = temp_path / "config.json"
            config_file.write_text("""
{
    "version": "1.0.0",
    "dependencies": {
        "python": ">=3.9"
    },
    "settings": {
        "debug": true
    }
}
""")
            files['config'] = config_file
            
            # Analysis file
            analysis_file = temp_path / "analysis_report.json"
            analysis_file.write_text("""
{
    "analysis_type": "performance",
    "metrics": {
        "cpu_usage": 45.2,
        "memory_usage": 128.5
    },
    "summary": "System performance analysis complete"
}
""")
            files['analysis'] = analysis_file
            
            yield files
    
    def test_module_info(self, classifier):
        """Test module information compliance"""
        info = classifier.get_module_info()
        
        assert info["module_id"] == "ContentClassifier"
        assert info["name"] == "ContentClassifier"
        assert info["version"] == "1.0.0"
        assert "description" in info
        assert "capabilities" in info
        assert "classifications_performed" in info
    
    def test_capabilities(self, classifier):
        """Test module capabilities"""
        capabilities = classifier.get_capabilities()
        
        assert ModuleCapability.CORE_FUNCTIONALITY in capabilities
        assert ModuleCapability.DATA_PROCESSING in capabilities
        assert ModuleCapability.VALIDATION in capabilities
    
    def test_health_status(self, classifier):
        """Test health status reporting"""
        health = classifier.get_health_status()
        
        assert health.module_id == "ContentClassifier"
        assert health.status in [ModuleStatus.HEALTHY, ModuleStatus.WARNING, ModuleStatus.ERROR]
        assert 0.0 <= health.health_score <= 1.0
        assert isinstance(health.issues, list)
    
    def test_graceful_degradation(self, classifier):
        """Test graceful degradation"""
        result = classifier.graceful_degradation()
        
        assert result.success is True
        assert isinstance(result.degraded_capabilities, list)
        assert isinstance(result.remaining_capabilities, list)
        assert ModuleCapability.CORE_FUNCTIONALITY in result.remaining_capabilities
    
    def test_classify_specification_file(self, classifier, temp_files):
        """Test specification file classification"""
        spec_file = temp_files['spec']
        
        confidence = classifier.get_classification_confidence(spec_file)
        assert confidence > 0.5  # Should have reasonable confidence
        
        # Test detailed classification
        content = spec_file.read_text()
        result = classifier._classify_single_file(spec_file, content)
        
        assert result.primary_type == ContentType.SPECIFICATION
        assert result.confidence > 0.5
        assert len(result.classification_reasons) > 0
        assert "Requirements" in str(result.classification_reasons) or "spec" in str(result.classification_reasons).lower()
    
    def test_classify_source_code_file(self, classifier, temp_files):
        """Test source code file classification"""
        code_file = temp_files['code']
        
        content = code_file.read_text()
        result = classifier._classify_single_file(code_file, content)
        
        assert result.primary_type == ContentType.SOURCE_CODE
        assert result.confidence > 0.5
        # Should have source code classification reasons
        assert any("source_code" in reason.lower() for reason in result.classification_reasons)
    
    def test_classify_test_file(self, classifier, temp_files):
        """Test test file classification"""
        test_file = temp_files['test']
        
        content = test_file.read_text()
        result = classifier._classify_single_file(test_file, content)
        
        assert result.primary_type == ContentType.TEST
        assert result.confidence > 0.5
        assert any("test" in reason.lower() for reason in result.classification_reasons)
    
    def test_classify_documentation_file(self, classifier, temp_files):
        """Test documentation file classification"""
        doc_file = temp_files['doc']
        
        content = doc_file.read_text()
        result = classifier._classify_single_file(doc_file, content)
        
        assert result.primary_type == ContentType.DOCUMENTATION
        assert result.confidence > 0.3  # Documentation can be ambiguous with specs
        assert any("documentation" in reason.lower() or "readme" in reason.lower() 
                  for reason in result.classification_reasons)
    
    def test_classify_configuration_file(self, classifier, temp_files):
        """Test configuration file classification"""
        config_file = temp_files['config']
        
        content = config_file.read_text()
        result = classifier._classify_single_file(config_file, content)
        
        assert result.primary_type == ContentType.CONFIGURATION
        assert result.confidence > 0.5
        # Should have some classification reason (extension or content match)
        assert len(result.classification_reasons) > 0
    
    def test_classify_analysis_file(self, classifier, temp_files):
        """Test analysis file classification"""
        analysis_file = temp_files['analysis']
        
        content = analysis_file.read_text()
        result = classifier._classify_single_file(analysis_file, content)
        
        assert result.primary_type == ContentType.ANALYSIS
        assert result.confidence > 0.5
        assert any("analysis" in reason.lower() for reason in result.classification_reasons)
    
    def test_batch_classification(self, classifier, temp_files):
        """Test batch classification functionality"""
        file_paths = list(temp_files.values())
        
        batch = classifier.classify_content_types(
            file_paths=file_paths,
            batch_size=3,
            confidence_threshold=0.5,
            include_alternatives=True
        )
        
        assert isinstance(batch, ClassificationBatch)
        assert batch.total_files == len(file_paths)
        assert len(batch.results) == len(file_paths)
        assert batch.processing_time > 0
        assert 0.0 <= batch.average_confidence <= 1.0
        assert isinstance(batch.accuracy_metrics, dict)
        
        # Check that all files were classified
        for result in batch.results:
            assert isinstance(result, ClassificationResult)
            assert result.primary_type in ContentType
            assert 0.0 <= result.confidence <= 1.0
    
    def test_alternative_classifications(self, classifier, temp_files):
        """Test alternative classification suggestions"""
        # Use a file that might have multiple interpretations
        spec_file = temp_files['spec']  # Could be spec or documentation
        
        content = spec_file.read_text()
        result = classifier._classify_single_file(
            spec_file, 
            content, 
            include_alternatives=True
        )
        
        assert len(result.alternative_types) >= 0
        for alt_type, alt_score in result.alternative_types:
            assert isinstance(alt_type, ContentType)
            assert 0.0 <= alt_score <= 1.0
            assert alt_score < result.confidence  # Alternatives should have lower scores
    
    def test_unknown_file_classification(self, classifier):
        """Test classification of unknown file types"""
        with tempfile.NamedTemporaryFile(suffix='.xyz', mode='w', delete=False) as f:
            f.write("This is some unknown content type")
            unknown_file = Path(f.name)
        
        try:
            content = unknown_file.read_text()
            result = classifier._classify_single_file(unknown_file, content)
            
            # Should either classify as unknown or have low confidence
            assert result.primary_type == ContentType.UNKNOWN or result.confidence < 0.3
            
        finally:
            unknown_file.unlink()
    
    def test_file_reading_safety(self, classifier):
        """Test safe file reading with various edge cases"""
        # Test non-existent file
        non_existent = Path("/non/existent/file.txt")
        content = classifier._read_file_safely(non_existent)
        assert content is None
        
        # Test with actual file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            test_file = Path(f.name)
        
        try:
            content = classifier._read_file_safely(test_file)
            assert content == "test content"
        finally:
            test_file.unlink()
    
    def test_confidence_threshold_filtering(self, classifier, temp_files):
        """Test confidence threshold filtering"""
        file_paths = list(temp_files.values())
        
        # Test with high confidence threshold
        batch_high = classifier.classify_content_types(
            file_paths=file_paths,
            confidence_threshold=0.8
        )
        
        # Test with low confidence threshold
        batch_low = classifier.classify_content_types(
            file_paths=file_paths,
            confidence_threshold=0.2
        )
        
        # Both should process all files, but confidence interpretation may differ
        assert batch_high.total_files == len(file_paths)
        assert batch_low.total_files == len(file_paths)
    
    def test_performance_tracking(self, classifier, temp_files):
        """Test performance tracking functionality"""
        initial_count = classifier._classification_count
        initial_time = classifier._total_processing_time
        
        file_paths = list(temp_files.values())
        batch = classifier.classify_content_types(file_paths)
        
        # Performance metrics should be updated
        assert classifier._classification_count > initial_count
        assert classifier._total_processing_time > initial_time
        
        # Average processing time should be calculable
        avg_time = classifier._get_average_processing_time()
        assert avg_time >= 0.0
    
    def test_accuracy_metrics_calculation(self, classifier, temp_files):
        """Test accuracy metrics calculation"""
        file_paths = list(temp_files.values())
        batch = classifier.classify_content_types(file_paths)
        
        metrics = batch.accuracy_metrics
        
        assert "total_files" in metrics
        assert "unknown_ratio" in metrics
        assert "high_confidence_ratio" in metrics
        assert metrics["total_files"] == len(file_paths)
        assert 0.0 <= metrics["unknown_ratio"] <= 1.0
        assert 0.0 <= metrics["high_confidence_ratio"] <= 1.0
    
    def test_classification_reasons(self, classifier, temp_files):
        """Test that classification reasons are provided"""
        for file_type, file_path in temp_files.items():
            content = file_path.read_text()
            result = classifier._classify_single_file(file_path, content)
            
            # Should have at least one reason for classification
            assert len(result.classification_reasons) > 0
            assert all(isinstance(reason, str) for reason in result.classification_reasons)
    
    def test_metadata_collection(self, classifier, temp_files):
        """Test metadata collection during classification"""
        spec_file = temp_files['spec']
        content = spec_file.read_text()
        result = classifier._classify_single_file(spec_file, content)
        
        assert "file_size" in result.metadata
        assert "has_content" in result.metadata
        assert "content_length" in result.metadata
        assert result.metadata["has_content"] is True
        assert result.metadata["content_length"] > 0
        assert result.metadata["file_size"] > 0


class TestContentClassifierIntegration:
    """Integration tests for ContentClassifier"""
    
    def test_real_repository_classification(self):
        """Test classification on real repository files"""
        classifier = ContentClassifier()
        
        # Test on actual project files
        project_root = Path(".")
        test_files = []
        
        # Find some real files to test
        if (project_root / "pyproject.toml").exists():
            test_files.append(project_root / "pyproject.toml")
        
        if (project_root / "README.md").exists():
            test_files.append(project_root / "README.md")
        
        # Find some Python files
        for py_file in project_root.glob("src/**/*.py"):
            test_files.append(py_file)
            if len(test_files) >= 5:  # Limit for test performance
                break
        
        if test_files:
            batch = classifier.classify_content_types(test_files)
            
            assert batch.total_files == len(test_files)
            assert len(batch.results) == len(test_files)
            
            # Should classify most files with reasonable confidence
            high_confidence_count = sum(1 for r in batch.results if r.confidence > 0.5)
            assert high_confidence_count >= len(test_files) * 0.5  # At least 50% should be high confidence
    
    def test_error_handling_with_invalid_files(self):
        """Test error handling with invalid or problematic files"""
        classifier = ContentClassifier()
        
        # Create list with mix of valid and invalid files
        file_paths = [
            Path("/non/existent/file.txt"),
            Path("pyproject.toml") if Path("pyproject.toml").exists() else Path("/another/non/existent.txt")
        ]
        
        # Should handle errors gracefully
        batch = classifier.classify_content_types(file_paths)
        
        assert batch.total_files == len(file_paths)
        assert len(batch.results) == len(file_paths)
        
        # Non-existent files should be classified as unknown
        for result in batch.results:
            if not result.file_path.exists():
                assert result.primary_type == ContentType.UNKNOWN
                assert result.confidence == 0.0


if __name__ == "__main__":
    pytest.main([__file__])