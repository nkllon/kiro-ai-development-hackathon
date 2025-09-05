"""
Performance Tests for Dependency Analysis Edge Cases

This module provides comprehensive tests for the dependency analysis system,
focusing on edge cases and performance scenarios.
"""

import pytest
import time
from pathlib import Path
from typing import Dict, List
from unittest.mock import Mock, patch

from src.beast_mode.domain_index.dependency_analyzer import (
    CircularDependencyDetector,
    OrphanedFileDetector,
    DependencyImpactAnalyzer,
    ComprehensiveDependencyAnalyzer
)
from src.beast_mode.domain_index.models import (
    Domain, DomainTools, DomainMetadata, PackagePotential
)


class TestCircularDependencyDetector:
    """Test circular dependency detection algorithms"""
    
    def create_test_domain(self, name: str, dependencies: List[str] = None) -> Domain:
        """Create a test domain with minimal required fields"""
        tools = DomainTools(linter="pylint", formatter="black", validator="mypy")
        package_potential = PackagePotential(score=0.5, reasons=[], dependencies=[], 
                                           estimated_effort="medium", blockers=[])
        metadata = DomainMetadata(demo_role="test", extraction_candidate="unknown", 
                                package_potential=package_potential)
        
        return Domain(
            name=name,
            description=f"Test domain {name}",
            patterns=[f"src/{name}/**/*.py"],
            content_indicators=[name],
            requirements=[],
            dependencies=dependencies or [],
            tools=tools,
            metadata=metadata
        )
    
    def test_no_circular_dependencies(self):
        """Test detection when no circular dependencies exist"""
        domains = {
            "A": self.create_test_domain("A", ["B"]),
            "B": self.create_test_domain("B", ["C"]),
            "C": self.create_test_domain("C", [])
        }
        
        detector = CircularDependencyDetector(domains)
        cycles = detector.detect_cycles_dfs()
        
        assert len(cycles) == 0
    
    def test_simple_circular_dependency(self):
        """Test detection of simple A->B->A cycle"""
        domains = {
            "A": self.create_test_domain("A", ["B"]),
            "B": self.create_test_domain("B", ["A"])
        }
        
        detector = CircularDependencyDetector(domains)
        cycles = detector.detect_cycles_dfs()
        
        assert len(cycles) == 1
        assert len(cycles[0]) == 3  # A -> B -> A
        assert cycles[0][0] == cycles[0][-1]  # First and last should be the same
    
    def test_complex_circular_dependency(self):
        """Test detection of complex A->B->C->D->A cycle"""
        domains = {
            "A": self.create_test_domain("A", ["B"]),
            "B": self.create_test_domain("B", ["C"]),
            "C": self.create_test_domain("C", ["D"]),
            "D": self.create_test_domain("D", ["A"])
        }
        
        detector = CircularDependencyDetector(domains)
        cycles = detector.detect_cycles_dfs()
        
        assert len(cycles) == 1
        assert len(cycles[0]) == 5  # A -> B -> C -> D -> A
    
    def test_multiple_circular_dependencies(self):
        """Test detection of multiple independent cycles"""
        domains = {
            "A": self.create_test_domain("A", ["B"]),
            "B": self.create_test_domain("B", ["A"]),
            "C": self.create_test_domain("C", ["D"]),
            "D": self.create_test_domain("D", ["E"]),
            "E": self.create_test_domain("E", ["C"]),
            "F": self.create_test_domain("F", [])
        }
        
        detector = CircularDependencyDetector(domains)
        cycles = detector.detect_cycles_dfs()
        
        assert len(cycles) == 2
    
    def test_self_dependency(self):
        """Test detection of self-dependency (A->A)"""
        domains = {
            "A": self.create_test_domain("A", ["A"])
        }
        
        detector = CircularDependencyDetector(domains)
        cycles = detector.detect_cycles_dfs()
        
        assert len(cycles) == 1
        assert cycles[0] == ["A", "A"]
    
    def test_tarjan_algorithm_consistency(self):
        """Test that Tarjan's algorithm produces consistent results with DFS"""
        domains = {
            "A": self.create_test_domain("A", ["B", "C"]),
            "B": self.create_test_domain("B", ["D"]),
            "C": self.create_test_domain("C", ["D"]),
            "D": self.create_test_domain("D", ["A"])
        }
        
        detector = CircularDependencyDetector(domains)
        dfs_cycles = detector.detect_cycles_dfs()
        tarjan_sccs = detector.detect_cycles_tarjan()
        
        # Both should detect the same cycle
        assert len(dfs_cycles) > 0
        assert len(tarjan_sccs) > 0
    
    def test_cycle_impact_analysis(self):
        """Test cycle impact analysis functionality"""
        domains = {
            "A": self.create_test_domain("A", ["B"]),
            "B": self.create_test_domain("B", ["A"])
        }
        
        # Set some file counts for impact analysis
        domains["A"].file_count = 10
        domains["A"].line_count = 1000
        domains["B"].file_count = 5
        domains["B"].line_count = 500
        
        detector = CircularDependencyDetector(domains)
        cycles = detector.detect_cycles_dfs()
        
        assert len(cycles) > 0
        
        impact = detector.analyze_cycle_impact(cycles[0])
        
        assert "cycle_path" in impact
        assert "complexity_score" in impact
        assert "total_files_affected" in impact
        assert "total_lines_affected" in impact
        assert impact["total_files_affected"] == 15
        assert impact["total_lines_affected"] == 1500
    
    def test_performance_large_graph(self):
        """Test performance with large dependency graph"""
        # Create a large graph with 100 domains
        domains = {}
        for i in range(100):
            deps = [f"domain_{j}" for j in range(max(0, i-3), i)]  # Each domain depends on previous 3
            domains[f"domain_{i}"] = self.create_test_domain(f"domain_{i}", deps)
        
        # Add one circular dependency at the end
        domains["domain_99"].dependencies.append("domain_95")
        
        detector = CircularDependencyDetector(domains)
        
        start_time = time.time()
        cycles = detector.detect_cycles_dfs()
        end_time = time.time()
        
        # Should complete within reasonable time (< 1 second)
        assert (end_time - start_time) < 1.0
        assert len(cycles) == 1  # Should find the one cycle we added


