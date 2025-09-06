"""
Unit tests for StandardGitProvider implementation.

These tests validate the standard git provider functionality using mocked
subprocess calls to ensure reliable testing without requiring actual git operations.
"""

import pytest
import subprocess
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.gitkraken_integration.providers.standard_git_provider import StandardGitProvider
from src.gitkraken_integration.providers.git_provider import (
    GitOperationStatus,
    FileStatus,
    BranchInfo
)


class TestStandardGitProvider:
    """Test StandardGitProvider implementation"""
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_initialization_success(self, mock_exists, mock_run):
        """Test successful provider initialization"""
        mock_exists.return_value = True
        
        # Mock git executable finding
        mock_run.side_effect = [
            # which git
            Mock(stdout="/usr/bin/git\n", returncode=0),
            # git rev-parse --git-dir (validate repo)
            Mock(stdout=".git\n", returncode=0)
        ]
        
        provider = StandardGitProvider("/test/repo")
        
        assert provider.repo_path == "/test/repo"
        assert provider.git_executable == "/usr/bin/git"
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_initialization_git_not_found(self, mock_exists, mock_run):
        """Test initialization when git is not found"""
        mock_exists.return_value = True
        mock_run.side_effect = subprocess.CalledProcessError(1, "which")
        
        with pytest.raises(RuntimeError, match="Git executable not found"):
            StandardGitProvider("/test/repo")
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_initialization_invalid_repo(self, mock_exists, mock_run):
        """Test initialization with invalid repository"""
        mock_exists.return_value = True
        
        # Mock git executable finding success
        mock_run.side_effect = [
            Mock(stdout="/usr/bin/git\n", returncode=0),
            # git rev-parse --git-dir fails
            subprocess.CalledProcessError(128, "git rev-parse")
        ]
        
        with pytest.raises(ValueError, match="Not a git repository"):
            StandardGitProvider("/test/repo")
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_get_status_clean_repo(self, mock_exists, mock_run):
        """Test get_status with clean repository"""
        mock_exists.return_value = True
        
        # Setup mocks for initialization and status
        mock_run.side_effect = [
            # Initialization mocks
            Mock(stdout="/usr/bin/git\n", returncode=0),  # which git
            Mock(stdout=".git\n", returncode=0),  # validate repo
            # get_status mocks
            Mock(stdout="", returncode=0),  # git status --porcelain
            Mock(stdout="main\n", returncode=0),  # git branch --show-current
            subprocess.CalledProcessError(1, "git")  # ahead/behind (no upstream)
        ]
        
        provider = StandardGitProvider("/test/repo")
        result = provider.get_status()
        
        assert result.success is True
        assert result.status == GitOperationStatus.SUCCESS
        assert "Clean" in result.message
        assert result.data["clean"] is True
        assert result.data["branch"] == "main"
        assert result.data["total_files"] == 0
        assert result.provider_used == "Standard Git"
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_get_status_with_changes(self, mock_exists, mock_run):
        """Test get_status with file changes"""
        mock_exists.return_value = True
        
        status_output = "M  modified_file.py\nA  new_file.py\n?? untracked_file.py\n M working_modified.py\n"
        
        mock_run.side_effect = [
            # Initialization mocks
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0),
            # get_status mocks
            Mock(stdout=status_output, returncode=0),  # git status --porcelain
            Mock(stdout="main\n", returncode=0),  # git branch --show-current
            Mock(stdout="2\t1\n", returncode=0)  # ahead/behind counts
        ]
        
        provider = StandardGitProvider("/test/repo")
        result = provider.get_status()
        
        assert result.success is True
        assert result.data["clean"] is False
        assert result.data["total_files"] == 4
        assert result.data["staged_files"] == 2  # M and A files
        assert result.data["modified_files"] == 1  # working_modified.py
        assert result.data["untracked_files"] == 1  # ?? file
        assert result.data["ahead_behind"]["ahead"] == 2
        assert result.data["ahead_behind"]["behind"] == 1
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_parse_status_output(self, mock_exists, mock_run):
        """Test parsing of git status output"""
        mock_exists.return_value = True
        
        # Setup initialization mocks
        mock_run.side_effect = [
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0)
        ]
        
        provider = StandardGitProvider("/test/repo")
        
        # Test various status formats
        status_output = "M  modified_staged.py\n M modified_unstaged.py\nA  added_file.py\nD  deleted_file.py\n?? untracked_file.py\n"
        files = provider._parse_status_output(status_output)
        
        assert len(files) == 5
        
        # Check modified staged file
        modified_staged = next(f for f in files if f.path == "modified_staged.py")
        assert modified_staged.status == "M"
        assert modified_staged.staged is True
        assert modified_staged.index_status == "M"
        assert modified_staged.working_tree_status == " "
        
        # Check untracked file
        untracked = next(f for f in files if f.path == "untracked_file.py")
        assert untracked.status == "??"
        assert untracked.staged is False
        assert untracked.index_status == "?"
        assert untracked.working_tree_status == "?"
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_get_current_branch(self, mock_exists, mock_run):
        """Test getting current branch"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            # Initialization mocks
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0),
            # get_current_branch mock
            Mock(stdout="feature/test-branch\n", returncode=0)
        ]
        
        provider = StandardGitProvider("/test/repo")
        result = provider.get_current_branch()
        
        assert result.success is True
        assert result.data["branch"] == "feature/test-branch"
        assert "feature/test-branch" in result.message
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_get_current_branch_detached_head(self, mock_exists, mock_run):
        """Test getting current branch in detached HEAD state"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            # Initialization mocks
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0),
            # get_current_branch mocks
            Mock(stdout="\n", returncode=0),  # Empty branch name (detached HEAD)
            Mock(stdout="abc123def456789\n", returncode=0)  # git rev-parse HEAD
        ]
        
        provider = StandardGitProvider("/test/repo")
        result = provider.get_current_branch()
        
        assert result.success is True
        assert "HEAD detached at abc123d" in result.data["branch"]
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_create_branch_success(self, mock_exists, mock_run):
        """Test successful branch creation"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            # Initialization mocks
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0),
            # create_branch mock
            Mock(stdout="Switched to a new branch 'feature/new-feature'\n", returncode=0)
        ]
        
        provider = StandardGitProvider("/test/repo")
        result = provider.create_branch("feature/new-feature", "main")
        
        assert result.success is True
        assert result.data["branch_name"] == "feature/new-feature"
        assert result.data["from_branch"] == "main"
        assert result.data["switched"] is True
        assert "Created and switched to" in result.message
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_create_branch_invalid_name(self, mock_exists, mock_run):
        """Test branch creation with invalid name"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0)
        ]
        
        provider = StandardGitProvider("/test/repo")
        result = provider.create_branch("invalid branch name")
        
        assert result.success is False
        assert result.error_code == "GIT_INVALID_BRANCH_NAME"
        assert "Invalid branch name" in result.message
        assert len(result.suggestions) > 0
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_create_branch_already_exists(self, mock_exists, mock_run):
        """Test branch creation when branch already exists"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            # Initialization mocks
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0),
            # create_branch mock - branch already exists
            subprocess.CalledProcessError(
                128, 
                "git checkout", 
                stderr="fatal: A branch named 'existing-branch' already exists."
            )
        ]
        
        provider = StandardGitProvider("/test/repo")
        result = provider.create_branch("existing-branch")
        
        assert result.success is False
        assert result.error_code == "GIT_CREATE_BRANCH_FAILED"
        assert "already exists" in result.message
        assert any("already exists" in suggestion for suggestion in result.suggestions)
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_switch_branch_success(self, mock_exists, mock_run):
        """Test successful branch switching"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            # Initialization mocks
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0),
            # switch_branch mock
            Mock(stdout="Switched to branch 'main'\n", returncode=0)
        ]
        
        provider = StandardGitProvider("/test/repo")
        result = provider.switch_branch("main")
        
        assert result.success is True
        assert result.data["branch_name"] == "main"
        assert result.data["created"] is False
        assert "Switched to" in result.message
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_switch_branch_not_found(self, mock_exists, mock_run):
        """Test switching to non-existent branch"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            # Initialization mocks
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0),
            # switch_branch mock - branch not found
            subprocess.CalledProcessError(
                1,
                "git checkout",
                stderr="error: pathspec 'nonexistent' did not match any file(s) known to git."
            )
        ]
        
        provider = StandardGitProvider("/test/repo")
        result = provider.switch_branch("nonexistent")
        
        assert result.success is False
        assert result.error_code == "GIT_SWITCH_BRANCH_FAILED"
        assert any("does not exist" in suggestion for suggestion in result.suggestions)
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_delete_branch_success(self, mock_exists, mock_run):
        """Test successful branch deletion"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            # Initialization mocks
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0),
            # delete_branch mock
            Mock(stdout="Deleted branch feature-branch (was abc123d).\n", returncode=0)
        ]
        
        provider = StandardGitProvider("/test/repo")
        result = provider.delete_branch("feature-branch")
        
        assert result.success is True
        assert result.data["branch_name"] == "feature-branch"
        assert result.data["forced"] is False
        assert "Deleted branch" in result.message
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_delete_branch_not_merged(self, mock_exists, mock_run):
        """Test deleting unmerged branch"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            # Initialization mocks
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0),
            # delete_branch mock - not fully merged
            subprocess.CalledProcessError(
                1,
                "git branch",
                stderr="error: The branch 'feature-branch' is not fully merged."
            )
        ]
        
        provider = StandardGitProvider("/test/repo")
        result = provider.delete_branch("feature-branch")
        
        assert result.success is False
        assert result.error_code == "GIT_DELETE_BRANCH_FAILED"
        assert any("not fully merged" in suggestion for suggestion in result.suggestions)
        assert any("force=True" in suggestion for suggestion in result.suggestions)
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_is_available_true(self, mock_exists, mock_run):
        """Test provider availability check - available"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            # Initialization mocks
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0),
            # is_available mock
            Mock(stdout="git version 2.34.1\n", returncode=0)
        ]
        
        provider = StandardGitProvider("/test/repo")
        assert provider.is_available() is True
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_is_available_false(self, mock_exists, mock_run):
        """Test provider availability check - not available"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            # Initialization mocks
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0),
            # is_available mock - git command fails
            subprocess.CalledProcessError(1, "git --version")
        ]
        
        provider = StandardGitProvider("/test/repo")
        assert provider.is_available() is False
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_get_provider_name(self, mock_exists, mock_run):
        """Test getting provider name"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0)
        ]
        
        provider = StandardGitProvider("/test/repo")
        assert provider.get_provider_name() == "Standard Git"
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_get_provider_capabilities(self, mock_exists, mock_run):
        """Test getting provider capabilities"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0)
        ]
        
        provider = StandardGitProvider("/test/repo")
        capabilities = provider.get_provider_capabilities()
        
        assert capabilities["branch_management"] is True
        assert capabilities["commit_operations"] is True
        assert capabilities["remote_operations"] is True
        assert capabilities["conflict_resolution"] is True
        assert capabilities["visual_merge_tools"] is False
        assert capabilities["enhanced_ui"] is False
        assert capabilities["api_integration"] is False
        assert capabilities["advanced_analytics"] is False
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_get_health_status_healthy(self, mock_exists, mock_run):
        """Test health status check - healthy"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            # Initialization mocks
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0),
            # Health check mocks
            Mock(stdout="git version 2.34.1\n", returncode=0),  # git --version
            Mock(stdout="", returncode=0),  # git status --porcelain
            Mock(stdout="origin\thttps://github.com/user/repo.git (fetch)\n", returncode=0)  # git ls-remote
        ]
        
        provider = StandardGitProvider("/test/repo")
        result = provider.get_health_status()
        
        assert result.success is True
        assert "healthy" in result.message
        assert result.data["repository_accessible"] is True
        assert result.data["remote_accessible"] is True
        assert "git version" in result.data["git_version"]
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_placeholder_methods_not_implemented(self, mock_exists, mock_run):
        """Test that placeholder methods return NOT_IMPLEMENTED"""
        mock_exists.return_value = True
        
        mock_run.side_effect = [
            Mock(stdout="/usr/bin/git\n", returncode=0),
            Mock(stdout=".git\n", returncode=0)
        ]
        
        provider = StandardGitProvider("/test/repo")
        
        # Test placeholder methods
        methods_to_test = [
            ("stage_files", []),
            ("unstage_files", []),
            ("commit_changes", ["test message"]),
            ("get_commit_history", []),
            ("push_changes", []),
            ("pull_changes", []),
            ("fetch_changes", []),
            ("get_merge_conflicts", []),
            ("resolve_conflict", ["file.py", "ours"])
        ]
        
        for method_name, args in methods_to_test:
            method = getattr(provider, method_name)
            result = method(*args)
            
            assert result.success is False
            assert result.error_code == "NOT_IMPLEMENTED"
            assert "not yet implemented" in result.message


if __name__ == "__main__":
    pytest.main([__file__])