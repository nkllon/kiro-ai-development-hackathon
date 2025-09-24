"""
Tests for Content Discovery Engine
=================================

Unit tests for the Ghostbusters Content Discovery Engine.

Author: Beast Mode Framework + Ghostbusters
Date: 2025-09-24
Purpose: Test the eyes of our supernatural productivity explosion scanner!
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.beast_mode.ghostbusters.productivity_triage.content_discovery import ContentDiscoveryEngine
from src.beast_mode.ghostbusters.productivity_triage import (
    TriageConfig,
    WorkArtifact,
    ArtifactType,
    DomainType,
    CompletionStatus,
    ReadinessStatus,
)
from src.rm_ddd.core.unified_reflective_module import ModuleStatus, ModuleCapability


class TestContentDiscoveryEngine:
    """Test suite for ContentDiscoveryEngine"""
    
    def test_engine_initialization(self):
        """Test that engine initializes correctly"""
        engine = ContentDiscoveryEngine()
        
        assert engine.module_id == "ghostbusters_content_discovery_engine"
        assert len(engine.discovered_artifacts) == 0
        assert len(engine.scan_cache) == 0
    
    def test_get_module_info(self):
        """Test ReflectiveModule get_module_info implementation"""
        engine = ContentDiscoveryEngine()
        
        info = engine.get_module_info()
        
        assert info["module_id"] == "ghostbusters_content_discovery_engine"
        assert info["module_name"] == "ContentDiscoveryEngine"
        assert info["version"] == "1.0.0"
        assert "capabilities" in info
        assert info["artifacts_discovered"] == 0
    
    def test_get_capabilities(self):
        """Test ReflectiveModule get_capabilities implementation"""
        engine = ContentDiscoveryEngine()
        
        capabilities = engine.get_capabilities()
        
        expected_capabilities = [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
        ]
        
        assert capabilities == expected_capabilities
    
    def test_get_health_status_healthy(self):
        """Test health status when engine is healthy"""
        engine = ContentDiscoveryEngine()
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)
            
            health = engine.get_health_status()
            
            assert health.module_id == "ghostbusters_content_discovery_engine"
            assert health.status == ModuleStatus.HEALTHY
            assert health.health_score == 1.0
            assert len(health.issues) == 0
    
    def test_get_health_status_git_unavailable(self):
        """Test health status when git is unavailable"""
        engine = ContentDiscoveryEngine()
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=1)
            
            health = engine.get_health_status()
            
            assert health.status in [ModuleStatus.WARNING, ModuleStatus.ERROR]
            assert health.health_score < 1.0
            assert any("Git" in issue for issue in health.issues)
    
    def test_graceful_degradation(self):
        """Test graceful degradation functionality"""
        engine = ContentDiscoveryEngine()
        
        result = engine.graceful_degradation()
        
        assert result.success is True
        assert ModuleCapability.CORE_FUNCTIONALITY in result.remaining_capabilities
        assert ModuleCapability.DATA_PROCESSING in result.remaining_capabilities
    
    def test_classify_artifact_type(self):
        """Test artifact type classification"""
        engine = ContentDiscoveryEngine()
        
        # Test Python code file
        assert engine._classify_artifact_type("src/module.py") == ArtifactType.CODE
        
        # Test Python test file
        assert engine._classify_artifact_type("tests/test_module.py") == ArtifactType.TEST
        
        # Test markdown spec
        assert engine._classify_artifact_type(".kiro/specs/feature/requirements.md") == ArtifactType.SPEC
        
        # Test documentation
        assert engine._classify_artifact_type("docs/readme.md") == ArtifactType.DOCUMENTATION
        
        # Test configuration
        assert engine._classify_artifact_type("config.json") == ArtifactType.CONFIGURATION
        
        # Test script
        assert engine._classify_artifact_type("scripts/deploy.sh") == ArtifactType.SCRIPT
        
        # Test unknown
        assert engine._classify_artifact_type("file.xyz") == ArtifactType.UNKNOWN
    
    def test_classify_domain(self):
        """Test domain classification"""
        engine = ContentDiscoveryEngine()
        
        # Test task queue domain
        assert engine._classify_domain("src/beast_mode/task_queue/models.py") == DomainType.TASK_QUEUE
        
        # Test MCP integrations domain
        assert engine._classify_domain("src/beast_mode/mcp_integrations/calendar.py") == DomainType.MCP_INTEGRATIONS
        
        # Test Ghostbusters domain
        assert engine._classify_domain("src/beast_mode/ghostbusters/triage.py") == DomainType.GHOSTBUSTERS
        
        # Test release automation
        assert engine._classify_domain("scripts/release-the-hounds.py") == DomainType.RELEASE_AUTOMATION
        
        # Test Beast Mode core
        assert engine._classify_domain("src/beast_mode/core/module.py") == DomainType.BEAST_MODE_CORE
        
        # Test unknown domain
        assert engine._classify_domain("random/file.py") == DomainType.UNKNOWN
    
    def test_assess_completion_status_empty_file(self):
        """Test completion status assessment for empty file"""
        engine = ContentDiscoveryEngine()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("")  # Empty file
            temp_path = f.name
        
        try:
            status = engine._assess_completion_status(temp_path)
            assert status == CompletionStatus.PLACEHOLDER
        finally:
            os.unlink(temp_path)
    
    def test_assess_completion_status_todo_file(self):
        """Test completion status assessment for file with TODOs"""
        engine = ContentDiscoveryEngine()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def function():\n    # TODO: implement this\n    pass\n")
            temp_path = f.name
        
        try:
            status = engine._assess_completion_status(temp_path)
            assert status == CompletionStatus.PARTIAL
        finally:
            os.unlink(temp_path)
    
    def test_assess_completion_status_complete_file(self):
        """Test completion status assessment for complete file"""
        engine = ContentDiscoveryEngine()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            # Write a substantial file without TODOs (45+ lines)
            content = "class CompleteClass:\n" + "    def method(self):\n        return 'complete'\n" * 25
            f.write(content)
            temp_path = f.name
        
        try:
            status = engine._assess_completion_status(temp_path)
            assert status == CompletionStatus.COMPLETE
        finally:
            os.unlink(temp_path)
    
    def test_assess_readiness_status(self):
        """Test integration readiness assessment"""
        engine = ContentDiscoveryEngine()
        
        # Test broken/placeholder files
        assert engine._assess_readiness_status("file.py", CompletionStatus.BROKEN) == ReadinessStatus.NOT_READY
        assert engine._assess_readiness_status("file.py", CompletionStatus.PLACEHOLDER) == ReadinessStatus.NOT_READY
        
        # Test complete files (Python files without tests need tests)
        with patch.object(engine, '_find_corresponding_test', return_value=None):
            assert engine._assess_readiness_status("file.py", CompletionStatus.COMPLETE) == ReadinessStatus.NEEDS_TESTS
        
        # Test complete files with tests
        with patch.object(engine, '_find_corresponding_test', return_value="test_file.py"):
            assert engine._assess_readiness_status("file.py", CompletionStatus.COMPLETE) == ReadinessStatus.READY
        
        # Test partial files (also need tests)
        with patch.object(engine, '_find_corresponding_test', return_value=None):
            assert engine._assess_readiness_status("file.py", CompletionStatus.PARTIAL) == ReadinessStatus.NEEDS_TESTS
    
    def test_should_exclude_file(self):
        """Test file exclusion logic"""
        engine = ContentDiscoveryEngine()
        
        exclude_patterns = ["__pycache__", ".git", "node_modules"]
        
        # Should exclude
        assert engine._should_exclude_file("src/__pycache__/module.pyc", exclude_patterns) is True
        assert engine._should_exclude_file(".git/config", exclude_patterns) is True
        assert engine._should_exclude_file("node_modules/package/index.js", exclude_patterns) is True
        
        # Should not exclude
        assert engine._should_exclude_file("src/module.py", exclude_patterns) is False
        assert engine._should_exclude_file("tests/test_module.py", exclude_patterns) is False
    
    def test_create_work_artifact(self):
        """Test work artifact creation"""
        engine = ContentDiscoveryEngine()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def test_function():\n    pass\n")
            temp_path = f.name
        
        try:
            artifact = engine._create_work_artifact(temp_path)
            
            assert artifact is not None
            assert artifact.path == temp_path
            assert artifact.artifact_type == ArtifactType.CODE
            assert artifact.file_size_bytes > 0
            assert artifact.last_modified is not None
            assert "discovered_by" in artifact.metadata
            
        finally:
            os.unlink(temp_path)
    
    def test_scan_workspace_with_temp_files(self):
        """Test workspace scanning with temporary files"""
        engine = ContentDiscoveryEngine()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_files = [
                "module.py",
                "test_module.py", 
                "README.md",
                "config.json",
            ]
            
            for filename in test_files:
                file_path = Path(temp_dir) / filename
                file_path.write_text(f"# Content of {filename}\npass\n")
            
            # Configure scan
            config = TriageConfig(scan_paths=[temp_dir])
            
            # Scan workspace
            artifacts = engine.scan_workspace(config)
            
            # Verify results
            assert len(artifacts) == len(test_files)
            
            # Check that all files were found
            found_names = [Path(artifact.path).name for artifact in artifacts]
            for filename in test_files:
                assert filename in found_names
    
    def test_analyze_open_files(self):
        """Test open files analysis (mock implementation)"""
        engine = ContentDiscoveryEngine()
        
        open_files = engine.analyze_open_files()
        
        # Should return mock data
        assert isinstance(open_files, list)
        assert len(open_files) >= 0  # Mock implementation may return empty or sample data
    
    def test_scan_specs_nonexistent_directory(self):
        """Test specs scanning with nonexistent directory"""
        engine = ContentDiscoveryEngine()
        
        specs = engine.scan_specs("/nonexistent/path")
        
        assert isinstance(specs, list)
        assert len(specs) == 0
    
    def test_scan_specs_with_temp_specs(self):
        """Test specs scanning with temporary spec directories"""
        engine = ContentDiscoveryEngine()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a spec directory
            spec_dir = Path(temp_dir) / "test-spec"
            spec_dir.mkdir()
            
            # Create spec files
            (spec_dir / "requirements.md").write_text("# Requirements\n")
            (spec_dir / "design.md").write_text("# Design\n")
            (spec_dir / "tasks.md").write_text("# Tasks\n")
            
            # Scan specs
            specs = engine.scan_specs(temp_dir)
            
            # Verify results
            assert len(specs) == 1
            spec = specs[0]
            assert spec["name"] == "test-spec"
            assert spec["has_requirements"] is True
            assert spec["has_design"] is True
            assert spec["has_tasks"] is True
            assert spec["completion_status"] == "complete"
    
    def test_analyze_git_status_not_git_repo(self):
        """Test git status analysis when not in a git repo"""
        engine = ContentDiscoveryEngine()
        
        with patch('subprocess.run') as mock_run:
            # Mock git rev-parse to return non-zero (not a git repo)
            mock_run.return_value = Mock(returncode=1)
            
            git_info = engine.analyze_git_status()
            
            assert git_info["is_git_repo"] is False
            assert len(git_info["modified_files"]) == 0
            assert len(git_info["staged_files"]) == 0
            assert len(git_info["untracked_files"]) == 0
    
    def test_analyze_git_status_with_changes(self):
        """Test git status analysis with changes"""
        engine = ContentDiscoveryEngine()
        
        with patch('subprocess.run') as mock_run:
            # Mock git commands
            def mock_subprocess(cmd, **kwargs):
                if "rev-parse" in cmd:
                    return Mock(returncode=0)  # Is git repo
                elif "status" in cmd:
                    # Mock git status output (space means not modified in working tree)
                    return Mock(returncode=0, stdout=" M modified.py\nA  added.py\n?? untracked.py\n")
                elif "branch" in cmd:
                    return Mock(returncode=0, stdout="main\n")
                else:
                    return Mock(returncode=0, stdout="")
            
            mock_run.side_effect = mock_subprocess
            
            git_info = engine.analyze_git_status()
            
            assert git_info["is_git_repo"] is True
            assert "modified.py" in git_info["modified_files"]
            assert "added.py" in git_info["staged_files"]
            assert "untracked.py" in git_info["untracked_files"]
            assert git_info["current_branch"] == "main"
    
    def test_parse_git_status(self):
        """Test git status parsing"""
        engine = ContentDiscoveryEngine()
        
        git_info = {
            "modified_files": [],
            "staged_files": [],
            "untracked_files": [],
        }
        
        status_output = " M modified.py\nA  added.py\n?? untracked.py\nAM both.py\n"
        
        engine._parse_git_status(status_output, git_info)
        
        assert "modified.py" in git_info["modified_files"]  # " M" = modified in working tree
        assert "added.py" in git_info["staged_files"]      # "A " = added to stage
        assert "untracked.py" in git_info["untracked_files"]  # "??" = untracked
        assert "both.py" in git_info["staged_files"]       # "A" in first position
        assert "both.py" in git_info["modified_files"]     # "M" in second position


if __name__ == "__main__":
    pytest.main([__file__])