class TestOrphanedFileDetector:
    """Test orphaned file detection algorithms"""
    
    def create_test_domains_with_patterns(self) -> Dict[str, Domain]:
        """Create test domains with specific patterns"""
        tools = DomainTools(linter="pylint", formatter="black", validator="mypy")
        package_potential = PackagePotential(score=0.5, reasons=[], dependencies=[], 
                                           estimated_effort="medium", blockers=[])
        metadata = DomainMetadata(demo_role="test", extraction_candidate="unknown", 
                                package_potential=package_potential)
        
        return {
            "core": Domain(
                name="core",
                description="Core domain",
                patterns=["src/core/**/*.py"],
                content_indicators=["core"],
                requirements=[],
                dependencies=[],
                tools=tools,
                metadata=metadata
            ),
            "utils": Domain(
                name="utils",
                description="Utils domain",
                patterns=["src/utils/**/*.py"],
                content_indicators=["utils"],
                requirements=[],
                dependencies=[],
                tools=tools,
                metadata=metadata
            )
        }
    
    @patch('pathlib.Path.glob')
    def test_no_orphaned_files(self, mock_glob):
        """Test when all files are covered by domain patterns"""
        # Mock file system to return files that match patterns
        mock_glob.return_value = [
            Path("src/core/main.py"),
            Path("src/core/helper.py"),
            Path("src/utils/tools.py")
        ]
        
        domains = self.create_test_domains_with_patterns()
        project_root = Path("/test/project")
        
        detector = OrphanedFileDetector(domains, project_root)
        
        with patch.object(detector, '_file_matches_pattern', return_value=True):
            result = detector.detect_orphaned_files()
        
        assert len(result["orphaned_files"]) == 0
        assert result["coverage_percentage"] == 100.0
    
    @patch('pathlib.Path.glob')
    def test_orphaned_files_detected(self, mock_glob):
        """Test detection of orphaned files"""
        # Mock file system to return some files that don't match patterns
        mock_glob.return_value = [
            Path("src/core/main.py"),      # Covered
            Path("src/orphan/lonely.py"),  # Not covered
            Path("scripts/build.py")       # Not covered
        ]
        
        domains = self.create_test_domains_with_patterns()
        project_root = Path("/test/project")
        
        detector = OrphanedFileDetector(domains, project_root)
        
        def mock_file_matches(file_path, pattern):
            # Only core files match core patterns
            return "core" in str(file_path) and "core" in pattern
        
        with patch.object(detector, '_file_matches_pattern', side_effect=mock_file_matches):
            result = detector.detect_orphaned_files()
        
        assert len(result["orphaned_files"]) == 2
        assert "src/orphan/lonely.py" in result["orphaned_files"]
        assert "scripts/build.py" in result["orphaned_files"]
        assert result["coverage_percentage"] < 100.0
    
    def test_file_pattern_matching(self):
        """Test file pattern matching logic"""
        domains = self.create_test_domains_with_patterns()
        project_root = Path("/test/project")
        
        detector = OrphanedFileDetector(domains, project_root)
        
        # Test various pattern matching scenarios
        assert detector._file_matches_pattern(Path("src/core/main.py"), "src/core/**/*.py")
        assert detector._file_matches_pattern(Path("src/core/sub/helper.py"), "src/core/**/*.py")
        assert not detector._file_matches_pattern(Path("src/other/main.py"), "src/core/**/*.py")
    
    def test_orphaned_file_analysis(self):
        """Test analysis of orphaned files characteristics"""
        domains = self.create_test_domains_with_patterns()
        project_root = Path("/test/project")
        
        detector = OrphanedFileDetector(domains, project_root)
        
        orphaned_files = [
            "src/orphan/file1.py",
            "src/orphan/file2.py",
            "scripts/build.js",
            "tests/old_test.py"
        ]
        
        analysis = detector._analyze_orphaned_files(orphaned_files)
        
        assert ".py" in analysis["file_types"]
        assert ".js" in analysis["file_types"]
        assert analysis["file_types"][".py"] == 3
        assert analysis["file_types"][".js"] == 1
        
        assert "src/orphan" in analysis["directories"]
        assert "scripts" in analysis["directories"]
        assert "tests" in analysis["directories"]
    
    def test_domain_assignment_suggestions(self):
        """Test generation of domain assignment suggestions"""
        domains = self.create_test_domains_with_patterns()
        project_root = Path("/test/project")
        
        detector = OrphanedFileDetector(domains, project_root)
        
        orphaned_files = [
            "src/core_utils/helper.py",  # Should suggest core domain
            "src/new_feature/main.py"    # Should suggest new domain
        ]
        
        suggestions = detector._suggest_domain_assignments(orphaned_files)
        
        assert len(suggestions) == 2
        
        # Check that suggestions are generated for each directory
        directories = [s["directory"] for s in suggestions]
        assert "src/core_utils" in directories
        assert "src/new_feature" in directories
    
    @patch('pathlib.Path.glob')
    def test_performance_large_file_set(self, mock_glob):
        """Test performance with large number of files"""
        # Create a large set of mock files
        large_file_set = [Path(f"src/file_{i}.py") for i in range(1000)]
        mock_glob.return_value = large_file_set
        
        domains = self.create_test_domains_with_patterns()
        project_root = Path("/test/project")
        
        detector = OrphanedFileDetector(domains, project_root)
        
        with patch.object(detector, '_file_matches_pattern', return_value=False):
            start_time = time.time()
            result = detector.detect_orphaned_files()
            end_time = time.time()
        
        # Should complete within reasonable time (< 2 seconds)
        assert (end_time - start_time) < 2.0
        assert len(result["orphaned_files"]) == 1000


