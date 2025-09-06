"""
Unit tests for ModelRegistry

Tests model-driven intelligence system with project registry integration.
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

from src.beast_mode.core.model_registry import ModelRegistry, DomainInfo
from src.beast_mode.core.pdca_models import (
    ModelIntelligence, Requirement, Pattern, Tool, ValidationLevel
)


class TestModelRegistry:
    """Test ModelRegistry functionality"""
    
    def setup_method(self):
        """Set up test data"""
        self.test_registry_data = {
            "description": "Test Registry",
            "domain_architecture": {
                "overview": {
                    "total_domains": 2,
                    "compliance_standard": "Reflective Module (RM)"
                },
                "core_domains": {
                    "description": "Core system domains",
                    "purpose": "Provide core functionality",
                    "compliance": "RM compliant",
                    "domains": ["testing", "validation"]
                },
                "support_domains": {
                    "description": "Support system domains", 
                    "purpose": "Provide support functionality",
                    "compliance": "RM compliant",
                    "domains": ["logging", "monitoring"]
                }
            }
        }
    
    def test_create_model_registry_with_valid_file(self):
        """Test creating ModelRegistry with valid registry file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_registry_data, f)
            registry_path = f.name
        
        try:
            registry = ModelRegistry(registry_path)
            
            assert len(registry.registry_data) > 0
            assert len(registry.domain_cache) == 4  # testing, validation, logging, monitoring
            assert "testing" in registry.domain_cache
            assert "validation" in registry.domain_cache
            assert "logging" in registry.domain_cache
            assert "monitoring" in registry.domain_cache
            
        finally:
            Path(registry_path).unlink()
    
    def test_create_model_registry_with_missing_file(self):
        """Test creating ModelRegistry with missing registry file"""
        registry = ModelRegistry("nonexistent_file.json")
        
        # Should create default registry
        assert len(registry.registry_data) > 0
        assert "description" in registry.registry_data
        assert registry.registry_data["description"] == "Default Beast Mode Registry"
    
    def test_domain_cache_building(self):
        """Test domain cache building from registry data"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_registry_data, f)
            registry_path = f.name
        
        try:
            registry = ModelRegistry(registry_path)
            
            # Check domain info
            testing_domain = registry.domain_cache["testing"]
            assert testing_domain.domain_name == "testing"
            assert testing_domain.description == "Core system domains"
            assert testing_domain.purpose == "Provide core functionality"
            assert testing_domain.compliance == "RM compliant"
            
        finally:
            Path(registry_path).unlink()
    
    def test_query_requirements_for_known_domain(self):
        """Test querying requirements for known domain"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_registry_data, f)
            registry_path = f.name
        
        try:
            registry = ModelRegistry(registry_path)
            requirements = registry.query_requirements("testing")
            
            assert len(requirements) >= 3  # RM, systematic, purpose requirements
            
            # Check RM requirement
            rm_req = next((r for r in requirements if "RM" in r.description), None)
            assert rm_req is not None
            assert rm_req.domain == "testing"
            assert rm_req.priority == 1
            
            # Check systematic requirement
            sys_req = next((r for r in requirements if "systematic" in r.description), None)
            assert sys_req is not None
            assert "systematic patterns" in sys_req.acceptance_criteria[0]
            
        finally:
            Path(registry_path).unlink()
    
    def test_query_requirements_for_unknown_domain(self):
        """Test querying requirements for unknown domain"""
        registry = ModelRegistry("nonexistent_file.json")
        requirements = registry.query_requirements("unknown_domain")
        
        assert len(requirements) >= 1
        default_req = requirements[0]
        assert default_req.domain == "unknown_domain"
        assert "basic systematic approach" in default_req.description
    
    def test_get_domain_patterns(self):
        """Test getting domain patterns"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_registry_data, f)
            registry_path = f.name
        
        try:
            registry = ModelRegistry(registry_path)
            patterns = registry.get_domain_patterns("testing")
            
            assert len(patterns) >= 2  # RM pattern + systematic pattern
            
            # Check RM pattern
            rm_pattern = next((p for p in patterns if "Reflective Module" in p.name), None)
            assert rm_pattern is not None
            assert rm_pattern.domain == "testing"
            assert "ReflectiveModule" in rm_pattern.implementation_steps[0]
            
            # Check systematic pattern
            sys_pattern = next((p for p in patterns if "Systematic" in p.name), None)
            assert sys_pattern is not None
            assert "model registry" in sys_pattern.implementation_steps[0]
            
        finally:
            Path(registry_path).unlink()
    
    def test_get_tool_mappings_for_testing_domain(self):
        """Test getting tool mappings for testing domain"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_registry_data, f)
            registry_path = f.name
        
        try:
            registry = ModelRegistry(registry_path)
            tools = registry.get_tool_mappings("testing")
            
            assert "pytest" in tools
            pytest_tool = tools["pytest"]
            assert pytest_tool.name == "pytest"
            assert pytest_tool.domain == "testing"
            assert "systematic unit testing" in pytest_tool.purpose
            assert "pytest" in pytest_tool.command_template
            
        finally:
            Path(registry_path).unlink()
    
    def test_get_tool_mappings_for_code_domain(self):
        """Test getting tool mappings for code-related domain"""
        registry = ModelRegistry("nonexistent_file.json")
        tools = registry.get_tool_mappings("code_implementation")
        
        assert "black" in tools
        assert "mypy" in tools
        
        black_tool = tools["black"]
        assert black_tool.name == "black"
        assert "systematic code formatting" in black_tool.purpose
        
        mypy_tool = tools["mypy"]
        assert mypy_tool.name == "mypy"
        assert "systematic type checking" in mypy_tool.purpose
    
    def test_update_learning(self):
        """Test updating learning patterns"""
        registry = ModelRegistry("nonexistent_file.json")
        
        # Create test pattern
        pattern = Pattern(
            pattern_id="test-pattern-001",
            name="Test Pattern",
            domain="testing",
            description="Test learning pattern",
            implementation_steps=["Step 1", "Step 2"],
            success_metrics={"accuracy": 0.95, "speed": 0.8},
            confidence_score=0.9
        )
        
        # Update learning
        result = registry.update_learning(pattern)
        assert result is True
        
        # Verify pattern was added
        intelligence = registry.get_domain_intelligence("testing")
        assert len(intelligence.patterns) > 0
        
        # Check if our pattern is there
        test_pattern = next((p for p in intelligence.patterns if p.pattern_id == "test-pattern-001"), None)
        assert test_pattern is not None
        assert test_pattern.name == "Test Pattern"
        
        # Check success metrics were updated
        assert "accuracy" in intelligence.success_metrics
        assert intelligence.success_metrics["accuracy"] == 0.95
    
    def test_get_domain_intelligence(self):
        """Test getting complete domain intelligence"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_registry_data, f)
            registry_path = f.name
        
        try:
            registry = ModelRegistry(registry_path)
            intelligence = registry.get_domain_intelligence("testing")
            
            assert intelligence.domain == "testing"
            assert len(intelligence.requirements) >= 3
            assert len(intelligence.patterns) >= 2
            assert len(intelligence.tools) >= 1
            assert intelligence.confidence_score > 0.0
            
        finally:
            Path(registry_path).unlink()
    
    def test_list_available_domains(self):
        """Test listing available domains"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_registry_data, f)
            registry_path = f.name
        
        try:
            registry = ModelRegistry(registry_path)
            domains = registry.list_available_domains()
            
            assert "testing" in domains
            assert "validation" in domains
            assert "logging" in domains
            assert "monitoring" in domains
            assert len(domains) == 4
            
        finally:
            Path(registry_path).unlink()
    
    def test_get_registry_stats(self):
        """Test getting registry statistics"""
        registry = ModelRegistry("nonexistent_file.json")
        
        # Perform some queries to generate stats
        registry.query_requirements("testing")
        registry.query_requirements("testing")  # Should hit cache
        
        stats = registry.get_registry_stats()
        
        assert "total_domains" in stats
        assert "cached_intelligence" in stats
        assert "query_count" in stats
        assert "cache_hit_rate" in stats
        assert "last_updated" in stats
        
        assert stats["query_count"] >= 2
        assert stats["cache_hit_rate"] > 0.0  # Should have some cache hits
    
    def test_caching_behavior(self):
        """Test caching behavior for performance"""
        registry = ModelRegistry("nonexistent_file.json")
        
        # First query - should not hit cache
        initial_cache_hits = registry.cache_hits
        requirements1 = registry.query_requirements("testing")
        
        # Second query - should hit cache
        requirements2 = registry.query_requirements("testing")
        final_cache_hits = registry.cache_hits
        
        assert final_cache_hits > initial_cache_hits
        assert requirements1 == requirements2  # Should be identical from cache


