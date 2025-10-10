"""
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
\t@echo "Target A"

b: c
\t@echo "Target B"

c: a
\t@echo "Target C"
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