class TestDependencyImpactAnalyzer:
    """Test dependency impact analysis"""
    
    def create_test_domains_with_dependencies(self) -> Dict[str, Domain]:
        """Create test domains with dependency relationships"""
        tools = DomainTools(linter="pylint", formatter="black", validator="mypy")
        package_potential = PackagePotential(score=0.5, reasons=[], dependencies=[], 
                                           estimated_effort="medium", blockers=[])
        metadata = DomainMetadata(demo_role="test", extraction_candidate="unknown", 
                                package_potential=package_potential)
        
        domains = {}
        
        # Create a dependency chain: A -> B -> C -> D
        for name, deps in [("A", ["B"]), ("B", ["C"]), ("C", ["D"]), ("D", [])]:
            domain = Domain(
                name=name,
                description=f"Test domain {name}",
                patterns=[f"src/{name}/**/*.py"],
                content_indicators=[name],
                requirements=[],
                dependencies=deps,
                tools=tools,
                metadata=metadata,
                file_count=10,
                line_count=1000
            )
            domains[name] = domain
        
        return domains
    
    def test_impact_analysis_modify(self):
        """Test impact analysis for domain modification"""
        domains = self.create_test_domains_with_dependencies()
        analyzer = DependencyImpactAnalyzer(domains)
        
        # Analyze impact of modifying domain C
        impact = analyzer.analyze_change_impact("C", "modify")
        
        assert impact["target_domain"] == "C"
        assert impact["change_type"] == "modify"
        assert "A" in impact["transitively_affected"]  # A depends on B which depends on C
        assert "B" in impact["transitively_affected"]  # B depends on C
        assert "D" not in impact["transitively_affected"]  # D doesn't depend on C
    
    def test_impact_analysis_delete(self):
        """Test impact analysis for domain deletion"""
        domains = self.create_test_domains_with_dependencies()
        analyzer = DependencyImpactAnalyzer(domains)
        
        # Analyze impact of deleting domain B
        impact = analyzer.analyze_change_impact("B", "delete")
        
        assert impact["target_domain"] == "B"
        assert impact["change_type"] == "delete"
        assert "A" in impact["transitively_affected"]  # A depends on B
        assert len(impact["directly_affected"]) == 1  # Only A directly depends on B
    
    def test_impact_metrics_calculation(self):
        """Test calculation of impact metrics"""
        domains = self.create_test_domains_with_dependencies()
        analyzer = DependencyImpactAnalyzer(domains)
        
        impact = analyzer.analyze_change_impact("B", "modify")
        metrics = impact["impact_metrics"]
        
        assert "affected_domain_count" in metrics
        assert "total_affected_files" in metrics
        assert "total_affected_lines" in metrics
        assert "coupling_score" in metrics
        assert "impact_severity" in metrics
        
        # B affects A, so should have affected domains
        assert metrics["affected_domain_count"] > 0
        assert metrics["total_affected_files"] > 0
    
    def test_risk_assessment(self):
        """Test risk assessment for changes"""
        domains = self.create_test_domains_with_dependencies()
        analyzer = DependencyImpactAnalyzer(domains)
        
        impact = analyzer.analyze_change_impact("C", "delete")
        risk = impact["risk_assessment"]
        
        assert "risk_level" in risk
        assert "risk_score" in risk
        assert "risk_factors" in risk
        assert "mitigation_strategies" in risk
        
        assert risk["risk_level"] in ["low", "medium", "high"]
        assert 0.0 <= risk["risk_score"] <= 1.0
    
    def test_change_recommendations(self):
        """Test generation of change recommendations"""
        domains = self.create_test_domains_with_dependencies()
        analyzer = DependencyImpactAnalyzer(domains)
        
        impact = analyzer.analyze_change_impact("B", "delete")
        recommendations = impact["recommendations"]
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Should include recommendations specific to deletion
        rec_text = " ".join(recommendations).lower()
        assert "alternative" in rec_text or "deprecation" in rec_text
    
    def test_circular_dependency_detection_in_impact(self):
        """Test detection of circular dependencies in impact analysis"""
        # Create domains with circular dependency
        domains = self.create_test_domains_with_dependencies()
        domains["D"].dependencies = ["A"]  # Create cycle A->B->C->D->A
        
        analyzer = DependencyImpactAnalyzer(domains)
        impact = analyzer.analyze_change_impact("A", "modify")
        risk = impact["risk_assessment"]
        
        # Should detect circular dependency as risk factor
        risk_factors_text = " ".join(risk["risk_factors"]).lower()
        assert "circular" in risk_factors_text