class TestReflectiveModuleInterface:
    """Test ReflectiveModule interface implementation"""
    
    def test_get_health_status(self):
        """Test health status reporting"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            test_data = {
                "domain_architecture": {
                    "test_domains": {
                        "domains": ["testing"],
                        "description": "Test",
                        "purpose": "Test",
                        "compliance": "RM compliant"
                    }
                }
            }
            json.dump(test_data, f)
            registry_path = f.name
        
        try:
            registry = ModelRegistry(registry_path)
            health = registry.get_health_status()
            
            assert health["status"] == "healthy"
            assert health["registry_loaded"] is True
            assert health["domains_available"] is True
            assert health["total_domains"] == 1
            assert "last_updated" in health
            
        finally:
            Path(registry_path).unlink()
    
    def test_get_performance_metrics(self):
        """Test performance metrics reporting"""
        registry = ModelRegistry("nonexistent_file.json")
        
        # Generate some activity
        registry.query_requirements("testing")
        registry.query_requirements("testing")  # Cache hit
        
        metrics = registry.get_performance_metrics()
        
        assert "query_count" in metrics
        assert "cache_hit_rate" in metrics
        assert "domains_cached" in metrics
        assert "avg_query_time" in metrics
        
        assert metrics["query_count"] >= 2.0
        assert metrics["cache_hit_rate"] > 0.0
    
    def test_validate_systematic_compliance(self):
        """Test systematic compliance validation"""
        # Test with no domains (LOW compliance)
        registry = ModelRegistry("nonexistent_file.json")
        compliance = registry.validate_systematic_compliance()
        assert compliance == ValidationLevel.LOW
        
        # Test with domains and cache activity (HIGH compliance)
        registry.query_requirements("testing")  # This will create cache entry
        registry.query_requirements("testing")  # This will hit cache
        compliance = registry.validate_systematic_compliance()
        assert compliance == ValidationLevel.HIGH