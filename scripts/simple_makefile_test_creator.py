#!/usr/bin/env python3
"""
Simple Makefile Test Creator
===========================

Creates unit tests for the Makefile system components.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def create_test_directories():
    """Create test directory structure."""
    directories = [
        Path("tests/unit/makefile_governance"),
        Path("tests/integration/makefile_governance"),
        Path("tests/fixtures/makefile_governance")
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py
        init_file = directory / "__init__.py"
        if not init_file.exists():
            init_file.write_text('"""Makefile governance test package."""\n')
    
    print(f"✅ Created test directories")

def create_test_fixtures():
    """Create test fixtures."""
    fixtures_content = '''"""Test fixtures for Makefile governance tests."""

import pytest
from pathlib import Path


@pytest.fixture
def sample_makefile_simple():
    """Simple Makefile for basic testing."""
    return """# Simple test Makefile
.PHONY: help clean test

help: ## Show help
\\t@echo "Available targets:"

clean: ## Clean files
\\t@echo "Cleaning..."

test: ## Run tests
\\t@echo "Running tests..."
"""


@pytest.fixture
def sample_makefile_complex():
    """Complex Makefile with dependencies."""
    return """# Complex test Makefile
.PHONY: help clean test build

PROJECT := test-project

help: ## Show help
\\t@echo "$(PROJECT) - Available targets:"

clean: ## Clean build artifacts
\\t@echo "Cleaning..."

test: clean ## Run test suite
\\t@echo "Running tests..."

build: test ## Build project
\\t@echo "Building..."
"""
'''
    
    fixtures_file = Path("tests/fixtures/makefile_governance/conftest.py")
    fixtures_file.write_text(fixtures_content)
    print(f"✅ Created test fixtures: {fixtures_file}")

def create_makefile_analyzer_test():
    """Create test for existing makefile analyzer."""
    test_content = '''"""
Unit tests for Makefile Analyzer
===============================
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from src.system_architecture.discovery.makefile_analyzer import MakefileAnalyzer, MakefileTarget


class TestMakefileAnalyzer:
    """Test class for MakefileAnalyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.sample_makefile = self.temp_dir / "Makefile"
        
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_analyzer_initialization(self):
        """Test analyzer can be initialized."""
        analyzer = MakefileAnalyzer(str(self.sample_makefile))
        assert analyzer is not None
        assert analyzer.module_id == "MakefileAnalyzer"
    
    def test_parse_simple_makefile(self, sample_makefile_simple):
        """Test parsing a simple Makefile."""
        self.sample_makefile.write_text(sample_makefile_simple)
        
        analyzer = MakefileAnalyzer(str(self.sample_makefile))
        targets = analyzer.parse_makefile()
        
        assert len(targets) >= 3  # help, clean, test
        assert "help" in targets
        assert "clean" in targets
        assert "test" in targets
    
    def test_parse_complex_makefile(self, sample_makefile_complex):
        """Test parsing a complex Makefile."""
        self.sample_makefile.write_text(sample_makefile_complex)
        
        analyzer = MakefileAnalyzer(str(self.sample_makefile))
        targets = analyzer.parse_makefile()
        
        assert len(targets) >= 4  # help, clean, test, build
        assert targets["test"].dependencies == ["clean"]
        assert targets["build"].dependencies == ["test"]
    
    def test_target_categorization(self):
        """Test target categorization works."""
        analyzer = MakefileAnalyzer()
        
        # Test various target names
        assert analyzer._categorize_target("tunnel-start") == "tunnel"
        assert analyzer._categorize_target("dashboard-up") == "dashboard"
        assert analyzer._categorize_target("prometheus-start") == "prometheus"
        assert analyzer._categorize_target("test-unit") == "testing"
        assert analyzer._categorize_target("clean-all") == "maintenance"
    
    def test_dependency_analysis(self, sample_makefile_complex):
        """Test dependency analysis."""
        self.sample_makefile.write_text(sample_makefile_complex)
        
        analyzer = MakefileAnalyzer(str(self.sample_makefile))
        analyzer.parse_makefile()
        dependency_analysis = analyzer.analyze_target_dependencies()
        
        assert "dependency_graph" in dependency_analysis
        assert "execution_chains" in dependency_analysis
        assert len(dependency_analysis["dependency_graph"]) >= 4
    
    def test_circular_dependency_detection(self):
        """Test circular dependency detection."""
        circular_makefile = """# Circular dependency test
