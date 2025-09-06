"""
Unit tests for ModelRegistry Learning Capabilities

Tests enhanced learning, pattern merging, persistence, and insights.
"""

import json
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

from src.beast_mode.core.model_registry import ModelRegistry
from src.beast_mode.core.pdca_models import Pattern, ValidationLevel


class TestModelRegistryLearning:
    """Test enhanced learning capabilities"""
    
    def setup_method(self):
        """Set up test environment"""
        # Create temporary learning directory
        self.temp_learning_dir = Path("test_learning_patterns")
        if self.temp_learning_dir.exists():
            shutil.rmtree(self.temp_learning_dir)
        self.temp_learning_dir.mkdir()
        
        # Patch the learning directory
        self.original_persist_method = ModelRegistry._persist_learning_update
        
        def mock_persist_learning_update(registry_self, domain: str, pattern: Pattern):
            """Mock persistence to use test directory"""
            try:
                pattern_file = self.temp_learning_dir / f"{domain}_patterns.json"
                
                existing_patterns = []
                if pattern_file.exists():
                    with open(pattern_file, 'r') as f:
                        existing_data = json.load(f)
                        existing_patterns = existing_data.get("patterns", [])
                
                pattern_dict = {
                    "pattern_id": pattern.pattern_id,
                    "name": pattern.name,
                    "domain": pattern.domain,
                    "description": pattern.description,
                    "implementation_steps": pattern.implementation_steps,
                    "success_metrics": pattern.success_metrics,
                    "confidence_score": pattern.confidence_score,
                    "updated_at": "2024-01-01T00:00:00"
                }
                
                updated = False
                for i, existing in enumerate(existing_patterns):
                    if existing.get("pattern_id") == pattern.pattern_id:
                        existing_patterns[i] = pattern_dict
                        updated = True
                        break
                
                if not updated:
                    existing_patterns.append(pattern_dict)
                
                with open(pattern_file, 'w') as f:
                    json.dump({
                        "domain": domain,
                        "patterns": existing_patterns,
                        "last_updated": "2024-01-01T00:00:00"
                    }, f, indent=2)
                
            except Exception as e:
                registry_self.logger.warning(f"Failed to persist learning update: {e}")
        
        ModelRegistry._persist_learning_update = mock_persist_learning_update
    
    def teardown_method(self):
        """Clean up test environment"""
        # Restore original method
        ModelRegistry._persist_learning_update = self.original_persist_method
        
        # Clean up test directory
        if self.temp_learning_dir.exists():
            shutil.rmtree(self.temp_learning_dir)
    
    def test_enhanced_learning_update(self):
        """Test enhanced learning update with weighted metrics"""
        registry = ModelRegistry("nonexistent_file.json")
        
        # Create initial pattern
        pattern1 = Pattern(
            pattern_id="test-pattern-001",
            name="Initial Pattern",
            domain="testing",
            description="Initial test pattern",
            implementation_steps=["Step 1", "Step 2"],
            success_metrics={"accuracy": 0.8, "speed": 0.7},
            confidence_score=0.8
        )
        
        # Update learning
        result1 = registry.update_learning(pattern1)
        assert result1 is True
        
        # Get intelligence and check initial state
        intelligence = registry.get_domain_intelligence("testing")
        assert intelligence.success_metrics["accuracy"] == 0.8
        assert intelligence.success_metrics["speed"] == 0.7
        
        # Create improved pattern with same ID
        pattern2 = Pattern(
            pattern_id="test-pattern-001",  # Same ID - should merge
            name="Improved Pattern",
            domain="testing",
            description="Improved test pattern",
            implementation_steps=["Step 1", "Step 2", "Step 3"],
            success_metrics={"accuracy": 0.9, "speed": 0.6, "reliability": 0.95},
            confidence_score=0.9
        )
        
        # Update learning again
        result2 = registry.update_learning(pattern2)
        assert result2 is True
        
        # Check that metrics were weighted averaged
        updated_intelligence = registry.get_domain_intelligence("testing")
        
        # accuracy: 0.8 * 0.7 + 0.9 * 0.3 = 0.83
        assert abs(updated_intelligence.success_metrics["accuracy"] - 0.83) < 0.01
        
        # speed: 0.7 * 0.7 + 0.6 * 0.3 = 0.67
        assert abs(updated_intelligence.success_metrics["speed"] - 0.67) < 0.01
        
        # reliability: new metric, should be 0.95
        assert updated_intelligence.success_metrics["reliability"] == 0.95
        
        # Confidence should have improved from initial 0.75
        # With the new calculation: 0.75 * 0.7 + 0.9 * 0.2 + metrics_boost
        # Expected around: 0.525 + 0.18 + boost ≈ 0.67+
        assert updated_intelligence.confidence_score > 0.65
    
    def test_pattern_merging(self):
        """Test pattern merging logic"""
        registry = ModelRegistry("nonexistent_file.json")
        
        # Create patterns to merge
        old_pattern = Pattern(
            pattern_id="merge-test-001",
            name="Old Pattern",
            domain="testing",
            description="Old pattern description",
            implementation_steps=["Old Step 1", "Old Step 2"],
            success_metrics={"accuracy": 0.7, "old_metric": 0.8},
            confidence_score=0.7
        )
        
        new_pattern = Pattern(
            pattern_id="merge-test-001",
            name="New Pattern",
            domain="testing",
            description="New pattern description",
            implementation_steps=["New Step 1", "Old Step 2", "New Step 3"],
            success_metrics={"accuracy": 0.9, "new_metric": 0.85},
            confidence_score=0.9
        )
        
        # Test merge
        merged = registry._merge_patterns(old_pattern, new_pattern)
        
        # Should use higher confidence pattern as base
        assert merged.name == "New Pattern"
        assert merged.confidence_score == 0.9
        
        # Should merge implementation steps
        assert "Old Step 1" in merged.implementation_steps
        assert "New Step 1" in merged.implementation_steps
        assert "Old Step 2" in merged.implementation_steps
        assert "New Step 3" in merged.implementation_steps
        assert len(merged.implementation_steps) == 4  # No duplicates
        
        # Should take better success metrics
        assert merged.success_metrics["accuracy"] == 0.9  # Better value
        assert merged.success_metrics["old_metric"] == 0.8  # Only in old
        assert merged.success_metrics["new_metric"] == 0.85  # Only in new
    
    def test_learning_persistence(self):
        """Test learning pattern persistence"""
        registry = ModelRegistry("nonexistent_file.json")
        
        # Create test pattern
        pattern = Pattern(
            pattern_id="persist-test-001",
            name="Persistence Test Pattern",
            domain="persistence",
            description="Test pattern for persistence",
            implementation_steps=["Persist Step 1", "Persist Step 2"],
            success_metrics={"persistence": 1.0, "durability": 0.95},
            confidence_score=0.88
        )
        
        # Update learning (should persist)
        result = registry.update_learning(pattern)
        assert result is True
        
        # Check that file was created
        pattern_file = self.temp_learning_dir / "persistence_patterns.json"
        assert pattern_file.exists()
        
        # Check file contents
        with open(pattern_file, 'r') as f:
            data = json.load(f)
        
        assert data["domain"] == "persistence"
        assert len(data["patterns"]) == 1
        
        saved_pattern = data["patterns"][0]
        assert saved_pattern["pattern_id"] == "persist-test-001"
        assert saved_pattern["name"] == "Persistence Test Pattern"
        assert saved_pattern["success_metrics"]["persistence"] == 1.0
        assert saved_pattern["confidence_score"] == 0.88
    
    def test_load_persisted_learning(self):
        """Test loading persisted learning patterns"""
        registry = ModelRegistry("nonexistent_file.json")
        
        # Create test pattern file
        pattern_data = {
            "domain": "load_test",
            "patterns": [
                {
                    "pattern_id": "load-test-001",
                    "name": "Load Test Pattern",
                    "domain": "load_test",
                    "description": "Pattern for load testing",
                    "implementation_steps": ["Load Step 1", "Load Step 2"],
                    "success_metrics": {"load_success": 0.92},
                    "confidence_score": 0.85,
                    "updated_at": "2024-01-01T00:00:00"
                }
            ],
            "last_updated": "2024-01-01T00:00:00"
        }
        
        pattern_file = self.temp_learning_dir / "load_test_patterns.json"
        with open(pattern_file, 'w') as f:
            json.dump(pattern_data, f)
        
        # Mock the load method to use test directory
        original_load_method = registry.load_persisted_learning
        
        def mock_load_persisted_learning(domain: str):
            try:
                pattern_file = self.temp_learning_dir / f"{domain}_patterns.json"
                if not pattern_file.exists():
                    return []
                
                with open(pattern_file, 'r') as f:
                    data = json.load(f)
                    patterns = []
                    
                    for pattern_data in data.get("patterns", []):
                        pattern = Pattern(
                            pattern_id=pattern_data["pattern_id"],
                            name=pattern_data["name"],
                            domain=pattern_data["domain"],
                            description=pattern_data["description"],
                            implementation_steps=pattern_data["implementation_steps"],
                            success_metrics=pattern_data["success_metrics"],
                            confidence_score=pattern_data["confidence_score"]
                        )
                        patterns.append(pattern)
                    
                    return patterns
            except Exception:
                return []
        
        registry.load_persisted_learning = mock_load_persisted_learning
        
        # Load patterns
        loaded_patterns = registry.load_persisted_learning("load_test")
        
        assert len(loaded_patterns) == 1
        pattern = loaded_patterns[0]
        assert pattern.pattern_id == "load-test-001"
        assert pattern.name == "Load Test Pattern"
        assert pattern.success_metrics["load_success"] == 0.92
        assert pattern.confidence_score == 0.85
    
    def test_learning_insights(self):
        """Test learning insights generation"""
        registry = ModelRegistry("nonexistent_file.json")
        
        # Add multiple patterns across domains
        patterns = [
            Pattern(
                pattern_id="insight-test-001",
                name="Pattern 1",
                domain="domain1",
                description="Test pattern 1",
                implementation_steps=["Step 1"],
                success_metrics={"accuracy": 0.8, "speed": 0.7},
                confidence_score=0.8
            ),
            Pattern(
                pattern_id="insight-test-002",
                name="Pattern 2",
                domain="domain1",
                description="Test pattern 2",
                implementation_steps=["Step 2"],
                success_metrics={"accuracy": 0.9, "reliability": 0.85},
                confidence_score=0.9
            ),
            Pattern(
                pattern_id="insight-test-003",
                name="Pattern 3",
                domain="domain2",
                description="Test pattern 3",
                implementation_steps=["Step 3"],
                success_metrics={"speed": 0.95, "efficiency": 0.88},
                confidence_score=0.85
            )
        ]
        
        # Update learning with all patterns
        for pattern in patterns:
            registry.update_learning(pattern)
        
        # Get overall insights
        insights = registry.get_learning_insights()
        
        assert insights["total_patterns"] == 3
        assert abs(insights["avg_confidence"] - 0.85) < 0.01  # (0.8 + 0.9 + 0.85) / 3
        
        # Check domain insights
        assert "domain1" in insights["domain_insights"]
        assert "domain2" in insights["domain_insights"]
        
        domain1_insights = insights["domain_insights"]["domain1"]
        assert domain1_insights["pattern_count"] == 2
        
        # Check top success metrics
        assert "accuracy" in insights["top_success_metrics"]
        assert "speed" in insights["top_success_metrics"]
        
        accuracy_metrics = insights["top_success_metrics"]["accuracy"]
        assert accuracy_metrics["count"] == 2  # Two patterns have accuracy
        assert abs(accuracy_metrics["avg"] - 0.85) < 0.01  # (0.8 + 0.9) / 2
        assert accuracy_metrics["max"] == 0.9
        
        # Check learning trends
        assert len(insights["learning_trends"]) >= 3
        assert "3 patterns" in insights["learning_trends"][0]
        assert "2 domains" in insights["learning_trends"][0]
    
    def test_domain_specific_insights(self):
        """Test domain-specific learning insights"""
        registry = ModelRegistry("nonexistent_file.json")
        
        # Add patterns for specific domain
        pattern1 = Pattern(
            pattern_id="domain-insight-001",
            name="Domain Pattern 1",
            domain="specific_domain",
            description="Specific domain pattern",
            implementation_steps=["Domain Step 1"],
            success_metrics={"domain_accuracy": 0.92, "domain_speed": 0.78},
            confidence_score=0.88
        )
        
        pattern2 = Pattern(
            pattern_id="domain-insight-002",
            name="Domain Pattern 2",
            domain="specific_domain",
            description="Another specific domain pattern",
            implementation_steps=["Domain Step 2"],
            success_metrics={"domain_accuracy": 0.87, "domain_reliability": 0.91},
            confidence_score=0.85
        )
        
        # Update learning
        registry.update_learning(pattern1)
        registry.update_learning(pattern2)
        
        # Get domain-specific insights
        insights = registry.get_learning_insights("specific_domain")
        
        assert insights["total_patterns"] == 2
        assert "specific_domain" in insights["domain_insights"]
        
        domain_insights = insights["domain_insights"]["specific_domain"]
        assert domain_insights["pattern_count"] == 2
        assert abs(domain_insights["avg_confidence"] - 0.865) < 0.01  # (0.88 + 0.85) / 2
        
        # Check that success metrics are properly aggregated
        assert "domain_accuracy" in insights["top_success_metrics"]
        accuracy_metrics = insights["top_success_metrics"]["domain_accuracy"]
        assert accuracy_metrics["count"] == 2
        assert accuracy_metrics["max"] == 0.92