class TestComprehensiveDependencyAnalyzer:
    """Test the main comprehensive dependency analyzer"""
    
    def create_mock_registry_manager(self):
        """Create a mock registry manager with test domains"""
        tools = DomainTools(linter="pylint", formatter="black", validator="mypy")
        package_potential = PackagePotential(score=0.5, reasons=[], dependencies=[], 
                                           estimated_effort="medium", blockers=[])
        metadata = DomainMetadata(demo_role="test", extraction_candidate="unknown", 
                                package_potential=package_potential)
        
        domains = {
            "A": Domain(
                name="A", description="Domain A", patterns=["src/A/**/*.py"],
                content_indicators=["A"], requirements=[], dependencies=["B"],
                tools=tools, metadata=metadata, file_count=10, line_count=1000
            ),
            "B": Domain(
                name="B", description="Domain B", patterns=["src/B/**/*.py"],
                content_indicators=["B"], requirements=[], dependencies=["A"],  # Circular!
                tools=tools, metadata=metadata, file_count=5, line_count=500
            ),
            "C": Domain(
                name="C", description="Domain C", patterns=["src/C/**/*.py"],
                content_indicators=["C"], requirements=[], dependencies=[],
                tools=tools, metadata=metadata, file_count=15, line_count=1500
            )
        }
        
        mock_registry = Mock()
        mock_registry.get_all_domains.return_value = domains
        mock_registry.get_domain.side_effect = lambda name: domains.get(name)
        
        return mock_registry
    
    def test_comprehensive_analysis_sequential(self):
        """Test comprehensive analysis in sequential mode"""
        mock_registry = self.create_mock_registry_manager()
        
        analyzer = ComprehensiveDependencyAnalyzer(
            registry_manager=mock_registry,
            config={"parallel_dependency_analysis": False}
        )
        analyzer.set_project_root("/test/project")
        
        with patch.object(analyzer, '_analyze_orphaned_files', return_value={"orphaned_files": []}):
            result = analyzer.perform_comprehensive_analysis()
        
        assert "circular_dependencies" in result
        assert "orphaned_files" in result
        assert "dependency_health" in result
        assert "summary" in result
        assert "recommendations" in result
        
        # Should detect the circular dependency we created
        assert result["circular_dependencies"]["has_circular_dependencies"]
        assert result["circular_dependencies"]["cycles_found"] > 0
    
    def test_comprehensive_analysis_parallel(self):
        """Test comprehensive analysis in parallel mode"""
        mock_registry = self.create_mock_registry_manager()
        
        analyzer = ComprehensiveDependencyAnalyzer(
            registry_manager=mock_registry,
            config={"parallel_dependency_analysis": True, "dependency_analysis_workers": 2}
        )
        analyzer.set_project_root("/test/project")
        
        with patch.object(analyzer, '_analyze_orphaned_files', return_value={"orphaned_files": []}):
            result = analyzer.perform_comprehensive_analysis()
        
        assert "circular_dependencies" in result
        assert "orphaned_files" in result
        assert "dependency_health" in result
        assert "summary" in result
        assert "recommendations" in result
    
    def test_domain_impact_analysis(self):
        """Test domain-specific impact analysis"""
        mock_registry = self.create_mock_registry_manager()
        
        analyzer = ComprehensiveDependencyAnalyzer(registry_manager=mock_registry)
        
        result = analyzer.analyze_domain_impact("A", "modify")
        
        assert "target_domain" in result
        assert "change_type" in result
        assert "impact_metrics" in result
        assert "risk_assessment" in result
        assert result["target_domain"] == "A"
    
    def test_analysis_summary_generation(self):
        """Test generation of analysis summary"""
        mock_registry = self.create_mock_registry_manager()
        
        analyzer = ComprehensiveDependencyAnalyzer(registry_manager=mock_registry)
        
        # Mock analysis results
        results = {
            "circular_dependencies": {
                "has_circular_dependencies": True,
                "cycles_found": 1
            },
            "orphaned_files": {
                "orphaned_files": ["orphan1.py", "orphan2.py"],
                "coverage_percentage": 85.0
            },
            "dependency_health": {
                "highly_coupled_domains": [{"domain": "A", "dependent_count": 6}]
            }
        }
        
        summary = analyzer._generate_analysis_summary(results)
        
        assert "overall_health" in summary
        assert "critical_issues" in summary
        assert "warnings" in summary
        
        # Should identify critical issues
        assert summary["overall_health"] == "critical"
        assert len(summary["critical_issues"]) > 0
    
    def test_performance_with_large_domain_set(self):
        """Test performance with large number of domains"""
        # Create a large set of domains
        tools = DomainTools(linter="pylint", formatter="black", validator="mypy")
        package_potential = PackagePotential(score=0.5, reasons=[], dependencies=[], 
                                           estimated_effort="medium", blockers=[])
        metadata = DomainMetadata(demo_role="test", extraction_candidate="unknown", 
                                package_potential=package_potential)
        
        large_domain_set = {}
        for i in range(50):  # 50 domains
            deps = [f"domain_{j}" for j in range(max(0, i-2), i)]  # Each depends on previous 2
            large_domain_set[f"domain_{i}"] = Domain(
                name=f"domain_{i}",
                description=f"Domain {i}",
                patterns=[f"src/domain_{i}/**/*.py"],
                content_indicators=[f"domain_{i}"],
                requirements=[],
                dependencies=deps,
                tools=tools,
                metadata=metadata,
                file_count=10,
                line_count=1000
            )
        
        mock_registry = Mock()
        mock_registry.get_all_domains.return_value = large_domain_set
        mock_registry.get_domain.side_effect = lambda name: large_domain_set.get(name)
        
        analyzer = ComprehensiveDependencyAnalyzer(registry_manager=mock_registry)
        analyzer.set_project_root("/test/project")
        
        with patch.object(analyzer, '_analyze_orphaned_files', return_value={"orphaned_files": []}):
            start_time = time.time()
            result = analyzer.perform_comprehensive_analysis()
            end_time = time.time()
        
        # Should complete within reasonable time (< 5 seconds for 50 domains)
        assert (end_time - start_time) < 5.0
        assert "circular_dependencies" in result
        assert "dependency_health" in result
    
    def test_error_handling(self):
        """Test error handling in comprehensive analysis"""
        # Test with no registry manager
        analyzer = ComprehensiveDependencyAnalyzer()
        
        result = analyzer.perform_comprehensive_analysis()
        
        assert "error" in result
        assert "Registry manager not set" in result["error"]
    
    def test_analyzer_stats(self):
        """Test analyzer statistics reporting"""
        mock_registry = self.create_mock_registry_manager()
        
        analyzer = ComprehensiveDependencyAnalyzer(registry_manager=mock_registry)
        
        stats = analyzer.get_analyzer_stats()
        
        assert "component_stats" in stats
        assert "project_root" in stats
        assert "parallel_analysis_enabled" in stats
        assert "analyzers_initialized" in stats
        assert "performance_metrics" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])