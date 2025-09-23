"""
Tests for the Adaptive Babel Fish classification system.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import os

from src.universal_artifact_classification.adaptive_babel_fish import AdaptiveBabelFish
from src.universal_artifact_classification.models import ModelConfig, ArtifactUnderstanding


class TestAdaptiveBabelFish:
    """Test the core Adaptive Babel Fish functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Use CPU-only config for testing
        self.config = ModelConfig(
            base_model_name="microsoft/codebert-base",
            enable_gpu=False,
            confidence_threshold=0.85
        )
        
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoModel')
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoTokenizer')
    def test_babel_fish_initialization(self, mock_tokenizer, mock_model):
        """Test that Babel Fish initializes correctly"""
        # Mock the model loading to avoid downloading
        mock_tokenizer.from_pretrained.return_value = Mock()
        mock_model.from_pretrained.return_value = Mock()
        
        babel_fish = AdaptiveBabelFish(self.config)
        
        assert babel_fish is not None
        assert babel_fish.config == self.config
        assert babel_fish.classification_count == 0
        assert babel_fish.heuristic_hits == 0
    
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoModel')
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoTokenizer')
    def test_understand_artifact_python_file(self, mock_tokenizer, mock_model):
        """Test understanding a Python source file"""
        # Mock the model components
        mock_tokenizer.from_pretrained.return_value = Mock()
        mock_model.from_pretrained.return_value = Mock()
        
        babel_fish = AdaptiveBabelFish(self.config)
        
        # Create a temporary Python file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def hello_world():\n    print("Hello, World!")\n')
            temp_path = Path(f.name)
        
        try:
            # Test understanding the artifact
            understanding = babel_fish.understand_artifact(temp_path)
            
            assert isinstance(understanding, ArtifactUnderstanding)
            assert understanding.primary_type in ["source_code", "unknown"]  # Depends on heuristic vs deep learning
            assert understanding.confidence >= 0.0
            assert understanding.explanation is not None
            
        finally:
            # Clean up
            os.unlink(temp_path)
    
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoModel')
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoTokenizer')
    def test_heuristic_classification(self, mock_tokenizer, mock_model):
        """Test that heuristic rules work for common cases"""
        # Mock the model components
        mock_tokenizer.from_pretrained.return_value = Mock()
        mock_model.from_pretrained.return_value = Mock()
        
        babel_fish = AdaptiveBabelFish(self.config)
        
        # Create a temporary Python file that should trigger heuristic
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('# Simple Python file\nprint("test")\n')
            temp_path = Path(f.name)
        
        try:
            understanding = babel_fish.understand_artifact(temp_path)
            
            # Should be classified as source_code with high confidence via heuristic
            assert understanding.primary_type == "source_code"
            assert understanding.confidence >= 0.95
            
            # Check that heuristic was used
            metrics = babel_fish.get_efficiency_metrics()
            assert metrics["heuristic_hits"] >= 1
            
        finally:
            os.unlink(temp_path)
    
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoModel')
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoTokenizer')
    def test_efficiency_metrics(self, mock_tokenizer, mock_model):
        """Test efficiency metrics tracking"""
        # Mock the model components
        mock_tokenizer.from_pretrained.return_value = Mock()
        mock_model.from_pretrained.return_value = Mock()
        
        babel_fish = AdaptiveBabelFish(self.config)
        
        # Initial metrics should show no activity
        metrics = babel_fish.get_efficiency_metrics()
        assert metrics["total_classifications"] == 0
        assert metrics["heuristic_hits"] == 0
        
        # Create and classify a file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('print("test")')
            temp_path = Path(f.name)
        
        try:
            babel_fish.understand_artifact(temp_path)
            
            # Metrics should now show activity
            metrics = babel_fish.get_efficiency_metrics()
            assert metrics["total_classifications"] == 1
            assert "heuristic_efficiency_percent" in metrics
            
        finally:
            os.unlink(temp_path)
    
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoModel')
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoTokenizer')
    def test_health_check(self, mock_tokenizer, mock_model):
        """Test health check functionality"""
        # Mock the model components
        mock_tokenizer.from_pretrained.return_value = Mock()
        mock_model.from_pretrained.return_value = Mock()
        
        babel_fish = AdaptiveBabelFish(self.config)
        
        health = babel_fish.health_check()
        
        assert "status" in health
        assert "babel_fish" in health
        assert "transfer_learning_engine" in health["babel_fish"]
        assert "heuristic_engine" in health["babel_fish"]
        assert "anomaly_detector" in health["babel_fish"]
        assert "learning_engine" in health["babel_fish"]
    
    def test_model_config_defaults(self):
        """Test that ModelConfig has sensible defaults"""
        config = ModelConfig()
        
        assert config.base_model_name == "microsoft/codebert-base"
        assert config.confidence_threshold == 0.85
        assert config.heuristic_threshold == 0.95
        assert config.max_sequence_length == 512
        assert config.batch_size == 16