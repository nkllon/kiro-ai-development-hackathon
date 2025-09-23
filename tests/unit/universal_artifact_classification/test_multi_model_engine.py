"""
Tests for multi-model adaptive classification engine.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import os

from src.universal_artifact_classification.adaptive_babel_fish import AdaptiveBabelFish
from src.universal_artifact_classification.models import ModelConfig


class TestMultiModelEngine:
    """Test the multi-model adaptive classification engine"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.config = ModelConfig(enable_gpu=False)
    
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoModel')
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoTokenizer')
    def test_model_selection_for_code(self, mock_tokenizer, mock_model):
        """Test that appropriate models are selected for different artifact types"""
        # Mock the model loading
        mock_tokenizer.from_pretrained.return_value = Mock()
        mock_model.from_pretrained.return_value = Mock()
        
        babel_fish = AdaptiveBabelFish(self.config)
        
        # Create a Python file with structural code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''
class TestClass:
    def __init__(self):
        self.value = 42
    
    def method(self):
        return self.value
''')
            temp_path = Path(f.name)
        
        try:
            understanding = babel_fish.understand_artifact(temp_path)
            
            # Should be classified as source_code
            assert understanding.primary_type == "source_code"
            assert understanding.confidence > 0.9
            
            # Check that explanation mentions the model used
            assert "classification" in understanding.explanation.lower()
            
        finally:
            os.unlink(temp_path)
    
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoModel')
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoTokenizer')
    def test_confidence_calibration(self, mock_tokenizer, mock_model):
        """Test confidence calibration for different file types"""
        # Mock the model loading
        mock_tokenizer.from_pretrained.return_value = Mock()
        mock_model.from_pretrained.return_value = Mock()
        
        babel_fish = AdaptiveBabelFish(self.config)
        
        test_cases = [
            ('.py', 'print("hello")', "source_code"),
            ('.md', '# README\nThis is documentation', "documentation"),
            ('.json', '{"key": "value"}', "configuration"),
            ('.unknown', 'some content', "unknown")
        ]
        
        confidences = []
        
        for extension, content, expected_type in test_cases:
            with tempfile.NamedTemporaryFile(mode='w', suffix=extension, delete=False) as f:
                f.write(content)
                temp_path = Path(f.name)
            
            try:
                understanding = babel_fish.understand_artifact(temp_path)
                confidences.append({
                    'extension': extension,
                    'confidence': understanding.confidence,
                    'type': understanding.primary_type
                })
                
            finally:
                os.unlink(temp_path)
        
        # Well-known extensions should have higher confidence
        py_confidence = next(c['confidence'] for c in confidences if c['extension'] == '.py')
        unknown_confidence = next(c['confidence'] for c in confidences if c['extension'] == '.unknown')
        
        assert py_confidence > unknown_confidence, "Well-known extensions should have higher confidence"
    
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoModel')
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoTokenizer')
    def test_heuristic_vs_deep_learning_routing(self, mock_tokenizer, mock_model):
        """Test that routing between heuristics and deep learning works correctly"""
        # Mock the model loading
        mock_tokenizer.from_pretrained.return_value = Mock()
        mock_model.from_pretrained.return_value = Mock()
        
        babel_fish = AdaptiveBabelFish(self.config)
        
        # Create a file that should trigger heuristic classification
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('print("simple")')
            temp_path = Path(f.name)
        
        try:
            understanding = babel_fish.understand_artifact(temp_path)
            
            # Should use heuristic for simple Python file
            assert understanding.primary_type == "source_code"
            assert len(understanding.heuristic_rules_used) > 0
            assert "heuristic" in understanding.explanation.lower()
            
            # Check efficiency metrics
            metrics = babel_fish.get_efficiency_metrics()
            assert metrics["heuristic_hits"] >= 1
            
        finally:
            os.unlink(temp_path)
    
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoModel')
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoTokenizer')
    def test_anomaly_detection_integration(self, mock_tokenizer, mock_model):
        """Test that anomaly detection works with the adaptive engine"""
        # Mock the model loading
        mock_tokenizer.from_pretrained.return_value = Mock()
        mock_model.from_pretrained.return_value = Mock()
        
        babel_fish = AdaptiveBabelFish(self.config)
        
        # Create a file that might trigger anomaly detection (unusual extension)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.weird', delete=False) as f:
            f.write('some unusual content')
            temp_path = Path(f.name)
        
        try:
            understanding = babel_fish.understand_artifact(temp_path)
            
            # Should detect some anomalies for unusual file
            # (low confidence, unusual extension, etc.)
            assert understanding.confidence < 0.8  # Should have low confidence
            
        finally:
            os.unlink(temp_path)
    
    def test_adaptive_engine_capabilities(self):
        """Test that the adaptive engine reports correct capabilities"""
        with patch('src.universal_artifact_classification.transfer_learning_engine.AutoModel'), \
             patch('src.universal_artifact_classification.transfer_learning_engine.AutoTokenizer'):
            
            babel_fish = AdaptiveBabelFish(self.config)
            capabilities = babel_fish.get_capabilities()
            
            assert capabilities["artifact_classification"] is True
            assert capabilities["transfer_learning"] is True
            assert capabilities["heuristic_generation"] is True
            assert capabilities["anomaly_detection"] is True
            assert capabilities["continuous_learning"] is True
            assert capabilities["domain_adaptation"] is True
            assert "supported_models" in capabilities
            assert "supported_artifact_types" in capabilities