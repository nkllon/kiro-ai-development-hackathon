"""
Integration tests for BabelFishContentClassifier compatibility.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, Mock
import tempfile
import os

from src.universal_artifact_classification.babel_fish_content_classifier import BabelFishContentClassifier
from src.repository_discovery.core.content_classifier import ContentType


class TestBabelFishContentClassifierCompatibility:
    """Test compatibility with original ContentClassifier interface"""
    
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoModel')
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoTokenizer')
    def test_classify_file_interface_compatibility(self, mock_tokenizer, mock_model):
        """Test that classify_file returns the expected interface"""
        # Mock the model loading
        mock_tokenizer.from_pretrained.return_value = Mock()
        mock_model.from_pretrained.return_value = Mock()
        
        classifier = BabelFishContentClassifier()
        
        # Create a test Python file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def hello():\n    print("Hello, World!")\n')
            temp_path = Path(f.name)
        
        try:
            result = classifier.classify_file(temp_path)
            
            # Validate interface compatibility
            assert hasattr(result, 'file_path')
            assert hasattr(result, 'primary_type')
            assert hasattr(result, 'confidence')
            assert hasattr(result, 'alternative_types')
            assert hasattr(result, 'classification_reasons')
            assert hasattr(result, 'metadata')
            
            # Validate types
            assert result.file_path == temp_path
            assert isinstance(result.primary_type, ContentType)
            assert isinstance(result.confidence, float)
            assert isinstance(result.alternative_types, list)
            assert isinstance(result.classification_reasons, list)
            assert isinstance(result.metadata, dict)
            
            # Validate content
            assert result.primary_type == ContentType.SOURCE_CODE
            assert 0.0 <= result.confidence <= 1.0
            assert len(result.classification_reasons) > 0
            assert "babel_fish_confidence" in result.metadata
            
        finally:
            os.unlink(temp_path)
    
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoModel')
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoTokenizer')
    def test_classify_batch_interface_compatibility(self, mock_tokenizer, mock_model):
        """Test that classify_batch returns the expected interface"""
        # Mock the model loading
        mock_tokenizer.from_pretrained.return_value = Mock()
        mock_model.from_pretrained.return_value = Mock()
        
        classifier = BabelFishContentClassifier()
        
        # Create test files
        test_files = []
        file_contents = [
            ('test1.py', 'print("hello")'),
            ('config.json', '{"key": "value"}'),
            ('README.md', '# Test Project\nThis is a test.')
        ]
        
        for filename, content in file_contents:
            with tempfile.NamedTemporaryFile(mode='w', suffix=Path(filename).suffix, delete=False) as f:
                f.write(content)
                test_files.append(Path(f.name))
        
        try:
            batch_result = classifier.classify_batch(test_files, "test_batch")
            
            # Validate interface compatibility
            assert hasattr(batch_result, 'batch_id')
            assert hasattr(batch_result, 'results')
            assert hasattr(batch_result, 'total_files')
            assert hasattr(batch_result, 'processing_time')
            assert hasattr(batch_result, 'average_confidence')
            assert hasattr(batch_result, 'accuracy_metrics')
            
            # Validate content
            assert batch_result.batch_id == "test_batch"
            assert len(batch_result.results) == len(test_files)
            assert batch_result.total_files == len(test_files)
            assert batch_result.processing_time > 0
            assert 0.0 <= batch_result.average_confidence <= 1.0
            assert isinstance(batch_result.accuracy_metrics, dict)
            
            # Validate Babel Fish specific metrics
            assert "heuristic_efficiency" in batch_result.accuracy_metrics
            assert "learning_events" in batch_result.accuracy_metrics
            
        finally:
            for file_path in test_files:
                os.unlink(file_path)
    
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoModel')
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoTokenizer')
    def test_type_mapping_accuracy(self, mock_tokenizer, mock_model):
        """Test that Babel Fish types are correctly mapped to ContentType"""
        # Mock the model loading
        mock_tokenizer.from_pretrained.return_value = Mock()
        mock_model.from_pretrained.return_value = Mock()
        
        classifier = BabelFishContentClassifier()
        
        # Test different file types
        test_cases = [
            ('.py', 'class Test:\n    pass', ContentType.SOURCE_CODE),
            ('.json', '{"config": true}', ContentType.CONFIGURATION),
            ('.md', '# Documentation\nThis is a doc.', ContentType.DOCUMENTATION),
            ('.sh', '#!/bin/bash\necho "script"', ContentType.SCRIPT)
        ]
        
        for extension, content, expected_type in test_cases:
            with tempfile.NamedTemporaryFile(mode='w', suffix=extension, delete=False) as f:
                f.write(content)
                temp_path = Path(f.name)
            
            try:
                result = classifier.classify_file(temp_path)
                
                # Should map to expected ContentType
                assert result.primary_type == expected_type, f"Expected {expected_type} for {extension}, got {result.primary_type}"
                assert result.confidence > 0.5, f"Low confidence for {extension}: {result.confidence}"
                
            finally:
                os.unlink(temp_path)
    
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoModel')
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoTokenizer')
    def test_babel_fish_enhanced_metadata(self, mock_tokenizer, mock_model):
        """Test that Babel Fish provides enhanced metadata"""
        # Mock the model loading
        mock_tokenizer.from_pretrained.return_value = Mock()
        mock_model.from_pretrained.return_value = Mock()
        
        classifier = BabelFishContentClassifier()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def test_function():\n    assert True')
            temp_path = Path(f.name)
        
        try:
            result = classifier.classify_file(temp_path)
            
            # Should have Babel Fish specific metadata
            metadata = result.metadata
            assert "babel_fish_confidence" in metadata
            assert "semantic_features" in metadata
            assert "heuristic_rules_used" in metadata
            assert "anomaly_indicators" in metadata
            assert "learning_opportunities" in metadata
            assert "babel_fish_type" in metadata
            
            # Babel Fish type should be the internal type
            assert metadata["babel_fish_type"] in ["source_code", "test_file"]
            
        finally:
            os.unlink(temp_path)
    
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoModel')
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoTokenizer')
    def test_classification_stats_enhanced(self, mock_tokenizer, mock_model):
        """Test that classification stats include Babel Fish metrics"""
        # Mock the model loading
        mock_tokenizer.from_pretrained.return_value = Mock()
        mock_model.from_pretrained.return_value = Mock()
        
        classifier = BabelFishContentClassifier()
        
        # Classify a file to generate stats
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('print("test")')
            temp_path = Path(f.name)
        
        try:
            classifier.classify_file(temp_path)
            
            stats = classifier.get_classification_stats()
            
            # Should have standard stats
            assert "total_classifications" in stats
            assert "total_processing_time" in stats
            assert "average_processing_time" in stats
            
            # Should have Babel Fish specific stats
            assert "babel_fish_metrics" in stats
            assert "learning_stats" in stats
            assert "heuristic_stats" in stats
            
            # Validate Babel Fish metrics structure
            babel_fish_metrics = stats["babel_fish_metrics"]
            assert "heuristic_efficiency_percent" in babel_fish_metrics
            assert "total_classifications" in babel_fish_metrics
            
        finally:
            os.unlink(temp_path)