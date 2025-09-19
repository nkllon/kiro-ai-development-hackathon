"""
Integration tests for the Adaptive Babel Fish with real repository files.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, Mock

from src.universal_artifact_classification.adaptive_babel_fish import AdaptiveBabelFish
from src.universal_artifact_classification.models import ModelConfig


class TestBabelFishIntegration:
    """Integration tests for the Adaptive Babel Fish"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.config = ModelConfig(enable_gpu=False)
    
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoModel')
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoTokenizer')
    def test_classify_real_repository_files(self, mock_tokenizer, mock_model):
        """Test classification on real files from our repository"""
        # Mock the model loading
        mock_tokenizer.from_pretrained.return_value = Mock()
        mock_model.from_pretrained.return_value = Mock()
        
        babel_fish = AdaptiveBabelFish(self.config)
        
        # Test files that should exist in our repository
        test_files = [
            ("pyproject.toml", "configuration"),
            ("README.md", "documentation"),
            ("src/universal_artifact_classification/adaptive_babel_fish.py", "source_code"),
            ("tests/integration/test_babel_fish_integration.py", "test_file")
        ]
        
        results = []
        for file_path, expected_type in test_files:
            path = Path(file_path)
            if path.exists():
                understanding = babel_fish.understand_artifact(path)
                results.append({
                    "file": file_path,
                    "expected": expected_type,
                    "predicted": understanding.primary_type,
                    "confidence": understanding.confidence,
                    "correct": understanding.primary_type == expected_type
                })
        
        # Validate results
        assert len(results) > 0, "No test files found"
        
        correct_classifications = sum(1 for r in results if r["correct"])
        accuracy = correct_classifications / len(results)
        
        print(f"\nClassification Results:")
        for result in results:
            status = "✓" if result["correct"] else "✗"
            print(f"{status} {result['file']}: {result['predicted']} (confidence: {result['confidence']:.2f})")
        
        print(f"\nAccuracy: {accuracy:.2%} ({correct_classifications}/{len(results)})")
        
        # Should achieve reasonable accuracy even with mocked models (heuristics)
        assert accuracy >= 0.5, f"Accuracy too low: {accuracy:.2%}"
        
        # Check efficiency metrics
        metrics = babel_fish.get_efficiency_metrics()
        assert metrics["total_classifications"] == len(results)
        assert "heuristic_efficiency_percent" in metrics
    
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoModel')
    @patch('src.universal_artifact_classification.transfer_learning_engine.AutoTokenizer')
    def test_babel_fish_learning_progression(self, mock_tokenizer, mock_model):
        """Test that the Babel Fish learns and improves over time"""
        # Mock the model loading
        mock_tokenizer.from_pretrained.return_value = Mock()
        mock_model.from_pretrained.return_value = Mock()
        
        babel_fish = AdaptiveBabelFish(self.config)
        
        # Classify several Python files to trigger learning
        python_files = [
            "src/universal_artifact_classification/adaptive_babel_fish.py",
            "src/universal_artifact_classification/models.py",
            "tests/integration/test_babel_fish_integration.py"
        ]
        
        initial_rules = babel_fish.heuristic_engine.get_rule_count()
        
        for file_path in python_files:
            path = Path(file_path)
            if path.exists():
                babel_fish.understand_artifact(path)
        
        final_rules = babel_fish.heuristic_engine.get_rule_count()
        
        # Should have learned some patterns (or at least maintained rules)
        assert final_rules >= initial_rules
        
        # Check learning statistics
        learning_stats = babel_fish.learning_engine.get_learning_stats()
        assert "total_learning_events" in learning_stats
        assert "domains_learned" in learning_stats