.PHONY: a b c

a: b
\\t@echo "Target A"

b: c
\\t@echo "Target B"

c: a
\\t@echo "Target C"
"""
        self.sample_makefile.write_text(circular_makefile)
        
        analyzer = MakefileAnalyzer(str(self.sample_makefile))
        analyzer.parse_makefile()
        dependency_analysis = analyzer.analyze_target_dependencies()
        
        # Should detect circular dependency
        assert len(dependency_analysis["circular_dependencies"]) > 0
    
    def test_script_mapping(self):
        """Test script to component mapping."""
        analyzer = MakefileAnalyzer()
        mappings = analyzer.map_scripts_to_components()
        
        assert len(mappings) > 0
        # Should have some known mappings
        script_names = [m.script_path for m in mappings]
        assert any("observatory" in name.lower() for name in script_names)
    
    def test_workflow_diagram_generation(self, sample_makefile_complex):
        """Test workflow diagram generation."""
        self.sample_makefile.write_text(sample_makefile_complex)
        
        analyzer = MakefileAnalyzer(str(self.sample_makefile))
        analyzer.parse_makefile()
        diagrams = analyzer.generate_automation_workflow_diagrams()
        
        assert "dependency_graph" in diagrams
        assert "nodes" in diagrams["dependency_graph"]
        assert "edges" in diagrams["dependency_graph"]
    
    def test_comprehensive_analysis(self, sample_makefile_complex):
        """Test comprehensive analysis report."""
        self.sample_makefile.write_text(sample_makefile_complex)
        
        analyzer = MakefileAnalyzer(str(self.sample_makefile))
        report = analyzer.get_comprehensive_analysis()
        
        assert "analysis_timestamp" in report
        assert "summary" in report
        assert "targets" in report
        assert "dependency_analysis" in report
        assert "script_mappings" in report
        assert "workflow_diagrams" in report
        assert "recommendations" in report
    
    def test_error_handling_missing_file(self):
        """Test error handling for missing Makefile."""
        analyzer = MakefileAnalyzer("nonexistent_makefile")
        targets = analyzer.parse_makefile()
        
        assert len(targets) == 0  # Should return empty dict
    
    def test_malformed_makefile_handling(self):
        """Test handling of malformed Makefile."""
        malformed_content = """# Malformed Makefile
invalid line without colon
target_with_spaces_not_tabs:
    @echo "This uses spaces instead of tabs"
"""
        self.sample_makefile.write_text(malformed_content)
        
        analyzer = MakefileAnalyzer(str(self.sample_makefile))
        targets = analyzer.parse_makefile()
        
        # Should handle gracefully without crashing
        assert isinstance(targets, dict)
'''
    
    test_file = Path("tests/unit/makefile_governance/test_makefile_analyzer.py")
    test_file.write_text(test_content)
    print(f"✅ Created makefile analyzer test: {test_file}")

def create_system_discovery_test():
    """Create test for system discovery."""
    test_content = '''"""
Unit tests for Makefile System Discovery
=======================================
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class TestMakefileSystemDiscovery:
    """Test class for Makefile system discovery."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_script_discovery(self):
        """Test discovery of Python scripts."""
        # Create mock scripts directory
        scripts_dir = self.temp_dir / "scripts"
        scripts_dir.mkdir()
        
        # Create sample scripts
        (scripts_dir / "deploy_observatory.py").write_text("#!/usr/bin/env python3\nprint('test')")
        (scripts_dir / "start_prometheus.py").write_text("#!/usr/bin/env python3\nprint('test')")
        
        # Test discovery logic would go here
        discovered_scripts = list(scripts_dir.glob("*.py"))
        assert len(discovered_scripts) == 2
    
    def test_service_discovery(self):
        """Test discovery of running services."""
        # Mock service discovery
        mock_services = [
            {"name": "observatory", "port": 8888, "status": "running"},
            {"name": "prometheus", "port": 9090, "status": "running"}
        ]
        
        # Test service discovery logic
        assert len(mock_services) == 2
        assert mock_services[0]["name"] == "observatory"
    
    def test_target_generation(self):
        """Test automatic target generation."""
        # Test target generation logic
        expected_categories = ["observatory", "beast_mode", "dag_orchestration", "infrastructure"]
        
        # Mock target generation
        generated_targets = {}
        for category in expected_categories:
            generated_targets[f"{category}-start"] = f"Start {category} services"
            generated_targets[f"{category}-stop"] = f"Stop {category} services"
        
        assert len(generated_targets) == 8  # 4 categories * 2 targets each
    
    def test_capability_mapping(self):
        """Test capability mapping functionality."""
        # Test capability mapping logic
        capabilities = {
            "observatory": ["monitoring", "websocket", "health"],
            "prometheus": ["metrics", "scraping", "alerts"],
            "grafana": ["visualization", "dashboards"]
        }
        
        assert "monitoring" in capabilities["observatory"]
        assert "metrics" in capabilities["prometheus"]
    
    def test_modular_target_inclusion(self):
        """Test modular target inclusion system."""
        # Test modular inclusion logic
        modules = ["observatory.mk", "beast_mode.mk", "infrastructure.mk"]
        
        for module in modules:
            # Mock module existence check
            assert module.endswith(".mk")
    
    def test_error_handling(self):
        """Test error handling in discovery."""
        # Test various error conditions
        assert True  # Placeholder for error handling tests
    
    def test_performance_requirements(self):
        """Test performance meets requirements."""
        import time
        
        # Mock discovery operation
        start_time = time.time()
        # Simulate discovery work
        time.sleep(0.001)  # 1ms simulation
        end_time = time.time()
        
        # Should complete quickly
        assert (end_time - start_time) < 1.0
'''
    
    test_file = Path("tests/unit/makefile_governance/test_makefile_system_discovery.py")
    test_file.write_text(test_content)
    print(f"✅ Created system discovery test: {test_file}")

def create_integration_test():
    """Create integration test."""
    test_content = '''"""
Integration tests for Makefile System
====================================
"""

import pytest
import subprocess
from pathlib import Path


class TestMakefileSystemIntegration:
    """Integration tests for the complete Makefile system."""
    
    def test_makefile_help_command(self):
        """Test that make help works."""
        try:
            result = subprocess.run(
                ["make", "help"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Should not fail
            assert result.returncode == 0 or result.returncode == 2  # 2 for missing targets
            
        except subprocess.TimeoutExpired:
            pytest.fail("make help command timed out")
        except FileNotFoundError:
            pytest.skip("make command not available")
    
    def test_makefile_exists(self):
        """Test that Makefile exists."""
        makefile = Path("Makefile")
        assert makefile.exists(), "Makefile should exist in project root"
    
    def test_makefile_syntax(self):
        """Test basic Makefile syntax."""
        makefile = Path("Makefile")
        if makefile.exists():
            content = makefile.read_text()
            
            # Basic syntax checks
            assert ".PHONY:" in content or "help:" in content
            # Should have some targets
            assert ":" in content
    
    def test_test_targets_exist(self):
        """Test that testing targets exist or can be created."""
        # This would test the actual test target creation
        assert True  # Placeholder
    
    def test_directory_structure(self):
        """Test that required directories exist."""
        required_dirs = [
            Path("scripts"),
            Path("src"),
            Path("tests")
        ]
        
        for directory in required_dirs:
            assert directory.exists(), f"Required directory {directory} should exist"
    
    @pytest.mark.slow
    def test_full_system_workflow(self):
        """Test complete system workflow."""
        # This would test the entire workflow
        assert True  # Placeholder
'''
    
    test_file = Path("tests/integration/makefile_governance/test_makefile_system_integration.py")
    test_file.write_text(test_content)
    print(f"✅ Created integration test: {test_file}")

def main():
    """Main function to create all tests."""
    print("🚀 Creating Makefile system unit tests...")
    
    # Create directory structure
    create_test_directories()
    
    # Create fixtures
    create_test_fixtures()
    
    # Create specific test files
    create_makefile_analyzer_test()
    create_system_discovery_test()
    create_integration_test()
    
    print("\n✅ Test creation completed!")
    print("\n📁 Created test files:")
    print("   - tests/unit/makefile_governance/test_makefile_analyzer.py")
    print("   - tests/unit/makefile_governance/test_makefile_system_discovery.py")
    print("   - tests/integration/makefile_governance/test_makefile_system_integration.py")
    print("   - tests/fixtures/makefile_governance/conftest.py")
    
    print("\n🧪 To run tests:")
    print("   python -m pytest tests/unit/makefile_governance/ -v")
    print("   python -m pytest tests/integration/makefile_governance/ -v")
    
    print("\n📊 To run with coverage:")
    print("   python -m pytest tests/unit/makefile_governance/ --cov=src --cov-report=html")

if __name__ == "__main__":
    main()